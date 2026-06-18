# AQ2009GM 096,097,098 早窗强震动补验

## 数据范围

- SeisBench AQ2009GM chunks：096, 097, 098
- metadata 总行数：48743
- 有效 PGA/PGV 记录：14814
- 事件数：2939
- 台站数：32
- HDF5 波形格式：measurement=velocity, unit=m/s, component_order=ZNE
- 目标变量：`trace_pga_cmps2` 和 `trace_pgv_cmps`，均来自 AQ2009GM metadata。

这个检查覆盖 3 个 AQ2009GM chunk。它是 2009 L'Aquila 余震数据子集，震级和幅值范围小于 K-NET 强震记录。这里适合作为独立 SeisBench 地震动补验，不应写成完整 AQ2009GM 结论。

## 分组切分

| Holdout | Eligible rows | Eligible groups | Train rows | Test rows | Train groups | Test groups | Overlap |
|---|---:|---:|---:|---:|---:|---:|---:|
| event | 14814 | 2939 | 7000 | 2000 | 2315 | 393 | 0 |
| station | 14814 | 32 | 7000 | 2000 | 22 | 9 | 0 |

## Metadata + early velocity 相对 metadata-only

| Holdout | Target | Window | Metadata MAE | Combined MAE | MAE reduction | Metadata R2 | Combined R2 |
|---|---|---:|---:|---:|---:|---:|---:|
| event | PGA | 1s | 0.192 | 0.143 | 25.6% | 0.895 | 0.940 |
| event | PGA | 3s | 0.192 | 0.108 | 43.6% | 0.895 | 0.961 |
| event | PGA | 10s | 0.192 | 0.081 | 58.0% | 0.895 | 0.981 |
| event | PGV | 1s | 0.187 | 0.141 | 24.7% | 0.898 | 0.943 |
| event | PGV | 3s | 0.187 | 0.091 | 51.5% | 0.898 | 0.970 |
| event | PGV | 10s | 0.187 | 0.038 | 79.7% | 0.898 | 0.992 |
| station | PGA | 1s | 0.385 | 0.245 | 36.5% | 0.593 | 0.813 |
| station | PGA | 3s | 0.385 | 0.220 | 43.0% | 0.593 | 0.842 |
| station | PGA | 10s | 0.385 | 0.147 | 61.8% | 0.593 | 0.933 |
| station | PGV | 1s | 0.356 | 0.229 | 35.7% | 0.650 | 0.849 |
| station | PGV | 3s | 0.356 | 0.168 | 52.7% | 0.650 | 0.893 |
| station | PGV | 10s | 0.356 | 0.037 | 89.5% | 0.650 | 0.989 |

## 解释边界

- 支持的说法：在 AQ2009GM 096,097,098 子集内，P 后早窗速度波形为 PGA/PGV 提供了 metadata 之外的信息。
- 暂不支持的说法：这不是完整 AQ2009GM 验证，也不是跨区域强震动完整外部验证。
- 写入主文时应作为 supplementary independent SeisBench check；如果要把它升为主证据，需要下载更多 chunk，并固定事件/台站分组方案。

## 文件

- Metrics CSV: `work/aq2009gm_chunks096-098_station10_baseline/aq2009gm_chunks096-098_metrics.csv`
- Comparison CSV: `work/aq2009gm_chunks096-098_station10_baseline/aq2009gm_chunks096-098_comparison.csv`
- Feature table: `work/aq2009gm_chunks096-098_station10_baseline/aq2009gm_chunks096-098_features.csv.gz`
- Split info: `work/aq2009gm_chunks096-098_station10_baseline/aq2009gm_chunks096-098_split_info.csv`
- Figure: `outputs/figures/ground_motion_audit/aq2009gm_chunks096-098_station10_panel.png`
