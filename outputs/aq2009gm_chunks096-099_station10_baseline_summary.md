# AQ2009GM 096,097,098,099 早窗强震动补验

## 数据范围

- SeisBench AQ2009GM chunks：096, 097, 098, 099
- metadata 总行数：71596
- 有效 PGA/PGV 记录：21895
- 事件数：4145
- 台站数：37
- HDF5 波形格式：measurement=velocity, unit=m/s, component_order=ZNE
- 目标变量：`trace_pga_cmps2` 和 `trace_pgv_cmps`，均来自 AQ2009GM metadata。

这个检查覆盖 4 个 AQ2009GM chunk。它是 2009 L'Aquila 余震数据子集，震级和幅值范围小于 K-NET 强震记录。这里适合作为独立 SeisBench 地震动补验，不应写成完整 AQ2009GM 结论。

## 分组切分

| Holdout | Eligible rows | Eligible groups | Train rows | Test rows | Train groups | Test groups | Overlap |
|---|---:|---:|---:|---:|---:|---:|---:|
| event | 21895 | 4145 | 9000 | 2500 | 3200 | 471 | 0 |
| station | 21895 | 37 | 9000 | 2500 | 26 | 10 | 0 |

## Metadata + early velocity 相对 metadata-only

| Holdout | Target | Window | Metadata MAE | Combined MAE | MAE reduction | Metadata R2 | Combined R2 |
|---|---|---:|---:|---:|---:|---:|---:|
| event | PGA | 1s | 0.202 | 0.150 | 25.8% | 0.864 | 0.922 |
| event | PGA | 3s | 0.202 | 0.112 | 44.6% | 0.864 | 0.952 |
| event | PGA | 10s | 0.202 | 0.084 | 58.6% | 0.864 | 0.975 |
| event | PGV | 1s | 0.191 | 0.143 | 25.1% | 0.872 | 0.928 |
| event | PGV | 3s | 0.191 | 0.092 | 52.2% | 0.872 | 0.963 |
| event | PGV | 10s | 0.191 | 0.033 | 82.9% | 0.872 | 0.992 |
| station | PGA | 1s | 0.549 | 0.247 | 54.9% | 0.089 | 0.795 |
| station | PGA | 3s | 0.549 | 0.173 | 68.5% | 0.089 | 0.898 |
| station | PGA | 10s | 0.549 | 0.108 | 80.3% | 0.089 | 0.961 |
| station | PGV | 1s | 0.539 | 0.262 | 51.4% | 0.077 | 0.789 |
| station | PGV | 3s | 0.539 | 0.157 | 70.9% | 0.077 | 0.908 |
| station | PGV | 10s | 0.539 | 0.047 | 91.3% | 0.077 | 0.982 |

## 解释边界

- 支持的说法：在 AQ2009GM 096,097,098,099 子集内，P 后早窗速度波形为 PGA/PGV 提供了 metadata 之外的信息。
- 暂不支持的说法：这不是完整 AQ2009GM 验证，也不是跨区域强震动完整外部验证。
- 写入主文时应作为 supplementary independent SeisBench check；如果要把它升为主证据，需要下载更多 chunk，并固定事件/台站分组方案。

## 文件

- Metrics CSV: `work/aq2009gm_chunks096-099_station10_baseline/aq2009gm_chunks096-099_metrics.csv`
- Comparison CSV: `work/aq2009gm_chunks096-099_station10_baseline/aq2009gm_chunks096-099_comparison.csv`
- Feature table: `work/aq2009gm_chunks096-099_station10_baseline/aq2009gm_chunks096-099_features.csv.gz`
- Split info: `work/aq2009gm_chunks096-099_station10_baseline/aq2009gm_chunks096-099_split_info.csv`
- Figure: `outputs/figures/ground_motion_audit/aq2009gm_chunks096-099_station10_panel.png`
