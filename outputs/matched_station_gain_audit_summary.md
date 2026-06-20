# Matched Held-Station Gain Audit

日期：2026-06-20

## 定位

这个自动审计只回答一个问题：把 held-station 测试样本裁到训练集震级、距离和目标幅值的 5-95% 覆盖范围内以后，早窗波形增益是否仍然存在。

裁剪使用目标幅值，因此它是事后分布伪影审计，不是可部署预警模型评估。

## 结果

| 数据集 | 目标 | matched 保留比例 | full reduction % | matched reduction % | matched rows |
|---|---|---:|---:|---:|---:|
| instancegm | pga | 0.730 | 35.5 | 38.4 | 730 |
| instancegm | pgv | 0.753 | 52.6 | 52.1 | 753 |
| instancegm | sa03 | 0.772 | 26.0 | 26.6 | 766 |
| instancegm | sa10 | 0.778 | 20.9 | 17.2 | 778 |
| instancegm | sa30 | 0.751 | 27.8 | 24.9 | 707 |
| knet | pga | 0.767 | 49.9 | 50.4 | 767 |

## 解释

所有 matched 子集仍为正增益，最小 matched MAE 降幅为 17.2%。最小保留比例为 0.730。

这个结果降低了“增益只来自 held-station 测试集分布异常”的风险。正文仍应保守表述为 source-path-target shift 下的稳健性证据，不能写成完全 distribution-matched transfer。

CSV：`work/ground_motion_balanced_station_10s/matched_station_gain_audit.csv`
图：`outputs/figures/ground_motion_audit/matched_station_gain_audit.png`
