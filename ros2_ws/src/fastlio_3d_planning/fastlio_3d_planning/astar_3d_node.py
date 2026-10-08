import heapq
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point, PoseWithCovarianceStamped, PoseStamped
from nav_msgs.msg import Path
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2
from visualization_msgs.msg import Marker


class AStar3DNode(Node):
    def __init__(self):
        super().__init__('astar_3d_node')
        self.declare_parameters(
            namespace='',
            parameters=[
                ('voxel_topic', '/planning_3d/occupied_voxels'),
                ('path_topic', '/planning_3d/astar_path'),
                ('marker_topic', '/planning_3d/path_markers'),
                ('start_topic', '/initialpose'),
                ('goal_topic', '/goal_pose'),
                ('resolution', 0.20),
                ('publish_rate', 1.0),
                ('allow_diagonal', True),
                ('inflation_radius', 0.30),
                ('search_margin', 1.00),
                ('min_z', -1.00),
                ('max_z', 2.50),
                ('max_expansions', 250000),
            ],
        )
        self.resolution = float(self.get_parameter('resolution').value)
        self.allow_diagonal = bool(self.get_parameter('allow_diagonal').value)
        self.inflation_radius = float(self.get_parameter('inflation_radius').value)
        self.search_margin = float(self.get_parameter('search_margin').value)
        self.min_z = float(self.get_parameter('min_z').value)
        self.max_z = float(self.get_parameter('max_z').value)
        self.max_expansions = int(self.get_parameter('max_expansions').value)
        self.occupied = set()
        self.bounds = None
        self.frame_id = ''
        self.start = None
        self.goal = None

        self.path_pub = self.create_publisher(
            Path, self.get_parameter('path_topic').value, 10)
        self.marker_pub = self.create_publisher(
            Marker, self.get_parameter('marker_topic').value, 10)
        self.create_subscription(
            PointCloud2, self.get_parameter('voxel_topic').value,
            self.voxel_callback, 10)
        self.create_subscription(
            PoseWithCovarianceStamped, self.get_parameter('start_topic').value,
            self.start_callback, 10)
        self.create_subscription(
            PoseStamped, self.get_parameter('goal_topic').value,
            self.goal_callback, 10)
        period = 1.0 / max(float(self.get_parameter('publish_rate').value), 0.1)
        self.timer = self.create_timer(period, self.plan)
        self.moves = self.build_moves()
        self.get_logger().info(
            f'Voxels: {self.get_parameter("voxel_topic").value}; path: '
            f'{self.get_parameter("path_topic").value}; resolution: '
            f'{self.resolution:.3f} m')

    def voxel_callback(self, msg):
        occupied = set()
        for x, y, z in point_cloud2.read_points(
                msg, field_names=('x', 'y', 'z'), skip_nans=True):
            occupied.add(self.world_to_cell((float(x), float(y), float(z))))
        self.occupied = self.inflate(occupied)
        self.bounds = self.compute_bounds(self.occupied)
        self.frame_id = msg.header.frame_id

    def start_callback(self, msg):
        self.start = (
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            msg.pose.pose.position.z,
        )

    def goal_callback(self, msg):
        self.goal = (
            msg.pose.position.x,
            msg.pose.position.y,
            msg.pose.position.z,
        )

    def world_to_cell(self, point):
        return tuple(int(math.floor(axis / self.resolution)) for axis in point)

    def cell_to_world(self, cell):
        return tuple((axis + 0.5) * self.resolution for axis in cell)

    def inflate(self, occupied):
        if self.inflation_radius <= 0.0 or not occupied:
            return occupied
        cells = int(math.ceil(self.inflation_radius / self.resolution))
        inflated = set()
        for cell in occupied:
            for dz in range(-cells, cells + 1):
                for dy in range(-cells, cells + 1):
                    for dx in range(-cells, cells + 1):
                        if dx * dx + dy * dy + dz * dz > cells * cells:
                            continue
                        inflated.add((cell[0] + dx, cell[1] + dy, cell[2] + dz))
        return inflated

    def compute_bounds(self, occupied):
        if not occupied:
            return None
        margin = int(math.ceil(self.search_margin / self.resolution))
        min_z_cell = int(math.floor(self.min_z / self.resolution))
        max_z_cell = int(math.floor(self.max_z / self.resolution))
        xs = [cell[0] for cell in occupied]
        ys = [cell[1] for cell in occupied]
        zs = [cell[2] for cell in occupied]
        return (
            min(xs) - margin, max(xs) + margin,
            min(ys) - margin, max(ys) + margin,
            max(min(zs) - margin, min_z_cell),
            min(max(zs) + margin, max_z_cell),
        )

    def in_bounds(self, cell):
        if self.bounds is None:
            return False
        min_x, max_x, min_y, max_y, min_z, max_z = self.bounds
        return (
            min_x <= cell[0] <= max_x and
            min_y <= cell[1] <= max_y and
            min_z <= cell[2] <= max_z
        )

    def free(self, cell):
        return self.in_bounds(cell) and cell not in self.occupied

    def build_moves(self):
        moves = []
        for dz in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    if not self.allow_diagonal and sum(
                            1 for value in (dx, dy, dz) if value != 0) > 1:
                        continue
                    moves.append((dx, dy, dz, math.sqrt(dx * dx + dy * dy + dz * dz)))
        return moves

    def plan(self):
        if not self.occupied or self.bounds is None:
            return
        if self.start is None or self.goal is None:
            return
        start = self.world_to_cell(self.start)
        goal = self.world_to_cell(self.goal)
        self.bounds = self.expand_bounds_for_endpoints(self.bounds, start, goal)
        if not self.free(start) or not self.free(goal):
            self.get_logger().warn(
                '3D start or goal is outside free voxel space',
                throttle_duration_sec=2.0)
            return
        cells = self.a_star(start, goal)
        if not cells:
            self.get_logger().warn('No 3D A* path found', throttle_duration_sec=2.0)
            return
        self.publish_path(cells)

    def expand_bounds_for_endpoints(self, bounds, start, goal):
        min_x, max_x, min_y, max_y, min_z, max_z = bounds
        margin = int(math.ceil(self.search_margin / self.resolution))
        min_z_cell = int(math.floor(self.min_z / self.resolution))
        max_z_cell = int(math.floor(self.max_z / self.resolution))
        return (
            min(min_x, start[0] - margin, goal[0] - margin),
            max(max_x, start[0] + margin, goal[0] + margin),
            min(min_y, start[1] - margin, goal[1] - margin),
            max(max_y, start[1] + margin, goal[1] + margin),
            max(min(min_z, start[2] - margin, goal[2] - margin), min_z_cell),
            min(max(max_z, start[2] + margin, goal[2] + margin), max_z_cell),
        )

    def neighbors(self, cell):
        for dx, dy, dz, step in self.moves:
            candidate = (cell[0] + dx, cell[1] + dy, cell[2] + dz)
            if self.free(candidate):
                yield candidate, step

    @staticmethod
    def heuristic(a, b):
        return math.sqrt(
            (a[0] - b[0]) ** 2 +
            (a[1] - b[1]) ** 2 +
            (a[2] - b[2]) ** 2)

    def a_star(self, start, goal):
        frontier = [(0.0, start)]
        came_from = {start: None}
        cost = {start: 0.0}
        expansions = 0
        while frontier and expansions < self.max_expansions:
            _, current = heapq.heappop(frontier)
            expansions += 1
            if current == goal:
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                return list(reversed(path))
            for nxt, step in self.neighbors(current):
                new_cost = cost[current] + step
                if nxt not in cost or new_cost < cost[nxt]:
                    cost[nxt] = new_cost
                    heapq.heappush(
                        frontier, (new_cost + self.heuristic(nxt, goal), nxt))
                    came_from[nxt] = current
        if expansions >= self.max_expansions:
            self.get_logger().warn(
                f'3D A* reached max_expansions={self.max_expansions}',
                throttle_duration_sec=2.0)
        return []

    def publish_path(self, cells):
        path = Path()
        path.header.stamp = self.get_clock().now().to_msg()
        path.header.frame_id = self.frame_id
        for cell in cells:
            pose = PoseStamped()
            pose.header = path.header
            x, y, z = self.cell_to_world(cell)
            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.position.z = z
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)
        self.path_pub.publish(path)
        self.publish_marker(path)

    def publish_marker(self, path):
        marker = Marker()
        marker.header = path.header
        marker.ns = 'astar_3d_path'
        marker.id = 0
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.scale.x = max(self.resolution * 0.35, 0.03)
        marker.color.r = 1.0
        marker.color.g = 0.25
        marker.color.b = 0.05
        marker.color.a = 1.0
        for pose in path.poses:
            point = Point()
            point.x = pose.pose.position.x
            point.y = pose.pose.position.y
            point.z = pose.pose.position.z
            marker.points.append(point)
        self.marker_pub.publish(marker)


def main(args=None):
    rclpy.init(args=args)
    node = AStar3DNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
