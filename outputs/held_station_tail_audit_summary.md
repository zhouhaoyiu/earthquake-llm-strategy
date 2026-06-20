# Held-Station Strong-Tail Audit

日期：2026-06-20

## 定位

这个自动审计只看 balanced held-station 测试集里目标最大的 top 10% 和 top 5% 样本，检查平均精度增益是否也出现在强震动尾部。

Factor-2 漏报定义为预测 log10 目标低于观测值 0.3 以上。

## 结果

| 数据集 | 目标 | Tail | rows | tail MAE 降幅 | factor-2 漏报变化 |
|---|---|---:|---:|---:|---:|
| instancegm | pga | top 10% | 100 | 28.2% | 0.170 |
| instancegm | pga | top 5% | 50 | 32.8% | 0.320 |
| instancegm | pgv | top 10% | 100 | 37.1% | 0.050 |
| instancegm | pgv | top 5% | 50 | 35.8% | 0.080 |
| instancegm | sa03 | top 10% | 100 | 22.3% | 0.050 |
| instancegm | sa03 | top 5% | 50 | 21.4% | 0.020 |
| instancegm | sa10 | top 10% | 100 | 19.4% | -0.010 |
| instancegm | sa10 | top 5% | 50 | 18.9% | 0.040 |
| instancegm | sa30 | top 10% | 95 | 24.2% | 0.074 |
| instancegm | sa30 | top 5% | 48 | 20.4% | -0.042 |
| knet | pga | top 10% | 100 | 67.9% | 0.390 |
| knet | pga | top 5% | 50 | 66.0% | 0.360 |

## 解释

top 5% 强目标样本里，tail MAE 降幅范围为 18.9% 到 66.0%。
factor-2 漏报率变化范围为 -0.042 到 0.360，负值表示早窗波形模型在该尾部子集里的 factor-2 漏报率更高。

这个结果应写成强尾部误差边界，不写成尾部问题已解决。

CSV：`work/ground_motion_balanced_station_10s/held_station_tail_audit.csv`
图：`outputs/figures/ground_motion_audit/held_station_tail_audit.png`
