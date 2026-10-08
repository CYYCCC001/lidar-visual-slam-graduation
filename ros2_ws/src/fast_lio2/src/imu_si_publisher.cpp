#include <memory>
#include <string>

#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/imu.hpp>

class ImuSiPublisher : public rclcpp::Node
{
public:
  ImuSiPublisher()
  : Node("imu_si_publisher")
  {
    input_topic_ = this->declare_parameter<std::string>("input_topic", "/livox/imu");
    output_topic_ = this->declare_parameter<std::string>("output_topic", "/livox/imu_si");
    acc_scale_ = this->declare_parameter<double>("acc_scale", 9.80665);

    pub_ = this->create_publisher<sensor_msgs::msg::Imu>(output_topic_, rclcpp::QoS(10).reliable());
    sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
      input_topic_, rclcpp::QoS(10).reliable(),
      [this](sensor_msgs::msg::Imu::SharedPtr msg) { this->on_imu(std::move(msg)); });

    RCLCPP_INFO(this->get_logger(),
                "IMU SI bridge started: %s -> %s, acc_scale=%.5f",
                input_topic_.c_str(), output_topic_.c_str(), acc_scale_);
  }

private:
  void on_imu(sensor_msgs::msg::Imu::SharedPtr msg)
  {
    msg->linear_acceleration.x *= acc_scale_;
    msg->linear_acceleration.y *= acc_scale_;
    msg->linear_acceleration.z *= acc_scale_;
    pub_->publish(*msg);
  }

  std::string input_topic_;
  std::string output_topic_;
  double acc_scale_ = 9.80665;
  rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr pub_;
  rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr sub_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ImuSiPublisher>());
  rclcpp::shutdown();
  return 0;
}
