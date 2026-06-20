# Held-Station Bootstrap CI Audit

日期：2026-06-20

## 定位

这个自动审计在同一批 balanced held-station 测试样本上比较 metadata-only 与 metadata + 早窗波形模型。每个 bootstrap replicate 重采样测试记录，并重新计算成对 MAE 降幅。

它回答的是抽样稳定性问题，不替代外部前瞻验证。

## 结果

| 数据集 | 目标 | 测试样本 | MAE 降幅 | 95% CI | bootstrap P(降幅<=0) |
|---|---|---:|---:|---:|---:|
| instancegm | pga | 1000 | 35.5% | 32.1-39.0% | 0.000 |
| instancegm | pgv | 1000 | 52.6% | 49.6-55.6% | 0.000 |
| instancegm | sa03 | 992 | 26.0% | 22.3-29.6% | 0.000 |
| instancegm | sa10 | 1000 | 20.9% | 16.9-24.9% | 0.000 |
| instancegm | sa30 | 942 | 27.8% | 23.9-31.3% | 0.000 |
| knet | pga | 1000 | 49.9% | 46.6-53.1% | 0.000 |

## 解释

六个主 held-station 目标的 95% bootstrap CI 下界全部大于 0，最小下界为 16.9%。最大 bootstrap P(降幅<=0) 为 0.000。

这说明当前 balanced held-station 早窗波形增益不只是一次测试样本抽取下的偶然结果。正文仍应写成经验稳定性证据，不应写成因果证明。

CSV：`work/ground_motion_balanced_station_10s/held_station_bootstrap_ci.csv`
图：`outputs/figures/ground_motion_audit/held_station_bootstrap_ci.png`
