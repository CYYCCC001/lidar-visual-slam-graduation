#!/usr/bin/env python3
import sys

import rclpy
from rclpy.executors import ExternalShutdownException
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
from rclpy.node import Node


class TumPathPublisher(Node):
    def __init__(self, path_file, topic_name, frame_id):
        super().__init__("tum_path_publisher")
        self.publisher = self.create_publisher(Path, topic_name, 10)
        self.path = Path()
        self.path.header.frame_id = frame_id
        with open(path_file, "r", encoding="utf-8") as handle:
            for line in handle:
                parts = line.strip().split()
                if len(parts) < 8:
                    continue
                timestamp, tx, ty, tz, qx, qy, qz, qw = map(float, parts[:8])
                pose = PoseStamped()
                pose.header.frame_id = frame_id
                pose.header.stamp = rclpy.time.Time(seconds=timestamp).to_msg()
                pose.pose.position.x = tx
                pose.pose.position.y = ty
                pose.pose.position.z = tz
                pose.pose.orientation.x = qx
                pose.pose.orientation.y = qy
                pose.pose.orientation.z = qz
                pose.pose.orientation.w = qw
                self.path.poses.append(pose)
        self.get_logger().info(
            f"Loaded {len(self.path.poses)} poses from {path_file}; publishing {topic_name}"
        )
        self.timer = self.create_timer(0.2, self.publish_path)

    def publish_path(self):
        self.path.header.stamp = self.get_clock().now().to_msg()
        for pose in self.path.poses:
            pose.header.stamp = self.path.header.stamp
        self.publisher.publish(self.path)


def main():
    if len(sys.argv) < 3:
        print("usage: publish_tum_path_ros2.py TRAJECTORY_TUM TOPIC [FRAME_ID]", file=sys.stderr)
        raise SystemExit(2)
    frame_id = sys.argv[3] if len(sys.argv) > 3 else "map"
    rclpy.init()
    node = TumPathPublisher(sys.argv[1], sys.argv[2], frame_id)
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
