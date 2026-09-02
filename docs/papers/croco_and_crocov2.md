# CroCo 与 CroCo v2：从跨视角补全到通用几何视觉骨干

> 面向刚入门的读者；资料检索截止到 **2026-09-02**。  
> 本文重点不是罗列所有引用 CroCo 的论文，而是回答三件事：CroCo 究竟学到了什么；证据有多强；它怎样演化为 DUSt3R 等现代 3D 视觉工作的技术起点。

## 0. 先给结论

CroCo（Cross-view Completion）的核心想法非常简洁：

> 不再让模型只根据一张被遮住的图像猜像素，而是给它同一场景的另一个视角，让它利用第二张图像去补全第一张图像。

这一个变化，把 MAE 式单图掩码建模中偏向“根据语义和纹理猜缺失内容”的问题，改造成了一个天然要求模型理解**跨视角对应、遮挡、视差和场景几何**的问题。CroCo 没有显式提供深度、光流或匹配标签，但想做好补全，模型就必须在内部回答：“参考图的哪个区域对应目标图的这个位置？”

CroCo v2 则把这个漂亮但尚显实验性的想法工程化、规模化：引入约 530 万真实图像对、2D RoPE 相对位置编码、更大的编码器与解码器，并把同一套骨干直接微调到立体匹配和光流。它证明了：在合适的跨视角预训练之后，一个不依赖 cost volume、warping、迭代更新或特征金字塔的通用 Transformer，也能成为很强的双目几何模型。

我对这条工作线的学术判断是：

1. **CroCo 最重要的贡献不是某个榜单数字，而是提出了一种正确的预训练偏置**：以“另一视角中的可观测证据”替代单图幻想，令自监督视觉预训练主动学习几何关系。
2. **CroCo v2 最重要的贡献是把这种偏置变成可复用的模型资产**：真实图像对、RoPE、高分辨率适应性，以及已经预训练好的跨注意力解码器，共同构成后续方法可直接继承的起点。
3. **DUSt3R 是这条脉络的关键转折点**：它继承 CroCo v2 的架构和权重，把“隐式的跨视角几何”改造成受监督的显式 3D pointmap。其后的 MASt3R、MonST3R、Fast3R、MUSt3R 等，更多是 DUSt3R 的后代，不能把它们的全部成功都归功于 CroCo。
4. **ZeroCo 给出了最直接的机理证据**：不重新训练，直接读取 CroCo v2 解码器的 cross-attention，就能得到很强的零样本对应关系。这比“下游任务分数提高了”更接近对 CroCo 原始假说的直接验证。
5. CroCo 不是“已经学会完整 3D 世界模型”。RGB 重建损失只会鼓励、不会保证度量 3D；不重叠区域、动态场景、多视图长期一致性仍需 Alligat0R、CroCo-Man、MuM、DUSt3R 家族等工作补足。

---

## 1. 阅读前需要的最少背景

### 1.1 什么是对应关系？

同一个三维点从两个相机观察，会投影到两张图像中的不同像素。找到这两个像素的关系，就是 correspondence（对应）。

- 相机只发生小的水平位移时，对应点的水平位移叫**视差**，可用于立体深度估计。
- 相邻视频帧之间每个像素的位移叫**光流**。
- 若知道足够多的对应点，可估计两相机的相对姿态；再结合多视图约束，可做三维重建和 SLAM。

传统方法常把这些结构显式写进系统：构造 cost volume、做特征相关、warping、PnP 或 bundle adjustment。CroCo 提出的问题是：能不能先用一个通用预训练任务，让 Transformer 自己在内部形成这套能力？

### 1.2 MAE 为什么不够“几何”？

MAE 将一张图的大量 patch 遮住，再从剩余 patch 恢复像素。它很适合学习物体、场景和纹理的统计规律，但被遮住的区域在单张图中常常没有唯一答案。模型可以靠“这看起来像一只猫，所以这里大概是猫腿”完成任务，不一定需要理解相机运动和三维结构。

CroCo 的洞见是：如果同时给出同一场景的另一张图，被遮区域的一部分内容不再只能靠猜——它在另一视角中可能真实可见。模型若想利用这些证据，就必须学习跨视角对应。

---

## 2. CroCo（NeurIPS 2022）在做什么？

原论文：[CroCo: Self-Supervised Pre-training for 3D Vision Tasks by Cross-View Completion](https://arxiv.org/abs/2210.10716)；[NeurIPS 论文 PDF](https://proceedings.neurips.cc/paper_files/paper/2022/file/16e71d1a24b98a02c17b1be1f634f979-Paper-Conference.pdf)。

### 2.1 预训练任务

给定同一场景的两张图像 (I_1,I_2)：

1. 把 (I_1) 切成 patch，随机遮住其中 **90%**；(I_2) 完整保留。
2. 用共享权重的 Siamese ViT 编码器分别编码 (I_1) 的可见 patch 和完整的 (I_2)。
3. 解码器先在目标图 token 内做 self-attention，再通过 cross-attention 查询参考图特征。
4. 只对 (I_1) 中被遮 patch 的归一化 RGB 像素计算均方误差。

可粗略写成：

\[
\hat P_1=D\big(E(\widetilde P_1),E(P_2)\big),\qquad
\mathcal L=\frac{1}{|\mathcal M|}\sum_{i\in\mathcal M}\|\hat P_{1,i}-P_{1,i}\|_2^2.
\]

这里的关键不是公式本身，而是信息流：**目标图缺失的信息必须尽量从参考图跨视角取回**。cross-attention 因而有动力学习隐式匹配。

### 2.2 数据与结构

- 编码器为 ViT-B/16：12 层、768 维、12 个注意力头。
- 解码器为 8 个 CrossBlock：512 维、16 个头。
- 输入为 (224\times224)，训练 400 epochs。
- 预训练使用 Habitat 模拟器，从 HM3D、ScanNet、Replica、ReplicaCAD 场景生成约 **182 万**对图像。
- 论文按共视程度筛选图像对。实验显示，约 50% 的重叠最合适：太少时参考图帮不上忙，问题退化成单图 MIM；太多时两张图近似相同，容易变成复制粘贴。

### 2.3 下游任务怎样使用它？

- 单目任务主要使用预训练编码器，例如单目深度、语义分割、Taskonomy 稠密预测和线性分类。
- 双目任务可直接继承编码器和跨注意力解码器，例如光流、相对位姿和立体匹配。

这点很重要：MAE 传统上主要产出一个可迁移的编码器；CroCo 则把**融合两张图的解码器**也预训练成了有价值的资产。

### 2.4 论文真正证明了什么？

几个消融最值得记住：

| 实验 | 结果或现象 | 能支持的结论 |
|---|---:|---|
| 遮挡率 | 90% 优于更低遮挡率 | 参考视角提供了额外信息，因此模型可承受比 MAE 常用的 75% 更高遮挡；高遮挡也减少仅靠目标图局部纹理完成任务的捷径。 |
| 真实双视角 vs. 单图几何变换 | ADE20K mIoU 38.8 vs. 27.0；NYUv2 深度 \(\delta_1\) 86.8 vs. 66.1 | 简单旋转/缩放一张图不能代替真实相机视角变化；视差、遮挡和真实共视结构是关键。 |
| 同一 Habitat 数据上 CroCo vs. MAE | NYUv2 \(\delta_1\)：85.6 vs. 79.0；Taskonomy 平均误差：33.00 vs. 35.65（越低越好） | 收益不只是来自合成数据，跨视角目标本身更适合稠密几何任务。 |
| 光流的编码器/解码器初始化 | 全随机 Sintel clean/final EPE 18.81/18.97；MAE 编码器+随机解码器 4.63/5.24；CroCo 全模型 3.00/3.60 | 已预训练的跨视角解码器确实包含有用的双目关系建模能力。 |

但也要看到边界：CroCo 在同样 Habitat 数据上的 ImageNet 线性分类只有 37.0，虽高于该数据上 MAE 的 32.5，却远低于用大规模自然图像做语义预训练的方法。它说明的不是“CroCo 全面优于 MAE”，而是：**预训练任务与数据会决定表征擅长什么；CroCo 的优势尤其集中在稠密几何与跨视角任务。**

### 2.5 CroCo 的意义

从学术思想看，CroCo 完成了三个转变：

1. **从单图先验到跨视角证据。** 缺失内容不再完全靠语义想象，而要从另一观察中寻找。
2. **从任务专用几何模块到通用预训练。** 它尝试用一个统一 Transformer，为深度、光流、位姿、立体等任务提供共同起点。
3. **从只预训练 encoder 到预训练 relation module。** cross-attention decoder 本身成为可迁移资产。

这也是为什么它后来能自然过渡到 DUSt3R：如果解码器已经学会在两幅图之间交换几何信息，只需把输出从 RGB patch 改成 3D 点，架构就可以成为显式几何预测器。

---

## 3. CroCo v2（ICCV 2023）改进了什么？

原论文：[CroCo v2: Improved Cross-view Completion Pre-training for Stereo Matching and Optical Flow](https://arxiv.org/abs/2211.10408)；[ICCV/CVF 页面](https://openaccess.thecvf.com/content/ICCV2023/html/Weinzaepfel_CroCo_v2_Improved_Cross-view_Completion_Pre-training_for_Stereo_Matching_and_ICCV_2023_paper.html)；[官方代码与权重](https://github.com/naver/croco)。

CroCo v2 没有改变“跨视角补全”这个核心目标，而是补齐 v1 的三个实际短板。

### 3.1 从合成数据走向大规模真实图像对

v2 新增约 **530 万**真实图像对：

| 数据源 | 图像对数量（论文） | 主要来源 |
|---|---:|---|
| ARKitScenes | 1,070,414 | 室内移动设备扫描 |
| MegaDepth | 2,014,789 | 互联网照片与 SfM |
| 3DStreetView | 655,464 | 街景 |
| IndoorVL | 1,593,689 | 室内视觉定位数据 |

再加 v1 的 182 万 Habitat 合成图像对，总量约 **710 万对**。论文借助已有 mesh、SfM、LiDAR 或位姿元数据估计共视区域，并从对应区域裁出训练图像对。

这里有一个容易误解的细节：CroCo 的训练目标是自监督的——目标就是原始 RGB，不需人工深度/光流标注；但 v2 的**图像对挖掘和裁剪**会利用数据集已有几何或相机元数据。因此，“完全不使用任何几何信息”并不是准确表述。

### 3.2 用 2D RoPE 取代绝对位置编码

v1 的绝对正弦位置编码对训练分辨率和裁剪方式较敏感。v2 使用二维 Rotary Positional Embedding（RoPE），让注意力更自然地依赖 token 间相对位置，从而更好地迁移到任意长宽比和更高测试分辨率。

消融中，仅把位置编码换成 RoPE，就将高分辨率 ETH3D 立体误差从 1.82 降到 0.60；不过它并非在每个指标上都单调变好，例如部分 Sintel 指标略退化。正确结论是：**RoPE 对跨分辨率泛化尤其关键，而不是一个在所有数据上独立包赢的模块。**

### 3.3 扩大模型，尤其是跨视角解码器

- 编码器由 ViT-B 扩为 ViT-L：24 层、1024 维、16 个头。
- 解码器由小型 8 层结构扩为 ViT-B 规模：12 层、768 维、12 个头。

扩大解码器很有针对性，因为两幅图的信息融合主要发生在那里。v2 的最佳模型因此不只是“更大编码器”，而是把容量加到了真正承担跨视角推理的位置。

### 3.4 下游：CroCo-Stereo 与 CroCo-Flow

微调时不再遮挡输入，两张完整图经过共享编码器和跨注意力解码器，再由 DPT 风格稠密预测头输出视差或光流。模型使用 Laplacian uncertainty loss，同时预测结果和不确定性。

值得注意的是，它没有传统立体/光流系统常见的 cost volume、显式 warping、迭代 refinement 或多尺度金字塔。论文发表时，CroCo-Flow 在 MPI-Sintel 测试集达到 clean/final EPE 1.09/2.44，在 KITTI 2015 达到 F1-all 3.64，并在 Spring 等高分辨率数据上表现突出。这些结果的价值在于证明通用预训练骨干可以承担以往由大量任务专用结构承担的工作，而不应只理解为一次排行榜竞争。

### 3.5 v2 消融怎样读？

| 逐步变化 | Middlebury bad@1 ↓ | ETH3D bad@1 ↓ | FlyingThings Flow clean/final EPE ↓ | Sintel clean/final EPE ↓ |
|---|---:|---:|---:|---:|
| v1：绝对位置、ViT-B、小解码器、182 万 Habitat 对 | 26.3 | 1.82 | 3.89 / 3.56 | 2.07 / 2.57 |
| + RoPE | 25.3 | 0.60 | 3.73 / 3.37 | 2.13 / 2.77 |
| + 530 万真实图像对 | 20.7 | 0.82 | 3.35 / 2.94 | 1.76 / 2.30 |
| + Base 解码器 | 17.1 | 1.14 | 3.10 / 2.73 | 1.51 / 1.99 |
| + ViT-L 编码器（完整 v2） | 15.5 | 0.38 | 2.85 / 2.45 | 1.43 / 1.99 |

这张表给出的严谨结论是：真实数据、模型容量和 RoPE 总体上互补，但不同数据集并非每一步都单调改善。v2 是一个**复合训练配方**，不能把全部提升简单归因于单一模块。

更强的证据来自“相同最终结构，是否预训练”的比较：随机初始化与 CroCo v2 预训练相比，Middlebury bad@1 为 43.4 vs. 15.5，FlyingThings final flow EPE 为 10.57 vs. 2.45。也就是说，强结果并不只是大模型带来的，跨视角补全预训练是决定性因素之一。

### 3.6 v1 与 v2 的一句话区别

| | CroCo | CroCo v2 |
|---|---|---|
| 核心贡献 | 证明 cross-view completion 是有效的几何预训练目标 | 把目标扩展成可规模化、可高分辨率迁移的强骨干 |
| 数据 | 约 182 万合成图像对 | 合成 + 约 530 万真实图像对 |
| 位置编码 | 绝对正弦位置编码 | 2D RoPE |
| 最大模型 | ViT-B + 小解码器 | ViT-L + Base 解码器 |
| 代表意义 | 概念验证 | 可复用模型与双目任务强基线 |

---

## 4. 发展脉络：哪些工作真正“基于”CroCo？

先看一棵简化的谱系树：

```text
MAE / masked image modeling
└── CroCo (2022): 单图补全 → 跨视角补全
    ├── CroCo v2 (2023): 真实图像对 + 2D RoPE + 扩模
    │   ├── SACReg：图像 + 稀疏场景坐标 → 稠密坐标与定位
    │   ├── DEBiT / GOAT：跨视角特征用于具身导航
    │   ├── 自监督单目深度与 VO
    │   ├── ZeroCo：直接读取 cross-attention 得到零样本对应
    │   ├── Co-op：新物体模板—查询图对应与位姿
    │   ├── CroCoDiLight：冻结编码器，分解光照与场景因素
    │   └── DUSt3R：RGB 补全 → 显式 3D pointmap
    │       ├── MASt3R：加入局部描述子和显式匹配
    │       │   ├── Splatt3R / NoPoSplat：无位姿 3D Gaussian / 新视角合成
    │       │   └── 其他重建与定位系统
    │       ├── Spann3R / SLAM3R：流式或实时重建
    │       ├── MonST3R：动态场景与视频 4D
    │       ├── Fast3R / MUSt3R：从图像对扩展到多视图
    │       ├── Reloc3r：相对位姿与定位
    │       └── CUT3R：持久状态与在线 3D 推理
    ├── MIMIC：改造真实图像对的收集方式
    ├── CroCo-Man：人体跨视角与跨姿态补全
    ├── Alligat0R：将 RGB 补全改成共视/遮挡分割
    └── MuM：从非对称双视图扩展到统一、多视图掩码建模
```

这里必须区分三类关系：

- **直接继承**：明确使用 CroCo/CroCo v2 权重、代码或 CrossBlock 架构。
- **目标延伸或对照**：保留“跨视角自监督几何”思想，但改变数据、预测目标或视图组织。
- **间接继承**：从 DUSt3R/MASt3R 权重开始，因而有 CroCo 血统，但实验并未单独检验 CroCo 的贡献。

下面按这个区分整理。证据等级含义为：**A** = 直接机理或受控消融；**B** = 直接使用并有较明确消融/迁移证据；**C** = 继承系统有效，但无法隔离 CroCo 的独立作用。

---

## 5. 第一条支线：改造预训练数据、目标和视图组织

### 5.1 MIMIC：CroCo 的收益是不是合成数据偶然造成的？

论文：[MIMIC: Masked Image Modeling with Image Correspondences](https://arxiv.org/abs/2306.15128)，CVPR 2024 3DMV Workshop。

MIMIC 的主要贡献不是发明新的 CroCo 网络，而是构建真实图像对的方法。它从真实视频和合成数据中利用图像对应、单应性与重叠度筛选图像对，不要求完整 3D mesh 或精确相机位姿，得到最多约 310 万对数据，再使用 CroCo 目标预训练。

- **利用了什么**：CroCo 的非对称双视图补全目标和架构。
- **验证了什么**：在 NYUv2 深度、Taskonomy 法线等任务上，真实对应数据预训练优于原 Habitat CroCo；因此 CroCo 的几何收益不是模拟器风格的偶然产物，图像对的真实性与多样性很重要。
- **学术意义**：把问题从“要不要跨视角补全”推进到“怎样便宜、可靠地挖掘训练图像对”。
- **证据等级**：A/B；它直接控制了预训练数据，但与 v2 的完整大规模配方并不完全等价。

### 5.2 CroCo-Man：静态场景目标能否迁移到非刚性人体？

论文：[Cross-view and Cross-pose Completion for 3D Human Understanding](https://arxiv.org/abs/2311.09104)，CVPR 2024。

该工作常被简称为 CroCo-Body、CroCo-Hand 或 CroCo-Man。它除了使用同一时刻的多视角人体图像，还使用同一人物在不同时刻/姿态下的图像做 cross-pose completion，并加入人体感知的遮挡策略。

- **利用了什么**：CroCo 权重、跨注意力补全架构和“从另一观察补足当前观察”的训练思想。
- **新增了什么**：人体域数据、跨姿态而非只跨相机、人体感知 masking。
- **验证了什么**：在人体 mesh 恢复、DensePose、手部/手势和抓取相关任务上，领域化预训练优于 MAE 和通用 CroCo；随机初始化也明显更差。跨姿态数据在多视图数据稀缺时尤其有用。
- **重要限制**：原始 CroCo 只在静态场景对上训练，不能自动得到完整的非刚性运动先验；跨姿态能力来自新的配对数据与训练设计。
- **证据等级**：B。

### 5.3 Alligat0R：在不共视区域，RGB 补全是不是错误目标？

论文：[Alligat0R: Pre-Training Through Co-Visibility Segmentation for Relative Camera Pose Regression](https://arxiv.org/abs/2503.07561)，NeurIPS 2025 Spotlight。

Alligat0R 对 CroCo 提出了很有学术价值的批评：如果目标图的区域在参考图中根本不可见，让模型恢复 RGB 是病态问题，它只能幻想。作者改为预测每个位置属于“共视、被遮挡、参考相机视野外”哪一类，再将预训练迁移到相对位姿回归。

- **利用/继承了什么**：CroCo 的核心问题设置——从两视图关系学习几何。
- **改变了什么**：把像素重建改为直接的共视与遮挡分割。
- **验证了什么**：相对位姿，尤其低重叠情况下更强；说明 CroCo 的跨视角方向是对的，但“应该预测 RGB”不是唯一、也未必总是最合适的答案。
- **证据等级**：A，属于对原始 pretext task 的直接反思。

### 5.4 MuM：为什么必须固定一张完整参考图？

论文：[MuM: Multi-View Masked Image Modeling for 3D Vision](https://arxiv.org/abs/2511.17309)，CVPR 2026；[官方代码](https://github.com/davnords/MuM)。

MuM 明确沿着 CroCo 前进，但去掉“目标图 90% 被遮、参考图完全可见”的固定非对称结构。它支持 2–24 个视图，对所有视图统一遮挡，使用轻量跨帧注意力解码器，并可混合单视图与多视图训练。

- **利用了什么**：masked RGB prediction 能诱导几何表征这一 CroCo 核心假设。
- **改变了什么**：双视图变多视图，非对称 masking 变成统一 masking；重点把几何能力保留在可冻结使用的 encoder 中。
- **验证了什么**：冻结编码器后，在重建、匹配和位姿任务上优于 CroCo v2 等基线；说明跨视角掩码预测可以扩展成更一般的多视图表征学习，永久保留一张完整参考图并非必要条件。
- **证据等级**：A/B；它验证的是 CroCo 思想的可扩展性，同时也揭示 v1/v2 的成对、非对称设计不是终点。

---

## 6. 第二条支线：直接使用 CroCo v2 的关系表征

### 6.1 SACReg：从稀疏 2D–3D 坐标传播到整张图

论文：[SACReg: Scene-Agnostic Coordinate Regression for Visual Localization](https://arxiv.org/abs/2307.11702)，CVPR 2024 3DMV Workshop。

给定查询图和数据库图，数据库图只有稀疏 2D–3D 场景坐标。SACReg 用 CroCo v2 的双分支和 cross-attention 将稀疏坐标信息传播成查询图的稠密场景坐标与置信度，再通过 PnP 定位。

- **利用了什么**：CroCo v2 权重、两图 cross-attention、RoPE 带来的高分辨率适应性。
- **验证了什么**：去掉 CroCo 初始化会显著下降；冻结 ViT encoder 反而更好，且 cross-attention 可视化呈现隐式图像匹配。它证明预训练关系模块能把一幅图的稀疏几何信息传到另一幅图。
- **证据等级**：B；这是很接近 CroCo 设计意图的下游复用。

### 6.2 DEBiT 与具身导航：对应能力能否服务于行动？

论文：[End-to-End (Instance)-Image Goal Navigation through Correspondence as an Emergent Phenomenon](https://arxiv.org/abs/2309.16634)，ICLR 2024；[官方代码](https://github.com/naver/debit)。

DEBiT 先进行 CroCo 式跨视角补全，再加入相对位姿与可见性预训练，最后用于 ImageNav 和 Instance-ImageNav 强化学习策略。

- **利用了什么**：CroCo cross-completion 初始化与图像对关系表示。
- **验证了什么**：不提供显式像素匹配监督，模型内部仍出现可用对应；这种关系能力不仅改善几何 benchmark，还能支持机器人根据目标图导航。
- **边界**：最终导航能力还来自相对位姿/可见性预训练和强化学习，不能只归因于 CroCo。
- **证据等级**：B/C。GOAT-Bench 等后续具身任务也使用冻结的 CroCo v2 编码器和适配器，进一步说明它能作为通用视觉前端。

### 6.3 自监督单目深度与 VO：与 SLAM 最直接的连接

论文：[Self-supervised Pretraining and Finetuning for Monocular Depth and Visual Odometry](https://arxiv.org/abs/2406.11019)，ICRA 2024。

该工作从 CroCo 的通用自监督预训练出发，再在无标注视频上用视图合成等信号联合微调单目深度和 visual odometry。

- **利用了什么**：CroCo 已学到的跨视角几何起点。
- **验证了什么**：即使下游也没有人工深度/位姿标签，预训练几何先验仍能有效迁移到深度与相机运动估计。
- **对 SLAM 学生的意义**：CroCo 的角色更像“学会怎样比较两帧”的视觉前端，而不是替代完整 SLAM 后端；尺度、长期一致性、回环和优化仍是另外的问题。
- **证据等级**：B。

### 6.4 ZeroCo：CroCo 真的在 cross-attention 中学出了匹配吗？

论文：[Cross-View Completion Models are Zero-shot Correspondence Estimators](https://arxiv.org/abs/2412.09072)，CVPR 2025 Highlight；[项目页面](https://cvlab-kaist.github.io/ZeroCo/)。

ZeroCo 没有先把 CroCo 当普通 backbone 再训练一个复杂匹配器，而是直接取 CroCo v2 解码器 cross-attention 中 query–key 的相似度，组成匹配 cost volume。

- **利用了什么**：预训练 CroCo v2 ViT-L 及其 decoder cross-attention map。
- **验证了什么**：不做对应监督、不重新训练，就能得到强的零样本稠密匹配；cross-attention 相似度优于简单使用 encoder 或 decoder 输出特征做相关，极端视角变化下仍有效。
- **为什么证据特别强**：它直接检查 CroCo 为完成补全而使用的内部机制，而不仅是观察某个微调任务变好。因此它是“CroCo 确实学到 correspondence”最有说服力的后续证据之一。
- **局限**：ViT patch 尺度使注意力图偏粗；要得到高精度稠密流/深度，仍需局部放大、组合注意力头或轻量下游训练。
- **证据等级**：A。

### 6.5 Co-op：新物体的模板—实拍图对应与 6D 位姿

论文：[Co-op: Correspondence-based Novel Object Pose Estimation](https://arxiv.org/abs/2503.17731)，CVPR 2025。

Co-op 将实拍查询图与 CAD 模型渲染的多个模板图送入 CroCo v2 风格网络，先估计半稠密对应，再做概率式 refinement、可微 PnP 和候选位姿选择。

- **利用了什么**：三个阶段都基于 CroCo v2 架构/预训练。
- **验证了什么**：在 BOP 七个核心数据集上表现很强；其消融中，去掉 CroCo 预训练后，粗匹配平均召回从 50.2 降到 46.4，refinement 从 64.0 降到 61.2。
- **意义**：跨视角补全学到的关系不局限于同一场景的自然相机对，也能迁移到“渲染模板—真实图像”、未知物体与大视角差异。
- **证据等级**：B。

### 6.6 CroCoDiLight：它学到的只有几何吗？

论文：[CroCoDiLight: Repurposing Cross-View Completion Encoders for Relighting](https://openreview.net/forum?id=GKvb3HCyNk)，ICLR 2026；[项目页面](https://alistairfoggin.com/projects/crocodilight/)。

该工作冻结 CroCo v2 encoder，从特征中分解全局光照 latent 与逐 patch 的光照不变场景 latent，用于重光照、光照插值、阴影移除和反照率相关任务。

- **利用了什么**：冻结的 CroCo v2 encoder，而非重新训练整个几何系统。
- **验证了什么**：跨视角预训练还保留了材质与光照信息；模型并不是只学到“纯几何”。训练图像对中的光照变化，反而提供了解耦这些因素的基础。
- **意义**：提醒我们不要把“几何偏置”误读为“表征中只有几何”。好的视觉表征往往同时编码形状、外观、材质和照明，只是下游读取方式不同。
- **证据等级**：B。

---

## 7. 第三条主线：CroCo v2 → DUSt3R → 通用 3D 视觉

### 7.1 DUSt3R 是怎样改造 CroCo 的？

论文：[DUSt3R: Geometric 3D Vision Made Easy](https://arxiv.org/abs/2312.14132)，CVPR 2024；[官方代码](https://github.com/naver/dust3r)。

DUSt3R 的网络类名甚至直接叫 `AsymmetricCroCo3DStereo`。它使用 CroCo v2 的 ViT-L/BaseDecoder 权重和 RoPE，保留两图编码与跨注意力融合，但做了关键改变：

1. 为两张图设置非对称的解码分支；
2. 用 DPT 头输出每个像素对应的三维点（pointmap）与置信度；
3. 把两张图的三维点都表达在第一相机坐标系；
4. 用有真值几何的数据监督 pointmap，而不再重建 RGB。

这样，相机内参、相对位姿、深度、像素匹配都不必先分别求解，而可从统一点图表示中恢复。多图时，再对所有图像对的点图进行全局对齐。

- **利用了什么**：CroCo v2 的完整权重、RoPE、非对称两图架构，以及 decoder 已具备的跨视角融合能力。
- **新增了什么**：大量有几何真值的数据、显式 3D pointmap 监督、置信度预测、全局对齐。
- **验证了什么**：无 CroCo 初始化的受控版本整体明显更差，说明 cross-view completion 是优良起点；同时，DUSt3R 能直接输出显式三维，说明这种隐式关系表征可以被几何监督“读出来并定标”。
- **不能推出什么**：DUSt3R 的完整能力不等于 CroCo 已经自监督学会了相机标定与度量 3D。显式 pointmap 监督和 DUSt3R 的训练数据是不可忽略的新贡献。
- **证据等级**：B。

这一步是整条谱系最关键的范式变化：

```text
CroCo：用几何关系帮助预测 RGB
                     ↓
DUSt3R：直接把几何关系预测成 3D 点
```

### 7.2 MASt3R：从 3D 点图再加入可检索的局部描述子

论文：[MASt3R: Grounding Image Matching in 3D with MASt3R](https://arxiv.org/abs/2406.09756)，ECCV 2024。

MASt3R 以 DUSt3R 为起点，额外预测局部描述子并加入匹配损失，使 reciprocal matching 更快、更可靠，尤其适合大视角变化。

- **继承了什么**：经 DUSt3R 间接继承 CroCo 的双视图 Transformer、RoPE 与初始化谱系。
- **验证了什么**：CroCo/DUSt3R 形成的跨视角骨干可以同时承载几何坐标与判别式匹配描述子。
- **归因边界**：匹配精度的新增部分来自 MASt3R 的描述子头和显式匹配监督，不能当作对原始 RGB 补全目标的独立验证。
- **证据等级**：C。

### 7.3 从两图到视频、多视图、动态场景和 3DGS

这些工作说明 CroCo → DUSt3R 的骨干具有很强可塑性，但大多属于**间接证据**：

| 工作 | 与谱系的关系 | 新增能力 | 它说明什么，以及不能说明什么 |
|---|---|---|---|
| [Spann3R](https://arxiv.org/abs/2408.16061) | 以 DUSt3R 及其权重为基础 | 用空间记忆增量输出统一坐标系 pointmap | 说明两图几何可改造成流式状态；实时和全局一致性来自新增 memory，而非 CroCo 本身。 |
| [SLAM3R](https://openaccess.thecvf.com/content/CVPR2025/html/Liu_SLAM3R_Real-Time_Dense_Scene_Reconstruction_from_Monocular_RGB_Videos_CVPR_2025_paper.html) | DUSt3R 系 | 面向单目视频的实时稠密重建 | 说明该表征能进入 SLAM 式流程；长期地图管理和实时设计是新贡献。 |
| [MonST3R](https://arxiv.org/abs/2410.03825) | 微调 DUSt3R decoder/head | 动态视频深度、相机运动与随时间变化的 3D | 证明静态场景先验可迁移；也反证原始 CroCo/DUSt3R 不会自动解决运动物体，必须加入动态数据和损失。 |
| [Fast3R](https://arxiv.org/abs/2501.13928) | 使用 DUSt3R/CroCo 系 encoder 起点 | 多张图一次前向、避免成对全局对齐，可扩到千图 | 说明 pairwise 架构可重构为多视图；其报告 DINOv2 初始化也能接近，故不能声称 CroCo 是唯一必要因素。 |
| [MUSt3R](https://arxiv.org/abs/2503.01661) | 先以 CroCo v2 初始化的 DUSt3R 式双图预训，再加入多视图 memory | 在线/离线统一坐标系重建，扩展到大量图像 | 支持“先学强两图关系，再学多视图状态”的路线；多视图一致性来自新增 memory 训练。 |
| [Reloc3r](https://arxiv.org/abs/2412.08376) | 采用 DUSt3R Transformer 骨干与权重 | 直接相对位姿回归和 motion averaging | 说明统一跨视角骨干可专门化为快速 pose 模型；主要验证的是几何微调和数据规模。 |
| [CUT3R](https://arxiv.org/abs/2501.12387) | DUSt3R 系的状态化扩展 | 持久递归状态、在线处理、动态/未观测视图查询 | 说明 pairwise pointmap 可提升为有记忆的 3D 状态；persistent state 是新增核心。 |
| [Splatt3R](https://arxiv.org/abs/2408.13912) | 冻结 MASt3R/DUSt3R 系几何特征 | 预测 3D Gaussian 属性，做无位姿新视角合成 | 说明 pointmap 是 3DGS 的好初始化；不能隔离 CroCo 自监督预训练的贡献。 |
| [NoPoSplat](https://arxiv.org/abs/2410.24207) | 主模型用 MASt3R；另比较 CroCo v2 初始化 | 无位姿稀疏视图的 3D Gaussian 与 NVS | 其初始化消融中 MASt3R/DUSt3R/CroCo v2/DINOv2/随机 PSNR 为 25.033/24.553/24.559/24.094/23.487；CroCo 比随机和 DINO 更好且接近 DUSt3R，但 CroCo/DINO/随机分支使用了短暂 point-cloud distillation warm-up，证据应保守解读。 |

这些成果共同证明的是：**CroCo 孵化出的跨视角 Transformer 是一个可塑性极强的架构与初始化家族。** 它们并不能逐篇独立证明“RGB cross-view completion 本身足以产生所有后续能力”。从导师角度，我建议你始终把“血统”和“因果贡献”分开。

### 7.4 哪些相近工作不应误算为 CroCo 后代？

例如 VGGT 与这条路线在目标上相近，也做多视图几何预测，但采用自己的多视图 Transformer 设计与预训练路线，并非简单继承 CroCo 权重。它可以放在同一研究版图里比较，却不应仅因任务相近就列为“基于 CroCo”。同理，后来的 BINO 等方法是对 CroCo v2 的 encoder/decoder 取舍提出替代方案，也更适合作为对照而非后代。

---

## 8. 后续工作究竟验证了 CroCo 的哪些特性？

把零散论文压缩成“性质—证据”会更清楚：

| 待验证性质 | 最直接证据 | 当前合理结论 | 仍不能过度声称的内容 |
|---|---|---|---|
| 模型学到跨视角对应 | CroCo 双视图/单图变换消融；ZeroCo 直接读取 Q–K cross-attention；SACReg 注意力分析 | cross-attention 中确实形成了可用于匹配的关系结构 | 注意力不是严格的一一对应证明；patch 分辨率和遮挡会限制精度 |
| 表征偏向几何而非只靠语义 | CroCo 对 MAE 的深度/Taskonomy/光流优势；分类优势有限 | 预训练目标把容量明显推向稠密几何 | 不能说表征没有语义、外观或光照信息 |
| decoder 是重要资产 | CroCo 光流初始化消融；ZeroCo；DUSt3R | 跨视图融合模块本身可迁移，不只是 encoder 好用 | 不同任务仍可能需要重新设计 decoder 或 head |
| 真实图像对和数据规模重要 | CroCo v2、MIMIC | 更多样、真实且有合适重叠的图像对能改善跨域泛化 | v2 是复合改进，不能把所有增益只归因于“真实数据” |
| 高分辨率/裁剪泛化 | CroCo v2 RoPE 在 ETH3D、SACReg 中表现 | 相对位置编码是部署到不同分辨率的重要设计 | RoPE 并非每个 benchmark 都独立、单调提升 |
| 隐式关系能转成显式 3D | DUSt3R 及其 NoCroCo 消融 | CroCo v2 是很好的 3D pointmap 初始化 | 度量 3D 的主要监督来自 DUSt3R，不能倒推 CroCo 已自监督学会完整 3D |
| 能迁移到新领域 | CroCo-Man、Co-op、导航、深度/VO | 跨视角先验适用于人体、物体模板、机器人与相机运动 | 每个领域都加入了数据、监督或任务结构 |
| 表征包含光照/材质因素 | CroCoDiLight | CroCo 表征不是“纯几何”，还可重组光照与外观 | 这不等价于通用 inverse rendering 已解决 |
| 原始 RGB 补全并非终点 | Alligat0R、MuM | 共视标签或统一多视图 masking 在某些目标上更合理 | 不能据此否定 CroCo；这些工作恰恰建立在其问题意识上 |
| pairwise 静态设置可被扩展 | CroCo-Man、MonST3R、Fast3R、MUSt3R、CUT3R | 可通过新数据、memory 和监督扩到动态、多图、流式 | 原始 CroCo 本身不具备长期状态、多视图闭环或动态建模 |

### 三层证据强度

1. **目标层证据**：CroCo 相对 MAE、真实视角相对单图变换的受控消融，说明“跨视角补全”方向有效。
2. **机理层证据**：ZeroCo、SACReg 发现 cross-attention 内部可以直接充当对应关系，这是最接近原始机制假设的证据。
3. **系统层证据**：DUSt3R 家族、Co-op、导航、VO、3DGS 等说明该表示可复用，但越往下游，新增数据和模块越多，对 CroCo 本身的因果归因就越弱。

---

## 9. 局限、未解问题与值得做的研究

### 9.1 RGB 重建是间接几何监督

模型可能依靠纹理复制、数据统计或局部外观完成一部分任务。Cross-view completion 会鼓励对应和几何，但不保证得到全局一致、带尺度、可解释的三维表示。ZeroCo 和 DUSt3R 使证据更强，却没有消除这个逻辑区别。

### 9.2 无共视区域天然病态

若目标区域在参考图中不可见，模型仍只能猜。Alligat0R 的共视/遮挡分割正面处理了这一点。一个值得继续研究的问题是：能否让模型先判断“哪里可以由几何证据恢复”，再对其余区域使用生成先验，而不是用一个 RGB MSE 混在一起？

### 9.3 成对、静态、短时

CroCo 每次只处理一对静态图像，没有长期记忆、闭环或全局地图。多视图与视频系统需要额外的 memory、全局对齐或递归状态。对 SLAM 来说，它更像强大的 learned front-end，而不是完整系统。

### 9.4 数据构建并不完全“免费”

v1 依赖可渲染三维场景，v2 的真实对挖掘常依赖 mesh、SfM、LiDAR 或位姿。MIMIC 试图降低这一门槛，但高质量重叠估计和数据去重仍是关键工程问题。

### 9.5 外观变化与动态物体

大光照变化、镜面、重复纹理、透明体和快速非刚性运动都会破坏简单对应假设。CroCo-Man、MonST3R、CroCoDiLight 说明这些因素可通过专门数据与目标建模，但通用解决方案仍未完成。

### 9.6 计算与分辨率

高遮挡预训练节省目标 encoder 的 token，但完整参考图、双分支和大型 decoder 仍有不小代价。CroCo 的 patch 级对应也偏粗。MuM、Fast3R、BINO 等后续路线分别尝试更高效的多视图或 encoder-centric 设计。

### 9.7 当前值得追问的研究问题

- 跨视角预训练最合适的预测对象是什么：RGB、深度、共视标签、pointmap，还是生成式 latent？
- 怎样同时兼顾语义不变性与精确几何等变性，而不让一种能力压制另一种？
- 能否不借助 SfM/位姿/mesh，自动从海量视频中筛出高价值图像对和多视图组？
- 怎样把 CroCo 式局部对应与 SLAM 的长期一致性、回环、动态物体状态统一训练？
- cross-attention 中哪些 head 表示几何、遮挡、光照或语义？这种分工能否被约束、压缩和校准？

---

## 10. 给初学者的阅读顺序

建议不要一上来追全部 DUSt3R 家族。按以下顺序，概念会更稳：

1. **MAE**：弄懂 patch、mask、encoder/decoder、像素重建。
2. **CroCo**：重点读 Fig. 2、图像对选择、mask ratio、CroCo vs. MAE 和光流初始化消融。
3. **CroCo v2**：重点读真实图像对构建、2D RoPE、Table 1 逐步消融，以及不使用 task-specific 结构的 stereo/flow 设计。
4. **ZeroCo**：理解 cross-attention 的 Q/K 为什么能成为 cost volume。这一步会把“隐式对应”从一句宣传语变成可观察对象。
5. **DUSt3R**：仔细区分 CroCo 初始化、pointmap 表示、几何监督与全局对齐分别贡献了什么。
6. 再按兴趣选支线：做 SLAM/重建读 Spann3R、SLAM3R、MUSt3R；做动态场景读 MonST3R/CUT3R；做匹配读 MASt3R；做预训练研究读 MIMIC、Alligat0R、MuM。

阅读每篇论文时，建议固定问四个问题：

1. 输入中的哪些变量是已知的——内参、外参、深度、时间顺序、CAD 模型？
2. 训练监督到底是什么——RGB 自监督、伪标签、相机元数据，还是显式 3D 真值？
3. 它继承的是 CroCo 的权重、架构、数据，还是仅仅一句思想？
4. 消融能否隔离这个继承项，还是只证明完整系统有效？

---

## 11. 总结性的学术评价

CroCo 是一个“问题设定胜过复杂模块”的典型好工作。它观察到单图掩码重建对几何的约束太弱，于是只增加一个同场景视角，就把自监督学习转化为必须处理对应与相机视差的问题。这个设计简单、可证伪，而且通过真实双视角/伪变换、CroCo/MAE、encoder/decoder 初始化等消融给出了相当干净的证据。

CroCo v2 的品位在于，它没有为了追榜单堆叠大量光流或立体专用结构，而是问：“数据、位置编码和容量补齐以后，通用 Transformer 到底能走多远？”结果显示它可以走得很远，并为后来整条 3D foundation model 路线提供了预训练权重和架构母体。

从今天回看，CroCo 的历史意义可以概括为：

> 它把 masked image modeling 从“理解一张图里通常会出现什么”，推进到“理解同一个三维世界在不同观察下怎样对应”；DUSt3R 随后又把这种隐式理解改写成了可以直接输出的三维表示。

这条路线也教给研究者一个重要方法论：不要只追问模型是否更大、损失是否更复杂，而要追问**预训练任务给模型提供了哪种可利用的信息，以及它排除了哪些捷径**。CroCo 的成功首先来自这个层面的选择。

---

## 12. 主要来源与检索说明

### 核心论文与官方资源

- [CroCo: Self-Supervised Pre-training for 3D Vision Tasks by Cross-View Completion](https://arxiv.org/abs/2210.10716), NeurIPS 2022.
- [CroCo v2: Improved Cross-view Completion Pre-training for Stereo Matching and Optical Flow](https://arxiv.org/abs/2211.10408), ICCV 2023.
- [NAVER CroCo 官方代码与模型权重](https://github.com/naver/croco).
- [DUSt3R 官方代码](https://github.com/naver/dust3r).

### 直接延伸、使用或检验 CroCo 的代表工作

- [MIMIC](https://arxiv.org/abs/2306.15128), CVPR 2024 3DMV Workshop.
- [Cross-view and Cross-pose Completion for 3D Human Understanding](https://arxiv.org/abs/2311.09104), CVPR 2024.
- [SACReg](https://arxiv.org/abs/2307.11702), CVPR 2024 3DMV Workshop.
- [DEBiT](https://arxiv.org/abs/2309.16634), ICLR 2024.
- [Self-supervised Pretraining and Finetuning for Monocular Depth and Visual Odometry](https://arxiv.org/abs/2406.11019), ICRA 2024.
- [DUSt3R](https://arxiv.org/abs/2312.14132), CVPR 2024.
- [ZeroCo](https://arxiv.org/abs/2412.09072), CVPR 2025 Highlight.
- [Co-op](https://arxiv.org/abs/2503.17731), CVPR 2025.
- [Alligat0R](https://arxiv.org/abs/2503.07561), NeurIPS 2025 Spotlight.
- [MuM](https://arxiv.org/abs/2511.17309), CVPR 2026.
- [CroCoDiLight](https://openreview.net/forum?id=GKvb3HCyNk), ICLR 2026.

### DUSt3R 之后的代表性间接谱系

- [MASt3R](https://arxiv.org/abs/2406.09756), ECCV 2024.
- [Spann3R](https://arxiv.org/abs/2408.16061).
- [Splatt3R](https://arxiv.org/abs/2408.13912).
- [MonST3R](https://arxiv.org/abs/2410.03825).
- [NoPoSplat](https://arxiv.org/abs/2410.24207), ICLR 2025.
- [Reloc3r](https://arxiv.org/abs/2412.08376), CVPR 2025.
- [CUT3R](https://arxiv.org/abs/2501.12387).
- [Fast3R](https://arxiv.org/abs/2501.13928), CVPR 2025.
- [MUSt3R](https://arxiv.org/abs/2503.01661), CVPR 2025.
- [SLAM3R](https://openaccess.thecvf.com/content/CVPR2025/html/Liu_SLAM3R_Real-Time_Dense_Scene_Reconstruction_from_Monocular_RGB_Videos_CVPR_2025_paper.html), CVPR 2025.

检索时使用论文全名以及 “CroCo pretrained / initialized / architecture / cross-view completion / CroCo V2” 等组合词，优先核对论文正文、官方项目页和官方仓库。纳入标准是：论文明确继承 CroCo 权重/架构/目标，或通过受控实验检验 CroCo 的核心假设；另选少量 DUSt3R 后代展示间接影响。仅在 related work 中提到 CroCo、没有实际依赖或实验关系的论文未逐一收录，因此这是一份**研究脉络图，而非机械穷尽的引用列表**。
