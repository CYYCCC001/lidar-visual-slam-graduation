# Stage 1 实验结果索引

## 总览

| 数据集 | 算法/实验 | 状态 | 推荐入口 |
|---|---|---|---|
| `Parking_02` | FAST-LIO2 默认参数 `filter_size_surf=0.5` | `VALID_FINAL` + `VALID_SUPPLEMENTAL` | [`STATUS.md`](Parking_02/fastlio_default/STATUS.md) / [`experiment_record.md`](Parking_02/fastlio_default/experiment_record.md) |
| `Parking_02` | FAST-LIO2 参数对比 `filter_size_surf=0.3` | `VALID_FINAL` | [`STATUS.md`](Parking_02/fastlio_filter03/STATUS.md) / [`experiment_record.md`](Parking_02/fastlio_filter03/experiment_record.md) |
| `Parking_02` | ORB-SLAM3 | `PARTIAL_RESULT` + `VALID_SUPPLEMENTAL` | [`STATUS.md`](Parking_02/orbslam3/STATUS.md) / [`experiment_record.md`](Parking_02/orbslam3/experiment_record.md) |
| `Street_02` | FAST-LIO2 默认参数 `filter_size_surf=0.5` | `VALID_FINAL` | [`STATUS.md`](Street_02/fastlio_default/STATUS.md) / [`experiment_record.md`](Street_02/fastlio_default/experiment_record.md) |
| `Street_02` | ORB-SLAM3 | `PARTIAL_RESULT` + `VALID_SUPPLEMENTAL` | [`STATUS.md`](Street_02/orbslam3/STATUS.md) / [`experiment_record.md`](Street_02/orbslam3/experiment_record.md) |
| `Street_02` | ROS 2 bag 兼容性诊断 | `DIAGNOSTIC_ONLY` | [`STATUS.md`](Street_02/bag_diagnosis/STATUS.md) / [`diagnosis_summary.md`](Street_02/bag_diagnosis/diagnosis_summary.md) |

## Parking_02

### FAST-LIO2 默认组

目录：[`Parking_02/fastlio_default/`](Parking_02/fastlio_default/)

- 正式 ATE/RPE、地图、资源记录和 RViz 截图位于该目录根部及其
  `fastlio_logs/`、`metrics/`、`rviz/` 子目录。
- 补充处理耗时位于 `timing_remeasure/`。
- 补充 RViz 复现位于 `rviz_remeasure/`。
- `failed_start_no_time_*`、`partial_before_calibration_*` 和
  `official_run_no_map_*` 是失败或未完成的历史尝试，不作为正式结果。

关键正式结果：

- ATE position RMSE：`0.303657 m`
- 正式地图：`map.pcd`
- 补测平均处理耗时：`112.914781 ms`
- 补测有效处理频率：`8.856236 Hz`

### FAST-LIO2 参数对比组

目录：[`Parking_02/fastlio_filter03/`](Parking_02/fastlio_filter03/)

- 配置：`filter_size_surf: 0.3`
- 默认配置未修改。
- 对比摘要：[`parameter_comparison.txt`](Parking_02/fastlio_filter03/parameter_comparison.txt)
- 阶段总结：[`stage1_summary.txt`](Parking_02/fastlio_filter03/stage1_summary.txt)
- 该目录是有效参数对比实验，不是默认组结果。

### ORB-SLAM3

目录：[`Parking_02/orbslam3/`](Parking_02/orbslam3/)

- 主结果是 `0.5x` 播放得到的部分关键帧轨迹。
- 帧级处理耗时、接收率和跟踪状态位于 `supplemental_measurement/`。
- 空轨迹、Pangolin 失败尝试和实时诊断记录不应作为最终轨迹引用。

## Street_02

### FAST-LIO2 默认组

目录：[`Street_02/fastlio_default/`](Street_02/fastlio_default/)

- 根目录中的 `run.log`、`map.pcd`、`metrics/`、`fastlio_logs/` 和
  `rviz/` 构成正式结果。
- `run_20261006_*` 是历史重复/中间运行，仅用于追溯，不作为最终结果。

关键正式结果：

- ATE position RMSE：`8.136328 m`
- 平均处理耗时：`158.225461 ms`
- 有效处理频率：`6.320095 Hz`
- 地图点数：`4,258,510`

### ORB-SLAM3

目录：[`Street_02/orbslam3/`](Street_02/orbslam3/)

- 主 `0.5x` 结果为部分单目轨迹，存在较大轨迹空段和地图重建。
- 帧级补测保存在 `supplemental_measurement/`，用于报告处理耗时、
  接收/丢帧比例和跟踪成功率。
- `metrics/resource_samples_rate0.5.csv` 与其对应的初次包装器运行属于
  诊断记录；应优先使用 `resource_samples_rate0.5_retry.csv`。

### ROS 2 bag 诊断

目录：[`Street_02/bag_diagnosis/`](Street_02/bag_diagnosis/)

该目录只记录 `street2_ros2` 的元数据兼容性和播放诊断。原始 bag 未修改；
`compat_bag/` 是诊断用兼容副本，不作为算法结果目录。

## 推荐引用规则

1. 论文或最终报告首先引用状态为 `VALID_FINAL` 的
   `experiment_record.md` 和 `metrics/` 文件。
2. 处理耗时、有效频率、丢帧率和跟踪成功率引用对应的
   `supplemental_measurement/` 或 `timing_remeasure/` 文件，并标明是补测。
3. ORB-SLAM3 必须同时报告轨迹覆盖率、关键帧数量、地图重建或跟踪失败等
   限制，不能将部分关键帧轨迹表述为完整逐帧轨迹。
4. `DIAGNOSTIC_ONLY`、`INVALID_ATTEMPT` 和 `HISTORICAL_RUN` 文件仅用于
   复盘和问题定位，不纳入正式性能对比。
