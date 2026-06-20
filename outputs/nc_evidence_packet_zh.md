# NC 证据包：跨数据集强震动早窗信息与残差审计

日期：2026-06-18

## 一句话结论

这个项目还有希望冲 Nature Communications。当前最强证据集中在早窗强震动信息与残差审计：

**早窗波形在随机划分、held-event、balanced held-station、OpenQuake 参考对照、AQ2009GM full-manifest chunk-streaming 和 ESM 欧洲强震动数据中都显示出稳定信息增益；跨区域 transfer 显示这种信息有清晰区域边界。**

## 已完成的硬证据

审稿风险矩阵已生成：`outputs/nc_reviewer_risk_matrix.md`。它把 10 秒窗口、split leakage、station 分布、GMM 对照、单位、phase alignment、不确定性、残差解释和 60% 概率边界逐项对应到已有证据。

### 0. Figure 1 数据集-任务矩阵

已生成主图：`outputs/figures/figure1_dataset_task_matrix.png`。这张图概括 unified manifest 的 2,460,425 条记录、各数据集任务覆盖、K-NET 22,119 条完整 ZNE 转换记录，以及 PNWAccelerometers 只作为 supplement 的边界。

### 1. 10 秒早窗随机划分

metadata + 早窗波形明显优于 metadata-only。

主图已生成：`outputs/figures/figure2_early_window_performance.png`。它展示 1/3/10 秒窗口下的 MAE 降幅、q95 残差降幅、combined MAE 和 combined R2。

早窗峰值捕获审计已生成：`outputs/early_window_peak_capture_audit.md`。K-NET 10 秒窗口中 94.7% 测试记录的早窗水平峰值达到 PGA target 的 0.8 倍以上；K-NET 1 秒窗口对应比例为 69.8%。K-NET 10 秒结果应写成 early strong-motion information。1 秒和 3 秒窗口承担 lead-time-sensitive 解释。InstanceGM 早窗幅值和 PGA target 在本地表中不能直接做单位比例解释。

K-NET pre-peak 子集审计已生成：`outputs/knet_prepeak_subset_audit.md`。在早窗水平峰值低于 full-record PGA 80% 的记录中，metadata + 早窗波形仍降低误差：1 秒子集 302 条，MAE 从 0.238 降到 0.205，降幅 13.8%；3 秒子集 255 条，MAE 从 0.239 降到 0.197，降幅 17.9%。10 秒 pre-peak 子集只有 53 条，适合作为审计结果。

| 数据集 | 目标 | metadata MAE | combined MAE | 降幅 | combined R2 |
|---|---|---:|---:|---:|---:|
| InstanceGM | PGA | 0.299 | 0.207 | 30.6% | 0.847 |
| InstanceGM | PGV | 0.298 | 0.165 | 44.7% | 0.863 |
| InstanceGM | SA03 | 0.273 | 0.221 | 19.0% | 0.834 |
| InstanceGM | SA10 | 0.286 | 0.210 | 26.8% | 0.827 |
| InstanceGM | SA30 | 0.306 | 0.242 | 20.9% | 0.680 |
| K-NET | PGA | 0.217 | 0.105 | 51.8% | 0.877 |

### 2. Held-event

事件完全留出后，结论仍成立。

| 数据集 | 目标 | metadata MAE | combined MAE | 降幅 | combined R2 |
|---|---|---:|---:|---:|---:|
| InstanceGM | PGA | 0.312 | 0.191 | 38.8% | 0.875 |
| InstanceGM | PGV | 0.313 | 0.155 | 50.4% | 0.895 |
| InstanceGM | SA03 | 0.287 | 0.223 | 22.5% | 0.842 |
| InstanceGM | SA10 | 0.282 | 0.212 | 24.7% | 0.855 |
| InstanceGM | SA30 | 0.298 | 0.224 | 24.9% | 0.723 |
| K-NET | PGA | 0.238 | 0.108 | 54.5% | 0.869 |

### 3. Balanced held-station

台站完全留出，测试集覆盖 50 个 InstanceGM 台站和 50 个 K-NET 台站，group overlap 为 0。

主图已生成：`outputs/figures/figure3_heldout_generalization.png`。这张图把 held-event、balanced held-station 和 station-split 分布审计放在同一张图里，对应 CSV 为 `outputs/figure3_heldout_generalization.csv`。

| 数据集 | 目标 | metadata MAE | combined MAE | 降幅 | combined R2 |
|---|---|---:|---:|---:|---:|
| InstanceGM | PGA | 0.392 | 0.253 | 35.5% | 0.799 |
| InstanceGM | PGV | 0.372 | 0.176 | 52.6% | 0.858 |
| InstanceGM | SA03 | 0.327 | 0.242 | 26.0% | 0.814 |
| InstanceGM | SA10 | 0.331 | 0.262 | 20.9% | 0.785 |
| InstanceGM | SA30 | 0.343 | 0.248 | 27.8% | 0.683 |
| K-NET | PGA | 0.222 | 0.111 | 49.9% | 0.875 |

### 3a. Held-station 1/2/3/5/10 秒信息增益曲线

已补齐 2 秒和 5 秒 balanced held-station 运行，并生成窗口扫描：`outputs/held_station_window_scan_summary.md`。

图：`outputs/figures/ground_motion_audit/held_station_window_scan.png`

| 数据集 | 目标 | 1s | 2s | 3s | 5s | 10s |
|---|---|---:|---:|---:|---:|---:|
| InstanceGM | PGA | 23.9% | 25.7% | 28.8% | 31.2% | 35.5% |
| InstanceGM | PGV | 40.1% | 40.7% | 41.6% | 45.4% | 52.6% |
| InstanceGM | SA03 | 15.2% | 15.9% | 19.6% | 21.1% | 26.0% |
| InstanceGM | SA10 | 16.5% | 16.8% | 16.7% | 18.8% | 20.9% |
| InstanceGM | SA30 | 24.2% | 25.9% | 26.3% | 26.3% | 27.8% |
| K-NET | PGA | 11.3% | 13.7% | 17.6% | 23.3% | 49.9% |

解释：这张图是当前最直接的 1-5 秒信息增益证据。K-NET 在 5 到 10 秒之间增益跳升，说明 10 秒窗口在日本强震动数据中更接近 early strong-motion information；1、2、3、5 秒更适合承载预警提前量叙事。

### 3b. Balanced held-station 分布审计

这层审计检查 held-station 测试集是否是“容易分布”。结果显示 InstanceGM 测试集距离更远、PGA 更低，K-NET train/test 在距离和 PGA 上覆盖较好。

| 数据集 | 变量 | train median | test median | KS | overlap |
|---|---|---:|---:|---:|---:|
| InstanceGM | magnitude | 2.20 | 2.40 | 0.14 | 0.86 |
| InstanceGM | distance km | 44.27 | 70.61 | 0.25 | 0.76 |
| InstanceGM | log10 PGA | -1.68 | -2.11 | 0.23 | 0.78 |
| K-NET | magnitude | 4.30 | 4.30 | 0.05 | 0.92 |
| K-NET | distance km | 54.43 | 57.73 | 0.05 | 0.93 |
| K-NET | log10 PGA | 0.95 | 0.89 | 0.06 | 0.92 |

写法：balanced held-station 仍保留 source-path-target shift；早窗信息在这种 shift 下仍有增益。避免写成 distribution-matched station transfer。

主图：`outputs/figures/figure3_heldout_generalization.png`
支撑图：`outputs/figures/ground_motion_audit/balanced_station_distribution_audit_panel.png`

### 4. OpenQuake Boore2014 参考

已补充一个低参数 attenuation-shaped ridge 参考：`outputs/attenuation_reference_summary.md`。它只用震级、log10 hypocentral-distance 形状、深度和可用 Vs30，在 balanced held-station 上拟合。InstanceGM 这个 split 有 Vs30；K-NET 没有 Vs30，所以 K-NET attenuation 参考不是 site-corrected。metadata + 早窗波形在所有 6 个目标上都优于这个参考，相对降幅为 17.5-51.6%。这个结果只作为 baseline check，不替代完整区域 GMM。

区域 GMM readiness 审计已生成：`outputs/regional_gmm_readiness_audit.md`。InstanceGM held-station 记录可以全部 join 回原始 metadata，且这个 split 的 Vs30 完整，但 focal-mechanism 覆盖很低：train 141/5,000，test 36/1,000。K-NET 当前批准使用的本地包有 source distance，但没有 Vs30、rupture distance 或 focal-mechanism 字段。因此现在只能写 GMM screening，不能写完整区域 GMM 对照。

OpenQuake 已装好。BooreEtAl2014 使用训练集 median bias correction。当前近似包括：`source_distance_km` 作为 Rjb 代理、`rake=0`、缺失 Vs30 用 760 m/s。

主图已生成：`outputs/figures/figure4_classical_uncertainty.png`。这张图把 OpenQuake 对照和 split-conformal 校准放在同一张图里，对应 CSV 为 `outputs/figure4_classical_uncertainty.csv`。

| 数据集 | 目标 | Boore2014 MAE | metadata HGB MAE | combined MAE | combined 相对 Boore 降幅 |
|---|---|---:|---:|---:|---:|
| InstanceGM | PGA | 0.399 | 0.392 | 0.253 | 36.6% |
| InstanceGM | PGV | 0.434 | 0.372 | 0.176 | 59.4% |
| InstanceGM | SA03 | 0.374 | 0.327 | 0.242 | 35.4% |
| InstanceGM | SA10 | 0.411 | 0.331 | 0.262 | 36.4% |
| InstanceGM | SA30 | 0.477 | 0.343 | 0.248 | 48.0% |
| K-NET | PGA | 0.282 | 0.222 | 0.111 | 60.6% |

这个结果足够当第一版 classical reference。不要写成“已全面优于区域调优 GMPE”。

### 4b. K-NET 日本 GMM screening

已补充 OpenQuake 日本或日本派生 GMM screening：Kanno2006、Zhao2006、SiMidorikawa1999 变体。输入使用 `source_distance_km` 作为 Rrup 代理，Vs30 用默认值，预测用训练集 median bias correction。

| 参考 | K-NET PGA MAE | R2 |
|---|---:|---:|
| best Japanese GMM screening, Kanno2006Shallow | 0.242 | 0.490 |
| metadata + early waveform | 0.111 | 0.875 |

写法：这是比单个 Boore2014 更强的 K-NET classical screening；仍受 Vs30、rupture distance 和震源类型近似限制，不能写成完整区域 GMM 证明。

### 5. 不确定性校准

Split conformal nominal coverage 为 90%。

| 数据集 | 目标 | 覆盖率 | 区间宽度 | 解释 |
|---|---|---:|---:|---|
| InstanceGM | PGA | 0.845 | 0.913 | under-cover |
| InstanceGM | PGV | 0.898 | 0.774 | 接近标称 |
| InstanceGM | SA03 | 0.859 | 0.930 | under-cover |
| InstanceGM | SA10 | 0.820 | 0.877 | under-cover |
| InstanceGM | SA30 | 0.876 | 0.946 | 略低 |
| K-NET | PGA | 0.925 | 0.545 | 良好 |

写法：早窗波形提升点预测，但 station shift 下不确定性校准仍有目标依赖性。

### 5b. 残差和波形审计

主图已生成：`outputs/figures/figure5_residual_waveform_audit.png`。这张图现在只保留 10 秒残差诊断，适合主文页面阅读。InstanceGM 重复高残差记录和 K-NET PGA 高残差波形案例已拆到扩展审计图：`outputs/figures/extended_waveform_case_audit.png`。

写法：残差图说明哪些记录和距离/幅值区间需要审计；不要把单变量残差结构写成物理因果。

### 6. Phase audit

已有 1,000 条/数据集的 phase audit，不需要立刻重跑。

主图已生成：`outputs/figures/figure6_phase_label_audit.png`。这张图按 P/S 相分别展示 MAE、q95 tail error 和 missing-pick rate，对应 CSV 为 `outputs/figure6_phase_label_audit.csv`。

| 数据集 | 主要结果 |
|---|---|
| STEAD | PhaseNet(STEAD) 很稳，P MAE 0.035 s，S MAE 0.082 s |
| K-NET | P picks 稳定，PhaseNet P MAE 0.056 s；S tail 更宽，q95 约 1.05 s |
| InstanceGM | missing-pick 问题最明显，S missing 约 45-48% |
| Iquique | P missing 低，S missing 约 16%，S MAE 0.42-0.67 s |

这支持 label-domain audit：P 相稳定性说明转换和对齐可信，S 相和 InstanceGM missing rate 暴露数据集/标签迁移问题。

### 7. AQ2009GM full-manifest chunk-streaming 独立 SeisBench 地震动补验

AQ2009GM 已按本地 SeisBench chunk manifest 完成流式验证：254 个 chunk；有效 PGA/PGV 记录 345,226；事件数 60,310；台站数 66。流程为逐 chunk 下载、提取 early-window velocity features、PGA/PGV target、metadata 和 event/station id，保存小特征表后用 `--delete-raw` 删除原始 HDF5/metadata 文件。目标使用 AQ2009GM metadata 的 `trace_pga_cmps2` 和 `trace_pgv_cmps`。

图：`outputs/figures/ground_motion_audit/aq2009gm_full_stream_panel.png`
报告：`outputs/aq2009gm_full_stream_validation_summary.md`
2/5 秒图：`outputs/figures/ground_motion_audit/aq2009gm_full_stream_2s5s_panel.png`
2/5 秒报告：`outputs/aq2009gm_full_stream_validation_2s5s_summary.md`

| holdout | target | window | metadata MAE | combined MAE | 降幅 | combined R2 |
|---|---|---:|---:|---:|---:|---:|
| event | PGA | 1s | 0.205 | 0.145 | 29.3% | 0.922 |
| event | PGA | 3s | 0.205 | 0.109 | 46.8% | 0.952 |
| event | PGA | 10s | 0.205 | 0.077 | 62.5% | 0.977 |
| event | PGV | 1s | 0.192 | 0.132 | 31.1% | 0.934 |
| event | PGV | 3s | 0.192 | 0.087 | 54.8% | 0.966 |
| event | PGV | 10s | 0.192 | 0.025 | 86.7% | 0.994 |
| station | PGA | 1s | 0.311 | 0.222 | 28.8% | 0.810 |
| station | PGA | 3s | 0.311 | 0.175 | 43.9% | 0.871 |
| station | PGA | 10s | 0.311 | 0.113 | 63.6% | 0.949 |
| station | PGV | 1s | 0.286 | 0.183 | 36.0% | 0.861 |
| station | PGV | 3s | 0.286 | 0.142 | 50.4% | 0.907 |
| station | PGV | 10s | 0.286 | 0.025 | 91.4% | 0.994 |
| time | PGA | 1s | 0.271 | 0.176 | 35.1% | 0.862 |
| time | PGA | 3s | 0.271 | 0.134 | 50.4% | 0.911 |
| time | PGA | 10s | 0.271 | 0.092 | 66.1% | 0.960 |
| time | PGV | 1s | 0.249 | 0.151 | 39.4% | 0.898 |
| time | PGV | 3s | 0.249 | 0.095 | 62.0% | 0.951 |
| time | PGV | 10s | 0.249 | 0.024 | 90.3% | 0.995 |

新增 2/5 秒全量补验：

| holdout | target | window | metadata MAE | combined MAE | 降幅 | combined R2 |
|---|---|---:|---:|---:|---:|---:|
| event | PGA | 2s | 0.205 | 0.128 | 37.6% | 0.937 |
| event | PGA | 5s | 0.205 | 0.087 | 57.8% | 0.969 |
| event | PGV | 2s | 0.192 | 0.114 | 40.5% | 0.949 |
| event | PGV | 5s | 0.192 | 0.048 | 74.9% | 0.985 |
| station | PGA | 2s | 0.311 | 0.206 | 33.9% | 0.832 |
| station | PGA | 5s | 0.311 | 0.138 | 55.8% | 0.921 |
| station | PGV | 2s | 0.286 | 0.166 | 42.1% | 0.883 |
| station | PGV | 5s | 0.286 | 0.081 | 71.9% | 0.958 |
| time | PGA | 2s | 0.271 | 0.162 | 40.1% | 0.878 |
| time | PGA | 5s | 0.271 | 0.103 | 61.9% | 0.946 |
| time | PGV | 2s | 0.249 | 0.135 | 46.0% | 0.918 |
| time | PGV | 5s | 0.249 | 0.048 | 80.6% | 0.984 |

解释：AQ2009GM 结果明显增强了独立 SeisBench 地震动补验层。它有官方 PGA/PGV metadata target，并用流式处理覆盖本地 manifest 中全部 254 个 chunk。边界是：本地没有保留完整 raw AQ2009GM，当前证据是从逐 chunk 下载后提取并保存的小特征表、split、metrics、subgroup 和 uncertainty 文件得到的。

### 7b. 跨区域 early-waveform 迁移边界

已新增跨区域迁移实验：`outputs/cross_region_waveform_transfer_summary.md`。它只使用早窗 waveform 特征，不使用 source distance、site terms、event id 或 station id。训练源域和测试目标域分开；offset 校准只使用目标域 train split，不使用目标域 test 标签。

图：`outputs/figures/ground_motion_audit/cross_region_waveform_transfer_boundary.png`
窗口扫描图：`outputs/figures/ground_motion_audit/cross_region_waveform_transfer_window_scan.png`

| 目标 | 测试域 | 设置 | 最好源域 | MAE | R2 | 相对目标域内训练 MAE |
|---|---|---|---|---:|---:|---:|
| PGA | AQ2009GM | zero-shot | InstanceGM | 0.167 | 0.853 | 1.71x |
| PGA | AQ2009GM | offset 校准 | InstanceGM | 0.164 | 0.860 | 1.68x |
| PGA | InstanceGM | zero-shot | AQ2009GM | 0.479 | 0.094 | 1.35x |
| PGA | InstanceGM | offset 校准 | AQ2009GM | 0.463 | 0.180 | 1.32x |
| PGA | K-NET | zero-shot | AQ2009GM | 0.356 | -0.195 | 2.60x |
| PGA | K-NET | offset 校准 | InstanceGM | 0.346 | -0.002 | 2.53x |
| PGV | AQ2009GM | zero-shot | InstanceGM | 0.109 | 0.920 | 4.98x |
| PGV | AQ2009GM | offset 校准 | InstanceGM | 0.102 | 0.920 | 4.66x |
| PGV | InstanceGM | zero-shot | AQ2009GM | 0.315 | 0.549 | 1.32x |
| PGV | InstanceGM | offset 校准 | AQ2009GM | 0.315 | 0.549 | 1.32x |

窗口扫描结果：

| window | zero-shot 中位惩罚 | offset 校准中位惩罚 |
|---:|---:|---:|
| 1s | 1.49x | 1.40x |
| 3s | 1.74x | 1.65x |
| 10s | 2.84x | 2.26x |

解释：跨区域迁移给出当前主结果的边界。zero-shot 跨域迁移在 10 秒窗口的中位数 MAE 为目标域内训练的 2.84 倍；用目标域 train split 做 offset 校准后降到 2.26 倍，仍高于目标域内训练。1、3、10 秒扫描显示迁移惩罚随窗口变长而增加，说明早窗后段振幅结构带有更强区域和测量体系依赖。这个结果适合写成公开强震动数据约束下的可预测性边界和单位/测量体系 harmonization 需求。

### 7c. ESM 欧洲强震动本地数据验证

已从本地 ESM ASCII zip 包生成 compact feature table：`outputs/esm_compact_features_full_summary.md`。数据来自 `/Users/yojironoda/Documents/New project 2/outputs/strong_motion_downloads/欧洲_ESM`，原始 zip 未解压改写。全量转换覆盖 951 个 zip，得到 134,250 行 1/2/3/5/10 秒 early-window features，对应 861 个事件、1,568 个台站、26,850 个事件-台站样本。读取错误为 0。PGA 非缺失 134,250 行；PGV 非缺失 134,245 行，有 1 个事件-台站样本跨 5 个窗口缺失 PGV。剔除了 6,515 个理论 P 到时不在记录内的窗口。

重要边界：ESM 本地 ASCII 头里没有显式 P 到时。本轮用发震时刻、首采样时刻、震中距、深度和 6 km/s P 波速度估计 P onset。论文里只能写 `theoretical P-onset estimate`，不能写成 catalog/manual P pick。

ESM P-onset sensitivity 审计已补：`outputs/esm_p_onset_sensitivity_audit.md`。审计没有重新提取波形特征，而是在已保留的 ESM compact feature table 上检查理论到时对 Vp 选择的敏感性。Vp 从 6.0 km/s 改到 5.5 km/s 时，理论 P onset 中位延后 2.517 秒；改到 6.5 km/s 时，中位提前 2.130 秒。所有 1/2/3/5/10 秒窗口在 5.5、6.0、6.5 km/s 下的 retained-window valid fraction 都大于 0.994。

ESM waveform-level onset-proxy spot audit 已补：`outputs/esm_waveform_p_pick_spotcheck.md`。它从 ESM feature table 中按距离和 PGA 分层抽取 200 个事件-台站样本，回读本地 ACC.AP 波形，用三分量加速度 envelope 阈值检测 onset proxy。200 个样本中 105 个检测到 onset proxy，其中 86 个为 high-confidence。high-confidence 子集中，proxy onset 相对 theoretical 6 km/s onset 的 median absolute offset 为 1.223 秒，q90 为 3.338 秒，q95 为 3.960 秒，98.8% 在 5 秒内。

解释：ESM retained-row 定义对合理 Vp 扰动稳定，自动波形 onset proxy 也没有显示理论到时存在灾难性系统偏差。论文里可以把 ESM 写成欧洲强震动外部域和 transfer-domain check，并说明有 waveform-onset sanity check；仍不能把它写成 catalog/manual P pick 下的 lead-time 严格证明。

ESM held-out baseline：`outputs/esm_heldout_baseline_summary.md`。

| 目标 | Window | held-station median MAE | P only MAE | P+distance MAE | P+distance+site MAE |
|---|---:|---:|---:|---:|---:|
| PGA | 1s | 0.717 | 0.522 | 0.378 | 0.371 |
| PGA | 2s | 0.455 | 0.300 | 0.279 | 0.275 |
| PGA | 3s | 0.553 | 0.263 | 0.251 | 0.251 |
| PGA | 5s | 0.457 | 0.226 | 0.224 | 0.214 |
| PGA | 10s | 0.616 | 0.207 | 0.221 | 0.197 |
| PGV | 1s | 0.676 | 0.516 | 0.371 | 0.382 |
| PGV | 2s | 0.471 | 0.368 | 0.330 | 0.323 |
| PGV | 3s | 0.556 | 0.338 | 0.308 | 0.308 |
| PGV | 5s | 0.483 | 0.311 | 0.290 | 0.282 |
| PGV | 10s | 0.600 | 0.253 | 0.227 | 0.214 |

解释：ESM 把证据从 SeisBench/AQ 和日本 K-NET 推到欧洲强震动域。held-station 下 P-only 已经明显优于 median；距离和场地项在多数窗口继续降低误差。这个结果直接支撑“公开强震动数据约束下的早期 P 波信息增益曲线”和“场地信息对不确定性的贡献”。

### 7d. ESM 跨区域 transfer

已将 ESM 和 AQ2009GM 2/5 秒全量特征加入 early-waveform-only transfer。1/2/3/5/10 秒均覆盖 InstanceGM、K-NET、AQ2009GM 和 ESM。

| Window | Target | ESM 域内 MAE | 最好外部源域到 ESM offset 校准 MAE | 退化倍数 |
|---:|---|---:|---:|---:|
| 1s | PGA | 0.420 | 0.540 | 1.26x |
| 1s | PGV | 0.462 | 0.551 | 1.18x |
| 2s | PGA | 0.321 | 0.490 | 1.53x |
| 2s | PGV | 0.380 | 0.495 | 1.30x |
| 3s | PGA | 0.250 | 0.448 | 1.77x |
| 3s | PGV | 0.333 | 0.453 | 1.35x |
| 5s | PGA | 0.208 | 0.407 | 1.95x |
| 5s | PGV | 0.299 | 0.411 | 1.38x |
| 10s | PGA | 0.184 | 0.461 | 2.53x |
| 10s | PGV | 0.275 | 0.433 | 1.58x |

整体 transfer 中位惩罚：

| Window | zero-shot 中位惩罚 | offset 校准中位惩罚 |
|---:|---:|---:|
| 1s | 2.25x | 1.40x |
| 2s | 2.65x | 1.55x |
| 3s | 2.98x | 1.67x |
| 5s | 3.38x | 1.85x |
| 10s | 4.27x | 2.46x |

解释：ESM 结果把“跨区域可预测性边界”扩展成欧洲外部测试域。随着窗口从 1 秒到 10 秒变长，zero-shot 和 offset 校准后的中位迁移惩罚都升高。10 秒窗口下，ESM 域内训练已经很强，但外部域训练迁移到 ESM 仍显著退化。这个现象比单纯追求更复杂模型更适合写 NC 主线。

### 7e. 不确定性、强震动尾部和 seed 稳健性补验

已补三项边界敏感性实验：`outputs/nc_boundary_sensitivity_summary.md`。特征只用 early log-waveform，不用 distance、site terms、event id 或 station id。

不确定性边界：

| Window | Mode | median coverage90 | median interval width |
|---:|---|---:|---:|
| 2s | target-domain conformal | 0.895 | 1.230 |
| 2s | source-domain conformal | 0.468 | 1.228 |
| 2s | target-offset conformal | 0.905 | 2.177 |
| 5s | target-domain conformal | 0.895 | 0.828 |
| 5s | source-domain conformal | 0.298 | 0.826 |
| 5s | target-offset conformal | 0.903 | 2.177 |

解释：源域校准区间直接迁移到目标域会明显 under-cover；使用目标域 train split 做 offset 和 conformal calibration 后 coverage 回到约 0.90，但 interval width 变大。这正是“不确定性边界”，不是模型失败。

强震动尾部漏报边界：

| Window | Mode | Tail | factor-2 underprediction rate | q95 underprediction |
|---:|---|---:|---:|---:|
| 2s | target-domain | top 5% | 0.520 | 1.479 |
| 2s | source-domain conformal | top 5% | 0.563 | 1.133 |
| 5s | target-domain | top 5% | 0.320 | 0.715 |
| 5s | source-domain conformal | top 5% | 0.442 | 1.017 |

解释：即使域内训练，强震动尾部仍存在漏报边界；5 秒比 2 秒缓解明显，但没有消除。跨域条件下尾部漏报仍然突出。

三 seed 稳健性：

| Window | Target | Mode | median transfer ratio range |
|---:|---|---|---:|
| 2s | PGA | offset conformal | 1.54-1.58 |
| 2s | PGV | offset conformal | 1.40-1.42 |
| 5s | PGA | offset conformal | 1.81-1.85 |
| 5s | PGV | offset conformal | 1.87-1.98 |

解释：跨域惩罚和 offset 后残余边界在三个 seed 下稳定，足以排除一次 split 偶然性。

### 7f. 主边界合成图

已生成一张压缩主图：`outputs/figures/nc_core_predictability_boundary.png`。对应表为 `outputs/nc_core_predictability_boundary_table.csv`，摘要为 `outputs/nc_core_predictability_boundary_summary.md`。

| Window | 主 held-station 增益 | AQ station 增益 | ESM station 增益 | zero-shot transfer | offset transfer | source conformal coverage | top5 漏报率 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1s | 20.2% | 32.4% | 45.9% | 2.25x | 1.40x | NA | NA |
| 2s | 21.2% | 38.0% | 35.5% | 2.65x | 1.55x | 0.468 | 0.520 |
| 3s | 22.9% | 47.2% | 49.6% | 2.98x | 1.67x | NA | NA |
| 5s | 24.8% | 63.8% | 47.4% | 3.38x | 1.85x | 0.298 | 0.320 |
| 10s | 31.6% | 77.5% | 66.2% | 4.27x | 2.46x | NA | NA |

解释：这张图把论文主线压成四个面板：早窗信息增益、跨区域迁移退化、不确定性迁移失配、强震动尾部漏报。它不是新实验，而是从已验证输出自动汇总，适合作为“边界测量”主图。

### 7g. Methods、理论边界、GMM 边界和图风格补丁

已补正式 Methods 草稿：`outputs/nc_methods_formal_draft.md`。它覆盖 Data Sources、Early-Window Features、Targets、Splits、Models、Classical References、Uncertainty and Boundary Analysis、Residual and Figure Audits。这里把 ESM 明确写成 theoretical P-onset supplement，把 AQ2009GM 写成 retained feature-table validation，把 K-NET 单位和 component mapping 写进 provenance。

已补不确定性理论说明：`outputs/nc_uncertainty_boundary_note.md`。核心是 split conformal 的 exchangeability 条件：calibration residuals 和 test residuals 需要来自同一残差分布。source-domain conformal transfer 会故意打破这个条件；观测到的 2 秒 coverage 0.468、5 秒 coverage 0.298 就是 uncertainty-transfer boundary。target-offset conformal 使用目标域 train split 后 coverage 回到约 0.90，但 interval width 增大。

已补区域 GMM 边界说明：`outputs/regional_gmm_boundary_note.md`。当前能支撑 classical-reference screening：attenuation-shaped ridge、BooreEtAl2014、K-NET Japanese GMM screening 和 readiness audit。当前不能支撑完整区域 GMPE/GMM 优越性声明，因为 K-NET 缺 Vs30、rupture distance 和 focal mechanism，InstanceGM focal-mechanism 覆盖很低。

已补主图重画和风格审计：`work/scripts/redraw_nc_main_figures.py` 重画 Figure 1-6，`outputs/nc_figure_style_audit.md` 记录 Figure 1-7 尺寸，contact sheet 为 `outputs/figures/nc_main_figure_contact_sheet.png`。Figure 5 已拆成主文残差诊断图和扩展波形案例图，其余主图已统一为紧凑多面板风格。

下一步实验判断已写入：`outputs/nc_next_experiment_decision.md`。小规模 ESM waveform-level onset-proxy spot audit 已完成，用来降低纯理论 P onset 的最弱环节。完整区域 GMPE/GMM 暂缓，直到 rupture distance、site terms 和 tectonic 或 focal-mechanism metadata 可用。

### 8. PNWAccelerometers 补充检查

这是补充 SeisBench 加速度数据检查，不作为正式 PGA 主证据。PNWAccelerometers 本地 HDF5 只记录了 `component_order=ENZ`，没有记录 waveform unit；因此目标写成全记录水平峰值波形振幅，而不是出版级 PGA。

单位 provenance 审计已生成：`outputs/pnw_unit_provenance_audit.md`。公开 PNW-ML README 说明 EN 是 accelerometer 通道，Seismica 论文摘要说明数据包含 strong-motion EN channels，但本地 SeisBench 缓存和 metadata 没有物理单位字段。

| holdout | window | metadata MAE | combined MAE | 降幅 | combined R2 |
|---|---:|---:|---:|---:|---:|
| event | 1s | 0.239 | 0.201 | 16.2% | 0.844 |
| event | 3s | 0.239 | 0.163 | 32.0% | 0.888 |
| event | 10s | 0.239 | 0.036 | 85.0% | 0.978 |
| station | 1s | 0.361 | 0.240 | 33.4% | 0.750 |
| station | 3s | 0.361 | 0.196 | 45.7% | 0.820 |
| station | 10s | 0.361 | 0.034 | 90.5% | 0.980 |

解释：1 秒和 3 秒结果支持早窗振幅信息不是 InstanceGM/K-NET 特有现象。10 秒结果很强，但更可能说明 PNW 小震/近震的峰值经常落在 P 后 10 秒内，因此不能单独作为 lead-time 证据。

## 当前可以写的主 claim

1. 早窗波形在 1 秒、3 秒、10 秒后均包含强震动信息。
2. 10 秒早窗在 InstanceGM 和 K-NET 上稳定提升 PGA/PGV/SA 预测。
3. held-event 和 balanced held-station 排除了普通随机划分泄漏解释。
4. OpenQuake Boore2014 近似参考下，早窗融合模型仍明显更好。
5. 残差和不确定性结果显示：station shift 下仍有目标依赖的风险。
6. AQ2009GM full-manifest chunk-streaming 可作为有官方 PGA/PGV metadata target 的 supplementary independent SeisBench check。
7. ESM 欧洲强震动数据提供独立外部区域验证，但 P onset 是理论估计。
8. 跨区域 early-waveform transfer 提供 predictability boundary 证据，主文按边界结果表述。
9. PNWAccelerometers 可作为补充 robustness 结果，但不能写成官方 PGA 验证。
10. ESM P-onset sensitivity 和 waveform-level onset-proxy spot audit 已量化：retained-row 稳定，high-confidence onset proxy q95 offset 为 3.960 秒，但 ESM 仍不是 catalog/manual P pick 数据。

## 不能写的 claim

1. 不能写地震预测。
2. 不能写 operational EEW ready。
3. 不能写 foundation model 已成功。
4. 不能写物理因果已经证明。
5. 不能写全面优于区域调优 GMPE/GMM。
6. 不能写成“完整 raw AQ2009GM 已下载并保留”；应写成“对本地 SeisBench AQ2009GM manifest 的 full-manifest chunk-streaming 验证”。
7. 不能把 PNWAccelerometers 的峰值振幅目标写成已验证物理单位 PGA。
8. 不能把 ESM theoretical P onset 或 automated onset proxy 写成 catalog/manual P pick。

## 还缺什么

### 必补

1. 对重画后的 Figure 1-6 做人工版式细修，重点检查 Figure 5 主文残差诊断图和扩展波形案例图在期刊页面里的可读性。
2. PNWAccelerometers 若进入正文，需要补充单位来源；否则只放补充材料。

### 可选

1. 给 ESM 做人工 P 到时抽查，以替代 automated onset proxy。
2. 做 magnitude-distance-balanced station split。
3. 在有 rupture class、rupture distance 和 site terms 后做完整区域 GMPE/GMM 对照。

## 当前 NC 概率判断

当前已验证主图证据包、AQ2009GM full-manifest chunk-streaming、ESM 欧洲强震动外部验证、ESM P-onset sensitivity 和 ESM waveform-onset spot audit：**68-72%**。

如果再做投稿级图文细修和人工 ESM P 到时抽查：**70-74%**。

已完成：主图 1-6 重画、NC 主边界合成图、held-out 证据、OpenQuake/conformal、残差/波形审计、phase audit、AQ2009GM full-manifest、ESM compact features、ESM held-out baseline、ESM P-onset sensitivity、四域 transfer、cross-region conformal/tail/seed sensitivity、uncertainty boundary note、regional GMM boundary note、formal Methods draft 压缩版、figure style audit、evidence verifier。

如果加入完整区域 GMM 对照或更强物理残差解释：**73-78%**。

现在可以诚实说接近 70%。原因是 ESM 提供了欧洲强震动外部测试域，四域 transfer 给出清晰退化边界，ESM P-onset sensitivity 和 waveform-onset spot audit 已经把主要相位风险量化。限制仍然明确：ESM 还不是人工 P pick，当前还没有完整区域 GMM 对照。

## 下一步

最短路径：

**补软件版本和数据访问细节，然后检查重画图在投稿页面里的可读性。**

理由：强震动部分已有 held-out、OpenQuake、uncertainty、AQ2009GM、ESM 外部验证和 ESM P-onset sensitivity。现在最大瓶颈是 Methods 的投稿级压缩、图件统一和正文叙事是否能把“信息增益”和“跨区域边界”直接讲清楚。
