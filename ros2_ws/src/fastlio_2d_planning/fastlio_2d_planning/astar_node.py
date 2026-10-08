import heapq
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped, PoseStamped
from nav_msgs.msg import OccupancyGrid, Path


class AStarNode(Node):
    def __init__(self):
        super().__init__('astar_node')
        self.declare_parameters(
            namespace='',
            parameters=[
                ('grid_topic', '/planning/occupancy_grid'),
                ('path_topic', '/planning/astar_path'),
                ('start_topic', '/initialpose'),
                ('goal_topic', '/goal_pose'),
                ('occupied_threshold', 50),
                ('allow_diagonal', True),
                ('publish_rate', 2.0),
            ],
        )
        self.grid = None
        self.start = None
        self.goal = None
        self.path_pub = self.create_publisher(
            Path, self.get_parameter('path_topic').value, 10)
        self.create_subscription(
            OccupancyGrid, self.get_parameter('grid_topic').value,
            self.grid_callback, 10)
        self.create_subscription(
            PoseWithCovarianceStamped, self.get_parameter('start_topic').value,
            self.start_callback, 10)
        self.create_subscription(
            PoseStamped, self.get_parameter('goal_topic').value,
            self.goal_callback, 10)
        period = 1.0 / max(float(self.get_parameter('publish_rate').value), 0.1)
        self.timer = self.create_timer(period, self.plan)
        self.get_logger().info(
            f'Grid: {self.get_parameter("grid_topic").value}; '
            f'path: {self.get_parameter("path_topic").value}; '
            f'start: {self.get_parameter("start_topic").value}; '
            f'goal: {self.get_parameter("goal_topic").value}')

    def grid_callback(self, msg):
        self.grid = msg

    def start_callback(self, msg):
        self.start = (msg.pose.pose.position.x, msg.pose.pose.position.y)

    def goal_callback(self, msg):
        self.goal = (msg.pose.position.x, msg.pose.position.y)

    def world_to_cell(self, point):
        info = self.grid.info
        return (
            int(math.floor((point[0] - info.origin.position.x) / info.resolution)),
            int(math.floor((point[1] - info.origin.position.y) / info.resolution)),
        )

    def cell_to_world(self, cell):
        info = self.grid.info
        return (
            info.origin.position.x + (cell[0] + 0.5) * info.resolution,
            info.origin.position.y + (cell[1] + 0.5) * info.resolution,
        )

    def free(self, cell):
        x, y = cell
        if self.grid is None or x < 0 or y < 0:
            return False
        if x >= self.grid.info.width or y >= self.grid.info.height:
            return False
        # Only explicitly free cells are traversable. Unknown cells (-1)
        # remain blocked so the validation path cannot cross unmapped space.
        return self.grid.data[y * self.grid.info.width + x] == 0

    def plan(self):
        if self.grid is None or self.start is None or self.goal is None:
            return
        start = self.world_to_cell(self.start)
        goal = self.world_to_cell(self.goal)
        if not self.free(start) or not self.free(goal):
            self.get_logger().warn(
                'Start or goal is outside the grid or occupied', throttle_duration_sec=2.0)
            return
        path_cells = self.a_star(start, goal)
        if not path_cells:
            self.get_logger().warn('No A* path found', throttle_duration_sec=2.0)
            return
        path = Path()
        path.header = self.grid.header
        path.poses = []
        for cell in path_cells:
            pose = PoseStamped()
            pose.header = path.header
            pose.pose.position.x, pose.pose.position.y = self.cell_to_world(cell)
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)
        self.path_pub.publish(path)

    def neighbors(self, cell):
        moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if bool(self.get_parameter('allow_diagonal').value):
            moves += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dx, dy in moves:
            candidate = (cell[0] + dx, cell[1] + dy)
            if self.free(candidate):
                yield candidate, math.sqrt(2.0) if dx and dy else 1.0

    @staticmethod
    def heuristic(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def a_star(self, start, goal):
        frontier = [(0.0, start)]
        came_from = {start: None}
        cost = {start: 0.0}
        while frontier:
            _, current = heapq.heappop(frontier)
            if current == goal:
                result = []
                while current is not None:
                    result.append(current)
                    current = came_from[current]
                return list(reversed(result))
            for nxt, step in self.neighbors(current):
                new_cost = cost[current] + step
                if nxt not in cost or new_cost < cost[nxt]:
                    cost[nxt] = new_cost
                    heapq.heappush(
                        frontier, (new_cost + self.heuristic(nxt, goal), nxt))
                    came_from[nxt] = current
        return []


def main(args=None):
    rclpy.init(args=args)
    node = AStarNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
