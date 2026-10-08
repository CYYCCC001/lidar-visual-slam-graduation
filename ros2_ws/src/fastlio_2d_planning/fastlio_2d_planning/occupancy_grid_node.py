import math

import numpy as np
import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2


class OccupancyGridNode(Node):
    def __init__(self):
        super().__init__('occupancy_grid_node')
        self.declare_parameters(
            namespace='',
            parameters=[
                ('input_topic', '/Laser_map'),
                ('output_topic', '/planning/occupancy_grid'),
                ('resolution', 0.10),
                ('update_rate', 1.0),
                ('min_height', -0.30),
                ('max_height', 1.50),
                ('obstacle_value', 100),
                ('unknown_value', -1),
                ('use_inflation', True),
                ('inflation_radius', 0.20),
            ],
        )
        self.input_topic = self.get_parameter('input_topic').value
        self.output_topic = self.get_parameter('output_topic').value
        self.resolution = float(self.get_parameter('resolution').value)
        self.min_height = float(self.get_parameter('min_height').value)
        self.max_height = float(self.get_parameter('max_height').value)
        self.obstacle_value = int(self.get_parameter('obstacle_value').value)
        self.unknown_value = int(self.get_parameter('unknown_value').value)
        self.use_inflation = bool(self.get_parameter('use_inflation').value)
        self.inflation_radius = float(self.get_parameter('inflation_radius').value)
        self.latest_msg = None
        self.last_frame = ''
        self.publisher = self.create_publisher(
            OccupancyGrid, self.output_topic, 10)
        self.subscription = self.create_subscription(
            PointCloud2, self.input_topic, self.cloud_callback, 10)
        period = 1.0 / max(float(self.get_parameter('update_rate').value), 0.1)
        self.timer = self.create_timer(period, self.publish_grid)
        self.get_logger().info(
            f'Input: {self.input_topic}; output: {self.output_topic}; '
            f'resolution: {self.resolution:.3f} m')

    def cloud_callback(self, msg):
        self.latest_msg = msg

    def publish_grid(self):
        if self.latest_msg is None:
            return
        msg = self.latest_msg
        points = point_cloud2.read_points(
            msg, field_names=('x', 'y', 'z'), skip_nans=True)
        values = [(float(x), float(y), float(z)) for x, y, z in points
                  if self.min_height <= float(z) <= self.max_height]
        if not values:
            return

        data = np.asarray(values, dtype=np.float64)
        min_x = math.floor(float(np.min(data[:, 0])) / self.resolution) * self.resolution
        min_y = math.floor(float(np.min(data[:, 1])) / self.resolution) * self.resolution
        max_x = math.ceil(float(np.max(data[:, 0])) / self.resolution) * self.resolution
        max_y = math.ceil(float(np.max(data[:, 1])) / self.resolution) * self.resolution
        width = max(1, int(round((max_x - min_x) / self.resolution)) + 1)
        height = max(1, int(round((max_y - min_y) / self.resolution)) + 1)
        # The dynamic point-cloud bounding box is the observed planning area.
        # Cells without projected points are treated as free for visualization
        # and A* validation; obstacle cells are written below.
        grid = np.zeros((height, width), dtype=np.int8)
        ix = np.floor((data[:, 0] - min_x) / self.resolution).astype(np.int64)
        iy = np.floor((data[:, 1] - min_y) / self.resolution).astype(np.int64)
        valid = (ix >= 0) & (ix < width) & (iy >= 0) & (iy < height)
        grid[iy[valid], ix[valid]] = self.obstacle_value

        if self.use_inflation and self.inflation_radius > 0.0:
            cells = int(math.ceil(self.inflation_radius / self.resolution))
            inflated = grid == self.obstacle_value
            obstacle_y, obstacle_x = np.nonzero(inflated)
            for dy in range(-cells, cells + 1):
                for dx in range(-cells, cells + 1):
                    if dx * dx + dy * dy > cells * cells:
                        continue
                    yy = obstacle_y + dy
                    xx = obstacle_x + dx
                    valid = (yy >= 0) & (yy < height) & (xx >= 0) & (xx < width)
                    grid[yy[valid], xx[valid]] = self.obstacle_value

        out = OccupancyGrid()
        out.header = msg.header
        out.info.resolution = self.resolution
        out.info.width = width
        out.info.height = height
        out.info.origin.position.x = min_x
        out.info.origin.position.y = min_y
        out.info.origin.orientation.w = 1.0
        out.data = grid.reshape(-1).tolist()
        self.publisher.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = OccupancyGridNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
