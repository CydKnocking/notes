# 三维视觉基础模型的长序列、低开销与新场景适配

> 检索截止：**2026-08-31**。范围以 CVPR / ICCV / ECCV / ICLR / NeurIPS / ICRA / IROS / WACV / 3DV 与 TPAMI 为主，并补充少量尚未正式发表、但直接命中问题的 2026 年预印本。正式录用论文与预印本分开标注；速度和显存数字只能在各论文自己的硬件、分辨率和输入设置下理解，**不宜跨论文直接横比**。

**纳入标准。** 核心表只收录至少直接解决以下一个问题的工作：长上下文复杂度、在线/有界记忆、跨窗口全局一致性、运行时加速，或新场景自适应。泛化的 SLAM、NeRF/3DGS 增量建图和只在短多视图上提升精度的模型没有展开。本次严格口径下的正式论文集中在 CVPR、ICCV、ICLR、ICRA、NeurIPS 与 3DV；没有检索到 ECCV、WACV、IROS、ICML 或 TPAMI 中**直接扩展上述四类新基础模型以满足长序列目标**的正式论文。这不表示这些 venue 没有广义的长序列 SLAM/重建工作。

## 0. 结论先行

VGGT、$\pi^3$、Depth Anything 3（DA3）和 VGGT-$\Omega$ 已经把短序列的前馈多视图几何做得很强，但“短序列精度高”并不等于“长视频可用”。它们的主要瓶颈是跨帧全局注意力：若每帧有 $P$ 个 token、共有 $T$ 帧，朴素全局注意力的时间复杂度为

\[
\mathcal{O}((TP)^2),
\]

并且需要一次看到完整序列。长视频研究真正竞争的是：**怎样在有限显存中保留局部精确几何、长期全局坐标和新场景信息**。

截至检索日，最值得关注的判断是：

1. **只想无训练加速现有 VGGT / $\pi^3$**：FastVGGT、AVGGT、HTTM、LiteVGGT 很实用；但 token merging / pruning 只是降低常数，通常没有从根本上消除长序列全局注意力或长期漂移。
2. **要真正在线、定长显存**：IncVGGT、TTT3R、LongStream、LASER，以及 2026 年预印本 LoGeR 更接近正确方向。单纯的因果 KV cache（StreamVGGT、STream3R）降低了重复计算，但若历史 cache 不压缩，显存和单帧延迟仍会随序列增长。
3. **要离线处理上千张图，同时保留全局双向推理**：VGG-T\(^3\)、ZipMap、Scal3R 是比“切块后硬拼”更有研究价值的路线；它们用 Test-Time Training（TTT）/ fast weights 把可变长 KV 记忆压缩成固定规模神经状态。
4. **要最快落地到已有权重**：VGGT-Long、Pi-Long、DA3-Streaming、LASER、MERG3R 的工程门槛最低。它们以窗口/子图为单位运行基础模型，再做显式对齐、回环或 BA。优点是模型无关、无需重训；弱点是窗口接缝和累积尺度漂移。
5. **要提升新场景适配**：必须区分“更多数据带来的零样本泛化”和“测试时真正适配”。VGGT-$\Omega$、DA3、Depth Anything 系主要属于前者；Online3R、Scal3R、TTT3R、Self-Geometry 才在测试时更新 prompt、fast weights、状态或 LoRA。
6. **只需要视频深度而非相机轨迹/统一点云**：Video Depth Anything 和 FlashDepth 比完整 3D 几何模型轻得多，分别适合超长离线视频和高分辨率在线流。
7. **期刊现状**：本次检索未发现已经正式刊于 TPAMI、且直接针对 VGGT / $\pi^3$ / DA3 / VGGT-$\Omega$ 长序列扩展的论文。该方向从 2024 年才快速形成，核心成果目前高度集中在 2025–2026 年顶会与最新预印本；不能把 arXiv 投稿误写成 TPAMI 论文。

## 1. 四个基础模型：强项与长序列短板

| 模型 | 会议 | 核心设计 | 泛化来源 | 对长视频的实际含义 |
|---|---|---|---|---|
| [Depth Anything](https://openaccess.thecvf.com/content/CVPR2024/html/Yang_Depth_Anything_Unleashing_the_Power_of_Large-Scale_Unlabeled_Data_CVPR_2024_paper.html) | CVPR 2024 | 单图相对深度；约 62M 无标注图像的数据引擎 | 大规模伪标注与语义先验 | 单帧很稳，但逐帧推理会闪烁，且不提供相机轨迹与跨帧统一坐标 |
| [Depth Anything V2](https://proceedings.neurips.cc/paper_files/paper/2024/file/26cfdcd8fe6fd75cc53e92963a656c58-Paper-Conference.pdf) | NeurIPS 2024 | 更强 teacher、合成真值、真实图像伪标签；多种模型尺寸 | teacher-student 与数据覆盖 | 是 Video Depth Anything、FlashDepth 的强单图 backbone；本身仍无视频记忆 |
| [VGGT](https://openaccess.thecvf.com/content/CVPR2025/html/Wang_VGGT_Visual_Geometry_Grounded_Transformer_CVPR_2025_paper.html) | CVPR 2025，Best Paper | 交替 frame/global attention，一次预测相机、深度、pointmap、track | 大规模多任务 3D 监督 | 短序列精度强；全局注意力随帧数二次增长，且参考帧选择会影响稳定性 |
| [$\pi^3$](https://proceedings.iclr.cc/paper_files/paper/2026/hash/11a09e0aaa74867c6b0719c639fc09f8-Abstract-Conference.html) | ICLR 2026 | 去掉固定参考视图；预测仿射不变相机与尺度不变局部 pointmap；排列等变 | 更好的坐标规范化与输入顺序鲁棒性 | 解决“参考帧偏置”，**没有解决全局注意力的二次复杂度**；很适合作为长序列方法的局部 backbone |
| [Depth Anything 3](https://proceedings.iclr.cc/paper_files/paper/2026/hash/e4cd50120b6d7e8daff1749d6bbaa889-Abstract-Conference.html) | ICLR 2026 | plain DINO Transformer + 单一 depth-ray 目标；可输入任意视图与可选相机 | DA2 teacher-student、统一目标、公开多源数据 | 细节与零样本几何很强；原生模型仍更适合有界多视图，超长视频需 DA3-Streaming 或新的相对/流式头 |
| [VGGT-$\Omega$](https://openaccess.thecvf.com/content/CVPR2026/html/Wang_VGGT-ohm_CVPR_2026_paper.html) | CVPR 2026，Best Paper Finalist | 单一稠密头、MLP+pixel shuffle、scene/register token attention；静态+动态 | 15× 更多监督数据、约 18M 无标注视频、自监督 | 训练内存约为 VGGT 的 30%，鲁棒性显著提高；但它不是定长显存流式模型，官方 500 帧示例仍约需 43.15 GB 峰值显存 |

### 关键辨析

- **VGGT-$\Omega$ 的“省内存”主要指训练可扩展性**。它用少量 register 聚合场景信息，并仅以 register 参与部分跨帧交换；这为长上下文提供了好结构，但官方推理显存仍随帧数增长。
- **$\pi^3$ 的“scalable”主要体现在任务、视图数与无参考帧鲁棒性**，并不意味着无限长、常数显存。
- **DA3 与 Video Depth Anything 是不同目标**：DA3恢复相机和空间一致几何；Video Depth Anything专注长视频的仿射不变深度与时间一致性。
- 对真实长视频，误差通常不只来自注意力复杂度，还来自参考坐标外推、尺度/shift 漂移、动态物体、窗口间非刚性畸变和回环缺失。

## 2. 方法谱系：六类长序列解法

| 路线 | 代表工作 | 总复杂度/显存趋势 | 优点 | 主要风险 |
|---|---|---|---|---|
| 减 token / 稀疏全局注意力 | FastVGGT、AVGGT、HTTM、LiteVGGT | 有效 token 变少，但一般仍非严格线性/定长 | 无训练或轻量微调；最大程度保留原模型 | 极长序列仍受全局上下文长度制约；过度合并损伤稠密几何 |
| 因果注意力 + KV cache | StreamVGGT、STream3R | 增量计算方便；未压缩 cache 时历史长度仍增长 | 在线低延迟；可直接复用 FlashAttention 生态 | cache 饱和、attention sink、单帧延迟随历史增长 |
| 固定状态递归/压缩记忆 | Spann3R、CUT3R、LONG3R、TTT3R、IncVGGT | 可做到 $\mathcal{O}(T)$ 与有界显存 | 真正在线；适合机器人与边缘部署 | 单一状态会遗忘细节，长程回环和全局尺度容易漂移 |
| TTT / fast-weight 记忆 | VGG-T\(^3\)、ZipMap、Scal3R、tttLRM | 以固定规模 MLP/子网络压缩 KV；近线性 | 比普通 RNN 状态容量高；可查询场景记忆 | 训练和内循环设计复杂；“TTT”不一定等价于域适配 |
| 窗口/子图 + 显式对齐 | VGGT-Long、LASER、MERG3R、TALO、MASt3R-SLAM | 固定窗口时 GPU 峰值有界；CPU/地图/图优化随场景增长 | 模型无关、无需重训、回环可解释 | 对齐退化、窗口接缝、动态区污染、后端不再是纯前馈 |
| 局部无损 + 全局压缩混合记忆 | LoGeR | 固定局部窗口 + 固定 fast weights，整体线性 | 同时保留邻域精度和全局坐标 | 仍是 2026 预印本；需要较大规模重新训练与更充分复现 |

最重要的结构性结论是：

> **长视频不应只保留一种记忆。** 相邻帧配准需要未压缩的局部 token；公里级坐标一致性需要压缩的全局状态；真正闭环还需要可检索的关键帧/拓扑图。只用全注意力太贵，只用单一 RNN 状态又太容易遗忘。

## 3. 顶会核心论文

### 3.1 直接加速 VGGT / $\pi^3$：低改造成本

#### FastVGGT — ICLR 2026

- 链接：[ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2026/hash/9f5b159f2c1d216d73bc0c289763dbfc-Abstract-Conference.html) · [code](https://github.com/mystorm16/FastVGGT)
- 发现 VGGT global attention 中大量 token 的注意力图趋同，即 “token collapse”。
- 在 global attention 前做三类 token 划分：保留第一帧锚点、保护显著 token、按图像区域均匀选代表 token；注意力后 unmerge，以兼容原稠密输出头。
- 无需训练；1000 张图报告约 **4×** 加速，并降低长序列误差累积。
- 评价：很好的工程基线，但对第一帧锚定的依赖与 VGGT 本身相同；它压缩计算，不建立持久全局地图。

#### AVGGT — CVPR 2026

- 链接：[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Sun_AVGGT_Rethinking_Global_Attention_for_Accelerating_VGGT_CVPR_2026_paper.html) · [arXiv](https://arxiv.org/abs/2512.02541)
- 对 VGGT 和 $\pi^3$ 的 global layer 逐层解剖：早层跨视图对应尚未形成，中层负责对齐，末层多为小幅修正。
- 将早期 global attention 改为 frame attention；对中间 global attention 的 K/V 做保对角线的子采样与均值填充。
- 无训练，报告 **8–10×** 加速，且可同时作用于 VGGT 与 $\pi^3$。
- 评价：比“统一 token merging”更有结构解释，适合成为任何新长序列架构的层级稀疏先验。

#### HTTM / LiteVGGT — CVPR 2026

- [HTTM](https://openaccess.thecvf.com/content/CVPR2026/html/Wang_HTTM_Head-wise_Temporal_Token_Merging_for_Faster_VGGT_CVPR_2026_paper.html)：按 attention head 独立做时间 token merging，利用不同 head 的空间局部性和时间对应；最高报告 **7×** 加速且性能下降很小。
- [LiteVGGT](https://openaccess.thecvf.com/content/CVPR2026/html/Shu_LiteVGGT_Boosting_Vanilla_VGGT_via_Geometry-aware_Cached_Token_Merging_CVPR_2026_paper.html)：按几何重要性选择 anchor，并跨层缓存 merge index；支持 FP8 微调，1000 图场景最高报告 **10×** 加速和显存下降。
- 评价：二者都适合已有 VGGT 部署。HTTM更偏运行时稀疏；LiteVGGT更像“稀疏 + 缓存 + 低精度”的整套加速方案。

#### QuantVGGT — ICLR 2026

- 链接：[ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2026/hash/618c8af8efd19b4ce90b8864a764d0fa-Abstract-Conference.html) · [code](https://github.com/wlfeng0509/QuantVGGT)
- 针对 VGGT 特殊 token 的重尾激活和多视图校准不稳定，设计专用 PTQ。
- 4-bit 版本报告 **3.7×** 内存下降、真实硬件 **2.5×** 加速，并保留超过 98% 的重建精度。
- 评价：量化与长上下文记忆是正交方向；它能让给定 GPU 容纳更多帧，但不会自动消除时序漂移。

#### Fast3R — CVPR 2025（早期大规模前馈基线）

- 链接：[CVF](https://openaccess.thecvf.com/content/CVPR2025/html/Yang_Fast3R_Towards_3D_Reconstruction_of_1000_Images_in_One_Forward_CVPR_2025_paper.html) · [project](https://fast3r-3d.github.io/)
- 将 DUSt3R 从成对处理推广为 $N$ 视图并行前向，直接输入 1000+ 张无序、无位姿图像，省掉逐对推理和昂贵的后续全局对齐；论文首页设置报告约 **251.1 FPS**。
- 评价：它比 VGGT 更早证明“大视图集合一次前向”可行，是重要速度基线；但“一次能吞 1000 图”不等于在线、有界显存或公里级稳定，后来的流式状态、分块对齐和 TTT 路线针对的正是这些缺口。

### 3.2 真正的流式/递归几何模型

#### Spann3R — 3DV 2025；CUT3R — CVPR 2025 Oral

- [Spann3R](https://hengyiwang.github.io/projects/spanner) 用外部 spatial memory 保存过去相关 3D 信息，并让新帧查询该记忆。
- [CUT3R](https://openaccess.thecvf.com/content/CVPR2025/html/Wang_Continuous_3D_Perception_Model_with_Persistent_State_CVPR_2025_paper.html) 用持续更新的 recurrent state 输出统一坐标下的 metric pointmap，可处理视频、稀疏无序照片、静态与动态场景，还能查询未观测视角。
- 评价：它们证明“单一持久状态”可替代全局全注意力，是后续 LONG3R / TTT3R 的重要起点；缺点是把所有历史压进单一状态后会出现遗忘和长度外泛化下降。

#### LONG3R — ICCV 2025

- 链接：[CVF](https://openaccess.thecvf.com/content/ICCV2025/html/Chen_LONG3R_Long_Sequence_Streaming_3D_Reconstruction_ICCV_2025_paper.html) · [code](https://github.com/zgchen33/LONG3R)
- memory gating 先筛相关记忆，再以 dual-source refined decoder 做粗到细交互。
- 3D 时空记忆动态裁剪冗余空间信息，并随场景调整分辨率；两阶段 curriculum 专门学习长序列能力。
- 报告在长序列上优于已有 streaming 方法，并维持实时推理。
- 评价：比固定大小、无结构的 recurrent token 更重视“记什么、以何种 3D 分辨率记”，但训练成本和公开复现成熟度需检查。

#### StreamVGGT — ICLR 2026

- 链接：[ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2026/hash/8da04a60948be713dc766f0c7e3a5b1f-Abstract-Conference.html) · [code](https://github.com/wzzheng/streamvggt)
- 把 VGGT 的双向 global attention 改成时间因果注意力；缓存历史 K/V 作为隐式记忆，并从 VGGT teacher 蒸馏。
- 优点是在线、低首帧延迟、容易迁移 FlashAttention 等 LLM 算子。
- 关键限制：**KV cache 本身会随时间增长**。因此 StreamVGGT 是“可流式”，不等价于“无限长、常数显存”。

#### IncVGGT — ICLR 2026

- 链接：[ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2026/hash/0a4096f09ab230082df548f901d4f79e-Abstract-Conference.html)
- 输入侧：把高度重叠的相邻帧注册并融合为 composite view，减少重复 token。
- 历史侧：只保留 top-$k$ 相关 slot 和最新 slot，以固定 cache 长度。
- 无需训练；相对 StreamVGGT，在 500 帧上报告 **58.5× 更少算子、9× 更低内存、25.7× 更少能耗、4.9× 更快**，80 GB GPU 可继续运行到 10k 帧。
- 评价：这是“定长显存 + 训练免费”里最直接的一篇，但激进帧融合与 top-$k$ 裁剪会牺牲重复纹理、细小结构和迟到回环所需的证据。

#### STream3R — ICLR 2026

- 链接：[paper/project](https://nirvanalan.github.io/projects/stream3r/) · [ICLR PDF](https://openreview.net/pdf?id=RTTYGeC2Io)
- 把 pointmap 预测重写为 decoder-only causal Transformer；每层先做 frame self-attention，再用历史 cache 做因果跨帧注册。
- 直接输出世界/相机坐标 pointmap、置信度与相机姿态；兼容 LLM 式训练基础设施，在动态场景上也有较强泛化。
- 评价：结构简洁、易扩规模；与 StreamVGGT 一样，需要继续解决历史 cache 的选择、压缩和回环检索。

#### TTT3R — ICLR 2026

- 链接：[ICLR poster](https://iclr.cc/virtual/2026/poster/10008709) · [arXiv](https://arxiv.org/abs/2509.26645)
- 将 CUT3R 类 recurrent state update 解释为在线学习；根据“旧记忆—新观测”的对齐置信度推导每 token 的闭式自适应学习率。
- 无新增参数和重训；报告全局 pose 提升约 **2×**，并以 **20 FPS、6 GB 显存**处理数千图像。
- 评价：真正解决的是 recurrent model 的 **length generalization / 稳定-可塑性平衡**。它不是传统意义上通过反向传播微调 backbone 的 TTA。

#### LongStream — CVPR 2026

- 链接：[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Cheng_LongStream_Long-Sequence_Streaming_Autoregressive_Visual_Geometry_CVPR_2026_paper.html) · [arXiv](https://arxiv.org/abs/2602.13172)
- 不再把所有 pose 锚定第一帧，而预测关键帧相对 pose，把无限增长的外推问题改为固定难度的局部估计。
- 用 orthogonal scale learning 把几何与尺度估计解耦；用 cache-consistent training 和周期 cache refresh 抑制 attention sink 与历史污染。
- 报告在公里级、数千帧严格在线场景达到 **18 FPS**。
- 评价：它同时处理了计算、坐标 gauge、尺度漂移和训练—推理 cache 不一致，研究完整性高；比“只换注意力”更值得作为新架构基线。

### 3.3 TTT / fast weights：线性时间的场景记忆

这里的 TTT 有两种含义，不能混淆：

- **序列建模型 TTT**：在推理时快速更新一个小 MLP，把历史 K/V 写入 fast weights；主要目标是用线性复杂度替代 softmax attention。
- **域/场景适配型 TTA**：用当前场景的自监督几何损失更新 prompt、LoRA 或部分网络；主要目标是修正分布偏移。

#### VGG-T\(^3\) — CVPR 2026

- 链接：[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Elflein_VGG-T3_Offline_Feed-Forward_3D_Reconstruction_at_Scale_CVPR_2026_paper.html) · [project/code](https://research.nvidia.com/labs/dvl/projects/vgg-ttt/)
- 用固定大小 MLP 取代 VGGT global attention 的变长 KV 空间，把一个图像集合写入 fast weights。
- 保留离线双向全局聚合，并能用新图像查询冻结后的场景状态做 relocalization。
- 复杂度对视图数近线性；1000 图报告约 **54 秒、11.6× 加速**。
- 评价：适合大规模离线图像集和“建图后多次定位”；不以逐帧最低延迟为首要目标。

#### ZipMap — CVPR 2026

- 链接：[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Jin_ZipMap_Linear-Time_Stateful_3D_Reconstruction_via_Test-Time_Training_CVPR_2026_paper.html) · [code](https://github.com/Haian-Jin/ZipMap)
- TTT layer 将整个集合压缩进紧凑 hidden scene state；支持双向离线重建、状态查询和流式扩展。
- 单张 H100 上报告 **700+ 帧低于 10 秒、超过 VGGT 20×**。
- 评价：速度/状态查询很亮眼；官方说明 streaming 分支训练仍较初步，长程流式结论应与离线结果分开看。

#### Scal3R — CVPR 2026 Highlight

- 链接：[CVF 条目](https://openaccess.thecvf.com/CVPR2026?day=2026-06-06) · [project/code](https://zju3dv.github.io/scal3r/) · [arXiv](https://arxiv.org/abs/2604.08542)
- 在 VGGT 多个 global layer 后加入 Global Context Memory；若干轻量神经子网络以自监督目标在测试时快速更新，形成比固定 token state 容量更高的全局上下文。
- 支持多 GPU chunk 并行，也可退化为单 GPU 顺序处理；在 KITTI（最长 4661 帧）和 Oxford Spires 等大场景测试。
- 评价：它把“长序列状态压缩”和“测试时场景适配”放在同一系统内，是很有潜力的结合；代价是训练、内循环和分布式实现都较复杂。

#### tttLRM — CVPR 2026 Highlight

- 链接：[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Wang_tttLRM_Test-Time_Training_for_Long_Context_and_Autoregressive_3D_Reconstruction_CVPR_2026_paper.html) · [project](https://cwchenwang.github.io/tttLRM/)
- 以 TTT fast weights 形成隐式 3D 表征，再解码为 Gaussian Splats；同时支持长上下文离线和渐进在线重建。
- 评价：如果最终输出目标是可渲染 3DGS 而非纯点云/相机，它比 VGGT 点云后接 3DGS 更原生；但评价任务与 pose/pointmap 系工作并不完全同构。

### 3.4 窗口、显式几何后端与可插拔系统

#### VGGT-Long — ICRA 2026

- 链接：[arXiv](https://arxiv.org/abs/2507.16443) · [code](https://github.com/DengKaiCQ/VGGT-Long)
- 固定大小 overlapping chunks 独立运行 VGGT；以重叠点云做置信度加权 Sim(3) 对齐，再用轻量回环优化修正长期漂移。
- 无需相机标定、深度监督或模型重训；面向 KITTI、Waymo 等公里级场景。
- 评价：是最强的“简单、可插拔、今天能用”基线之一。它把 GPU 显存固定在 chunk 大小，但中间地图、CPU/磁盘和图优化仍随轨迹增长。

#### Pi-Long / DA3-Streaming — 官方工程扩展，无独立论文

- [Pi-Long](https://github.com/DengKaiCQ/Pi-Long) 将 VGGT-Long 的 chunk/align/loop 框架迁到 $\pi^3$ / Pi3X；官方明确说明**没有独立论文**，KITTI 504×154 设置下更新版约 8 FPS。
- [DA3-Streaming](https://github.com/ByteDance-Seed/Depth-Anything-3/blob/main/da3_streaming/README.md) 将同一思想迁到 DA3，滑窗和跨块状态管理可在少于 12 GB GPU 显存下处理超长视频。
- 评价：它们说明长序列后端应与 backbone 解耦。$\pi^3$ 的无参考帧局部几何、DA3 的 detail/metric 能力都可直接替换 VGGT。

#### LASER — CVPR 2026

- 链接：[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Ding_LASER_Layer-wise_Scale_Alignment_for_Training-Free_Streaming_4D_Reconstruction_CVPR_2026_paper.html) · [arXiv](https://arxiv.org/abs/2512.13680)
- 指出简单 Sim(3) 不能修复不同深度层在相邻窗口中的非一致尺度；将深度离散成 layer，逐层估计 scale 并跨窗口、跨时间传播。
- 无训练地把 VGGT / $\pi^3$ 等离线模型改造成流式 4D 系统；在 RTX A6000 上报告 **14 FPS、6 GB 峰值显存**和公里级视频。
- 评价：相比 VGGT-Long，它直接建模“单个 Sim(3) 对局部非刚性误差无能为力”的核心失败模式，部署价值很高。

#### MERG3R — CVPR 2026

- 链接：[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Cheng_MERG3R_A_Divide-and-Conquer_Approach_to_Large-Scale_Neural_Visual_Geometry_CVPR_2026_paper.html) · [code](https://github.com/LeoChengKX/MERG3R)
- 面向**无序大图集**：先以视觉相似图生成伪顺序，再切成有几何多样性的重叠子集；用任意 VGGT / $\pi^3$ backbone 重建局部子图，最后全局对齐和置信度加权 BA。
- 评价：视频可直接用顺序窗口，但它最有价值的地方是把“超显存无序图集”也纳入统一 divide-and-conquer 框架。

#### TALO — CVPR 2026

- 链接：[CVF PDF](https://openaccess.thecvf.com/content/CVPR2026/papers/Zhang_TALO_Pushing_3D_Vision_Foundation_Models_Towards_Globally_Consistent_Online_CVPR_2026_paper.pdf) · [code](https://github.com/Xian-Bei/TALO)
- 认为 VGGT-Long 的 Sim(3) 与 VGGT-SLAM 的 SL(4) 都是假设“整块共享同一种误差场”，在多相机、噪声点云和局部畸变下不成立。
- 用 Thin Plate Spline 和全局传播 control points 做高自由度、长时程对齐；point-agnostic submap registration 增强对噪声的鲁棒性。
- 评价：TALO解决的是**子图拼接的模型误差**而非 backbone 推理成本；与 token/TTT 加速互补。

#### AMB3R / AMB3R-VO — CVPR 2026

- 链接：[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Wang_AMB3R_Accurate_Feed-forward_Metric-scale_3D_Reconstruction_with_Backend_CVPR_2026_paper.html) · [project](https://hengyiwang.github.io/projects/amber)
- AMB3R 在多视图前馈模型后加入稀疏、紧凑的 volumetric backend，把多次观测融合到同一 metric-scale 空间位置；AMB3R-VO 再用**固定容量 active keyframe memory + 可增长 global keyframe memory**处理任意长度在线序列。
- VO/SfM 扩展无需重新训练基础模型，也无需 test-time optimization；补充材料在 RTX 4090、392×518 输入上报告 VO 平均约 **4.2 FPS**。
- 评价：它的贡献不是极致 FPS，而是把 metric scale、显式空间紧致性和关键帧后端合在一起。GPU 工作集可控，但全局关键帧地图仍随场景增长；这比声称“整体常数内存”更准确。

#### MASt3R-SLAM / SLAM3R — CVPR 2025

- [MASt3R-SLAM](https://openaccess.thecvf.com/content/CVPR2025/html/Murai_MASt3R-SLAM_Real-Time_Dense_SLAM_with_3D_Reconstruction_Priors_CVPR_2025_paper.html)：以 MASt3R 两视图先验统一 tracking、local fusion、图构建、回环与二阶全局优化，约 **15 FPS**；对野外视频和时变中心相机模型更务实。
- [SLAM3R](https://openaccess.thecvf.com/content/CVPR2025/papers/Liu_SLAM3R_Real-Time_Dense_Scene_Reconstruction_from_Monocular_RGB_Videos_CVPR_2025_paper.pdf)：窗口内直接回归 pointmap，窗口间用网络完成注册与形变，**20+ FPS**，不显式求相机参数。
- 评价：如果目标是可靠机器人建图，而不是纯粹的“一次前向”，含回环与稀疏图优化的混合系统目前仍更可控。

### 3.5 Depth Anything 路线：长视频深度与低算力

#### Video Depth Anything — CVPR 2025 Highlight

- 链接：[CVF](https://openaccess.thecvf.com/content/CVPR2025/html/Chen_Video_Depth_Anything_Consistent_Depth_Estimation_for_Super-Long_Videos_CVPR_2025_paper.html) · [code](https://github.com/DepthAnything/Video-Depth-Anything)
- 冻结 DA2 encoder，换成轻量时空 head；以 temporal depth-gradient loss 学一致性，不依赖光流或相机位姿。
- 长视频用 overlapping clips + key-frame reference，统一整段视频的 scale/shift；展示 196 秒、4690 帧例子。
- 小模型可达 **30 FPS**，并宣称可处理任意长视频。
- 评价：若下游只要稳定相对深度，这是性价比最高的起点；若要统一 3D 地图，还需要相机、尺度和回环模块。

#### FlashDepth — ICCV 2025

- 链接：[CVF PDF](https://openaccess.thecvf.com/content/ICCV2025/papers/Chou_FlashDepth_Real-time_Streaming_Video_Depth_Estimation_at_2K_Resolution_ICCV_2025_paper.pdf) · [code](https://github.com/Eyeline-Research/FlashDepth)
- 在 DA2 上加入 recurrent feature alignment，使每帧中间深度特征在线对齐到统一 scale。
- 在 A100 上以 **2044×1148、24 FPS** 真正流式运行，边界和细结构明显强于低分辨率流式模型。
- 评价：适合视频编辑、机器人近场深度和高分辨率传感；它不解决相机 pose 与全局点云。

#### DyFN — CVPR 2026

- 链接：[CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Lyu_Stabilizing_Streaming_Video_Geometry_via_Dynamic_Feature_Normalization_CVPR_2026_paper.html) · [project](https://shawlyu.github.io/DyFN/)
- 将视频几何抖动追溯到 latent feature 的均值/方差波动；冻结单图几何 backbone，只训练一个因果 recurrent normalization module。
- 仅增加约 **2% 参数**，时间稳定性最高提升约 14%，同时保留单图精度。
- 评价：这是极具迁移性的“小适配器”思想：不要重训整套几何模型，只校正决定视频尺度/shift 的统计量。

### 3.6 新场景泛化与测试时适配

#### Online3R — CVPR 2026

- 链接：[CVF PDF](https://openaccess.thecvf.com/content/CVPR2026/papers/Zhou_Online3R_Online_Learning_for_Consistent_Sequential_Reconstruction_Based_on_Geometry_CVPR_2026_paper.pdf) · [arXiv](https://arxiv.org/abs/2604.09480)
- 冻结 MASt3R 等几何基础模型，只在线更新少量 visual prompt，以编码当前环境的 scene-specific prior。
- 局部约束从历史融合结果产生伪真值；全局约束只在稀疏远距离关键帧上计算，降低在线更新开销。
- 评价：这是最直接回答“怎样适应从未见过的新场景”的顶会工作。风险是在线伪标签错误会自我强化，需要置信度、回滚和场景切换检测。

#### VGGT-$\Omega$ / DA3 / Depth Anything：数据规模带来的零样本适配

- VGGT-$\Omega$ 用 15× 监督数据、18M 无标注视频和自监督协议扩展静态/动态覆盖。
- DA3 用更简洁的 depth-ray 目标和 DA2 teacher 保留细节与跨域鲁棒性。
- Depth Anything V1/V2 证明海量无标注图像、强 teacher 与伪标签是降低新域误差的有效方式。
- 评价：这是**训练前扩大支持域**，不是测试时适配。它通常稳定、零额外延迟，但无法针对单个新场景纠正系统性 bias。

#### MapAnything — 3DV 2026（相关补充）

- 链接：[project](https://map-anything.github.io/) · [arXiv](https://arxiv.org/abs/2509.13414)
- 同一模型可接收图像及可选 intrinsics、pose、depth、partial reconstruction，输出 metric depth、ray、pose 与尺度。
- 评价：把已有传感器/先验当作输入提示，比纯 RGB 模型测试时“猜 metric scale”稳得多。它非常适合与 VGGT-Long 的 SE(3) 对齐结合，减少 Sim(3) 尺度自由度。

## 4. 一张表看懂选型

| 工作 | 正式发表 | 输入/输出 | 在线 | GPU 峰值能否与序列长度解耦 | 需要重训 | 新场景机制 | 最适合 |
|---|---|---|---:|---:|---:|---|---|
| VGGT / $\pi^3$ / DA3 | CVPR 2025 / ICLR 2026 | pose + depth + pointmap | 否 | 否 | — | 大规模预训练 | 短/中等多视图，最高局部精度 |
| VGGT-$\Omega$ | CVPR 2026 | pose + depth，静态/动态 | 否 | 否 | — | 大规模无标注视频自监督 | 更鲁棒的通用 backbone |
| FastVGGT / AVGGT / HTTM / LiteVGGT | ICLR/CVPR 2026 | 保持 VGGT 输出 | 否 | 通常否，只显著降低常数 | 否或轻微 | 无 | 现有 VGGT 推理加速 |
| Fast3R | CVPR 2025 | 大规模无序图集 pose + pointmap | 否 | 否 | 是 | 大规模多视图训练 | 1000+ 图单次前向速度基线 |
| QuantVGGT | ICLR 2026 | 保持 VGGT 输出 | 否 | 否，降低模型/激活成本 | PTQ | 无 | 小显存、低精度部署 |
| CUT3R / LONG3R | CVPR/ICCV 2025 | 流式 pose + pointmap | 是 | 近似是 | 是 | learned recurrent state | 通用实时流式重建 |
| StreamVGGT / STream3R | ICLR 2026 | 流式 3D/4D geometry | 是 | 否，普通 KV cache 会增长 | 是 | 蒸馏/大规模训练 | 中长序列、低增量延迟 |
| IncVGGT | ICLR 2026 | 流式 VGGT geometry | 是 | **是** | 否 | 相关性 top-$k$ cache | 训练免费、超长序列 |
| TTT3R | ICLR 2026 | 流式 pointmap/pose | 是 | **是** | 否 | 置信度控制状态更新 | 数千帧、6 GB 级部署 |
| LongStream | CVPR 2026 | metric streaming geometry | 是 | 设计目标为有界/周期 cache | 是 | keyframe-relative gauge + scale 解耦 | 公里级严格在线 |
| VGG-T\(^3\) | CVPR 2026 | 离线全局 geometry + query localization | 否 | **是** | 是 | fast-weight scene state | 大图集、建图后定位 |
| ZipMap | CVPR 2026 | 双向 geometry + state query | 可扩展 | **是** | 是 | TTT hidden scene state | 极快大图集重建 |
| Scal3R | CVPR 2026 | 长视频 geometry | 可顺序/并行 | **是/近似是** | 是 | 自监督更新全局神经记忆 | 大场景 + 场景适配 |
| VGGT-Long / Pi-Long / DA3-Streaming | ICRA 2026 / 工程扩展 | chunk pose/depth/pointmap | 准在线 | **GPU 是** | 否 | 显式对齐与回环 | 最快落地、backbone 可替换 |
| LASER | CVPR 2026 | streaming 4D pointmap/pose | 是 | **是** | 否 | layer-wise scale alignment | 6 GB、公里级、动态视频 |
| AMB3R-VO | CVPR 2026 | metric-scale VO + dense map | 是 | **GPU 工作集是** | VO 扩展否 | active/global keyframe memory | 未标定长序列与 metric scale |
| MERG3R | CVPR 2026 | 大规模无序图集 | 否 | **局部 GPU 是** | 否 | 全局 BA | 无序照片与超显存集合 |
| Online3R | CVPR 2026 | 顺序重建 | 是 | 取决于基础系统 | 只更新 prompt | **局部+全局自监督 TTA** | 新环境持续适配 |
| Video Depth Anything | CVPR 2025 | 长视频相对深度 | 窗口式 | **是** | 是 | DA2 泛化 + keyframe | 只要稳定深度 |
| FlashDepth / DyFN | ICCV 2025 / CVPR 2026 | 在线视频深度/几何 | 是 | **是** | 小模块 | recurrent feature/statistics | 高分辨率、低延迟稳定深度 |

## 5. 2026 年重要预印本：值得跟踪，但不要当作已录用论文

### LoGeR：目前最完整的“局部无损 + 全局压缩”方案

- 链接：[project](https://loger-project.github.io/) · [arXiv](https://arxiv.org/abs/2603.03269)
- 每个 chunk 内做双向几何推理；跨 chunk 同时使用 Sliding Window Attention 保存最近未压缩 token，和 TTT fast weights 压缩全局坐标信息。
- 只用 128 帧训练，测试扩展到 19k 帧 VBR；无后端优化，KITTI ATE 相对既有 feed-forward 方法报告下降超过 74%。
- 研究判断：它最准确地抓住了长序列的两类信息需求。如果后续复现稳定，混合记忆很可能比“纯 KV cache”或“纯单状态 RNN”更有生命力。

### InfiniteVGGT / RetrieveVGGT / FrameVGGT：固定预算的历史选择

- [InfiniteVGGT](https://arxiv.org/abs/2601.02281)：训练免费 rolling memory，目标是 endless streams，并发布 Long3D benchmark。
- [RetrieveVGGT](https://arxiv.org/abs/2605.09644)：直接用 attention query-key 相似性检索历史，报告相对 StreamVGGT、TTT3R、InfiniteVGGT更好且内存常数。
- [FrameVGGT](https://arxiv.org/abs/2603.07690)：将一帧的 KV 增量作为完整 evidence block，以 rolling explicit memory 避免逐 token 裁剪破坏几何证据。
- 研究判断：历史压缩不应只追求 top-$k$ token；以 frame / keyframe / submap 为基本记忆单元，通常更符合多视图几何的可观测性结构。

### R\(^3\)：用相对回归消除无限增长坐标

- 链接：[arXiv](https://arxiv.org/abs/2605.26519) · [model](https://huggingface.co/KevinXu02/R3)
- 基于 DA3 backbone，用轻量 MLP 预测带置信度的相对 pose 约束，而不是相对固定世界原点回归所有绝对 pose。
- 同时支持全上下文离线和有界内存因果流式。
- 研究判断：与 LongStream 的 keyframe-relative pose 结论相互印证——长视频 pose 表示应当是局部相对/规范自由的，全球坐标交给图或记忆系统聚合。

### ViGeo：同一模型统一 full-sequence / streaming / long-video

- 链接：[project](https://pkqbajng.github.io/ViGeo/) · [arXiv](https://arxiv.org/abs/2605.30060)
- dynamic chunking attention 让同一训练模型在完整序列、在线和 chunk 模式间切换，输出 depth、point、normal、confidence、pose。
- 研究判断：统一训练/推理模式很有吸引力，避免分别维护 offline、streaming 两套模型；仍需等待正式评审与更广泛复现。

### SAGE / Self-Geometry：专门面向适配

- [SAGE](https://arxiv.org/abs/2602.07891)：从互联网视频挖训练轨迹，以 SfM 稀疏 anchor + 3DGS 可微渲染一致性构造弱监督，并用 anchor data 防遗忘；在 7Scenes、TUM-RGBD、Matterport3D 等未见基准报告 Chamfer Distance 下降 20–42%。它是**离线扩展训练数据**。
- [Self-Geometry](https://arxiv.org/abs/2608.10708)：用 2D correspondence 产生显式多视图几何伪真值，以 LoRA 在测试时适配 VGGT、$\pi^3$ 与多个 DA3 尺寸；它是**真正的单场景 TTA**。
- 研究判断：前者解决数据墙，后者解决部署时域偏移；可以串联，而不是二选一。

### VGGT-Align：切块法的尺度漂移修正

- 链接：[arXiv](https://arxiv.org/abs/2608.15260)
- 从每块点云提取几何不变量，建立独立于点云配准的跨块尺度约束，把 7-DoF Sim(3) 对齐退化为 6-DoF rigid transform，以切断链式尺度误差。
- 研究判断：这是对 VGGT-Long / LASER 的又一补充：如果 metric 或几何不变量足够可靠，应尽早消掉 scale 自由度，而不是让每个窗口都重新估尺度。

### oVDA：Video Depth Anything 的在线化

- 链接：[arXiv](https://arxiv.org/abs/2510.09182)
- 对 Video Depth Anything 使用 latent KV cache 和训练时 frame masking，报告 A100 42 FPS、Jetson 20 FPS，并显著降低 VRAM。
- 研究判断：只做 depth 时，它可能比迁移完整 VGGT streaming architecture 更符合边缘设备预算。

## 6. 研究品味：哪些方向更可能继续有效

### 6.1 最有前景的组合不是“再做一个更大 VGGT”

一个合理的下一代长序列几何模型可以组合四个互补思想：

```text
每帧/每小块高质量局部几何
  VGGT-Ω / π³ / DA3
          │
          ▼
局部未压缩短期记忆 ── SWA / frame evidence
          │
          ▼
固定规模全局神经记忆 ── TTT / fast weights / register memory
          │
          ├── 相对 pose / gauge-free 输出，避免坐标外推
          │
          └── 可检索关键帧图 + 显式回环，纠正长期漂移
```

仅增大 backbone 通常会提高单块精度，却不自动解决跨块 gauge、记忆淘汰与 loop closure。

### 6.2 新场景适配应是“受控的小更新”

推荐优先级：

1. 冻结 backbone，只更新 feature statistics、visual prompts、register memory 或 LoRA；
2. 用多视图 correspondence、局部/全局闭环和稀疏 sensor anchor 作为自监督；
3. 以置信度决定是否更新，并维护可回滚的稳定 checkpoint；
4. 检测场景切换后再清空或分支记忆，避免把旧场景 prompt 污染到新场景；
5. 最后才考虑全模型在线 fine-tuning。

Online3R、DyFN、Self-Geometry 的共同启示是：新场景适配未必需要修改十亿参数，**更关键的是选择正确的低维自由度和可靠监督信号**。

### 6.3 记忆淘汰必须尊重几何，而不是只看 feature similarity

应保留的内容不只是“与当前帧最相似”的 token，还包括：

- 提供最大视差、能约束尺度和旋转的关键帧；
- 可能形成回环的长期地点描述子；
- 低纹理区域的结构线/平面/重力方向；
- 动态区的独立运动状态，而不是把它混入静态地图；
- 置信度不高但观测稀有的视角。

因此，frame/submap-level evidence、可观测性评分和拓扑记忆，往往比简单 token top-$k$ 更稳。

### 6.4 评价协议应专门检查“长度外泛化”

建议至少报告：

- 误差随帧数/里程的曲线，而不是只给整段平均 ATE；
- 峰值 GPU 显存、CPU 内存、磁盘增长、单帧延迟 p50/p95、总能耗；
- 训练长度 $T_{\mathrm{train}}$ 与测试长度 $T_{\mathrm{test}}$ 的比例；
- 是否严格因果、是否看未来帧、是否使用回环/BA/外部 depth/标定；
- 静态、动态、低纹理、重复纹理、曝光变化、焦距变化与场景切换；
- 新场景适配前后，以及适配失败时能否回滚；
- 关键帧采样率和输入分辨率，因为“1000 帧”在 224p 与 1k/2k 分辨率下不是同一问题。

目前各论文硬件、分辨率、frame stride、输出类型和是否包含后端的差异很大，单看“FPS”非常容易误判。

## 7. 面向不同目标的推荐阅读与复现顺序

### 目标 A：24 GB 内做长视频相机轨迹 + 稠密点云

1. VGGT-Long 或 DA3-Streaming：先获得稳定可运行基线；
2. LASER：检查 layer-wise scale alignment 是否显著改善窗口接缝；
3. IncVGGT / TTT3R：比较固定 cache 与固定 recurrent state；
4. 加 DINO/几何混合回环，而不是只依赖相邻窗口；
5. 新场景偏差明显时，再加 Online3R 式 prompt 或 Self-Geometry 式 LoRA。

### 目标 B：最高吞吐的大规模离线图像集

1. FastVGGT / AVGGT：最小改动 benchmark；
2. VGG-T\(^3\) 与 ZipMap：测试真正线性 fast-weight memory；
3. 无序图集加入 MERG3R；
4. 需要 relocalization 时优先 VGG-T\(^3\) 的 scene-state query。

### 目标 C：机器人严格在线与新环境适配

1. LongStream：相对 pose、尺度解耦、cache-consistent training；
2. TTT3R / IncVGGT：控制显存与历史遗忘；
3. Online3R / DyFN：小参数在线适配；
4. 保留传统稀疏 factor graph / loop closure 作为安全后端；
5. 需要 metric scale 时加入 AMB3R-VO 式紧凑体素/关键帧后端；若有 intrinsics、稀疏深度或 IMU，则使用 MapAnything 式条件输入并优先 SE(3) 而非 Sim(3) 对齐。

### 目标 D：只需长视频稳定深度

1. Video Depth Anything：长视频离线/窗口式高质量；
2. FlashDepth：2K 分辨率实时流；
3. oVDA：Jetson/低显存在线；
4. DyFN：给任意单图几何模型增加极小的时序稳定模块。

## 8. 精选阅读顺序

1. [VGGT, CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Wang_VGGT_Visual_Geometry_Grounded_Transformer_CVPR_2025_paper.html)：理解 alternating frame/global attention 和统一几何输出。
2. [$\pi^3$, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/11a09e0aaa74867c6b0719c639fc09f8-Abstract-Conference.html)：理解 reference-free / permutation-equivariant geometry。
3. [Video Depth Anything, CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Chen_Video_Depth_Anything_Consistent_Depth_Estimation_for_Super-Long_Videos_CVPR_2025_paper.html)：最干净的长视频深度基线。
4. [VGGT-Long, ICRA 2026](https://arxiv.org/abs/2507.16443)：最简单实用的 chunk-align-loop 系统。
5. [StreamVGGT, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/8da04a60948be713dc766f0c7e3a5b1f-Abstract-Conference.html) → [IncVGGT](https://proceedings.iclr.cc/paper_files/paper/2026/hash/0a4096f09ab230082df548f901d4f79e-Abstract-Conference.html)：看清“因果 cache”到“有界 cache”的差别。
6. [TTT3R, ICLR 2026](https://arxiv.org/abs/2509.26645) → [VGG-T\(^3\), CVPR 2026](https://research.nvidia.com/labs/dvl/projects/vgg-ttt/) → [ZipMap, CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/html/Jin_ZipMap_Linear-Time_Stateful_3D_Reconstruction_via_Test-Time_Training_CVPR_2026_paper.html)：理解 TTT 在状态更新、全局记忆和场景查询中的三种用法。
7. [LongStream, CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/html/Cheng_LongStream_Long-Sequence_Streaming_Autoregressive_Visual_Geometry_CVPR_2026_paper.html)：看完整的 gauge、scale、cache 联合设计。
8. [LASER, CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/html/Ding_LASER_Layer-wise_Scale_Alignment_for_Training-Free_Streaming_4D_Reconstruction_CVPR_2026_paper.html)：理解窗口 Sim(3) 为什么仍会失败。
9. [Online3R, CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/papers/Zhou_Online3R_Online_Learning_for_Consistent_Sequential_Reconstruction_Based_on_Geometry_CVPR_2026_paper.pdf)：真正的新场景在线适配。
10. [LoGeR, arXiv 2026](https://arxiv.org/abs/2603.03269)：当前最值得追踪的混合记忆方向。

## 9. 最终判断

如果研究问题是“让 VGGT / $\pi^3$ / DA3 / VGGT-$\Omega$ 在更长视频上低开销、快速并适应新场景”，最有含金量的切入点不是孤立地做 token pruning，而是同时处理三件事：

\[
\boxed{\text{local lossless geometry}}
\; + \;
\boxed{\text{bounded global memory}}
\; + \;
\boxed{\text{confidence-controlled scene adaptation}}
\]

具体而言，**$\pi^3$/R\(^3\)/LongStream 的相对或 gauge-free 几何表示 + LoGeR/VGG-T\(^3\)/Scal3R 的固定规模神经记忆 + LASER/TALO 的显式跨块约束 + Online3R/Self-Geometry 的小参数适配**，比单独扩大模型或单独稀疏注意力更可能在真实公里级、动态、未知场景中取得稳健收益。
