# fastlio_2d_planning

This package converts the FAST-LIO2 accumulated map `/Laser_map` into a
2D `nav_msgs/msg/OccupancyGrid` and computes an A* path for RViz validation.

It does not modify or subscribe to the Livox raw topic, FAST-LIO2 parameters,
or FAST-LIO2 source files.
