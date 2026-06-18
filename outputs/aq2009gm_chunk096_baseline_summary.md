# AQ2009GM chunk096 早窗强震动补验

## 数据范围

- SeisBench AQ2009GM chunk096 metadata 总行数：11223
- 有效 PGA/PGV 记录：3433
- 事件数：762
- 台站数：23
- HDF5 波形格式：measurement=velocity, unit=m/s, component_order=ZNE
- 目标变量：`trace_pga_cmps2` 和 `trace_pgv_cmps`，均来自 AQ2009GM metadata。

这个检查只覆盖 chunk096。它是 2009 L'Aquila 余震数据的单 chunk 子集，震级和幅值范围小于 K-NET 强震记录。这里适合作为独立 SeisBench 地震动补验，不应写成完整 AQ2009GM 结论。

## 分组切分

| Holdout | Eligible rows | Eligible groups | Train rows | Test rows | Train groups | Test groups | Overlap |
|---|---:|---:|---:|---:|---:|---:|---:|
| event | 3433 | 762 | 2500 | 700 | 603 | 156 | 0 |
| station | 3433 | 23 | 2500 | 700 | 17 | 5 | 0 |

## Metadata + early velocity 相对 metadata-only

| Holdout | Target | Window | Metadata MAE | Combined MAE | MAE reduction | Metadata R2 | Combined R2 |
|---|---|---:|---:|---:|---:|---:|---:|
| event | PGA | 1s | 0.199 | 0.144 | 27.6% | 0.877 | 0.929 |
| event | PGA | 3s | 0.199 | 0.114 | 42.8% | 0.877 | 0.955 |
| event | PGA | 10s | 0.199 | 0.090 | 54.8% | 0.877 | 0.970 |
| event | PGV | 1s | 0.195 | 0.145 | 25.3% | 0.872 | 0.927 |
| event | PGV | 3s | 0.195 | 0.089 | 54.1% | 0.872 | 0.964 |
| event | PGV | 10s | 0.195 | 0.046 | 76.2% | 0.872 | 0.985 |
| station | PGA | 1s | 0.330 | 0.262 | 20.4% | 0.748 | 0.845 |
| station | PGA | 3s | 0.330 | 0.192 | 41.8% | 0.748 | 0.906 |
| station | PGA | 10s | 0.330 | 0.157 | 52.3% | 0.748 | 0.944 |
| station | PGV | 1s | 0.263 | 0.240 | 8.6% | 0.838 | 0.867 |
| station | PGV | 3s | 0.263 | 0.122 | 53.5% | 0.838 | 0.954 |
| station | PGV | 10s | 0.263 | 0.057 | 78.1% | 0.838 | 0.984 |

## 解释边界

- 支持的说法：在 AQ2009GM chunk096 内，P 后早窗速度波形为 PGA/PGV 提供了 metadata 之外的信息。
- 暂不支持的说法：这不是完整 AQ2009GM 验证，也不是跨区域强震动完整外部验证。
- 写入主文时应作为 supplementary independent SeisBench check；如果要把它升为主证据，需要下载更多 chunk，并固定事件/台站分组方案。

## 文件

- Metrics CSV: `work/aq2009gm_chunk096_baseline/aq2009gm_chunk096_metrics.csv`
- Comparison CSV: `work/aq2009gm_chunk096_baseline/aq2009gm_chunk096_comparison.csv`
- Feature table: `work/aq2009gm_chunk096_baseline/aq2009gm_chunk096_features.csv.gz`
- Split info: `work/aq2009gm_chunk096_baseline/aq2009gm_chunk096_split_info.csv`
- Figure: `outputs/figures/ground_motion_audit/aq2009gm_chunk096_panel.png`
