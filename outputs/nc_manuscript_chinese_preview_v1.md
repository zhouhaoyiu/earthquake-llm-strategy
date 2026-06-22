# 基于公开数据刻画早期 P 波预测强震动的边界

周浩宇^1，马强^1*

^1 中国地震局工程力学研究所，哈尔滨，中国。

*通讯作者：马强，maqiang@iem.ac.cn。作者邮箱：zhouhaoyiu@gmail.com。ORCID：周浩宇，0009-0003-8817-1209；马强，0000-0002-9768-5223。

## 摘要

地震预警必须在破坏性地震动充分到达前估计后续强震动。P 波到时后的最初几秒包含震源、路径和场地响应的信息，但这些信息在跨区域预测中的可迁移边界并不清楚。我们构建了一个事件-台站级公开基准，用 P 到时后 1、2、3、5 和 10 秒窗口预测 PGA、PGV 和反应谱加速度。该基准包含 2,460,425 条统一清单记录，主证据来自 InstanceGM 和本地转换的 K-NET，AQ2009GM、CWA 和欧洲强震动数据提供独立补验。早期波形特征在 held-station 测试中持续降低误差：10 秒窗口下 InstanceGM PGA、InstanceGM PGV 和 K-NET PGA 的 MAE 分别降低 35.5%、52.6% 和 49.9%。AQ2009GM 全清单流式验证、CWA 官方 PGA/PGV 一年补验、ESM 欧洲强震动补验、bootstrap、source-path support 和强震动尾部审计均支持同一结论。跨区域迁移显示边界：源域 conformal 区间在目标区域明显欠覆盖，目标域校准可恢复覆盖率，但区间变宽。结果给出了 P 窗口长度、强震动尾部风险和区域不确定性之间的可测量曲线。

## 引言

地震预警需要知道早期 P 波在多大程度上约束后续破坏性地震动。P 到时后的最初几秒是台站最早获得的波形证据。它可能携带震源增长、传播路径、局部场地和初始振幅演化信息，也可能受到区域、仪器和标注体系的限制。

随机划分不能回答这个问题。随机训练测试划分会混合相近事件、台站和路径，局部相似性容易被误认为可预测性。更接近实际预警场景的是 held-event、held-station 和跨区域 transfer：未来地震未在训练集中出现，目标台站未参与训练，或者目标区域与源区域的仪器和地震动分布不同。

公开强震动数据为这个问题提供了足够样本量，也带来严格的数据溯源要求。不同数据集的单位、分量方向、P 到时定义、场地信息和目标变量并不一致。本文以事件-台站记录为基本单位，把一个短 P 窗口、预警时可获得的元数据和同一台站后续观测到的强震动目标连接起来。

主基准使用 InstanceGM 和 K-NET。InstanceGM 提供大规模地震动目标和多样的震源-路径覆盖；K-NET 提供日本强震动记录，并经本地转换得到完整 ZNE 分量。STEAD 和 Iquique 用于相位标注迁移审计。AQ2009GM、CWA 和欧洲强震动数据作为独立补验层，测试同一信息增益是否能在其他公开强震动数据中出现。

本文估计的是离线信息边界。实时通信、报警逻辑和人员响应属于下一层系统问题。这里的预测单元是一个台站的一条事件记录，问题是：在后续强震动目标尚未知时，早期 P 波能在多大程度上减少 PGA、PGV 或 SA 的预测误差。

## 结果

### 公开事件-台站基准连接了波形、目标和评估边界

统一清单包含 2,460,425 条记录。InstanceGM 贡献 1,159,223 条地震动记录，K-NET 贡献 22,119 条完整 ZNE 强震动记录。K-NET 从原始 BSON 包转换为 HDF5 和 CSV 元数据，分量映射为 UD 到 Z、NS 到 N、EW 到 E。NIED 文档说明 K-NET 加速度单位为 gal，等价于 cm/s2。这个转换步骤写入 provenance，因为单位和分量错误会被模型当成区域信号学习。

其他数据源承担清晰角色。STEAD 和 Iquique 检查 P/S 标注域迁移。AQ2009GM 提供一个独立 SeisBench 地震动数据层，当前全清单流式处理覆盖 254 个本地 manifest chunk，保留 345,226 条有效 PGA/PGV 特征记录。CWA 提供台湾官方 PGA/PGV metadata target 的 2011 年补验层，保留 5,882 条有效记录、775 个事件和 705 个台站。ESM 提供欧洲强震动外部域。PNWAccelerometers 只作为波形峰值幅度稳健性检查，因为本地缓存缺少波形单位和官方 PGA/PGV 目标。

每条事件-台站记录提取 P 到时后 1、2、3、5 和 10 秒窗口。特征包括分量最大绝对值、RMS、标准差、95 分位绝对幅值、水平向最大值、三分量向量最大值和向量 RMS。目标变量在 log10 单位下建模。主比较是 source-path metadata 基线与 metadata 加早期波形模型。held-event 和 held-station 划分均检查 group overlap，主验证中的 overlap 为 0。

### 早期 P 波提供了 metadata 之外的信息

早期 P 波在主 held-station 测试中稳定降低误差。10 秒窗口下，metadata 加早期波形模型相对 metadata-only 基线的 MAE 降低为：InstanceGM PGA 35.5%，InstanceGM PGV 52.6%，InstanceGM SA03 26.0%，SA10 20.9%，SA30 27.8%，K-NET PGA 49.9%。这些测试排除了训练和测试台站重叠。

信息增益随窗口长度变化。K-NET PGA 的 held-station 误差降低从 1 秒的 11.3% 增至 5 秒的 23.3%，10 秒达到 49.9%。InstanceGM PGV 在 1 秒已有 40.1% 降低，5 秒为 45.4%，10 秒为 52.6%。这说明不同目标的可用早期信息不同：PGV 更早出现强信号，PGA 对窗口长度更敏感。

K-NET 的 peak-capture 审计给出 lead-time 边界。部分短窗已经包含接近最终 PGA 的水平向峰值。为避免把“已经看到目标峰值”误写成预警信息，我们筛选 early horizontal peak 低于最终 PGA 80% 的 K-NET 记录。在这个 pre-peak 子集中，1 秒和 3 秒窗口仍分别降低 MAE 13.8% 和 17.9%。因此 1 秒和 3 秒结果可以支撑 lead-time 解释；10 秒结果更适合写成较强的 early strong-motion information。

### 稳健性审计显示增益不是抽样偶然

paired bootstrap 对 held-station 测试记录重采样，所有六个主目标的 95% 置信区间下界均为正。最弱下界为 InstanceGM SA10 的 16.9%。K-NET PGA 的 49.9% 平均降低对应 46.6% 到 53.1% 的区间。该审计说明增益在测试记录重采样下保持稳定。

source-path support 审计只根据震级和距离把测试记录限制在训练集中心支持范围内，不使用目标幅值做筛选。该审计保留 82.4% 到 83.9% 的 held-station 测试记录，六个主目标仍全部为正增益，范围为 20.1% 到 54.5%。这降低了“只是测试分布异常造成”的解释空间。

强震动尾部审计聚焦目标幅值最高的 5% 记录。早期波形特征对所有主目标的尾部 MAE 均有降低，范围为 18.9% 到 66.0%。但是 factor-2 underprediction 并未完全消失，InstanceGM SA30 的最强尾部中还出现轻微恶化。该结果支持边界表述：早期 P 波减少强震动尾部误差，但不能消除高后果漏报风险。

残差审计显示剩余误差具有结构。K-NET PGA 的大残差尾部偏向更远距离；InstanceGM 的大残差在 PGA、PGV 和 SA 中重复出现。残差机制表把最大 5% 残差映射到路径衰减边界、强震动尾部边界和早期幅值边界。这个分类是描述性的，不作为因果归因。

### 独立数据层支持同一信息增益

AQ2009GM 是一个独立 SeisBench 地震动补验。流程按本地 chunk manifest 流式处理全部 254 个 chunk，提取早期 velocity features、`trace_pga_cmps2`、`trace_pgv_cmps`、event id 和 station id，写出小特征表后删除原始 chunk 文件。保留结果包含 345,226 条有效 PGA/PGV 记录、60,310 个事件和 66 个台站。5 秒 held-station 测试中，AQ2009GM PGA 和 PGV 的误差降低分别为 55.8% 和 71.9%。

CWA 补上官方独立 PGA/PGV 数据层。当前处理的是公开 CWA benchmark 的 2011 年，不是完整 2011-2021 CWA validation。该层保留 5,882 条有效记录、775 个事件和 705 个台站。held-station 测试中，2 秒窗口 PGA/PGV 分别降低 14.6%/17.7%，5 秒窗口分别降低 29.9%/40.3%。原始 CWA HDF5、metadata、tar 包和失败下载 cache 已在特征提取后删除。

ESM 提供欧洲强震动外部域。当前本地包包含 951 个 zip，得到 134,250 个早窗特征行、861 个事件和 1,568 个台站。ESM 本地头段缺少显式 P 到时，因此使用理论 P 到时。Vp 敏感性审计显示，Vp=5.5 km/s 相对 6.0 km/s 的中位延迟为 2.517 s，Vp=6.5 km/s 的中位提前为 2.130 s。200 条波形 envelope onset  spot audit 中，86 条高置信记录的中位绝对偏移为 1.223 s，95 分位为 3.960 s。ESM 因此作为外部强震动和 transfer 域使用，不能写成 catalog/manual P-pick 证据。

### 经典参考和区域 GMM screening 支持 added-information 结论

我们使用低参数 attenuation-shaped ridge、bias-corrected OpenQuake BooreEtAl2014、K-NET 日本 GMM screening 和 ESM regional GMM screening 作为 classical references。InstanceGM 在当前 split 中有 Vs30；K-NET 缺少 Vs30、rupture distance 和 focal mechanism，因此 K-NET GMM 只能作为 screening reference。

在相同 held-station 行上，metadata 加早期波形模型优于 BooreEtAl2014 参考。相对 BooreEtAl2014，InstanceGM PGA、PGV、SA03、SA10、SA30 和 K-NET PGA 的 MAE 分别降低 36.6%、59.4%、35.4%、36.4%、48.0% 和 60.6%。K-NET PGA 的日本 GMM screening 中，最佳候选 Kanno2006Shallow 的 MAE 为 0.242，而早期波形模型为 0.111。

ESM regional GMM screening 使用 BooreEtAl2014、AkkarEtAl2014、BindiEtAl2014 和 CauzziEtAl2015 候选。相对最佳 screened regional GMM，早期 P+distance+site 模型在 2 秒 PGA/PGV 上降低 MAE 34.8%/23.8%，5 秒为 48.3%/30.2%，10 秒为 43.1%/30.4%。这个层是目前最强的经典参考补充，但仍属于 screening，因为 rupture geometry、rake 和完整构造类型信息不完备。

### 不确定性和跨区域迁移给出边界

target-domain conformal intervals 在主 held-station 测试中接近或略低于 90% 标称覆盖率。K-NET PGA 覆盖率为 0.925，InstanceGM PGV 为 0.898，其他 InstanceGM 目标为 0.820 到 0.876。这说明在同一目标域校准时可以得到可用的不确定性估计。

跨区域直接迁移时，coverage 明显失效。2 秒和 5 秒 transfer 中，source-domain conformal coverage 分别为 0.468 和 0.298，对 0.90 标称覆盖率的 gap 为 0.432 和 0.602。target-offset conformal calibration 可把覆盖率拉回接近 0.90，但中位区间宽度达到 2.177 log10 units。结论很直接：源区域残差不能直接代表目标区域不确定性。

跨区域误差曲线同样显示边界。四域 transfer 使用早期波形特征，不使用震级、距离、场地、event id 或 station id。zero-shot transfer 的中位 MAE penalty 从 1 秒的 2.25 倍升至 10 秒的 4.27 倍。target-offset 校准可降低 penalty，但所有窗口仍高于目标域训练。更多早期波形信息提升域内预测，也可能放大区域和仪器差异。

## 讨论

本文支持一个收窄但可验证的结论：早期 P 波窗口包含 metadata 之外的强震动信息；这种信息在 held-event、balanced held-station、AQ2009GM、CWA 和 ESM 补验中保持可见；跨区域迁移和 conformal coverage 显示它有清晰边界。

该结论限定在离线 event-station 信息增益和不确定性边界。实时系统还需要通信延迟、触发逻辑、报警阈值、前瞻验证和用户响应评估。

当前最强主证据是 InstanceGM PGV、InstanceGM PGA 和 K-NET PGA。SA 目标也有正增益，但 tail underprediction 和 calibration 风险更明显。残差审计不是附属装饰，而是结果的一部分：它指出哪些强震动记录在加入早期 P 波后仍难以预测。

现在的 NC 概率可诚实写成 65-70%。CWA 官方 PGA/PGV 层补上了一个关键独立数据短板，ESM regional GMM screening 提升了 classical-reference 对照强度，四域 transfer 给出了边界曲线。要稳定冲到 70-80%，仍需要更强的独立证据，例如人工 ESM P pick 小样本验证、完整区域 GMPE/GMM 对照，或更明确的物理机制层。

## 方法概述

### 数据源和目标

主基准使用 InstanceGM 和 K-NET。支持分析使用 STEAD、Iquique、AQ2009GM、CWA、ESM 和 PNWAccelerometers。目标在 log10 单位下建模，包括 PGA、PGV 和 SA。K-NET PGA 使用 NIED 文档支持的 gal 到 cm/s2 映射。AQ2009GM 和 CWA 使用 metadata 中的 `trace_pga_cmps2` 和 `trace_pgv_cmps`。ESM PGA/PGV 从本地 ACC.AP 和 VEL.AP 文件计算。

### 特征和模型

P 窗口特征在 1、2、3、5 和 10 秒上提取。full-record peak features 不进入预测特征，避免目标泄漏。主模型为稳定的树模型，核心比较为 metadata-only 与 metadata plus early waveform。跨区域 transfer 只使用早期波形特征，排除震级、距离、场地、event id 和 station id。

### 划分和验证

held-event 保证事件不重叠，held-station 保证台站不重叠。所有主结果都记录 train groups、test groups 和 group overlap。group overlap 非零即不通过 verifier。bootstrap、source-path support、strong-tail、residual-persistence、conformal 和 transfer 审计用于刻画边界，而不是扩大主结论。

### 软件和复现

当前结果由本地 `zhy` 环境生成，主要依赖 Python 3.12、pandas、scikit-learn、matplotlib、h5py、SeisBench 和 OpenQuake。仓库保留派生特征表、split、metrics、图表和 verifier。原始波形数据按各提供方许可获取，不在最终公开仓库中重新分发。

## 图注草稿

**图 1｜公开数据基准设计。** InstanceGM 和 K-NET 支撑主域内强震动测试；AQ2009GM、CWA 和 ESM 提供外部补验；STEAD 和 Iquique 支撑相位窗口质量控制。

**图 2｜更长 P 窗口增加强震动信息。** 早期波形特征从短窗口开始降低均值误差和尾部误差，不同目标显示不同饱和曲线。

**图 3｜held-out 测试显示增益可泛化到未见事件和未见台站。** group-overlap 检查为零，分布审计显示 held-station 是更接近部署的困难测试。

**图 4｜早期波形观测优于可用经典参考，但需要校准。** OpenQuake 和区域 GMM screening 支持 added-information 结论，conformal panel 显示目标依赖的校准边界。

**图 5｜残差结构显示早期 P 波仍无法完全解释的强震动部分。** 距离尾部、重复高残差记录和欠预测风险构成后续物理解释和数据改进目标。

**图 6｜P 窗口对齐足以支撑主任务，S 相迁移更不稳定。** phase audit 支持 P-window benchmark，而不是泛化成完整相位迁移结论。

**图 7｜可预测性边界在域内为正，在直接跨区域迁移下脆弱。** 域内信息增益随窗口增长，跨区域误差 penalty 增大，source conformal 欠覆盖，强震动尾部仍保留漏报边界。

**扩展数据图 1｜高残差波形案例。** 展示加入早期波形后仍有大残差的 InstanceGM 和 K-NET 记录，用于审计，不作因果归因。

**扩展数据图 2｜大残差集中在特定协变量角落。** IQR 标准化偏移把残差尾部分为路径衰减、强震动尾部和早期幅值边界。
