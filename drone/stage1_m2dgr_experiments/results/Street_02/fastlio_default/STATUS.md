# 状态说明：Street_02 FAST-LIO2 默认组

## 总状态

`VALID_FINAL`。

这是 `filter_size_surf: 0.5` 的正式 FAST-LIO2 结果。根目录中的结果文件
构成当前最终组，不应被下面的历史运行目录替换。

## 正式证据

- 实验记录：`experiment_record.md`
- 使用配置副本：`config_used.yaml`
- 主运行日志：`run.log`
- bag 播放日志：`bag_play.log`
- 资源采样：`resource_samples.csv`
- 轨迹和状态日志：`fastlio_logs/`
- 地图：`map.pcd`
- 地图保存日志：`map_save.log`
- ATE/RPE：`metrics/`
- RViz 日志和截图：`rviz/`

正式记录中的 ATE position RMSE 为 `8.136328 m`，平均单帧处理耗时为
`158.225461 ms`，有效处理频率为 `6.320095 Hz`。

## 历史运行

以下目录是重复、试运行或中间运行留档，不作为正式结果：

- `run_20261006_135046/`
- `run_20261006_135200/`
- `run_20261006_135239/`
- `run_20261006_135802/`

这些目录中的日志只能用于复盘启动、播放、资源采样或地图保存过程。

## 引用规则

正式报告优先引用本目录根部文件和 `metrics/`、`rviz/`、`fastlio_logs/`。
历史运行目录不得与根目录结果混合统计。

