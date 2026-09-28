# 3DGS / 4DGS 研究综述：前馈式重建与任意点跟踪

> **第 0–11 节检索截止：2026-09-15。** 前馈重建主线覆盖 **2024 年下半年至 2026 年 9 月**，并补入理解该方向必需的 2024 年奠基论文；其中少数论文的首次预印本在 2023 年末。
>
> **第 12 节新增检索截止：2026-09-24。** 专题整理 **2023–2026 年 3DGS / 4DGS 与 point tracking / Tracking Any Point（TAP）** 的结合，区分轨迹先验、轨迹输出、前馈预测和相邻工作。
>
> 本文是代表性工作综述，不是穷尽式论文清单。重点是通用场景重建，兼顾物体、单图生成、动态场景和 SLAM。来源优先使用原论文、正式会议论文页、作者项目页及官方代码。  
> 年份尽量区分“首次公开”与“正式发表”；仅由作者页面确认录用的论文会说明依据。文中“评价 / 判断 / 建议”属于综合分析。未运行模型，速度与质量不作为统一条件下的实测排名。

## 0. 先看结论

近两年的变化可以概括为：**把高斯从“每个场景单独拟合的渲染表示”，变成“网络直接预测、可以融合和持续更新的场景表示”。** 但前馈推理只解决了其中一部分问题，相机估计、几何精度、地图规模与长期一致性仍需要分别考察。

1. **2024 年建立基础范式。** pixelSplat、MVSplat 把多视图匹配、深度和逐像素高斯联系起来；GS-LRM 展示 Transformer 直接预测高斯的可扩展性。理解后续工作，先读这三篇。[pixelSplat](https://arxiv.org/abs/2312.12337)、[MVSplat](https://arxiv.org/abs/2403.14627)、[GS-LRM](https://arxiv.org/abs/2404.19702)
2. **2025 年的重要变化是减少输入约束。** DepthSplat 强化深度先验；NoPoSplat、FLARE、FreeSplatter、AnySplat 把重点移到无位姿、未标定和更多视图的输入。不同方法对内参、训练监督及测试时相机求解的要求并不一样。[DepthSplat](https://arxiv.org/abs/2410.13862)、[NoPoSplat](https://proceedings.iclr.cc/paper_files/paper/2025/hash/857b34d81f0a8bfe3e18879dee3b5086-Abstract-Conference.html)、[AnySplat](https://github.com/InternRobotics/AnySplat)
3. **2025–2026 年开始重视高斯本身的组织方式。** VolSplat、SparseSplat、F4Splat 和 GlobalSplat 分别从体素、稀疏点、自适应增密与全局场景 token 出发，减少逐像素预测造成的冗余。这一变化直接关系到地图大小和后续使用成本。[VolSplat](https://arxiv.org/abs/2509.19297)、[SparseSplat](https://arxiv.org/abs/2604.03069)、[F4Splat](https://arxiv.org/abs/2603.21304)、[GlobalSplat](https://arxiv.org/abs/2604.15284)
4. **单图场景重建与几何基础模型正在进入同一生态。** SHARP 面向单张照片的近邻视角合成；Depth Anything 3 的特定模型提供高斯预测分支。不能据此认为所有深度模型、所有型号都能直接导出同等质量的 3DGS。[SHARP](https://arxiv.org/abs/2512.10685)、[DA3 官方接口说明](https://github.com/ByteDance-Seed/Depth-Anything-3/blob/main/docs/API.md)
5. **“更多帧”和“流式”是两类问题。** Long-LRM 扩大一次处理的视图集合；流式模型需要进一步处理历史复用、因果性和状态更新。一次前向处理整段视频，不自动等于在线 SLAM。[Long-LRM](https://openaccess.thecvf.com/content/ICCV2025/html/Ziwen_Long-LRM_Long-sequence_Large_Reconstruction_Model_for_Wide-coverage_Gaussian_Splats_ICCV_2025_paper.html)、[StreamSplat：2026 年流式前馈工作](https://arxiv.org/abs/2608.01659)
6. **面向 SLAM 的研究判断：应把渲染质量和几何可靠性分开优化、分开评价。** 好看的新视角不保证可测量表面、正确尺度或回环一致性。前馈初始化加在线校正，是值得研究的组合，但不是已被证明对所有场景最优的方案。[2DGS](https://arxiv.org/abs/2403.17888)、[Splat-SLAM](https://openaccess.thecvf.com/content/CVPR2025W/VOCVALC/html/Sandstrom_Splat-SLAM_Globally_Optimized_RGB-only_SLAM_with_3D_Gaussians_CVPRW_2025_paper.html)

**阅读导航：** 第 1 节统一概念；第 2 节快速了解非前馈背景；第 3–8 节按技术路线梳理前馈工作；第 9–11 节讨论比较方法、研究问题和阅读顺序；**第 12 节是新增的“3DGS / 4DGS + 任意点跟踪”专题**，可独立阅读。

## 1. 前馈式 3DGS 究竟指什么

### 1.1 从逐场景拟合到跨场景预测

原始 3DGS 用一组各向异性高斯表示场景。第 $i$ 个高斯可写成：

$$
g_i = (\mu_i,\Sigma_i,\alpha_i,c_i),\qquad
\Sigma_i=R_i\operatorname{diag}(s_i^2)R_i^\top.
$$

其中 $\mu_i$ 是位置，$\Sigma_i$ 决定形状与朝向，$\alpha_i$ 是不透明度，$c_i$ 是颜色或球谐系数。原方法从运动恢复结构（SfM）得到的稀疏点云初始化，再对当前场景反复优化高斯参数，并交替增密、裁剪，最后快速光栅化渲染。[原始 3DGS，SIGGRAPH 2023](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/)

前馈式方法则在大量训练场景上学习共享参数 $\theta$，对未见场景直接预测：

$$
\mathcal G=f_\theta(I_1,\ldots,I_N;\text{可选相机信息}).
$$

若模型需要相机内外参，其逐像素高斯中心常由深度反投影得到：

$$
\mu_{v,p}=R_v\left(d_{v,p}K_v^{-1}\tilde p\right)+t_v.
$$

这里 $K_v$ 是内参，$R_v,t_v$ 把相机坐标变换到公共坐标；$\tilde p$ 是最后一维为 1 的齐次像素坐标，$d_{v,p}$ 是相机光轴方向的深度。若使用沿射线的距离，则应先归一化 $K_v^{-1}\tilde p$。这个形式容易学习，但多张图可能为同一表面重复生成高斯。[MVSplat](https://arxiv.org/abs/2403.14627)、[VolSplat](https://arxiv.org/abs/2509.19297)

### 1.2 阅读论文时必须分开的概念

| 概念 | 本文采用的含义 | 不能据此直接推出什么 |
|---|---|---|
| Feed-forward reconstruction | 共享模型在新场景上通过固定网络推理预测表示 | 不代表从不需要离线训练，也不代表全部辅助步骤只有一次网络前向 |
| Pose-free / unposed | 推理不要求预先提供输入图像的外参，方法内部可能估计外参 | 可能仍输入内参；训练时也可能需要已标定数据 |
| Uncalibrated | 推理不要求预先提供内外参 | 模型预测的相机和绝对尺度仍可能不准 |
| Generalizable | 同一模型可以处理未见场景 | 跨数据集、跨相机、跨光照的泛化强度仍需实测 |
| Real-time rendering | 已得到高斯后，渲染新视角很快 | 不等于重建、位姿估计、全流程都实时 |
| Streaming / online | 新输入到达后增量更新 | 不自动意味着严格因果、固定工作内存或有回环 |
| Generative reconstruction | 显式引入生成模型合成或补全内容，例如变分特征解码或扩散生成新视图 | 补出的遮挡区域不一定对应真实世界 |
| Hybrid / refinement | 前馈初始化后，再求解相机或优化场景 | 优化后的结果和耗时必须与纯前馈结果分开 |

还要检查**表示是否依赖目标视角**。有些方法先重建一份场景，之后任意渲染；另一些方法会针对每个目标相机构建代价体积或执行神经解码，两者部署成本不同。MVSGaussian 就需要特别注意这一点。[MVSGaussian](https://arxiv.org/abs/2405.12218)

## 2. 3DGS 整体进展：前馈研究的背景

本节方法主要属于**逐场景优化、渲染改进或已有模型后处理**。它们提供重要思想，但不因此属于跨场景前馈重建。

| 方向 | 代表工作与时间 | 核心贡献 | 对前馈式研究的启发 |
|---|---|---|---|
| 高斯到网格 | [SuGaR](https://openaccess.thecvf.com/content/CVPR2024/html/Guedon_SuGaR_Surface-Aligned_Gaussian_Splatting_for_Efficient_3D_Mesh_Reconstruction_and_CVPR_2024_paper.html)，CVPR 2024 | 表面对齐正则、网格提取与高斯/网格联合优化 | 渲染表示还需要能转换成可编辑、可测量的表面 |
| 表面高斯 | [2DGS](https://arxiv.org/abs/2403.17888)，SIGGRAPH 2024；[PGSR](https://arxiv.org/abs/2406.06521)，2024 首次公开 | 二维圆盘或平面高斯，结合深度、法线及多视图一致性 | 高斯位置、形状、遮挡关系需要几何约束 |
| 抗混叠 | [Mip-Splatting](https://openaccess.thecvf.com/content/CVPR2024/html/Yu_Mip-Splatting_Alias-free_3D_Gaussian_Splatting_CVPR_2024_paper.html)，CVPR 2024 | 3D 平滑与 2D Mip 滤波，改善尺度变化时的伪影 | 测试改变分辨率、焦距、视距时的稳定性 |
| 结构化与层次细节 | [Scaffold-GS](https://openaccess.thecvf.com/content/CVPR2024/papers/Lu_Scaffold-GS_Structured_3D_Gaussians_for_View-Adaptive_Rendering_CVPR_2024_paper.pdf)，CVPR 2024；[Octree-GS](https://github.com/city-super/Octree-GS)，2024 预印本 / TPAMI 2025 | 锚点、视角相关属性、八叉树和 LOD | 让高斯密度服从场景结构和显示需求；Scaffold-GS 的属性解码不等于新场景前馈重建 |
| 压缩 | [HAC](https://arxiv.org/abs/2403.14530)，ECCV 2024；[KISS-GS](https://arxiv.org/abs/2608.26948)，2026-08 预印本 | 前者利用哈希上下文做压缩感知优化；后者强调与重建训练解耦的模块化压缩 | 原生预测紧凑表示和重建后压缩可以互补；文件大小、显存、解码时间须分别报告 |
| Gaussian SLAM | [MonoGS / Gaussian Splatting SLAM](https://openaccess.thecvf.com/content/CVPR2024/html/Matsuki_Gaussian_Splatting_SLAM_CVPR_2024_paper.html)、[SplaTAM](https://openaccess.thecvf.com/content/CVPR2024/html/Keetha_SplaTAM_Splat_Track__Map_3D_Gaussians_for_Dense_RGB-D_CVPR_2024_paper.html)，CVPR 2024 | 围绕高斯地图交替跟踪与增量建图；SplaTAM 使用 RGB-D | 前馈输出能否融合进地图，比单帧展示更重要 |
| 全局一致 SLAM | [Splat-SLAM](https://openaccess.thecvf.com/content/CVPR2025W/VOCVALC/html/Sandstrom_Splat-SLAM_Globally_Optimized_RGB-only_SLAM_with_3D_Gaussians_CVPRW_2025_paper.html)，2024 预印本 / CVPR Workshops 2025 | 联合调整视差、尺度和位姿，使高斯地图随全局几何更新 | 回环或尺度修正后，旧高斯也需要一致地修正 |
| 更受约束的 RGB-D 建图 | [SGAD-SLAM](https://openaccess.thecvf.com/content/CVPR2026/html/Hu_SGAD-SLAM_Splatting_Gaussians_at_Adjusted_Depth_for_Better_Radiance_Fields_CVPR_2026_paper.html)，CVPR 2026 | 高斯沿像素对应射线调整深度 | 适当限制自由度可能改善几何；像素对齐本身不是前馈标志 |
| 动态表示 | [4D Gaussian Splatting for Real-Time Dynamic Scene Rendering](https://openaccess.thecvf.com/content/CVPR2024/papers/Wu_4D_Gaussian_Splatting_for_Real-Time_Dynamic_Scene_Rendering_CVPR_2024_paper.pdf)，CVPR 2024，Wu 等 | 以时空特征和变形网络驱动高斯随时间变化 | 动态渲染、在线重建与物质点跟踪是不同目标 |
| 真实成像模型 | [3DGUT](https://openaccess.thecvf.com/content/CVPR2025/html/Wu_3DGUT_Enabling_Distorted_Cameras_and_Secondary_Rays_in_Gaussian_Splatting_CVPR_2025_paper.html)，CVPR 2025 | 无迹变换处理非线性投影，支持畸变相机、滚动快门与二次光线 | 针孔相机近似不是所有场景都成立，需考虑真实传感器 |

**总体判断：** 前馈模型继承了高斯的渲染效率，也继承了几何歧义、冗余、尺度变化和真实成像误差。更强编码器之外，表示、渲染器和地图维护同样是研究空间。

## 3. 第一条主线：已知相机的稀疏多视图重建

这条路线把相机内外参作为输入，重点研究“如何从有限观测恢复深度并预测高斯”。它适合用于有标定位姿的数据，或接在已有 SfM / SLAM 前端后面。

### 3.1 pixelSplat — 奠基性的双视图高斯预测

- **论文：** [pixelSplat: 3D Gaussian Splats from Image Pairs for Scalable Generalizable 3D Reconstruction](https://arxiv.org/abs/2312.12337)，2023-12 首次公开，CVPR 2024。
- **输入：** 主要是 2 张已标定图片；需要内参和相对外参。
- **方法：** 极线 Transformer 交换跨视图信息；预测沿射线的深度概率分布，采样高斯中心并用可微参数化训练。
- **意义：** 建立了跨场景学习、逐像素高斯预测和快速新视角渲染的基本组合。
- **局限与评价：** 跨视图高斯直接合并容易冗余；输入没看到的区域信息不足；极线注意力扩展到很多视图成本较高。主重建路径不需要逐场景优化。
- **资源：** [项目](https://davidcharatan.com/pixelsplat/) · [官方代码](https://github.com/dcharatan/pixelsplat)

### 3.2 MVSplat — 用代价体积显式恢复几何

- **论文：** [MVSplat: Efficient 3D Gaussian Splatting from Sparse Multi-View Images](https://arxiv.org/abs/2403.14627)，2024-03，ECCV 2024。
- **输入：** 稀疏已标定多视图，主要基准为 2 视图。
- **方法：** 多视图特征提取 → 平面扫描代价体积 → 深度预测及细化 → 反投影高斯中心，并预测其余属性。
- **意义：** 把明确的多视图匹配约束放回模型，是理解后续 DepthSplat、体素预测等路线的实用基线。
- **局限与评价：** 弱纹理、反射、透明物体和小重叠仍然困难；深度错误会传到高斯位置。论文里的 depth refinement 是网络模块，不能直接理解成测试时优化。
- **资源：** [项目](https://donydchen.github.io/mvsplat/) · [官方代码](https://github.com/donydchen/mvsplat)

### 3.3 DepthSplat — 连接单目先验、多视图深度和高斯学习

- **论文：** [DepthSplat: Connecting Gaussian Splatting and Depth](https://arxiv.org/abs/2410.13862)，2024-10 首次公开，[CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Xu_DepthSplat_Connecting_Gaussian_Splatting_and_Depth_CVPR_2025_paper.html)。
- **输入：** 已标定多视图；论文展示了更多视图和更高分辨率的重建。
- **方法：** 用预训练单目深度特征增强多视图深度估计，再预测高斯；反过来，用可微高斯渲染作为深度模型的无监督预训练目标。
- **意义：** 贡献不是只“加一个深度网络”，而是研究深度学习与高斯重建之间的双向收益。
- **局限与评价：** 单目先验可以补足匹配不足，却不保证跨域尺度和遮挡正确；原方法仍需要输入相机参数。应分别评价深度和新视角合成。
- **资源：** [官方代码](https://github.com/cvg/depthsplat)

### 3.4 GS-LRM — Transformer 直接预测高斯

- **论文：** [GS-LRM: Large Reconstruction Model for 3D Gaussian Splatting](https://arxiv.org/abs/2404.19702)，2024-04，ECCV 2024。
- **输入：** 2–4 张已标定图片；支持物体与场景，但论文对两类任务分别训练相应模型。
- **方法：** 将图像与相机射线编码分块，跨视图 Transformer 处理后直接解码逐像素高斯。
- **意义：** 代表简洁网络结构配合大规模训练的路线，与显式代价体积形成有价值的对照。
- **局限与评价：** 相机和训练分布仍重要；逐像素输出的规模、视锥外覆盖以及高分辨率计算量是限制。
- **资源：** [作者项目页](https://sai-bi.github.io/project/gs-lrm/)。本次查阅项目页未找到官方实现或权重链接，不能把非官方复现标作作者代码。

### 3.5 MVSGaussian — 要注意目标视角相关性

- **论文：** [MVSGaussian: Fast Generalizable Gaussian Splatting Reconstruction from Multi-View Stereo](https://arxiv.org/abs/2405.12218)，2024-05，ECCV 2024。
- **方法：** 在目标视锥构建 MVS 代价体积，结合 Gaussian splatting 与轻量体渲染；另提供几何一致性聚合和逐场景微调。
- **评价：** 它是重要的泛化重建路线，但前馈合成依赖目标相机。比较成本时要拆开“每个新目标视角的推理”和“重建一次后的纯高斯渲染”，并单列微调结果。
- **资源：** [项目](https://mvsgaussian.github.io/) · [官方代码](https://github.com/TQTQliu/MVSGaussian)

### 小结：这组工作主要改变了什么

| 方法 | 几何信息的主要来源 | 适合重点学习的部分 |
|---|---|---|
| pixelSplat | 极线交互与深度概率分布 | 如何让逐像素高斯定位可以端到端学习 |
| MVSplat | 显式多视图代价体积 | 几何归纳偏置如何提高重建效率和可靠性 |
| DepthSplat | 单目预训练特征 + 多视图几何 | 图像先验与几何观测如何互补 |
| GS-LRM | 相机条件 Transformer 与训练数据 | 简洁结构的扩展能力与计算代价 |
| MVSGaussian | 目标视锥中的多视图匹配 | 泛化合成、场景初始化与后优化的关系 |

## 4. 第二条主线：无位姿与未标定多视图

### 4.1 先比较输入和监督，避免只看名称

下表里的“无需”仅指新场景推理输入。相机求解器、评估对齐和高斯后优化另列；它们不是同一种操作。

| 工作 | 首次公开 / 发表 | 推理相机条件 | 几何与监督来源 | 需要留意的额外步骤 |
|---|---|---|---|---|
| [Splatt3R](https://arxiv.org/abs/2408.13912) | 2024-08；按预印本记录 | 双图，不需提供内外参 | MASt3R 骨干；高斯训练利用已知相机、深度及共视掩码 | 主高斯预测前馈；zero-shot 不表示没有训练 |
| [NoPoSplat](https://arxiv.org/abs/2410.24207) | 2024-10 / ICLR 2025 | 不需外参，**需要内参** | 规范空间直接回归；新视角 RGB 监督；预训练骨干 | 位姿任务有 PnP 与光度优化；NVS 评估含目标相机对齐 |
| [PF3plat](https://proceedings.mlr.press/v267/hong25c.html) | 2024-10 / ICML 2025 | 外参由系统估计，**需要内参** | 预训练深度和匹配；RGB 与几何一致性；不使用真值外参训练 | 先做粗几何对齐，再学习修正 |
| [SelfSplat](https://arxiv.org/abs/2411.17190) | 2024-11 / CVPR 2025 | 不需预先提供外参，**需要共享内参** | 自监督重投影及高斯渲染；无深度/位姿真值；使用 CroCo v2 图像预训练 | NVS 评估将目标图像输入位姿分支估计目标相机，须单列协议 |
| [FreeSplatter](https://arxiv.org/abs/2412.09573) | 2024-12 / ICCV 2025 | 不需提供内外参 | 位置预训练 + 渲染及射线对齐；物体/场景独立模型 | 从高斯中心恢复焦距，再用 PnP-RANSAC 求外参 |
| [FLARE](https://arxiv.org/abs/2502.12138) | 2025-02 / CVPR 2025 | 通用框架不需标定；**RE10K 双图 NVS 实验额外使用内参** | 相机、点图和渲染多任务监督 | 先预测相机，再恢复几何和外观；比较时匹配实际实验协议 |
| [AnySplat](https://arxiv.org/abs/2505.23716) | 2025-05 / SIGGRAPH Asia 2025、TOG | 未标定多视图，预测内外参 | VGGT 伪几何蒸馏 + RGB 与几何一致性 | 基本模型前馈；官方另有后优化版本 |
| [DA3 的 GS 分支](https://arxiv.org/abs/2511.10647) | 2025-11 / ICLR 2026 | 任意视图数量，可选相机输入 | 统一 depth-ray 几何学习及教师-学生训练 | 仅特定权重带 GS 分支；需明确启用 |

### 4.2 从几何基础模型到高斯：Splatt3R

[Splatt3R: Zero-shot Gaussian Splatting from Uncalibrated Image Pairs](https://arxiv.org/abs/2408.13912) 在 MASt3R 的几何预测上增加高斯属性头，并使用共视掩码限制渲染监督，避免要求网络准确复原输入根本看不到的区域。这是一条直接的“几何骨干 + 渲染表示”路线。[官方代码](https://github.com/btsmart/splatt3r)

**评价：** 它解释了为什么 DUSt3R / MASt3R 一类点图模型能帮助 3DGS，但原始点图并不等于完整的高斯属性、透明度和可渲染外观。双图覆盖及预训练几何质量仍然限制输出。

### 4.3 两种 pose-free 思路：NoPoSplat 与 PF3plat

**NoPoSplat** 的完整标题是 [No Pose, No Problem: Surprisingly Simple 3D Gaussian Splats from Sparse Unposed Images](https://arxiv.org/abs/2410.24207)。它把一个输入相机坐标系作为公共参考，直接预测所有视图对应的高斯，减少“每帧先预测再依靠不准位姿变换”带来的误差。内参编码帮助网络处理成像和尺度歧义，但不能把学习到的尺度理解成普遍正确的度量尺度。[官方代码](https://github.com/cvg/NoPoSplat)

**PF3plat** 的会议标题是 [PF3plat: Pose-Free Feed-Forward 3D Gaussian Splatting for Novel View Synthesis](https://proceedings.mlr.press/v267/hong25c.html)。它先用单目深度与匹配恢复粗几何，再由学习模块校正深度和位姿，利用几何置信度指导高斯预测。[官方代码](https://github.com/cvlab-kaist/PF3plat)

**比较判断：** NoPoSplat 更适合研究“公共坐标直接回归能否绕开中间位姿误差”；PF3plat 更适合研究“显式几何估计如何被学习模块修正”。两者都不能仅凭 pose-free 名称归类为完全未标定输入。

特别注意 NoPoSplat 的结果口径：**高斯预测本身、位姿估计的两阶段求解，以及 NVS 的目标相机对齐，是不同环节。** “只用光度损失训练”也不等于训练完全不需要相机信息，因为目标视角渲染监督仍用到标定数据。[NoPoSplat 原文](https://arxiv.org/html/2410.24207v1)

**另一个分支是 SelfSplat。** [SelfSplat: Pose-Free and 3D Prior-Free Generalizable 3D Gaussian Splatting](https://arxiv.org/abs/2411.17190) 联合学习自监督深度、匹配感知位姿和高斯，研究减少三维标注与预训练深度先验的依赖。其“3D prior-free”不等于从零训练：仍使用 CroCo v2 编码器；需要提供内参。高斯分支只看上下文图像，但 NVS 评估用目标图像估计目标相机，因此不能与其他输入协议直接混比。[原文及附录 B.6](https://arxiv.org/html/2411.17190v5) · [官方代码](https://github.com/Gynjn/selfsplat)

### 4.4 FreeSplatter 与 FLARE：把相机恢复纳入系统

[FreeSplatter: Pose-free Gaussian Splatting for Sparse-view 3D Reconstruction](https://arxiv.org/abs/2412.09573) 在统一参考系中预测像素高斯，再由几何恢复相机。它同时研究物体与场景，但使用独立模型；主文相机恢复还包含共享焦距、中心主点等假设。其高斯网络是前馈的，完整相机恢复不能忽略 PnP-RANSAC。[官方代码](https://github.com/TencentARC/FreeSplatter)

[FLARE: Feed-forward Geometry, Appearance and Camera Estimation from Uncalibrated Sparse Views](https://arxiv.org/abs/2502.12138) 按“相机 → 局部/全局几何 → 高斯外观”组织联合预测，体现几何与渲染多任务学习的路线。[作者项目页](https://zhanghe3z.github.io/FLARE/)

**评价：** 两者都在减少外部标定负担，但网络结构、监督和求解流程不同。FLARE 的 RE10K 双图新视角合成结果使用了内参条件，不能把该表与完全不输入内参的方法混作相同设定。[FLARE 原文 §4.3](https://arxiv.org/html/2502.12138v4)

### 4.5 AnySplat：从几何先验到多视图可渲染表示

[AnySplat: Feed-forward 3D Gaussian Splatting from Unconstrained Views](https://arxiv.org/abs/2505.23716) 联合预测高斯、深度及相机，通过可微体素化合并像素高斯。它用 VGGT 提供伪几何监督，是将几何基础模型能力转移到高斯重建的代表。[项目](https://city-super.github.io/anysplat/) · [官方代码](https://github.com/InternRobotics/AnySplat)

**评价：** 它既降低相机输入要求，也关注多视图冗余，适合作为未标定场景重建基线。伪标签路线节省为目标训练集重新制作几何标注的成本，但并未消除教师模型的几何监督来源。论文和代码里的基础预测、1000/3000 步后优化结果必须分开；共同处理多张图片也不自动成为流式系统。

### 4.6 Depth Anything 3：可选高斯输出的基础模型

[Depth Anything 3: Recovering the Visual Space from Any Views](https://arxiv.org/abs/2511.10647) 以统一 depth-ray 表示恢复空间一致几何，支持带相机或不带相机的输入；正式发表于 [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/e4cd50120b6d7e8daff1749d6bbaa889-Abstract-Conference.html)。

官方实现提供 GS 分支：当前文档要求显式设置 `infer_gs=True`，高斯导出由 `da3-giant`、`da3nested-giant-large` 等指定模型支持。GS 头输出属性，再结合深度和相机变换到公共坐标。[官方 API](https://github.com/ByteDance-Seed/Depth-Anything-3/blob/main/docs/API.md)、[模型实现](https://github.com/ByteDance-Seed/Depth-Anything-3/blob/main/src/depth_anything_3/model/da3.py)

**评价：** 对研究者，它提供一个同时输出几何与高斯的较新起点；比较时必须固定模型大小和分支配置。本文不把 DA3 的几何基准胜出直接解读成其高斯分支在所有 NVS 数据集胜出。

## 5. 第三条主线：让高斯密度服从三维结构

### 5.1 为什么逐像素输出会成为瓶颈

若每幅输入有 $H\times W$ 个像素，每像素预测 $L$ 个高斯，直接合并 $N$ 幅图像的原始输出约为：

$$
M\approx NHWL.
$$

这是**未融合、未裁剪的逐像素设计**的计数关系，并非所有前馈模型的复杂度定律。同一面墙被十张图看见，不必在最终地图里保留十份；另一方面，细杆和复杂边缘可能比平墙需要更多表示容量。这推动了 2025–2026 年的体素、稀疏点和自适应增密路线。[VolSplat](https://arxiv.org/abs/2509.19297)、[SparseSplat](https://arxiv.org/abs/2604.03069)

| 方法 | 首次公开 / 发表 | 输入相机条件 | 核心改变 | 评价与边界 |
|---|---|---|---|---|
| [VolSplat](https://arxiv.org/abs/2509.19297) | 2025-09 / ECCV 2026，作者论文及代码已标注 | 已知内外参 | 深度反投影特征到体素，稀疏 3D 解码器预测占用体素中的高斯 | 融合后再输出，更适合三维一致性；仍用深度和多视图匹配，不能宣传成完全去掉这些环节 |
| [SparseSplat](https://arxiv.org/abs/2604.03069) | 2026-04 / CVPR 2026 | 已知相机参数 | 熵驱动概率采样产生稀疏三维锚点，再用点云网络预测属性 | 让细节区域和简单区域具有不同密度；需考察预算下降时薄结构和低纹理几何的损失 |
| [F4Splat](https://arxiv.org/abs/2603.21304) | 2026-03 / ECCV 2026，官方代码标注 | 未标定多视图 | 预测增密分数，按空间复杂度和视图重叠分配高斯；无需重训即可控制最终预算 | 把逐场景启发式增密的一部分转成可学习预测；预算、外观和几何应一起评价 |
| [GlobalSplat](https://arxiv.org/abs/2604.15284) | 2026-04，预印本 | 已标定多视图；官方实现使用相机/射线编码 | 先形成紧凑全局场景 token，再解码高斯，采用逐级增加容量的训练 | 高斯输出数量不必随输入像素直接增长；固定容量仍存在复杂场景细节的取舍 |

**关键区别：** AnySplat 是先预测像素高斯再做可微体素融合；VolSplat 把三维体素特征放到高斯预测之前；SparseSplat 选择非均匀稀疏支撑；F4Splat 学习分配密度；GlobalSplat 则从固定规模全局隐表示解码。它们不能笼统地视为相同的“高斯裁剪”。[AnySplat](https://github.com/InternRobotics/AnySplat)、[VolSplat 方法](https://arxiv.org/html/2509.19297v3)、[F4Splat 方法](https://arxiv.org/html/2603.21304v1)

资源：[VolSplat 官方代码](https://github.com/ziplab/VolSplat) · [SparseSplat 项目](https://victkk.github.io/SparseSplat-page/) · [F4Splat 官方代码](https://github.com/mlvlab/F4Splat) · [GlobalSplat 官方代码](https://github.com/R-Itk/globalsplat)

### 5.2 几何正确性：SurfSplat 与 G3Splat

[SurfSplat: Conquering Feedforward 2D Gaussian Splatting with Surface Continuity Priors](https://arxiv.org/abs/2602.02000)，2026-02 首次公开，论文标注 ICLR 2026。它将表面连续性先验与特定 alpha blending 策略引入前馈 2DGS，并提出高分辨率渲染一致性指标 HRRC，关注普通分辨率下不明显、放大后暴露的表面问题。

[G3Splat: Geometrically Consistent Generalizable Gaussian Splatting](https://arxiv.org/abs/2512.17547)，2025-12 首次公开，本文按预印本记录。它分析 pose-free 高斯仅靠视图合成监督的几何歧义，并通过几何先验改善重建、位姿与新视角合成。[项目及资源](https://m80hz.github.io/g3splat/)

**综合判断：** “高斯更少”和“表面更准”是两个相关但不同的目标。仅凭紧凑性或 PSNR 上升，不能证明模型更适合 SLAM；应同时检查深度、法线、表面精度、遮挡边界和多视图一致性。

## 6. 第四条主线：整场景、长序列与流式重建

### 6.1 FreeSplat / FreeSplat++：局部聚合和显式融合

[FreeSplat: Generalizable 3D Gaussian Splatting Towards Free-View Synthesis of Indoor Scenes](https://arxiv.org/abs/2405.17958)，2024-05 首次公开，NeurIPS 2024。它使用附近视图的低成本代价体积和跨视图聚合，再用 Pixel-wise Triplet Fusion 消除重叠区域冗余，面向更广视角的室内场景重建。[官方代码及会议信息](https://github.com/wangys16/FreeSplat)

[FreeSplat++: Generalizable 3D Gaussian Splatting for Efficient Indoor Scene Reconstruction](https://arxiv.org/abs/2503.22986)，2025-03 预印本，在整场景重建中进一步采用增量融合及加权漂浮点移除，并研究深度约束的逐场景微调。[官方代码](https://github.com/wangys16/FreeSplatPP)

**评价：** 这条路线说明，只增加输入图像不够，还需要控制重复表面和累积噪声。它们使用相机几何来聚合视图，不能与 FreeSplatter 的未标定输入混淆；FreeSplat++ 的纯前馈与微调后结果也应分列。

### 6.2 Long-LRM：扩大一次推理的覆盖范围

[Long-LRM: Long-sequence Large Reconstruction Model for Wide-coverage Gaussian Splats](https://arxiv.org/abs/2410.12781)，2024-10 首次公开，[ICCV 2025](https://openaccess.thecvf.com/content/ICCV2025/html/Ziwen_Long-LRM_Long-sequence_Large_Reconstruction_Model_for_Wide-coverage_Gaussian_Splats_ICCV_2025_paper.html)。它混合 Mamba2 与 Transformer，结合 token merging 和高斯裁剪，处理较长的已标定视图集合。正式论文展示 32 张 960×540 图像在单张 A100 上约 1 秒完成重建，这是作者特定设置的结果。

**评价：** 其意义在于扩大单次推理所覆盖的场景，尤其适合与 GS-LRM 对照阅读。Mamba2 模块或长序列输入不自动赋予整个系统在线因果性、固定工作内存和回环能力。[项目](https://arthurhero.github.io/projects/llrm/) · [作者发布的重新实现与权重](https://github.com/arthurhero/Long-LRM)

### 6.3 StreamGS：无位姿静态场景的在线重建

[StreamGS: Online Generalizable Gaussian Splatting Reconstruction for Unposed Image Streams](https://arxiv.org/abs/2503.06235)，2025-03 首次公开，[ICCV 2025](https://openaccess.thecvf.com/content/ICCV2025/papers/Li_StreamGS_Online_Generalizable_Gaussian_Splatting_Reconstruction_for_Unposed_Image_Streams_ICCV_2025_paper.pdf)。它用冻结 DUSt3R 给出粗点图，再通过对应关系调整几何与相机，合并跨帧特征来减少重复高斯。

**评价：** 这是把免逐场景渲染优化的泛化重建推进到在线处理的代表，但完整管线包含 PnP-RANSAC 等几何求解。其静态场景设定、初始几何和相邻帧匹配依赖，需要与真正动态场景、全局闭环能力分开。

### 6.4 两个 StreamSplat：名称相同，问题不同

| 项目 | 动态 StreamSplat，Wu 等 | 静态流式 StreamSplat，Song 等 |
|---|---|---|
| 完整标题 | [StreamSplat: Towards Online Dynamic 3D Reconstruction from Uncalibrated Video Streams](https://arxiv.org/abs/2506.08862) | [StreamSplat: Streaming Feed-Forward 3D Gaussian Splatting](https://arxiv.org/abs/2608.01659) |
| 时间 | 2025-06 首次公开；ICLR 2026 | 2026-08-03 预印本 |
| 输入 | 未标定动态视频；使用单目伪深度 | **已标定**静态视图流 |
| 核心 | 正交规范空间、静态高斯编码、双向形变及融合 | 体素对齐因果缓存 VACC；历史深度锚定 HPDA；缓存特征注入 CGFI |
| 关注的能力 | 不依赖相机标注的在线视频动态表示 | 复用历史三维状态，避免反复完整重建 |
| 重要边界 | 相机运动和透视效果吸收进高斯动态，不能直接视为物理准确的相机轨迹和度量地图 | 依赖已知相机；训练与推理以 4 视图块处理，应算入块等待延迟 |
| 资源状态 | [项目](https://streamsplat3d.github.io/) · [官方代码](https://github.com/DSL-Lab/StreamSplat) | 本次所查论文称代码将在接收后公开，不按已开源记录 |

**评价：** 动态版本的“无相机”来自不同的表示选择，强透视近景、快速运动和长期遮挡仍是边界；静态版本研究的是历史缓存复用，论文测试扩展到 1024 视图，但不能据此声称无限序列、无漂移或所有存储都恒定。[动态版本全文及局限](https://arxiv.org/html/2506.08862v2)、[静态版本全文](https://arxiv.org/html/2608.01659v1)

### 6.5 2026 年的动态前馈高斯：不只是一帧静态重建

除流式方法外，还有直接处理双帧或一组视频的动态高斯模型。下列工作均实际输出高斯，但不能仅凭“动态”或“长序列”归类为持续在线建图。

| 工作 | 首次公开 / 发表 | 输入与相机条件 | 核心贡献与边界 |
|---|---|---|---|
| [DGGT: Feedforward 4D Reconstruction of Dynamic Driving Scenes using Unposed Images](https://arxiv.org/abs/2512.03004) | 2025-12 / [CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/html/Chen_DGGT_Feedforward_4D_Reconstruction_of_Dynamic_Driving_Scenes_using_Unposed_CVPR_2026_paper.html) | 驾驶图像序列，联合预测内外参；集合共同推理 | 预测高斯、动态掩码、运动及生命周期，融合静态背景并插值动态部分；另有单步扩散增强，需区分原始高斯渲染和增强结果 |
| [UFO-4D: Unposed Feedforward 4D Reconstruction from Two Images](https://arxiv.org/abs/2602.24290) | 2026-02 / ICLR 2026，作者论文标注 | 不同时刻的双图，**已知内参**，预测相对外参 | 动态高斯带三维速度，以共享光栅化监督图像、点图及场景流；局部线性运动假设和双图覆盖限制了插值范围 |
| [No Pose, No Problem in 4D: Feed-Forward Dynamic Gaussians from Unposed Multi-View Videos（NoPo4D）](https://arxiv.org/abs/2605.22190) | 2026-05，预印本 | 多路同步视频、静止相机阵列；以 DA3 预测内外参 | 将高斯运动分为像平面位移与深度变化，结合伪光流学习时变高斯；不宜直接推广到移动单目相机或异步视频，另有可选后优化 |

方法依据：[DGGT](https://arxiv.org/html/2512.03004v1)、[UFO-4D](https://arxiv.org/html/2602.24290v2)、[NoPo4D](https://arxiv.org/html/2605.22190v1)。**评价：** 这一分支开始联合学习几何、相机与运动，但驾驶序列、双帧运动和固定多相机视频仍是不同实验问题。对 SLAM 读者，首先核查输入是否匹配自己的传感器与运动条件。

### 6.6 这条路线还缺少哪些闭环

以下是本文的系统分析：

- **时间闭环：** 新帧修正旧几何后，历史高斯、颜色和缓存是否同步更新？
- **空间闭环：** 相机回到旧位置时，是融合旧地图、重新定位，还是再生成一份重复地图？
- **资源闭环：** 除网络缓存外，高斯地图、历史帧和 CPU 存储会如何增长？
- **动态闭环：** 静态背景与运动物体是否分离，同一个物理点能否保持身份？

这些问题使“流式前馈 3DGS”与“完整 SLAM 系统”之间仍有值得研究的距离。

## 7. 第五条主线：单张图像到物体或场景

单图缺乏多视图三角化约束，对未观测区域必须依赖先验。物体中心重建、室内场景近邻合成和任意 360° 场景恢复的难度不同，不能只因都输入一张图就合并比较。

| 方法 | 首次公开 / 发表 | 对象与输入 | 核心设计 | 主要边界 |
|---|---|---|---|---|
| [Splatter Image](https://arxiv.org/abs/2312.13150) | 2023-12 / CVPR 2024 | 主要为物体级单图；有多视图扩展 | U-Net 输出每像素高斯；深度加三维偏移可表达物体其他表面 | 规范化物体数据、相机与尺度条件不可忽略；多视图扩展需要相对位姿 |
| [Flash3D](https://arxiv.org/abs/2406.04343) | 2024-06 / **3DV 2025** | 单图场景；焦距已知或估计 | 冻结 UniDepth，预测多层高斯与边界扩展 | 深度先验错误、遮挡和大视差会造成孔洞或模糊；评测含尺度对齐 |
| [SHARP](https://arxiv.org/abs/2512.10685) | 2025-12 / **ICLR 2026** | 单图场景；使用焦距信息 | 一次前馈预测可实时渲染的高斯，强调照片级近邻视角和度量尺度 | 主要证明附近视角合成；单图绝对尺度仍来自学习先验 |
| [UniSHARP](https://arxiv.org/abs/2606.07514) | 2026-06，预印本 | 透视、广角、鱼眼和全景单图 | 统一射线—距离表示，在特征与高斯空间处理不同相机 | 扩展的是成像模型；主评测仍约束局部可达目标视角，不等于完整自由探索 |

资源：[Splatter Image 代码](https://github.com/szymanowiczs/splatter-image) · [Flash3D 代码](https://github.com/eldar/flash3d) · [SHARP 代码与权重](https://github.com/apple/ml-sharp) · [UniSHARP 项目与资源](https://insta360-research-team.github.io/Unisharp-website/)

**Flash3D → SHARP 的阅读重点：** 从单目几何先验出发，如何把可见表面、遮挡后的内容与清晰外观编码成可快速渲染的高斯。二者作为场景路线，比物体中心的 Splatter Image 更接近手机照片和真实室内图像。[Flash3D 项目](https://www.robots.ox.ac.uk/~vgg/research/flash3d/)、[SHARP 正式论文](https://proceedings.iclr.cc/paper_files/paper/2026/hash/297fe652867e4897e9f1fe1cd715de19-Abstract-Conference.html)

SHARP 官方实现从图像元数据读取焦距；缺失时使用默认值，因此“只需上传一张图”不能解释为成像几何完全不参与推理。焦距错误可能影响几何与度量相机运动。[官方图像读取实现](https://github.com/apple/ml-sharp/blob/main/src/sharp/utils/io.py)

UniSHARP 对全景/鱼眼研究尤其相关，但其项目明确把主目标视角限制在局部范围，并要求较高重叠。应分别讨论**视场覆盖更广**与**相机可以移动更远**。[UniSHARP 评测协议](https://insta360-research-team.github.io/Unisharp-website/)

## 8. 第六条主线：生成补全与真实环境变化

### 8.1 latentSplat：带不确定性的特征高斯

[latentSplat: Autoencoding Variational Gaussians for Fast Generalizable 3D Reconstruction](https://arxiv.org/abs/2403.16292)，2024-03，ECCV 2024。它从两张已标定图片预测变分特征高斯，渲染特征后再通过 VAE-GAN 解码 RGB，面向视角外推与缺少观测的区域。[官方代码](https://github.com/Chrixtar/latentsplat)

**评价：** 它将不确定性和生成先验引入泛化重建，且不依赖扩散的多步采样。但最终外观需要神经解码器，不能与一个普通 RGB/SH 高斯文件的直接渲染完全等同。

### 8.2 LGM：物体资产生成中的前馈高斯重建器

[LGM: Large Multi-View Gaussian Model for High-Resolution 3D Content Creation](https://arxiv.org/abs/2402.05054)，2024-02，ECCV 2024。完整生成流程先由 MVDream / ImageDream 产生四视图，再用带相机射线编码和跨视图注意力的 U-Net 预测高斯。[项目](https://me.kiui.moe/lgm/) · [官方代码](https://github.com/3DTopia/LGM)

**评价：** Gaussian 重建阶段是前馈的，文本/单图到资产的完整流程仍有多视图扩散采样；可选网格转换另含优化。它适合说明前馈高斯作为生成管线中间表示的价值，不宜直接作为真实场景几何重建基线。

### 8.3 MVSplat360：用视频生成补足稀疏观测

[MVSplat360: Feed-Forward 360 Scene Synthesis from Sparse Views](https://arxiv.org/abs/2411.04924)，2024-11，NeurIPS 2024。它从稀疏已标定图片构建高斯，将渲染特征作为 Stable Video Diffusion 的条件，合成覆盖更大视角范围的视频。[项目](https://donydchen.github.io/mvsplat360/) · [官方代码](https://github.com/donydchen/mvsplat360)

**评价：** 这是几何约束与视频生成结合的代表。高斯提供可控视角和粗几何，扩散模型提供缺少观测时的外观先验；完整链条有多步去噪，生成后的照片质量不能直接代表原始高斯本身的几何精度。

### 8.4 WildSplat：把跨光照变化纳入前馈重建

[WildSplat: Feedforward Gaussian Splatting from Unposed In-the-Wild Images](https://arxiv.org/abs/2607.05347)，2026-07；原论文和作者项目页标注 **ECCV 2026 已录用**。它从无位姿、外观不一致的照片中重建，采用几何与外观双分支，并让参考图像控制目标外观。[项目](https://zju3dv.github.io/wildsplat/)

**评价：** 这项工作处理的是跨时段、光照和曝光变化，不应与未观测区域生成混为一谈。对长期建图的启发是：同一块表面颜色变了，不一定意味着几何变了。但外观条件化也不自动等于物理正确的材质分解与重光照。

### 8.5 需要单独列出的混合方案：InstantSplat

[InstantSplat: Sparse-view Gaussian Splatting in Seconds](https://arxiv.org/abs/2403.20309)，2024-03 首次公开，本文按预印本记录；早期版本标题含 SfM-free。它用预训练几何模型获得稠密几何及相机初始化，再通过 Gaussian Bundle Adjustment 联合优化相机和高斯。[项目](https://instantsplat.github.io/) · [官方代码](https://github.com/NVlabs/InstantSplat)

**分类：前馈初始化 + 逐场景快速优化。** 它是重要的质量—耗时折中基线。SfM-free 表示不依赖传统 SfM 初始化，不能据此称为全流程无优化；“几秒完成”也不是纯前馈的定义。

## 9. 如何比较这些论文：比一张 PSNR 表更重要的内容

### 9.1 先确保实验问题相同

| 维度 | 需要固定或明确报告的条件 |
|---|---|
| 输入 | 图像数量、分辨率、视角间隔、重叠率；单图、双图、多图、长视频分别报告 |
| 相机 | 内外参真实已知、估计、完全未知；焦距是否共享；是否允许目标相机对齐 |
| 输出 | 静态高斯、带特征的高斯、神经解码图像、动态表示、网格；能否导出独立可渲染资产 |
| 计算流程 | 几何预处理、主网络、PnP/对齐、后优化、渲染、扩散生成各耗时多少 |
| 学习成本 | 训练数据、教师模型、预训练权重、训练分辨率与模型大小；是否跨场景共享 |
| 评价范围 | 输入视图插值、宽基线外推、不可见区域生成、跨数据集测试分别报告 |
| 流式条件 | 是否使用未来帧、块大小与等待延迟、地图和缓存随输入长度的增长 |

**典型陷阱：** NoPoSplat 的目标相机对齐、SelfSplat 的目标图像参与位姿估计、FLARE 的内参条件实验、AnySplat 的后优化、MVSplat360 的扩散解码和 MVSGaussian 的目标视角相关推理，都会改变比较含义。应按具体实验配置比较，而不是按论文标题比较。[NoPoSplat](https://arxiv.org/html/2410.24207v1)、[SelfSplat](https://arxiv.org/html/2411.17190v5)、[FLARE](https://arxiv.org/html/2502.12138v4)、[AnySplat](https://arxiv.org/html/2505.23716v2)、[MVSplat360](https://donydchen.github.io/mvsplat360/)、[MVSGaussian](https://arxiv.org/abs/2405.12218)

### 9.2 常用数据与它们回答的问题

下表归纳上述代表论文的使用方式，不意味着每篇论文都采用同一划分和协议。

| 数据 / 场景 | 主要价值 | 外推结论时的限制 |
|---|---|---|
| RealEstate10K | 泛化双视图/稀疏视图 NVS 的常见起点 | 在相似视频分布上表现好，不代表大规模完整建图已解决 |
| ACID | 常用于跨数据集泛化 | 要检查是否真正未参与训练、是否使用一致相机协议 |
| DL3DV | 更复杂场景、更广覆盖、多视图和 360° 合成 | 采样、子集与视角跨度不同会显著影响难度 |
| ScanNet / ScanNet++ | 室内几何与 NVS，便于检查深度和表面 | RGB-D 真值或几何教师是否进入训练需要说明 |
| Tanks and Temples | 较大范围的真实场景重建 | 稀疏输入方式与传统密集多视图结果需区分 |
| Objaverse / CO3D | 物体中心重建与生成、真实物体视图变化 | 物体背景、尺度和视图分布与一般场景不同 |
| MegaScenes / Phototourism | 跨外观、非受控照片集合 | 光照一致性和相机估计成为额外变量 |

代表协议来源：[pixelSplat](https://arxiv.org/abs/2312.12337)、[DepthSplat](https://arxiv.org/abs/2410.13862)、[Long-LRM](https://openaccess.thecvf.com/content/ICCV2025/html/Ziwen_Long-LRM_Long-sequence_Large_Reconstruction_Model_for_Wide-coverage_Gaussian_Splats_ICCV_2025_paper.html)、[FreeSplatter](https://arxiv.org/abs/2412.09573)、[WildSplat](https://zju3dv.github.io/wildsplat/)。

### 9.3 推荐报告的指标

以下是本文建议的评价框架：

- **外观：** PSNR、SSIM、LPIPS；生成式结果还需感知评价，不能只看逐像素误差。
- **几何：** 深度误差、法线误差、表面精度与完整度、多视图重投影一致性；注明尺度对齐方式。
- **位姿：** 相对旋转/平移精度；用于 SLAM 时再报告 ATE、RPE、尺度漂移、失败率和回环后的误差。
- **表示成本：** 高斯数量、模型文件、GPU 峰值显存、CPU 存储和渲染显存，分别报告。
- **运行成本：** 首次输出时间、重建时间、相机求解时间、单帧更新时间、纯渲染 FPS；给出设备与输入条件。
- **长期稳定性：** 随序列长度变化的误差和工作内存曲线、重复表面、遗忘、再进入已见区域后的表现。
- **动态场景：** 区分逐时刻渲染质量、时序几何一致性和同一物质点的跟踪准确性。

## 10. 综合趋势与值得研究的问题

本节为基于文献的判断与研究假设，不代表已经验证的新颖性或性能收益。

### 10.1 从“预测更准的像素高斯”到“维护可用的三维地图”

早期模型天然沿输入图像组织输出；体素、稀疏点和全局 token 开始让预测更贴近三维场景。下一步值得考察的是：**新增观测应该创建高斯，还是修正已有高斯？** 可以用重复观察、遮挡后重现和长序列输入验证，而不只测固定双图。[VolSplat](https://arxiv.org/abs/2509.19297)、[F4Splat](https://arxiv.org/abs/2603.21304)、[静态 StreamSplat](https://arxiv.org/abs/2608.01659)

### 10.2 深度、透明度、尺度和颜色可能互相“补偿错误”

渲染损失允许模型通过改颜色、不透明度和高斯尺度弥补几何偏差。几何正则、表面参数化和基础模型先验都有价值，但应验证它们是在减少真实几何误差，还是仅改善特定视角的外观。[G3Splat](https://arxiv.org/abs/2512.17547)、[SurfSplat](https://arxiv.org/abs/2602.02000)

**可检验问题：** 当相机存在小扰动、视距变化或视角转到训练观测之外时，模型是否仍保持同一表面？比较深度、法线与重投影误差，比只比较插值 PSNR 更有说服力。

### 10.3 无位姿前馈重建如何与 SLAM 的全局修正衔接

NoPoSplat、AnySplat 等提供快速初始几何；Splat-SLAM 表明，全局几何变化后地图也需更新。因此值得研究**低自由度相机/尺度校正、局部高斯更新和全局地图一致性的配合**，并明确哪些变量被优化。[NoPoSplat](https://arxiv.org/abs/2410.24207)、[AnySplat](https://arxiv.org/abs/2505.23716)、[Splat-SLAM](https://openaccess.thecvf.com/content/CVPR2025W/VOCVALC/html/Sandstrom_Splat-SLAM_Globally_Optimized_RGB-only_SLAM_with_3D_Gaussians_CVPRW_2025_paper.html)

**可检验问题：** 回环后，已有表面能否在不重新优化全部高斯的情况下修正？相机误差大时，前馈先验会帮助恢复，还是把错误写进长期地图？

### 10.4 动态表示需要分清相机运动与真实物体运动

把相机效应吸收到形变中的表示可以改善视频重建，但对机器人定位和长期物质点跟踪，通常还需要物理意义明确的公共坐标。[动态 StreamSplat](https://arxiv.org/html/2506.08862v2)

**可检验问题：** 在相机运动与物体运动同时发生时，能否稳定区分二者？动态高斯是否保留同一物理点的身份，还是每帧生成外观相似的新点？

### 10.5 泛化正在从“新场景”扩展到“新成像条件”

WildSplat 关注外观不一致，UniSHARP 关注广角/鱼眼/全景输入。这说明相机模型、曝光、照明及采集方式正在成为更明确的变量。[WildSplat](https://arxiv.org/abs/2607.05347)、[UniSHARP](https://arxiv.org/abs/2606.07514)

**可检验问题：** 同一场景不同时间、相机或投影模型下，模型是否保持相同几何？改进来自真正的几何鲁棒性，还是训练集更接近测试分布？

### 10.6 对 SLAM / 三维视觉研究者的优先建议

| 关注目标 | 建议首先比较的工作 | 能形成清晰问题的切入点 |
|---|---|---|
| 已知位姿下的泛化重建 | MVSplat、DepthSplat、VolSplat | 几何精度、弱纹理/遮挡、多视图融合 |
| 未标定稀疏重建 | NoPoSplat、FLARE、AnySplat、DA3-GS | 相机条件差异、几何监督与泛化、位姿误差传播 |
| 紧凑高斯表示 | AnySplat、SparseSplat、F4Splat、GlobalSplat | 固定高斯预算下的几何—外观取舍与跨视图去重 |
| 在线建图 | FreeSplat++、StreamGS、静态 StreamSplat；结合 Splat-SLAM | 地图合并、历史修正、回环和资源增长 |
| 单图真实场景 | Flash3D、SHARP；广视场时加 UniSHARP | 局部视角范围、焦距误差、遮挡补全与真实几何 |
| 动态视频 | 动态 StreamSplat、UFO-4D；驾驶看 DGGT，固定多相机看 NoPo4D | 相机/物体运动解耦、时序身份、长期遮挡，先匹配输入设定 |

选题时优先围绕一个能反复复现的失败机制展开。仅组合“基础模型 + Gaussian 头 + 时序模块”，不足以说明解决了什么新问题。

## 11. 建议阅读顺序与最小文献包

### 11.1 建立主线的 10 篇

1. **原始 3DGS**：理解表示、可微渲染、增密和逐场景优化。
2. **pixelSplat**：理解跨场景训练后直接预测高斯的起点。
3. **MVSplat**：理解代价体积、深度反投影与高斯属性预测。
4. **DepthSplat**：理解单目先验、多视图约束和深度学习的连接。
5. **NoPoSplat**：理解无位姿输入与公共参考坐标。
6. **AnySplat**：理解几何教师、多视图预测和可微融合。
7. **Long-LRM**：理解更大输入集合与计算扩展。
8. **VolSplat**：理解为何要从像素组织转向三维组织。
9. **F4Splat**：理解高斯预算和可学习密度分配。
10. **StreamGS / 静态 StreamSplat 二选一**：前者看未标定在线管线，后者看三维缓存与历史复用。

这不是性能排名。对应论文和代码链接均在前文条目中；如果主要做几何，应额外优先读 **2DGS、G3Splat、SurfSplat**。

### 11.2 按兴趣扩展

- **位姿未知输入：** Splatt3R → NoPoSplat / PF3plat / SelfSplat → FreeSplatter / FLARE → AnySplat / DA3-GS；各方法的内参条件分别核查。
- **单图场景：** Splatter Image（物体前史）→ Flash3D → SHARP → UniSHARP。
- **表示紧凑性：** FreeSplat / AnySplat → VolSplat → SparseSplat / F4Splat / GlobalSplat。
- **生成先验：** latentSplat → LGM（物体）/ MVSplat360（场景）；同时检查神经解码与扩散成本。
- **在线与动态：** Long-LRM（离线长输入）→ StreamGS（静态在线）→ 两个 StreamSplat；再按输入条件扩展到 UFO-4D、DGGT 或 NoPo4D。
- **实际部署与优化折中：** InstantSplat、FreeSplat++ 后优化，以及 AnySplat 的可选后优化。

### 11.3 一句话总结

**前馈式 3DGS 已从“几张图快速出一个可渲染模型”，发展到同时研究相机恢复、几何先验、表示预算、长期更新与真实成像条件。对 SLAM 而言，最关键的衡量标准是：这个快速生成的表示，能否被持续融合、校正和可靠地用于几何推理。**

## 12. 新增专题：3DGS / 4DGS 与 Point Tracking / Tracking Any Point

> **范围与口径：** 检索截至 **2026-09-24**，回溯 2023 年以来的代表性工作。本节将“4DGS”作为动态高斯方法的宽泛统称，涵盖持久高斯、形变场、运动基、运动骨架和时间条件预测；不限定为某一篇同名论文，也不要求每个方法都使用四维协方差高斯。正文优先使用论文、正式会议页、作者项目和官方实现；“未见 TAP 定量”表示在本次核查的正文、补充或项目资料中未找到相应结果，不等于证明作者从未进行该实验。

### 12.1 先看结论：两类任务正在汇合，但不能互相替代

**这一方向的核心问题是：能否让一个可渲染的高斯表示，同时记录“同一个物理点随时间去了哪里”。** 从论文脉络看，有三条主线：

1. **重建产生轨迹。** Dynamic 3D Gaussians 以持久高斯表达运动；DynOMo 将这一思路推进到单目在线优化。两者都不以现成的 2D 点轨迹作为必要监督，但仍有相机、深度或特征方面的输入条件。[Dynamic 3D Gaussians](https://arxiv.org/abs/2308.09713)、[DynOMo](https://arxiv.org/abs/2409.02104)
2. **轨迹帮助重建，再从重建中读取轨迹。** Shape of Motion、MoSca、4D-Fly、MotionScale 把外部点跟踪、深度和运动约束融合到动态高斯中。这是近几年非常清晰的技术路线；收益应同时用渲染和跟踪实验验证。[Shape of Motion](https://arxiv.org/abs/2407.13764)、[MoSca](https://arxiv.org/abs/2405.17421)、[4D-Fly](https://diankun-wu.github.io/4D-Fly/)、[MotionScale](https://arxiv.org/abs/2603.29296)
3. **跨场景学习高斯及运动。** MoVieS、C4G 将动态表示与轨迹输出纳入前馈模型；Video-GMAE 则研究通过动态高斯视频重建，学习可用于点跟踪的表征。它们与第 3–8 节的前馈重建主线直接相接，但监督方式、相机条件和跟踪输出并不相同。[MoVieS](https://arxiv.org/abs/2507.10065)、[C4G](https://arxiv.org/abs/2605.31595)、[Video-GMAE](https://videogmae.org/)

**阅读时最重要的判断：** 高斯有运动、能渲染新视角、能输出任意查询点的长期轨迹，是三个不同层次。持续保留一个 Gaussian ID，并不能单独证明它始终对应同一物理表面点；颜色变化、遮挡、增密和裁剪都可能破坏这种对应。这是本综述对表示与任务关系的分析，而非某篇论文的性能结论。

### 12.2 统一概念与分类

#### 12.2.1 Point tracking、光流和相机 tracking 的区别

- **TAP / 任意点跟踪：** 输入视频和查询点 $(u_q,v_q,t_q)$，输出该物理点在其他帧中的位置及可见性；查询点可以选在图像中的物体区域内部，不限于角点或语义关键点，并对应查询帧中可见的物质点。2D TAP 输出像素轨迹，3D TAP 还需明确三维坐标、尺度和坐标系。[TAP-Vid](https://tapvid.github.io/)、[TAPVid-3D](https://tapvid3d.github.io/)
- **光流：** 通常描述两帧之间的像素对应。多次串接光流能构造长轨迹，但跨遮挡身份保持与误差积累仍需额外处理。本文把仅使用成对光流的工作标为“对应先验”，不直接归为完整 TAP 方法。
- **相机 tracking：** 估计相机自身的位姿，常用 ATE / RPE 衡量。它与场景中任意物质点的轨迹是不同输出。
- **静态 feature tracks：** 同一个静态场景点在多张图像中的观测链，常用于 SfM、标定和束调整；不自动包含动态物体的长程点跟踪。
- **分割传播：** Track Anything / SAM2 可以输出随时间变化的物体掩码；同一掩码内的每个像素是否对应同一物理点，需要另一个模型解决。

#### 12.2.2 按信息流，而不是按论文标题分类

| 类别 | 轨迹与高斯的关系 | 代表工作 | 应核查的证据 |
|---|---|---|---|
| 高斯 → 轨迹 | 从持久动态表示读取运动，外部点轨迹不是必要输入 | Dynamic 3D Gaussians、DynOMo | 查询点如何绑定高斯、可见性如何计算、是否评测轨迹 |
| 轨迹 → 高斯 | 已有 tracker / 光流提供初始化或约束 | TrackerSplat、MOSAIC-GS；MoDGS 属光流分支 | 是否真的改善重建；不能据此声称提出了更强 tracker |
| 轨迹 → 高斯 → 轨迹 | 用外部轨迹约束场景，再输出几何一致的对应 | Shape of Motion、MoSca、4D-Fly、MotionScale | 输入教师与输出轨迹的差别、独立跟踪评估 |
| 前馈高斯 + 运动 | 网络在新视频上预测动态表示和轨迹 | MoVieS、C4G | 是否需要已知相机、整段视频及测试时优化 |
| 高斯用于跟踪表征学习 | 用动态高斯视频重建塑造跨帧对应能力 | Video-GMAE | 零样本与微调协议、2D 跟踪与真实三维恢复的区别 |
| 相邻任务 | 高斯服务于生成、静态配准或 SLAM | GS-DiT、DreamScene4D、TrackGS、ProDyG | tracking 到底指什么，指标属于哪个模块 |

这几类可以重叠。例如，MoSca 既利用轨迹，又能输出对应关系；分类只强调它主要如何连接两个任务。

### 12.3 核心论文对照表

年份以“预印本 / 正式会议”区分。**“优化”指对测试视频或场景执行梯度更新；“前馈”指已有模型在新片段上预测表示，仍可能依赖外部相机估计或后处理。** 表中的跟踪证据只记录已核实内容，不构成统一性能排行榜。

| 工作与发表信息 | 场景与重要输入条件 | 跟踪的作用 | 计算方式 | 已核实的跟踪证据 |
|---|---|---|---|---|
| [Dynamic 3D Gaussians](https://arxiv.org/abs/2308.09713)，2023 / 3DV 2024 | 同步多相机、标定；论文首帧用深度相机点云初始化 | 高斯运动产生轨迹 | 逐时间步优化 | 持久 3D / 6-DoF 运动及点跟踪实验 |
| [Shape of Motion](https://arxiv.org/abs/2407.13764)，2024 / ICCV 2025 | 单目；相机、深度、掩码、TAPIR tracks | 输入监督 + 输出 | 全视频优化 | 2D 与 3D 点跟踪定量 |
| [MoSca](https://arxiv.org/abs/2405.17421)，2024 / CVPR 2025 | 单目；深度与外部 tracks，可优化相机 | 骨架初始化、监督及对应输出 | 全视频优化 | DyCheck 2D correspondence，PCK-T |
| [DynOMo](https://arxiv.org/abs/2409.02104)，2024 / 3DV 2025 | 单目；深度、特征、掩码；估计外参 | 无输入 tracks / flow，输出轨迹 | 在线逐帧优化 | TAPVid-DAVIS、Panoptic Sports、iPhone |
| [4D-Fly](https://diankun-wu.github.io/4D-Fly/)，CVPR 2025 | 单目；内外参、深度、前景及 TAPIR tracks | 传播先验 + 输出 | 流式扩展及逐帧优化 | DyCheck iPhone 2D / 3D 点跟踪 |
| [TrackerSplat](https://doi.org/10.1145/3757377.3763829)，SIGGRAPH Asia 2025；arXiv 2026 | 标定多视图视频；预训练 tracker | 预对齐高斯，辅助重建 | 逐场景优化，可多 GPU 并行 | 主要是渲染质量和重建吞吐；未见标准 TAP 定量 |
| [MotionScale](https://arxiv.org/abs/2603.29296)，CVPR 2026 | 单目；几何、分割和 CoTracker3 等先验 | 运动监督 + 输出 | 渐进扩展及历史联合优化 | 有点跟踪定量及查询轨迹构造 |
| [MOSAIC-GS](https://arxiv.org/abs/2601.05368)，CVPR 2026 | 单目；相机、深度、分割、tracks | 主要用于动态初始化 | 全片预处理 + 优化 | 主要验证动态 NVS；未见标准 TAP 输出评测 |
| [MoVieS](https://arxiv.org/abs/2507.10065)，2025 / CVPR 2026 | 单目视频、已知逐帧内外参与时间戳 | 训练监督 + 推理输出 | 片段联合前馈 | TAPVid-3D 三子集 |
| [C4G](https://arxiv.org/abs/2605.31595)，2026 预印本 | 单目视频与时间戳；模型输入不要求相机位姿 | 训练轨迹监督、Gaussian 轨迹及特征场 | 全时间上下文前馈 | 直接轨迹的 ADT / DriveTrack 2D 实验；另有特征场跟踪实验 |
| [Video-GMAE](https://videogmae.org/)，2025 / CVPR 2026 | RGB 片段；固定虚拟相机建模 | 自监督预训练，零样本 / 监督读出 | 前馈预测 + 轨迹传播 | TAP-Vid / Kubric 2D；须核对短片段评测协议 |

### 12.4 重点论文：方法、价值与限制

#### 12.4.1 Dynamic 3D Gaussians：以持久身份连接重建与跟踪

**完整题名：** *Dynamic 3D Gaussians: Tracking by Persistent Dynamic View Synthesis*。

- **方法：** 首帧建立高斯，后续通过局部刚性、旋转和等距约束，使同一组高斯随场景运动。任意 3D 查询点可以绑定到高斯的局部坐标并随其运动；2D 查询还需深度反投影与重新投影。[论文](https://arxiv.org/abs/2308.09713)
- **价值：** 把用于渲染的基元变成持久运动载体，是理解后续工作的合适起点。
- **限制：** 依赖同步标定多相机；论文实验首帧使用深度相机稀疏点云。逐帧在线优化不等于实时推理，首帧未建模、后续新进入的内容也较难处理。[项目与演示](https://dynamic3dgaussians.github.io/)
- **实现注意：** 作者仓库是部分代码发布；论文的固定颜色与代码中的颜色时间一致性软约束存在差异，复现时需核对。[官方代码](https://github.com/JonathonLuiten/Dynamic3DGaussians)

#### 12.4.2 Shape of Motion：轨迹、几何与低维运动基联合优化

**完整题名：** *Shape of Motion: 4D Reconstruction from a Single Video*。

- **方法：** 用 canonical 高斯、共享 SE(3) 运动基及高斯固定混合系数表达运动。TAPIR 轨迹经深度提升参与初始化，之后联合图像、几何、轨迹及运动约束；可从查询时刻的渲染权重读取目标时刻 XYZ。[方法正文](https://arxiv.org/html/2407.13764v2)
- **价值：** 同时研究动态 NVS 和长期 2D / 3D tracking，展示了“用轨迹拟合可渲染运动场，再查询轨迹”的闭环。
- **限制：** 需要整段视频优化，并依赖相机、深度和前景掩码。相机可以先估计，不代表优化器完全无需相机输入；不同版本的预处理也有变化。[正式论文](https://openaccess.thecvf.com/content/ICCV2025/papers/Wang_Shape_of_Motion_4D_Reconstruction_from_a_Single_Video_ICCV_2025_paper.pdf)
- **复现入口：** [项目](https://shape-of-motion.github.io/)、[官方代码与预处理](https://github.com/vye16/shape-of-motion/)。对比时应记录相机来源、深度尺度对齐方式和输入 tracker。

#### 12.4.3 MoSca：从稀疏轨迹构造可变形的运动骨架

**完整题名：** *MoSca: Dynamic Gaussian Fusion from Casual Videos via 4D Motion Scaffolds*。

- **方法：** 用轨迹与深度建立稀疏 4D motion scaffold；节点带有运动，时空拓扑和局部约束补全未观测部分。高斯可来自多个参考时刻，经蒙皮随骨架运动并融合。[方法正文](https://arxiv.org/html/2405.17421v2)
- **价值：** 把较稀疏的点对应转换成能驱动密集高斯的结构，同时解决不同时间所见几何的融合。作者实现支持多种深度模型和 BootsTAPIR / CoTracker 等 tracker。[官方代码](https://github.com/JiahuiLei/MoSca)
- **评测边界：** DyCheck 的对应关系结果使用 PCK-T，属于 2D correspondence；不能改称 TAP-Vid AJ 或完整 TAP3D 结果。其主要 DyCheck 设置使用 iPhone LiDAR 深度，另有 RGB 深度替代实验。[CVPR 正式论文](https://openaccess.thecvf.com/content/CVPR2025/papers/Lei_MoSca_Dynamic_Gaussian_Fusion_from_Casual_Videos_via_4D_Motion_CVPR_2025_paper.pdf)
- **限制：** 全片优化；外部 tracks 和深度出错会影响骨架。未观测区域及无法用几何形变解释的外观变化仍困难。[当前项目页](https://jiahuilei.com/projects/mosca/)

#### 12.4.4 DynOMo：不依赖轨迹监督的单目在线重建与点跟踪

**完整题名：** *DynOMo: Online Point Tracking by Dynamic Online Monocular Gaussian Reconstruction*。

- **方法：** 逐帧优化相机和动态高斯，以 RGB、深度、特征、语义及局部运动约束保持对应；查询像素绑定高斯并持续追踪。它不用外部点轨迹或光流监督，但使用其他预训练先验。[论文正文](https://arxiv.org/html/2409.02104v2)
- **价值：** 是“从在线重建中产生点跟踪”的直接案例，并有 TAPVid-DAVIS 及其他数据上的跟踪实验。
- **比较陷阱：** DynOMo⋆ 使用真值选择更合适的高斯，是 oracle，不能当作可部署主结果。论文中 Panoptic Sports 与 iPhone 的深度分别来自 Dynamic 3D Gaussians、Shape of Motion 的预处理；DAVIS 条件又不同。[官方数据与评测说明](https://github.com/dvl-tum/DynOMo)
- **限制：** online 指逐帧处理与优化，不意味着一次前向或实时。大幅相机运动、深度不一致和严重遮挡会影响结果。[项目失败案例](https://jennyseidenschwarz.github.io/DynOMo.github.io/)

#### 12.4.5 4D-Fly：利用跟踪锚点显式传播高斯

**完整题名：** *4D-Fly: Fast 4D Reconstruction from a Single Monocular Video*。

- **方法：** 将 TAPIR 轨迹、深度及相机参数组合成三维运动锚点，传播动态高斯，再优化静态与动态部分，并扩展 canonical map。野外管线还用 DROID-SLAM、DepthCrafter 和前景分割。[CVPR 论文](https://openaccess.thecvf.com/content/CVPR2025/papers/Wu_4D-Fly_Fast_4D_Reconstruction_from_a_Single_Monocular_Video_CVPR_2025_paper.pdf)
- **证据：** 有 DyCheck iPhone 上的 2D AJ / 位置精度 / OA，以及 3D EPE 和距离阈值精度。不能把这一结果改标为 TAPVid-DAVIS。
- **限制：** 是“传播 + 逐帧优化”，前置先验是否使用未来帧要单独审核；论文所报重建耗时与渲染 FPS 属于不同阶段。[正式会议页](https://openaccess.thecvf.com/content/CVPR2025/html/Wu_4D-Fly_Fast_4D_Reconstruction_from_a_Single_Monocular_Video_CVPR_2025_paper.html)
- **资源状态：** 本次在[作者项目页](https://diankun-wu.github.io/4D-Fly/)核实到论文、补充与视频，未找到可确认的官方实现入口。

#### 12.4.6 TrackerSplat：跟踪先对齐，梯度再细化

**完整题名：** *TrackerSplat: Exploiting Point Tracking for Fast and Robust Dynamic 3D Gaussians Reconstruction*。

- **方法：** 对标定多视图视频提取点轨迹，用 PWI-LS 估计投影运动，经多视图关系更新高斯位置、旋转和尺度，再做图像重建优化。论文比较多个 tracker，最终选择 DOT；不能写成默认使用 CoTracker3。[论文正文](https://arxiv.org/html/2604.02586v1)
- **价值：** 对大帧间位移和多 GPU 分帧重建很直接：先把高斯移到接近正确的位置，有助于避免单靠图像梯度导致的褪色、改色和漂移。
- **边界：** 主要目标是重建稳定性与吞吐，未核到标准 TAP 定量；需要已标定多视图及场景优化，不能归为单目前馈 tracker。[正式出版记录](https://doi.org/10.1145/3757377.3763829)
- **年份与代码：** 正式发表于 **SIGGRAPH Asia 2025**，arXiv 于 **2026-04** 上传，不能仅按 arXiv 号归为 2026 年首发。[官方代码](https://github.com/yindaheng98/TrackerSplat)

#### 12.4.7 MotionScale：在更长视频中组织与优化高斯运动

**完整题名：** *MotionScale: Reconstructing Appearance, Geometry, and Motion of Dynamic Scenes with Scalable 4D Gaussian Splatting*。

- **方法：** 用以聚类为中心的全局 / 局部运动基驱动高斯，渐进扩展动态场景。真实视频默认先验包括 π³ 几何、SAM2 分割和 CoTracker3 轨迹；外参进一步优化。[论文与查询轨迹公式](https://arxiv.org/html/2603.29296v1)
- **与 TAP 的联系：** 可按查询帧的 alpha-blending 权重组合目标时刻高斯位置，得到三维轨迹并投影；论文也进行点跟踪评估。
- **限制：** 这是逐场景渐进优化，非前馈。后期会采样整个已处理历史中的帧对联合细化，不能据此认定总内存固定；历史回放本身不违反因果性，严格因果性还需核查预处理和窗口是否使用未来帧。[CVPR 正式记录](https://openaccess.thecvf.com/content/CVPR2026/html/Zhou_MotionScale_Reconstructing_Appearance_Geometry_and_Motion_of_Dynamic_Scenes_with_CVPR_2026_paper.html)
- **资源：** [项目](https://hrzhou2.github.io/motion-scale-web/)、[官方代码](https://github.com/hrzhou2/motion-scale)。其意义在于研究更大时间跨度下如何组织运动，而非证明点身份问题已经解决。

#### 12.4.8 MOSAIC-GS：先恢复运动，再拟合外观

**完整题名：** *MOSAIC-GS: Monocular Scene Reconstruction via Advanced Initialization for Complex Dynamic Environments*。

- **方法：** 将深度、相机、分割和 BootsTAPIR / CoTracker 等轨迹用于初始化；用实例级刚性约束细化运动，给动态高斯分配 Poly-Fourier 时间曲线，再进行渲染优化。[论文](https://arxiv.org/html/2601.05368v1)
- **价值：** 强调运动初始化的重要性，是“现成 TAP 能怎样改善 4DGS”的直接例子。
- **边界：** 输入定义仍需要相机和深度，且采用全片先验与场景优化。主要验证 NVS，本次未核到独立任意点轨迹输出的标准 TAP 评估。[CVPR 正式记录](https://openaccess.thecvf.com/content/CVPR2026/html/Morkva_MOSAIC-GS_Monocular_Scene_Reconstruction_via_Advanced_Initialization_for_Complex_Dynamic_CVPR_2026_paper.html)

#### 12.4.9 MoVieS：前馈重建与三维点轨迹的直接结合

**完整题名：** *MoVieS: Motion-Aware 4D Dynamic View Synthesis in One Second*。

- **方法：** 从视频预测像素对齐高斯，用时间条件 motion head 预测目标时刻的三维位移及属性变化，同时支持渲染、深度与点轨迹。[方法和实验](https://arxiv.org/html/2507.10065v2)
- **关键条件：** 输入包括每帧已知内参、外参及时间戳。真实视频可先用 MegaSaM 求相机，但这属于额外处理；不能归为无需相机的模型。
- **跟踪证据：** 有任意像素对应的 3D 轨迹构造和 TAPVid-3D 三子集评测；训练使用几何与 3D 轨迹监督。[CVPR 正式记录](https://openaccess.thecvf.com/content/CVPR2026/html/Lin_MoVieS_Motion-Aware_4D_Dynamic_View_Synthesis_in_One_Second_CVPR_2026_paper.html)
- **限制：** 对一个片段联合前馈，不等于逐帧因果推理；长序列、高分辨率与外部相机成本应计入部署评估。[官方代码](https://github.com/chenguolin/MoVieS)

#### 12.4.10 C4G：从逐像素高斯转向紧凑的全局运动表示

**完整题名：** *Learning Global Motion with Compact Gaussians for Feed-Forward 4D Reconstruction*；2026-05 预印本。

- **方法：** 时间条件的可学习 Gaussian query tokens 汇聚整段上下文，再解码动态高斯；模型输入为视频和时间戳，无需提供相机位姿。训练仍使用几何、相机及 CowTracker 轨迹等监督。[论文](https://arxiv.org/html/2605.31595v1)
- **两种跟踪用途：** 一种将查询关联到最近高斯并传播其中心，在 ADT / DriveTrack 做 2D tracking；另一种把视觉特征提升到 4D 高斯场，通过渲染特征进行匹配。二者应分别看待。[项目](https://cvlab-kaist.github.io/C4G/)
- **价值与限制：** 为第 5 节讨论的“减少逐像素高斯冗余”增加动态场景实例。最近高斯关联会引入查询偏差；全时间上下文不是因果流式。论文另有扩散式渲染增强和 NVS 测试时相机对齐，整体耗时应与基础高斯前馈分别报告。

#### 12.4.11 Video-GMAE：用动态高斯重建视频，学习点对应

**完整题名：** *Tracking by Predicting 3-D Gaussians Over Time*；2025-12 首次公开，项目标注 CVPR 2026 Highlight。[论文记录](https://arxiv.org/abs/2512.22489)、[项目](https://videogmae.org/)

- **方法：** 掩码视频编码器预测首帧高斯和后续残差，用视频重建进行自监督预训练。零样本时把高斯投影位移渲染成 flow，结合固定的 top-k 高斯锚点传播 2D 查询点；官方零样本路径为前馈及解析传播，无逐视频梯度优化。
- **监督口径：** 预训练不用轨迹标签；冻结编码器后的监督读出、完整微调使用 Kubric 标签，零样本提取器的超参数也依据训练集表现选择。不能把所有表格都归为无监督结果。[正文 §4–7](https://arxiv.org/html/2512.22489v2)
- **三维边界：** 使用固定虚拟相机建模，论文明确不能恢复度量三维。其贡献是对应表征与 2D tracking，不能据“3-D Gaussians”推断已实现真实世界尺度的 TAP3D。
- **评测注意：** 正文比较注明 stride=5；本次所见[官方零样本评测实现](https://github.com/tekotan/video-gmae/blob/master/vidgmae/models/zeroshot_gmae.py)还将指标截取到输入片段的前 5 帧。该观察限定于所核查代码路径，不能推定每个论文数字都由此产生；复现时须对齐查询采样、片段长度和计分范围，不能直接拿数字做完整长视频排名。

### 12.5 补充工作：相关，但与标准 TAP 的距离不同

下面这些工作有助于理解技术来源和应用边界。它们不都提出任意点跟踪器。

| 工作 | 与 GS + tracking 的具体联系 | 应如何解读 |
|---|---|---|
| **DynMF**，2023 / ECCV 2024；*Neural Motion Factorization for Real-time Dynamic View Synthesis with 3D Gaussian Splatting* | 共享运动基与每高斯固定系数给出连续轨迹，项目展示 trajectory tracking | 主要研究动态 NVS，是运动表示背景；渲染时运行小网络不等于跨场景前馈重建。[论文](https://arxiv.org/abs/2312.00112)、[项目](https://agelosk.github.io/dynmf/) |
| **GFlow**，2024 / AAAI 2025；*Recovering 4D World from Monocular Video* | MASt3R 几何与 UniMatch 光流支撑相机 / 高斯优化，并展示高斯点轨迹 | 顺序逐帧优化，主要定量为重建与相机指标；未见标准 TAP 定量。预处理因果性需另查。[论文](https://arxiv.org/html/2405.18426)、[官方代码](https://github.com/littlepure2333/GFlow) |
| **MoDGS**，2024 / ICLR 2025；*Dynamic Gaussian Splatting from Casually-captured Monocular Videos with Depth Priors* | 已知相机、深度与 RAFT 成对光流构造三维对应，初始化可逆变形场及高斯 | 属于对应先验辅助重建；不是 CoTracker 长轨迹方法，主要验证 NVS。[论文](https://arxiv.org/html/2406.00434)、[项目](https://modgs.github.io/) |
| **SplineGS**，2024 / CVPR 2025；*Robust Motion-Adaptive Spline for Real-Time Dynamic 3D Gaussians from Monocular Video* | CoTracker 轨迹和 UniDepth 初始化 Hermite 样条运动，再优化高斯、曲线与相机 | 补充材料明确将 motion tracking 展示与输入视频中的 2D 对应任务区分；不能把轨迹可视化当作 TAP 验证。“实时”指渲染。[论文](https://openaccess.thecvf.com/content/CVPR2025/papers/Park_SplineGS_Robust_Motion-Adaptive_Spline_for_Real-Time_Dynamic_3D_Gaussians_from_CVPR_2025_paper.pdf)、[补充 §A/§D](https://openaccess.thecvf.com/content/CVPR2025/supplemental/Park_SplineGS_Robust_Motion-Adaptive_CVPR_2025_supplemental.pdf) |
| **GS-DiT / D3D-PT**，CVPR 2025；*Advancing Video Generation with Dynamic 3D Gaussian Fields through Efficient Dense 3D Point Tracking* | D3D-PT 预测稠密 $(u,v,d)$ 与可见性；轨迹形成动态高斯场，渲染结果用于可控视频生成 | D3D-PT 的跟踪评测与 GS-DiT 的生成评测分属不同模块；TAPVid-3D 使用 minival。不能把 tracker 成绩归因于高斯重建，也不能把整个扩散生成管线叫一次前馈。[正式论文](https://openaccess.thecvf.com/content/CVPR2025/papers/Bian_GS-DiT_Advancing_Video_Generation_with_Dynamic_3D_Gaussian_Fields_through_CVPR_2025_paper.pdf)、[项目](https://wkbian.github.io/Projects/GS-DiT/) |
| **DreamScene4D**，NeurIPS 2024；*Dynamic Multi-Object Scene Generation from Monocular Videos* | 将单目多物体视频提升成动态高斯；项目展示将高斯轨迹投影得到 2D tracking | 属于生成式视频到 4D；轨迹展示说明表示可用于跟踪，生成补全的合理性不等于不可见真实运动的准确性。[项目与论文入口](https://dreamscene4d.github.io/) |
| **TrackGS**，2025 / AAAI 2026；*Optimizing COLMAP-Free 3D Gaussian Splatting with Global Track Constraints* | 静态多视图特征链构造 track Gaussians，用重投影 / 反投影约束联合优化相机和场景 | “track”是静态特征观测链，适合与前文 pose-free GS 对照；不是动态 TAP。[论文](https://arxiv.org/abs/2502.19800)、[AAAI 正式记录](https://ojs.aaai.org/index.php/AAAI/article/view/37851) |
| **ProDyG**，NeurIPS 2025；*Progressive Dynamic Scene Reconstruction via Gaussian Splatting from Monocular Videos* | 用提升到三维的像素轨迹初始化渐进运动骨架，结合 SLAM 和高斯重建 | 主要 tracking 表是相机 ATE；未核到通用 TAP 评测。不能将相机结果列入点跟踪排行榜。[论文](https://arxiv.org/html/2509.17864v1)、[官方代码](https://github.com/cs-vision/ProDyG) |

**另外两类建议保留为对照：**

- **几何 + tracking，但不用 GS 的方法。** [C4D: 4D Made from 3D through Dual Correspondences（ICCV 2025）](https://openaccess.thecvf.com/content/ICCV2025/html/Wang_C4D_4D_Made_from_3D_through_Dual_Correspondences_ICCV_2025_paper.html)结合深度、相机、点轨迹和优化，输出 pointmaps，不应列为高斯方法；[TAPIP3D（NeurIPS 2025）](https://tapip3d.github.io/)可作为持久三维几何跟踪的相邻基线。
- **动态 GS 的系统性分析。** [Monocular Dynamic Gaussian Splatting: Fast, Brittle, and Scene Complexity Rules](https://arxiv.org/html/2412.04457v2)研究表示、优化和场景复杂度；早期题名为 *Monocular Dynamic Gaussian Splatting is Fast and Brittle but Smooth Motion Helps*。它适合帮助理解重建失败原因，不能当作新的 TAP 方法。[初版记录](https://arxiv.org/abs/2412.04457v1)

**代码入口不等于实现已发布。** 截至本次核查，[DynMF](https://github.com/agelosk/dynmf)、[GS-DiT](https://github.com/wkbian/GS-DiT)和 [TrackGS](https://shidongbo97.github.io/TrackGS/)仍出现代码待发布说明或仅展示资料；本节不保证其已有可运行的完整算法。其他仓库也未在本次综述中实际安装运行。

### 12.6 从方法层面看：轨迹如何约束高斯，高斯又如何输出轨迹

以下公式用于解释共性，**不是宣称所有论文采用同一公式**。

#### 12.6.1 轨迹约束动态场景

设二维轨迹观测为 $\hat u_{q,t}$，模型中的对应三维位置为 $X_q(t)$，世界到相机的旋转和平移分别为 $R_{cw,t}$、$\mathbf t_{cw,t}$，则可用重投影约束：

$$
\mathcal L_{\mathrm{track}}
=\sum_{q,t}m_{q,t}\,
\rho\!\left(
\pi\!\left(K_t(R_{cw,t}X_q(t)+\mathbf t_{cw,t})\right)-\hat u_{q,t}
\right).
$$

这里 $m_{q,t}$ 表示有效性或置信度，$\rho$ 是鲁棒误差；深度、渲染、局部刚性等项提供补充约束。直观上，**图像损失要求“画得像”，轨迹损失要求“这个点应当移动到这里”。**

两者仍可能冲突：错误的二维轨迹会强迫三维形变配合它；错误的相机或深度又能产生看似正确的重投影。因此，轨迹提供了额外约束，但单靠二维吻合不能唯一确定三维运动。SoM 的运动基、MoSca 的骨架、SplineGS 的曲线，分别限制了允许的运动形式。

#### 12.6.2 查询点如何绑定到高斯

常见思路包括：

1. **单高斯及局部坐标。** 查询点在 $t_q$ 与某个高斯建立关联，保存相对偏移；后续跟随该高斯平移和旋转。对应 Dynamic 3D Gaussians 一类显式持久身份思路。
2. **查询帧的混合权重。** 根据查询像素在 $t_q$ 的渲染贡献，为一组高斯确定权重，再组合它们在目标时刻的位置。例如，简化写成

   $$
   X_q(t)=\sum_i \bar w_i(q,t_q)\mu_i(t),
   \qquad \sum_i\bar w_i(q,t_q)=1.
   $$

   这里强调的是保持查询关联；具体论文可能使用未归一化渲染、局部偏移或其他修正。
3. **运动骨架或形变映射。** 先将查询点关联到局部节点 / canonical 空间，再随运动场传播，而非直接把查询点等同于高斯中心。
4. **渲染位移或特征。** 例如 Video-GMAE 的位移场加锚点、C4G 的特征场匹配。此时高斯参与构建跟踪所需信息，最终输出器并不只是“读取某个中心”。

#### 12.6.3 为什么“同一个高斯”未必等于“同一个物理点”

- **高斯是有体积的渲染基元。** 其中心未必落在真实表面；一个大高斯可能覆盖多个纹理点。
- **混合会跨层。** 前景边缘的像素可能同时受前后两个深度层影响，位置加权平均可能落在空中。
- **增密 / 裁剪改变身份。** 分裂后的高斯应怎样继承旧轨迹，删除高斯后怎样保留查询点，不能仅靠数组索引解决。
- **可见性不等于 opacity。** 高斯自身不透明不代表目标点在某帧可见；还要考虑遮挡、深度排序及是否移出画面。
- **外观拟合有替代路径。** 优化器可能通过改颜色、透明度或形状降低渲染误差，而没有恢复真实运动。

这些因素解释了为什么 NVS 与 TAP 应分别评价，也说明“持久 ID + 可渲染”仍有研究空间。

### 12.7 怎样公平比较：避免把不同输入与指标放进一张排行榜

#### 12.7.1 先记录输入和计算条件

| 必须记录的字段 | 需要区分的设置 |
|---|---|
| 相机数量与标定 | 同步多相机 / 单目；给定 / 预测内参；给定 / 优化外参 |
| 深度来源 | 传感器 / 单目预测 / 多视图估计；是否做真值尺度对齐 |
| 轨迹先验 | 无；成对光流；TAPIR / CoTracker 等长轨迹；具体模型版本 |
| 使用先验的阶段 | 仅训练监督，还是测试视频也需运行教师 tracker |
| 时间可用性 | 整段视频；双向窗口；允许未来帧的数量；严格因果 |
| 场景适配 | 一次预测；每帧更新；全视频优化；是否回放历史 |
| 查询与输出 | 首帧或任意帧查询；2D / 相机系 3D / 世界系 3D；可见性 |
| 资源 | 先验提取、重建 / 更新、查询、渲染四阶段的时间与显存 |

**给定相机的 MoVieS、单目估计相机的 DynOMo、多相机的 Dynamic 3D Gaussians、LiDAR 辅助设置的 MoSca，不能只按一个平均误差得出无条件优劣。**

#### 12.7.2 指标分别回答什么问题

- **2D TAP：** AJ 综合位置和可见性；$\delta_{\mathrm{avg}}$ 反映可见点落在距离阈值内的比例；OA 衡量遮挡 / 可见性判断。必须保留数据集、分辨率、查询协议、序列范围及评测脚本版本。[TAP-Vid 论文](https://arxiv.org/abs/2211.03726)、[官方评测实现](https://github.com/google-deepmind/tapnet)
- **3D tracking：** 位置误差、阈值精度、AJ3D 等需要说明坐标系及尺度处理。TAPVid-3D 的标准轨迹位于**各时刻相机坐标系**，单位为米；世界系预测应转换到同一坐标定义。[官方数据格式](https://github.com/google-deepmind/tapnet/tree/main/tapnet/tapvid3d#data-format)
- **协议不能合并：** TAPVid-3D 的全局尺度对齐与逐轨迹对齐并非同一条件；minival 与完整集也不同。DyCheck PCK-T、iPhone EPE 与 TAPVid-3D AJ3D不能直接互换。[TAPVid-3D 论文](https://arxiv.org/html/2407.05921v2)、[DyCheck 对应关系接口](https://github.com/KAIR-BAIR/dycheck#2-correspondence-metrics)
- **渲染与相机：** PSNR / SSIM / LPIPS 回答图像质量，ATE / RPE 回答相机运动；它们可以作为附加指标，不能代替物质点轨迹精度。

#### 12.7.3 本方向尤其需要注意的评测陷阱

1. **伪真值来源。** TAPVid-3D 的 Panoptic Studio 子集使用预训练 Dynamic 3D Gaussians 重建生成轨迹伪真值：把查询关联到高斯并跟随其运动，可见性来自渲染深度。它不是独立传感器逐点直接测得的三维真值。[原论文 §3.3](https://arxiv.org/html/2407.05921v2#S3.SS3)

   **综述判断：** 评价高斯跟踪器时，应同时看其他标注来源的数据，避免单一表示生成的伪真值成为唯一依据。
2. **拟合教师不等于独立验证。** 使用 TAPIR / CoTracker 预测作为测试时优化输入是允许的方法设计，但应报告原始教师结果，以及优化输出相对独立真值的提升；教师轨迹一致性只能说明拟合程度。
3. **oracle 与正常查询必须分开。** 不能用真值在多个候选高斯中挑选最优轨迹后，再当作普通查询算法的成绩。DynOMo⋆ 是需要明确标注的例子。
4. **查询采样与计分长度都影响任务。** Video-GMAE 的代码提示了这种核查的必要性；“用了 TAP-Vid 指标”并不自动意味着完整长视频、完全一致的评测协议。
5. **长遮挡与新进入内容要单独看。** 平均指标之外，建议报告遮挡前后重识别、长时间离开画面后返回、细小物体及大相机运动的结果。
6. **速度包含整个系统。** tracker、深度、分割和相机预处理都计入端到端延迟；训练后的渲染 FPS 不代表重建或跟踪 FPS。

### 12.8 对前馈 4DGS、SLAM 和研究选题的启发

以下为综合研究判断，**不是已完成新颖性论证的选题，也不是保证优于已有方法的结论**。

#### 12.8.1 值得优先研究的五个问题

| 问题 | 可探索的做法 | 验证时最关键的证据 |
|---|---|---|
| 高斯 ID 与物理点 ID 不一致 | 分离用于渲染的高斯与用于身份保持的锚点；设计分裂 / 合并的继承关系 | 长遮挡、增密和新物体进入后，轨迹是否仍连续正确 |
| 前馈结果跨窗口漂移 | 用前馈模型初始化动态地图，再以历史锚点约束局部更新 | 统一世界坐标中的累计误差；窗口交界和回环后的点身份 |
| 教师轨迹有误差 | 显式估计置信度，联合深度、几何与多视图可见性筛选约束 | 独立真值下优于原始 tracker，而非只降低教师拟合损失 |
| 重建与跟踪目标存在取舍 | 同时监督渲染、表面几何、轨迹与可见性，控制共享和独立参数 | 同条件下同时报告 NVS、TAP 与几何；展示取舍曲线 |
| 在线状态随视频增长 | 压缩运动基 / 骨架，保留可追溯查询关联，限制历史回放 | 状态大小、最坏更新延迟、未来帧依赖与长期身份误差 |

#### 12.8.2 一个具体、可检验的研究起点

**建议：以“前馈动态高斯初始化 + 持久点锚点 + 有界窗口校正”为研究假设。**

- **初始化：** 参考 MoVieS 的像素运动预测，或 C4G 的紧凑动态表示；明确相机是否已知。
- **关联：** 为用户查询点维护独立锚点及局部坐标，使渲染高斯增密 / 裁剪不会直接删除轨迹身份。
- **更新：** 只利用声明范围内的帧和先验更新几何、相机与运动；若回放历史，应计入资源并说明延迟。
- **比较：** 与相同输入条件的直接 tracker、单纯高斯传播、带锚点的联合更新做对照；主结果使用独立轨迹真值。
- **消融：** 比较最近高斯、查询帧混合权重、显式锚点三种查询方式；检查提升来自身份关联还是更多计算 / 更强先验。

这条建议连接了前文的前馈重建与本节的跟踪问题。它的难点不是再加一个轨迹损失，而是同时处理**坐标一致性、表面身份、遮挡和表示更新**。

### 12.9 阅读顺序与可复用的论文记录模板

#### 12.9.1 按问题选择阅读路线

| 主要兴趣 | 建议顺序 |
|---|---|
| 理解 GS 为什么能做点跟踪 | Dynamic 3D Gaussians → DynOMo → Shape of Motion |
| 用现成 TAP 改善动态重建 | Shape of Motion → MoSca → SplineGS / 4D-Fly → TrackerSplat / MOSAIC-GS |
| 前馈 4DGS + tracking | MoVieS → C4G → Video-GMAE；三者分别看联合三维预测、紧凑表示、自监督对应学习 |
| 在线与长视频 | DynOMo → 4D-Fly → MotionScale；逐一检查先验和历史优化的因果性 |
| 视频生成与运动控制 | D3D-PT / GS-DiT → DreamScene4D |
| SLAM / 未知相机 | DynOMo → MoSca；以 ProDyG、TrackGS 为相邻任务对照 |

如果只精读 **6 篇**：**Dynamic 3D Gaussians、Shape of Motion、MoSca、DynOMo、MoVieS、Video-GMAE**。之后按对紧凑表示或大规模优化的兴趣补 C4G、MotionScale；这只是覆盖不同技术思路的阅读建议，不是效果排名。

#### 12.9.2 后续增补每篇论文时记录这些字段

- **论文信息：** 完整题名、首次公开日期、正式发表、所读版本、论文 / 项目 / 代码链接。
- **任务：** NVS、TAP2D、TAP3D、相机 tracking、生成；分别列出实际验证的输出。
- **输入：** RGB / RGB-D、相机数量、内外参、深度、掩码、外部 tracker 与来源。
- **表示：** 高斯组织方式、运动模型、时间范围、增密 / 裁剪及身份继承。
- **查询：** 任意时刻是否可查询，像素怎样关联三维点，可见性怎样计算。
- **计算：** 前馈 / 场景优化 / 混合；因果性、前置模型、历史回放与完整耗时。
- **证据：** 数据划分、真值来源、尺度与坐标协议、跟踪指标、NVS 指标、失败案例。
- **判断：** 相比输入 tracker 或已有动态表示，实际增加了什么能力；哪些结论仍缺实验。

**本节总结：** 3DGS / 4DGS 与 TAP 的结合，已经从“动态高斯附带轨迹”发展到“利用轨迹重建可渲染场景”，并进一步走向“跨场景学习几何、运动与点对应”。判断贡献时应沿着**输入轨迹 → 动态表示 → 查询关联 → 输出轨迹 → 独立评测**逐步检查；对于前馈与在线系统，还要把相机条件、未来信息和完整计算成本写清。

---

**资料说明：** 本文链接以论文与作者原始资料为依据；未核实正式发表的工作保留预印本标注。“官方代码”表示找到了作者实现入口，不保证已验证所有权重、训练流程和环境均可复现。少数条目的发表信息来自原论文 Comments 或作者项目/代码页，已在条目中注明。后续更新时应重新核查版本、实验协议及资源状态。
