# Balanced Held-Station Distribution Audit

日期：2026-06-18

## 定位

这个审计回答一个审稿风险：balanced held-station 的测试集是否因为震级、距离或目标幅值分布异常才显得容易或困难。它不替代 held-station 结果，只给 split provenance 加一层可检查证据。

## 结果

| 数据集 | 变量 | train median | test median | train q05-q95 | test q05-q95 | KS | overlap |
|---|---|---:|---:|---:|---:|---:|---:|
| InstanceGM | source_magnitude | 2.2 | 2.4 | 1-3.4 | 1.2-3.6 | 0.14 | 0.86 |
| InstanceGM | source_distance_km | 44.3 | 70.6 | 8.76-151 | 19.2-192 | 0.25 | 0.76 |
| InstanceGM | target_log10_pga | -1.68 | -2.11 | -2.81--0.0523 | -3.06--0.541 | 0.23 | 0.78 |
| K-NET | source_magnitude | 4.3 | 4.3 | 3.6-5.8 | 3.5-5.9 | 0.05 | 0.92 |
| K-NET | source_distance_km | 54.4 | 57.7 | 13.2-124 | 13-120 | 0.05 | 0.93 |
| K-NET | target_log10_pga | 0.947 | 0.888 | 0.407-1.82 | 0.412-1.81 | 0.06 | 0.91 |

## 解释

InstanceGM 的 held-station test 在震级和距离上与训练集存在可见偏移，尤其距离更远，说明它不是一个容易测试集；combined 模型仍保持明显提升。K-NET 的距离和 PGA 分布覆盖较好，震级分布有中等差异。

这支持一个更稳的写法：balanced held-station 不是随机同分布复现，仍保留 source-path-target shift；早窗信息在这种 shift 下仍有增益。不要写成完全 distribution-matched station transfer。

图：`outputs/figures/ground_motion_audit/balanced_station_distribution_audit_panel.png`
CSV：`work/ground_motion_balanced_station_10s/balanced_station_distribution_audit.csv`
