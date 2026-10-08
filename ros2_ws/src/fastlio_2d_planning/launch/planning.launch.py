from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('fastlio_2d_planning'),
        'config',
        'planning.yaml',
    )
    return LaunchDescription([
        Node(
            package='fastlio_2d_planning',
            executable='occupancy_grid_node',
            name='occupancy_grid_node',
            parameters=[config],
            output='screen',
        ),
        Node(
            package='fastlio_2d_planning',
            executable='astar_node',
            name='astar_node',
            parameters=[config],
            output='screen',
        ),
    ])
