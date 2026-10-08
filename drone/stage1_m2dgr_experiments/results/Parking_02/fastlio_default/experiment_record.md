# Stage 1 FAST-LIO2 Experiment Record

## Dataset

- Dataset: M2DGR Parking_02
- ROS 2 bag: `/home/nvidia/drone/stage1_m2dgr_experiments/bags/Parking_02/parking2_ros2`
- Original ROS 1 bag was not modified.
- Playback topics: `/rslidar_points` and `/imu`
- Playback wall time: 146 s
- Bag duration: approximately 144.98 s

## Configuration

- FAST-LIO2 config: `/home/nvidia/drone/stage1_m2dgr_experiments/configs/fastlio_parking2.yaml`
- Calibration source: `/home/nvidia/drone/stage1_m2dgr_experiments/calibration/calibration.txt`
- LiDAR type: generic PointCloud2 (`lidar_type: 0`)
- LiDAR scan lines: 16
- LiDAR scan rate: 4 Hz
- IMU topic: `/imu`
- LiDAR topic: `/rslidar_points`
- `extrinsic_est_en`: false
- `extrinsic_T`: `[-0.13, 0.0, -1.03]`
- `extrinsic_R`:

  ```text
  [1, 0, 0;
   0, -1, 0;
   0, 0, -1]
  ```

- Camera intrinsics were not used by FAST-LIO2. They remain available in
  `calibration.txt` for the later camera/ORB-SLAM3 stage.
- FAST-LIO2 was run with `use_sim_time:=true` and `rviz:=false`.

## Results

- Final run log: `run.log`
- Runtime/resource samples: `resource_samples.csv`
- Pose/state logs: `fastlio_logs/pos_log.txt`, `fastlio_logs/mat_out.txt`,
  `fastlio_logs/mat_pre.txt`
- Saved map: `map.pcd`
- Map point count from the PCD header: 5,457,205
- Map file size: approximately 167 MB
- Map save service: `/map_save`
- Map save response: `success=True`, `Map saved.`

Resource samples for `fastlio_mapping` during the final run:

- Average CPU: approximately 41.18%
- Maximum sampled CPU: approximately 54.30%
- Average memory: approximately 2.98%
- Maximum sampled memory: approximately 5.90%
- Maximum sampled RSS: approximately 952,148 KB

## RViz Reproduction

- RViz replay completed with `rviz:=true`.
- Replay bag: `/home/nvidia/drone/stage1_m2dgr_experiments/bags/Parking_02/parking2_ros2`
- RViz fixed frame: `camera_init`
- Displays confirmed during replay: TF, Odometry, Path, Cloud Registered,
  CloudEffected, and CloudMap.
- Mid-run screenshot: `rviz/parking2_rviz_midrun.png`
- Final screenshot: `rviz/parking2_rviz_final.png`
- Both screenshots show non-empty point cloud/map data and the RViz Displays
  panel reports an OK global status.

## ATE/RPE Evaluation

- Ground truth: `/home/nvidia/drone/stage1_m2dgr_experiments/ground_truth/Parking_02/parking2.txt`
- Estimated trajectory: `fastlio_logs/pos_log.txt`
- Time association uses the first `/rslidar_points` timestamp from the ROS 2
  bag: `1668742169159889718` ns.
- Matched poses: 536
- ATE position after metric SE(3) Umeyama alignment:
  - RMSE: `0.303657 m`
  - Mean: `0.286248 m`
  - Median: `0.295087 m`
  - Maximum: `0.523618 m`
- RPE translation, delta `1 s`: RMSE `0.173436 m`
- RPE translation, delta `5 s`: RMSE `0.467672 m`
- RPE rotation, delta `1 s`: RMSE `0.504116 deg`
- RPE rotation, delta `5 s`: RMSE `1.853694 deg`

The evaluation files are in `metrics/`, including `metrics.txt`,
`ate_aligned_trajectory.csv`, and `rpe_pairs.csv`. Absolute orientation
error is reported separately for diagnosis, but is approximately 142 degrees
because the supplied ground truth and FAST-LIO pose orientations use
different fixed sensor/frame conventions. Relative rotation RPE is the
appropriate rotational comparison here; no sensor-frame offset refinement was
applied.

## Supplemental Performance and RViz Verification

The original FAST-LIO2 result files were retained. The following measurements
were collected as supplemental evidence and were not used to overwrite the
original trajectory, map, or ATE/RPE results:

- Timing source: `timing_remeasure/fast_lio_time_log.csv`
- Timing summary: `timing_remeasure/timing.txt`
- Supplemental run log: `timing_remeasure_run.log`
- Supplemental bag playback log: `timing_remeasure_bag.log`
- Supplemental RViz replay directory: `rviz_remeasure/`

Supplemental FAST-LIO2 processing measurements:

- Processed frames: `674`
- Average processing time: `112.914781 ms`
- Effective processing rate: `8.856236 Hz`
- Input timestamp rate: `4.674817 Hz`
- Minimum processing time: `85.719940 ms`
- Maximum processing time: `138.178580 ms`
- Parameter during this measurement: `filter_size_surf: 0.5`

The effective processing rate is the rate implied by the measured algorithm
processing time. It is separate from the bag input timestamp rate and should
not be interpreted as the LiDAR publication frequency.

Supplemental RViz evidence:

- `rviz_remeasure/parking2_default_rviz_midrun.png`
- `rviz_remeasure/parking2_default_rviz_final.png`
- Additional manually captured screenshots are retained under `rviz/`.

The supplemental replay completed successfully and confirmed non-empty
three-dimensional point-cloud/map displays. The original result screenshots
and all earlier run directories remain preserved.

## Status

The calibrated FAST-LIO2 playback, map export, and RViz visual reproduction
and ATE/RPE evaluation completed successfully. Screenshots and metric files
were saved as evidence. The camera intrinsics and
camera extrinsics are reserved for the later visual or visual-inertial
experiment and were not applied to this LiDAR-inertial-only run.

The supplemental timing and RViz verification were completed separately and
are retained as supporting evidence. They do not replace the original
FAST-LIO2 trajectory, map, or accuracy evaluation.

The earlier incomplete runs were preserved in timestamped directories under
this result directory and are not used as final results.
