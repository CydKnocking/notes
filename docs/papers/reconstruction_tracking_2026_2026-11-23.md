# 2026 年 3D / 4D 重建与点跟踪研究更新

调研截止：**2026-11-23（北京时间）**。面向：单目 RGB、未知相机位姿、动态场景、长序列 / 流式处理，以及低训练成本适配和伪标签生成。

## 0. 范围与阅读方式

本文是一次独立更新，不覆盖原有 `streaming_4d_tracking_research_2026.md`。主表以 **2026 年首次提交到 arXiv 的工作**为主，另列“2025 年首发、2026 年仍重要”的基线。覆盖场景几何重建、动态几何与运动联合估计、2D/3D 点跟踪、相关预测模型和数据集；不是对所有物体生成、人体重建、SLAM、NeRF/3DGS 论文的穷尽检索。

- 日期采用论文页面的 **v1 提交日期**；修订和代码发布单独说明。编号月份不一定等于实际提交月份，例如 TAP-Out 首发于 10 月 30 日，SceneBound 首发于 10 月 31 日。
- **★近期**表示 2026-10-19 至本次截止日首次公开；不表示此前的年内工作都已收录在旧笔记中。
- 原始依据为论文、作者项目页和官方仓库。重点核读了 π⁴、Track4D、3R-Adapter、SGAR 的方法与相关实验；其他条目主要为摘要、项目说明和已有笔记的定向复核，不能视为全部逐页精读。
- “代码可见”不等于已复现；“有权重入口”不等于已经完成下载和性能验收。未确认的发布状态明确写作“未核实”，不据此断言作者未开源。
- 会议录用信息只在查到作者或论文页面明确说明时列出；其余以预印本引用，不推测录用状态。本文不依据异构数据集和指标给出统一 SOTA 排名。

## 1. 先看结论：这轮最值得关注什么

| 优先级 | 工作 | 对我们最重要的变化 |
|---|---|---|
| 第一批运行 | **π⁴ / Pi4** | 统一几何、位姿、动态分割、2D/3D 跟踪；支持无序图像集合，已有代码和权重入口。应加入联合任务与伪标签教师候选。 |
| 第一批运行 | **ARROW** | 不是本月新论文，但开源状态必须更新：当前已有推理、权重和评测代码；无序动态观测设定非常相关。 |
| 第一批精读 | **3R-Adapter** | 把域迁移失败归因到跨视图关系退化，提供低成本适配与测试时适配路线。 |
| 第一批精读 | **SceneBound** | 对流式记忆 / 门控方法提出关键公平性问题：同等写入预算下，复杂策略是否优于均匀选帧？ |
| 第二批精读 | **Track4D** | 视频扩散骨干与 3D 轨迹表示结合；少量运动数据适配值得借鉴，但完整代码尚待发布。 |
| 第二批精读 | **SGAR / Zebra3D** | 从几何引导稀疏注意力和预训练模型转换入手扩展视图规模；适合讨论低成本长上下文。 |
| 特定设定 | **Tracktail / TAP-Out** | 分别针对标定多视图无深度 3D 跟踪、出视野 2D 跟踪；不能直接当作同输入条件的单目基线。 |
| 应用延伸 | **Video-Point Model（VPM）** | 将持久 3D 点轨迹监督用于多视图未来生成，并扩展机器人动作预测，直接联系此前讨论的“预测有什么用”。 |

上述判断是针对本项目的阅读 / 实验优先级，不是性能榜单。论文、代码和边界见下面各节。

## 2. 3D 重建：基础模型、长序列与低成本适配

这里的“3D”主要指几何 / 位姿恢复。能够在动态视频中运行，不自动意味着输出动态物体的持久点轨迹。

| 首发日期 | 论文与链接 | 输入、核心方法与输出 | 对我们的意义 / 边界 |
|---|---|---|---|
| 03-02 | [MERG3R: A Divide-and-Conquer Approach to Large-Scale Neural Visual Geometry](https://arxiv.org/abs/2603.02351) | 将大图像集合组织为重叠子集，调用预训练几何模型，再以相似变换与几何优化拼接。 | 无需重训的规模扩展基线；全局集合处理不能直接称为因果在线。[代码](https://github.com/LeoChengKX/MERG3R)。 |
| 03-03 | [LoGeR: Long-Context Geometric Reconstruction with Hybrid Memory](https://arxiv.org/abs/2603.03269) | 结合局部窗口与全局记忆，在分块处理中维持长上下文几何。 | 与长视频直接相关；要区分块内双向访问、块间状态和端到端延迟。 |
| 03-04 | [ZipMap: Linear-Time Stateful 3D Reconstruction with Test-Time Training](https://arxiv.org/abs/2603.04385) | 使用快速权重状态压缩上下文，实现线性规模重建。 | TTT 层本身是模型机制，不等于给任意模型免费添加无训练插件；主要双向配置与流式扩展应分开。[代码](https://github.com/haian-jin/ZipMap)。 |
| 03-19 | [FILT3R: Latent State Adaptive Kalman Filter for Streaming 3D Reconstruction](https://arxiv.org/abs/2603.18493) | 在潜在状态更新中加入自适应滤波，用不确定性控制新旧信息融合。 | training-free 状态更新的重要对照；09-05 修订不应计作新的九月论文。 |
| 03-21 | [RayMap3R: Inference-Time RayMap for Dynamic 3D Reconstruction](https://arxiv.org/abs/2603.20588) | 在推理时利用射线 / 图像分支的差异抑制动态干扰，结合状态平滑与尺度处理。 | 面向动态环境中的稳定几何；相机轨迹改善不等于物体点跟踪改善。 |
| 05-14 | [VGGT-Ω](https://arxiv.org/abs/2605.15195) | 扩展视觉几何基础模型及其训练 / 推理能力。 | 几何骨干与高质量几何教师候选；10-25 为版本更新。[官方仓库](https://github.com/facebookresearch/vggt-omega)。 |
| 05-16 | [Rethinking the State Update Gate for Long-Sequence Recurrent 3D Reconstruction](https://arxiv.org/abs/2605.16981) | 从帧级特征变化设计状态更新门控，减少冗余更新。 | 与 FILT3R、SceneBound 放在同一写入预算下比较；11-06 的 v4 不是首次公开。论文页标注 NeurIPS 2026。 |
| 05-22 | [HorizonStream: Long-Horizon Attention for Streaming 3D Reconstruction](https://arxiv.org/abs/2605.23889) | 长程线性注意力与局部注意力结合，以紧凑状态处理远长于训练窗口的输入。 | 强流式几何参考；需独立检查动态身份保持。10-24 修订；论文页标注 NeurIPS 2026。 |
| 05-28 | [Déjà View: Looping Transformers for Multi-View 3D Reconstruction](https://arxiv.org/abs/2605.30215) | 共享参数的循环 Transformer，通过推理迭代次数调节计算与几何质量。 | 可作为自适应计算骨干；网络层迭代不等于视频时间上的因果递推。[代码](https://github.com/nv-tlabs/dvlt)，官方标注 NeurIPS 2026 Oral。 |
| 07-20 | [MoGe-3: Fine-Detail Monocular Geometry Estimation with Self-Guided Sparse Volumetric Refinement](https://arxiv.org/abs/2607.17967) | 单图粗点图提升到稀疏体素壳，再进行三维局部几何细化，改善细杆和深度边界。 | 对抓取接触点、边界点的几何伪标签尤其有意义；不单独保证跨帧一致性。[项目](https://qft-333.github.io/moge3page/)，[代码](https://github.com/microsoft/MoGe)。 |
| 09-04 | [BLASt3R: Bundle Adjustment of Any Image Set with Multi-View Matching and Monocular Priors](https://arxiv.org/abs/2609.05210) | 多视图对应、单目先验与 BA 结合，可处理图像集合。 | 无序静态重建 / 几何校正强对照；静态特征轨迹不等于动态材料点轨迹。[代码](https://github.com/naver/blast3r)。 |
| 10-01 | [CLoSeR: Closing the Loop for Long-Context Streaming Reconstruction](https://arxiv.org/abs/2610.01927) | 为长上下文重建引入检索、回环窗口和位姿图校正。 | 回访一致性比单纯帧数更贴近长序列价值；动态对象的回访关联仍需另测。 |
| 10-08 | [Zebra3D: Efficient Hybrid Foundation Models For Scalable 3D Reconstruction](https://arxiv.org/abs/2610.12727) | 按层使用线性 / 稀疏注意力；支持闭式拟合的免训练转换，以及可选蒸馏式后训练。 | 与“只有有限微调预算”高度相关。公开实现和权重本轮未核实。 |
| ★10-31 | [SceneBound: How Much Should a Streaming 3D Reconstruction Model Remember?](https://arxiv.org/abs/2611.00756) | 根据场景空间覆盖决定记忆写入，以重解码的历史帧检测漂移并组织子地图。 | 关键对照是同等写入数量的均匀采样；空间覆盖增长时，存储仍可能增长。代码本轮未核实。 |
| ★11-09 | [3R-Adapter: Retrieval, Rewiring, and Refinement for Efficient Adaptation of 3D Reconstruction Model](https://arxiv.org/abs/2611.11964) | 冻结骨干，通过检索、关系调整与一致性细化恢复跨视图几何关系。 | 域迁移、低照度、人体场景和 TTA 值得精读。[实现](https://github.com/PKU-OV3-LAB/3R-Adapter)可见；论文页标注 NeurIPS 2026 Spotlight。 |
| ★11-12 | [Kosmo-GFM: A Production-Ready Geometry Foundation Model](https://arxiv.org/abs/2611.16840) | 几何基础模型配合几何优化引擎和重建数据，支持相机、深度、对应及后续 3D/4D 表示。 | 系统与数据闭环参考；“Production-Ready”是作者命名，不代表经过本项目的部署验证。代码本轮未核实。 |
| ★11-18 | [Infer3D: Inverse Generative Modeling Enables Robust 3D Reconstruction](https://arxiv.org/abs/2611.25061) | 借助生成模型的潜在空间进行逆向优化，以几何模型约束多视图一致性。 | 推理时计算换 OOD 鲁棒性的路线；不是现成动态点跟踪器。代码本轮未核实。 |
| ★11-18 | [Accord: Universal Online Metric Localization and Dense Mapping from one Camera and an IMU](https://arxiv.org/abs/2611.25279) | 将单相机、IMU、基础模型深度和几何约束结合，在线恢复尺度一致的稠密地图。 | **额外使用 IMU**，不能作为纯单目 RGB 的同条件方法；适合系统应用参考。 |
| ★11-19 | [SGAR: Feed-Forward 3D Reconstruction via Sparse Geometry-Guided Attention](https://arxiv.org/abs/2611.26493) | 用几何接近性指导稀疏注意力，减少多视图重建中的全局交互成本。 | 相比从头训练更贴近现有骨干微调；仍需数据与训练，不能标为 training-free。代码本轮未核实。 |

## 3. 动态 4D 重建与重建—跟踪联合模型

重点区分两类输出：**随时间变化的几何 / 渲染表示**，以及**同一个物理点在多个时刻的位置**。前者不必然包含后者。

| 首发日期 | 论文与链接 | 核心工作 | 输入 / 评价边界 |
|---|---|---|---|
| 01-14 | [V-DPM: 4D Video Reconstruction with Dynamic Point Maps](https://arxiv.org/abs/2601.09499) | 以动态点图联合表示场景几何和运动。 | 本项目已有经验，应保留为年初联合模型基线。[代码](https://github.com/eldar/vdpm)。 |
| 02-04 | [TrajVG: 3D Trajectory-Coupled Visual Geometry Learning](https://arxiv.org/abs/2602.04439) | 通过轨迹、点图和相机之间的约束耦合视觉几何，利用真实视频上的跟踪监督。 | 值得看伪标签如何参与训练、静态锚点如何约束几何，而非只看总指标。 |
| 02-10 | [4RC: 4D Reconstruction via Conditional Querying Anytime and Anywhere](https://arxiv.org/abs/2602.10094) | 视频编码后，以条件查询读出源位置到目标时刻的几何 / 对应。 | 其流式版本 S-4RC 与主模型协议应分开；不能只因支持查询就认定因果。[代码](https://github.com/Luo-Yihang/4RC)。 |
| 02-15 | [Flow4R: Unifying 4D Reconstruction and Tracking with Scene Flow](https://arxiv.org/abs/2602.14021) | 从两视图几何与场景流出发，组合局部运动、相机和全局表示。 | 几何—运动联合约束强相关；局部精度与长程积分漂移需要分别测量。 |
| 03-28 | [Complet4R: Geometric Complete 4D Reconstruction](https://arxiv.org/abs/2603.27300) | 利用跨时间上下文恢复更完整的动态几何，包括当前视图不可见部分。 | 利用其他已观察帧补全，与真正预测未发生的未来不同。 |
| 07-12 | [OmniX: Any-view and Any-time 4D Reconstruction via Feed-forward Trajectory Fields](https://arxiv.org/abs/2607.10840) | 用轨迹场统一跨视角、跨时间的动态恢复。 | 可处理复杂采样，但时间信息 / 视频标识仍是设定的一部分；“不连续”不等于“完全不需要时间”。[代码](https://github.com/yanqinJiang/OmniX)。 |
| 08-18 | [UniQuery4R: Unified 4D Scene Reconstruction from a Single Query](https://arxiv.org/abs/2608.17283) | 用统一查询组织几何、对应、深度和运动输出。 | 应核对输出所在坐标系、跨窗口查询和不可见点的定义；代码本轮未核实。 |
| 08-20 | [Gallileo-4D: Frozen Backbone Ensemble for Dynamic 4D Reconstruction](https://arxiv.org/abs/2608.19743) | 用冻结模型与推理集成改进动态几何，避免大规模训练。 | 低成本参考；属于特定评测 / 技术报告语境，不能将集成收益直接外推到所有长视频。 |
| 09-08 | [Point4D: Long-range 4D Motion Reconstruction](https://arxiv.org/abs/2609.09145) | 通过三维查询和跨片段关联恢复长程运动，配合片段之间的几何对齐。 | 直接对应本项目；要拆开尺度 / 位姿误差与真正点身份漂移。[代码](https://github.com/point-4d/Point4D)。 |
| 09-24 | [TrackEverything: Long Horizon Dense Tracking via De-Duplicating 3D Scene Representations](https://arxiv.org/abs/2609.30222) | 利用三维场景表示去重，维护长程稠密轨迹，减少反复保存同一表面的代价。 | 依赖上游世界坐标点图；存储随新几何增长，不等于严格常数内存。代码现状本轮未核实。 |
| 10-01 | [ARROW: Arbitrary Reconstruction and Tracking of 4D Observation in the Wild](https://arxiv.org/abs/2610.01314) | 用源 / 目标 / 参考观测查询组织重建与跟踪，面向任意排列的动态观测。 | 无序集合重点基线；查询观测之间的运动不等于预测未知未来。[代码与权重入口](https://github.com/ifradlin/arrow)。 |
| 10-01 | [Dyna3: VLM-Guided Training-Free 4D Reconstruction via Depth Foundation Models](https://arxiv.org/abs/2610.01286) | 基于深度基础模型、视觉语言引导和分割，构建静态背景与逐帧动态几何。 | 适合免训练几何系统；逐帧动态点云本身不提供可靠的持久点身份。 |
| 10-01 | [SCOPE-4D: Endoscopic 4D Geometry Foundation Models](https://arxiv.org/abs/2610.02343) | 面向内窥镜，联合恢复几何、相机和组织运动，并提供专门数据。 | 强形变、反光和遮挡的域外验证参考；研究结果不等于临床可部署。 |
| 10-02 | [MoSE3: Learning World-Space SE(3) at Every Pixel](https://arxiv.org/abs/2610.03716) | 冻结几何骨干，在像素层面估计世界坐标刚体运动及相关结构。 | 对机械臂操作中的物体 / 部件运动有价值；局部刚性假设与非刚体点轨迹需区分。[代码](https://github.com/mose3-tracker/MoSE3)。 |
| 10-07 | [DynStream: Online Streaming 4D Gaussian Reconstruction of Dynamic Worlds from Unposed Video](https://arxiv.org/abs/2610.09720) | 未知位姿视频的窗口式动态高斯重建，结合局部恢复、对齐与融合。 | 渲染导向的在线 4D 基线；高 PSNR 不能替代点轨迹身份正确性。 |
| ★11-17 | [π⁴: A Foundation Model for 4D Scene Geometry and Motion](https://arxiv.org/abs/2611.23144) | 从单图、无序图像或视频统一输出几何、相机、动态区域和 2D/3D 对应。 | 最值得立即加入的联合教师候选；注意其 3D 跟踪的提升方式及遮挡局限，见第 6 节。[代码](https://github.com/yyfz/Pi4)。 |
| ★11-19 | [OffBeat: Multicoset Sampling for 4D Capture Beyond the Camera Frame Rate](https://arxiv.org/abs/2611.26347) | 利用多相机错时采样及时间约束，提高动态捕获 / 重建的时间分辨率。 | 是采集策略与 4D 表示联合设计，非普通单目输入；论文中的模拟错时实验不可直接当作真实硬件部署。 |

## 4. 点跟踪：二维、三维与特殊传感器

π⁴、ARROW、Point4D、4RC 等已经在上一节列出，不重复计作独立新论文。

| 首发日期 | 论文与链接 | 类型与核心方法 | 对我们的意义 / 边界 |
|---|---|---|---|
| 02-04 | [CoWTracker: Tracking by Warping instead of Correlation](https://arxiv.org/abs/2602.04877) | 2D；用特征扭曲组织稠密点跟踪，预测可见性 / 置信度。 | 高质量 2D 教师候选，也是 π⁴ 运动分支的重要来源；离线窗口上下文不能误记为因果。[代码](https://github.com/facebookresearch/cowtracker)。 |
| 03-05 | [TAPFormer / TTAPFormer](https://arxiv.org/abs/2603.04989) | RGB 与事件信息结合的点跟踪。 | 快速运动 / 模糊条件参考；增加事件输入，不适合作为纯 RGB 的直接公平对照。 |
| 03-12 | [Real-World Point Tracking with Verifier-Guided Pseudo-Labeling（Track-On-R）](https://arxiv.org/abs/2603.12217) | 2D；通过验证器选择可靠伪标签，利用真实视频训练跟踪器。 | 与用户提出的“模型提供伪真值监督”最直接相关；验证器和学生的时序访问权限应分别说明。[代码](https://github.com/gorkaydemir/track_on)。 |
| 03-18 | [M2P: Improving Visual Foundation Models with Mask-to-Point Weakly-Supervised Learning for Dense Point Tracking](https://arxiv.org/abs/2603.17813) | 2D；把分割级监督转化为点级学习信号，适配视觉基础特征。 | 弱标注和低成本适配路线；分割内部的点身份歧义仍值得关注。 |
| 04-12 | [TAPNext++: What's Next for Tracking Any Point (TAP)?](https://arxiv.org/abs/2604.10582) | 2D；关注因果递推、长程跟踪和重检测。 | 适合作为在线教师 / 学生参考；不能只与使用未来帧的离线方法比较速度与精度。 |
| 05-12 | [TrackCraft3R: Repurposing Video Diffusion Transformers for Dense 3D Tracking](https://arxiv.org/abs/2605.12587) | 3D；将视频扩散 Transformer 改造为轨迹估计器，结合外部几何。 | 与 Track4D 对读，比较表示、训练数据及几何先验；LoRA 不自动意味着小显存或低总算力。[代码](https://github.com/cvlab-kaist/TrackCraft3r)。 |
| 09-13 | [S3-Tracker: Self-Supervised Surgical Tissue Tracking With Contrastive Random Walks](https://arxiv.org/abs/2609.14313) | 手术场景的自监督组织点跟踪。 | 可借鉴形变区域的对应学习；属于短篇工作，证据规模应与完整论文区别对待。 |
| 09-27 | [3D Point Tracking with State Space Models](https://arxiv.org/abs/2609.34035) | 3D；以状态空间模型组织轨迹时序信息。 | 与长程高效跟踪相关；需核对深度来源、数据划分和评测协议后再判断优势。 |
| ★10-30 | [TAP-Out: Tracking Any Point in 360° via Outpainting](https://arxiv.org/abs/2611.00406) | 2D；通过视频向外补全、分割及视角变换处理出视野跟踪。 | 解决 OOV 的新路线；生成的视野外内容不是观测真值，不能无筛选用于监督。[代码](https://github.com/finlay-hudson/TAP-Out)，论文页标注 BMVC 2026。 |
| ★11-05 | [Selective Event Evidence and Persistent Temporal Priors for Event-Based Point Tracking（SEPT）](https://arxiv.org/abs/2611.07713) | 事件点跟踪；选择可靠事件证据，并跨窗口传递时间先验。 | 可靠性加权与跨窗口运动先验可迁移思考，但输入不是 RGB；发布完整性未核实。 |
| ★11-11 | [Track4D: Representing Dense 3D Tracking for Video Diffusion Models](https://arxiv.org/abs/2611.15287) | 3D；研究适合视频扩散模型的稠密轨迹表示，并进行 LoRA 适配。 | 少量运动数据训练值得关注；仍依赖外部几何，完整代码待发布。论文页标注 NeurIPS 2026。 |
| ★11-19 | [Tracktail: Multi-View 3D Point Tracking without Depth Input](https://arxiv.org/abs/2611.26779) | 3D；融合多视图视频特征，直接预测三维轨迹和可见性，不要求深度输入。 | **要求相机标定及三维查询**，不是无位姿单目跟踪；适合多相机离线教师。[项目](https://ai-hhmi.github.io/tracktail/)，[代码](https://github.com/AI-HHMI/tracktail)。 |

## 5. 轨迹预测、世界模型与新增数据

这些工作回答“重建 / 跟踪的表示还能做什么”，但评测目标与观测区间内的重建不同。预测有多解性，不能以生成的合理轨迹代替真实运动标签。

| 首发日期 | 论文 / 数据 | 做什么 | 与本项目的关系 |
|---|---|---|---|
| 01-07 | [PointWorld](https://arxiv.org/abs/2601.03782) | 用点空间动力学建模动作作用下的未来变化，联系机器人控制。 | 从恢复轨迹走向动作条件预测；输入和控制设定不能直接简化为单目无位姿视频。[项目](https://point-world.github.io/)。 |
| 05-06 | [Syn4D: A Multiview Synthetic 4D Dataset](https://arxiv.org/abs/2605.05207) | 提供相机、深度、稠密轨迹及人体等标注，支持跨时刻 / 跨相机的几何查询。 | 可用统一标注评估几何、3D 跟踪与视角变换；训练 / 测试切分和教师使用数据需要核查。 |
| 06-15 | [Geometric Action Model for Robot Policy Learning（GAM）](https://arxiv.org/abs/2606.17046) | 在预训练几何骨干中插入因果未来预测模块，结合语言、本体状态和动作历史，联合预测几何与动作。 | 几何表示服务机器人策略的应用证据；不是只加一个未来轨迹头就能等价复现。 |
| 09-01 | [TAPVid-MV: A Benchmark for Tracking Any Point in 3D Across Multiple Views](https://arxiv.org/abs/2609.01899) | 多视图、世界坐标三维点跟踪评测。 | 减少单相机坐标系带来的歧义；不同数据子集的可标注对象范围不同，不能默认所有操作物都有精确轨迹。[项目](https://tapvidmv.github.io/)。 |
| 09-30 | [Reconstructing the Dynamic World: A Representation-Centric View of 4D Scene Reconstruction](https://arxiv.org/abs/2609.39960) | 从表示角度整理动态 4D 重建。 | 适合补全相关工作 taxonomy；综述不替代对具体模型输入、开源和实验的核查。 |
| ★10-20 | [Learning the 4D World through Point Trajectory Forecasting（Video-Point Model, VPM）](https://arxiv.org/abs/2610.28594) | 多视图历史与语言条件下，联合生成未来视频和持久三维点轨迹，并扩展动作 token。 | 轨迹作为多视图动态一致性的监督；论文报告模拟和真实机器人实验，是“点轨迹有何应用”的直接新证据。附带 VPM-Data、VP-WorldBench。 |
| ★11-19 | [AdaPixFlow: Learning Continuous-Time 3D Dynamics Across Scenes from Sparse Multi-view Observations](https://arxiv.org/abs/2611.26433) | 从稀疏多视图 RGB-D 观测学习连续时间三维动力学，支持时间插值和预测。 | 几何条件较强；可借鉴跨场景速度场，但不可直接当作单目 RGB 预测基线。 |
| ★11-19 | [Plan4D: Generative Plannable 4D Worlds](https://arxiv.org/abs/2611.26516) | 组合几何与视频生成能力，用上下文和文本动作规划生成未来的几何 / 运动。 | 文本描述动作与机器人执行器动作不同；适合生成一致性研究。论文页标注 NeurIPS 2026。 |
| ★11-19，随 Tracktail | [Multi-View Point Odyssey](https://ai-hhmi.github.io/tracktail/) | 同一动态场景的多视角视频和对应三维轨迹。 | 标定多视图教师训练 / 评测候选；和原始单视图 Point Odyssey 的输入及划分不能混用。 |

## 6. 重点论文阅读判断

### 6.1 π⁴：应当立即加入候选，但先理解 3D 轨迹从哪里来

π⁴ 将几何与运动放到同一框架，并去除运动模块对时间位置编码的依赖，以适配任意观测排列。值得特别注意：其三维跟踪通过预测二维对应，再在目标观测的重建点图上取样并变换得到。这对于可见点很自然，但被遮挡点的投影位置可能落在遮挡物表面，因此 **不能把每个输出三维坐标都当作正确的物理点位置**。[论文方法](https://arxiv.org/html/2611.23144v1)

仓库同时提供可见性、跟踪置信度、几何置信度与动态掩码，适合构建有筛选的伪标签。实现中点图 / 相机平移与 `tracks_3d` 的尺度约定需要分别核对，避免重复乘尺度。支持长输入也不等于固定内存、因果流式处理。[官方实现与使用说明](https://github.com/yyfz/Pi4)

**建议先验证：**同一段视频的动态可见点、遮挡点、背景点分别测 2D 和 3D 精度；固定二维对应后更换深度，区分“对应错”和“提升到三维错”。再测输入打乱、稀疏抽帧与跨窗口查询的一致性。

### 6.2 3R-Adapter：与我们的预算最贴近的适配路线之一

论文强调域迁移时跨视图关系退化，围绕对应检索和关系修复适配冻结几何骨干。它的重要性不只是参数少，而是把可诊断的失效现象与适配位置关联起来。仓库包含训练、评测与测试时适配流程；不同骨干和任务使用的配置不同，不能把一个任务的结果直接推广到所有模型。[论文](https://arxiv.org/html/2611.11964v1)、[代码](https://github.com/PKU-OV3-LAB/3R-Adapter)

**建议借鉴：**在动态边界、低照度和大位移场景先量化对应退化；再判断少量关系适配能否同时改善几何与点跟踪。把无适配、仅置信度筛选、普通 LoRA 和自监督适配放在相同数据 / 计算预算下比较。

### 6.3 SceneBound：先补公平对照，再谈新门控

作者报告，在控制记忆写入 / 更新预算后，均匀选择可以匹配多种既有门控策略。这是其具体实验结论，不是所有门控都无效的证明；但它足以改变我们的实验设计。其空间覆盖式记忆也提醒我们，应区别重复扫描固定房间和不断进入新区域两类长视频。[论文](https://arxiv.org/abs/2611.00756)

**最低限度的对照：**固定间隔、同数量随机采样、运动幅度阈值、置信度阈值，以及所提策略。分别报告累计写入次数、活跃记忆量、每帧延迟和精度。否则“减少更新后更好”可能只是消除了冗余写入。

### 6.4 Track4D：看轨迹表示，不要只看“LoRA”标签

论文研究残差三维轨迹视频、归一化典范坐标视频等表示，将冻结视频生成先验用于三维跟踪。不同表示的读出方式不同，部分依赖额外二维跟踪；外部几何也承担了重要作用。作者展示了使用 5,600 个合成运动片段适配的结果，但不能据此得出整体训练一定廉价或全面优于所有方法。[论文方法与实验](https://arxiv.org/html/2611.15287v1)

**对 8 张 H20D 的判断：**值得研究小数据适配与表示选择；不建议在完整代码未发布时，把复现大视频骨干作为短周期项目的关键路径。比较推理成本时应包括外部几何和轨迹读出，而非仅计视频骨干。[项目](https://nirvanalan.github.io/projects/track4d/)、[当前仓库](https://github.com/NIRVANALAN/Track4D)

### 6.5 SGAR 与 Zebra3D：长上下文效率的竞争已经具体化

SGAR 通过几何指导减少注意力连接；论文给出的训练配置包含 4 张 H100、50k 步及预训练骨干微调。这说明它不是从零训练大型模型，但也不是无需数据的推理插件。不能把该配置直接换算为 H20D 的等价训练天数。[SGAR 正文](https://arxiv.org/html/2611.26493v1)

Zebra3D 则同时讨论免训练转换与后训练增强，更适合拆分成“立即可测的转换收益”和“追加学习收益”。二者的速度结果都依赖视图数和测试配置；需要同时检查边界细节、大视差及动态区域是否受损。[Zebra3D](https://arxiv.org/abs/2610.12727)

### 6.6 Tracktail 与 TAP-Out：输入条件和不可见区域决定可比性

Tracktail 不输入深度，但使用标定多视图和三维查询。若实验室能采集同步相机，它可以成为较强的离线标注工具；若训练目标只有单目 RGB，应把它明确定位为“使用额外传感信息的教师”。[论文](https://arxiv.org/abs/2611.26779)、[官方项目](https://ai-hhmi.github.io/tracktail/)

TAP-Out 用生成式补全处理视野外跟踪，提供了有趣的推断先验，但看不见的运动不因此变成可验证事实。做伪标签时，应将观测支持的轨迹和生成推测轨迹分开，后者只能作为带不确定性的辅助约束。[论文](https://arxiv.org/abs/2611.00406)、[实现](https://github.com/finlay-hudson/TAP-Out)

### 6.7 VPM：轨迹监督与下游用途的连接更直接了

VPM 的出发点是不同相机生成的视频必须描述同一个三维动态场景，以持久点轨迹为共同约束。它进一步加入机器人动作模态，报告点监督对生成和控制的帮助。这为“跟踪不仅是一个孤立 benchmark”提供了新的研究案例，但收益取决于完整训练与任务设定，不能直接推断提高任意 TAP 指标都会提高机器人成功率。[论文](https://arxiv.org/abs/2610.28594)

## 7. 当前开源状态核查

本节是截至本次访问的网页核查，未进行模型下载、环境安装或运行验收。对于已有年内方法，主表中的仓库链接仅是复现入口，不代表本轮重新审计了全部权重与许可证。

| 方法 | 本轮可确认的情况 | 对实验安排的影响 |
|---|---|---|
| [π⁴](https://github.com/yyfz/Pi4) | 有实现、示例与 `from_pretrained("yyfz233/Pi4")` 权重加载入口。 | 可以开始环境与小样本验收；仍需检查显存、许可证和失败模式。 |
| [ARROW](https://github.com/ifradlin/arrow) | README 列出 10-12 发布推理代码 / 权重 / 查看器，11-03 发布评测代码；训练代码仍列为后续计划。 | **此前“尚未开源”的判断应被本次核查替换。**推理可作为近期实验入口，训练复现需另查。 |
| [3R-Adapter](https://github.com/PKU-OV3-LAB/3R-Adapter) | 已有实现及训练、评测、TTA 说明；未单独确认所有适配权重。 | 适合研究代码与配置；不能默认所有论文任务都可直接加载成品模型。 |
| [Track4D](https://github.com/NIRVANALAN/Track4D) | 当前仓库为说明页，标注完整发布待完成；另有[模型入口](https://huggingface.co/yslan/Track4D-2026)。 | 不应把模型页面存在等同于完整可运行管线已开源。 |
| [Tracktail](https://github.com/AI-HHMI/tracktail) | 有实现；官方项目提供数据 / 权重入口。 | 值得验证多视图教师，但先核对标定和查询格式。 |
| [TAP-Out](https://github.com/finlay-hudson/TAP-Out) | 有实现，涉及多个外部组件。 | 安装成功与端到端成本需分别验收，不应当作单一轻量跟踪器。 |
| [MoGe-3](https://qft-333.github.io/moge3page/) | 官方项目明确指向 Microsoft MoGe 仓库。 | 可进一步核对具体模型版本，作为单帧细节几何教师。 |
| SGAR、SceneBound、Infer3D、Kosmo-GFM、AdaPixFlow、Plan4D | 本轮未完成官方实现与权重审计。 | 可以读论文、设计对照；不要把未核实状态写成“已开源”或“未开源”。 |

## 8. 2025 年首发、但仍应保留的背景基线

以下条目用于避免“2026 年论文”与“2026 年会议论文”的混淆，不计入本笔记的 2026 首发主表。此节为原有文献体系的补充索引，并非重新完成所有开源状态检查。

| 工作 | 首发 / 论文链接 | 为什么仍需要 |
|---|---|---|
| D4RT | [2025-12，2512.08924](https://arxiv.org/abs/2512.08924) | 统一动态重建与跟踪的重要比较对象；查询式建模与今年的方法有直接联系。 |
| Any4D | [2025-12，2512.10935](https://arxiv.org/abs/2512.10935) | 任意观测条件下的动态几何恢复参考。 |
| Trace Anything | [2025-10，2510.13802](https://arxiv.org/abs/2510.13802) | 查询式轨迹 / 几何恢复；论文支持范围与具体代码的输入限制应分开核对。 |
| PAGE-4D | [2025-10，2510.17568](https://arxiv.org/abs/2510.17568) | 几何与运动的联合建模，但不能自动视作通用 TAP 接口。 |
| MoVieS | [2025-07，2507.10065](https://arxiv.org/abs/2507.10065) | 动态高斯与运动表示；注意已知相机条件。 |
| π³ | [2025-07，2507.13347](https://arxiv.org/abs/2507.13347) | 无序几何骨干，便于理解 π⁴ 增加了哪些运动能力。 |
| Depth Anything 3 | [2025-11，2511.10647](https://arxiv.org/abs/2511.10647) | 常见几何先验 / 点图来源；其几何输出本身不等于动态材料点轨迹。 |
| MapAnything | [2025-09，2509.13414](https://arxiv.org/abs/2509.13414) | 度量几何重建参考。 |
| MV-TAP | [2025-12，2512.02006](https://arxiv.org/abs/2512.02006) | 多视图点跟踪背景；需区分二维输出与直接三维输出。 |
| AnthroTAP | [2025-07，2507.06233](https://arxiv.org/abs/2507.06233) | 从人体先验获得真实视频点监督，与伪标签质量相关。 |

更早的 **CoTracker3、AllTracker、SpaTrackerV2、TAPIP3D** 仍应留在实际实验候选中。新论文更多不意味着应删掉稳定、易复现且输入协议清晰的旧基线。

## 9. 对当前项目的具体建议

### 9.1 建议阅读顺序

1. **π⁴ → ARROW → Point4D / 4RC**：弄清当前联合模型的输出、查询接口、无序能力与长程限制。
2. **3R-Adapter → Track-On-R → TrajVG**：分别学习几何适配、伪标签验证和几何—轨迹耦合。
3. **SceneBound → FILT3R / 状态门控工作 → SGAR / Zebra3D**：建立公平的长序列效率与记忆实验。
4. **Track4D → TrackCraft3R → VPM / GAM**：研究生成先验和未来预测，等复现条件成熟再扩展主线。

### 9.2 先做一次小而严格的教师验收

建议把 π⁴、ARROW 和现有已跑通联合模型作为第一批候选，配一个成熟二维跟踪器交叉核验。教师不需要因果，但若学生是在线模型，必须说明离线教师使用了未来观测。

统一记录源帧、目标帧、查询点、相机内外参约定、坐标系、尺度、可见性和置信度。几何和轨迹应拆开验收：

| 检查 | 想排除的问题 |
|---|---|
| 可见 / 遮挡 / 出视野分组的 2D 与 3D 误差 | 平均指标掩盖“不可见点被提升到遮挡物表面”。 |
| 静态 / 动态、边界 / 内部分组 | 模型主要靠背景占比取得好结果。 |
| 固定 2D 对应、更换深度或位姿 | 确认误差来自跟踪、深度还是坐标变换。 |
| 循环一致性、跨模型一致性与有真值小集 | 检查筛选是否真的提高标签正确率；一致性本身不是正确性证明。 |
| 连续输入、抽帧、打乱顺序、跨窗口 | 区分时序依赖、无序能力和尺度 / 身份漂移。 |
| 单次全局对齐与分窗口对齐分别报告 | 避免频繁对齐掩盖长程漂移。 |

以上是本次调研提出的实验建议，不是已运行的实验结论。

### 9.3 当前更值得寻找的研究缺口

**第一类：二维对应较准，但三维身份或几何错误。** 新联合模型使这一问题更可测：可见性误判、遮挡边界深度混合和跨片段尺度漂移可能给伪标签带来系统性偏差。若能够诊断并用小模块或测试时优化修正，比只提高某个整体均值更容易形成明确论点。

**第二类：记忆更新对动态场景存在选择性遗忘。** 在相同存储 / 更新预算下，背景反复出现、物体离开后返回、相机回访等事件，是否会破坏对象点身份？必须证明改进超出减少更新次数本身的收益。

**第三类：教师不确定性能够预测下游监督价值。** 相比简单平均多个模型，识别在哪些条件下采用几何教师、二维教师或拒绝监督，更贴近 8 卡预算。验证指标应包括标签精度—覆盖率曲线和学生提升，不能只展示更平滑的轨迹。

**第四类：观测重建改善能否带来未来预测收益。** 可作为两个月级别的扩展：固定预测器，改变历史几何 / 轨迹质量，观察三维预测或控制指标。应先证明中间表示改善与下游收益的联系，再考虑训练更大世界模型。

## 10. 使用这份清单时保留的限制

- 这是围绕本项目筛选的年内研究地图，不能称为 2026 全领域完整清单。
- 主表论文均提供可追溯的原始论文链接；代码状态只对明确核查的条目下结论。
- “支持无序图像”“支持动态场景”“支持长视频”“在线因果”“持续物理点身份”是五个不同能力，不能互相替代。
- 数百 / 数千帧演示不能证明常数内存；低参数量或 LoRA 不能单独证明低训练成本。
- 新视角渲染质量、几何精度、相机定位、点轨迹与未来预测，应使用各自指标并保留输入条件差异。
- 本文未重新跑模型、下载权重或复现论文表格；性能与预算判断仍需在本实验室环境中验证。
