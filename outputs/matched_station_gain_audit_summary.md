# Matched Held-Station Gain Audit

日期：2026-06-20

## 定位

这个自动审计回答两个问题：只把 held-station 测试样本裁到训练集震级和距离的 5-95% 覆盖范围内以后，早窗波形增益是否仍然存在；再加入目标幅值裁剪以后结果是否一致。

`source_path_support` 不使用目标幅值。`matched_train_support` 使用目标幅值，因此后者是事后分布伪影审计，不是可部署预警模型评估。

## Source-path support 结果

| 数据集 | 目标 | 保留比例 | full reduction % | source-path reduction % | rows |
|---|---|---:|---:|---:|---:|
| instancegm | pga | 0.833 | 35.5 | 37.7 | 833 |
| instancegm | pgv | 0.833 | 52.6 | 54.5 | 833 |
| instancegm | sa03 | 0.836 | 26.0 | 27.2 | 829 |
| instancegm | sa10 | 0.833 | 20.9 | 20.1 | 833 |
| instancegm | sa30 | 0.839 | 27.8 | 29.4 | 790 |
| knet | pga | 0.824 | 49.9 | 51.2 | 824 |

## Target-matched 结果

| 数据集 | 目标 | 保留比例 | full reduction % | target-matched reduction % | rows |
|---|---|---:|---:|---:|---:|
| instancegm | pga | 0.730 | 35.5 | 38.4 | 730 |
| instancegm | pgv | 0.753 | 52.6 | 52.1 | 753 |
| instancegm | sa03 | 0.772 | 26.0 | 26.6 | 766 |
| instancegm | sa10 | 0.778 | 20.9 | 17.2 | 778 |
| instancegm | sa30 | 0.751 | 27.8 | 24.9 | 707 |
| knet | pga | 0.767 | 49.9 | 50.4 | 767 |

## 解释

只按震级和距离裁剪时，所有子集仍为正增益，最小 MAE 降幅为 20.1%。最小保留比例为 0.824。

加入目标幅值裁剪后，所有 matched 子集仍为正增益，最小 matched MAE 降幅为 17.2%。最小保留比例为 0.730。

这个结果降低了“增益只来自 held-station 测试集分布异常”的风险。正文仍应保守表述为 source-path shift 下的稳健性证据，不能写成完全 distribution-matched transfer。

CSV：`work/ground_motion_balanced_station_10s/matched_station_gain_audit.csv`
图：`outputs/figures/ground_motion_audit/matched_station_gain_audit.png`
