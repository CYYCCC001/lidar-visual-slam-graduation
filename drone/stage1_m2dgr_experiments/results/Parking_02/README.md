# Parking_02 实验结果

## 目录状态

| 目录 | 状态说明 | 状态 | 用途 |
|---|---|---|---|
| [`fastlio_default/`](fastlio_default/) | [`STATUS.md`](fastlio_default/STATUS.md) | `VALID_FINAL` + `VALID_SUPPLEMENTAL` | FAST-LIO2 默认参数正式结果和补测 |
| [`fastlio_filter03/`](fastlio_filter03/) | [`STATUS.md`](fastlio_filter03/STATUS.md) | `VALID_FINAL` | `filter_size_surf=0.3` 参数对比 |
| [`orbslam3/`](orbslam3/) | [`STATUS.md`](orbslam3/STATUS.md) | `PARTIAL_RESULT` + `VALID_SUPPLEMENTAL` | ORB-SLAM3 部分轨迹及帧级补测 |

## FAST-LIO2 默认组

正式记录：[ `fastlio_default/experiment_record.md`](fastlio_default/experiment_record.md)

- 默认配置：`configs/fastlio_parking2.yaml`
- 正式地图：`fastlio_default/map.pcd`
- 正式指标：`fastlio_default/metrics/`
- 正式 RViz：`fastlio_default/rviz/`
- 补测耗时：`fastlio_default/timing_remeasure/`
- 补测 RViz：`fastlio_default/rviz_remeasure/`

以下目录均为历史失败或未完成尝试，不作为正式结果：

- `failed_start_no_time_20261004_153205/`
- `partial_before_calibration_20261004_153006/`
- `official_run_no_map_20261004_153824/`
- `official_run_no_map_20261004_153951/`

## FAST-LIO2 参数对比

记录：[ `fastlio_filter03/experiment_record.md`](fastlio_filter03/experiment_record.md)

- 对比参数：`filter_size_surf`
- 默认值：`0.5`
- 实验值：`0.3`
- 对比摘要：`fastlio_filter03/parameter_comparison.txt`
- `fastlio_param_test/` 当前为空或未形成有效实验结果，仅保留目录名以
  便追溯，不应作为实验组引用。

## ORB-SLAM3

记录：[ `orbslam3/experiment_record.md`](orbslam3/experiment_record.md)

主结果是部分关键帧轨迹；`supplemental_measurement/` 是有效的帧级补测。
实时运行、Pangolin 失败和空轨迹文件保留用于诊断，不作为最终性能结果。
