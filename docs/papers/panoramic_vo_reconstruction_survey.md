# 全景相机 Visual Odometry 与场景重建：精选文献简报

调研日期：**2026-09-12**。覆盖经典方法与截至该日可查的近期工作；以论文原文、会议论文集和作者项目页核对。本文重在代表性与选题价值，不追求穷尽。文中的阅读优先级和研究机会是综合判断，性能不作跨数据集排名。

## 1. 先划清问题边界

- **输入相机**：重点是覆盖 360°×180° 的球面全景，通常存为等距柱状投影图（ERP）；兼收原始双鱼眼、多鱼眼相机组、全景环带镜头（PAL），并明确标注。它们的成像模型和标定条件不同。
- **输入组织**：视频／连续序列适合 VO、SLAM；离散多站位图片适合 SfM 和多视图重建；单张全景主要依赖深度或生成先验。把一张全景切成六张 cubemap，只改变投影，**不会产生新的平移视差**。
- **输出任务**：VO 估计连续运动；SLAM 还考虑地图与全局一致性；几何重建输出深度、点云或网格；新视角合成（NVS）重视渲染。高质量 NeRF／3D Gaussian Splatting（3DGS）渲染不自动意味着高精度表面。
- **动态场景**：应分别讨论“动态干扰下定位”“去除动态物体后的静态重建”“保留真实运动的 4D 重建”“由单图／文本生成 4D”。后两者尤其不能混为一谈。

**建议抓住三条主线**：球面几何与可微束调整（BA）；真实相机标定与全景可微渲染；无位姿多图的前馈几何重建。对应代表分别是 **360DVO／CubeDVO、Seam360GS／ODGS-SLAM、PanoSplatt3R／PanoVGGT／Argus**，原文见下表。

## 2. Visual Odometry、SLAM 与在线建图

以下以顺序输入为主。除明确的动态建模外，能处理部分运动干扰不等于能恢复动态物体的三维运动。

| 论文与发表信息 | 输入 → 输出 | 核心贡献与阅读价值 |
|---|---|---|
| [Omnidirectional DSO: Direct Sparse Odometry with Fisheye Cameras](https://arxiv.org/abs/1808.02775)，RA-L / IROS 2018 | **单鱼眼**视频 → 轨迹、稀疏结构 | 用统一全向相机模型扩展 DSO，在滑窗内联合优化位姿、结构、相机与亮度参数。理解大视场直接法的经典起点；输入不是完整 ERP。 |
| [OpenVSLAM: A Versatile Visual SLAM Framework](https://arxiv.org/abs/1910.01122)，ACM MM 2019 | 含 ERP 的图像序列 → 轨迹、稀疏地图 | 支持多种相机模型的特征式 SLAM，适合做全景几何基线。工程入口可参考其非官方延续分支 [stella_vslam](https://github.com/stella-cv/stella_vslam)。 |
| [OmniSLAM: Omnidirectional Localization and Dense Mapping for Wide-baseline Multi-camera Systems](https://arxiv.org/abs/2003.08056)，ICRA 2020 | **宽基线多鱼眼**序列 → 轨迹、稠密地图 | 把学习式全景深度用于匹配与 VO，再做回环和 TSDF 融合。是“深度估计—定位—表面融合”完整系统的代表，依赖相机组标定。 |
| **[360VO: Visual Odometry Using A Single 360 Camera](https://huajianup.github.io/research/360VO/360VO_ICRA2022.pdf)**，ICRA 2022 | 单台 360 相机 ERP 视频 → 轨迹、稀疏结构 | 将 DSO 扩展到球面投影和全景极线几何，直接优化 ERP 光度误差。**全景 VO 必读基线**；关注光度变化、拼接误差和尺度漂移。 |
| [PAL-SLAM2](https://doi.org/10.1016/j.isprsjprs.2024.03.016)，ISPRS JPRS 2024 | **PAL 环带图像**，可加 IMU → 轨迹、稀疏地图 | 用单位球处理相机后半空间的特征，结合视觉惯性优化、多地图与回环。适合机器人全向定位；环带视场并不覆盖完整天顶／地面。 |
| [Omnidirectional Dense SLAM for Back-to-back Fisheye Cameras](https://ieeexplore.ieee.org/document/10610351/)，ICRA 2024 | **背靠背双鱼眼 + IMU** → 位姿、稠密重建 | VIO 前端提供稀疏深度，多基底全景深度补全后继续几何优化。适合研究实际双鱼眼硬件上的在线稠密建图。 |
| **[360DVO: Deep Visual Odometry for Monocular 360-Degree Camera](https://arxiv.org/abs/2601.02309)**，RA-L 2026 | ERP 连续帧 → 位姿、patch 深度 | 畸变感知球面特征 + 循环匹配更新 + 全向可微 BA。是学习式全景 VO 的重点基线；[作者页](https://chris1004336379.github.io/360DVO-homepage/)提供代码与真实评测集入口。 |
| **[CubeDVO: Cubemap-Spherical Deep Visual Odometry for a Monocular 360-Degree Camera](https://www.robot.t.u-tokyo.ac.jp/~yamashita/paper/A/A230Final.pdf)**，RA-L 2026 | ERP 视频，经 cubemap 编码 → 位姿、patch 深度 | 在 cubemap 上提特征，在单位球切空间做可微 BA，并给光流网络注入球面几何。**适合与 360DVO 对读**：核心问题是特征与误差应定义在哪个空间。 |
| **[ODGS-SLAM: Omnidirectional Gaussian Splatting SLAM](https://odgs-slam.github.io/)**，CVPR 2026 | ERP RGB 或 RGB-D 序列 → 位姿、3DGS 地图 | 推导 ERP 下跟踪与建图的闭式梯度，以高斯统一表示地图，并用图分析移除关键帧。**全景 GS-SLAM 重点读物**；RGB 与 RGB-D 设置应分开比较。 |
| [HALO-SLAM / Look Up and Look Back](https://arxiv.org/abs/2608.00925)，**arXiv 2026-08** | 单目全景序列 → 轨迹、全局对齐子地图 | 从冻结全景几何模型读取重力线索，用跨视图注意力筛选回环，再以 Sim(3) 位姿图校正尺度与漂移。新意在模型内部特征如何服务 SLAM；目前按预印本看待。 |

**阅读顺序**：360VO → 360DVO → CubeDVO；随后按目标读 ODGS-SLAM（稠密地图）或 HALO-SLAM（基础模型与回环）。手里有原始双鱼眼和 IMU 时，优先补读 ICRA 2024 的背靠背双鱼眼系统。

## 3. 静态场景：离散图片与视频重建

### 3.1 先保留可靠的几何基线

**SfM → 多视图深度 → 点云／网格融合**仍是必要对照。SfM 可以处理无序多站位图片，但需要足够共视与平移视差；不同站位之间没有视觉重叠时，常规匹配式方法无法凭空确定相对位置。

[COLMAP 官方文档](https://github.com/colmap/colmap/blob/main/doc/rigs.rst)提供将全景渲染为虚拟透视相机组的流程，同一全景的子视图共享相机中心和已知相对旋转。另据[官方更新记录](https://colmap.github.io/changelog.html)，**4.1.0（2026-06）已加入原生球面 ERP 相机模型**；因此不能再笼统写“COLMAP 不支持全景”。原生球面与虚拟透视两条路线值得实测比较，密集阶段也要核对具体投影支持。

| 论文与发表信息 | 输入 → 输出 | 核心贡献与适用边界 |
|---|---|---|
| [OmniPhotos: Casual 360° VR Photography](https://richardt.name/publications/omniphotos/)，TOG / SIGGRAPH Asia 2020 | 沿小圆轨迹拍摄的 360 视频 → 带视差的 VR 浏览 | 用代理几何与图像重投影合成视图，展示低成本全景采集的价值；适合局部移动浏览，不应当作精确完整网格重建。 |
| **[Egocentric Scene Reconstruction from an Omnidirectional Video](https://vclab.kaist.ac.kr/siggraph2022p2/paper-acmtog-main-final.pdf)**，TOG / SIGGRAPH 2022 | 短全景视频 → **带纹理的表面网格** | 球面视差网络估深度，再用 spherical binoctree 与自适应 TSDF 融合。**如果真正关心几何表面，这篇比只看渲染指标的方法更直接。** |
| [360Roam](https://huajianup.github.io/research/360Roam/)，arXiv 2022；另有 SIGGRAPH Asia 2022 Technical Communications 版本 | 多站位 360 图像与位姿 → 室内辐射场 | 先恢复概率占据结构，再按几何划分局部辐射场，实现大室内场景漫游。关注空间分解与采样，不把实时渲染理解为实时重建。 |
| **[EgoNeRF / Balanced Spherical Grid for Egocentric View Synthesis](https://www.changwoon.info/publications/EgoNeRF)**，CVPR 2023 | 360 视频抽帧与位姿 → 辐射场 | 以平衡球面网格表达向外观察的场景，分配近远处采样与表示容量。理解“全景相机应配什么三维表示”的代表。 |

### 3.2 全景 3DGS：从逐场景优化到无位姿前馈重建

“带位姿”表示重建阶段使用已知或预先估计的相机参数；“无位姿”表示无需把相机位姿作为输入，仍可能依赖预训练几何先验。下列方法以静态场景为主要目标。

| 论文与发表信息 | 输入 → 输出 | 核心贡献与适用边界 |
|---|---|---|
| **[ODGS: 3D Scene Reconstruction from Omnidirectional Images with 3D Gaussian Splattings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/6882dbdc34bcd094e6f858c06ce30edb-Abstract-Conference.html)**，NeurIPS 2024 | 多张带位姿 ERP → 逐场景优化的 3DGS | 为全景设计高斯投影与光栅化，解决直接套透视 rasterizer 的畸变。适合研究全景可微渲染的底层模块。 |
| **[SC-OmniGS: Self-Calibrating Omnidirectional Gaussian Splatting](https://arxiv.org/abs/2502.04734)**，ICLR 2025 | 多张全景，位姿有噪声或无位姿先验 → 位姿、相机模型、3DGS | 联合优化球面相机、畸变与高斯；强调自标定。适合真实消费级相机与初始位姿不可靠的情况，属于逐场景优化。 |
| **[Seam360GS](https://openaccess.thecvf.com/content/ICCV2025/papers/Shin_Seam360GS_Seamless_360deg_Gaussian_Splatting_from_Real-World_Omnidirectional_Images_ICCV_2025_paper.pdf)**，ICCV 2025 | 真实双鱼眼设备产生的全景图 → 校准后的 3DGS / NVS | 显式建模镜头间距和角度畸变，联合校准与高斯优化。**做真实全景数据值得优先读**：拼接图并不严格服从理想共心球面模型。 |
| **[Splatter-360](https://openaccess.thecvf.com/content/CVPR2025/html/Chen_Splatter-360_Generalizable_360_Gaussian_Splatting_for_Wide-baseline_Panoramic_Images_CVPR_2025_paper.html)**，CVPR 2025 | 稀疏、宽基线、带位姿全景 → 前馈 3DGS | ERP 与 cubemap 双投影编码，结合球面扫描代价体做多视图匹配。**已知位姿、离散全景重建的重要基线**。 |
| [OmniSplat](https://openaccess.thecvf.com/content/CVPR2025/html/Lee_OmniSplat_Taming_Feed-Forward_3D_Gaussian_Splatting_for_Omnidirectional_Images_with_CVPR_2025_paper.html)，CVPR 2025 | 稀疏带位姿全景 → 前馈 3DGS | 用 Yin–Yang 球面网格复用透视域预训练网络，降低畸变与域差距。“Training-free”指适配不需额外训练，不代表没有预训练或位姿条件。 |
| [PanSplat: 4K Panorama Synthesis with Feed-Forward Gaussian Splatting](https://openaccess.thecvf.com/content/CVPR2025/html/Zhang_PanSplat_4K_Panorama_Synthesis_with_Feed-Forward_Gaussian_Splatting_CVPR_2025_paper.html)，CVPR 2025 | 宽基线带位姿全景 → 高分辨率前馈 3DGS | Fibonacci 球面分布、高斯金字塔和分层代价体，降低极区冗余及显存需求。适合关注 4K 输出与效率的工作。 |
| **[PanoSplatt3R](https://npucvr.github.io/PanoSplatt3R/)**，ICCV 2025 | **无位姿、宽基线全景图对** → 三维几何、3DGS | 将透视域重建预训练迁移到全景，以 RoPE rolling 表达水平周期性。适合研究无位姿稀疏全景的几何与渲染；[代码](https://github.com/zhichu99/PanoSplatt3R)。 |
| **[PanoVGGT: Feed-Forward 3D Reconstruction from Panoramic Imagery](https://arxiv.org/abs/2603.17571)**，CVPR 2026 | **单张或无序多张、无位姿 ERP** → 位姿、深度、点云 | 球面位置编码、三轴 SO(3) 增强、随机锚点训练；同时提供 PanoCity。**当前研究全景几何基础模型的重要起点**；[代码与发表信息](https://github.com/YijingGuo-June/PanoVGGT)。 |
| [CylinderSplat](https://arxiv.org/abs/2603.05882)，ICLR 2026 | 单张或多张全景 → 前馈 3DGS | 像素分支重建可见区，圆柱 triplane 分支补全遮挡区。适合研究三维表示与稀疏视图补全；补出的结构依赖先验，不能等同于实测几何。 |
| **[PFGS360 / Pose-Free Omnidirectional Gaussian Splatting for 360-Degree Videos with Consistent Depth Priors](https://openaccess.thecvf.com/content/CVPR2026/html/Zhuang_Pose-Free_Omnidirectional_Gaussian_Splatting_for_360-Degree_Videos_with_Consistent_Depth_CVPR_2026_paper.html)**，CVPR 2026 | **无位姿全景视频** → 位姿、3DGS | 用球面一致的 2D–3D 对应估位姿，以深度一致性筛选增密。适合研究摆脱 SfM 初始化的重建流程；不能仅凭 pose-free 就认定具备完整 SLAM 的回环能力。 |
| **[Argus: Metric Panoramic 3D Reconstruction for Indoor Scenes](https://argus-paper.realsee.ai/)**，ECCV 2026（作者页确认录用） | **稀疏、无序、无位姿室内全景** → 度量位姿、深度、点云 | 学习共视关系选择参考帧，分解并监督像素到世界坐标的几何变换。Realsee3D 支持其度量学习；**与 PanoVGGT 对读**，重点检查跨场景尺度泛化；[代码](https://github.com/realsee-developer/Argus)。 |

### 3.3 单张全景：重建与补全先验

单张全景提供完整的观察方向，却只观测一个站位的可见表面。以下方法适合沉浸式内容制作；遮挡后方的形状与纹理包含推断或生成成分。

| 论文与发表信息 | 输入 → 输出 | 一句话总结 |
|---|---|---|
| [PERF: Panoramic Neural Radiance Field from a Single Panorama](https://github.com/perf-project/PeRF)，TPAMI 2024 | 单张全景 → NeRF | 从深度初始化出发，协同补全 RGB 与深度，并渐进修复多视图不一致；是单图全景漫游的代表。 |
| [Pano2Room: Novel View Synthesis from a Single Indoor Panorama](https://arxiv.org/abs/2408.11413)，SIGGRAPH Asia 2024 | 单张室内全景 → 网格、3DGS | 先建初始网格，以全景 RGB-D 修复器扩展几何并生成伪新视图，再优化高斯；[作者代码](https://github.com/TrickyGo/Pano2Room)。 |
| [Scene4U](https://openaccess.thecvf.com/content/CVPR2025/html/Huang_Scene4U_Hierarchical_Layered_3D_Scene_Reconstruction_from_Single_Panoramic_Image_CVPR_2025_paper.html)，CVPR 2025 | 单张全景 → 分层 3DGS | 开放词表分割与语言模型分层，扩散修复遮挡区域，再分层优化高斯。关注前后景分离与编辑；“4U”不意味着真实动态 4D。 |

## 4. 动态场景：哪些工作真的重建了运动？

| 工作 | 输入与实际输出 | 方法与判断 |
|---|---|---|
| **[OmniLocalRF: Omnidirectional Local Radiance Fields from Dynamic Videos](https://openaccess.thecvf.com/content/CVPR2024/html/Choi_OmniLocalRF_Omnidirectional_Local_Radiance_Fields_from_Dynamic_Videos_CVPR_2024_paper.html)**，CVPR 2024 | 真实／合成全景动态视频 → **去动态后的静态辐射场** | 局部辐射场、双向射线优化和多分辨率运动掩码，去掉行人、拍摄者等干扰并补全背景。动态输入重建的重点论文，但不输出运动物体的真实 4D。 |
| [4K4DGen: Panoramic 4D Generation at 4K Resolution](https://arxiv.org/abs/2406.13527)，ICLR 2025 | **单张全景** → 生成的动态视频 → 4D 高斯 | 全景扩散去噪器生成运动，再做时空一致的三维提升。属于 Panorama-to-4D **生成**，运动并非来自真实视频观测。 |
| [HoloTime: Taming Video Diffusion Models for Panoramic 4D Scene Generation](https://arxiv.org/abs/2504.21650)，arXiv 2025 | 文本／参考图 → 生成全景视频 → 4D 高斯 | 360World 数据、全景视频生成和时空深度重建结合；适合参考时序一致性与 4D 表达，仍属于生成路线。 |

**本次检索判断**：在已核实的代表工作中，原生全景的静态重建、动态移除和生成式 4D 已有清楚脉络；“从真实移动 360 相机视频，同时恢复相机轨迹、动态物体几何与长期三维对应”的成熟方案相对稀少。这是值得继续检索与验证的机会，不能据此宣称整个领域不存在相关工作。

可迁移的动态思路包括 [MonST3R](https://monst3r-project.github.io/) 的动态视频几何估计，以及 [4DGS360](https://arxiv.org/abs/2603.21618) 的动态物体大视角重建。但应核对其输入模型；尤其 **4DGS360 的“360”指物体环视重建，不是 ERP 全景相机输入**。把透视模型迁移到全景，需要重新处理射线、跨接缝对应、球面误差与相机运动分离。

## 5. 深度与立体：作为重建模块阅读

以下方法通常不独立完成跨帧定位和全局建图，但可以提供深度初始化、几何监督或可微匹配模块。

| 论文 | 输入与核心思想 | 与主任务的关系 |
|---|---|---|
| [OmniMVS: End-to-End Learning for Omnidirectional Stereo Matching](https://snu.elsevierpure.com/en/publications/omnimvs-end-to-end-learning-for-omnidirectional-stereo-matching/)，ICCV 2019 | 标定多鱼眼 → 球面扫描、代价体 → 全景深度 | 球面多视图匹配的经典起点；几何尺度由已知相机基线提供。 |
| [UniFuse: Unidirectional Fusion for 360° Panorama Depth Estimation](https://arxiv.org/abs/2102.03550)，2021 | 单张 ERP 与对应 cubemap，解码时单向融合特征 | 简洁的双投影深度基线，适合理解全局上下文与局部畸变的取舍。 |
| [OmniVidar](https://openaccess.thecvf.com/content/CVPR2023/html/Xie_OmniVidar_Omnidirectional_Depth_Estimation_From_Multi-Fisheye_Images_CVPR_2023_paper.html)，CVPR 2023 | 四鱼眼极线校正，将全向深度化为双目估计 | 避开高开销 3D 卷积，适合高分辨率与机器人部署。 |
| **[Depth Any Panoramas（DAP）](https://openaccess.thecvf.com/content/CVPR2026/html/Lin_Depth_Any_Panoramas_A_Foundation_Model_for_Panoramic_Depth_Estimation_CVPR_2026_paper.html)**，CVPR 2026 | 单张 ERP → 度量深度；大规模数据与伪标签、距离范围建模 | 适合为全景 SLAM／GS 提供深度先验；预测的度量尺度仍须在目标域验证。 |
| [VGGT-360: Geometry-Consistent Zero-Shot Panoramic Depth Estimation](https://arxiv.org/abs/2603.18943)，CVPR 2026 | 单张全景自适应切透视视图，借助几何基础模型对齐后重投影 | 无额外训练的全景深度路线。**区别于 PanoVGGT 的无序多站位联合重建任务**。 |

## 6. 数据集：按任务选，不只看是否写着“360”

| 数据／入口 | 适合评什么 | 关键条件 |
|---|---|---|
| [360DVO Dataset](https://chris1004336379.github.io/360DVO-homepage/) | 真实全景 VO、快速运动与动态干扰 | 20 段序列，Easy / Hard 划分；位姿是 **Metashape SfM 伪真值**，不能当独立高精度测量。 |
| [ODGS-SLAM Dataset](https://odgs-slam.github.io/) | 全景轨迹与建图、不同相机模型对比 | 含受控真实与合成序列及轨迹真值，适合补充 VO 成功率与 ATE 评测。 |
| [PanoCity / PanoVGGT](https://github.com/YijingGuo-June/PanoVGGT) | 室外多图几何、位姿与深度 | 合成城市全景，提供深度和 6-DoF 位姿；用于训练后应额外检查真实域泛化。 |
| [Holo360D](https://github.com/Jou719/Holo360D)，ECCV 2026（作者确认录用） | 真实连续轨迹的多视图几何重建 | 109,495 张全景，配准点云、网格、深度和位姿。深度含扫描与后处理成分，不等同于动态物体逐帧真值。 |
| [Realsee3D / Argus](https://dataset.realsee.ai/) | 稀疏、无序室内全景的度量重建 | 约 29.9 万站位，1,000 个真实与 9,000 个合成场景；适合与连续视频设置形成互补。 |
| [HELVIPAD](https://vita-epfl.github.io/Helvipad/)，CVPR 2025 | 真实动态环境下的全景立体深度 | 上下双 360 相机 + LiDAR，约 4 万帧；应区分 LiDAR 投影标签与补全标签，主要针对深度而非完整 4D 对应。 |
| [OmniBlender / Ricoh360](https://www.changwoon.info/publications/EgoNeRF) | 静态全景 NVS 与 GS / NeRF 基线 | 分别为合成与真实全景采集；几何真值条件不同，不应合并成同一种监督数据。 |
| [Splatter-360 数据入口](https://3d-aigc.github.io/Splatter-360/) | 室内宽基线全景 NVS | 提供基于 HM3D / Replica 的处理与评测入口；应统一站位、基线距离及划分，避免相邻视图泄漏。 |

## 7. 阅读与选题建议

**先读这八项**，能较快形成完整认识：360VO；360DVO 与 CubeDVO 对读；SIGGRAPH 2022 的 Egocentric Scene Reconstruction；ODGS-SLAM；Seam360GS；PanoSplatt3R；PanoVGGT 与 Argus 对读；OmniLocalRF。再按兴趣补读 Splatter-360／PanSplat（渲染）或 4K4DGen（生成式 4D）。

| 你的目标 | 建议基线组合 | 最值得追问的问题 |
|---|---|---|
| 单台全景相机的稳健 VO | 360VO + 360DVO + CubeDVO | 精度提升来自特征、球面误差，还是数据与初始化？快速转动、弱纹理和动态占比升高时是否仍成立？ |
| 视频输入的稠密地图 | 几何 SfM / SLAM + ODGS-SLAM + PFGS360 | 位姿漂移、表面误差与渲染误差能否同时降低？长序列的存储与回环是否可靠？ |
| 离散无位姿全景图片重建 | COLMAP + PanoSplatt3R + PanoVGGT / Argus | 稀疏共视、房间切换和真实拼接误差下，几何一致性及度量尺度能否保持？ |
| 真实动态全景 4D | OmniLocalRF 的动静分离 + 全景几何前端 + 动态几何模型 | 能否同时恢复背景、自运动和物体运动，并提供跨时间三维对应，而不只是消掉运动物体？ |

**更值得投入的方向（研究判断）**：① 面向真实双鱼眼的非共心射线建模与联合标定；② 无位姿全景几何模型与长序列回环结合；③ 真实动态全景的运动分解与三维跟踪。单纯“把 ERP 切成透视图再套现有模型”可以是有用基线，但要形成有说服力的贡献，需要证明如何解决几何、跨接缝或时间一致性问题。

**比较论文时保留四项检查**：单目绝对尺度来自额外传感器还是学习先验；VO 报告是否包含失败序列；重建是否有独立深度／表面评测；NVS 是否在统一的留出视角和球面加权指标下比较。理想共心、纯视觉几何的全景相机仍有单目尺度歧义，纯旋转也不会提供平移三角化深度。

> 使用说明：表格链接直接指向原文、出版记录或作者入口；项目代码仅核对公开入口，未在本次调研中运行复现。生成式 4D、鱼眼／PAL 系统与原生 ERP 几何方法已分别标注。
