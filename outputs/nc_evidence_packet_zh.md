# NC 证据包：跨数据集强震动早窗信息与残差审计

日期：2026-06-18

## 一句话结论

这个项目还有希望冲 Nature Communications。当前最强证据集中在早窗强震动信息与残差审计：

**早窗波形在随机划分、held-event、balanced held-station 和 OpenQuake 参考对照下，都能稳定提高强震动目标预测；AQ2009GM 096-100 补验显示同一早窗信息也出现在另一个有官方 PGA/PGV 目标的 SeisBench 地震动数据中。**

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

主图已生成：`outputs/figures/figure5_residual_waveform_audit.png`。这张图合并 10 秒残差诊断、InstanceGM 重复高残差记录和 K-NET PGA 高残差记录。

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

### 7. AQ2009GM 096-100 独立 SeisBench 地震动补验

AQ2009GM chunks 096-100 已作为五 chunk 补验完成：metadata 总行数 101,218；有效 PGA/PGV 记录 30,737；事件数 5,497；台站数 50。HDF5 明确记录 `measurement=velocity`、`unit=m/s`、`component_order=ZNE`。目标使用 AQ2009GM metadata 的 `trace_pga_cmps2` 和 `trace_pgv_cmps`。

图：`outputs/figures/ground_motion_audit/aq2009gm_chunks096-100_station12_panel.png`
报告：`outputs/aq2009gm_chunks096-100_station12_baseline_summary.md`

| holdout | target | window | metadata MAE | combined MAE | 降幅 | combined R2 |
|---|---|---:|---:|---:|---:|---:|
| event | PGA | 1s | 0.215 | 0.153 | 28.7% | 0.924 |
| event | PGA | 3s | 0.215 | 0.115 | 46.5% | 0.953 |
| event | PGA | 10s | 0.215 | 0.079 | 63.0% | 0.977 |
| event | PGV | 1s | 0.206 | 0.147 | 28.6% | 0.928 |
| event | PGV | 3s | 0.206 | 0.096 | 53.2% | 0.961 |
| event | PGV | 10s | 0.206 | 0.034 | 83.5% | 0.990 |
| station | PGA | 1s | 0.510 | 0.187 | 63.4% | 0.871 |
| station | PGA | 3s | 0.510 | 0.140 | 72.5% | 0.918 |
| station | PGA | 10s | 0.510 | 0.120 | 76.5% | 0.946 |
| station | PGV | 1s | 0.486 | 0.190 | 61.0% | 0.874 |
| station | PGV | 3s | 0.486 | 0.114 | 76.6% | 0.933 |
| station | PGV | 10s | 0.486 | 0.037 | 92.3% | 0.987 |

解释：AQ2009GM 结果明显增强了独立 SeisBench 地震动补验层。它有清楚的 HDF5 速度单位和官方 PGA/PGV metadata target，比 PNWAccelerometers 更适合写成地震动补充证据。边界是 096-100 五 chunk 余震小幅值子集，不应写成完整 AQ2009GM 或完整外部强震动验证。

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
6. AQ2009GM 096-100 可作为有明确单位和官方 PGA/PGV metadata target 的 supplementary independent SeisBench check。
7. PNWAccelerometers 可作为补充 robustness 结果，但不能写成官方 PGA 验证。

## 不能写的 claim

1. 不能写地震预测。
2. 不能写 operational EEW ready。
3. 不能写 foundation model 已成功。
4. 不能写物理因果已经证明。
5. 不能写全面优于区域调优 GMPE/GMM。
6. 不能把 AQ2009GM 096-100 写成完整 AQ2009GM 或完整外部强震动验证。
7. 不能把 PNWAccelerometers 的峰值振幅目标写成已验证物理单位 PGA。

## 还缺什么

### 必补

1. 把 OpenQuake 参考的近似写清楚：Rjb 代理、rake 默认、Vs30 缺失。
2. 写 Methods，确保 split、单位、target 定义可复现。
3. PNWAccelerometers 若进入正文，需要补充单位来源；否则只放补充材料。

### 可选

1. 加其他有明确单位和官方 GM target 的独立强震动数据。
2. 做 magnitude-distance-balanced station split。
3. 在有 rupture class、rupture distance 和 site terms 后做完整区域 GMPE/GMM 对照。

## 当前 NC 概率判断

当前已验证主图证据包加 AQ2009GM 096-100 补验：**48-58%**。

如果补齐正式 Methods、数据 provenance 和正文叙事：**50-59%**。

已完成：主图 1-6、held-out 证据、OpenQuake/conformal、残差/波形审计、phase audit、evidence verifier。

如果把 AQ2009GM 扩展到更大覆盖，或加入完整区域 GMM 对照，或建立更强物理残差解释：**52-59%**。

目前还不能诚实说 60%。AQ2009GM 096-100 把证据推进到“另一个有官方 PGA/PGV 目标的数据也在五 chunk 子集成立”，但余震和小幅值覆盖仍限制它对 NC 录用概率的提升。

## 下一步

最短路径：

**整理主图和 Methods。**

理由：强震动部分已有 held-out、OpenQuake、uncertainty 三重支撑，phase audit 已有 1,000 条/数据集结果。现在最大瓶颈是图和方法叙述是否能经得起审稿。
