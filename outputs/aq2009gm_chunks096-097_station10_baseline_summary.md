# AQ2009GM 096,097 早窗强震动补验

## 数据范围

- SeisBench AQ2009GM chunks：096, 097
- metadata 总行数：28464
- 有效 PGA/PGV 记录：8794
- 事件数：1799
- 台站数：31
- HDF5 波形格式：measurement=velocity, unit=m/s, component_order=ZNE
- 目标变量：`trace_pga_cmps2` 和 `trace_pgv_cmps`，均来自 AQ2009GM metadata。

这个检查覆盖 2 个 AQ2009GM chunk。它是 2009 L'Aquila 余震数据子集，震级和幅值范围小于 K-NET 强震记录。这里适合作为独立 SeisBench 地震动补验，不应写成完整 AQ2009GM 结论。

## 分组切分

| Holdout | Eligible rows | Eligible groups | Train rows | Test rows | Train groups | Test groups | Overlap |
|---|---:|---:|---:|---:|---:|---:|---:|
| event | 8794 | 1799 | 5000 | 1400 | 1459 | 287 | 0 |
| station | 8794 | 31 | 5000 | 1400 | 21 | 9 | 0 |

## Metadata + early velocity 相对 metadata-only

| Holdout | Target | Window | Metadata MAE | Combined MAE | MAE reduction | Metadata R2 | Combined R2 |
|---|---|---:|---:|---:|---:|---:|---:|
| event | PGA | 1s | 0.203 | 0.151 | 25.6% | 0.866 | 0.921 |
| event | PGA | 3s | 0.203 | 0.119 | 41.5% | 0.866 | 0.944 |
| event | PGA | 10s | 0.203 | 0.091 | 55.4% | 0.866 | 0.967 |
| event | PGV | 1s | 0.202 | 0.145 | 28.1% | 0.858 | 0.925 |
| event | PGV | 3s | 0.202 | 0.095 | 53.2% | 0.858 | 0.955 |
| event | PGV | 10s | 0.202 | 0.042 | 79.2% | 0.858 | 0.983 |
| station | PGA | 1s | 0.402 | 0.284 | 29.3% | 0.531 | 0.757 |
| station | PGA | 3s | 0.402 | 0.247 | 38.5% | 0.531 | 0.796 |
| station | PGA | 10s | 0.402 | 0.184 | 54.1% | 0.531 | 0.899 |
| station | PGV | 1s | 0.318 | 0.251 | 20.8% | 0.679 | 0.813 |
| station | PGV | 3s | 0.318 | 0.181 | 42.9% | 0.679 | 0.875 |
| station | PGV | 10s | 0.318 | 0.049 | 84.7% | 0.679 | 0.984 |

## 解释边界

- 支持的说法：在 AQ2009GM 096,097 子集内，P 后早窗速度波形为 PGA/PGV 提供了 metadata 之外的信息。
- 暂不支持的说法：这不是完整 AQ2009GM 验证，也不是跨区域强震动完整外部验证。
- 写入主文时应作为 supplementary independent SeisBench check；如果要把它升为主证据，需要下载更多 chunk，并固定事件/台站分组方案。

## 文件

- Metrics CSV: `work/aq2009gm_chunks096-097_station10_baseline/aq2009gm_chunks096-097_metrics.csv`
- Comparison CSV: `work/aq2009gm_chunks096-097_station10_baseline/aq2009gm_chunks096-097_comparison.csv`
- Feature table: `work/aq2009gm_chunks096-097_station10_baseline/aq2009gm_chunks096-097_features.csv.gz`
- Split info: `work/aq2009gm_chunks096-097_station10_baseline/aq2009gm_chunks096-097_split_info.csv`
- Figure: `outputs/figures/ground_motion_audit/aq2009gm_chunks096-097_station10_panel.png`
