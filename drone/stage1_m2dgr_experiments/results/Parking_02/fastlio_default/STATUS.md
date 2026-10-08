# 状态说明：Parking_02 FAST-LIO2 默认组

## 总状态

`VALID_FINAL`，并包含 `VALID_SUPPLEMENTAL` 补测证据。

这是 `filter_size_surf: 0.5` 的默认参数结果。正式地图、轨迹、
ATE/RPE、资源记录和 RViz 结果均保留在本目录根部及标准子目录中。

## 正式结果

- 实验记录：`experiment_record.md`
- 主运行日志：`run.log`
- 主资源采样：`resource_samples.csv`
- 轨迹和状态日志：`fastlio_logs/`
- 地图：`map.pcd`
- 精度指标：`metrics/`
- 正式 RViz 截图：`rviz/parking2_rviz_midrun.png`、
  `rviz/parking2_rviz_final.png`

正式 ATE position RMSE 为 `0.303657 m`。默认组的实验配置和结果未被
参数对比实验覆盖。

## 有效补测

补测不替换正式结果，只用于补充性能和可视化证据：

- 处理耗时 CSV：`timing_remeasure/fast_lio_time_log.csv`
- 耗时摘要：`timing_remeasure/timing.txt`
- 补测运行日志：`timing_remeasure_run.log`
- 补测 bag 日志：`timing_remeasure_bag.log`
- 补测 RViz：`rviz_remeasure/`

## 历史无效或未完成运行

以下目录保留用于问题追溯，不纳入正式结果：

- `failed_start_no_time_20261004_153205/`：启动失败，未形成完整结果；
- `partial_before_calibration_20261004_153006/`：校准前的部分运行；
- `official_run_no_map_20261004_153824/`：未完成地图保存；
- `official_run_no_map_20261004_153951/`：未完成正式结果。

## 引用规则

默认性能和精度引用根目录正式文件；单帧处理耗时和有效处理频率引用
`timing_remeasure/`，并在报告中注明为补测。

