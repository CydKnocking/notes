本文档为全景相机做三维重建/四维重建的相关论文整理。  
范围：近三年（约 2023–2025）CVPR / ICCV / ECCV / AAAI / NeurIPS / ICLR / ICRA / 3DV / TPAMI / ICML / IROS（及紧密相关的 RA-L）。  
重点：动态场景 / 4D；其次为静态新视角合成、深度/立体、SLAM。

> **总览判断**  
> - **真·全景动态重建（从真实 360 视频重建可漫游 4D）仍极少**：明确顶会代表作主要是 **OmniLocalRF (CVPR’24)**（偏“去动态、保静态”）与生成式 **4K4DGen (ICLR’25)** 等。  
> - 主线仍是：**全景几何适配（球坐标 / ERP 光栅化）→ 可泛化 feed-forward 3DGS → 单张全景 lift-to-3D → 全景深度/OSM / SLAM**。  
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

### 1.3 空白与可做方向（结合本仓库兴趣）

| 方向 | 现状 |
|------|------|
| 真实 360 视频上的 dense 4D + correspondence | 几乎空；透视域有 St4RTrack / CUT3R / Flow4R |
| 全景 feed-forward 动态几何（类 MonST3R/POMATO 的 ERP 版） | 未见顶会成熟方案；PanoVGGT 等偏静态 |
| 驾驶/室内全景动态 + metric scale | 数据稀缺；Helvipad 等仍偏立体深度 |

相关透视动态工作见 `4drecon_tracking.md`，可迁移球形 PE / ERP 光栅化。


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

- [PanoVGGT](https://arxiv.org/abs/2603.17571)  
  全景版 VGGT；球感位置编码 + SO(3) 增强；PanoCity 等。静态、离线。上科大。

- [VGGT-360](https://arxiv.org/abs/2603.18943)  
  （待补读）


## 六、按会议速查（2023–2025，不完全表）

| 会议 | 代表工作 |
|------|----------|
| **CVPR’23** | EgoNeRF；HRDFuse；OmniVidar |
| **CVPR’24** | **OmniLocalRF（动态）**；OmniSDF |
| **CVPR’25** | Scene4U；Splatter-360；OmniSplat；PanSplat；Helvipad |
| **ICCV’25** | Seam360GS；MDP-Omni |
| **ECCV** | 近三年核心全景 3D/4D 偏少（需持续扫）；透视 3DGS 误差分析等工作有间接价值 |
| **NeurIPS’23** | PanoGRF |
| **NeurIPS’24** | ODGS |
| **NeurIPS’25** | Omni3D |
| **ICLR’25** | SC-OmniGS；**4K4DGen（全景 4D 生成）** |
| **AAAI’24** | Pano-NeRF |
| **TPAMI’24** | PERF |
| **ICRA’24** | Omnidirectional Dense SLAM（双鱼眼） |
| **IROS’23** | 360FusionNeRF |
| **3DV’25** | 360-GS |
| **RA-L’24** | RomniStereo |
| **ICML** | 近三年几乎未见“全景相机原生 3D/4D”主力论文 |

**ECCV / ICML**：该时间窗内“全景相机做 3D/4D 重建”的一线论文密度明显低于 CVPR/NeurIPS/ICLR；很多相关工作在 WACV、RA-L 或 arXiv。


## 七、相关工作（原笔记）

- [PanoVGGT](https://arxiv.org/abs/2603.17571)
  
  全景相机版本 VGGT，上海科大。静态场景，离线。

  构造了新的数据集 PanoCity: 超过 120000 张带位姿和深度标注的全景图。虚拟数据集、室外场景、主要静态场景、不同天气条件。

  方法：

  1. DINOv2 编码。和 VGGT 类似的交替注意力模块。

  2. 从标准的 2D 网格编码改为球感位置编码 (Spherical-aware PE)

  3. 数据增强改用了 SO(3) 旋转增强，并随机定 target frame。
  
  8 张 A100 训练 10 天。用的数据集：PanoCity、Matterport3D、Stanford2D3D 和 Structured3D。

- [VGGT-360](https://arxiv.org/abs/2603.18943)
  

## 八、数据集

- [360+x](https://x360dataset.github.io/)

  动态场景。无 3D 标注。室内室外。

- [Pano3D](https://vcl3d.github.io/Pano3D/)

  静态场景。有 3D 标注。室内。

- [Panorama_498](https://github.com/CrazyPhilip/Panorama_498)

- [H-OmniStereo](https://github.com/JIANG-CX/H-OmniStereo)

  合成数据集。双全景相机。动态场景。室内外。暂未开源。

- [OmniStereo](https://sites.google.com/view/snu-rvlab/research/omnistereo)

  合成数据集。动态场景。有 depth 标注，室外驾驶场景。

- [SUN360](https://3dvision.princeton.edu/projects/2012/SUN360/)

  静态场景。

- [Matterport3D](https://huggingface.co/datasets/Gen3DF/Matterport3d/tree/main/matterport3d)

  静态场景。benchmark。

- [Holo360D](https://huggingface.co/datasets/ouou123/Holo360D)

  静态场景。室内外。真实数据集。有 depth，camera poses。2.66T。ECCV2026。

- [OmniHorizon](https://omnihorizon.github.io/)

  暂未开源。

- [Structured3D](https://huggingface.co/datasets/Gen3DF/Structured3D)

- [Stanford 2D-3D-S](https://github.com/alexsax/2D-3D-Semantics)

- [Helvipad](https://github.com/vita-epfl/Helvipad) — CVPR 2025，真实 OSM（双 360 + LiDAR）

- EgoNeRF 配套：OmniBlender（合成）、Ricoh360（真实）

- ODGS 评测常用：OmniPhotos、360Roam、OmniScenes、360VO 等


## 九、方法方案

### 实验

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
