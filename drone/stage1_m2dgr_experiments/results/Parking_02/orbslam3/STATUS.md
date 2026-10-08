# 状态说明：Parking_02 ORB-SLAM3

## 总状态

`PARTIAL_RESULT`，并包含 `VALID_SUPPLEMENTAL` 补测证据。

主结果是降速播放得到的关键帧轨迹，不是完整逐帧轨迹。报告中必须同时
说明关键帧覆盖范围、轨迹空段及跟踪失败情况。

## 主结果

- 实验记录：`experiment_record.md`
- 主关键帧轨迹：`trajectories/KeyFrameTrajectory_TUM_Format_rate0.5.txt`
- 主评估指标：`metrics/metrics_orbslam3.txt`
- 主对齐轨迹：`metrics/ate_aligned_trajectory_rate0.5.csv`
- 主 RPE 数据：`metrics/rpe_pairs_rate0.5.csv`
- 主资源采样：`metrics/resource_samples_rate0.5_retry.csv`
- 推荐 RViz 截图：`rviz/orbslam3_rviz_path.png`

主结果存在局部地图跟踪失败和地图重建，不能按稳定完整序列结果表述。

## 有效补测

以下文件用于帧级处理耗时、接收率、丢帧比例和跟踪状态：

- `supplemental_measurement/measurement_summary.txt`
- `supplemental_measurement/frame_measurements.csv`
- `supplemental_measurement/measurement_run.log`
- `supplemental_measurement/measurement_bag.log`
- `supplemental_measurement/KeyFrameTrajectory_TUM_Format_rate0.5.txt`

这些数据独立保留，不覆盖主轨迹和主评估结果。

## 诊断或无效文件

- `trajectories/KeyFrameTrajectory_TUM_Format_pangolin_rate0.5.txt`：
  空轨迹，不作为结果；
- `logs/orbslam3_pangolin_rate0.5.log`：
  Pangolin 失败或中断诊断；
- `logs/orbslam3_rate0.5_run.log`：
  初次降速运行记录，结果不作为最终主结果；
- `metrics/resource_samples_rate0.5.csv`：
  初次资源采样记录，采样目标不是最终算法进程；
- `rviz/*supplemental*`：
  多次复现截图和日志，正式引用时优先选择
  `orbslam3_rviz_path.png`，避免使用包含桌面或浮层的截图。

实时运行文件 `logs/orbslam3_direct_run.log` 和对应资源记录用于诊断，
不替代主 `0.5x` 结果。

