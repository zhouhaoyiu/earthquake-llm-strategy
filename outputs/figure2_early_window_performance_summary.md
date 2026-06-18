# Figure 2 Early-Window Performance

日期：2026-06-18

## 文件

- 图：`outputs/figures/figure2_early_window_performance.png`
- CSV：`outputs/figure2_early_window_performance.csv`

## 关键结果

- InstanceGM PGA 10 s: MAE reduction 30.6%, q95 reduction 13.6%, combined R2 0.847.
- InstanceGM PGV 10 s: MAE reduction 44.7%, q95 reduction 37.2%, combined R2 0.863.
- K-NET PGA 10 s: MAE reduction 51.8%, q95 reduction 43.0%, combined R2 0.877.

## 解释

The figure shows that early waveform features improve mean error and tail error from the 1 s window onward. Gains generally increase by 10 s, especially for InstanceGM PGV and K-NET PGA. Operational lead-time claims require latency-aware and prospective validation.
