# AQ2009GM 096,097,098,099,100 早窗强震动补验

## 数据范围

- SeisBench AQ2009GM chunks：096, 097, 098, 099, 100
- metadata 总行数：101218
- 有效 PGA/PGV 记录：30737
- 事件数：5497
- 台站数：50
- HDF5 波形格式：measurement=velocity, unit=m/s, component_order=ZNE
- 目标变量：`trace_pga_cmps2` 和 `trace_pgv_cmps`，均来自 AQ2009GM metadata。

这个检查覆盖 5 个 AQ2009GM chunk。它是 2009 L'Aquila 余震数据子集，震级和幅值范围小于 K-NET 强震记录。这里适合作为独立 SeisBench 地震动补验，不应写成完整 AQ2009GM 结论。

## 分组切分

| Holdout | Eligible rows | Eligible groups | Train rows | Test rows | Train groups | Test groups | Overlap |
|---|---:|---:|---:|---:|---:|---:|---:|
| event | 30737 | 5497 | 12000 | 3500 | 4217 | 659 | 0 |
| station | 30737 | 50 | 12000 | 3500 | 35 | 11 | 0 |

## Metadata + early velocity 相对 metadata-only

| Holdout | Target | Window | Metadata MAE | Combined MAE | MAE reduction | Metadata R2 | Combined R2 |
|---|---|---:|---:|---:|---:|---:|---:|
| event | PGA | 1s | 0.215 | 0.153 | 28.7% | 0.850 | 0.924 |
| event | PGA | 3s | 0.215 | 0.115 | 46.5% | 0.850 | 0.953 |
| event | PGA | 10s | 0.215 | 0.079 | 63.0% | 0.850 | 0.977 |
| event | PGV | 1s | 0.206 | 0.147 | 28.6% | 0.856 | 0.928 |
| event | PGV | 3s | 0.206 | 0.096 | 53.2% | 0.856 | 0.961 |
| event | PGV | 10s | 0.206 | 0.034 | 83.5% | 0.856 | 0.990 |
| station | PGA | 1s | 0.510 | 0.187 | 63.4% | 0.134 | 0.871 |
| station | PGA | 3s | 0.510 | 0.140 | 72.5% | 0.134 | 0.918 |
| station | PGA | 10s | 0.510 | 0.120 | 76.5% | 0.134 | 0.946 |
| station | PGV | 1s | 0.486 | 0.190 | 61.0% | 0.108 | 0.874 |
| station | PGV | 3s | 0.486 | 0.114 | 76.6% | 0.108 | 0.933 |
| station | PGV | 10s | 0.486 | 0.037 | 92.3% | 0.108 | 0.987 |

## 解释边界

- 支持的说法：在 AQ2009GM 096,097,098,099,100 子集内，P 后早窗速度波形为 PGA/PGV 提供了 metadata 之外的信息。
- 暂不支持的说法：这不是完整 AQ2009GM 验证，也不是跨区域强震动完整外部验证。
- 写入主文时应作为 supplementary independent SeisBench check；如果要把它升为主证据，需要下载更多 chunk，并固定事件/台站分组方案。

## 文件

- Metrics CSV: `work/aq2009gm_chunks096-100_station12_baseline/aq2009gm_chunks096-100_metrics.csv`
- Comparison CSV: `work/aq2009gm_chunks096-100_station12_baseline/aq2009gm_chunks096-100_comparison.csv`
- Feature table: `work/aq2009gm_chunks096-100_station12_baseline/aq2009gm_chunks096-100_features.csv.gz`
- Split info: `work/aq2009gm_chunks096-100_station12_baseline/aq2009gm_chunks096-100_split_info.csv`
- Figure: `outputs/figures/ground_motion_audit/aq2009gm_chunks096-100_station12_panel.png`
