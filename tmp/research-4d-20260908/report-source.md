# 动态长序列的 4D 重建与 Point Tracking：文献调研与选题判断

> 更新至 **2026-09-08**。面向正在准备 ICLR/CVPR 级论文的研究合作者。  
> 已确认设置：**单目 RGB、未知相机位姿、动态场景、流式输入或长视频；可用 8 张 H20D；优先 training-free、测试时优化/适配或有限微调。**  
> 本文在已有 4D/tracking/长序列笔记基础上重新检索原论文、补充材料和官方代码。论文结果、作者的资源报告与本文的研究推断分别标明；没有实际运行模型，也没有实测 H20D 性能。

## 1. 先给选题判断

**这个方向值得做，但“4D reconstruction + tracking + streaming + 少量训练”已经不足以定义创新。** St4RTrack 已联合世界坐标重建、跟踪和测试时适配；Flow4R 用 scene flow 统一几何与运动；V-DPM 将动态点图扩展到视频；Point4Cast 已面向流式输入维护可按时间查询的场景状态。因此，论文应围绕一种明确、可复现的失效机制展开，而不是围绕模块组合展开。[St4RTrack](https://arxiv.org/html/2504.13152v1)、[Flow4R](https://arxiv.org/html/2602.14021v1)、[V-DPM](https://arxiv.org/html/2601.09499v1)、[Point4Cast](https://www.merl.com/research/highlights/point4cast)

**我的优先建议是研究：有限记忆下，如何用当前可获得的证据，持续校正世界几何，同时保持动态物质点身份。** 具体先验证“相机/尺度漂移、物体真实运动和对应错误相互补偿”是否是现有模型的主要长程失败来源，再决定做低维在线优化、可观测性约束的 TTA，还是身份记忆。这里是研究假设，不是已验证的新颖性或性能结论。

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

**Point4D: Long-range 4D Motion Reconstruction** 的公开索引稿提出 3D point query、跨 chunk endpoint chaining，以及来自任意可见帧的外观 patch，以应对边界遮挡。它已经非常接近“3D 身份跨窗口传递”的直觉方案。[公开稿](https://msjeon.me/data/Point4D.pdf)

Point4D 本次只核到原稿的搜索索引段落，完整 PDF 未成功读取；稿件标匿名、NeurIPS 2026 submitted，**不能写成录用论文，作者、代码和完整评测仍待核**。但其公开方法描述已足以构成新颖性风险，不能忽略。

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

TAPNext++ 尤其重要：从公开 BootsTAPNext-B 微调，使用 8 H100，训练设计针对长序列与再检测，并提出再检测评价。**“延长训练片段 + 遮挡 loss reweighting + 长程新指标”已有直接竞争。** 我们需要证明 3D 几何提供了额外的可检验约束，而非换一个记忆结构重新做同样的事。[TAPNext++ §4](https://arxiv.org/html/2604.10582v1)

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

本次是面向选题决策的定向调研，不是全领域穷尽书目。重点覆盖 2023–2026 年直接相关方法，部分更早基准作为必要背景；未系统展开多相机输入、已知物体模型、人体专用重建、生成式补全或完整物理世界模型。

- 核心方法优先阅读原论文的方法、实验和补充材料；TAPIR/BootsTAP 等成熟背景方法主要作谱系定位，阅读深度不与核心方法等同。
- **Point4Cast** 完整 PDF 抓取受限，使用正式条目、官方说明和原 PDF 可检索段落；精确代码状态、完整训练/评测细节未全部确认。
- **Point4D** 为证据有限的公开匿名稿线索，不把 submitted 当 accepted，不据此给出完整性能判断。
- 代码“已公开”表示查看到官方实现/下载入口，不表示本机运行成功；权重的实际完整性、evaluator 默认配置和端到端因果性仍需运行核查。
- 论文数据与代码版本可能不同，尤其 St4RTrack 与 SpaTrackerV2，复现时应记录 commit、checkpoint、数据 split 和评测脚本。
- 所有算力数字是作者在其配置下的报告。H20D 显存规格、互联、可用总训练时间未实测或指定，本文没有推断具体型号容量，也没有进行跨 GPU 耗时换算。
- Markdown 已进行结构、链接格式和内容一致性检查；未生成 PDF/DOCX，也未执行浏览器排版检查。

**用于下一次讨论的最具体决策是：先围绕 St4RTrack/V-DPM 做受控的长程误差分解，检验方向 A；若主要瓶颈在 GT 几何下仍然存在的身份交换，则转向方向 B。** 在实验前，不能声称找到了“无人做过”的组合；真正值得投入的是能够清楚解释、稳定重现并被一个小机制修复的失败。
