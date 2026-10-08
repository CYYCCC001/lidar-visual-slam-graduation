from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('fastlio_3d_planning'),
        'config',
        'planning_3d.yaml',
    )
    return LaunchDescription([
        Node(
            package='fastlio_3d_planning',
            executable='voxel_map_node',
            name='voxel_map_node',
            parameters=[config],
            output='screen',
        ),
        Node(
            package='fastlio_3d_planning',
            executable='astar_3d_node',
            name='astar_3d_node',
            parameters=[config],
            output='screen',
        ),
    ])
