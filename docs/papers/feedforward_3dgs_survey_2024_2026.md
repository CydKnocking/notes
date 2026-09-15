# 近两年 3D Gaussian Splatting 研究综述：以前馈式重建为主线

> 检索截止：**2026-09-15**。主线覆盖 **2024 年下半年至 2026 年 9 月**，并补入理解该方向必需的 2024 年奠基论文；其中少数论文的首次预印本在 2023 年末。  
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

**阅读导航：** 第 1 节统一概念；第 2 节快速了解非前馈背景；第 3–8 节按技术路线梳理前馈工作；第 9–11 节讨论比较方法、研究问题和阅读顺序。

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

---

**资料说明：** 本文链接以论文与作者原始资料为依据；未核实正式发表的工作保留预印本标注。“官方代码”表示找到了作者实现入口，不保证已验证所有权重、训练流程和环境均可复现。少数条目的发表信息来自原论文 Comments 或作者项目/代码页，已在条目中注明。后续更新时应重新核查版本、实验协议及资源状态。
