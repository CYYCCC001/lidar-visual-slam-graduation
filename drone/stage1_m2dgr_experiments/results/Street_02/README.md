# Street_02 实验结果

## 目录状态

| 目录 | 状态说明 | 状态 | 用途 |
|---|---|---|---|
| [`fastlio_default/`](fastlio_default/) | [`STATUS.md`](fastlio_default/STATUS.md) | `VALID_FINAL` | FAST-LIO2 默认参数正式结果 |
| [`orbslam3/`](orbslam3/) | [`STATUS.md`](orbslam3/STATUS.md) | `PARTIAL_RESULT` + `VALID_SUPPLEMENTAL` | ORB-SLAM3 部分轨迹及帧级补测 |
| [`bag_diagnosis/`](bag_diagnosis/) | [`STATUS.md`](bag_diagnosis/STATUS.md) | `DIAGNOSTIC_ONLY` | ROS 2 bag 元数据兼容性和播放诊断 |
| [`fastlio/`](fastlio/) | `INVALID_ATTEMPT` 或未完成 | 历史遗留目录，不能作为正式结果 |

## FAST-LIO2

记录：[ `fastlio_default/experiment_record.md`](fastlio_default/experiment_record.md)

- 配置副本：`fastlio_default/config_used.yaml`
- 正式地图：`fastlio_default/map.pcd`
- 正式指标：`fastlio_default/metrics/`
- 正式日志：`fastlio_default/run.log`、`bag_play.log`
- RViz 证据：`fastlio_default/rviz/`

`run_20261006_135046/`、`run_20261006_135200/`、
`run_20261006_135239/` 和 `run_20261006_135802/` 是历史重复或中间运行，
保留用于追溯，不作为最终结果。

## ORB-SLAM3

记录：[ `orbslam3/experiment_record.md`](orbslam3/experiment_record.md)

主结果为部分单目关键帧轨迹，不能表述为完整稳定的全序列轨迹。有效的
处理耗时、接收/丢帧比例和跟踪状态补测位于：

- `orbslam3/supplemental_measurement/`
- `orbslam3/metrics/resource_samples_measurement.csv`

初次包装器运行和相关资源采样属于诊断记录；最终引用时优先使用
`logs/orbslam3_rate0.5_retry.log`、对应 bag 日志和
`metrics/resource_samples_rate0.5_retry.csv`。

## Bag 诊断

记录：[ `bag_diagnosis/diagnosis_summary.md`](bag_diagnosis/diagnosis_summary.md)

原始 `bags/Street_02/street2_ros2/` 未修改。`compat_bag/` 仅为元数据兼容性
诊断副本，不是新的算法输入结果，也不应与正式结果混在一起。
