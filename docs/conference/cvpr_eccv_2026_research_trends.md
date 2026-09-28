# CVPR 2026 与 ECCV 2026：代表论文梳理与科研趋势

> 检索截止：**2026 年 9 月 28 日**。本文面向科研选题，兼顾计算机视觉全局与三维视觉、SLAM、流式 4D 的具体问题。
>
> **范围与方法：**以两届主会的正式论文页面、官方录用记录和作者原文为依据，按研究问题选择代表论文。主要阅读摘要与方法说明，重点几何论文补查执行方式和局限；不是数千篇论文的逐篇全文综述，也不是完整主题计量分析。未运行模型或独立复现论文结果。表中的“阅读边界”主要是本文提出的核查问题，只有明确归于作者的内容才表示论文已报告的局限。

## 1. 先把握整体变化

**从本次核实的论文样本看，2026 年视觉研究的一条共同主线是：在基础模型已有较强能力的前提下，让它们更准确地使用视觉证据、更持久地维护世界状态，并在可承担的计算预算内完成任务。**这体现在推理、生成、三维、具身和评测等多个方向；不代表传统识别、分割或计算成像已经失去价值。

可以用下面十个问题组织阅读。这里的“趋势”是跨论文的定性归纳，不是论文数量增长率或主题热度排名；具体证据见第 3 节。

| 研究主线 | 论文集中解决的问题 | 阅读时应追问 |
|---|---|---|
| 视觉参与推理 | 中间视觉表示、主动查看局部区域、选择有效证据 | 输出正确究竟来自图像，还是语言先验？ |
| 理解与生成的统一 | 共享语义表示，同时保留生成所需的细节 | 任务之间是否互相伤害？统一带来什么可测收益？ |
| 可控且高效的生成 | 一步编辑、少步视频、轨迹控制、低成本训练 | 画质、控制误差、延迟是否同时改善？ |
| 几何基础模型扩展 | 静态与动态场景、多任务几何、规模化数据 | 几何精度、训练成本和域外泛化分别如何变化？ |
| 4D 与长期状态 | 相机、几何、物体运动、点身份与历史记忆 | 长视频能力是否包含真正的长期一致性？ |
| SLAM 与学习模型结合 | 地图维护、历史压缩、状态更新、全局校正 | 是否因果？有没有回环？总记忆如何随时长增长？ |
| 视觉到行动 | 游戏、网页和机器人中的感知—决策—反馈 | 离线预测准确率能否转化为闭环任务成功？ |
| 数据与监督机制 | 合成物理数据、真实对齐、软标签与奖励设计 | 增益来自方法，还是额外数据、教师和计算量？ |
| 诊断性评测 | 数值物理、多图幻觉、真实恶劣条件、动态一致性 | 基准能否定位失败原因，而非只给一个总分？ |
| 领域与传感器约束 | 医疗、遥感、事件相机、物理成像 | 是否利用了该领域独有的信息与约束？ |

对已有 SLAM / 三维背景的研究者，最值得优先跟进的是 **几何基础模型 + 长期状态维护 + 可靠评测** 的交叉区域。选题应进一步收窄成某个可测的失效机制，例如遮挡后的身份恢复、动态运动与相机漂移混淆、有限记忆下的历史证据丢失，而不是只组合“4D、streaming、world model”等名称。第 5 节给出可验证的研究假设。

## 2. 会议与论文公开情况

| 项目 | CVPR 2026 | ECCV 2026 |
|---|---|---|
| 举办时间与地点 | 6 月 3–7 日，美国丹佛；主会 6 月 5–7 日 | 9 月 8–12 日，瑞典 Malmö；主会 9 月 10–12 日 |
| 可核实的规模 | 官方新闻：16,092 篇投稿，4,089 篇录用 | Springer 论文集介绍：10,473 篇投稿，收入 2,834 篇论文 |
| 根据上述数字计算 | 约 25.41% | 约 27.06% |
| 主要论文入口 | CVF Open Access 主会论文库 | 官方录用列表、主会视频列表、Springer LNCS 论文集 |
| 本文处理口径 | 使用 `CVPR2026` 主会记录；不混入 `CVPR2026W` 或 `CVPR2026F` | 官方录用列表仍注明出版检查状态；能找到正式章节时优先引用正式章节 |

来源：[CVPR 官方新闻](https://cvpr.thecvf.com/Conferences/2026/News/Best_Papers)、[CVPR 日程](https://cvpr.thecvf.com/Conferences/2026/TentativeSchedule)、[CVF 论文库](https://openaccess.thecvf.com/CVPR2026)、[ECCV 官网](https://eccv.ecva.net/Conferences/2026)、[ECCV 录用列表](https://eccv.ecva.net/Conferences/2026/AcceptedPapers)、[Springer 论文集介绍](https://link.springer.com/book/10.1007/978-3-032-37314-4)。两列分别采用官方录用与出版方统计口径，不能据此比较会议审稿难度。

CVPR 的官方奖项为阅读提供了几个入口：**D4RT** 获最佳论文，**Native and Compact Structured Latents for 3D Generation** 获最佳学生论文，**NitroGen、SAM 3D** 获最佳论文荣誉提名，**ChordEdit** 获最佳学生论文荣誉提名。它们涉及动态几何、三维表示、行动模型和高效编辑，但奖项样本很小，不宜代替整体趋势分析。[官方奖项公告](https://cvpr.thecvf.com/Conferences/2026/News/Best_Papers)

**如何解读两届会议的差异：**下文比较的是它们在共同问题上的不同方法，而不是断言研究领域在 6 月到 9 月之间发生了某种整体转向。论文的投稿、预印本、修订和正式出版日期也不同；“2026 年 arXiv 论文”不能自动归为这两届会议。

## 3. 按研究问题梳理代表论文

下文论文名保持英文，便于检索。CVPR 链接优先指向正式 CVF 记录；ECCV 同时保留正式章节或官方身份记录与原文入口。论文摘要中的性能改善均属于作者实验结果，本文不将不同数据、硬件或评价协议下的数字直接横向排序。

### 3.1 多模态推理：决定看什么、保留什么、如何推理

**观察：**这组工作把视觉证据的获取和编码放进推理过程，也开始联合分配视觉与语言计算预算。它们并不支持“思维链越长就越可靠”的简单结论。

| 编号与会议 | 论文 | 核心内容 | 阅读边界 |
|---|---|---|---|
| P01 · CVPR | [Latent Implicit Visual Reasoning](https://openaccess.thecvf.com/content/CVPR2026/html/Li_Latent_Implicit_Visual_Reasoning_CVPR_2026_paper.html) | 学习潜在视觉推理 token，按任务重编码图像，避免预先规定中间表示必须是裁剪、深度图或辅助图。 | 潜在 token 的有效性不自动证明推理可解释或忠实于视觉证据。 |
| P02 · CVPR | [When Visualizing is the First Step to Reasoning: MIRA, a Benchmark for Visual Chain-of-Thought](https://openaccess.thecvf.com/content/CVPR2026/html/Zhou_When_Visualizing_is_the_First_Step_to_Reasoning_MIRA_a_CVPR_2026_paper.html) | 用 546 道需要中间视觉线索的题目，比较直接回答、文字 CoT 和视觉辅助条件。 | 提供正确中间图像后的收益，与模型自主产生正确中间图像的能力要分开。 |
| P03 · CVPR | [Rethinking Token Reduction for Large Vision-Language Models](https://openaccess.thecvf.com/content/CVPR2026/html/Wang_Rethinking_Token_Reduction_for_Large_Vision-Language_Models_CVPR_2026_paper.html) | MetaCompress 以可学习映射统一剪枝与合并，并采用不依赖当前问题的压缩，关注多轮问答中的信息保留。 | 首轮无用的视觉信息可能在后续轮次变得关键；不能只评首轮准确率。 |
| P04 · ECCV | [Foveated Reasoning: Stateful, Action-Based Visual Focusing for Vision-Language Models](https://link.springer.com/chapter/10.1007/978-3-032-36969-7_1) | 从低分辨率全图出发，在推理中主动选择何时、何处补充高分辨率观察，并通过监督学习与 RL 训练。 | 应固定视觉预算，测量漏看关键证据的情况；主动观察也有额外成本。 |
| P05 · ECCV | [Look Less, Think Faster: Joint Token-Compute Adaptation for Multimodal LLMs](https://link.springer.com/chapter/10.1007/978-3-032-37359-5_12) | SmartVL 用视觉和语言两个控制器，按输入复杂度与预算联合分配 token 和计算。 | 计算量估计需要以实际硬件上的端到端延迟和显存检验。 |
| P06 · ECCV | [Reinforcing Video Reasoning with Focused Thinking](https://arxiv.org/abs/2505.24718) | TW-GRPO 对信息量较高的推理 token 加权，结合多答案软奖励和问答反转数据增强。 | 需分离奖励、数据增强与训练预算的贡献；多答案设置的收益不自动迁移到开放问答。 |

P06 的主会身份见 [ECCV 官方视频目录](https://eccv.ecva.net/Conferences/2026/Videos)。其预印本始于 2025 年，会议归属与首次公开年份应分别记录。

### 3.2 理解与生成：表示统一、细节保留、运动控制与低延迟

**观察：**“生成得好看”之外，论文开始共同优化语义遵循、局部编辑、运动控制、物理一致性和计算成本。二维生成与三维资产生成仍有不同的输入、表示和评价目标。

| 编号与会议 | 论文 | 核心内容 | 阅读边界 |
|---|---|---|---|
| P07 · CVPR | [ChordEdit: One-Step Low-Energy Transport for Image Editing](https://openaccess.thecvf.com/content/CVPR2026/html/Lu_ChordEdit_One-Step_Low-Energy_Transport_for_Image_Editing_CVPR_2026_paper.html) | 将编辑写成源、目标分布间的传输，构造适合一步推断的低能量编辑场，无需额外训练或反演。 | 编辑遵循度与非编辑区域保持应分别评价；一步推断不等于任意设备实时。 |
| P08 · CVPR | [FlashMotion: Few-Step Controllable Video Generation with Trajectory Guidance](https://openaccess.thecvf.com/content/CVPR2026/html/Li_FlashMotion_Few-Step_Controllable_Video_Generation_with_Trajectory_Guidance_CVPR_2026_paper.html) | 结合轨迹适配、生成器蒸馏和再对齐，并以 FlashBench 同时测画质和轨迹准确性。 | 二维轨迹控制准确，不足以证明三维物理一致或可用于闭环机器人控制。 |
| P09 · ECCV | [Cheers: Decoupling Patch Details from Semantic Representations Enables Unified Multimodal Comprehension and Generation](https://arxiv.org/abs/2603.12793) | 解耦语义与局部细节；共享主干承担理解与生成，级联 flow-matching 头逐步补充细节。 | 统一表示的价值需用任务冲突、理解精度、生成质量与训练成本共同检验。 |
| P10 · ECCV | [EFlow: Fast Few-Step Video Generator Training from Scratch via Efficient Solution Flow](https://link.springer.com/chapter/10.1007/978-3-032-37314-4_17) | 结合 solution-flow 目标、局部—全局注意力、token 丢弃和低成本训练目标，同时降低单步成本与采样步数。 | 这是从头训练少步生成器的方案，不应与无训练的推断加速混为一类。 |
| P11 · ECCV | [PhysRAG: Enhancing Physics-Awareness in Video Generation via Retrieval-Augmented Generation](https://arxiv.org/abs/2606.26916) | 构建物理参考视频库，以检索和可学习查询向扩散模型注入参考信息，测试物理相关与综合视频指标。 | 参考库覆盖、检索匹配和域外外推需要单独验证；物理观感不能替代定量动力学。 |
| P12 · CVPR | [Native and Compact Structured Latents for 3D Generation](https://openaccess.thecvf.com/content/CVPR2026/html/Xiang_Native_and_Compact_Structured_Latents_for_3D_Generation_CVPR_2026_paper.html) | O-Voxel 同时表示复杂拓扑、几何和材质，配合稀疏压缩 VAE 与 flow matching 学习三维生成。 | 紧凑表示与高质量资产生成，不等于低成本从头训练，也不同于在线场景测量。 |
| P13 · CVPR | [SAM 3D: 3Dfy Anything in Images](https://openaccess.thecvf.com/content/CVPR2026/html/Chen_SAM_3D_3Dfy_Anything_in_Images_CVPR_2026_paper.html) | 从单图预测对象几何、纹理和布局；通过人机协同数据流程、合成预训练与真实对齐提升复杂自然图像中的重建。 | 遮挡部分包含生成性补全；视觉偏好上的优势不能等同真实几何的度量精度。 |

P09、P11 的主会身份见 [ECCV 官方视频目录](https://eccv.ecva.net/Conferences/2026/Videos)；方法分别对照 [Cheers 作者代码](https://github.com/AI9Stars/Cheers)、[PhysRAG 作者项目](https://sediment1024.github.io/PhysRAG/)。

### 3.3 CVPR 的三维与 4D 样本：统一表示、动态重建与系统约束

**观察：**前馈几何正在同时扩展模型和数据规模、输出任务、输入模态与场景时长。但“前馈”“4D”“在线”“完整 SLAM”描述的是不同属性，不能互相替代。

| 编号与会议 | 论文 | 核心内容 | 阅读边界 |
|---|---|---|---|
| P14 · CVPR | [VGGT-ohm](https://openaccess.thecvf.com/content/CVPR2026/html/Wang_VGGT-ohm_CVPR_2026_paper.html) | VGGT-O 简化密集预测头，以 scene token 聚合特征，结合动态场景标注与自监督视频训练，扩展静态、动态几何能力。 | 需分离架构、数据规模和监督协议的增益；计算更省不自动意味着已经解决无限长流式重建。 |
| P15 · CVPR | [Efficiently Reconstructing Dynamic Scenes One D4RT at a Time](https://openaccess.thecvf.com/content/CVPR2026/html/Zhang_Efficiently_Reconstructing_Dynamic_Scenes_One_D4RT_at_a_Time_CVPR_2026_paper.html) | 将视频编码为全局表征，再以轻量查询解码深度、时空对应、相机及不同时间的三维位置。 | **全局视频编码与按需查询，不等于因果 streaming。**其核心价值是统一、可查询的 4D 表示。 |
| P16 · CVPR | [Any4D: Unified Feed-Forward Metric 4D Reconstruction](https://openaccess.thecvf.com/content/CVPR2026/html/Karhade_Any4D_Unified_Feed-Forward_Metric_4D_Reconstruction_CVPR_2026_paper.html) | 联合预测几何与运动，分离相机局部和世界坐标因子，并支持 RGB、RGB-D 及可用的 IMU、Radar 信息。 | 作者指出场景流以首帧为源，且附加传感器采用理想模拟；真实噪声、异步和新出现对象仍需核查。 |
| P17 · CVPR | [Point4Cast: Streaming Dynamic Scene Reconstruction and Forecasting](https://openaccess.thecvf.com/content/CVPR2026/html/Liu_Point4Cast_Streaming_Dynamic_Scene_Reconstruction_and_Forecasting_CVPR_2026_paper.html) | 新帧更新持续演化的潜在时空状态，再按时间查询过去、当前和未来的点图与相机参数。 | 重建、跟踪与预测应分别评价；能预测未来点图尚不能证明一般物理规律外推。 |
| P18 · CVPR | [SLARM: Streaming and Language-Aligned Reconstruction Model for Dynamic Scenes](https://openaccess.thecvf.com/content/CVPR2026/html/Qiu_SLARM_Streaming_and_Language-Aligned_Reconstruction_Model_for_Dynamic_Scenes_CVPR_2026_paper.html) | 将高阶运动、可微渲染、语言对齐语义和窗口因果注意力结合，联合处理动态场景表示。 | 几何、画质与语义指标改善，需要进一步检查长期物体身份和下游任务收益。 |
| P19 · CVPR | [LASER: Layer-wise Scale Alignment for Training-Free Streaming 4D Reconstruction](https://openaccess.thecvf.com/content/CVPR2026/html/Ding_LASER_Layer-wise_Scale_Alignment_for_Training-Free_Streaming_4D_Reconstruction_CVPR_2026_paper.html) | 冻结离线模型，通过重叠窗口与分层尺度对齐处理跨窗几何不一致；不同深度层不强制共用单一尺度。 | 窗口流式仍需注明输出等待；层间关联、低视差条件和回环后的尺度修正值得检查。 |
| P20 · CVPR | [MERG3R: A Divide-and-Conquer Approach to Large-Scale Neural Visual Geometry](https://openaccess.thecvf.com/content/CVPR2026/html/Cheng_MERG3R_A_Divide-and-Conquer_Approach_to_Large-Scale_Neural_Visual_Geometry_CVPR_2026_paper.html) | 将无序图像分成有重叠且几何多样的子集，调用基础模型后做全局对齐和置信度加权 BA，无需额外训练。 | 面向大规模无序图集；全局优化流程不应直接称为严格在线 SLAM。 |
| P21 · CVPR | [Unblur-SLAM: Dense Neural SLAM for Blurry Inputs](https://openaccess.thecvf.com/content/CVPR2026/html/Zhang_Unblur-SLAM_Dense_Neural_SLAM_for_Blurry_Inputs_CVPR_2026_paper.html) | 前馈去模糊与局部、全局多视图优化协同，对困难帧结合 3DGS 和模糊形成过程进行处理。 | 需同时衡量退化强度、失败率和计算开销；清晰图像上的平均精度不足以评价鲁棒系统。 |

其中 Any4D 的具体边界来自[作者原文](https://any-4d.github.io/assets/Any4D.pdf)；D4RT 的编码—查询结构也可对照[作者项目](https://d4rt-paper.github.io/)。

### 3.4 ECCV 的长序列几何样本：记忆、状态估计与全局校正

以下六篇均在 [ECCV 官方主会录用名单](https://eccv.ecva.net/Conferences/2026/AcceptedPapers)核实；表内链接为作者论文或项目。其方法设置不同，不宜放在一张仅比较 FPS 的榜单中。

| 编号与会议 | 论文 | 核心内容 | 阅读边界 |
|---|---|---|---|
| P22 · ECCV | [Geometric Context Transformer for Streaming 3D Reconstruction](https://arxiv.org/abs/2604.14141) | GCT / LingBot-Map 以锚点、局部位姿参考窗口和轨迹记忆，分别维护坐标基准、局部几何和历史轨迹。 | 作者说明没有显式回环，历史压缩可能损失细节；每历史帧保留 6 个 context token，不能称严格常数内存。 |
| P23 · ECCV | [FILT3R: Latent State Adaptive Kalman Filter for Streaming 3D Reconstruction](https://arxiv.org/abs/2603.18493) | 在潜在状态上加入无需训练的滤波层，以逐 token 方差和自适应增益平衡旧状态与新证据。 | 作者指出测量噪声固定，难以适应模糊和遮挡；大漂移可能导致过度相信不可靠新状态。 |
| P24 · ECCV | [Scal3R: Learning Efficient Multi-Relative Pose Query for Scalable Online 3D Reconstruction](https://linjohnss.github.io/scal3r/) | 冻结主干，以少量相对位姿查询参数连接历史关键帧，并结合在线位姿图与回环保持全局一致性。 | 作者指出仍受主干、外观回环与阈值限制；这里是 Lin 等的相对位姿查询论文，勿与另一篇同名 Scal3R 混引。 |
| P25 · ECCV | [RegVGGT: Sustainable Visual Geometry Grounding for Streaming via Regulated Memory](https://arxiv.org/abs/2609.23286) | 利用 token 初始显著性预测长期重要性，限制每帧进入记忆的 token，以较小的增长速度延长推断序列。 | 保留每帧约 1% token 仍然可能随帧数增长；初始显著性是否等于未来重访价值值得验证。 |
| P26 · ECCV | [RayMap3R: Inference-Time RayMap for Dynamic 3D Reconstruction](https://github.com/Brack-Wang/raymap3r) | 比较图像与 RayMap 分支的深度，用静态偏置构造权重并门控记忆更新，同时处理重置后的尺度和轨迹。 | 减少动态物体污染静态地图，不等于完整维护动态物体的几何和长期身份。 |
| P27 · ECCV | [SLAM-Former: Putting SLAM into One Transformer](https://tsinghua-mars-lab.github.io/SLAM-Former/) | 将逐帧跟踪、增量建图与后端全局修正组织进统一 Transformer，并使前后端交替协作。 | 需检查全局校正时机、历史地图更新和整体计算量；与 SLAMFormer-Infinity 是不同论文。 |

影响选题的三个细节可直接回到原文核查：[GCT 方法与局限](https://arxiv.org/html/2604.14141v2)、[FILT3R 第 5 节](https://arxiv.org/html/2603.18493v2)、[Scal3R 方法与局限](https://arxiv.org/html/2609.04201v1)。这些细节比“支持上千帧”更能说明还有什么问题未解决。

### 3.5 视觉到行动，以及长视频中的可检索记忆

**观察：**任务单元从单次预测扩展为连续执行与证据检索。游戏、网页和视频问答提供了不同环境，不能直接用一个任务的成功率代表所有具身能力。

| 编号与会议 | 论文 | 核心内容 | 阅读边界 |
|---|---|---|---|
| P28 · CVPR | [NitroGen: An Open Foundation Model for Generalist Gaming Agents](https://openaccess.thecvf.com/content/CVPR2026/html/Magne_NitroGen_An_Open_Foundation_Model_for_Generalist_Gaming_Agents_CVPR_2026_paper.html) | 从游戏视频提取动作，结合大规模行为克隆、多游戏评测及开放数据、权重，学习视觉—行动模型。 | 跨游戏迁移是其证据范围；游戏控制与真实机器人接触、动力学和安全约束仍不同。 |
| P29 · ECCV | [MolmoWeb: Open Visual Web Agent and Open Data for the Open Web](https://link.springer.com/chapter/10.1007/978-3-032-37393-9_17) | 提供合成与人类示范轨迹及 GUI 感知数据，让策略依据截图和任务产生网页动作。 | 单次成功率与多次尝试成功率须分开；重试会改变使用成本与错误暴露。 |
| P30 · ECCV | [Keep It Simple: Multi-Key Episodic Memory Retrieval for Ultra-Long Video Understanding](https://arxiv.org/abs/2608.07663) | MERIT 建立问题无关的片段记忆，以事件、对话、对象等多键检索，再围绕候选片段补充时序上下文。 | 前端记忆遗漏的证据很难靠后续推理补回；应分开评检索召回和最终回答。 |

P30 的主会身份见 [ECCV 官方视频目录](https://eccv.ecva.net/Conferences/2026/Videos)，方法说明见 [MERIT 作者项目](https://choi-yeeun.github.io/MERIT/)。

### 3.6 基础表征、监督机制与资源效率

**观察：**基础模型并没有使表征研究终结。监督如何分配、性能由什么产生、能否在设备上持续适应，仍是具体且可检验的问题。

| 编号与会议 | 论文 | 核心内容 | 阅读边界 |
|---|---|---|---|
| P31 · CVPR | [Vision Transformers Need More Than Registers](https://openaccess.thecvf.com/content/CVPR2026/html/Shi_Vision_Transformers_Need_More_Than_Registers_CVPR_2026_paper.html) | 分析 ViT 利用背景 patch 聚合全局语义的捷径，并选择性地将 patch 特征汇入 CLS token。 | 机制解释来自论文分析；应核查不同训练目标和模型规模是否一致成立。 |
| P32 · ECCV | [ExPLoRe: Expert Patch-Level Loss Routing for Multi-objective Masked Image Modeling](https://link.springer.com/chapter/10.1007/978-3-032-37314-4_16) | 将 Soft MoE 路由权重作为逐 patch 损失系数，按内容分配 token 蒸馏、CLS 对齐与像素重建监督。 | 对 SLAM 的启发是监督可信度可随区域变化，但分类与分割实验不能直接证明几何收益。 |
| P33 · CVPR | [Rethinking Dataset Distillation: Hard Truths about Soft Labels](https://openaccess.thecvf.com/content/CVPR2026/html/Dey_Rethinking_Dataset_Distillation_Hard_Truths_about_Soft_Labels_CVPR_2026_paper.html) | 区分硬标签、固定软标签和大量软标签，指出某些评测下教师信息与计算预算掩盖了数据子集质量的差别，并提出计算适配方案。 | 不能据此断言所有数据蒸馏无效；关键是监督信息与计算量受控的比较。 |
| P34 · ECCV | [LANCE: Low Rank Activation Compression for Efficient On-Device Continual Learning](https://arxiv.org/abs/2509.21617) | 复用一次性标定的低秩激活子空间，并为连续任务分配正交子空间，以降低端侧学习的存储负担。 | 激活存储压缩率不是总内存压缩率，也不等于同幅加速；实验主要是分类设置。 |

P34 的录用记录见 [ECCV 官方视频目录](https://eccv.ecva.net/Conferences/2026/Videos)，实现见 [LANCE 作者仓库](https://github.com/mapolinario94/LANCE)。

### 3.7 数据与评测：从总分转向可定位的失效机制

**观察：**这些论文给出的共同提醒是：语言合理、视觉漂亮、平均分高，分别都不足以证明物理正确、证据忠实或开放环境可靠。

| 编号与会议 | 论文 | 核心内容 | 阅读边界 |
|---|---|---|---|
| P35 · CVPR | [PhysInOne: Visual Physics Learning and Reasoning in One Suite](https://openaccess.thecvf.com/content/CVPR2026/html/Zhou_PhysInOne_Visual_Physics_Learning_and_Reasoning_in_One_Suite_CVPR_2026_paper.html) | 提供覆盖多类物理现象的合成动态场景和视频，同时标注几何、运动、物理属性与文本，支持生成、预测和属性估计。 | 合成数据提供密集真值，但迁移到真实传感器与复杂物理交互仍需验证。 |
| P36 · CVPR | [QUANTIPHY: A Quantitative Benchmark Evaluating Physical Reasoning Abilities of Vision-Language Models](https://openaccess.thecvf.com/content/CVPR2026/html/Puyin_QUANTIPHY_A_Quantitative_Benchmark_Evaluating_Physical_Reasoning_Abilities_of_Vision-Language_CVPR_2026_paper.html) | 用带数值真值的视频任务评估尺寸、速度与加速度；发现受测 VLM 的合理叙述与数值正确性存在差距。 | 任务提供某项物理量作为先验，不能视为任意单目视频中的无条件米制恢复。 |
| P37 · CVPR | [From Indoor to Open World: Revealing the Spatial Reasoning Gap in MLLMs](https://openaccess.thecvf.com/content/CVPR2026/html/Wu_From_Indoor_to_Open_World_Revealing_the_Spatial_Reasoning_Gap_CVPR_2026_paper.html) | OSI-Bench 利用双目、LiDAR、IMU/GPS 产生室外度量真值，检查空间关系、尺度与运动推理，并分析语言先验依赖。 | 真值采集使用传感器，不应误写为所有传感器都作为被测模型的推断输入。 |
| P38 · CVPR | [Fine-Grained Multi Image Object Hallucination Benchmark](https://openaccess.thecvf.com/content/CVPR2026/html/Min_Fine-Grained_Multi_Image_Object_Hallucination_Benchmark_CVPR_2026_paper.html) | MIOH 将对象存在、数量、属性、位置与不同多图推理模式交叉组合，控制上下文规模、感知难度和偏差。 | 应定位跨图整合与感知各自的失败；一个幻觉总分容易掩盖任务差异。 |
| P39 · ECCV | [DynEval: Holistic Evaluations of T2I Generative Models in the Wild](https://arxiv.org/abs/2607.11199) | 以结构化语义与图像质量推理构建数据并蒸馏评价器，分析多个生成模型和细分能力。 | 教师模型、提示分布和人工标注仍影响评价；总体相关性不能保证每个子项准确。 |
| P40 · ECCV | [SpecV: Specification Verification for Robust Unified Multimodal Evaluation](https://link.springer.com/chapter/10.1007/978-3-032-37029-7_5) | 将任务要求分成可核验的原子、二元规格，结合去重与可验证性筛选，降低整体打分的不稳定。 | 规格覆盖不全、生成错误或裁判失误仍可能影响结论。 |
| P41 · CVPR | [Your One-Stop Solution for AI-Generated Video Detection](https://openaccess.thecvf.com/content/CVPR2026/html/Ma_Your_One-Stop_Solution_for_AI-Generated_Video_Detection_CVPR_2026_paper.html) | AIGVDBench 扩大视频生成器覆盖，并系统比较检测器，研究生成内容鉴别。 | 需要区分已知生成器、未知生成器与压缩后泛化；有限数据上的高分不是永久通用鉴伪能力。 |

P39 的主会身份见 [ECCV 官方视频目录](https://eccv.ecva.net/Conferences/2026/Videos)，补充说明见 [DynEval 作者项目](https://vcl-iisc.github.io/dyneval/)。

### 3.8 真实条件、垂直领域与计算成像

**观察：**应用方向的有价值变化，常来自任务特有的观测、监督或物理约束，而不只是替换成更大的通用模型。

| 编号与会议 | 论文 | 核心内容 | 阅读边界 |
|---|---|---|---|
| P42 · CVPR | [Robust Promptable Video Object Segmentation](https://openaccess.thecvf.com/content/CVPR2026/html/Lee_Robust_Promptable_Video_Object_Segmentation_CVPR_2026_paper.html) | MoGA 利用跨帧对象记忆对适配做条件化，并引入真实恶劣条件下的可提示视频分割评测。 | 对象级适配是否保持长期一致性值得分析；有限恶劣条件数据不代表所有真实退化。 |
| P43 · CVPR | [MedGRPO: Multi-Task Reinforcement Learning for Heterogeneous Medical Video Understanding](https://openaccess.thecvf.com/content/CVPR2026/html/Su_MedGRPO_Multi-Task_Reinforcement_Learning_for_Heterogeneous_Medical_Video_Understanding_CVPR_2026_paper.html) | 汇集多源医学视频指令，通过奖励归一化和医学模型评分改善异构任务上的强化学习。 | 应核查评分模型偏差与跨数据源泛化；基准收益不等同临床获益。 |
| P44 · ECCV | [MedSynapse-V: Bridging Visual Perception and Clinical Intuition via Latent Memory Evolution](https://link.springer.com/chapter/10.1007/978-3-032-37550-6_32) | 用解剖先验生成潜在记忆，以区域遮蔽奖励筛选记忆，再通过教师—学生对齐内化知识。 | 遮蔽奖励不等于临床因果证据；实际适用性仍需跨中心、跨设备验证。 |
| P45 · CVPR | [GeoViS: Geospatially Rewarded Visual Search for Remote Sensing Visual Grounding](https://openaccess.thecvf.com/content/CVPR2026/html/Zhang_GeoViS_Geospatially_Rewarded_Visual_Search_for_Remote_Sensing_Visual_Grounding_CVPR_2026_paper.html) | 将遥感定位组织成树状搜索和推理，利用局部视觉证据逐步修正地理空间假设。 | 在相同总计算预算下比较，并分析小目标漏检和错误搜索路径。 |
| P46 · CVPR | [Coded-E2LF: Coded Aperture Light Field Imaging from Events](https://openaccess.thecvf.com/content/CVPR2026/html/Tsuchida_Coded-E2LF_Coded_Aperture_Light_Field_Imaging_from_Events_CVPR_2026_paper.html) | 通过编码孔径与静止事件相机，从事件信息恢复光场，并以真实硬件验证成像设计。 | 此处“4D 光场”表示光线的空间—角度参数，不是三维场景随时间变化的 4D 重建。 |
| P47 · ECCV | [Event-Driven Motion Deblurring via Trajectory-Based Kernel Reconstruction](https://link.springer.com/chapter/10.1007/978-3-032-37314-4_14) | 从事件估计像素运动轨迹，构造空间变化的模糊核，再结合物理数据一致性和展开网络恢复图像。 | 显式成像模型使约束更清楚，但事件噪声、轨迹精度与跨设备适应仍需检验。 |

以上共 **47 篇代表论文：CVPR 27 篇、ECCV 20 篇**。这一配比由本次选题与证据可得性决定，不代表两届会议在各方向上的实际份额。

## 4. 把不同方向串起来：哪些判断最值得保留

### 4.1 “统一”正在发生于表示、状态和任务接口

Cheers 将理解与生成放进共享系统，D4RT 用查询接口关联不同几何任务，Point4Cast 通过一个演化状态连接重建与预测，SLARM 将几何、运动和语言语义相连。这些工作共同支持一个判断：**共享的中间表示能否保留各任务需要的证据，是比简单共用网络更具体的研究问题。**语义需要抽象不变性，几何需要精确位置，生成需要保留细节，长期跟踪需要身份连续；这些要求可能冲突。[Cheers](https://arxiv.org/abs/2603.12793)、[D4RT](https://d4rt-paper.github.io/)、[Point4Cast](https://openaccess.thecvf.com/content/CVPR2026/html/Liu_Point4Cast_Streaming_Dynamic_Scene_Reconstruction_and_Forecasting_CVPR_2026_paper.html)

对新工作的启示是：应明确什么被共享、什么被分离，以及这种选择解决了哪种任务冲突。只展示一个模型输出了更多结果，尚不足以说明统一表示本身有价值。

### 4.2 扩大有效信息与减少无效计算同时存在

VGGT-ohm、SAM 3D 强调数据规模、标注流程与训练配方；SmartVL、EFlow、RegVGGT 研究怎样把算力集中到有用信息上。两类路线可以互相补充。应把效率至少拆成 **训练成本、推断延迟、工作记忆、历史存储和适应成本**，并比较质量—成本曲线，不能用一个 FLOPs 或单个压缩率概括。[VGGT-ohm](https://openaccess.thecvf.com/content/CVPR2026/html/Wang_VGGT-ohm_CVPR_2026_paper.html)、[SmartVL](https://link.springer.com/chapter/10.1007/978-3-032-37359-5_12)、[EFlow](https://link.springer.com/chapter/10.1007/978-3-032-37314-4_17)

CVPR 2026 还引入了实验性的作者计算量报告机制，反映计算透明度受到关注；官方明确这些报告不向审稿人展示，也不影响录用，不能把它说成“低算力论文更容易中”。[官方作者指南](https://cvpr.thecvf.com/Conferences/2026/AuthorGuidelines)

### 4.3 学习先验与几何估计结构继续结合

MERG3R 使用基础模型与 BA，Scal3R 使用相对位姿查询与位姿图，FILT3R 将滤波结构放进潜在状态更新，SLAM-Former 将跟踪、建图与全局修正共同建模。它们说明，坐标、尺度、回环和不确定性仍需要明确处理。现有样本支持“几何约束与学习方法继续融合”，不足以支持“传统 SLAM 已被替代”。[MERG3R](https://openaccess.thecvf.com/content/CVPR2026/html/Cheng_MERG3R_A_Divide-and-Conquer_Approach_to_Large-Scale_Neural_Visual_Geometry_CVPR_2026_paper.html)、[Scal3R](https://arxiv.org/html/2609.04201v1)、[FILT3R](https://arxiv.org/html/2603.18493v2)

特别要避免以下概念混淆：

| 论文中的表述 | 不能自动推出 | 需要另外提供的证据 |
|---|---|---|
| 前馈、快速、可查询 | 严格因果、低首帧等待 | 编码阶段是否使用未来帧，何时能产生输出 |
| 能处理长视频 | 长时间无漂移、身份不丢失 | 连续跟踪时长、重访恢复、误差随时长曲线 |
| 历史 token 大幅压缩 | 总内存恒定 | GPU 工作状态、CPU 地图、历史缓存各自的增长 |
| 新视角渲染质量高 | 相机准确、物质点对应正确 | 位姿、几何与轨迹分别评价 |
| 生成结果物理合理 | 学到了可用于外推的动力学 | 数值物理量、干预与未见条件预测 |
| 无需额外训练 | 无优化开销、无底座训练成本 | 底座来源、推断优化次数和总体延迟 |

上表是阅读与实验设计准则；P15、P19、P22、P25、P36 分别提供了对应的具体案例。

### 4.4 数据质量与评价协议本身成为研究贡献

SAM 3D 的数据流程、PhysInOne 的物理真值、MolmoWeb 的开放轨迹，以及 MIRA、OSI-Bench、MIOH、SpecV 的诊断设计，说明“训练和测试究竟提供了什么信息”需要被显式描述。数据蒸馏分析尤其提醒我们：当教师软标签和训练计算未被控制时，看起来属于数据构造的收益可能来自其他因素。[SAM 3D](https://openaccess.thecvf.com/content/CVPR2026/html/Chen_SAM_3D_3Dfy_Anything_in_Images_CVPR_2026_paper.html)、[数据蒸馏分析](https://openaccess.thecvf.com/content/CVPR2026/html/Dey_Rethinking_Dataset_Distillation_Hard_Truths_about_Soft_Labels_CVPR_2026_paper.html)、[SpecV](https://link.springer.com/chapter/10.1007/978-3-032-37029-7_5)

因此，小团队也可以从严谨的诊断、监督质量控制、数据机制和推断策略切入。这里是研究路径建议，不是录用成功的保证；仍需证明问题具有普遍性，且强基线不能以更简单的方法解决。

### 4.5 生成、感知与行动需要各自的验证闭环

可以将相关研究理解为：观测提供证据，状态表示组织证据，推理或预测利用状态，行动产生新的观测。不同论文通常只覆盖其中一部分。PhysRAG 的物理视频生成、Point4Cast 的几何预测、NitroGen 的游戏动作、MolmoWeb 的网页执行，都有明确任务范围，不能合并成“通用世界模型已经成熟”的结论。[PhysRAG](https://arxiv.org/abs/2606.26916)、[NitroGen](https://openaccess.thecvf.com/content/CVPR2026/html/Magne_NitroGen_An_Open_Foundation_Model_for_Generalist_Gaming_Agents_CVPR_2026_paper.html)、[MolmoWeb](https://link.springer.com/chapter/10.1007/978-3-032-37393-9_17)

更扎实的研究命题应明确：状态表示的哪项改善，通过哪个机制，提升哪种下游任务；同时保留对应的感知误差和行动失败分析。

## 5. 面向 SLAM、三维与流式 4D 的选题建议

以下是**基于本次文献的研究假设**，并未完成全面新颖性检索或实验验证。若沿用本笔记本已有的“单目 RGB、未知相机位姿、动态场景、长序列或流式输入”方向，建议优先考虑前两项；多传感器方向需要额外数据条件。

| 优先级 | 具体问题 | 为什么值得验证、直接相关论文 | 最小可检验方案与停止条件 |
|---|---|---|---|
| 高 | **区分真实状态变化与观测退化，可靠地更新记忆** | FILT3R 明确存在固定测量噪声和不可靠候选状态的问题；RayMap3R、Unblur-SLAM 分别处理动态污染与模糊。 | 先划分清晰/模糊、静态/动态、可见/遮挡组合，分析状态增益与实际误差的关系；与固定阈值、简单置信门控和不更新基线比较。如果复杂估计不能稳定优于简单门控，应停止增加模块。 |
| 高 | **在明确的记忆预算下保留有助于重访和跟踪的证据** | GCT、RegVGGT 已压缩历史，MERIT 则展示按需检索路径；机会在记忆选择的任务价值，而非泛泛“加入 memory”。 | 固定 GPU 工作记忆和历史存储预算，比较滑窗、均匀保留、显著性和基于重访价值的选择；测长遮挡重现、回环和最差序列。若收益只来自存储更多帧，不成立。 |
| 中高 | **全局校正后，位姿、尺度与动态身份如何保持一致** | Scal3R、LASER、SLAM-Former 分别覆盖位姿图、跨窗尺度与前后端校正，但组合后仍需定义动态状态如何同步变化。 | 构造同一场景重访和移动对象干扰实验，分别报告校正前后静态地图误差、轨迹连续性和身份交换。如果只降低 ATE 却破坏动态轨迹，需重新定义目标。 |
| 中 | **把可查询 4D 状态用于遮挡恢复或主动观测** | D4RT 提供统一查询接口，Point4Cast 提供演化状态与未来预测。 | 固定底座，检验预测是否确实改善重现定位或观测选择；与不预测、匀速预测比较。若只改善演示效果而无可重复任务收益，应收窄问题。 |
| 条件性 | **含噪、异步与缺失传感器条件下的米制 4D** | Any4D 的理想传感器设定给出明确迁移问题。 | 分离时间偏移、标定误差、漂移和缺失；比较纯 RGB、理想融合与受扰融合。如果只有理想条件有收益，尚不能支持真实系统价值。 |

### 5.1 对有限训练预算，先定位失败再决定是否训练

一条可执行的研究顺序是：

1. **选一个可获得且版本明确的底座。**记录论文、代码、权重和数据版本；原文链接并不等于所有资源都已可用。
2. **先复现一个稳定失效现象。**例如长遮挡后的身份漂移、模糊帧导致状态污染、回环后动态轨迹跳变。要在多条序列上复现，避免围绕单个演示设计方法。
3. **建立能解释现象的简单基线。**滑窗、固定门控、位姿图校正、均匀记忆选择等往往比额外网络更适合检验机制。
4. **再选择推断干预、小规模微调或训练新模块。**LASER、FILT3R、RayMap3R 提供推断期改进路径；Scal3R 提供少量参数训练的例子。无需额外训练本身不是创新，关键是修复什么失效。[LASER](https://openaccess.thecvf.com/content/CVPR2026/html/Ding_LASER_Layer-wise_Scale_Alignment_for_Training-Free_Streaming_4D_Reconstruction_CVPR_2026_paper.html)、[Scal3R](https://arxiv.org/html/2609.04201v1)
5. **最后才扩大数据与实验规模。**如果核心机制未成立，扩展实验只会增加成本。

### 5.2 建议统一报告的实验口径

| 维度 | 最低应说明的内容 |
|---|---|
| 输入信息 | 单目/多目、已知或预测内参、是否有深度/IMU、绝对尺度来自何处 |
| 时间条件 | 严格因果、固定延迟还是离线；是否预先运行全片位姿、深度或跟踪模型 |
| 位姿与尺度 | ATE/RPE 的具体定义、SE(3) 或 Sim(3) 对齐、全局一次对齐还是分段对齐；不能用频繁重对齐掩盖漂移 |
| 动态对应 | 跟踪的是同一物理点还是对象中心；轨迹时长、遮挡跨度、重识别与可见性指标 |
| 几何与渲染 | 分开报告几何误差和渲染质量，避免用画质替代真实对应精度 |
| 资源 | 设备、输入分辨率、帧数、工作显存、历史存储、首帧等待、平均与高分位延迟 |
| 鲁棒性 | 不同动态比例、低纹理、快速运动、模糊、光照变化下的分组结果和失败序列 |
| 监督公平性 | 是否使用额外教师、伪标签、未来帧或测试视频适配；把这些信息与计算成本计入比较 |

**新颖性风险较高的宽泛表述：**“给基础模型加记忆”“把离线模型变流式”“引入 Kalman 更新”“只保留少量 token”“把重建和跟踪结合”。P15–P27 已覆盖其中多个基本命题。更有辨识度的贡献应说明某种现有方案无法处理的条件、失败机制与可证伪假设，而不是仅改模块名称。

## 6. 推荐阅读顺序与使用方式

### 6.1 快速建立全局视野：四组对照阅读

| 顺序 | 论文组合 | 阅读目的 |
|---|---|---|
| 1 | P04 Foveated Reasoning → P05 SmartVL → P02 MIRA | 区分主动获取证据、分配计算和利用视觉中间步骤 |
| 2 | P09 Cheers → P07 ChordEdit → P10 EFlow | 区分统一模型、推断期编辑和从头训练少步生成器 |
| 3 | P14 VGGT-ohm → P15 D4RT → P17 Point4Cast | 从几何底座到可查询 4D，再到随时间更新的状态 |
| 4 | P37 OSI-Bench → P33 数据蒸馏分析 → P40 SpecV | 检查视觉依赖、监督公平性和评价可验证性 |

这些是推荐顺序，不是会议重要性排名。若只想先读一篇与现有研究最接近的工作，可从 **D4RT** 开始，再立即对照其是否需要完整视频，避免把离线接口直接迁移成流式假设。

### 6.2 面向 SLAM / streaming 4D 的深入阅读

建议主线为 **D4RT → Point4Cast → GCT → FILT3R → Scal3R → LASER → SLARM**；研究多传感器时加入 Any4D，研究真实退化时加入 Unblur-SLAM。

每篇统一记录六件事：**输入及时间条件、状态具体存什么、状态如何更新、世界坐标如何保持、失败机制、总计算与存储成本**。这样比按“模型名字—SOTA 数字”记笔记更容易找到可验证的问题。

可以先用一页对照表回答三件事，再决定复现顺序：

- 哪篇与目标设置真正一致，哪篇需要整段视频、已知位姿或额外传感器？
- 哪个失败现象有明确证据，哪些只是根据摘要提出的猜想？
- 改进能否在相同底座、数据与预算下成立；是否已有更简单的修复？

## 7. 检索口径与后续维护

- **收录依据：**先检查会议身份，再用摘要或方法说明归纳贡献；仅有标题的条目不用于推断方法细节。官方名录能确认录用，但不自动证明代码、权重和训练数据都已公开。
- **主要入口：**[CVPR 主会论文库](https://openaccess.thecvf.com/CVPR2026)、[ECCV 录用列表](https://eccv.ecva.net/Conferences/2026/AcceptedPapers)、[ECCV 官网及 Springer 分卷入口](https://eccv.ecva.net/Conferences/2026)。部分页面可能因网站访问策略无法直接读取；本文也使用这些一手页面的检索索引及作者公开版本交叉核对。
- **样本偏差：**为了贴近本笔记本，三维、动态场景和效率方向有所侧重。未系统覆盖全部人体、自动驾驶、检测、分割、遥感或医学子领域；没有给出全会主题百分比、机构排名或“增长最快”榜单。
- **证据强度：**官方会议信息、论文方法与本文研究判断分开处理；未将作者宣传中的“首次”“通用”“最优”直接作为独立确认的结论。摘要级阅读不足以支持完整的新颖性审查。
- **更新时优先核查：**正式出版标题是否变化；预印本修订是否引入额外训练数据；代码与权重是否对应论文版本；评测是否使用未来帧或整段视频预处理；数据和计算预算是否公平。

本笔记本中的进一步阅读：[动态长序列 4D 与 Point Tracking](../papers/streaming_4d_tracking_research_2026.md)、[长序列三维基础模型](../papers/long_sequence_3d_foundation_models.md)、[前馈 3DGS 综述](../papers/feedforward_3dgs_survey_2024_2026.md)。这些旧笔记具有各自的检索截止时间，引用其中论文时仍需核实其会议归属。
