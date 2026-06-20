# PNW Accelerometer Peak-Amplitude Baseline

日期：2026-06-18

## 定位

这是补充 SeisBench 加速度数据检查，不作为正式 PGA 主证据。PNWAccelerometers 本地 HDF5 只记录了 `component_order=ENZ`，没有记录 waveform unit；因此目标写成全记录水平峰值波形振幅，而不是出版级 PGA。

## 数据和拆分

- 可用 earthquake 加速度记录：5,981 条
- held-event：训练 4,000，测试 1,000，测试事件 552，overlap=0
- held-station：训练 4,000，测试 1,000，测试台站 40，overlap=0

## 结果

| holdout | window | metadata MAE | combined MAE | 降幅 | combined R2 |
|---|---:|---:|---:|---:|---:|
| event | 1s | 0.239 | 0.201 | 16.2% | 0.844 |
| event | 3s | 0.239 | 0.163 | 32.0% | 0.888 |
| event | 10s | 0.239 | 0.036 | 85.0% | 0.978 |
| station | 1s | 0.361 | 0.240 | 33.4% | 0.750 |
| station | 3s | 0.361 | 0.196 | 45.7% | 0.820 |
| station | 10s | 0.361 | 0.034 | 90.5% | 0.980 |

## 解释

1 秒和 3 秒结果支持早窗振幅信息在另一个 SeisBench 加速度数据集上也成立。10 秒结果非常强，但更可能说明小震/近震的峰值经常落在 P 后 10 秒内，因此不能单独作为 lead-time 证据。

这组结果可以放在补充材料或 robustness 小节，用来说明早窗信息不是 InstanceGM/K-NET 特有现象。它不能替代有明确物理单位和官方目标定义的强震动数据。

图：`outputs/figures/ground_motion_audit/pnw_accelerometer_peak_panel.png`
