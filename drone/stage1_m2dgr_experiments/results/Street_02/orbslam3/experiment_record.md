# Street_02 ORB-SLAM3 Experiment Record

## Dataset

- Dataset: M2DGR Street_02
- ROS 2 bag: `/home/nvidia/drone/stage1_m2dgr_experiments/bags/Street_02/street2_ros2`
- Ground truth: `/home/nvidia/drone/stage1_m2dgr_experiments/ground_truth/Street_02/street2.txt`
- Image topic: `/camera/color/image_raw`
- Image messages: `1819`
- Bag image duration: `121.290640 s`
- Image input frequency: approximately `14.993 Hz`
- Image size: `640 x 480`
- Encoding used by the node: `rgb8`

The bag also contains LiDAR, IMU, odometry, TF, GNSS, and other topics.
GNSS topics requiring the unavailable `gnss_comm` package were ignored during
playback; this did not affect the ORB-SLAM3 image test.

## Configuration

- Camera configuration:
  `/home/nvidia/drone/stage1_m2dgr_experiments/configs/orbslam3_street2_camera.yaml`
- ROS 2 configuration:
  `/home/nvidia/drone/stage1_m2dgr_experiments/configs/orbslam3_street2_ros2.yaml`
- Frame-level measurement configuration:
  `/home/nvidia/drone/stage1_m2dgr_experiments/configs/orbslam3_street2_measurement.yaml`
- Vocabulary:
  `/home/nvidia/drone/camera/orbslam3/ORB_SLAM3-master/Vocabulary/ORBvoc.txt`
- Camera model: pinhole
- Camera intrinsics:
  - `fx = 603.955566`
  - `fy = 603.125793`
  - `cx = 324.085815`
  - `cy = 232.723038`
- Distortion coefficients: all zero
- ORB features per image: `1000`
- ORB scale factor: `1.2`
- ORB levels: `8`
- Camera FPS configured in the camera file: `15`
- Viewer disabled for algorithm runs: `use_viewer: false`

Configuration copies used for the experiment are retained in this directory:

- `config_orbslam3_street2_camera.yaml`
- `config_orbslam3_street2_ros2.yaml`
- `config_orbslam3_street2_measurement.yaml`

## Main 0.5x Replay

The main test used a direct invocation of the compiled
`orb_slam3_mono` executable and played only `/camera/color/image_raw` at
`0.5x`. This ensured that the trajectory was saved by the node destructor and
that resource sampling targeted the actual ORB-SLAM3 process.

- Run log: `logs/orbslam3_rate0.5_retry.log`
- Bag playback log: `logs/orbslam3_rate0.5_retry_bag.log`
- Trajectory:
  `trajectories/KeyFrameTrajectory_TUM_Format_rate0.5.txt`
- Keyframes: `93`
- Keyframe time span: `74.658808 s`
- Image-stream time coverage: `61.553643%`
- Largest keyframe gap: `12.179235 s`
- Local-map failure reports: `41`
- New maps created: `2`
- Relocalization messages: `0`

The initial attempt made through the `ros2 run` wrapper did not save a
trajectory and is retained only as diagnostic evidence in
`logs/orbslam3_rate0.5_run.log`. It is not used as the final result.

The two-map behavior and large keyframe gaps indicate tracking degradation
and partial trajectory coverage. The trajectory must therefore not be
treated as a complete frame-by-frame camera trajectory.

## ATE/RPE Evaluation

Monocular ORB-SLAM3 was evaluated using Sim(3) alignment. Missing frames were
not interpolated. The evaluation file is
`metrics/metrics_orbslam3.txt`.

All saved keyframes:

- ATE translation RMSE: `2.093840 m`
- ATE rotation RMSE: `119.888485 deg`
- RPE translation RMSE, delta `1 s`: `0.271236 m`
- RPE translation RMSE, delta `5 s`: `1.058986 m`
- RPE rotation RMSE, delta `1 s`: `5.057974 deg`
- RPE rotation RMSE, delta `5 s`: `14.587808 deg`
- Sim(3) scale: `130.337221`

Longest continuous segment using a keyframe gap threshold of `2 s`:

- Keyframes: `49`
- ATE translation RMSE: `0.033408 m`
- RPE translation RMSE, delta `1 s`: `0.021014 m`
- RPE translation RMSE, delta `5 s`: `0.059046 m`
- RPE rotation RMSE, delta `1 s`: `3.845205 deg`
- RPE rotation RMSE, delta `5 s`: `8.380309 deg`
- Sim(3) scale: `183.069844`

The all-keyframe ATE is strongly affected by map creation and trajectory
gaps. For interpretation, the longest continuous segment and the RPE values
should be reported together with the coverage and map-reset diagnostics.
Absolute orientation is not used as a primary cross-system metric because
the ground-truth and ORB-SLAM3 camera pose frame conventions were not
independently verified to be identical.

Evaluation artifacts:

- `metrics/ate_aligned_trajectory_rate0.5.csv`
- `metrics/rpe_pairs_rate0.5.csv`
- `metrics/metrics_orbslam3.txt`

## Supplemental Frame-Level Measurement

A separate `0.5x` replay measured the `TrackMonocular` call and recorded
per-callback tracking states. The original trajectory, metrics, and resource
records were not overwritten.

- Summary: `supplemental_measurement/measurement_summary.txt`
- Per-callback CSV: `supplemental_measurement/frame_measurements.csv`
- Measurement log: `supplemental_measurement/measurement_run.log`
- Bag log: `supplemental_measurement/measurement_bag.log`
- Supplemental trajectory:
  `supplemental_measurement/KeyFrameTrajectory_TUM_Format_rate0.5.txt`
- Supplemental resource samples:
  `metrics/resource_samples_measurement.csv`

Results:

- Received callbacks: `1730 / 1819`
- Message delivery rate: `95.1072%`
- Dropped frames: `89`
- Dropped-frame ratio: `4.8928%`
- Mean `TrackMonocular` time: `35.264772 ms`
- Minimum/maximum time: `21.357022 / 142.206951 ms`
- Effective algorithm processing rate: `28.356911 Hz`
- `NOT_INITIALIZED`: `137`
- `OK`: `1593`
- `RECENTLY_LOST`: `0`
- `LOST`: `0`
- Strict success rate among received callbacks: `92.0809%`
- Strict success rate relative to all bag images: `87.5756%`

Supplemental resource statistics:

- Samples: `49`
- Average CPU: `84.13%`
- Maximum CPU: `89.00%`
- Average memory: `3.81%`
- Maximum memory: `4.30%`
- Maximum RSS: `689916 KB`

The timing measures the algorithm call only. It excludes ROS callback
scheduling and image-copy overhead, so it must not be presented as the bag
input frequency.

## RViz Verification

- RViz configuration: `rviz/orbslam3_path.rviz`
- Published topic: `/orb_trajectory`
- Fixed frame: `map`
- Path publisher log: `rviz/path_publisher.log`
- RViz log: `rviz/rviz2.log`
- Replay log: `rviz/rviz_replay.log`
- Screenshot: `rviz/orbslam3_rviz_path.png`

The screenshot shows the saved Street_02 keyframe trajectory as a non-empty
RViz `nav_msgs/Path`. This is a trajectory visualization only; it does not
apply a metric scale to the displayed monocular path.

## Status

The Street_02 ORB-SLAM3 test, Sim(3) trajectory evaluation, frame-level
performance supplement, resource sampling, and RViz trajectory reproduction
are complete. The result directory preserves the main run, the independent
supplemental measurement, the failed initial wrapper attempt, and all
evaluation artifacts.

The result should be reported as a partial monocular trajectory with tracking
degradation and map recreation, not as a complete stable full-sequence
trajectory.
