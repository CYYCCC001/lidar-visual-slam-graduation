# Stage 1 FAST-LIO2 Street_02 Experiment Record

## Dataset

- Dataset: M2DGR Street_02
- ROS 2 bag: `/home/nvidia/drone/stage1_m2dgr_experiments/bags/Street_02/street2_ros2`
- Ground truth: `/home/nvidia/drone/stage1_m2dgr_experiments/ground_truth/Street_02/street2.txt`
- Original ROS 1 bag was not modified.
- Playback topics used by FAST-LIO2: `/rslidar_points` and `/imu`
- Bag duration: approximately `121.347 s`
- LiDAR messages: `610`
- IMU messages: `12135`
- LiDAR input rate: approximately `5.033 Hz`
- IMU input rate: approximately `100.12 Hz`

The bag also contains camera, odometry, TF, GNSS, and other topics. GNSS
topics requiring the unavailable `gnss_comm` package were ignored by
`ros2 bag play`; this did not affect the FAST-LIO2 LiDAR-IMU playback.

## Configuration

- FAST-LIO2 config used:
  `/home/nvidia/drone/stage1_m2dgr_experiments/configs/fastlio_street2.yaml`
- Archived config copy: `config_used.yaml`
- Calibration source:
  `/home/nvidia/drone/stage1_m2dgr_experiments/calibration/calibration.txt`
- LiDAR type: generic PointCloud2 (`lidar_type: 0`)
- LiDAR scan lines: `16`
- Configured LiDAR scan rate: `4 Hz`
- Point filter number: `4`
- Surface filter size: `0.5`
- Map filter size: `0.5`
- IMU topic: `/imu`
- LiDAR topic: `/rslidar_points`
- `time_sync_en`: `false`
- `time_offset_lidar_to_imu`: `0.0`
- `extrinsic_est_en`: `false`
- `extrinsic_T`: `[-0.13, 0.0, -1.03]`
- `extrinsic_R`:

  ```text
  [1, 0, 0;
   0, -1, 0;
   0, 0, -1]
  ```

- FAST-LIO2 was run with `use_sim_time:=true`.
- RViz was launched with the standard FAST-LIO2 RViz configuration.

Camera intrinsics were not used by FAST-LIO2. They remain available in
`calibration.txt` for the visual or visual-inertial experiments.

## Runtime and Saved Results

- Main run log: `run.log`
- Bag playback log: `bag_play.log`
- Runtime/resource samples: `resource_samples.csv`
- Pose/state log: `fastlio_logs/pos_log.txt`
- State matrices: `fastlio_logs/mat_out.txt`, `fastlio_logs/mat_pre.txt`
- Saved map: `map.pcd`
- Map save log: `map_save.log`
- Map save result: `success=True`

The saved PCD contains:

- Point count: `4,258,510`
- File size: approximately `136.3 MB`
- Point fields: `x y z intensity normal_x normal_y normal_z curvature`

Resource samples for `fastlio_mapping`:

- Sample count: `25`
- Average CPU: `76.076%`
- Maximum CPU: `83.800%`
- Average RSS: approximately `464582 KB`
- Maximum RSS: `775452 KB`

Timestamped run directories are retained under this result directory. The
main result files and metrics refer to the completed Street_02 run.

## Processing Performance

Timing source: `fastlio_logs/fast_lio_time_log.csv`.

- Processed frames: `532`
- Average processing time: `158.225461 ms`
- Effective processing rate: `6.320095 Hz`
- Minimum processing time: `118.454160 ms`
- Maximum processing time: `210.642830 ms`

The effective processing rate is derived from FAST-LIO2 processing time. It is
not the same as the LiDAR input publication rate.

The summary is also stored in `metrics/timing.txt`, and the resource summary
is stored in `metrics/performance.txt`.

## RViz Verification

- RViz replay status: `rviz/replay_status.txt`
- RViz fixed frame: `camera_init`
- Replay bag:
  `/home/nvidia/drone/stage1_m2dgr_experiments/bags/Street_02/street2_ros2`
- RViz logs:
  `rviz/rviz2.log`, `rviz/fastlio_mapping.log`,
  `rviz/imu_si_publisher.log`, `rviz/rviz_launch.log`
- Mid-run screenshot: `rviz/street2_fastlio_rviz_midrun.png`
- Final screenshot: `rviz/street2_fastlio_rviz_final.png`
- Additional manually captured screenshots are retained under `rviz/`.

The replay completed successfully with non-empty point-cloud, map, and
trajectory displays. The visual replay was used to verify the Street_02
three-dimensional mapping result and did not modify the algorithm
configuration.

## ATE/RPE Evaluation

- Estimated trajectory: `fastlio_logs/pos_log.txt`
- Matched poses: `532`
- ATE position after SE(3) Umeyama alignment:
  - RMSE: `8.136328 m`
  - Mean: `7.313292 m`
  - Median: `8.973151 m`
  - Maximum: `12.688860 m`
- RPE translation, delta `1 s`: RMSE `0.441570 m`
- RPE translation, delta `5 s`: RMSE `1.471480 m`
- RPE rotation, delta `1 s`: RMSE `4.493349 deg`
- RPE rotation, delta `5 s`: RMSE `15.772323 deg`

The evaluation files are in `metrics/`, including:

- `metrics/metrics.txt`
- `metrics/ate_aligned_trajectory.csv`
- `metrics/rpe_pairs.csv`

The absolute orientation error after alignment is approximately `147.293
degrees`. This is reported for diagnosis only because the supplied ground
truth and FAST-LIO pose orientations use different fixed
sensor/frame conventions. Relative rotation RPE is the appropriate
rotational comparison here; no sensor-frame offset refinement was applied.

## Status

The Street_02 FAST-LIO2 playback, map export, runtime measurement, trajectory
evaluation, and RViz visual verification completed successfully. The result
directory contains the configuration, logs, trajectory, map, performance
metrics, resource samples, and screenshots required for the comparison
experiment.

This is the `filter_size_surf: 0.5` default FAST-LIO2 result. No algorithm
configuration was modified during the Street_02 observation run, and no
existing result was overwritten.
