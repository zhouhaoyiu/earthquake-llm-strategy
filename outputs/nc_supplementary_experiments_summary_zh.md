# 补充实验摘要

本文件汇总三个补强实验：目标区校准样本量、轻量波形编码器对照、四域早期波形 transfer。它们补充主文边界结论，不替代主 held-station 和外部数据验证。

## 1 目标区校准样本量

source-domain conformal interval 在跨区应用时欠覆盖。只估计一个目标区 offset 和 conformal 残差宽度后，50 条目标区校准记录已经使两个窗口的覆盖率中位数接近 0.90；100 条记录更稳定。区间宽度仍然很大，说明校准修复的是覆盖率，不是把跨区问题变成域内问题。

| P窗长/s | 校准条数 | 覆盖率中位数 | 覆盖率IQR | 区间宽度中位数(log10) |
|---:|---:|---:|---:|---:|
| 2 | 10 | 0.867 | 0.811-0.924 | 1.980 |
| 2 | 50 | 0.888 | 0.863-0.911 | 2.039 |
| 2 | 100 | 0.905 | 0.869-0.923 | 2.161 |
| 2 | 1000 | 0.902 | 0.889-0.922 | 2.172 |
| 5 | 10 | 0.882 | 0.800-0.921 | 1.926 |
| 5 | 50 | 0.882 | 0.859-0.920 | 2.008 |
| 5 | 100 | 0.902 | 0.873-0.925 | 2.080 |
| 5 | 1000 | 0.901 | 0.889-0.917 | 2.128 |

source-domain conformal baseline：

| P窗长/s | 源域覆盖率中位数 | 源域区间宽度中位数(log10) |
|---:|---:|---:|
| 2 | 0.468 | 1.228 |
| 5 | 0.298 | 0.826 |

## 2 轻量波形编码器对照

小型 CNN 证明端到端早期波形可以学习到强震动信息；但在当前样本量和训练设置下，它没有超过稳定树模型和手工早窗统计。该结果支持本文选择保守模型：主结论来自公开数据、划分和不确定性边界，不来自复杂模型冲分。

| P窗长/s | 数据集 | 模型 | 目标数 | MAE中位数(log10) | R2中位数 |
|---:|---|---|---:|---:|---:|
| 3 | instancegm | cnn_waveform | 5 | 0.519 | 0.132 |
| 3 | instancegm | cnn_waveform_metadata | 5 | 0.337 | 0.622 |
| 3 | instancegm | hgb_metadata_plus_early_waveform | 5 | 0.239 | 0.822 |
| 3 | knet | cnn_waveform | 1 | 0.213 | 0.553 |
| 3 | knet | cnn_waveform_metadata | 1 | 0.198 | 0.609 |
| 3 | knet | hgb_metadata_plus_early_waveform | 1 | 0.178 | 0.688 |
| 10 | instancegm | cnn_waveform | 5 | 0.506 | 0.171 |
| 10 | instancegm | cnn_waveform_metadata | 5 | 0.351 | 0.613 |
| 10 | instancegm | hgb_metadata_plus_early_waveform | 5 | 0.210 | 0.834 |
| 10 | knet | cnn_waveform | 1 | 0.161 | 0.730 |
| 10 | knet | cnn_waveform_metadata | 1 | 0.139 | 0.799 |
| 10 | knet | hgb_metadata_plus_early_waveform | 1 | 0.105 | 0.877 |

## 3 四域早期波形 transfer

只用早期波形统计进行跨域迁移时，误差相对目标域训练保持明显 penalty。目标区 offset 校准能降低 penalty，但不能消除跨区域差异。这一层把主文结论从“域内可预测”推进到“跨区域可预测性有边界”。

| P窗长/s | 校准方式 | MAE penalty中位数 | IQR | MAE中位数(log10) | pair数 |
|---:|---|---:|---:|---:|---:|
| 2 | source_only | 2.94 | 1.63-3.78 | 0.648 | 12 |
| 2 | target_offset_calibrated | 1.56 | 1.52-1.88 | 0.517 | 12 |
| 5 | source_only | 4.30 | 2.10-6.53 | 1.026 | 12 |
| 5 | target_offset_calibrated | 1.84 | 1.70-3.05 | 0.502 | 12 |
