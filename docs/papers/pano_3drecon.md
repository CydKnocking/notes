本文档为全景相机做三维重建/四维重建的相关论文整理。  
范围：约 2023–2026，CVPR / ICCV / ECCV / AAAI / NeurIPS / ICLR / ICRA / 3DV / TPAMI / ICML / IROS（及紧密相关的 RA-L）+ **arXiv 2025–2026**。  
重点：动态场景 / 4D；其次为静态新视角合成、深度/立体、SLAM、feed-forward 几何基础模型。

> **总览判断**  
> - **真·全景动态重建（从真实 360 视频重建可漫游 4D）仍极少**：观测驱动代表仍是 **OmniLocalRF (CVPR’24)**（去动态）；生成式有 **4K4DGen / HoloTime / TiP4GEN**；**4DGS360 (arXiv’26)** 是透视视频上的“360° 物体环视 4D”，**输入不是 ERP 全景相机**。  
> - **2026 年主线转向 feed-forward 全景几何**：PanoVGGT / VGGT-360 / Depth Any Panoramas / CylinderSplat / ODGS-SLAM / PFGS360；数据侧 **Holo360D (ECCV’26)**、PanoCity、AirSim360、ORBIT 明显补强。  
> - 透视域 4D（4D-GS、MonST3R 等）很热，但多数**未原生支持 ERP/鱼眼**；全景 4D 多走“生成视频 + lift”而非观测驱动重建。


## 一、动态场景 / 四维（优先）

### 1.1 观测驱动：全景视频 → 场景重建（含动态处理）

- [OmniLocalRF](https://openaccess.thecvf.com/content/CVPR2024/html/Choi_OmniLocalRF_Omnidirectional_Local_Radiance_Fields_from_Dynamic_Videos_CVPR_2024_paper.html) — **CVPR 2024**  
  输入 casual 360° 动态视频；LocalRF + 全景双向射线优化；多分辨率 neural feature planes 预测 motion mask，**去除并 inpaint 动态物体（含拍摄者）**，输出静态可漫游场景；可联合估 pose。长视频、大视角遮挡是核心难点。  
  [code](https://github.com/KAIST-VCLAB/OmniLocalRF)

- [Scene4U](https://openaccess.thecvf.com/content/CVPR2025/html/Huang_Scene4U_Hierarchical_Layered_3D_Scene_Reconstruction_from_Single_Panoramic_Image_CVPR_2025_paper.html) — **CVPR 2025**  
  **单张**全景 → 开放词表分割 + LLM 分层 → diffusion 分层修复遮挡 → 分层 3DGS。强调去掉前景/动态层、全局纹理一致、可自由漫游。偏“去动态后的沉浸式静态场景”，非时空 4D 跟踪。

### 1.2 生成式：全景 → 4D（动画 + lifting，非真实动态观测重建）

- [4K4DGen](https://proceedings.iclr.cc/paper_files/paper/2025/file/fa41e9d5dfcc97cd9eed99f001aa28e5-Paper-Conference.pdf) — **ICLR 2025**  
  单张全景 → Panoramic Denoiser 生成 360° 动态视频 → Dynamic Panoramic Lifting 到 4D Gaussians；首次宣称 **4K（4096×2048）全景 4D**。任务是 **Panorama-to-4D generation**。

- [HoloTime](https://zhouhyocean.github.io/holotime/) — arXiv 2025（跟进类）  
  360World 数据集 + Panoramic Animator（图生视频）+ 时空深度对齐 + 4D-GS。同属生成式全景 4D。

- [TiP4GEN](https://arxiv.org/abs/2508.12415) — arXiv 2025  
  **Text → 动态全景 4D**：双分支（全景+透视）视频生成 + 度量深度对齐的 3DGS 重建。

### 1.3 环视/全向动态（注意：多为透视输入，非 ERP 相机）

- [4DGS360](https://jaewon040.github.io/4dgs360/) — arXiv 2026（`2603.21618`）  
  单目透视视频 → **物体完整 360° 环视 4D GS**；AnchorTAP3D（2D track 锚定 3D 轨迹）缓解遮挡区深度歧义；新基准 **iPhone360**（测试视角与训练差可达 135°）。**不是全景相机输入**，但对“大视角动态几何”有参考价值。

### 1.4 空白与可做方向（结合本仓库兴趣）

| 方向 | 现状 |
|------|------|
| 真实 360 视频上的 dense 4D + correspondence | 几乎空；透视域有 St4RTrack / CUT3R / Flow4R |
| 全景 feed-forward 动态几何（类 MonST3R/POMATO 的 ERP 版） | **2026 仍未见顶会成熟方案**；PanoVGGT / CylinderSplat 偏静态 |
| 驾驶/室内全景动态 + metric scale | Helvipad、Holo360D、PanoCity 补数据，但动态标注仍弱 |

相关透视动态工作见 `4drecon_tracking.md`，可迁移球形 PE / ERP 光栅化。


## 〇、2026 会议 + 2025–2026 arXiv（补遗，优先读）

### 0.1 CVPR 2026（全景 3D/深度/SLAM 相关）

- [PanoVGGT](https://openaccess.thecvf.com/content/CVPR2026/html/Guo_PanoVGGT_Feed-Forward_3D_Reconstruction_from_Panoramic_Imagery_CVPR_2026_paper.html) — **CVPR 2026**  
  无序多张 ERP → 单次前向联合预测 pose / depth / 点云；球感 PE + SO(3) 三轴旋转增强 + stochastic anchoring；发布 **PanoCity**。见下文第五节详细笔记。

- [VGGT-360](https://openaccess.thecvf.com/content/CVPR2026/html/Yuan_VGGT-360_Geometry-Consistent_Zero-Shot_Panoramic_Depth_Estimation_CVPR_2026_paper.html) — **CVPR 2026**  
  **训练无关**全景深度：不确定度引导自适应切透视片 → VGGT 多视图 3D → correlation-weighted 校正 → 反投影回 ERP。见第五节。

- [Depth Any Panoramas (DAP)](https://openaccess.thecvf.com/content/CVPR2026/html/Lin_Depth_Any_Panoramas_A_Foundation_Model_for_Panoramic_Depth_Estimation_CVPR_2026_paper.html) — **CVPR 2026**  
  全景 **metric depth 基础模型**；DINOv3-Large；range mask head + 几何一致性优化；大规模伪标签管线；评测 Stanford2D3D / Matterport3D / Deep360 等。Insta360 Research。  
  [project](https://insta360-research-team.github.io/DAP_website/)

- [PFGS360](https://openaccess.thecvf.com/content/CVPR2026/html/Zhuang_Pose-Free_Omnidirectional_Gaussian_Splatting_for_360-Degree_Videos_with_Consistent_Depth_CVPR_2026_paper.html) — **CVPR 2026**  
  **无 pose** 全景视频 → omnidirectional 3DGS；球一致 2D–3D 对应估位姿 + depth-inlier densification。  
  [code](https://github.com/zcq15/PFGS360)

- [ODGS-SLAM](https://openaccess.thecvf.com/content/CVPR2026/papers/Spiss_ODGS-SLAM_Omnidirectional_Gaussian_Splatting_SLAM_CVPR_2026_paper.pdf) — **CVPR 2026**  
  **首个**以 omnidirectional 3DGS 统一跟踪+建图的全景 SLAM（RGB/RGBD）；ERP 投影闭式梯度；图分析删关键帧降内存；自建室内外评测集。  
  [code](https://github.com/odgs-slam/odgs-slam)

- [ORBIT](https://openaccess.thecvf.com/content/CVPR2026/html/Sabour_ORBIT_Benchmarking_SfM_in_the_Wild_with_360deg_Video_CVPR_2026_paper.html) — **CVPR 2026**  
  野外 **360° 视频 SfM** 基准（Google/相关团队）；评测 wild 条件下结构恢复。

- [Pano3DComposer](https://openaccess.thecvf.com/content/CVPR2026/html/Qiu_Pano3DComposer_Feed-Forward_Compositional_3D_Scene_Generation_from_Single_Panoramic_Image_CVPR_2026_paper.html) — **CVPR 2026**  
  单张全景 → 组合式 3D 场景生成；Alignment-VGGT 预测物体→世界变换；~20s/场景。

- [Pantheon360](https://koi953215.github.io/pantheon360_page/) — **CVPR 2026**  
  稀疏 360 输入 → 显式 3D Cache（π3/VGGT）条件化 360 视频扩散，做数字孪生/可控轨迹；偏生成，几何 scaffold 可参考。

- [AirSim360](https://openaccess.thecvf.com/content/CVPR2026/html/Ge_AirSim360_A_Panoramic_Simulation_Platform_within_Drone_View_CVPR_2026_paper.html) — **CVPR 2026**  
  无人机视角全景仿真平台（深度/几何标注友好，常与 DAP 等配合）。

- [Pano360](https://openaccess.thecvf.com/content/CVPR2026/papers/Zhu_Pano360_Perspective_to_Panoramic_Vision_with_Geometric_Consistency_CVPR_2026_paper.pdf) — **CVPR 2026**  
  多张透视 → 几何一致全景拼接；VGGT 式 3D 对齐；新真实大规模全景数据集。

### 0.2 ECCV / ICLR / IROS 2025–2026

- [Holo360D](https://arxiv.org/abs/2604.22482) — **ECCV 2026**  
  真实大规模连续轨迹全景 3D 数据集：109,495 张全景 + LiDAR mesh/点云/深度/位姿；室内外；用于微调 Pi3 等 feed-forward。  
  [HF](https://huggingface.co/datasets/ouou123/Holo360D) · [code](https://github.com/Jou719/Holo360D)

- [CylinderSplat](https://arxiv.org/abs/2603.05882) — **ICLR 2026**  
  圆柱 Triplane + 双分支（像素重建 / 体积补全）feed-forward 全景 3DGS；可变视角数（单张→多张）；相对 Splatter-360 / PanSplat 更强遮挡补全。  
  [code](https://github.com/wangqww/CylinderSplat)

- [DFI-OmniStereo](https://vita-epfl.github.io/DFI-OmniStereo-website/) — **IROS 2025**  
  预训练相对深度基础模型注入迭代式 OSM；Helvipad 上 disparity MAE 约降 16%。

### 0.3 arXiv 2025–2026（尚未确认会议或预印）

| 工作 | 时间 | 要点 |
|------|------|------|
| [TPGS / Transition Plane](https://arxiv.org/abs/2504.09062) | 2025.04 | cubemap 面间加 Transition Plane；intra→inter face 优化；单张/多张全景 3DGS |
| [360-GeoGS](https://arxiv.org/abs/2601.02102) | 2026.01 | feed-forward 360 3DGS + Depth-Normal 正则，强化几何一致性 |
| [Spherical-GOF](https://arxiv.org/abs/2603.08503) | 2026.03 | 单位球上 ray-Gaussian（GOF）；深度重投影误差大降，利于 mesh |
| [Underwater360](https://arxiv.org/abs/2605.26447) | 2026.05 | 水下全景物理介质建模 + 球空间 omni-GS；新水下 360 基准 |
| [FastPano3D](https://arxiv.org/abs/2606.30352) | 2026.06 | 单张室内全景秒级 feed-forward GS；宣称相对 Pano2Room ~156× |
| [HALO-SLAM](https://arxiv.org/abs/2608.00925) | 2026.08 | 冻结全景几何基础模型读重力 + attention 回环；多真实全景基准 ATE 优 |
| [PanoWorld](https://arxiv.org/html/2605.17916) | 2026.05 | 整屋 VR tour：楼层平面 + 全景 LRM → 渐进 3DGS 缓存（生成向） |

> **ICCV / AAAI / NeurIPS / ICML / ICRA / 3DV 2026**：截至整理时，除 CVPR’26 / ECCV’26 / ICLR’26 / IROS’25 外，**其余 2026 届次上“全景相机原生 3D/4D”公开清单仍稀疏**；ICCV’25 已有 Seam360GS、MDP-Omni（见后文）；后续可继续扫 openaccess / OpenReview。


## 二、静态 / 慢动场景三维重建与新视角合成

### 2.1 NeRF 系（全景 / 球坐标）

- [EgoNeRF](https://www.changwoon.info/publications/EgoNeRF)（Balanced Spherical Grid for Egocentric View Synthesis）— **CVPR 2023**  
  短时 egocentric 360 视频；平衡球网格 + 指数径向划分 + 无穷远环境图；适配无界第一人称场景。数据集：OmniBlender / Ricoh360。

- [PanoGRF](https://thucz.github.io/PanoGRF/) — **NeurIPS 2023**  
  **宽基线**全景可泛化球形 radiance field；球投影聚合几何/外观；360° 单目深度先验引导 MVS cost volume。对比 OmniSyn / IBRNet / NeuRay。

- [Pano-NeRF](https://ojs.aaai.org/index.php/AAAI/article/view/28185) — **AAAI 2024**  
  稀疏 LDR 全景 → irradiance fields：几何恢复 + HDR 新视角；副产品：空间变化光照估计。

- [PERF](https://perf-project.github.io/) — **TPAMI 2024**  
  **单张**全景 → collaborative RGBD inpainting + progressive inpainting-and-erasing → panoramic NeRF，支持复杂场景 3D roaming。

- [360FusionNeRF](https://doi.org/10.1109/iros55552.2023.10341346) — **IROS 2023**  
  单张 360 RGB-D；几何监督 + CLIP 语义一致性；Structured3D / Matterport3D / Replica360。

- [OmniSDF](https://openaccess.thecvf.com/content/CVPR2024/html/Kim_OmniSDF_Scene_Reconstruction_using_Omnidirectional_Signed_Distance_Functions_and_Adaptive_Binoctrees_CVPR_2024_paper.html) — **CVPR 2024**  
  小圆轨迹全景视频 → 球 binoctree 上的 SDF；小基线、大深度范围；自适应细分。

### 2.2 3D Gaussian Splatting 系（全景光栅化 / 可泛化）

- [ODGS](https://arxiv.org/abs/2410.20686) — **NeurIPS 2024**  
  全景专用光栅化：高斯投到单位球切平面再映到 ERP；CUDA；相对 NeRF 约 100× 加速。多数据集（OmniBlender、Ricoh360、OmniPhotos、360Roam 等）。

- [SC-OmniGS](https://proceedings.iclr.cc/paper_files/paper/2025/file/a9cae5b74cfc8f71c39a4e646db819c2-Paper-Conference.pdf) — **ICLR 2025**  
  **自标定**全景 3DGS：联合优化 Gaussian、球相机外参、可微畸变模型；宽基线 / 无 pose prior 可用；利于下游全景 GS-SLAM。

- [OmniGS](https://liquorleaf.github.io/research/OmniGS/) — WACV 2025（相关）  
  球相机模型导数 → 直接 ERP 可微 splatting，无需 cubemap / 切平面近似。

- [360-GS](https://github.com/LeoDarcy/360GS) — **3DV 2025**  
  Layout-guided 室内漫游全景 GS；依赖房间布局先验，室外泛化受限。

- [Splatter-360](https://3d-aigc.github.io/Splatter-360/) — **CVPR 2025**  
  宽基线全景 **可泛化** 3DGS；球域 cost volume（spherical sweep）+ bi-projection（ERP+cubemap）encoder；HM3D / Replica。强于 PanoGRF / MVSplat 等。

- [OmniSplat](https://openaccess.thecvf.com/content/CVPR2025/html/Lee_OmniSplat_Taming_Feed-Forward_3D_Gaussian_Splatting_for_Omnidirectional_Images_with_CVPR_2025_paper.html) — **CVPR 2025**  
  **训练无关** feed-forward：Yin-Yang 网格拆球，复用透视域 feed-forward 3DGS prior；Yin-Yang rasterizer 减轻极区伪影。

- [PanSplat](https://openaccess.thecvf.com/content/CVPR2025/html/Zhang_PanSplat_4K_Panorama_Synthesis_with_Feed-Forward_Gaussian_Splatting_CVPR_2025_paper.html) — **CVPR 2025**  
  宽基线全景 → feed-forward GS，目标 **4K** 新视角；解决极区高斯冗余与高分显存。

- [Seam360GS](https://openaccess.thecvf.com/content/ICCV2025/html/Shin_Seam360GS_Seamless_360deg_Gaussian_Splatting_from_Real-World_Omnidirectional_Images_ICCV_2025_paper.html) — **ICCV 2025**  
  真实双鱼眼：联合标定镜头间隙与角畸变 + 3DGS，无缝 360° 渲染。

- [Omni3D](https://omni3d-neurips.github.io) — **NeurIPS 2025**  
  单张图 omnidirectional 重建：diffusion 新视角 + MASt3R 几何先验，**Pose-View Optimization** 迭代校正，再 3DGS。偏“全向渲染能力”，输入未必是 ERP。


## 三、深度 / 立体 / 几何感知

### 3.1 单目 360° 深度

- [HRDFuse](https://vlis2022.github.io/HRDFuse/) — **CVPR 2023**  
  ERP 全局上下文 + 切平面局部结构；SFA + 协同深度分布分类。

### 3.2 多鱼眼 / Omnidirectional Stereo Matching (OSM)

- [OmniVidar](https://openaccess.thecvf.com/content/CVPR2023/html/Xie_OmniVidar_Omnidirectional_Depth_Estimation_From_Multi-Fisheye_Images_CVPR_2023_paper.html) — **CVPR 2023**  
  四鱼眼 → 极线校正成双目问题；无 3D CNN，高分辨率更快。

- [RomniStereo](https://arxiv.org/abs/2401.04345) — **RA-L 2024**（ICRA 相关轨）  
  RAFT 式迭代更新移植到 OSM；opposite adaptive weighting + spherical sweeping；四正交鱼眼 → 虚拟参考视点全景深度。

- [MDP-Omni](https://openaccess.thecvf.com/content/ICCV2025/html/Son_MDP-Omni_Parameter-free_Multimodal_Depth_Prior-based_Sampling_for_Omnidirectional_Stereo_Matching_ICCV_2025_paper.html) — **ICCV 2025**  
  无参多峰深度先验采样，改善边界过平滑；方位角多视角 volume fusion。

- [DFI-OmniStereo](https://vita-epfl.github.io/DFI-OmniStereo-website/) — **IROS 2025**  
  相对深度基础模型特征 → 迭代 OSM；Helvipad SOTA。

- [Helvipad](https://github.com/vita-epfl/Helvipad) — **CVPR 2025**  
  真实 OSM 数据集：上下双 360° + LiDAR，约 40K 帧，室内外拥挤场景；配套 360-IGEV 等基准。

### 3.3 深度 + 新视角联合

- [MSI-NeRF](https://arxiv.org/abs/2403.10840) — WACV 2025（相关）  
  四鱼眼 → multi-sphere image cost volume + NeRF；同时做 omni-depth 与 6DoF 合成；可用已有全景深度集训练。


## 四、SLAM / VO / 稠密建图（全景）

- [Omnidirectional Dense SLAM for Back-to-back Fisheye Cameras](https://doi.org/10.1109/icra57147.2024.10610351) — **ICRA 2024**  
  背靠背双鱼眼 VI-SLAM；轻量全景深度补全（multi-basis）+ 传统优化提高全局深度一致性；可跑移动端 demo。

- [360ORB-SLAM](https://arxiv.org/abs/2401.10560) — 2024（arxiv / 期刊类，常被全景 SLAM 引用）  
  全景三角化 + 深度补全网络 → 稠密深度进 ORB-SLAM 管线，缓解尺度漂移；自建驾驶全景数据。

- LF-VIO / LF-VISLAM、PAL-SLAM2 等（大 FoV / 负半平面特征）— 偏机器人期刊（如 T-ASE），做全景前端时可参考。

- 近期 arXiv：[HALO-SLAM](https://arxiv.org/abs/2608.00925)（冻结全景几何基础模型做重力/回环）— 未计入正式顶会列表，可跟踪。


## 五、Feed-forward 几何基础模型（全景版）

- [PanoVGGT](https://arxiv.org/abs/2603.17571) — **CVPR 2026**
  
  全景相机版本 VGGT，上海科大。静态场景，离线。

  构造了新的数据集 PanoCity: 超过 120000 张带位姿和深度标注的全景图。虚拟数据集、室外场景、主要静态场景、不同天气条件。

  方法：

  1. DINOv2 编码。和 VGGT 类似的交替注意力模块。

  2. 从标准的 2D 网格编码改为球感位置编码 (Spherical-aware PE)

  3. 数据增强改用了 SO(3) 旋转增强，并随机定 target frame（stochastic anchoring）。
  
  8 张 A100 训练 10 天。用的数据集：PanoCity、Matterport3D、Stanford2D3D 和 Structured3D。  
  [code](https://github.com/YijingGuo-June/PanoVGGT) · [weights](https://huggingface.co/YijingGuo/PanoVGGT)

- [VGGT-360](https://arxiv.org/abs/2603.18943) — **CVPR 2026**
  
  **训练无关**零样本全景深度：不确定度引导切透视片 → VGGT 多视图重建 → structure-saliency attention → correlation-weighted 3D 校正 → 全景反投影。  
  [code](https://github.com/Yuanjiayii/VGGT-360)

- [Depth Any Panoramas](https://insta360-research-team.github.io/DAP_website/) — **CVPR 2026**  
  监督式全景 metric depth 基础模型（与 VGGT-360 路线互补：训大模型 vs 训无关）。


## 六、按会议速查（2023–2026，不完全表）

| 会议 | 代表工作 |
|------|----------|
| **CVPR’23** | EgoNeRF；HRDFuse；OmniVidar |
| **CVPR’24** | **OmniLocalRF（动态）**；OmniSDF |
| **CVPR’25** | Scene4U；Splatter-360；OmniSplat；PanSplat；Helvipad |
| **CVPR’26** | **PanoVGGT；VGGT-360；DAP；PFGS360；ODGS-SLAM；ORBIT；Pano3DComposer；Pantheon360；AirSim360** |
| **ICCV’25** | Seam360GS；MDP-Omni |
| **ECCV’26** | **Holo360D（数据集+基准）** |
| **ECCV’24–25** | 核心全景 3D/4D 仍偏少 |
| **NeurIPS’23** | PanoGRF |
| **NeurIPS’24** | ODGS |
| **NeurIPS’25** | Omni3D |
| **ICLR’25** | SC-OmniGS；**4K4DGen（全景 4D 生成）** |
| **ICLR’26** | **CylinderSplat** |
| **AAAI’24** | Pano-NeRF |
| **TPAMI’24** | PERF |
| **ICRA’24** | Omnidirectional Dense SLAM（双鱼眼） |
| **IROS’23** | 360FusionNeRF |
| **IROS’25** | **DFI-OmniStereo** |
| **3DV’25** | 360-GS |
| **RA-L’24** | RomniStereo |
| **ICML** | 近三年几乎未见“全景相机原生 3D/4D”主力论文 |
| **arXiv’25–26** | TPGS；360-GeoGS；Spherical-GOF；4DGS360；Underwater360；FastPano3D；HALO-SLAM；TiP4GEN；HoloTime |

> 说明：AAAI / NeurIPS / ICML / ICRA / 3DV **2026** 届次上，公开可确认的“全景相机原生 3D/4D”仍少；持续扫 OpenReview / openaccess。


## 七、全景（ERP）数据集整理

> 范围：近几年常用 / 新发布的 **ERP 全景**数据集（含“鱼眼→ERP 参考全景”的 OSM 数据）。  
> 维度：**静态/动态**、**合成/真实**、**深度真值**、**相机位姿**。  
> 符号：✓ 有官方/可靠 GT；△ 部分/弱（仅位置、仅立体外参、SfM 伪 GT、稀疏投影等）；✗ 无或未发布。  
> **动态**分两类：① **相机运动**（连续轨迹 VO/SLAM）；② **场景动态**（行人/车/活动物体）。二者可同时存在。

### 7.0 优先：动态场景 + 相机轨迹位姿（新补，2026-08）

> 「场景动态 + 真值轨迹位姿 + dense depth」的**真实** ERP 数据仍然极稀缺。多数是：合成真值全 / 真实仅 SfM 伪位姿 / 有深度但无轨迹 / 有轨迹但场景偏静。

| 数据集 | 相机运动 | 场景动态 | 合成/真实 | 深度 GT | 轨迹位姿 | 规模/要点 | 链接 |
|--------|----------|----------|-----------|---------|----------|-----------|------|
| **pano_point_odyssey** | ✓ | ✓ 物体/人 | 合成 | ✓ | ✓ | 本仓库；PointOdyssey 管线全景版 | `research_diary` |
| **TartanAir V2（Panorama）** | ✓ 挑战轨 | △ 环境可动 | 合成 | ✓ | ✓ 精确 | 可渲染 ERP+depth+pose；COLMAP 有 5k 全景 SfM 子集 | [tartanair.org](https://tartanair.org/) · [SfM bench](https://github.com/colmap/colmap/releases/tag/datasets-tartanair-v2-v1) |
| **360VO（合成）** | ✓ | △ 城市场景 | 合成 | △ 可渲染 | ✓ dense | ICRA’22；10 序列×~2k 帧；1920×960；人/车/UAV 运动风格 | [page](https://huajianup.github.io/research/360VO/) |
| **Omni360-Human**（AirSim360） | ✓ | ✓ 行人 NPC | 合成 | ✓（平台可出） | ✓ 相机 6-DoF | ~10 万帧；行人 3D keypoints；CVPR’26 | [AirSim360](https://insta360-research-team.github.io/AirSim360-website/) |
| **OmniHorizon** | ✓ 路径 | ✓ 行人/车/光照 | 合成 | ✓ depth+normal | △ 路径渲染位姿 | 2.4 万户外 top-bottom 立体 ERP | [site](https://omnihorizon.github.io/) |
| **H-OmniStereo** | ✓ | ✓ | 合成 | ✓（宣称） | △ rig/轨迹 | 双全景；**暂未开源** | [GitHub](https://github.com/JIANG-CX/H-OmniStereo) |
| **OmniLocalRF-Synth** | ✓ | ✓ 漂浮动态物 | 合成 | ✗/弱 | ✓（评 ATE） | 3 条合成 360 视频；配合方法估位姿 | [OmniLocalRF](https://github.com/KAIST-VCLAB/OmniLocalRF) |
| **360DVO Dataset** | ✓ | ✓ Hard 子集含遮挡/拥挤 | 真实 | ✗ | △ Metashape **伪 GT** | RA-L’26；20 序列×~1k；3840×1920；Easy/Hard | [360dvo](https://360dvo.hkustvgd.com/) |
| **Helvipad** | ✓ 视频序列 | ✓ 人群/交通 | 真实 | ✓ LiDAR→ERP | △ **立体外参✓**，绝对轨迹弱/未作主 GT | ~4 万帧；上下双 Theta | [site](https://vita-epfl.github.io/Helvipad/) |
| **PanoHK360** | ✓ 驾驶连续轨 | △ 城市场景 | 真实 | ✓ LiDAR | ✓ 6-DoF | 8K ERP；港城；Ladybug+LiDAR | [HF](https://huggingface.co/datasets/adadai3132/PanoHK360) |
| **OmniLocalRF-Real** | ✓ casual | ✓ 行人/拍摄者 | 真实 | ✗ | ✗（方法自估） | 6 户外 Insta360 场景；无官方轨迹 GT | 同上 OmniLocalRF |
| **360+x** | ✗/弱（多固定机位） | ✓ 活动 | 真实 | ✗ | ✗ | 动作标签丰富；**无几何** | [site](https://x360dataset.github.io/) |
| **360VOT / 360VOTS** | △ | ✓ 目标跟踪 | 真实 | ✗ | ✗ | 目标框/FoV；非 3D 几何集 | [360VOT](https://360vot.hkustvgd.com) |
| **ORBIT** | ✓ | △ | 真实 | ✗ | △ SfM 评测 | CVPR’26；野外 360 视频 SfM | CVPR’26 |
| **PanoGeo**（PanoWorld） | ✓ 视频 | △ | 真+合混合 | △ 伪深度管线 | △ 轨迹（光流补偿） | 自采 4K + 公开全景 + Habitat；生成向 | [arXiv](https://arxiv.org/html/2605.15391) |

**相机运动为主、场景偏静，但轨迹+深度齐全（常被当「动态相机」训练用）：**

| 数据集 | 合成/真实 | 深度 | 轨迹位姿 | 备注 |
|--------|-----------|------|----------|------|
| **Matrix-Pano** | 合成 | ✓ | ✓ | 116k **静态场景**全景视频 + 探索轨迹；UE5；生成/重建 | [Matrix-3D](https://matrix-3d.github.io/) |
| **Holo360D** | 真实 | ✓ | ✓ | 连续扫；场景基本静；**当前最大真实 ERP+depth+pose** | [HF](https://huggingface.co/datasets/ouou123/Holo360D) |
| **PanoCity** | 合成 | ✓ | ✓ | 城市连续轨；静态为主 | [HF](https://huggingface.co/datasets/YijingGuo/PanoCity) |
| **AirSim360 Omni360-Scene / WayPoint** | 合成 | ✓ | ✓ | 航拍 ERP；WayPoint 给物理一致 UAV 轨迹 | [GitHub](https://github.com/Insta360-Research-Team/AirSim360) |
| **CM-EVS** | 合+真资产渲染 | ✓ range depth | ✓ | 稀疏覆盖 ERP（非稠密视频）；Blender/HM3D/ScanNet++/TartanGround/OB3D | [GitHub](https://github.com/Strange-animalss/CM-EVS) |
| **360Loc** | 真实 | ✓（mesh 射线） | ✓ 6-DoF | CVPR’24 定位；LiDAR+360 建图；多场景序列 | [page](https://huajianup.github.io/research/360Loc/) |

### 7.1 总表（静态+动态合集，含既有条目）

| 数据集 | 年份/出处 | 静/动 | 合成/真实 | 深度 GT | 位姿 GT | 规模/场景要点 | 链接 |
|--------|-----------|-------|-----------|---------|---------|---------------|------|
| **Holo360D** | ECCV 2026 | 静（连续扫） | 真实 | ✓ LiDAR mesh/点云深度 | ✓ 6-DoF | ~10.9 万 ERP；75 场景；室内+室外；连续轨迹 | [HF](https://huggingface.co/datasets/ouou123/Holo360D) |
| **PanoCity** | CVPR 2026 | 静（连续轨） | 合成 | ✓ dense | ✓ 6-DoF（pinhole+pano） | ~12.0 万 ERP；京/济/甬城市场景 | [HF](https://huggingface.co/datasets/YijingGuo/PanoCity) |
| **Matrix-Pano** | 2025 Matrix-3D | 静景+相机运动视频 | 合成 | ✓ | ✓ 轨迹 | 116k 全景视频序列；1024×2048；文本 | [site](https://matrix-3d.github.io/) |
| **TartanAir V2 Panorama** | AirLab | 相机挑战运动 | 合成 | ✓ | ✓ | 可 ERP；SfM bench 5k/100 scenes | [tartanair.org](https://tartanair.org/) |
| **AirSim360 / Omni360-X** | CVPR 2026 | 静景 / **Human 动态** / 轨迹 | 合成 | ✓ | ✓ | Scene~61k；Human~100k；WayPoint>100k | [site](https://insta360-research-team.github.io/AirSim360-website/) |
| **CM-EVS** | arXiv 2026 | 静（稀疏多视） | 合为主 | ✓ | ✓ | 36k+ 室内 curated ERP；户外 schema 兼容 | [GitHub](https://github.com/Strange-animalss/CM-EVS) |
| **Helvipad** | CVPR 2025 | 动（人群/交通） | 真实 | ✓ LiDAR→ERP（+补全） | △ 立体外参✓，绝对轨迹弱 | ~4 万帧；上下双 Theta | [site](https://vita-epfl.github.io/Helvipad/) |
| **PanoHK360** | 2025–26 HF | 驾驶连续轨 | 真实 | ✓ LiDAR metric | ✓ 6-DoF | 8K ERP；港城 | [HF](https://huggingface.co/datasets/adadai3132/PanoHK360) |
| **360DVO Dataset** | RA-L 2026 | **动**（相机+Hard 场景） | 真实 | ✗ | △ SfM 伪 GT | 20×~1k；3840×1920 | [360dvo](https://360dvo.hkustvgd.com/) |
| **360Loc** | CVPR 2024 | 序列定位 | 真实 | ✓ | ✓ | 跨设备 query；LiDAR+360 | [page](https://huajianup.github.io/research/360Loc/) |
| **360VO（合成）** | ICRA 2022 | 相机运动 | 合成 | △ | ✓ | 10 城市场景序列 | [page](https://huajianup.github.io/research/360VO/) |
| **Matterport3D**（ERP） | 2017 | 静 | 真实 | ✓（完整度有限） | ✓ | ~1.08 万；**离散站位** | [site](https://niessner.github.io/Matterport/) |
| **Stanford 2D-3D-S** | 2017 | 静 | 真实 | ✓ | ✓ | ~1.3k ERP；室内 | [GitHub](https://github.com/alexsax/2D-3D-Semantics) |
| **Structured3D** | ECCV 2020 | 静 | 合成 | ✓ | △ 多仅 `camera_xyz` | 3.5k 户型 | [GitHub](https://github.com/bertjiazheng/Structured3D) |
| **Pano3D**（GibsonV2） | OmniCV@CVPR21 | 静 | 合成（扫描渲染） | ✓ | △/✓ | 深度 benchmark | [site](https://vcl3d.github.io/Pano3D/) |
| **OmniBlender** | CVPR 2023 | 静（小圆轨） | 合成 | ✓ | ✓ | EgoNeRF；11 场景 | [data](https://github.com/changwoonchoi/EgoNeRF) |
| **Ricoh360** | CVPR 2023 | 静（小圆轨） | 真实 | ✗ | △ SfM | Theta V | 同上 |
| **OmniPhotos** | SA 2020 | 静（圆轨） | 真实 | △ proxy mesh | △ SfM | Insta360 | [Bath](https://researchdata.bath.ac.uk/948/) |
| **Deep360** | ECCV 2022 | 静/慢动 | 合成 | ✓ depth+disp | △/✓ | 多视 OSM；污损版 | [MODE](https://github.com/nju-ee/MODE-2022) |
| **OmniHorizon** | 2022–23 | 含动态元素 | 合成 | ✓ | △ | 2.4 万户外 | [site](https://omnihorizon.github.io/) |
| **OmniStereo 系** | ICCV/ICRA | 静～慢动 | 合成 | ✓ | △ rig 外参 | 四鱼眼+ERP depth | [SNU](https://rvlab.snu.ac.kr/research/omnistereo) |
| **360Roam** | — | 静 | 真实 | ✗ | △ SfM | 分发受限 | [page](https://huajianup.github.io/research/360Roam/) |
| **OmniScenes** | PICCOLO | 静/变化 | 真实 | △ 点云 | ✓ | 室内定位；场景变化 | [PICCOLO](https://github.com/82magnolia/piccolo) |
| **360+x** | CVPR 2024 | **动**（活动） | 真实 | ✗ | ✗ | 无 3D GT | [site](https://x360dataset.github.io/) |
| **ORBIT** | CVPR 2026 | 动（相机） | 真实 | ✗ | △ SfM | 野外 SfM | CVPR’26 |
| **OmniLocalRF**（配套） | CVPR 2024 | 动视频 | 真+合 | ✗ | 合✓ / 真✗ | NVS 去动态 | [code](https://github.com/KAIST-VCLAB/OmniLocalRF) |
| **SUN360** | 2012 | 静 | 真实 | ✗ | ✗ | 无几何 | [Princeton](https://3dvision.princeton.edu/projects/2012/SUN360/) |
| **H-OmniStereo** | — | **动** | 合成 | ✓（宣称） | △ | **未开源** | [GitHub](https://github.com/JIANG-CX/H-OmniStereo) |
| **pano_point_odyssey** | 自研 | **动** | 合成 | ✓ | ✓ | 训练用 | `research_diary` |
| **Panorama_498** | 社区 | 静为主 | 混合 | △ | △ | 标注不统一 | [GitHub](https://github.com/CrazyPhilip/Panorama_498) |
| **360VOT(S)** | — | 动（目标） | 真实 | ✗ | ✗ | 跟踪框，非几何 | [360VOT](https://360vot.hkustvgd.com) |

**非原生 ERP / 弱相关（对比用）：**  
- **KITTI-360**：驾驶动、pose+LiDAR；透视+鱼眼，非标准拼接 ERP。  
- **TartanGround**：六向立体覆盖 360°，原生多 pinhole，可拼 ERP；pose+depth✓。  
- **PALVIO**：环带 PAL（非完整球面 ERP）+ mocap 位姿。  
- **iPhone360**：透视环视动态，非 ERP。

### 7.2 按维度速查

**同时 depth ✓ + 轨迹 pose ✓（重建/训练首选）**  
Holo360D，PanoCity，Matrix-Pano，TartanAir V2 Pano，AirSim360（Scene/Human），PanoHK360，360Loc，CM-EVS，OmniBlender，Deep360（多视），pano_point_odyssey，360VO（合成，depth 视导出）。

**动态（场景）+ 轨迹 pose（稀缺）**  
- **合成真值全**：pano_point_odyssey，Omni360-Human，OmniHorizon，OmniLocalRF-Synth，H-OmniStereo（未开源）。  
- **真实**：360DVO（伪位姿、无 depth），Helvipad（有 depth、绝对轨迹弱），PanoHK360（驾驶，场景动态有限）。

**有 depth、位姿弱/仅标定**  
Helvipad，Structured3D（xyz），OmniStereo 系，Pano3D。

**有轨迹 pose、无 dense depth**  
360DVO（伪 GT），Ricoh360，OmniPhotos，360Roam，ORBIT，OmniLocalRF-Real。

**连续轨迹**  
Holo360D，PanoCity，Matrix-Pano，PanoHK360，360VO，360DVO，TartanAir V2，AirSim360，Helvipad，ORBIT；Matterport3D / Stanford / CM-EVS 偏离散/稀疏站位。

### 7.3 简注（常用集 + 本次新增）

- **Holo360D / PanoCity / Matrix-Pano / TartanAir V2 Pano**：轨迹+深度齐全；前三者场景偏静，TartanAir/360VO 更适合「相机大幅运动」。  
- **360DVO**：目前较完整的**真实 360 VO** 基准（含 Hard 动态遮挡），但位姿是 **SfM 伪 GT**、无 depth——适合评 VO，不适合有监督几何。  
- **Helvipad**：真实 OSM + 场景动态 + LiDAR depth；缺的是官方绝对轨迹。  
- **Omni360-Human**：合成「场景动态 + 相机位姿」少见组合；行人 keypoints 利于 4D。  
- **pano_point_odyssey**：本仓库动态全景几何主训练源。  
- **360+x / 360VOT**：动态真实视频丰富，**无** depth/pose，不能直接当几何监督。  
- 实验区曾写「360VO 真实」——**原版 360VO 合成集是合成**；真实对应看 **360DVO Dataset**。


## 八、方法方案

### 实验

训练数据集

- PanoCity
- Matterport3D
- Stanford2D3DS
- PanoPointOdyssey, 自造，合成，动态，深度+位姿gt
- 360DVO Dataset, **真实**，动态（Hard），位姿△ SfM 伪 GT，无 depth
- helvipad, 真实，动态，深度gt，绝对轨迹弱
- OmniStereo, urban和things子集，合成，动态，深度gt
- 360+x, 真实，动态，相机不动，没有深度gt
- AirSim360——Omni360_Scene, 室外，合成，静止，深度+位姿gt
- TartanAir V2 Pano（可选）, 合成，挑战轨迹，深度+位姿gt。https://github.com/colmap/colmap/releases/tag/datasets-tartanair-v2-v1
- Deep360, 合成，室外，自动驾驶，深度gt

评测数据集

- [PanoCity]

  相机位姿、深度、点云重建

- [Matterport3D]

  相机位姿、深度、点云重建

- [2D-3D-S](https://github.com/alexsax/2D-3D-Semantics)

  相机位姿、深度、室内点云重建。[下载链接](https://sdss.redivis.com/datasets/f304-a3vhsvcaf)

  test split 是 area_5b 序列。

- [Structured3D](https://zju-kjl-jointlab-azure.kujiale.com/Structured3D/README.txt)

  弹幕深度估计

- [Pano3D]

  zero-shot 测深度

- pano_point_odyssey（见 research_diary）：indoor/outdoor，**dynamic**

- 360DVO

  有位姿gt

- Holo360D ?

  室外，真实，连续轨迹，位姿+深度gt
