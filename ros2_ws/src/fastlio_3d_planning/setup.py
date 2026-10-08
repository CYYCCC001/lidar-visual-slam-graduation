from setuptools import setup

package_name = 'fastlio_3d_planning'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/planning_3d.launch.py']),
        ('share/' + package_name + '/launch', ['launch/interactive_3d.launch.py']),
        ('share/' + package_name + '/config', ['config/planning_3d.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'voxel_map_node = fastlio_3d_planning.voxel_map_node:main',
            'astar_3d_node = fastlio_3d_planning.astar_3d_node:main',
            'interactive_3d_node = fastlio_3d_planning.interactive_3d_node:main',
        ],
    },
)
