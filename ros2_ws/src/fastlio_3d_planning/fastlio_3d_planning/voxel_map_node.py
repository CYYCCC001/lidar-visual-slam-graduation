import math
from collections import Counter

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Header
from visualization_msgs.msg import Marker


class VoxelMapNode(Node):
    def __init__(self):
        super().__init__('voxel_map_node')
        self.declare_parameters(
            namespace='',
            parameters=[
                ('input_topic', '/Laser_map'),
                ('voxel_cloud_topic', '/planning_3d/occupied_voxels'),
                ('marker_topic', '/planning_3d/voxel_markers'),
                ('slice_marker_topic', '/planning_3d/voxel_slice_markers'),
                ('resolution', 0.20),
                ('update_rate', 1.0),
                ('min_z', -1.00),
                ('max_z', 2.50),
                ('slice_min_z', 0.00),
                ('slice_max_z', 1.50),
                ('min_points_per_voxel', 1),
                ('max_voxels', 120000),
                ('publish_markers', True),
                ('publish_slice_markers', True),
            ],
        )
        self.input_topic = self.get_parameter('input_topic').value
        self.voxel_cloud_topic = self.get_parameter('voxel_cloud_topic').value
        self.marker_topic = self.get_parameter('marker_topic').value
        self.slice_marker_topic = self.get_parameter('slice_marker_topic').value
        self.resolution = float(self.get_parameter('resolution').value)
        self.min_z = float(self.get_parameter('min_z').value)
        self.max_z = float(self.get_parameter('max_z').value)
        self.slice_min_z = float(self.get_parameter('slice_min_z').value)
        self.slice_max_z = float(self.get_parameter('slice_max_z').value)
        self.min_points_per_voxel = int(
            self.get_parameter('min_points_per_voxel').value)
        self.max_voxels = int(self.get_parameter('max_voxels').value)
        self.publish_markers = bool(self.get_parameter('publish_markers').value)
        self.publish_slice_markers = bool(
            self.get_parameter('publish_slice_markers').value)
        self.latest_msg = None

        self.cloud_pub = self.create_publisher(
            PointCloud2, self.voxel_cloud_topic, 10)
        self.marker_pub = self.create_publisher(Marker, self.marker_topic, 10)
        self.slice_marker_pub = self.create_publisher(
            Marker, self.slice_marker_topic, 10)
        self.create_subscription(
            PointCloud2, self.input_topic, self.cloud_callback, 10)
        period = 1.0 / max(float(self.get_parameter('update_rate').value), 0.1)
        self.timer = self.create_timer(period, self.publish_voxels)
        self.get_logger().info(
            f'Input: {self.input_topic}; occupied voxels: '
            f'{self.voxel_cloud_topic}; resolution: {self.resolution:.3f} m')

    def cloud_callback(self, msg):
        self.latest_msg = msg

    def publish_voxels(self):
        if self.latest_msg is None:
            return
        msg = self.latest_msg
        counts = Counter()
        for x, y, z in point_cloud2.read_points(
                msg, field_names=('x', 'y', 'z'), skip_nans=True):
            z = float(z)
            if z < self.min_z or z > self.max_z:
                continue
            key = (
                math.floor(float(x) / self.resolution),
                math.floor(float(y) / self.resolution),
                math.floor(z / self.resolution),
            )
            counts[key] += 1

        occupied = [key for key, count in counts.items()
                    if count >= self.min_points_per_voxel]
        if not occupied:
            return
        if len(occupied) > self.max_voxels:
            occupied = occupied[:self.max_voxels]
            self.get_logger().warn(
                f'Voxel output limited to {self.max_voxels} cells',
                throttle_duration_sec=5.0)

        points = [self.voxel_center(key) for key in occupied]
        header = Header()
        header.stamp = msg.header.stamp
        header.frame_id = msg.header.frame_id
        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
        ]
        cloud = point_cloud2.create_cloud(header, fields, points)
        self.cloud_pub.publish(cloud)

        if self.publish_markers:
            self.publish_marker(self.marker_pub, header, points, 'occupied_voxels',
                                (0.1, 0.55, 1.0, 0.22))
        if self.publish_slice_markers:
            slice_points = [
                point for point in points
                if self.slice_min_z <= point[2] <= self.slice_max_z
            ]
            self.publish_marker(self.slice_marker_pub, header, slice_points,
                                'occupied_voxel_slice',
                                (1.0, 0.85, 0.1, 0.70))

    def voxel_center(self, key):
        return tuple((axis + 0.5) * self.resolution for axis in key)

    def publish_marker(self, publisher, header, points, namespace, color):
        marker = Marker()
        marker.header = header
        marker.ns = namespace
        marker.id = 0
        marker.type = Marker.CUBE_LIST
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.scale.x = self.resolution
        marker.scale.y = self.resolution
        marker.scale.z = self.resolution
        marker.color.r = color[0]
        marker.color.g = color[1]
        marker.color.b = color[2]
        marker.color.a = color[3]
        marker.points = []
        for x, y, z in points:
            point = Point()
            point.x = x
            point.y = y
            point.z = z
            marker.points.append(point)
        publisher.publish(marker)


def main(args=None):
    rclpy.init(args=args)
    node = VoxelMapNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
