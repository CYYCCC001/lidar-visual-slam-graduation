from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='fastlio_3d_planning',
            executable='interactive_3d_node',
            name='interactive_3d_node',
            output='screen',
        ),
    ])
