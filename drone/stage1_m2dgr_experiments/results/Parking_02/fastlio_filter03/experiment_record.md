# Stage 1 FAST-LIO2 Parameter Experiment Record

## Experiment

- Dataset: M2DGR Parking_02
- Parameter: `filter_size_surf`
- Baseline value: `0.5`
- Experiment value: `0.3`
- Configuration used:
  `/home/nvidia/drone/stage1_m2dgr_experiments/configs/fastlio_parking2_filter03.yaml`
- Default configuration was not modified:
  `/home/nvidia/drone/stage1_m2dgr_experiments/configs/fastlio_parking2.yaml`
- ROS 2 bag:
  `/home/nvidia/drone/stage1_m2dgr_experiments/bags/Parking_02/parking2_ros2`
- Ground truth:
  `/home/nvidia/drone/stage1_m2dgr_experiments/ground_truth/Parking_02/parking2.txt`
- LiDAR topic: `/rslidar_points`
- IMU topic: `/imu`
- FAST-LIO2 was launched with `use_sim_time:=true` and `rviz:=false` for the measurement run.

## Outputs

- Run log: `run.log`
- Bag playback log: `bag_play.log`
- Resource samples: `resource_samples.csv`
- Pose/state logs: `fastlio_logs/pos_log.txt`, `mat_out.txt`, `mat_pre.txt`
- Timing log: `fastlio_logs/fast_lio_time_log.csv`
- Saved map: `map.pcd`
- Map point count: `5,533,015`
- RViz replay log: `rviz_replay.log`
- RViz bag playback log: `rviz_bag_play.log`
- Mid-run screenshot: `rviz/parking2_rviz_midrun.png`
- Final screenshot: `rviz/parking2_rviz_final.png`
- Default timing remeasure: `../fastlio_default/timing_remeasure/timing.txt`
- Default timing CSV: `../fastlio_default/timing_remeasure/fast_lio_time_log.csv`
- Default RViz remeasure log: `../fastlio_default/rviz_remeasure.log`
- Default RViz bag playback log: `../fastlio_default/rviz_remeasure_bag.log`
- Default mid-run screenshot:
  `../fastlio_default/rviz_remeasure/parking2_default_rviz_midrun.png`
- Default final screenshot:
  `../fastlio_default/rviz_remeasure/parking2_default_rviz_final.png`

## ATE/RPE

Evaluation used the supplied ground truth and the first `/rslidar_points`
timestamp in the converted ROS 2 bag as the time base. ATE uses metric SE(3)
Umeyama alignment. RPE uses relative poses at 1 s and 5 s without additional
per-interval alignment.

- Matched poses: `627`
- ATE position RMSE: `0.148522 m`
- RPE translation RMSE, delta `1 s`: `0.064888 m`
- RPE translation RMSE, delta `5 s`: `0.117748 m`
- RPE rotation RMSE, delta `1 s`: `0.509677 deg`
- RPE rotation RMSE, delta `5 s`: `1.805768 deg`

The supplied ground truth and FAST-LIO pose orientations use different fixed
sensor/frame conventions. Absolute orientation error is therefore retained
for diagnosis, while relative rotation RPE is the appropriate rotation
comparison.

## Timing

Timing was computed from `fastlio_logs/fast_lio_time_log.csv`.

- Processed frames: `627`
- Average total processing time: `143.546 ms`
- Effective processing rate: `6.966 Hz`
- Input timestamp rate: `4.348 Hz`
- Minimum total processing time: `106.668 ms`
- Maximum total processing time: `178.138 ms`

The default timing was remeasured in the isolated directory
`../fastlio_default/timing_remeasure/`, without overwriting the original
default result files.

- Default processed frames: `674`
- Default average total processing time: `112.915 ms`
- Default effective processing rate: `8.856 Hz`
- Default input timestamp rate: `4.675 Hz`
- Default minimum total processing time: `85.720 ms`
- Default maximum total processing time: `138.179 ms`

Compared with the default group, the `0.3` experiment increased average
single-frame processing time by `27.14%` and reduced effective processing rate
by `21.34%`. The two timing runs processed different frame counts (`674`
versus `627`), so this is a descriptive comparison rather than an
identical-frame benchmark.

## Resources

Resource samples cover the bag playback phase only, excluding the idle startup
period.

- Valid samples: `34`
- Average CPU: `36.632%`
- Maximum CPU: `52.200%`
- Average memory: `3.294%`
- Maximum memory: `5.900%`
- Maximum RSS: `958,664 KB` (`936.195 MB`)

## RViz

- Fixed frame: `camera_init`
- Confirmed displays: TF, Odometry, Path, CloudRegistered, CloudEffected,
  CloudMap
- Global RViz status: `Ok`
- Both screenshots contain non-empty point cloud and trajectory/map data.
- Default-group remeasure screenshots are saved separately under
  `../fastlio_default/rviz_remeasure/`:
  `parking2_default_rviz_midrun.png` and
  `parking2_default_rviz_final.png`.
- The default screenshots were validated as 1920x1080 RGBA PNG files and
  visually contain point cloud/map data with `Global Status: Ok`.

The replay log contains several `No Effective Points!` warnings near the end
of playback. The FAST-LIO2 and RViz processes did not crash, and the
screenshots were saved successfully.

## Status

The `filter_size_surf: 0.3` experiment completed with map export,
trajectory/log collection, ATE/RPE evaluation, timing/resource measurement,
and RViz evidence. The default configuration and default result directory
were not modified.
