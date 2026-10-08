from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="orb_slam3_ros2",
            executable="orb_slam3_mono",
            name="orb_slam3_mono",
            output="screen",
            parameters=["/home/nvidia/ros2_ws/src/orb_slam3_ros2/config/mono.yaml"],
        )
    ])
