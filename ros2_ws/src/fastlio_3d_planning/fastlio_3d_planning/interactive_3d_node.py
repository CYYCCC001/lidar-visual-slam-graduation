from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from interactive_markers import InteractiveMarkerServer
from rclpy.node import Node
import rclpy
from visualization_msgs.msg import InteractiveMarker, InteractiveMarkerControl


class Interactive3DNode(Node):
    def __init__(self):
        super().__init__('interactive_3d_node')
        self.declare_parameter('frame_id', 'camera_init')
        self.declare_parameter('start_x', 2.5)
        self.declare_parameter('start_y', 6.9)
        self.declare_parameter('start_z', 0.5)
        self.declare_parameter('goal_x', 2.5)
        self.declare_parameter('goal_y', 7.3)
        self.declare_parameter('goal_z', 0.5)
        self.frame_id = self.get_parameter('frame_id').value
        self.start = [
            float(self.get_parameter('start_x').value),
            float(self.get_parameter('start_y').value),
            float(self.get_parameter('start_z').value),
        ]
        self.goal = [
            float(self.get_parameter('goal_x').value),
            float(self.get_parameter('goal_y').value),
            float(self.get_parameter('goal_z').value),
        ]
        self.start_pub = self.create_publisher(
            PoseWithCovarianceStamped, '/initialpose', 10)
        self.goal_pub = self.create_publisher(PoseStamped, '/goal_pose', 10)
        self.server = InteractiveMarkerServer(self, 'three_d_points')
        self.make_marker('start', '3D Start', self.start, (0.1, 0.9, 0.2, 1.0))
        self.make_marker('goal', '3D Goal', self.goal, (1.0, 0.2, 0.1, 1.0))
        self.server.applyChanges()
        self.get_logger().info(
            'Drag the Start and Goal markers in RViz. '
            f'Frame: {self.frame_id}')

    def make_marker(self, name, description, position, color):
        marker = InteractiveMarker()
        marker.header.frame_id = self.frame_id
        marker.name = name
        marker.description = description
        marker.pose.position.x = position[0]
        marker.pose.position.y = position[1]
        marker.pose.position.z = position[2]
        marker.pose.orientation.w = 1.0
        marker.scale = 0.6

        visual = InteractiveMarkerControl()
        visual.name = f'{name}_visual'
        visual.always_visible = True
        visual.markers.append(self.sphere_marker(color))
        marker.controls.append(visual)

        free_move = InteractiveMarkerControl()
        free_move.name = f'{name}_move_3d'
        free_move.interaction_mode = InteractiveMarkerControl.MOVE_3D
        free_move.always_visible = False
        marker.controls.append(free_move)

        for axis, orientation in (
                ('x', (1.0, 0.0, 0.0, 1.0)),
                ('y', (0.0, 1.0, 0.0, 1.0)),
                ('z', (0.0, 0.0, 1.0, 1.0))):
            control = InteractiveMarkerControl()
            control.name = f'{name}_move_{axis}'
            control.orientation.x = orientation[0]
            control.orientation.y = orientation[1]
            control.orientation.z = orientation[2]
            control.orientation.w = orientation[3]
            control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
            marker.controls.append(control)

        self.server.insert(marker, feedback_callback=self.feedback_callback)

    def sphere_marker(self, color):
        from visualization_msgs.msg import Marker
        marker = Marker()
        marker.type = Marker.SPHERE
        marker.scale.x = 0.25
        marker.scale.y = 0.25
        marker.scale.z = 0.25
        marker.color.r = color[0]
        marker.color.g = color[1]
        marker.color.b = color[2]
        marker.color.a = color[3]
        return marker

    def feedback_callback(self, feedback):
        point = feedback.pose.position
        position = [point.x, point.y, point.z]
        if feedback.marker_name == 'start':
            self.start = position
            self.publish_start(position)
        elif feedback.marker_name == 'goal':
            self.goal = position
            self.publish_goal(position)
        self.get_logger().info(
            f'{feedback.marker_name}: '
            f'({point.x:.2f}, {point.y:.2f}, {point.z:.2f})')

    def publish_start(self, position):
        message = PoseWithCovarianceStamped()
        message.header.frame_id = self.frame_id
        message.header.stamp = self.get_clock().now().to_msg()
        message.pose.pose.position.x = position[0]
        message.pose.pose.position.y = position[1]
        message.pose.pose.position.z = position[2]
        message.pose.pose.orientation.w = 1.0
        self.start_pub.publish(message)

    def publish_goal(self, position):
        message = PoseStamped()
        message.header.frame_id = self.frame_id
        message.header.stamp = self.get_clock().now().to_msg()
        message.pose.position.x = position[0]
        message.pose.position.y = position[1]
        message.pose.position.z = position[2]
        message.pose.orientation.w = 1.0
        self.goal_pub.publish(message)


def main(args=None):
    rclpy.init(args=args)
    node = Interactive3DNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
