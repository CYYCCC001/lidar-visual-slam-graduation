# 状态说明：Street_02 ROS 2 bag 诊断

## 总状态

`DIAGNOSTIC_ONLY`。

本目录不是 FAST-LIO2 或 ORB-SLAM3 的算法结果目录，只用于说明
`street2_ros2` 的元数据兼容性、数据库完整性和播放验证过程。

## 诊断结论

- 原始数据库通过 SQLite 完整性检查；
- 原始 `metadata.yaml` 的 `offered_qos_profiles: []` 与本机 ROS 2
  Humble 解析器不兼容；
- `compat_bag/` 是诊断用兼容副本；
- 原始 bag 目录未修改。

## 文件用途

- `diagnosis_summary.md`：完整诊断结论；
- `checksums.txt`：校验和记录；
- `metadata.yaml`：诊断副本的元数据；
- `compat_bag/`：兼容性测试副本；
- `fastlio_short_test/`：短时 FAST-LIO2 播放诊断；
- `image_play_test.log`：图像话题播放测试；
- `fixed_bag_info.txt`、`compat_bag_info.txt`：兼容副本的 bag 信息；
- `ros2_bag_info.txt`、`sqlite_integrity.txt`：原始检查输出，可能为空或
  为未完成命令的留档。

## 使用限制

本目录中的文件不能纳入算法精度、处理频率、资源占用或轨迹质量统计。
算法实验的结果应查看同级的 `fastlio_default/` 或 `orbslam3/`。

