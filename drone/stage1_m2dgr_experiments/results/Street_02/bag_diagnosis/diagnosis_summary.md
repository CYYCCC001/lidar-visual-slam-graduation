# Street_02 ROS 2 Bag Diagnosis

## Source

- Original directory:
  `/home/nvidia/drone/stage1_m2dgr_experiments/bags/Street_02/street2_ros2`
- Database: `street2_ros2.db3`
- Metadata: `metadata.yaml`
- Original database SHA-256:
  `f5fa83186650b9c2386aa585c8dad4d87412c742038a5c89f3c75402351fe61b`

## Database Integrity

The SQLite database passed both checks:

- `PRAGMA integrity_check`: `ok`
- `PRAGMA quick_check`: `ok`
- Topics table rows: `13`
- Messages table rows: `53248`

## Root Cause

The original metadata contains:

```yaml
offered_qos_profiles: []
```

for each topic. The local ROS 2 Humble `ros2 bag info` parser expects this
field to be a string, as used by the previously working `Parking_02` bag:

```yaml
offered_qos_profiles: ''
```

With the original metadata, `ros2 bag info` stops with:

```text
yaml-cpp: error at line 25, column 29: bad conversion
```

This is a metadata-format compatibility issue. The SQLite database itself is
not corrupted.

## Compatibility Diagnosis Copy

A diagnosis-only compatibility directory was created at:

```text
compat_bag/
```

It contains a copied metadata file with the empty QoS lists represented as
empty strings, and a symbolic link to the original database. The original
`street2_ros2/` directory was not modified.

`ros2 bag info compat_bag/` succeeded and reported:

- Duration: `121.347465991 s`
- Total messages: `53248`
- `/camera/color/image_raw`: `1819`
- `/camera/aligned_depth_to_color/image_raw`: `1819`
- `/rslidar_points`: `610`
- `/imu`: `12135`
- `/camera/imu`: `24271`

A limited playback test of `/camera/color/image_raw` also opened the database
successfully and ran without read errors. It was intentionally stopped by
`timeout` after approximately 8 seconds; return code `124` is expected for
that diagnostic stop.

## Next Step

Use `bag_diagnosis/compat_bag/` as a read-only input for the FAST-LIO2 and
ORB-SLAM3 experiments after confirmation. Do not modify the original
`street2_ros2/metadata.yaml`.
