# 状态说明：Parking_02 FAST-LIO2 参数对比

## 总状态

`VALID_FINAL`。

这是阶段一第七步的有效参数对比实验，不是默认组结果。

## 实验定义

- 对比参数：`filter_size_surf`
- 默认值：`0.5`
- 实验值：`0.3`
- 使用配置：`configs/fastlio_parking2_filter03.yaml`
- 默认配置：`configs/fastlio_parking2.yaml`
- 默认配置未被修改。

## 正式证据

- 实验记录：`experiment_record.md`
- 参数对比摘要：`parameter_comparison.txt`
- 阶段总结：`stage1_summary.txt`
- 运行日志：`run.log`
- bag 播放日志：`bag_play.log`
- 轨迹和状态日志：`fastlio_logs/`
- 地图：`map.pcd`
- ATE/RPE 和性能指标：`metrics/`
- RViz 截图：`rviz/`

## 对比注意事项

默认组耗时来自：
`../fastlio_default/timing_remeasure/`。

两次运行处理的帧数不同，因此耗时和有效频率是描述性对比，不应表述为
严格相同帧集合上的基准测试。

## 其他目录

`../fastlio_param_test/` 是未形成有效结果的遗留目录，不属于本实验组，
也不应与本目录的 `filter_size_surf: 0.3` 结果混用。

