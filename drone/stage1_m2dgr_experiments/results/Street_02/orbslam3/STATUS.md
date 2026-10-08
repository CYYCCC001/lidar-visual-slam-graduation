# 状态说明：Street_02 ORB-SLAM3

## 总状态

`PARTIAL_RESULT`，并包含 `VALID_SUPPLEMENTAL` 补测证据。

主测试得到的是部分单目关键帧轨迹，存在较大轨迹空段、跟踪退化和地图
重建。不能作为完整稳定的全序列轨迹结果。

## 主结果

- 实验记录：`experiment_record.md`
- 主运行日志：`logs/orbslam3_rate0.5_retry.log`
- 主 bag 日志：`logs/orbslam3_rate0.5_retry_bag.log`
- 主轨迹：`trajectories/KeyFrameTrajectory_TUM_Format_rate0.5.txt`
- 主指标：`metrics/metrics_orbslam3.txt`
- 主资源采样：`metrics/resource_samples_rate0.5_retry.csv`
- RViz 截图：`rviz/orbslam3_rviz_path.png`

主结果应同时报告关键帧数量、轨迹覆盖率、最大关键帧间隔、局部地图失败
次数和新建地图数量。

## 有效补测

- 摘要：`supplemental_measurement/measurement_summary.txt`
- 帧级数据：`supplemental_measurement/frame_measurements.csv`
- 补测运行日志：`supplemental_measurement/measurement_run.log`
- 补测 bag 日志：`supplemental_measurement/measurement_bag.log`
- 补测资源采样：`metrics/resource_samples_measurement.csv`

这些文件用于补充单帧处理耗时、有效处理频率、消息接收/丢帧比例和跟踪
状态统计，不覆盖主结果。

## 诊断文件

- `logs/orbslam3_rate0.5_run.log`：
  初次通过 ROS 2 包装器运行的诊断记录；
- `metrics/resource_samples_rate0.5.csv`：
  初次包装器运行的资源采样，采样对象不是最终算法进程；
- 对应 `logs/orbslam3_rate0.5_bag.log`：
  初次运行的 bag 日志。

正式资源引用优先使用 `resource_samples_rate0.5_retry.csv` 和
`resource_samples_measurement.csv`。

## RViz 截图选择

正式引用优先使用 `rviz/orbslam3_rviz_path.png`。带有 supplemental、
桌面终端或截图浮层的其他图片保留用于复现记录，不作为首选论文证据。

