#include <chrono>
#include <fstream>
#include <iomanip>
#include <memory>
#include <mutex>
#include <string>

#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>

#include <opencv2/core.hpp>

#include "System.h"

class OrbSlam3MonoNode final : public rclcpp::Node
{
public:
  OrbSlam3MonoNode()
  : Node("orb_slam3_mono")
  {
    const auto vocabulary_path =
      declare_parameter<std::string>("vocabulary_path", "");
    const auto settings_path =
      declare_parameter<std::string>("settings_path", "");
    const auto image_topic =
      declare_parameter<std::string>("image_topic", "/camera/image_raw");
    const auto trajectory_path =
      declare_parameter<std::string>(
        "keyframe_trajectory_path", "KeyFrameTrajectory_TUM_Format.txt");
    const auto use_viewer = declare_parameter<bool>("use_viewer", false);
    const auto queue_size = declare_parameter<int>("queue_size", 10);
    const auto measurement_log_path =
      declare_parameter<std::string>("measurement_log_path", "");

    if (vocabulary_path.empty() || settings_path.empty()) {
      throw std::runtime_error(
        "Parameters 'vocabulary_path' and 'settings_path' are required");
    }
    if (queue_size < 1) {
      throw std::runtime_error("Parameter 'queue_size' must be positive");
    }

    slam_ = std::make_unique<ORB_SLAM3::System>(
      vocabulary_path,
      settings_path,
      ORB_SLAM3::System::MONOCULAR,
      use_viewer);
    trajectory_path_ = trajectory_path;
    if (!measurement_log_path.empty()) {
      measurement_log_.open(measurement_log_path);
      if (!measurement_log_.is_open()) {
        throw std::runtime_error(
          "Could not open measurement log: " + measurement_log_path);
      }
      measurement_log_
        << "sequence,stamp_s,processing_time_ms,tracking_state\n";
      measurement_log_ << std::fixed << std::setprecision(9);
    }

    subscription_ = create_subscription<sensor_msgs::msg::Image>(
      image_topic,
      rclcpp::QoS(rclcpp::KeepLast(static_cast<std::size_t>(queue_size))).best_effort(),
      std::bind(&OrbSlam3MonoNode::image_callback, this, std::placeholders::_1));

    RCLCPP_INFO(
      get_logger(),
      "ORB-SLAM3 ROS 2 monocular interface ready; image topic: %s",
      image_topic.c_str());
  }

  ~OrbSlam3MonoNode() override
  {
    if (slam_) {
      slam_->Shutdown();
      slam_->SaveKeyFrameTrajectoryTUM(trajectory_path_);
    }
    if (measurement_log_.is_open()) {
      measurement_log_.close();
    }
  }

private:
  void image_callback(const sensor_msgs::msg::Image::ConstSharedPtr msg)
  {
    try {
      int image_type = -1;
      if (msg->encoding == "mono8") {
        image_type = CV_8UC1;
      } else if (msg->encoding == "bgr8" || msg->encoding == "rgb8") {
        image_type = CV_8UC3;
      } else {
        RCLCPP_WARN_THROTTLE(
          get_logger(), *get_clock(), 5000,
          "Unsupported image encoding '%s'; expected mono8, bgr8, or rgb8",
          msg->encoding.c_str());
        return;
      }

      if (msg->height == 0 || msg->width == 0 ||
        msg->step < msg->width * static_cast<unsigned int>(CV_ELEM_SIZE(image_type)) ||
        msg->data.size() < static_cast<std::size_t>(msg->step) * msg->height)
      {
        RCLCPP_ERROR(get_logger(), "Invalid image dimensions or data size");
        return;
      }

      const cv::Mat image_view(
        static_cast<int>(msg->height),
        static_cast<int>(msg->width),
        image_type,
        const_cast<unsigned char *>(msg->data.data()),
        static_cast<std::size_t>(msg->step));
      const cv::Mat image = image_view.clone();

      const auto start = std::chrono::steady_clock::now();
      slam_->TrackMonocular(
        image,
        rclcpp::Time(msg->header.stamp).seconds());
      const auto end = std::chrono::steady_clock::now();
      const double processing_time_ms =
        std::chrono::duration<double, std::milli>(end - start).count();

      if (measurement_log_.is_open()) {
        std::lock_guard<std::mutex> lock(measurement_mutex_);
        measurement_log_
          << measurement_sequence_++ << ","
          << rclcpp::Time(msg->header.stamp).seconds() << ","
          << processing_time_ms << ","
          << slam_->GetTrackingState() << "\n";
        measurement_log_.flush();
      }
    } catch (const std::exception & error) {
      RCLCPP_ERROR(get_logger(), "ORB-SLAM3 frame processing failed: %s", error.what());
    }
  }

  std::unique_ptr<ORB_SLAM3::System> slam_;
  std::string trajectory_path_;
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr subscription_;
  std::ofstream measurement_log_;
  std::mutex measurement_mutex_;
  std::size_t measurement_sequence_{0};
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  try {
    rclcpp::spin(std::make_shared<OrbSlam3MonoNode>());
  } catch (const std::exception & error) {
    fprintf(stderr, "Failed to start orb_slam3_mono: %s\n", error.what());
    rclcpp::shutdown();
    return 1;
  }
  rclcpp::shutdown();
  return 0;
}
