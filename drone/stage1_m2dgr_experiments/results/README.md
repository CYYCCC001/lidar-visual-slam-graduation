# Stage 1 实验结果目录

本目录保存 M2DGR `Parking_02` 和 `Street_02` 数据集的 FAST-LIO2、
ORB-SLAM3 及相关补测、诊断和历史运行记录。

## 状态标签

- `VALID_FINAL`：可作为该组实验的正式结果。
- `VALID_SUPPLEMENTAL`：有效补测证据，不覆盖正式结果。
- `PARTIAL_RESULT`：算法运行完成，但轨迹或覆盖范围不完整，引用时必须同时说明限制。
- `DIAGNOSTIC_ONLY`：用于检查 bag、兼容性、资源采样或复现过程，不纳入正式算法结果。
- `INVALID_ATTEMPT`：失败或未完成的尝试，仅用于追溯问题。
- `HISTORICAL_RUN`：已保留的重复/中间运行，不作为当前最终结果。

## 快速入口

- [完整结果索引](RESULTS_INDEX.md)
- [Parking_02 数据集说明](Parking_02/README.md)
- [Street_02 数据集说明](Street_02/README.md)

## 整理原则

原始日志、地图、轨迹和截图均保留。当前只增加索引和说明文件，不删除、
覆盖或移动已有实验数据；因此历史文件中的相对路径仍然有效。

正式结果优先查看对应算法目录下的 `experiment_record.md`、`metrics/`、
`rviz/` 和地图/轨迹文件。补测结果单独作为支持证据，不能与正式结果
混写或替换。

