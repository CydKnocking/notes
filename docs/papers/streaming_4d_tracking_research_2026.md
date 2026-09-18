# 动态长序列的 4D 重建与 Point Tracking：文献调研与选题判断

> 更新至 **2026-09-17**。面向正在准备 ICLR/CVPR 级论文的研究合作者。
>
> 已确认设置：**单目 RGB、未知相机位姿、动态场景、流式输入或长视频；可用 8 张 H20D；优先 training-free、测试时优化/适配或有限微调。**  
> 本文在已有 4D/tracking/长序列笔记基础上重新检索原论文、补充材料和官方代码。论文结果、作者的资源报告与本文的研究推断分别标明；没有实际运行模型，也没有实测 H20D 性能。

> **本轮增量阅读入口：第 13–18 节。** 补查 2026 年论文、近期公开稿及代码更新，并扩展到机器人、视频生成/编辑、姿态估计和场景理解。第 1–12 节保留 9 月 8 日的研究脉络；Point4D、TAPNext++ 等已重新核实的状态在原处修正，其他旧条目不代表本轮逐一重审。

## 1. 先给选题判断

**这个方向值得做，但“4D reconstruction + tracking + streaming + 少量训练”已经不足以定义创新。** St4RTrack 已联合世界坐标重建、跟踪和测试时适配；Flow4R 用 scene flow 统一几何与运动；V-DPM 将动态点图扩展到视频；Point4Cast 已面向流式输入维护可按时间查询的场景状态。因此，论文应围绕一种明确、可复现的失效机制展开，而不是围绕模块组合展开。[St4RTrack](https://arxiv.org/html/2504.13152v1)、[Flow4R](https://arxiv.org/html/2602.14021v1)、[V-DPM](https://arxiv.org/html/2601.09499v1)、[Point4Cast](https://www.merl.com/research/highlights/point4cast)

**我的优先建议是研究：有限记忆下，如何用当前可获得的证据，持续校正世界几何，同时保持动态物质点身份。** 具体先验证“相机/尺度漂移、物体真实运动和对应错误相互补偿”是否是现有模型的主要长程失败来源，再决定做低维在线优化、可观测性约束的 TTA，还是身份记忆。这里是研究假设，不是已验证的新颖性或性能结论。

**9 月 17 日补充：** 应把 **4RC/S-4RC、Complet4R 和正式公开的 Point4D** 加入直接竞争集。S-4RC 已有因果联合重建/运动查询，Complet4R 已展示 8 卡一天级微调，Point4D 已实现跨窗口 3D endpoint 传递。因此，“流式 + 小成本微调”以及“3D 轨迹跨窗口连接”需要更窄、更可证伪的问题定义，详见第 14、18 节。[4RC](https://arxiv.org/html/2602.10094v1)、[Complet4R](https://arxiv.org/html/2603.27300v1)、[Point4D](https://arxiv.org/html/2609.09145v1)

对我们最重要的变化有四个：

1. **长序列 2D tracking 已有新强基线。** TAPNext++ 明确处理长时间跟踪与重新检测；Track-On2 已有推理时记忆扩展。不能只和早期 CoTracker/TAPIR 比较。[TAPNext++](https://arxiv.org/html/2604.10582v1)、[Track-On2](https://arxiv.org/abs/2509.19115)
2. **通用 memory gate、Kalman 更新和动态区域抑制已经拥挤。** TTT3R、FILT3R、RayMap3R 分别覆盖这些方向。仅增加一个动态置信权重，创新风险很高。[TTT3R](https://rover-xingyu.github.io/TTT3R/)、[FILT3R](https://arxiv.org/html/2603.18493v1)、[RayMap3R](https://arxiv.org/html/2603.20588v1)
3. **窗口拼接和世界坐标评估也有非常新的先例。** 9 月 1 日提交的 TAPVid-MV 已评测共同世界坐标，附录还实现短窗口重建模型的对齐和轨迹交接。它的多视角主任务不等同于我们的单目设定，但这些实现必须进入创新性检查。[TAPVid-MV](https://arxiv.org/html/2609.01899v1)
4. **8 卡允许有竞争力的研究，不能理解成必须完全不训练。** St4RTrack 的公开训练与 TTA 成本是很实际的参照；反之，V-DPM 的“适量微调”实际使用 16 GH200，LoGeR 使用两阶段 32 卡训练。应选可复用的权重和小范围改动，而非重做基础模型。[St4RTrack §4.1](https://arxiv.org/html/2504.13152v1)、[V-DPM 补充材料 §6](https://arxiv.org/html/2601.09499v1)、[LoGeR §4](https://arxiv.org/html/2603.03269v1)

## 2. 先把任务定义清楚

### 2.1 我们真正需要输出什么

给定截至时刻 t 的图像 I₁,…,Iₜ 和查询点，应输出：

- 当前帧稠密几何，以及估计的相机参数；
- 查询所指的同一个物理表面点在共同世界坐标下的轨迹 xᵢ(t)；
- 可见性、存在性或定位可靠性；
- 可持续更新的状态，使新物体、新表面和遮挡后重现能够进入同一个表示。

“每帧都有点云”不足以确定物质点运动。例如，一个外形不变但旋转的球，其逐帧表面几何可以完全相同，表面点身份却持续移动。这正是动态点图/轨迹表示相对逐帧深度的重要性。[TAPVid-3D 引言](https://arxiv.org/html/2407.05921v2)、[V-DPM §3](https://arxiv.org/html/2601.09499v1)

建议实验主任务写成：

> 在单目 RGB、未知相机位姿条件下，对动态视频进行因果或明确固定延迟的处理，在受限工作记忆与计算预算下，联合估计几何、相机和长期 3D 点轨迹。

内参 K 尚未由用户指定。建议主实验使用预测 K；另报告已知 K 的校准设定。两者必须分行，不能把已知内参与完全未标定输入混报。

### 2.2 四个容易混淆的概念

| 表述 | 必须核查的内容 | 对本文的含义 |
|---|---|---|
| Dynamic reconstruction / 4D | 是否输出同一物质点的时间对应，还是只输出时变深度/点云 | 重建漂亮不等于 tracking 正确 |
| Online / streaming | 当前输出是否需要未来帧；是否先运行全片深度、pose 或 tracker | 前端和后端都因果，才是端到端因果 |
| Long sequence | 是真实完整长视频，还是裁成 16/40/64 帧；是否保留跨遮挡身份 | 要同时报告输入长度与连续跟踪时长 |
| Constant memory | 是 GPU active state，还是连 CPU 地图、历史图像、优化器都固定 | 保存完整历史输出本身会增长；应限定工作记忆 |

这里尤其要区分三种执行方式：

- **严格因果**：时刻 t 的输出只依赖 I≤t。
- **固定延迟**：允许 L 帧 lookahead，报告 L、首帧等待和端到端延迟。
- **离线**：可以使用整段视频、双向跟踪、全局 BA 或最后状态回看历史。

对于块内双向注意力，块末到达后才输出整块，属于有块延迟的处理。滚动使用已到达历史窗口、仅输出当前帧，也可实现严格因果，但计算与准确率需要重新测。不要仅凭论文标题替方法归类。

### 2.3 Training-free、TTO、TTA 和 TTT

| 类型 | 测试时改变什么 | 典型参照 |
|---|---|---|
| Training-free intervention | 冻结模型，改变推理规则、记忆筛选或对齐 | TTT3R、RayMap3R、LASER |
| Test-time optimization，TTO | 相机、深度、轨迹、Gaussians 等场景变量 | DynOMo、Shape of Motion、MotionScale |
| Test-time adaptation / training | 网络权重、prompt、adapter 等 | St4RTrack TTA、Test3R、Online3R |
| Fast-weight / sequence-model TTT | 把历史信息写入可快速更新的权重状态 | LoGeR |
| Fine-tuning | 测试前在训练数据上更新模型 | V-DPM、PointSt3R、TAPNext++ |

这些标签可以重叠。例如 TTT3R 从 TTT 角度解释状态更新，但其干预无需额外模型训练；LoGeR 虽使用测试时快权重记忆，仍需要训练整个适配后的模型。“zero-shot”则通常指训练后跨域推理，不能推出没有训练。[TTT3R](https://rover-xingyu.github.io/TTT3R/)、[LoGeR](https://arxiv.org/html/2603.03269v1)、[ZeroMSF](https://arxiv.org/html/2501.10357v1)

## 3. 核心文献：直接决定选题的联合方法

### 3.1 St4RTrack：首先复现，而且要用当前权重

**Feng、Zhang 等，ICCV 2025。** 双分支点图在共同世界坐标中同时表达重建与点运动；固定参考帧与后续帧配对即可顺序预测。TTA 用 2D trajectories 和单目深度，通过可微 PnP / 重投影监督适配无 4D 标注视频。它已经覆盖“联合 4D + tracking + 自监督测试时适配”的基本命题。[论文](https://arxiv.org/html/2504.13152v1)

真正的边界在于：原方法没有持续吸收历史的显式长期记忆；24 帧训练，WorldTrack 主实验为四个子集各 50 条、前 64 帧；“理论上能继续配对”不等于千帧身份保持已经成立。原 TTA 使用整段测试视频的监督来源，不能直接算作因果在线 TTA。[论文 §4 与附录](https://arxiv.org/html/2504.13152v1)

**代码版本是重要变量。** 官方仓库在投稿后发现模型会通过压低动态像素的 confidence 来逃避运动误差，新增 dynamic pixel reweighting，默认推荐 Seqmode_reweightMax5。Dynamic Replica 的 dynamic APD 从旧版 68.13 到 76.82，但 ADT all-points 从 76.00 到 73.03，并非所有项一致上涨。因此要固定 checkpoint；仅引用后来论文中旧版 St4RTrack 的表格不够。[官方代码与修正说明](https://github.com/HavenFeng/St4RTrack)

**对我们：第一网络基线，也是 TTA 必须超越的直接对照。** 特别值得研究动态置信度、可见性和可观测性之间的区别。

### 3.2 Flow4R：运动分解和跨对尺度已经有人处理

**Qian、Zhang、Wu、Cremers，2026；官方项目标 ECCV 2026。** 两帧图像预测点图、camera-space flow、pose weights 等，通过加权刚体配准分解相机与场景运动。采用固定 anchor 配对所有后续帧，并根据 anchor 点图的平均范数校准尺度。[论文](https://arxiv.org/html/2602.14021v1)、[官方项目](https://shenhanqian.github.io/flow4r)

它比“独立点图相减”更明确地建模了相机/物体运动，但仍是 anchor-pair 机制，WorldTrack 主要仍评前 64 帧。从 CroCo 初始化、跨多数据集训练，不是直接无训练插件。官方项目和定向搜索未确认可运行算法仓库；这应写成“代码未确认”，不能断言永久未开源。

**对我们：必须检查运动分解是否与它重复；也要补比 St4RTrack 新版，不能照抄旧对比表。**

### 3.3 V-DPM：很合适的表示骨干，但长视频输出成本不能忽略

**Sucar、Insafutdinov、Lai、Vedaldi，CVPR 2026。** VGGT 先预测各帧自身时刻的点图，再用时间条件 decoder，把不同观测映射到共同查询时刻。这样一个表示同时支持动态几何与稠密时间对应，且复用静态几何预训练。[论文](https://arxiv.org/html/2601.09499v1)、[官方代码](https://github.com/eldar/vdpm)

限制很直接：训练窗口约 20 帧以内，作者报告测试能泛化至约 50 帧；几百帧的 depth/pose 实验采用滑窗和 BA 融合。这并非已经验证的长期动态身份跟踪。其多帧上下文有实际作用，直接替换成 causal attention 可能破坏预训练分布，必须和冻结骨干滑窗方案比较。[正式论文 §4.2](https://openaccess.thecvf.com/content/CVPR2026/papers/Sucar_V-DPM_4D_Video_Reconstruction_with_Dynamic_Point_Maps_CVPR_2026_paper.pdf)

**对我们：适合作为“短窗口强先验 + 小型在线机制”的主骨干。** 但每帧、每像素、每查询时刻全部解码会产生很大的输出规模；应固定活动查询集、使用按需查询，而非把全历史稠密轨迹存储开销隐藏在推理之外。这是复杂度上的推断。

### 3.4 Track4World：轨迹帮助相机优化也已被覆盖

**Track4World，2026；官方仓库标 ECCV 2026。** 将全视频几何推理、帧对 2D/3D flow 和时间聚合结合，输出世界坐标稠密轨迹。代码有 DA3、π3、MoGe 相关模型路径。[论文](https://arxiv.org/html/2603.02573v1)

补充材料已有测试时相机细化：识别动态区域后，利用静态 3D tracks 进行 clip 内、clip 间及全序列优化。因此“用 tracks 做 BA”也不是空白。其全片联合处理及最终全局优化，留出了因果、有界预算场景的差别，但差别需要算法与实验共同证明。[论文附录 F](https://arxiv.org/html/2603.02573v1)

### 3.5 D4RT、Point4Cast：要读来校准论文上限

**D4RT，Zhang、Le Moing 等，CVPR 2026**，使用视频编码和查询解码统一 4D reconstruction 与 tracking；长视频处理有重叠 chunks 与置信点 Sim(3) 对齐。它说明统一查询式 4D 表示已经是强竞争方向。其长相机轨迹实验不能自动等价为千帧动态物质点身份测试。原版和第三方 OpenD4RT 复现必须分开记账。[D4RT 官方项目](https://d4rt-paper.github.io/)、[论文及补充材料](https://arxiv.org/html/2512.08924v2)

**Point4Cast，Liu 等，CVPR 2026**，维护持续更新的时空 latent state，给定 query image 和时间读出过去、当前或未来点图，也可导出 scene flow。它直接覆盖“流式状态 + 时间条件查询 + 未来几何”这一组合。[CVF 正式条目](https://openaccess.thecvf.com/content/CVPR2026/html/Liu_Point4Cast_Streaming_Dynamic_Scene_Reconstruction_and_Forecasting_CVPR_2026_paper.html)、[MERL 官方说明](https://www.merl.com/research/highlights/point4cast)

本次 Point4Cast 全 PDF 因抓取大小限制未完整读入；训练设备仅核到原 PDF 的可检索段落，代码完整性和精确长序列协议仍未确认。因此不基于它的摘要宣称其已解决全部长程 tracking。

### 3.6 OmniX 与 Point4D：最新的创新性约束

**OmniX，2026-07 预印本**，用 trajectory fields 处理更自由的视角与运动，分离动态前景与静态结构，并构建大规模 UE5 数据。值得注意的是，原论文各项评价均裁成 **16 帧**；这些结果不能当成完整 TAPVid-3D 长视频成绩。[论文 §4](https://arxiv.org/html/2607.10840v1)

**Point4D: Long-range 4D Motion Reconstruction，Jeon、Karhade、Ramanan、Tulsiani，2026-09-08 UTC 首发。** 9 月 17 日已核到署名全文、项目和实际推理代码，替代上一版仅有匿名索引稿的证据。方法以 3D point query、跨 chunk endpoint chaining 和可见帧外观描述子支持长程 tracking；仍需重叠几何对齐。属于窗口处理，不能据此标成逐帧严格因果。[署名论文](https://arxiv.org/html/2609.09145v1)、[官方代码](https://github.com/point-4d/Point4D)

目前仅确认预印本，**未确认 NeurIPS 2026 录用**；训练代码和权重下载完整性未核实。长序列协议、完整窗口遮挡局限与对我们选题的影响见第 14.1 节。

## 4. 从优化式 4D 表示中学什么

| 方法 | 方法本质与有价值的设计 | 对当前任务的实际边界 |
|---|---|---|
| **DynOMo，Seidenschwarz 等，3DV 2025** | 在线维护动态 Gaussians，联合相机定位，使用深度、语义与 DINO 特征，轨迹从重建得到 | 作者约 45 秒/帧，非实时；各数据集先验来源不同，完整前端因果性需审；适合作在线优化对照 |
| **Shape of Motion，Wang 等，ICCV 2025** | 持久 Gaussians + 共享 SE(3) motion bases，整合长程 2D tracks 和深度 | 重建模块输入相机；全视频优化。约 2 小时/300 帧是重建，140 FPS 是重建后渲染 |
| **4D-Fly，Wu 等，CVPR 2025** | anchor 传播、canonical map 扩展和逐帧 Gaussian 优化 | 已知 K/E；5.3 分钟对应 100 帧；历史 replay、前端与 DyCheck LiDAR depth 要单列，不能直接称纯 RGB 实时流 |
| **ProDyG，Chen 等，NeurIPS 2025** | 静态 SLAM 后端与 progressive 动态 scaffold，批次间扩展轨迹 | 批次处理；论文指出物体出视野后再现的欠约束；仓库仍是展示内容，算法代码未确认发布 |
| **MotionScale，Zhou、Lee，CVPR 2026** | cluster-centric 全局/局部运动基、自适应 split/prune、逐步扩展背景与相机细化 | 默认 π3/SAM2/CoTracker3 先验；单 4090 实验，但长期阶段仍采样全部已优化历史，未证明总工作记忆固定 |
| **C4D，Wang 等，ICCV 2025** | 短期 flow + 长期 tracks 的双对应，联合优化深度、相机和运动区域 | 整体非 training-free：DynPT 需训练；窗口含前后额外帧，且有全局优化；官方仓库仍待完整代码 |

来源：[DynOMo 论文](https://arxiv.org/html/2409.02104v1) / [代码](https://github.com/dvl-tum/DynOMo)；[Shape of Motion](https://arxiv.org/html/2407.13764v2) / [代码](https://github.com/vye16/shape-of-motion/)；[4D-Fly](https://diankun-wu.github.io/4D-Fly/) / [正式论文](https://openaccess.thecvf.com/content/CVPR2025/papers/Wu_4D-Fly_Fast_4D_Reconstruction_from_a_Single_Monocular_Video_CVPR_2025_paper.pdf)；[ProDyG](https://arxiv.org/html/2509.17864v1) / [仓库](https://github.com/cs-vision/ProDyG)；[MotionScale](https://arxiv.org/html/2603.29296v1) / [代码](https://github.com/hrzhou2/motion-scale)；[C4D](https://arxiv.org/html/2510.14960v1) / [仓库](https://github.com/littlepure2333/C4D)。

**阅读时最值得抓住的是“表示的身份是否稳定”。** Photometric reconstruction 可以通过复制、删除或重新分配 Gaussians 改善渲染，却未必保持同一物质点。动态表面的 split/merge、遮挡期间正则化、回到视野后的重新关联，是比 PSNR 更直接的 tracking 问题。这是本文的机制分析，需通过原语身份与表面对应的实验验证。

若选择 Gaussian 路线，必须区分：优化耗时、预处理耗时、渲染 FPS 和轨迹查询耗时。训练自由度少不代表总实验便宜；每视频优化 × 多基线 × 多消融可能比一次微调更费时。

## 5. Point tracking 谱系：哪些必须成为前端或对照

### 5.1 2D 跟踪的实用主线

| 方法族 | 应重点阅读的部分 | 用于我们工作的角色 |
|---|---|---|
| **TAPIR → BootsTAP** | 查询匹配、轨迹细化、遮挡；从无标注视频自举训练 | 基础 tracker 与伪监督思想，不能把旧版当唯一对照 |
| **CoTracker → CoTracker3** | 多点联合推理、真实视频伪标签；online 为半窗重叠滑窗，需报告窗口延迟 | 易用的强 2D 前端和控制变量；非默认逐帧零延迟 |
| **TAPNext → TAPNext++** | SSM/递归跟踪、长训练上下文、重新检测；++ 直接针对长时退化 | 若声称严格在线或长期重现，应加入较新基线 |
| **Track-On2** | query memory、推理时记忆长度扩展 | 检验收益是否只是保存更多外观历史 |
| **Track-On-R** | 多 tracker verifier 选择可靠伪标签、真实视频微调 | “多教师 + confidence 筛选微调”的直接重合工作 |

主要原始来源与实现：[TAPIR](https://arxiv.org/abs/2306.08637)、[BootsTAP](https://arxiv.org/abs/2402.00847)、[CoTracker3](https://arxiv.org/abs/2410.11831)、[CoTracker 官方实现](https://github.com/facebookresearch/co-tracker)、[TAPNext++](https://arxiv.org/html/2604.10582v1)、[Track-On2](https://arxiv.org/abs/2509.19115)、[Track-On-R](https://arxiv.org/abs/2603.12217)、[TAP 官方实现](https://github.com/google-deepmind/tapnet)。

TAPNext++ 尤其重要：从公开 BootsTAPNext-B 微调，使用 8 H100，训练设计针对长序列与再检测，并提出再检测评价。**“延长训练片段 + 遮挡 loss reweighting + 长程新指标”已有直接竞争。** 我们需要证明 3D 几何提供了额外的可检验约束，而非换一个记忆结构重新做同样的事。9 月 17 日核实其正式类别为 **CVPR 2026 Findings**，引用时保留 Findings。[TAPNext++ §4](https://arxiv.org/html/2604.10582v1)、[CVF 正式记录](https://openaccess.thecvf.com/content/CVPR2026F/html/Jung_TAPNext_Whats_Next_for_Tracking_Any_Point_TAP_CVPRF_2026_paper.html)

### 5.2 3D 跟踪：输入几何与坐标系比名称更重要

| 方法 | 核心价值 | 不能默认成立的能力 |
|---|---|---|
| **SpatialTracker / SpaTracker** | 将点跟踪提升到 3D 表示中推理，利用几何邻域 | 使用预测深度不等于消除了相机误差 |
| **DELTA / DELTAv2** | RGB-D 条件下的稠密 UVD tracking；v2 以稀疏更新和学习式插值渐进加密 | 稠密不等于共同世界坐标长期建图；需控制深度输入，效率实验不能只比较旧 DELTA |
| **TAPIP3D** | 在 3D 几何/点云中跟踪，对几何质量敏感；有训练与评估实现 | 给定几何条件下的提升不等于 raw RGB 端到端提升 |
| **SpaTrackerV2** | 相机与物体运动分解、迭代几何/轨迹优化，RGB 到世界 tracking 的直接强基线 | online tracker checkpoint 不足以证明整个几何前端因果 |
| **PointSt3R** | 以 3D grounded correspondence 微调 MASt3R，低训练成本得到 matching/tracking | pair-only，没有真正多帧时间状态 |
| **ZeroMSF** | 两帧 RGB 预测点图和 scene flow；可作为局部运动先验 | zero-shot 不是无训练，camera-space offset 不是持久 world track |

来源：[SpatialTracker](https://arxiv.org/abs/2404.04319)、[DELTA](https://snap-research.github.io/DELTA/)、[TAPIP3D 官方代码](https://github.com/zbw001/TAPIP3D)、[SpaTrackerV2 官方代码](https://github.com/henry123-boy/SpaTrackerV2)、[PointSt3R](https://arxiv.org/html/2510.26443v1) / [代码](https://github.com/rhodriguerrier/PointSt3R)、[ZeroMSF](https://arxiv.org/html/2501.10357v1) / [代码](https://github.com/NVlabs/zero-msf)。

**TAPIP3D（Tracking Any Point in Persistent 3D Geometry，NeurIPS 2025）** 的 persistent 主要指稳定的几何空间，不能直接理解成无界的身份数据库。原文 train/test 窗口为 16 帧；RGB 场景可由 MegaSaM 提供几何。因此适合作可训练 3D tracker，但前端与窗口延迟需纳入评价。[原论文](https://arxiv.org/html/2504.14717v3)

**SpaTrackerV2 的公开状态要谨慎读。** 官方 README 的 online TODO 与实际发布不同步：Hugging Face 已有 Online checkpoint，代码也有加载路径；但已审的 RGB 推理路径先进行整视频几何计算。因此正确表述是“online tracker 权重公开，默认端到端 RGB pipeline 的因果性需要修改与验证”，不能简单写“无 online 代码”或“已经全流程因果”。其 ICCV 2025 正式标题为 Advancing 3D Point Tracking with Explicit Camera Motion，与仓库的 3D Point Tracking Made Easy 是同一工作。[论文](https://arxiv.org/html/2507.12462v2)、[Online 权重](https://huggingface.co/Yuxihenry/SpatialTrackerV2-Online)、[推理代码](https://github.com/henry123-boy/SpaTrackerV2/blob/main/inference.py)

**DELTAv2** 应补入效率实验：它从 DELTA 初始化后训练，不能视作可直接套用的 training-free 插值。CoTracker3 的 online 变体同样要标明重叠窗口延迟，不能和 TAPNext++ 的逐帧模式只按 FPS 对比。[DELTAv2 论文](https://arxiv.org/html/2508.01170v1) / [代码](https://github.com/snap-research/DenseTrack3Dv2)、[CoTracker3 正式论文](https://www.robots.ox.ac.uk/~vgg/publications/2025/Karaev25/karaev25.pdf)

## 6. 流式几何与低成本适配：哪些点已经被占据

| 方法 | 已有贡献 | 对我们选题的约束 |
|---|---|---|
| **MonST3R，ICLR 2025；MegaSaM，CVPR 2025** | 动态视频的深度与相机恢复，几何初始化的重要参照 | 不可把相机改善直接当成长期物质点 tracking 的突破 |
| **CUT3R，CVPR 2025** | recurrent persistent state；RGB 在线预测共同坐标点图 | 动态点云输出本身未定义持久点身份；online 与 revisiting 分开 |
| **StreamVGGT，ICLR 2026** | causal temporal attention 与历史缓存，复用 VGGT | 原始缓存随历史增长；只改因果 mask 也已有先例 |
| **TTT3R，ICLR 2026** | 无额外训练的 per-token state update rate，增强长度泛化 | 通用更新门控不宜单独成为新工作 |
| **FILT3R，2026** | per-token 方差与 Kalman-style gain，训练自由的状态滤波 | “引入不确定性/Kalman 维护记忆”已有直接竞争 |
| **RayMap3R，2026** | 利用 RayMap-only 静态偏置识别动态区域，抑制污染，reset 后 Sim(3) 校准 | “动态 mask + 门控 + 重置尺度对齐”已被组合 |
| **LASER，CVPR 2026** | 冻结离线模型，跨窗口 depth-layer scale alignment | 简单 Sim(3) 不足的观察与分层校准已经有人做 |
| **LoGeR，2026** | 块间局部 attention + 全局 fast-weight TTT，长上下文几何 | 长程几何记忆强对照；块内双向且需训练，不能等同逐帧零延迟 |
| **Test3R，NeurIPS 2025** | shared-reference triplet 一致性 + test-time prompt tuning | 泛化几何一致性适配不是新概念 |
| **Online3R，CVPR 2026** | 冻结几何基础模型、用局部融合与远关键帧约束在线更新 prompt | “历史伪真值 + 小 prompt 在线适配”已被覆盖 |
| **Flow3r，CVPR 2026** | 用 flow prediction 与大量无标注视频改进几何模型 | 2D correspondence 监督几何微调已有工作；它本身非长程 tracker |

原始来源：[MonST3R](https://monst3r-project.github.io/)、[MegaSaM](https://openaccess.thecvf.com/content/CVPR2025/papers/Li_MegaSaM_Accurate_Fast_and_Robust_Structure_and_Motion_from_Casual_CVPR_2025_paper.pdf)、[CUT3R](https://cut3r.github.io/)、[StreamVGGT](https://arxiv.org/html/2507.11539v1)、[TTT3R](https://rover-xingyu.github.io/TTT3R/)、[FILT3R](https://arxiv.org/html/2603.18493v1)、[RayMap3R](https://arxiv.org/html/2603.20588v1)、[LASER](https://neu-vi.github.io/LASER/)、[LoGeR](https://arxiv.org/html/2603.03269v1)、[Test3R](https://papers.nips.cc/paper_files/paper/2025/file/911dd89c81efc624c4e1c39381179505-Paper-Conference.pdf)、[Online3R](https://arxiv.org/html/2604.09480v1)、[Flow3r](https://arxiv.org/html/2602.20157v1)。

还有两个判断边界：

- **静态世界记忆与动态实体记忆的目标不同。** 保持背景稳定时可以压制动态像素；如果要跟踪运动实体，把这些像素从记忆中删除就会损失任务需要的信息。因此潜在贡献应研究保留什么、如何随运动更新、何时视为不可观测，而不是只降低动态权重。
- **全局尺度一致不等于动态几何正确。** 即使相机和背景对齐得很好，局部前景仍可能产生错误深度、沿表面滑动或身份交换。评估必须拆开这几类误差。

## 7. 8 张 H20D：真实成本与复现顺序

以下为作者报告，**不同设备、分辨率、点数、数据与计时边界不同，不能直接比较，更不能换算成 H20D 的承诺耗时。**

| 方法 / 阶段 | 原文资源 | 决策含义 |
|---|---|---|
| St4RTrack 训练 | 4 A100，50 epochs，约 1 天 | 相对可行的训练规模先例 |
| St4RTrack 单序列 TTA | 4 A100，500 steps，约 5 分钟 | 适配并不免费，需计入端到端耗时 |
| PointSt3R 微调 | 4 H100，约 12 小时 | pair correspondence 小规模改造的先例 |
| ZeroMSF 训练 | 8 A100，约 12 小时 | 局部 scene flow 可做；数据准备另算 |
| Flow4R 训练 | 8 A100/H100，约 4 天 | 卡数接近，但数据体系和训练目标并不轻 |
| V-DPM 训练 | 16 GH200，60 epochs | 优先复用已发布模型，避免照搬完整训练 |
| StreamVGGT 微调 | 4 A800，10 epochs，约 950M 可训练参数 | “微调”不一定是参数高效适配；原文未给可直接套用的耗时 |
| TAPNext++ 微调 | 8 H100，20,000 steps / dataset，有效 batch 1 | 长上下文训练仍需实测激活与并行开销 |
| SpaTrackerV2：仅 SyncFormer 阶段 | 8 H20，100k steps，约 3 天 | 前端另用了 64 H20，之后还有联合训练；不能当整个系统成本 |
| TAPIP3D 训练 | 8 L40S，200k steps，约 4.2 天 | 可训练的小 tracker 路线，输入几何与前端成本另算 |
| LoGeR 训练 | 32 H100 约 2 天，再 32 H200 约 2 天 | 不作为当前首选训练路线 |
| MotionScale 实验 | 单 RTX 4090 | 硬件可访问，但每视频优化与全历史阶段成本需测 |
| Shape of Motion 重建 | 单 A100，300 帧约 2 小时 | 不等同其 140 FPS 渲染速度 |
| DynOMo 在线优化 | RTX 3090，约 45 秒/帧 | 可作质量/机制参照，吞吐较低 |

成本来源：[St4RTrack](https://arxiv.org/html/2504.13152v1)、[PointSt3R](https://arxiv.org/html/2510.26443v1)、[ZeroMSF](https://arxiv.org/html/2501.10357v1)、[Flow4R](https://arxiv.org/html/2602.14021v1)、[V-DPM 补充材料](https://arxiv.org/html/2601.09499v1)、[StreamVGGT §4.1](https://arxiv.org/html/2507.11539v1)、[TAPNext++ §4.2](https://arxiv.org/html/2604.10582v1)、[LoGeR §4 / A.3](https://arxiv.org/html/2603.03269v1)、[MotionScale](https://arxiv.org/html/2603.29296v1)、[Shape of Motion](https://arxiv.org/html/2407.13764v2)、[DynOMo](https://arxiv.org/html/2409.02104v1)。

新增成本来源：[SpaTrackerV2 训练细节](https://arxiv.org/html/2507.12462v2)、[TAPIP3D 训练细节](https://arxiv.org/html/2504.14717v3)。

### 建议的实施顺序

1. **先用 8 卡并行评估，不急于分布式训练。** 复现 St4RTrack 新权重、V-DPM 短窗、一个 2D tracking + geometry lifting 的强基线；统一 RGB 输入和指标。
2. **优先冻结大模型，仅优化可解释的小变量。** 相机/尺度、局部 motion state、少量 prompts/adapters 或稀疏因子；每次迭代限定历史窗口与更新步数。
3. **先测再决定训练长度。** 记录单卡峰值显存、forward/backward、输入分辨率、query 数和激活开销。LoRA 减少参数与优化器状态，不会自动消除长序列 attention 激活。
4. **确定最小机制有效后，再做有限微调。** 八卡累计 GPU-hours = GPU 数 × 小时，是设备内部预算记账方式，不是跨 A100/H100/H20D 的速度换算。

优先下载与运行的代码：St4RTrack、V-DPM、CoTracker/TAPNext、TAPIP3D；选择 Gaussian 路线时加入 DynOMo/MotionScale。Flow4R、C4D、ProDyG、Point4Cast 不宜在尚未确认完整代码时成为两周 pilot 的唯一依赖。

## 8. 三个候选方向与证伪实验

以下均是基于文献的**研究建议**。它们尚未获得实验支持，也不代表已完成穷尽的新颖性检索。建议先选一个主机制，避免同时引入 memory、LoRA、BA、分割和运动基，最后难以解释收益来源。

### 方向 A：可观测性约束的因果 4D 适配——首选

**问题。** 重投影误差下降时，相机、深度和物体运动可能相互补偿，世界轨迹反而更错。伪标签也可能与当前几何模型共享错误；只做自一致性会强化错误。静态纹理不足、相机纯旋转或运动物体占满画面时，部分自由度本来就无法可靠估计。

**最小方案。** 用冻结的 St4RTrack 或 V-DPM 得到局部几何和候选轨迹；在固定历史窗口中只更新相机/尺度与低维运动变量。利用可靠静态锚点、运动一致的局部点组和可见性，识别哪些参数方向受到数据约束；对欠约束方向保留先验或扩大不确定性。先用小型显式优化验证，收益成立后再考虑将相同约束放入 adapter/prompt 更新。

可用的目标结构是：

    E = 可见点重投影误差
      + 独立来源的深度/跨观测几何约束
      + 可靠静态锚点的世界一致性
      + 适用于局部运动的弱先验
      + 防止无依据大幅更新的约束

关键不是这些 loss 名称，而是**如何避免不可辨识的自由度吸收误差**。局部线性化后可检查加权 Jacobian 的弱方向，或用受控扰动分析相机、深度、运动之间的可互换性。不能在没有满足假设时宣称恢复了唯一真实运动。

**最近竞争。** St4RTrack TTA、Flow4R 的运动分解、C4D、Track4World pose refinement、Test3R/Online3R，以及 FILT3R 的置信更新。区别必须落在参数可辨识性、因果证据与联合轨迹效果上，不能仅称“更好的 confidence”。[St4RTrack](https://arxiv.org/html/2504.13152v1)、[Track4World](https://arxiv.org/html/2603.02573v1)、[Online3R](https://arxiv.org/html/2604.09480v1)、[FILT3R](https://arxiv.org/html/2603.18493v1)

**必须通过的实验。**

- 相同 backbone、伪标签、梯度/优化步数下，对比普通 TTA、置信加权、只优化 pose、只优化 depth。
- 画出低重投影误差但高 world-track error 的实际反例，并证明机制减少这种失配。
- 分别用 GT camera、GT depth、GT correspondence 做诊断，定位收益来源。
- 若改善完全来自 pose，对 dynamic identity 没有帮助，应收窄为相机/几何贡献，不能包装成 tracking 突破。

**适合投稿的论点。** 计算预算下，对“什么能从当前视频中学到”作明确建模，并在多个场景/骨干上验证。若仅是在一套 pipeline 上调 loss 权重，贡献仍偏弱。

### 方向 B：可见性删失下的持久身份——第二选择

**问题。** 被遮挡、出视野和真实消失不是同一件事。图像没有观测时，轨迹平滑正则容易把点吸向错误表面；再次出现时，重建可以解释外观，却可能已经交换身份。

**最小方案。** 显式保存固定数量的点/局部表面身份、最后可靠外观、运动状态与不确定性；不可见期间禁止将预测当作新测量反复自我强化；重现时由几何与外观共同重新关联。若使用 Gaussians，要记录 split/merge 后的身份继承，而非把 Gaussian index 直接当物质点身份。

**最近竞争。** TAPNext++ 的重新检测、Track-On2 memory、DynOMo 持久特征、ProDyG scaffold、MotionScale，以及 Point4D 的 3D query 跨窗口传递。**仅把 endpoint 改成 3D query 已经不够。** 重点应是观测缺失时的状态更新与身份恢复，并验证其对几何的反向帮助。[TAPNext++](https://arxiv.org/html/2604.10582v1)、[DynOMo](https://arxiv.org/html/2409.02104v1)、[ProDyG](https://arxiv.org/html/2509.17864v1)、[Point4D 公开稿](https://msjeon.me/data/Point4D.pdf)

**必须通过的实验。** 同外观物体交叉、接触/分离、遮挡长度分桶、离开视野后重现；报告重新捕获率、错误关联、恢复延迟、world-track error，并同时检查重建。只提升 PSNR 或仅在可见帧变好，不支持持久身份主张。

**风险。** 单目长时间完全不可见运动无法唯一恢复。应评价可见时正确恢复及不确定性是否合理，不应要求模型猜中任意不可观测运动。

### 方向 C：保留动态约束的有限记忆优化——偏系统但可做深

**问题。** MotionScale 一类方法用全部历史细化维持长期一致性；神经状态压缩则可能丢失细粒度运动和身份。我们需要知道哪些历史约束真正影响未来的几何与点身份。

**最小方案。** 固定前端，将过期图像/轨迹约束压缩为稀疏因子或边缘化信息，保留对相机 gauge、局部变形与身份仍有效的约束。与随机 reservoir、关键帧 replay、纯 latent gate 在相同预算比较。明确什么被保留、什么被近似，以及动态物体如何避免污染静态约束。

**最近竞争。** MotionScale 全历史细化、LASER 对齐、TTT3R/FILT3R/LoGeR 记忆与 TAPVid-MV 的窗口基线。泛称“4D memory”或“动态关键帧选择”不足以区分。[MotionScale](https://arxiv.org/html/2603.29296v1)、[LASER](https://neu-vi.github.io/LASER/)、[LoGeR](https://arxiv.org/html/2603.03269v1)、[TAPVid-MV](https://arxiv.org/html/2609.01899v1)

**必须通过的实验。** 完整长视频逐前缀 256/512/1024/全长，固定活动点数、GPU/CPU 工作记忆和每帧优化预算；比较长期动态误差、相机漂移与重现恢复。若收益来自越来越大的历史缓存，或 equal-compute 的大窗口已达到同样效果，这个方向不成立。

### 三个方向的取舍

| 方向 | 预计主要投入 | 创新最容易失败的位置 | 当前优先级 |
|---|---|---|---|
| A：可观测性与在线适配 | 小变量优化、误差诊断、有限微调 | 退化成已有重投影 + confidence loss | 第一 |
| B：持久身份与遮挡恢复 | 跟踪状态/关联、可见性、诊断数据 | 退化成 Point4D chaining 或 2D memory | 第二 |
| C：有限历史约束 | 后端、边缘化/压缩、长序列系统 | 仅是关键帧策略或工程加速 | 取决于团队后端经验 |

这里的优先级是结合当前算力和已有 St4RTrack/V-DPM 积累的判断，不是对最终投稿成功率的预测。

## 9. 数据集与公平评估

### 9.1 推荐的数据组合

| 数据集 | 合适的角色 | 长度与协议要点 |
|---|---|---|
| **TAPVid-3D** | 真实世界 3D tracking 主指标 | ADT 300 帧、PStudio 150 帧、DriveTrack 最长 300 帧；标准轨迹在逐帧相机坐标，主协议全视频一次 global median scaling |
| **PointOdyssey 原始长视频** | 千帧级持续状态与点身份主测试 | 官方当前描述平均约 2,000 帧；v1.2 为 131 train / 15 val / 13 test；实际长度以 manifest 为准 |
| **Dynamic Replica 完整测试** | 第二个长动态几何/轨迹数据源 | train/val 300 帧；test 为 20 段、每段约 900 帧；不要沿用后续工作只测前 150 帧的结果 |
| **WorldTrack** | St4RTrack/Flow4R 的直接可比实验 | 四源各 50 条、64 帧；世界坐标，但不足支撑千帧主张 |
| **LSFOdyssey** | 与 SceneTracker 等的短序列 bridge | 测试 90 条、每条 40 帧/256 queries；不是 PointOdyssey 长序列替代品 |
| **Syn4D** | 密集动态几何、3D correspondence 补充 | 原始约 300 帧；论文 dense tracking 实际测 24-frame clips；challenge 为 192 帧输入、32 个评分时刻，协议不同 |
| **TAPVid-MV 的单目设置** | 最新真实域/世界一致性补充 | 2026-09 新预印本支持 monocular 3D/4D；不能把多相机辅助输入混进主结果 |
| **TAP-Vid DAVIS** | 2D tracking 与 occlusion sanity check | 固定 first/strided query 协议；不提供 4D 完整证据 |
| **TUM-dynamic / Bonn / Sintel** | 相机、深度和失效机制诊断 | 不可代替动态任意物质点的长期 GT tracking |

来源：[TAPVid-3D 原论文](https://arxiv.org/html/2407.05921v2) / [官方数据说明](https://github.com/google-deepmind/tapnet/blob/main/tapnet/tapvid3d/README.md)；[PointOdyssey](https://pointodyssey.com/) / [v1.2 发布说明](https://github.com/y-zheng18/point_odyssey)；[Dynamic Replica 原论文](https://www.robots.ox.ac.uk/~vgg/publications/2023/Karaev23/karaev23.pdf) / [代码与数据](https://github.com/facebookresearch/dynamic_stereo)；[WorldTrack](https://arxiv.org/html/2504.13152v1)；[LSFOdyssey / SceneTracker](https://arxiv.org/html/2403.19924v4)；[Syn4D](https://arxiv.org/html/2605.05207v1) / [challenge](https://github.com/jzr99/syn4d-kaggle-challenge-participants/blob/main/README.md)；[TAPVid-MV](https://arxiv.org/html/2609.01899v1)；[TAP-Vid](https://github.com/google-deepmind/tapnet/blob/main/tapnet/tapvid/README.md)；[TUM](https://cvg.cit.tum.de/data/datasets/rgbd-dataset) / [Bonn](https://www.ipb.uni-bonn.de/data/rgbd-dynamic-dataset/) / [Sintel depth](https://sintel.is.tue.mpg.de/depth)。

首轮建议先拿 PointOdyssey val/test、TAPVid-3D debug/minival 和 Dynamic Replica 少量完整序列。Dynamic Replica 全注释解压数据较大，官方 test 约 328 GB；不要在验证方案前先准备所有训练数据。[Dynamic Replica 存储要求](https://github.com/facebookresearch/dynamic_stereo)

### 9.2 两层指标必须同时存在

**第一层：遵循官方指标，保持可比性。** TAPVid-3D 报 AJ3D、APD3D、OA，固定 evaluator 和 query protocol。其标准阈值随 GT 深度与焦距变化，主表全视频一次 median rescaling；WorldTrack 的 APD 阈值与坐标定义不同，二者数值不能直接并表排名。[TAPVid-3D §3.5](https://arxiv.org/html/2407.05921v2)、[WorldTrack 协议](https://arxiv.org/html/2504.13152v1)

**第二层：专门验证我们声称的能力。** 共同 world frame 下的动态轨迹误差、camera ATE/RPE、尺度随时间变化、遮挡/出视野后恢复，以及误差随跟踪时长的增长。除全序列一次对齐，再给“初始化前缀只拟合一次尺度，后续固定”的严格诊断；禁止每窗重新拟合 GT 变换再宣称长期稳定。这是建议的补充协议。

这要求先把预测与 GT 锚定到第一帧相机坐标，固定旋转/平移规范。若模型输出任意世界坐标，应仅用初始化前缀的几何或相机拟合一次 SE(3)/Sim(3) 后冻结，不能用完整 GT tracks 拟合。严格因果主结果只评分 query 到达之后的 t≥t_query；若官方协议还评价 query 前的历史轨迹，须另列回溯结果，并注明协议差别。

官方 evaluator 用全序列 GT 做尺度对齐，**不等于模型偷看未来**；它是评分操作，但可能掩盖部分尺度问题。模型利用未来图像做深度、相机或伪标签，才属于推理输入的未来访问。两者要区分。

### 9.3 最小公平性清单

- 主表仅输入 RGB；已知 K、GT depth、GT camera、oracle correspondences 单独列诊断行。
- 不能借助 GT camera 把模型逐帧预测“扶正”，再评价其世界坐标稳定性。
- 同 backbone、分辨率、活动点数、历史窗口、优化步数；附加 equal-compute 大窗口和简单拼接对照。
- 预处理、分割、depth/pose、tracker、在线更新全部纳入端到端计时。
- 记录 lookahead、首帧等待、P50/P95 latency、吞吐、峰值 GPU/CPU 工作记忆。
- 区分可见/不可见、静态/动态、首帧 query/新生 query；新加入的点不应稀释老轨迹失效。
- 每个测试视频是否重置 TTA 参数必须明示；超参数只在独立验证集选择。
- 用真实长序列，不能把短片反复播放作为主要证据；循环播放只能作特定压力测试。
- 对追加未来帧进行 prefix-invariance 检查：严格因果系统已经发布的过去输出不得改变。
- 保留失败序列与逐序列统计；最好以序列为单位做 bootstrap，避免海量像素造成虚假的显著性。

有界工作记忆不要求删掉供 evaluator 使用的历史输出日志；但如果算法之后重新读取这些日志，它们就属于算法记忆，必须计入。

## 10. 两周 pilot：先判断能不能形成论文

这是一份建议执行方案，没有启动训练、下载大型数据或创建定时任务。

| 时间 | 工作 | 必须拿到的结果 |
|---|---|---|
| 第 1–3 天 | 固定数据/checkpoint/evaluator；跑 St4RTrack 新版、V-DPM 短窗、2D track + geometry lifting；审坐标与因果性 | 小样本可复现结果、H20D profile、明确失败类别 |
| 第 4–7 天 | 比较 naive chaining、robust overlap alignment、较大窗口；做 GT camera/depth 诊断 | 确定主要瓶颈是几何、相机还是 correspondence/identity |
| 第 8–11 天 | 只加入一个核心机制；配 equal-compute 消融 | 机制针对预期失败起作用，而非所有模块一起涨点 |
| 第 12–14 天 | 冻结参数；跑保留真实域与完整长视频；检查长程尾部 | 动态/静态分解、随时间曲线、资源曲线、失败案例 |

**建议事先设定继续门槛。** 例如，在两个独立数据源上，动态 world-track 误差相对下降至少 10%，长时段收益明显，AJ3D 无明显退化，并且差异得到逐序列分析支持；或者在同等质量下显著降低内存/端到端延迟。10% 是项目内部止损阈值，不是文献结论、会议录用标准或预期实验结果。

**应停止或转向的情形：**

- 只在 GT camera、未来帧或每窗重新对齐后有效；
- 只赢 40/64 帧，不赢完整长序列；
- 改善被相同计算量的大窗口或简单重叠拼接吃掉；
- 背景几何改善，动态点反而更差；
- 所谓恒定内存依赖越来越大的 CPU 地图或历史 replay；
- 测试时优化成本显著增长，但改进很小且不稳定。

## 11. 推荐精读顺序与阅读问题

**第一轮，决定问题是否成立：**

1. **St4RTrack + 当前官方代码**：看双点图定义、TTA 梯度、WorldTrack、动态 confidence 修正。
2. **V-DPM**：看时间/视角不变性、decoder 查询成本、长序列滑窗与训练预算。
3. **Flow4R**：看相机/运动分解、anchor 尺度、64 帧评测范围。
4. **TAPVid-3D + TAPVid-MV 附录 B/C**：看坐标、尺度、窗口对齐、轨迹交接。
5. **SpaTrackerV2 / TAPIP3D**：看几何输入改变时 tracking 的敏感性，检查完整 RGB pipeline。

**第二轮，决定机制：**

6. **TTT3R → FILT3R → RayMap3R**：梳理 gate、uncertainty、dynamic suppression 已经做到哪里。
7. **Test3R → Online3R**：看自监督一致性目标如何构造、是否可能自我强化错误。
8. **TAPNext++ / Track-On2**：看长期失效、重新检测和记忆扩展，避免只用旧 tracker。
9. **DynOMo → Shape of Motion → MotionScale**：看持久表示、运动基、历史优化和身份问题。
10. **D4RT / Point4Cast / OmniX / Point4D**：核查最新统一表示与长程链式查询的重合范围。

每篇只回答六个问题，就比单纯记网络模块更有价值：

- 输入到底有哪些，哪些由其他模型或 GT 提供？
- 输出坐标系是什么；相机运动与物体运动在哪里分开？
- 同一物质点如何跨时间、遮挡和窗口保持身份？
- 单步计算、活动记忆和地图存储如何随时间增长？
- 成功结果用了多长片段、什么对齐和哪些未来信息？
- 在冻结它的权重后，我们增加的机制究竟改变哪个失败原因？

## 12. 证据边界与当前结论的使用方式

第 1–12 节是面向选题决策的定向调研，不是全领域穷尽书目，重点覆盖 2023–2026 年直接相关方法。9 月 17 日新增的第 13–18 节扩展到多视角、人体先验、生成式补全和下游任务；仍不等同于整个世界模型或机器人领域的系统综述。

- 核心方法优先阅读原论文的方法、实验和补充材料；TAPIR/BootsTAP 等成熟背景方法主要作谱系定位，阅读深度不与核心方法等同。
- **Point4Cast** 完整 PDF 抓取受限，使用正式条目、官方说明和原 PDF 可检索段落；精确代码状态、完整训练/评测细节未全部确认。
- **Point4D** 的证据已升级为署名全文、项目与推理实现，详见第 14.1 节；预印本与会议录用仍严格区分。
- 代码“已公开”表示查看到官方实现/下载入口，不表示本机运行成功；权重的实际完整性、evaluator 默认配置和端到端因果性仍需运行核查。
- 论文数据与代码版本可能不同，尤其 St4RTrack 与 SpaTrackerV2，复现时应记录 commit、checkpoint、数据 split 和评测脚本。
- 所有算力数字是作者在其配置下的报告。H20D 显存规格、互联、可用总训练时间未实测或指定，本文没有推断具体型号容量，也没有进行跨 GPU 耗时换算。
- Markdown 已进行结构、链接格式和内容一致性检查；未生成 PDF/DOCX，也未执行浏览器排版检查。

**用于下一次讨论的最具体决策是：先围绕 St4RTrack/V-DPM 做受控的长程误差分解，检验方向 A；若主要瓶颈在 GT 几何下仍然存在的身份交换，则转向方向 B。** 在实验前，不能声称找到了“无人做过”的组合；真正值得投入的是能够清楚解释、稳定重现并被一个小机制修复的失败。

---

## 13. 2026-09-17 增补：如何阅读这一轮更新

本轮按三条线检索：**动态几何/联合重建与跟踪；2D/3D point tracking；把几何或轨迹用于其他任务**。来源优先为 arXiv 署名全文、CVF/OpenReview/会议或期刊记录、作者项目及代码；不以二手论文列表直接确定录用或开源状态。

时间分三类，避免把“这次发现”误称为“这周才发表”：

| 类别 | 本轮代表 | 应如何理解 |
|---|---|---|
| 9 月 8 日附近及其后新公开 | Point4D（9/8 UTC，国内已是 9/9）、S3-Tracker（9/13）、Track, Articulate, Act（9/16） | 属于需要立刻检查的近期变化；各自证据和任务级别不同 |
| 2026 年已公开、本轮补入 | 4RC、Complet4R、CoWTracker、AnthroTAP、TrajVG、TrackCraft3R、UniQuery4R、SceneScribe-1M 等 | 是原调研的补漏，不是过去一周全部新发 |
| 2025 首发、2026 正式发表/修订，或发布状态变化 | MoVieS、Any4D、PAGE-4D、HistRISE、Edit-by-Track；VGGT-Ω 的 9 月复现更新 | 分别记录首发、会议和发布事件，不按会议年份伪造首发时间 |

以下“首发”默认指 arXiv v1 的 **UTC 提交日期**。有的论文在编号所属月份之前提交；只核到正式论文的，直接列会议年份，不猜 arXiv 日期。“作者标注某会议”与“已核到正式出版记录”分别表述；Findings、短论文和 benchmark challenge 保留各自类别。代码状态为 **2026-09-17 的页面核查**，不是已完成复现。

**本轮最需要改变原研究计划的四点：**

1. **streaming 联合查询已有 S-4RC，低预算联合补全已有 Complet4R。** 应把问题收紧到受限记忆、完整窗口遮挡、新查询加入与跨窗误差传播，见第 14.1 节。
2. **几何帮助 tracking 不是单一套路。** TrajVG 做训练期双向耦合，TrackCraft3R 迁移视频生成先验，CoWTracker 在 VGGT 特征上用 warping 替代 correlation；三者都要进入方法重合检查，见第 14–15 节。
3. **下游价值应落实到具体接口。** 轨迹可以是机器人目标、历史记忆、关节拟合证据、视频控制条件，或仅训练监督。不能把这些都当作同一种“4D world model”，见第 16 节。
4. **评测与数据版本已经会改变结论。** VGGT-Ω 有新的 benchmark checkpoint；SceneScribe-1M 的几何/轨迹来自教师模型；ITTO、SynthVerse 和 VOTSp 提供不同维度的评测补充，见第 14.3、17 节。

## 14. 新增及更新：动态 4D 重建、联合 tracking 与几何骨干

### 14.1 与我们主任务最直接相关的方法

| 工作、首发与发表状态 | 核心机制和实际输入/输出 | 长序列边界、资源与复现状态 |
|---|---|---|
| **4RC: 4D Reconstruction via Conditional Querying Anytime and Anywhere**；Luo 等；2026-02-10，ICML 2026 | 单目 RGB、未知 pose；视频编码后，以源时间/目标时间条件查询几何与运动。DA3 初始化，几何与相对运动分解 | 标准版整段编码，16 A100、50 epochs。推理、权重及 evaluation 脚本公开，training 尚未发布。[全文](https://arxiv.org/html/2602.10094v1)、[官方代码](https://github.com/Luo-Yihang/4RC) |
| **S-4RC**；4RC 附录 B.1 的流式变体，非另一篇新论文 | STream3R 因果骨干，逐帧更新；支持过去→当前及当前→过去的 motion query | 8 A100、20 epochs 微调，但保存**全部历史帧 latent**，未证明总工作记忆有界；未确认单独公开的 S-4RC 权重/执行入口。不能用标准 4RC 的开源状态替代流式变体状态。[附录](https://arxiv.org/html/2602.10094v1) |
| **Complet4R: Geometric Complete 4D Reconstruction**；Wang 等；2026-03-28，CVPR 2026 | 单目未知 pose；以 aggregation tokens/head 将不同源帧的几何汇聚到目标时间，补出该时刻不可见但其他时刻见过的部分，并支持 3D tracking | VGGT 初始化，冻结 camera/depth heads；8 A100、23 小时、10 epochs。使用过去和未来帧，全局注意力限制长视频；作者实现尚未确认公开。[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Wang_Complet4R_Geometric_Complete_4D_Reconstruction_CVPR_2026_paper.html)、[全文](https://arxiv.org/html/2603.27300v1) |
| **Point4D: Long-range 4D Motion Reconstruction**；Jeon 等；2026-09-08，预印本 | DA3 几何骨干；3D query 配可见帧外观描述子，跨块直接传递 3D endpoint；重叠几何用于 Sim(3) 对齐 | 48 帧窗口、8 帧重叠，在约 150–200 帧协议检验；8 H100、150 epochs。推理代码及长视频接口公开，README 有权重入口但本次未验证下载；训练代码未确认。[论文](https://arxiv.org/html/2609.09145v1)、[项目](https://point-4d.github.io/)、[代码](https://github.com/point-4d/Point4D) |
| **UniQuery4R: Unified 4D Scene Reconstruction from a Single Query**；Chen 等；2026-08-18，预印本 | 单目未知 pose；连续源像素/源时间/目标时间 query 同时解码 2D 对应、3D 点、flow 和源深度；输出 view-0 坐标的相对尺度几何 | 整段编码；16 H20、150k steps，训练 4–12 帧，含内部骨干/数据；公开骨干对照用 8 A800。跨窗融合留待未来；项目仍 Code soon。[全文](https://arxiv.org/html/2608.17283v1)、[项目](https://kosmoresearch.github.io/UniQuery4R/) |
| **Any4D: Unified Feed-Forward Metric 4D Reconstruction**；Karhade 等；2025-12-11，CVPR 2026 | RGB 可以独立输入，也接受 depth、pose/IMU、Radar 等可选条件；联合估计 metric 几何、camera 和世界 scene flow | MapAnything 初始化；8 H100、100 epochs。批量多帧输入，未见因果机制；flow 从首帧出发，关注点须在首帧出现。推理/权重公开，完整训练代码仍待发布。[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Karhade_Any4D_Unified_Feed-Forward_Metric_4D_Reconstruction_CVPR_2026_paper.html)、[全文](https://arxiv.org/html/2512.10935v1)、[代码](https://github.com/Any-4D/Any4D) |
| **TrajVG: 3D Trajectory-Coupled Visual Geometry Learning**；Miao 等；2026-02-04，作者主页标 SIGGRAPH 2026 | 相机系 3D trajectories 与 pointmaps/pose 双向耦合；利用 stop-gradient、一致性以及静态轨迹锚点避免相机与物体运动互相污染；可利用野外视频伪 2D tracks | 是训练期耦合，不是即插即用的测试时修正；未证明因果长流式。项目下载区仍 Code Coming Soon；未核到完整训练开销或 ACM 正式出版条目。[全文](https://arxiv.org/html/2602.04439v1)、[项目](https://xingy038.github.io/TrajVG/)、[作者发表列表](https://weiguangzhao.github.io/) |

**Point4D 必须精读的局限：**它跨块传递点坐标及其 patch descriptor，但未保留可检索的历史场景表示或特征库；若一个点在整个当前窗口内都不可见，当前块缺乏新的视觉证据。深度、跨窗坐标对齐及 endpoint 本身的误差也会累积。这使“经历完整窗口不可见后，重新出现时的身份恢复”和“几何漂移与身份错误如何分离”成为比再做一次 endpoint chaining 更值得验证的问题。这是依据其方法边界提出的研究推断，并不是已经证明的提升空间。[Point4D 方法与局限](https://arxiv.org/html/2609.09145v1)

**S-4RC 与 Complet4R 对预算判断的意义：**前者已展示 8 卡微调的流式联合模型，后者展示一天级的几何 completion 适配。它们说明 8 张 H20D 可以考虑有限微调，但 A100/H100 的原报耗时不能直接按卡数换算为 H20D 耗时；代码、输入长度及数据准备仍决定复现周期。

### 14.2 动态渲染、语义重建与生成式补全

这些工作很值得读，但应与“未知 pose、单目 RGB、持久点身份”的主实验分组。

| 工作与发表信息 | 4D 表示及 tracking 的作用 | 输入、成本及复现边界 |
|---|---|---|
| **MoVieS: Motion-Aware 4D Dynamic View Synthesis in One Second**；Lin 等；2025-07-14，2026-02-22 修订，CVPR 2026 | Pixel-aligned Gaussians 配显式运动，统一 NVS、几何与 3D tracking | 模型输入需要 **pose/K**；野外 demo 用 MegaSaM 补 pose。VGGT 初始化，32 H20 约 5 天，最多 13 帧训练；短片“一秒”不是长流式速度。训练/推理实现及权重入口已公开，tracking 使用说明仍有 TODO。[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Lin_MoVieS_Motion-Aware_4D_Dynamic_View_Synthesis_in_One_Second_CVPR_2026_paper.html)、[全文](https://arxiv.org/html/2507.10065v2)、[代码](https://github.com/chenguolin/MoVieS) |
| **SLARM: Streaming and Language-Aligned Reconstruction Model for Dynamic Scenes**；Qiu 等；2026-03-24，CVPR 2026，作者标 Highlight | 流式窗口注意力预测动态 Gaussians、高阶运动和语言对齐特征；可做动态 NVS、语言查询/分割 | **已知相机内外参**，主场景包括多相机驾驶数据；当前状态因果，但有回溯 warping 修正近期历史，需区分发布时刻。64 Ascend 910B、4 天；训练/eval 实现可见，权重完整性未核。[正式论文](https://openaccess.thecvf.com/content/CVPR2026/papers/Qiu_SLARM_Streaming_and_Language-Aligned_Reconstruction_Model_for_Dynamic_Scenes_CVPR_2026_paper.pdf)、[全文](https://arxiv.org/html/2603.22893v1)、[代码](https://github.com/kevinchiu19/SLARM) |
| **MOSAIC-GS: Monocular Scene Reconstruction via Advanced Initialization for Complex Dynamic Environments**；Morkva 等；2026-01-08，CVPR 2026 | 以 motion segmentation、点轨迹和局部刚性改进动态 GS 初始化，用 PolyFourier 轨迹表示复杂运动 | 重建模块消耗 pose/depth 先验；逐场景离线优化。项目报告 <11 分钟重建训练、180 FPS 渲染，二者均不代表全部先验的端到端耗时。项目有代码入口，本轮未运行核验。[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Morkva_MOSAIC-GS_Monocular_Scene_Reconstruction_via_Advanced_Initialization_for_Complex_Dynamic_CVPR_2026_paper.html)、[全文](https://arxiv.org/html/2601.05368v1)、[项目](https://rffr.leggedrobotics.com/works/mosaic/) |
| **PASTEL: Panoramic Alignment for Monocular 4D Scene Reconstruction**；Yang 等；2026-09-05，官方仓库标 ECCV 2026 | 规划扩展相机路径，用视频生成补不可见区域，再选择性蒸馏到 MoSca 4DGS | 消耗预估几何/pose，离线生成与场景优化；作者约 5 分钟预处理、10 分钟扩展生成、1.5 小时重建。仓库只有展示/论文等文件，未见算法实现；不能把生成补全当观测到的真实轨迹。[全文](https://arxiv.org/html/2609.06099v1)、[官方仓库](https://github.com/LogosRoboticsGroup/PASTEL) |
| **FreeOrbit4D: Training-Free Arbitrary Camera Redirection for Monocular Videos via Foreground-Complete 4D Reconstruction**；Cao 等；2026-01-26，5/19 修订，SIGGRAPH Conference Papers 2026 | PAGE-4D/VGGT 估计几何，SAM2 分割，SV4D2.0 补前景多视角，Wan2.2-VACE 生成目标视角视频；不另训练专用模型 | 源 RGB 无需用户给 pose，另需前景提示/目标相机轨迹；双向平滑及扩散推理，非 causal。45 帧、832×480、单 A40 约 50 分钟；真实代码已发布，推荐 ≥46 GB 显存/约 130 GB 磁盘；单主体、重遮挡受限。[元数据与正式 DOI](https://arxiv.org/abs/2601.18993)、[v2 全文](https://arxiv.org/html/2601.18993v2)、[代码](https://github.com/VVeiCao/FreeOrbit4D) |
| **MuBe4D: A Mutual Benefit Framework for Generalizable Motion Segmentation and Geometry-First 4D Reconstruction**；Zhang 等；Information Fusion 133，2026 年 9 月卷期，104252 | 摘要称以 3D priors 改善泛化 motion segmentation，再用运动分割改善几何优先的 4D reconstruction | **本轮仅核摘要与出版信息，未获取全文。** 首次 online 日期、输入 pose 假设、在线性、训练成本及代码均未确认；9 月卷期不等于 9 月首发，暂列待精读。[期刊原页](https://www.sciencedirect.com/science/article/abs/pii/S1566253526001314) |

FreeOrbit4D 早期标题为 **Geometry-Complete**，正式更新为 **Foreground-Complete**，应按所引用版本填写。其 training-free 指不训练新模型，仍包含几何对齐、双向时间处理和昂贵扩散采样；这和低延迟在线推理是两个维度。

### 14.3 骨干与代码版本：不能漏掉的状态变化

**VGGT-Ω（Wang 等，2026-05-14 首发；官方标 CVPR 2026 Oral）**是几何/相机骨干候选，不等同于持续身份 tracker。9 月的新发布对实验有直接影响：

- 作者复核训练数据时发现**可能的数据污染风险**，但**未能确定原 checkpoint 是否实际受影响**；随后用重新核查 benchmark overlap 的数据重训。
- **9/8** 发布训练代码及重训权重，未来 benchmark 对比应使用 **VGGT-Omega-1B-416-Reproduction**；**9/9** 发布数据收集/清洗工具；**9/10** 发布 8 个数据集的训练 sequence lists。
- 原 512 模型仍用于 in-the-wild 应用推荐；不能将它和 reproduction benchmark 模型混成一条结果。重训为 256 GPU，原论文为 128 GPU，不是我们应从头复刻的规模。

以上为作者说明，不能改写成“已证实测试集泄漏”。[论文](https://arxiv.org/abs/2605.15195)、[官方仓库](https://github.com/facebookresearch/vggt-omega)、[复现说明](https://github.com/facebookresearch/vggt-omega/blob/main/reproduction.md)

**PAGE-4D（Zhou 等，2025-10-20 首发，2026-08-04 v8；ICLR 2026）**通过不同的动态 mask 使用方式分离 pose 与 geometry 的需要，只微调中间 10 层、约 30% 参数。它是低成本动态几何适配的重要对照，但论文未纳入 point tracking，仍是全局多帧 attention；训练含内部数据。官方训练/eval/权重公开，推荐的 checkpoint_nomask 在推理期不使用 mask，不能误写成推理必须配动态分割。[OpenReview](https://openreview.net/pdf?id=Nfmzp5PBzr)、[v8 全文](https://arxiv.org/html/2510.17568v8)、[代码](https://github.com/kaichen-z/PAGE4D)

原文 **Flow4R** 的官方项目现标 **ECCV 2026**；本轮仍未确认作者发布算法代码/权重。**TAPNext++** 正式类别为 **CVPR 2026 Findings**，已在第 5.1 节修正。这些是发表或发布状态核查，不计作新方法。[Flow4R 项目](https://shenhanqian.github.io/flow4r)、[TAPNext++ 正式条目](https://openaccess.thecvf.com/content/CVPR2026F/html/Jung_TAPNext_Whats_Next_for_Tracking_Any_Point_TAP_CVPRF_2026_paper.html)

## 15. 新增及更新：2D / 3D Point Tracking

### 15.1 直接相关的 RGB tracking 与低成本适配

| 工作与时间/发表信息 | 机制、输出与关键贡献 | 在线性、训练预算和可复现性 |
|---|---|---|
| **CoWTracker: Tracking by Warping instead of Correlation**；Lai 等；2026-02-04，CVPR 2026 | VGGT+DPT 高分辨率特征，以 warping 替代 correlation cost volume，再作时空更新；输出稠密 2D tracks、visibility 和 confidence | 全片/窗口处理，骨干时间复杂度随长度二次增长；提供 CoWTrackerWindowed。Kubric、50k steps、最多 16 帧训练；GPU/总时长未核。推理和权重公开，完整训练流程未确认；600 帧定性展示不等于无界身份稳定。[全文](https://arxiv.org/html/2602.04877v1)、[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Lai_CoWTracker_Tracking_by_Warping_instead_of_Correlation_CVPR_2026_paper.html)、[代码](https://github.com/facebookresearch/cowtracker) |
| **AnthroTAP: Learning Point Tracking with Real-World Motion**；Kim 等；2025-07-08，2026-03-30 v3，CVPR 2026 | 人体 SMPL 拟合与投影、ray casting、flow 过滤产生约 1.4k 真实视频监督，微调 LocoTrack/TAPNext；任务是 RGB→2D tracking | 4 A6000、1 天、50k steps，为 tracker 训练而非全部标注制作成本；在线性继承底座。训练/eval、数据及两类权重入口公开。[论文日期](https://arxiv.org/abs/2507.06233)、[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Kim_AnthroTAP_Learning_Point_Tracking_with_Real-World_Motion_CVPR_2026_paper.html)、[代码](https://github.com/cvlab-kaist/AnthroTAP) |
| **M2P: Improving Visual Foundation Models with Mask-to-Point Weakly-Supervised Learning for Dense Point Tracking**；Wu 等；2026-03-18，预印本 | 用 VOS masks、局部 Procrustes 和边界/前景约束适配 DINOv2/v3；另做 DINO-Tracker 式逐视频 TTO，输出 2D tracks | 预训练约 2 RTX4090、1 天；TTO 约 0.5M 参数、2500 iterations、0.7 小时/视频。文中 online optimization 不代表因果流式；代码仍称 upon acceptance。不同指标有升有降，不能写成全面超越 DINO-Tracker。[全文](https://arxiv.org/html/2603.17813v1) |
| **Fast Spatial Tracking with Visual Geometry Transformer**；Huang 等；CVPR 2026，首次公开日期未核 | RGB 不额外输入 depth/pose，几何 Transformer 配全局/逐帧双分支 query decoder，输出 **相机系、尺度不定** 3D tracks、2D tracks 与可见性 | 全局分支读取整片，作者将 streaming 列为未来工作。16×80GB GPU、约 3 天、50k steps；150 帧/50 tracks 下约 28ms/frame 是整片处理折算的平均每帧耗时，不代表因果在线发布延迟。代码/权重未确认。[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Huang_Fast_Spatial_Tracking_with_Visual_Geometry_Transformer_CVPR_2026_paper.html)、[正式全文](https://openaccess.thecvf.com/content/CVPR2026/papers/Huang_Fast_Spatial_Tracking_with_Visual_Geometry_Transformer_CVPR_2026_paper.pdf) |
| **PairFormer: Matching Every Pair to Track Every Point**；Wu 等；CVPR 2026，首次公开日期未核 | CorrBank 构造帧对 motion tokens，broadcast mixer 传递全局轨迹信息；输出任意 source-target 的稠密 **2D** displacement、visibility、confidence | 离线，长视频 query-centric 窗口 L=16；实验最多 600 帧。8 H100、50k iterations，π-R10K+Kubric；正式论文承诺代码/数据，实际发布未确认。[完整正式标题与论文](https://openaccess.thecvf.com/content/CVPR2026/papers/Wu_Matching_Every_Pair_to_Track_Every_Point_PairFormer_for_All-Pairs_CVPR_2026_paper.pdf) |
| **Generative Point Tracking and Forecasting（Gen-Points）**；Lu、Cao、Feng、Owens；CVPR 2026，首次公开日期未核 | DINOv3-S 配 point-space flow-matching DiT，使用 causal attention、点间交互和 diffusion forcing；去掉未来视觉条件可预测未来 2D 轨迹 | 窗口自回归生成，可因果运行但需另核每帧发布延迟；训练 200k steps，GPU/总时长未核。官方仓库仍为 README，code/weights coming soon。[正式论文](https://openaccess.thecvf.com/content/CVPR2026/papers/Lu_Generative_Point_Tracking_and_Forecasting_CVPR_2026_paper.pdf)、[项目](https://gen-points.github.io/)、[仓库](https://github.com/Charles-Lu/Generative-Point-Tracking-and-Forecasting) |
| **TrackCraft3R: Repurposing Video Diffusion Transformers for Dense 3D Tracking**；Nam 等；2026-05-12，预印本 | 将 Wan2.1-T2V-1.3B 改成单步回归，以 RGB 与外部 depth/K/pose 构造的 pointmaps 预测首帧全部像素的 **以首帧相机为参考的世界系 3D tracks+visibility** | 完整 3D attention，长视频按已知总长度 stride 分组并固定首帧锚点，非因果；主评 84/24 帧，长度实验到 120 帧。LoRA rank1024、后期解冻 VAE；8 H200、5 天。训练/eval/推理/权重均公开。[论文](https://arxiv.org/abs/2605.12587)、[代码](https://github.com/cvlab-kaist/TrackCraft3r)、[权重](https://huggingface.co/trackcraft3r/checkpoint) |

**这些方法分别挤占什么研究叙事？**

- CoWTracker / Fast Spatial Tracker：几何基础模型特征加高效 tracking decoder 已有直接先例。
- PairFormer：任意源时刻、全像素轨迹场及跨源信息交换已有方法，不能单靠换 query 定义构成贡献。
- AnthroTAP / M2P：小成本且更可靠的监督、弱监督适配和逐视频 TTO 已有实际结果；值得复用，也要求更具体的差异。
- TrackCraft3R：视频生成先验迁移到 3D tracking 已被明确提出；其离线锚点、外部几何依赖和高 rank 适配留下更具体的比较维度。
- Gen-Points：遮挡期间的运动不确定性和 forecasting 可以用生成式轨迹模型表达，但轨迹先验与重新观测后的身份确认仍是不同问题。

以上是本笔记的研究判断；没有直接运行这些模型，也不据不同论文表格给它们排统一名次。

**命名去重：Gen-Points ≠ GenPT。** 后者是 Tesfaldet 等的 *Generative Point Tracking with Flow Matching*，2025-10-23 首发；本轮未核其 2026 录用状态。不要混淆作者、代码或实验。[GenPT 对应论文](https://arxiv.org/abs/2510.20951)

### 15.2 多视角、事件相机与专门领域

| 工作与发表信息 | 与 point tracking 的关系 | 对本项目的边界 |
|---|---|---|
| **MV-TAP: Tracking Any Point in Multi-View Videos**；Koo 等；2025-12-01，CVPR 2026 | CoTracker3 加 Plücker camera encoding 和 view attention；输入同步多 RGB、K/pose、跨视角 query，输出各视角 **2D tracks**；另研究三角化 refinement | 不需 depth，但并非单目未知 pose，也不直接输出世界 3D。4 A6000、50k steps；时间 attention/窗口处理。训练/eval、权重与采样脚本公开。[全文](https://arxiv.org/html/2512.02006v1)、[项目](https://cvlab-kaist.github.io/MV-TAP/)、[代码](https://github.com/cvlab-kaist/MV-TAP) |
| **TTAPFormer / TAPFormer: Robust Arbitrary Point Tracking via Transient Asynchronous Fusion of Frames and Events**；Liu 等；2026-03-05，3/8 v2，CVPR 2026 | RGB+events→2D；瞬态特征更新与局部可靠度融合，针对高速/模糊 | CVF 与 arXiv 标题拼写不同，是同一篇；时间窗口 W=16，异步特征更新不证明整个 tracker 逐帧因果。4 RTX4090；推理、数据及权重公开，完整训练入口未核。[论文](https://arxiv.org/abs/2603.04989)、[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Liu_TTAPFormer_Robust_Arbitrary_Point_Tracking_via_Transient_Asynchronous_Fusion_of_CVPR_2026_paper.html)、[代码](https://github.com/ljx1002/TAPFormer) |
| **MER-Tracker: Towards High-Speed 3D Point Tracking via Multi-View Event-RGB Hybrid Cameras**；Chang 等；CVPR 2026，首发日期未核 | 4 RGB+2 event views，另使用 depth/K/pose，lift 到统一 3D；融合插值特征并 LoRA 适配 MVTracker | 150fps 指轨迹时间采样率，不能当实测系统运行速度；插值使用后一 RGB 帧。2 A6000、40 小时、20k steps；实现/权重未确认。[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Chang_MER-Tracker_Towards_High-Speed_3D_Point_Tracking_via_Multi-View_Event-RGB_Hybrid_CVPR_2026_paper.html)、[全文](https://openaccess.thecvf.com/content/CVPR2026/papers/Chang_MER-Tracker_Towards_High-Speed_3D_Point_Tracking_via_Multi-View_Event-RGB_Hybrid_CVPR_2026_paper.pdf) |
| **S3-Tracker: Self-Supervised Surgical Tissue Tracking With Contrastive Random Walks**；Zhang 等；**2026-09-13**，Hamlyn Symposium 2026 两页短文 | 内镜 RGB→2D；回文随机游走自监督、全局匹配、可见性/前后向检查与最后可见帧回退，原文描述 streaming | 单 A100 40GB，报告约 301ms 延迟；STIR 精度低于 CoTracker3；代码未确认。是近期无标注领域适配线索，不能提升为通用 4D 强基线。[元数据](https://arxiv.org/abs/2609.14313)、[全文](https://arxiv.org/html/2609.14313v1) |

### 15.3 对 8 张 H20D 最有用的训练成本参照

| 路线 | 新增文献中的原报成本 | 实际决策 |
|---|---|---|
| 数据质量驱动的 2D 微调 | AnthroTAP：4 A6000×约 1 天 | 如果标签机制与目标失败对应，少量高质量运动监督值得优先试；数据制作成本另算 |
| 弱监督特征适配 | M2P：2 RTX4090×约 1 天；TTO 0.7 小时/视频 | 训练容易纳入预算，逐视频优化可能成为总评测瓶颈 |
| 联合几何 completion 微调 | Complet4R：8 A100×23 小时 | 提供一天级联合适配先例，但代码发布和数据配齐是前提 |
| 生成骨干迁移 | TrackCraft3R：8 H200×5 天 | 能复用权重；从头照做不是“便宜 LoRA”，应缩小适配范围 |
| 多模态小数据适配 | MV-TAP、MER-Tracker | 可借鉴方法与预算，不能直接把多相机/事件输入的收益移植到 RGB-only 结论 |

这些是跨论文的资源参照，**不是等价 GPU-hours 排名，更不是对 H20D 的速度承诺**。

## 16. 利用 4D 重建 / Tracking 做其他任务

先区分表示在系统中的角色：**推理时控制/记忆接口、几何优化证据、生成条件、训练期辅助监督**。前三类都可能依赖可靠对应，但消费完整离线轨迹与在线维护持久身份是不同要求；训练期辅助监督则可能在部署时完全移除。

### 16.1 机器人操作、动作模型与历史记忆

| 工作与时间/状态 | 轨迹或几何在系统中做什么 | 可借鉴之处、成本与边界 |
|---|---|---|
| **Dex4D: Task-Agnostic Point Track Policy for Sim-to-Real Dexterous Manipulation**；Kuang 等；2026-02-17，预印本 | 生成视频经深度/CoTracker 得到目标 3D tracks；当前 RGB-D 提供对应点，paired-point policy 闭环执行 | 轨迹是目标及观测接口。单 A6000：仿真 teacher 2–3 天，student 约 20 小时，不含生成/预处理；仿真训练、权重、视觉代码公开。依赖 RGB-D 和机器人标定，零样本部署不等于无训练。[全文](https://arxiv.org/html/2602.15828v1)、[仿真代码](https://github.com/Dex4D/Dex4D-Simulation)、[视觉代码](https://github.com/Dex4D/Dex4D-Vision) |
| **3PoinTr: 3D Point Tracks for Learning Manipulation from Unconstrained Human Videos**；Hung 等；2026-03-09，6/3 v2，预印本 | 从初始点云预测未来 3D tracks，压缩成 motion tokens 条件化策略；利用无动作人类视频及每任务 20 条机器人动作示范 | 少机器人示范不等于少全部数据；真实监督用 2D tracks+stereo-to-depth 提升到 3D，**非纯单目 metric GT**。训练总成本未核，项目代码仍 coming soon。[日期](https://arxiv.org/abs/2603.08485)、[v2 正文/附录](https://arxiv.org/html/2603.08485v2)、[项目](https://adamhung60.github.io/3PoinTr/) |
| **Point Tracking Improves World Action Models（JOPAT）**；Guan 等；2026-05-22，预印本 | denoising transformer 联合预测视频 latent、2D tracks、visibility 与动作；CoTracker3 伪标签，无动作视频屏蔽 action loss | 显式轨迹作为联合监督；预训练 4 H200 约 5 天，任务微调单 H200 约 1 天；19 步预测窗口不等于长期 3D 状态。官方代码未确认。[全文](https://arxiv.org/html/2605.23856v1) |
| **History-Aware Visuomotor Policy Learning via Point Tracking（HistRISE）**；Chen 等；2025-09-21，2026-03-16 v2，ICRA 2026 | 点轨迹经时间编码/attention 压成对象历史 token，辅助阶段辨识、重复计数和位置记忆；主实现 RGB-D+TAPIP3D | 适合检验轨迹历史相对图像堆叠的价值；每任务 50 demos，训练总时长未核；训练、在线 tracking、部署代码公开。完整历史不等于有界内存。[v2 全文](https://arxiv.org/html/2509.17141v2)、[发表记录](https://arxiv.org/abs/2509.17141)、[代码](https://github.com/rise-policy/HistRISE) |
| **WAM4D: Fast 4D World Action Model via Spatial Register Tokens**；Li 等；2026-06-12，7/7 v3，预印本 | 训练时用 register 读出 future-depth，给 video-action 模型几何约束；部署删除辅助几何分支 | 属于训练监督；作者仍展示遮挡后身份不一致的 rollout，不能说已解决长期 object memory。单 A800 原报约 525ms/action chunk，训练总成本及代码未确认。[日期](https://arxiv.org/abs/2606.14048)、[v3 全文](https://arxiv.org/html/2606.14048v3) |
| **Learning 4D Geometric Priors for Inference-Efficient World Action Models（MECo-WAM）**；Zhang 等；2026-07-06，预印本 | 用 VGGT 几何 feature 关系蒸馏辅助 4D expert；非对称 attention 和时序蒸馏，部署移除整个辅助模块 | 推理期没有该几何分支，不等于持久 3D tracks；原报 **64 H20-96GB 训练**、单 RTX5090 推理，时长/代码未确认。适合了解趋势，不适合我们从头复刻。[全文](https://arxiv.org/html/2607.05468v1) |

### 16.2 从点轨迹到物体位姿、关节结构和可交互资产

| 工作与时间/状态 | 几何证据如何转成下游结果 | 对我们最值得验证的指标 |
|---|---|---|
| **Point2Pose: Occlusion-Recovering 6D Pose Tracking and 3D Reconstruction for Multiple Unknown Objects via 2D Point Trackers**；Lin 等；2026-04-12，8/25 v2，官方项目标 ECCV 2026 | 单目 **RGB-D** 下，2D tracks 提供持续关联；多假设 frame-to-map registration 和 factor graph 恢复未知刚体位姿，构建在线 TSDF，支持完全遮挡后恢复 | 冻结后端换 tracker，测重现后的 pose recovery、ID 错配、map consistency；原报 2–10Hz，硬件未核。代码公开，YCBMultiTrack 数据仍 Coming Soon；刚体和深度假设需明示。[全文](https://arxiv.org/html/2604.10415v2)、[项目](https://point2pose.github.io/)、[代码](https://github.com/tzuyuan/point-to-pose) |
| **Track, Articulate, Act: Generating Articulation from Casual Human Videos**；Zhang、Bharadhwaj；**2026-09-16**，预印本 | 单目视频经 TrackCraft3R、DA3、SAM3D 等预训练模块获得轨迹和几何，拟合转动/移动关节，以 track/silhouette 重投影优化并生成 MuJoCo 资产、重放手部交互 | 新增方法里最贴近低训练成本下游：关节 type、axis、state、交互重放质量。无需训练专用 articulation 模型，但有逐视频优化；全片离线、单主关节及 open-loop 重放，非通用闭环 policy。总耗时/代码发布未确认。[全文](https://arxiv.org/html/2609.19119v1)、[日期](https://arxiv.org/abs/2609.19119)、[项目入口](https://track-articulate-act.github.io/) |

**研究推断：**如果我们首先改善的是遮挡后的点身份或跨窗坐标一致性，这一组比重新训练一个 world action model 更适合证明实际价值。实验应固定后端，只替换轨迹/几何来源，同时报告下游误差和前端成本；RGB-D 下游的收益不能反推我们的 RGB-only 主任务已达到 metric 精度。

### 16.3 视频生成、相机重定向和运动编辑

| 工作与时间/状态 | 4D / tracks 的作用 | 成本、发布与解释边界 |
|---|---|---|
| **Track2View: 4D-Consistent Camera-Controlled Video Generation via Paired 3D Point Tracks**；Qiao 等；2026-06-14，预印本 | SpaTrackerV2 得到 source camera/3D tracks，目标相机投影出 paired coordinates，沿身份轨迹聚合 appearance 再散射到目标视角 | Wan2.1 conditioner+LoRA rank64；4 A100、576 GPU-hours；81 帧、480×832。官方 repo 仍将代码/权重/训练/data 列为待发布；离线短片生成不是长期重建精度验证。[全文](https://arxiv.org/html/2606.15534v1)、[仓库](https://github.com/mvrl/Track2View) |
| **Generative Video Motion Editing with 3D Point Tracks（Edit-by-Track）**；Lee 等；2025-12-01，CVPR 2026 | 几何模型+TAPIP3D 提轨迹，用户编辑 tracks/camera 后条件化视频生成，支持运动转移、形变、复制/删除 | Wan1.3B+conditioner+LoRA，两阶段 16 A100 约 60 小时；81 帧、672×384、单 A100、50 步生成约 4.5 分钟，另有 3D 预处理。项目演示/论文可读，模型实现未确认发布；基于另一 tracker 的 EPE 不是独立物理真值。[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Lee_Generative_Video_Motion_Editing_with_3D_Point_Tracks_CVPR_2026_paper.html)、[全文](https://arxiv.org/html/2512.02015v1)、[项目](https://edit-by-track.github.io/) |
| **Video Models as Native 4D Renderers: World-Grounded Conditioning from Animated Mesh（DAR）**；Chen 等；**2026-07-30**，8/4 v2，预印本 | 已有动画 mesh 的 tracking、world-position、normal G-buffers 与目标 camera/appearance 条件化 Wan2.2；显式区分表面身份和当前坐标 | 不是从 RGB 重建 4D；LoRA rank256+adapter，3 A800 或 2 H100 约 36 小时；full finetune 用 7 A800。官方实现未确认。可借鉴 identity/position 分离接口，但不能列入 reconstruction 排名。[元数据](https://arxiv.org/abs/2608.00094)、[全文](https://arxiv.org/html/2608.00094v2) |
| **NeoVerse: Enhancing 4D World Model with in-the-wild Monocular Videos**；Yang 等；2026-01-01，3/26 v2，CVPR 2026，作者标 Highlight | pose-free 前馈 4DGS 和双向运动产生目标视角粗渲染，再由视频模型补全/提升，支持 camera redirect、bullet time、编辑 | 原报 81 帧、336×560、单 A800、加速配置下约 20/28 秒，分别对应 11 keyframes/全帧重建设置；总训练成本未核。推理/demo/权重公开。world model 在这里主要指 novel-trajectory rendering，不自动包含动作条件动力学或长期点身份。[全文](https://arxiv.org/html/2601.00393v2)、[项目](https://neoverse-4d.github.io/)、[代码](https://github.com/IamCreateAI/NeoVerse) |

第 14.2 节的 **FreeOrbit4D、PASTEL、MoVieS** 也属于这条联系：前两者引入生成补全，MoVieS 直接连接动态几何与渲染。实验须把**观测到的几何一致性**与**未见区域的生成合理性**分开，不能仅凭感知质量判断重建/跟踪准确。

### 16.4 视频表征、动作理解与语言中的时间关系

| 工作与时间/状态 | 如何利用 tracking / 4D | 适合读什么、不能推出什么 |
|---|---|---|
| **TrackMAE: Video Representation Learning via Track Mask and Predict**；Vandeghen 等；2026-03-28，CVPR 2026 | CoTracker3 提供 2D motion targets，配 motion-aware masking 与像素/语义重建训练 video encoder，评测动作分类和重复计数等 | 轨迹是训练监督；16 A100、800 epochs、16 帧输入，代码公开。适合“追踪质量→运动表征”的消融，但不是 3D streaming memory。[全文](https://arxiv.org/html/2603.27268v1)、[发表记录](https://arxiv.org/abs/2603.27268)、[代码](https://github.com/rvandeghen/TrackMAE) |
| **4DVLT: Dynamic Scene Understanding with Worldline-Centered Vision-Language Tracking**；Li 等；2026-06-21，预印本 | 全观测多视图视频+instruction→语义实体、metric 3D 轨迹、同步 2D boxes；4DTrack 用图路由/双向解码，Instruct-4D 含约 129.4k QA | 是 **object-centric** worldlines，不是任意 material-point tracking；多视角/双向处理。成本未核，代码/数据/checkpoint 全 Coming Soon；适合理解长期身份如何支持语言查询。[全文](https://arxiv.org/html/2606.22631v1)、[元数据](https://arxiv.org/abs/2606.22631)、[发布状态](https://github.com/mikubaka88/4DVLT) |

对本课题，这两类工作主要提供**评价用途**：当点轨迹更稳定时，动作阶段、运动关系和重复计数是否更可靠？不宜在没有控制实验的情况下，把 tracking 指标提高直接等同于语义理解提高。

## 17. 新数据、评测协议与容易误用的监督

### 17.1 新增数据/基准记录

| 数据或协议、时间/发表信息 | 标注来源与覆盖 | 如何用于本项目，哪些结论不能据此得出 |
|---|---|---|
| **SceneScribe-1M: A Large-Scale Video Dataset with Comprehensive Geometric and Semantic Annotations**；Wang 等；2026-04-09，4/26 v2，CVPR 2026 | 约 100 万野外视频、4191 小时；含语义、camera/depth、动态区域和 3D tracks。语义由 Qwen2.5-VL、几何由 MegaSaM、轨迹由 TAPIP3D 等生成 | 是大规模**模型伪标注**资源，不是传感器/人工提供的独立 3D 真值。原报标注用 >1000 H20、约 150k GPU-hours；不应计划自行全量重建。已查作者 HF 页面仅占位文件，完整数据下载未确认。[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Wang_SceneScribe-1M_A_Large-Scale_Video_Dataset_with_Comprehensive_Geometric_and_Semantic_CVPR_2026_paper.html)、[方法与数据生产](https://arxiv.org/html/2604.07990v2)、[已查 HF 文件页](https://huggingface.co/datasets/wangyunnan/SceneScribe-1M/tree/main) |
| **SynthVerse: A Large-Scale Diverse Synthetic Dataset for Point Tracking**；Zhao 等；2026-02-04，作者标 SIGGRAPH 2026 | Blender/IsaacSim，约 48k 序列；人/动物、交互、导航、具身等，含 RGB/depth/K/pose/2D–3D tracks/visibility | 适合扩大运动和场景类型，控制 GT pose/depth 做失效诊断；合成精确标签不等于真实域性能。官方 benchmark HF 已见实际分域数据文件；完整训练集下载未核，不能把所有序列都称千帧长视频。[全文](https://arxiv.org/html/2602.04441v1)、[项目/数据入口](https://weiguangzhao.github.io/SynthVerse/)、[代码仓库](https://github.com/weiguangzhao/SynthVerse)、[benchmark 文件](https://huggingface.co/datasets/InternRobotics/SynthVerse-Benchmark/tree/main) |
| **ITTO: Is This Tracker On? A Benchmark Protocol for Dynamic Tracking**；Demler 等；**2025-10-22**，NeurIPS 2025 Datasets and Benchmarks | 真实视频中的人工 2D 点标注，重视动态运动、遮挡和重新出现；本轮补入的较早重要基准 | 用于检查平均 AJ 掩盖的长遮挡/重现失败；不是新 2026 数据集，也没有独立 metric 3D GT。代码及数据入口公开。[论文](https://arxiv.org/abs/2510.19819)、[正式论文](https://papers.nips.cc/paper_files/paper/2025/file/18093dfe68516361d5b6239d33e045b1-Paper-Datasets_and_Benchmarks_Track.pdf)、[项目](https://glab-caltech.github.io/ITTO/)、[代码](https://github.com/ilonadem/itto) |
| **VOTSp 2026**；官方 point-tracking challenge/protocol | 首帧指定 2D 点，跨 egocentric、机器人、动物、细胞等来源测试，官方给 AllTracker baseline | 是评测活动，不是一篇新的 tracker 论文。适合跨域泛化；输入、训练限制和服务器协议以官方为准，**不可默认把测试来源数据纳入训练**；不是世界 3D 评价。[官方参与规则](https://www.votchallenge.net/vots2026/participation.html) |
| **D4D: The Dresden Dataset for 4D Reconstruction of Non-Rigid Abdominal Surgical Scenes**；Docea 等；2026-03-03；arXiv 注明 submitted to Scientific Data | 离体猪腹腔场景，立体内镜与 structured-light 扫描配准，含非刚性组织、器械、立体深度/掩码与参考点云 | 有价值的真实非刚体几何域；结构光主要是记录的开始/结束参考，**不是每帧稠密物质点真值**。未核期刊录用，不写 Scientific Data 已发表；数据下载未验证。[元数据](https://arxiv.org/abs/2603.02985)、[全文](https://arxiv.org/html/2603.02985v1) |
| **Bridging Vision and Language for Robust Context-Aware Surgical Point Tracking: The VL-SurgPT Dataset and Benchmark**；Zhou 等；AAAI 2026，出版社页面 2026-03-14 | 908 段体内组织/器械视频，2D point annotations 配状态/语义描述；提出 TG-SurgPT 文本引导 tracker | 研究烟雾、反光、组织形变下的 context-aware tracking；语言是额外输入，不能并入 RGB-only tracker 排名。本轮读取出版页/摘要，完整实现与数据发布未确认。[出版社与 DOI](https://ojs.aaai.org/index.php/AAAI/article/view/38383)、[正式 PDF](https://ojs.aaai.org/index.php/AAAI/article/download/38383/42345) |

### 17.2 这次更新对实验协议的具体约束

1. **教师产生的“GT”与真实/合成几何真值分开。** 如果新方法训练于 SceneScribe-1M，再用同一 MegaSaM/TAPIP3D 管线产生的标签测试，很可能只测到教师一致性。训练伪监督可以保留，主结论仍应由独立标签支撑。
2. **相机系、世界系、metric 与相对尺度分开。** Fast Spatial Tracker 的相机系轨迹、MV-TAP 的多视角 2D 输出、Any4D 的 metric 预测不是同一种任务。转换坐标所用的 pose/K/depth 及其来源必须一起报告。
3. **“完整长视频”同时记录连续身份长度。** 600 帧输入展示、16 帧窗口、首帧锚点跳采样、在整个窗口都不可见的点，难度不同。除总帧数，还应报查询年龄、遮挡持续时间、新点加入时间和有效连续轨迹长度。
4. **离线吞吐、发布延迟和轨迹时间采样率分别列。** 28ms/frame 不必然在线；150fps 可能只是输出采样；GS render FPS 不包含重建；前端全片 depth/pose 也会引入未来信息。
5. **评测版本要可追踪。** 固定代码 commit、权重名、数据 split 与 alignment protocol；VGGT-Ω 的 reproduction 模型与旧模型、St4RTrack 的动态重加权版本必须分开记录。
6. **场景重建与物质点身份分别评价。** 动态 GS 可以靠生成/删除原语改善渲染，生成模型可以填补“看起来合理”的遮挡区域；都不能自动证明物理表面点保持一致。建议搭配独立 point metrics、几何误差和下游指标。

第 9 节已有 **TAPVid-3D、WorldTrack、PointOdyssey、Dynamic Replica、TAPVid-MV、LSFOdyssey/Syn4D**。本轮补充并不取代它们：优先在已有数据和代码上增加受控分组，再决定是否引入更大数据集。完整未知 pose RGB 管线与使用 GT 几何的诊断实验应分别报告。

## 18. 读完这一轮后，研究优先级如何调整

### 18.1 接下来最值得精读与实现核查的顺序

| 优先级 | 文献组合 | 读完必须能回答的问题 |
|---|---|---|
| **第一组：直接竞争** | Point4D、4RC/S-4RC、Complet4R，连同原有 V-DPM/St4RTrack | 我们声称解决的遮挡、跨窗身份或固定内存问题，是否已被这些方法覆盖？可公开复现的是哪一个变体？ |
| **第二组：身份与几何的联系** | TrajVG、TrackCraft3R、CoWTracker、Fast Spatial Tracker | 收益来自更好的几何、更强的外观/运动先验，还是独立的身份关联机制？输出到底在哪个坐标系？ |
| **第三组：预算与监督** | AnthroTAP、M2P、PAGE-4D、VGGT-Ω reproduction | 能复用什么训练资产？最小适配能否对准一个可测失败？教师/benchmark 是否独立？ |
| **第四组：低训练成本下游验证** | Point2Pose、Track–Articulate–Act；有机器人条件再加 Dex4D/HistRISE | 冻结下游后，更可靠的点身份/几何是否带来 pose、joint 或任务成功率改善？ |
| **第五组：较长期拓展** | Gen-Points、Track2View、Edit-by-Track、4DVLT、WAM4D/MECo-WAM | 不确定轨迹、生成控制、语义身份和训练监督分别需要怎样的表示？哪些项目的公开性/成本尚不足以支撑短周期实验？ |

### 18.2 对原候选方向的保留与收紧

**仍然值得优先验证：有界历史条件下，点经历完整窗口不可见后重新出现时的身份恢复，以及它与几何漂移的耦合。** 支撑这一判断的是更明确的方法边界：Point4D 传递点坐标及 patch descriptor，但没有可检索的历史场景特征库；S-4RC 缓存全部历史；UniQuery4R 未完成跨窗融合；TrackCraft3R 保持首帧锚点并按整片长度分组。各方法的这些边界都已在上文来源中标出。**它们是否在我们的数据上造成主要误差，仍须实验验证。**

应降低优先级的宽泛命题包括：“几何 backbone 加 tracker head”“将视频生成先验适配到 3D tracking”“加入动态 mask 保护 pose”“用 point trajectories 改善 world model 或视频表征”。对应先例已分别见于 CoWTracker/Fast Spatial Tracker、TrackCraft3R、PAGE-4D、JOPAT/TrackMAE 等。只有输入约束、失效机制和验证证据更清楚时，才值得继续。

若延续短周期投稿计划，建议先完成三项小规模诊断，不先训练大模型：

- **同一组完整视频、同一初始 query**：对 Point4D 与已有 V-DPM/St4RTrack，画误差随 query age、遮挡时长和窗口边界距离的变化，分别看动态/静态点。
- **单一跨窗边界的受控干预**：将坐标对齐误差与 query/identity 交接误差分开；能用 GT 做 oracle 诊断时，明确只作为定位失败原因，不进入可部署主结果。
- **下游冻结验证**：若身份错误是主因，用 Point2Pose 式位姿恢复或关节拟合任务检验“identity 改善是否比单纯逐帧几何改善更有用”；先选择已有代码/数据支持的最小实验。

对于两个月周期，可以在同一失败证据上发展持久状态、有限容量记忆或小规模适配；**不建议同时新训练 tracking backbone、重建器和机器人/视频生成下游**。这是结合 1 位主力、2–3 位辅助以及 8 张 H20D 约 70% 可用时间作出的工作范围判断，不是中稿保证。

### 18.3 本轮证据深度与未解决项

- 核心新增方法优先读方法、实验、限制与官方实现说明；**MuBe4D** 只获得期刊摘要，**VL-SurgPT** 主要依据出版页/摘要，不能与精读条目等量使用。
- **TrajVG/SynthVerse 的 SIGGRAPH、PASTEL/Point2Pose 的 ECCV** 已有作者官方标注，本文明确保留来源级别；没有额外声称已核正式卷页。FreeOrbit4D 已核正式 DOI 与会议类别。
- 未确认开源的条目不会作为短周期计划的唯一依赖。仓库存在、README 承诺、推理实现、training/evaluator 与权重可下载是不同状态。
- 本次没有重新跑实验、下载大数据集或测试模型权重；论文中的效率、精度及硬件报告均为作者结果。跨模型公平性和 H20D 实际可行性需后续复现。
- 检索截止 **2026-09-17**，以已公开可定位证据为准；这是面向当前研究问题的更新，不宣称穷尽所有 2026 年相关投稿。后续更新应追加明确日期，并保留当前版本的证据边界。
