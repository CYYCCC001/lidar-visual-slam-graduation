# ORB-SLAM3 Parking_02 Experiment Record

## Result Directory Layout

- `logs/`: configuration checks, bag playback logs, Pangolin failure log, and
  RViz replay log.
- `metrics/`: ATE/RPE results, aligned trajectory data, performance summary,
  and resource samples.
- `trajectories/`: saved ORB-SLAM3 keyframe trajectories, including the empty
  trajectory produced by the interrupted Pangolin run.
- `rviz/`: RViz2 configuration and screenshots.

## Configuration and Topic Checks

- Camera topic: `/camera/color/image_raw`
- Encoding: `rgb8`
- Image size: `640 x 480`
- Camera settings: `configs/orbslam3_parking2_camera.yaml`
- ROS 2 parameters: `configs/orbslam3_parking2_ros2.yaml`

## Real-Time Trial

- Log: `logs/orbslam3_direct_run.log`
- Trajectory: `trajectories/KeyFrameTrajectory_TUM_Format.txt`
- Result: process completed and trajectory was saved.
- Diagnostic: repeated `Fail to track local map!`; 46 frames were reported
  lost and the active map was reset.
- This trial is not treated as the final ORB-SLAM3 result.

## 0.5x Playback Trial

- Log: `logs/orbslam3_rate0.5_run.log`
- Resource log: `metrics/resource_samples_rate0.5.csv`
- Trajectory: `trajectories/KeyFrameTrajectory_TUM_Format_rate0.5.txt`
- Playback rate: `0.5`
- Result: process completed and trajectory was saved.
- Keyframe trajectory lines: 116
- Diagnostic: 43 `Fail to track local map!` messages; a second map was
  created during the run.
- Average sampled CPU: approximately 97.67%
- Maximum sampled CPU: approximately 112.00%
- Maximum sampled RSS: approximately 712 MB

The slower playback reduced CPU pressure compared with the real-time trial,
but did not make monocular tracking stable enough for final evaluation.

## Trajectory Coverage Audit

The camera image stream contains 2,174 images over approximately 144.942 s.
The saved keyframe trajectories do not cover the full stream:

- Real-time trial: 94 keyframes, 116.965 s keyframe span, approximately
  80.70% of the image time span, maximum keyframe gap 7.868 s.
- 0.5x trial: 116 keyframes, 115.431 s keyframe span, approximately 79.64%
  of the image time span, maximum keyframe gap 7.006 s.

This audit confirms that the trajectories are partial keyframe trajectories,
not complete frame-by-frame trajectories. Any visual ATE/RPE result must
report the coverage and must not fill the missing intervals by interpolation.

## Partial-Trajectory ATE/RPE

Evaluation file: `metrics/metrics_orbslam3.txt`.

The 0.5x playback trajectory is used as the main visual baseline because it
contains more keyframes. It was evaluated with Sim(3) alignment, as required
for monocular SLAM. Missing intervals were not filled.

0.5x trajectory, all saved keyframes:

- Keyframes: 116
- Time coverage: approximately 79.64% of the image stream
- Segment count using a 2 s keyframe-gap threshold: 12
- ATE translation RMSE: `0.022600 m`
- RPE translation RMSE, delta 1 s: `0.013844 m`
- RPE translation RMSE, delta 5 s: `0.028868 m`
- RPE rotation RMSE, delta 1 s: `0.622612 deg`
- RPE rotation RMSE, delta 5 s: `2.358879 deg`
- Sim(3) scale: `8.765791`

0.5x trajectory, longest continuous segment:

- Keyframes: 52
- ATE translation RMSE: `0.017164 m`
- RPE translation RMSE, delta 1 s: `0.013343 m`
- RPE translation RMSE, delta 5 s: `0.026215 m`
- RPE rotation RMSE, delta 1 s: `0.652887 deg`
- RPE rotation RMSE, delta 5 s: `2.310058 deg`

Absolute orientation error is not used as a primary metric because the
ground-truth orientation and ORB-SLAM3 camera pose convention are not in the
same verified frame convention. Relative rotation RPE is used instead.

## RViz2 Reproduction

- Published the 0.5x keyframe trajectory as `nav_msgs/Path`.
- ROS 2 topic: `/orb_trajectory`
- RViz fixed frame: `map`
- RViz configuration: `rviz/orbslam3_path.rviz`
- Screenshot: `rviz/orbslam3_rviz_path.png`
- The screenshot shows the `ORB_SLAM3_Path` display and a non-empty green
  trajectory.
- The trajectory appears compact because the saved monocular trajectory is
  shown before applying a display-only metric scale; its Sim(3) evaluation
  scale was `8.765791`.

## Frequency and Resource Record

Performance record: `metrics/performance.txt`.

- Image input: 2,174 messages over 144.942 s
- Image input frequency: `14.992 Hz`
- Real-time trial average CPU: `126.95%`
- Real-time trial maximum RSS: approximately `641.03 MB`
- 0.5x trial average CPU: `97.67%`
- 0.5x trial maximum RSS: approximately `695.50 MB`
- Real-time trial mean keyframe frequency: `0.795 Hz`
- 0.5x trial mean keyframe frequency: `0.996 Hz`

The ROS 2 wrapper does not publish a dedicated image-processing frequency
topic. Keyframe frequency is therefore reported as an observable output rate,
not as a substitute for the full frame-processing rate.

## Supplemental Frame-Level Measurement

The ROS 2 wrapper was rebuilt with an optional measurement output parameter.
The normal behavior is unchanged when the parameter is absent. A separate
0.5x replay used the same `Parking_02` bag and camera configuration, with
outputs kept under `supplemental_measurement/`.

- Measurement summary: `supplemental_measurement/measurement_summary.txt`
- Per-callback CSV: `supplemental_measurement/frame_measurements.csv`
- Measurement run log: `supplemental_measurement/measurement_run.log`
- Bag playback log: `supplemental_measurement/measurement_bag.log`
- Supplemental trajectory:
  `supplemental_measurement/KeyFrameTrajectory_TUM_Format_rate0.5.txt`

The bag contains `2174` camera image messages. The measurement callback
recorded `2026`, corresponding to a message-level delivery rate of `93.1923%`
and a dropped-frame ratio of `6.8077%`.

The measured operation is the `TrackMonocular` call only, excluding the ROS
subscription callback overhead and image clone. Results:

- Mean processing time: `45.063489 ms`
- Standard deviation: `16.432815 ms`
- Minimum processing time: `20.991600 ms`
- Maximum processing time: `134.877373 ms`
- Effective algorithm processing rate: `22.190914 Hz`

ORB-SLAM3 callback state counts:

- `NOT_INITIALIZED`: `297`
- `OK`: `1683`
- `RECENTLY_LOST`: `45`
- `LOST`: `1`

Using `OK/OK_KLT` as strict successful tracking, the success rate is
`83.0701%` among received callbacks, or `77.4149%` relative to all bag image
messages. Among callbacks after initialization, the successful tracking rate
is `97.3395%`; loss states account for `2.2705%` of received callbacks.

The run log also reports `49` `Fail to track local map!` messages and
`55 Frames set to lost`. These are diagnostic event counters and are kept
separate from the per-callback state statistics. They should not be added to
the frame counts.

The frame-level measurement supplement is already incorporated into this
record. It is retained as independent evidence and did not overwrite the
original ORB-SLAM3 trajectories, metrics, resource samples, or RViz
artifacts. No additional numerical supplement is currently required for the
two requested items:

- single-frame processing time / effective algorithm processing rate;
- tracking success and frame/message loss ratios.

For final reporting, cite the independent files directly:
`supplemental_measurement/measurement_summary.txt`,
`supplemental_measurement/frame_measurements.csv`,
`supplemental_measurement/measurement_run.log`, and
`supplemental_measurement/measurement_bag.log`.
