from setuptools import setup

package_name = 'fastlio_2d_planning'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/planning.launch.py']),
        ('share/' + package_name + '/config', ['config/planning.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'occupancy_grid_node = fastlio_2d_planning.occupancy_grid_node:main',
            'astar_node = fastlio_2d_planning.astar_node:main',
        ],
    },
)
