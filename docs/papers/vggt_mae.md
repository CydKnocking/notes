# VGGT 类几何基础模型 × MAE / Masked Modeling

整理「三维几何基础模型（VGGT / DUSt3R 系）」与「MAE / Masked Image Modeling」交叉相关的工作。  
结论先说清：

> **截至目前，未检索到一篇论文把完整 VGGT 架构直接加上标准 MAE 预训练目标做端到端训练。**  
> 但已有清晰谱系：**MAE → CroCo（跨视角 completion）→ DUSt3R/MASt3R（CroCo 初始化 + 几何监督）→ VGGT（多视图几何预测）→ MuM / Muskie（多视图 MAE 学几何表征）**。  
> 其中 **MuM (CVPR 2026)**、**Muskie (arXiv 2025)** 是最接近「MAE 版 VGGT 思想」的工作。


## 1. 问题拆分：两条路线

| 路线 | 目标形式 | 代表 |
|------|----------|------|
| **A. 几何预测 foundation** | \(I_{1:N}\rightarrow\{\text{camera},\,D,\,P,\,\text{tracks}\}\) | DUSt3R, MASt3R, **VGGT** |
| **B. Masked modeling 预训练** | \(I_{1:N}^{\text{masked}}\rightarrow I_{1:N}^{\text{orig}}\)（或 depth/BEV/Gaussian） | MAE, CroCo, **MuM**, **Muskie**, GeoMIM, Video-GMAE |

交叉点：

1. **用 B 预训练，再接 A 下游**（CroCo→DUSt3R；MuM frozen encoder + VGGT-style heads）  
2. **A 的架构 + B 的 pretext**（Muskie：交替注意力多视图 backbone + multi-view MIM）  
3. **A 产出几何，再对几何做 mask 学习**（POMA-3D：对 pointmap 做 JEPA；依赖 VGGT 生成数据）


## 2. 技术谱系（推荐阅读顺序）

```text
MAE (He+ 2022)
  │  单图 patch mask → 像素重建（偏语义）
  ▼
CroCo / CroCo v2 (NeurIPS 2022 / ICCV 2023)
  │  跨视角 completion：用 view B 补 view A 的 mask
  │  （强制学对应 / 相对位姿 / 场景几何）
  ▼
DUSt3R (CVPR 2024)  ← 权重常从 CroCo 初始化
  │  监督回归 pointmap
  ▼
MASt3R (ECCV 2024) / VGGT (CVPR 2025)
  │  匹配增强 / 任意多视图一次前向几何预测
  ▼
MuM (CVPR 2026) · Muskie (2025)
     多视图 MAE：任意 N 视图 mask 重建 → 几何感知 backbone
     MuM 下游显式训「VGGT-inspired」feed-forward recon
```


## 3. 核心论文

### 3.1 最接近「VGGT + MAE」

#### MuM: Multi-View Masked Image Modeling for 3D Vision — **CVPR 2026**

- 链接：[arXiv:2511.17309](https://arxiv.org/abs/2511.17309) · [project](https://www.davnords.com/mum) · [code](https://github.com/davnords/MuM)
- 作者：David Nordström, Johan Edstedt, Fredrik Kahl, Georg Bökman
- **做法**：把 MAE 扩到**任意多视图**；各 view 均匀 mask；轻量 decoder + **inter-frame attention** 重建 mask patch。
- **定位**：自述延续 CroCo；比 CroCo 更简单可扩展（对称目标、不强制严格 covisibility）。
- **与 VGGT 关系**：下游用 **frozen MuM encoder + VGGT/MapAnything 风格** 的 camera/DPT heads 做 feed-forward 重建；并训 RoMa 式匹配。报告在重建 / matching / relative pose 上超过 **DINOv3、CroCo v2**。
- **数据**：约 20M 帧混合（ScanNet++、MegaScenes、DL3DV、CO3D、MegaDepth 等）+ 10% ImageNet。
- **一句话**：目前最像「用 multi-view MAE 训出几何 backbone，再接到 VGGT 式几何头」的工作。

#### Muskie: Multi-view Masked Image Modeling for 3D Vision Pre-training — arXiv 2025

- 链接：[arXiv:2511.18115](https://arxiv.org/abs/2511.18115) · [project](https://leo-frank.github.io/Muskie/) · [code](https://github.com/leo-frank/Muskie)
- 作者：Wenyu Li, Sidun Liu, Peng Qiao, Yong Dou, Tongrui Hu
- **做法**：**原生多视图** backbone（非逐帧再融合）；高 mask 率 + 空间集中 mask；用其他 view 的几何对应补当前 view；**无 3D 监督**。
- **架构**：交替注意力等设计，与 VGGT 系「frame/global attention」思路接近。
- **下游**：camera pose、pointmap reconstruction、multi-view correspondence；相对 DINO 等 frame-wise VFM 多视图一致性更强。
- **一句话**：比 MuM 更强调「native multi-view encoder」；是另一条「MAE → 3D foundation backbone」直通车。


### 3.2 源头：跨视角 MAE

#### CroCo — **NeurIPS 2022**

- 链接：[project](https://croco.europe.naverlabs.com/) · [NeurIPS PDF](https://proceedings.neurips.cc/paper_files/paper/2022/file/16e71d1a24b98a02c17b1be1f634f979-Paper-Conference.pdf)
- **做法**：mask view A；用 A 可见部分 + **完整 view B** 重建 A。  
  单图 MAE 靠语义先验；跨视角 completion 必须理解相对几何与对应。
- **意义**：MuM 明确称 CroCo 为「面向 3D 的 MAE 形态」。

#### CroCo v2 — **ICCV 2023**

- 链接：[arXiv:2211.10408](https://arxiv.org/abs/2211.10408)
- 强化相对位置编码与规模；面向 stereo / optical flow；DUSt3R 常用其预训练权重初始化。


### 3.3 几何预测系（对照，非 MAE 主目标）

#### DUSt3R — **CVPR 2024**

- [arXiv:2312.14132](https://arxiv.org/abs/2312.14132)
- **监督** pointmap 回归；**预训练**：CroCo 初始化（MAE 系 → 几何监督）。

#### MASt3R — **ECCV 2024**

- 在 DUSt3R 上增强匹配 / metric 能力。

#### VGGT — **CVPR 2025**

- [arXiv:2503.11651](https://arxiv.org/abs/2503.11651) · [CVPR OA](https://openaccess.thecvf.com/content/CVPR2025/html/Wang_VGGT_Visual_Geometry_Grounded_Transformer_CVPR_2025_paper.html)
- 任意多视图一次前向预测 camera / depth / pointmap / tracks；**主目标是几何监督预测，不是 mask 重建**。
- 架构：标准大 Transformer + frame-wise / global 交替注意力；无强 3D inductive bias。


### 3.4 相关但任务不同的 MIM + 几何

| 工作 | 会议/年份 | 与 VGGT+MAE 的关系 |
|------|-----------|-------------------|
| [GeoMIM](https://openaccess.thecvf.com/content/ICCV2023/html/Liu_GeoMIM_Towards_Better_3D_Knowledge_Transfer_via_Masked_Image_Modeling_ICCV_2023_paper.html) | ICCV 2023 | 多相机 MIM；语义特征 + **depth** 分支；LiDAR BEV 知识蒸馏；面向 **BEV 检测**，非 feed-forward scene recon foundation |
| [CroCo-Man](https://europe.naverlabs.com/research/3d-foundation-models/) | CVPR 2024 | CroCo 扩展到人体跨视角/跨姿态 completion |
| [POMA-3D](https://arxiv.org/abs/2511.16567) | arXiv 2025 | 在 **pointmap** 上做 JEPA 式 mask 表征学习；用 **VGGT** 从图像造单视图 pointmap 数据；偏 3D scene understanding / VL，不是 RGB multi-view MAE→VGGT |
| [Video-GMAE](https://videogmae.org/) | CVPR 2026 | 视频 MAE：解码 **运动 3D Gaussian**，渲染重建；零样本 tracking；偏 video SSL / 4D 对应，非 VGGT 式多视图几何头 |
| [M³3D](https://arxiv.org/abs/2309.15313) | 2023 | RGB-D 多模态 MAE，学 3D prior 服务 2D/视频理解 |


## 4. 对比表

| 方法 | Pretrain 目标 | 直接预测 3D？ | 视图数 | 角色 |
|------|---------------|--------------|--------|------|
| MAE | 单图 RGB 重建 | ✗ | 1 | 语义 VFM |
| CroCo / v2 | 跨视角 RGB 重建 | 间接 | 2 | 3D 友好预训练 |
| GeoMIM | 特征 + depth（+BEV） | 部分 | 多相机 | 检测预训练 |
| **Muskie** | 多视图 RGB 重建 | 间接 | 多视图 | **3D backbone** |
| **MuM** | 任意视图 RGB 重建 | 间接（下游可接几何头） | **任意 N** | **3D backbone**；下游 VGGT-style |
| DUSt3R / MASt3R | pointmap（监督） | ✓ | 2（+后处理） | 几何预测 |
| **VGGT** | camera/D/P/tracks（监督） | ✓ | **任意 N** | 几何预测 foundation |
| POMA-3D | pointmap JEPA + VL | 表征层 | — | 理解；用 VGGT 造数据 |
| Video-GMAE | 掩码视频→运动 Gaussian | 隐式 4D | 时序 | 跟踪 / video SSL |

**严格「VGGT 架构 + MAE loss」一体模型：未见公开论文。**


## 5. 研究空白（可做方向）

当前缺口不是「再做一个 multi-view MAE」，而是：

### 5.1 Geometry-aware masked modeling on VGGT outputs

不只重建 RGB，还重建被 mask 的 **depth / pointmap / correspondence / camera**：

```text
I_{1:T}  --spatio-temporal mask-->  VGGT-like encoder
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
               RGB decoder      Depth decoder    Pointmap / Track decoder
```

目标从「补图像洞」变成「补 3D world state」。

### 5.2 4D / streaming 版

结合动态重建（见 `4drecon_tracking.md`）：

- mask：空间 patch / 整帧 / 时间段 / 特定轨迹点  
- 恢复：\(\hat D_t,\,\hat P_t,\,\hat T_t\) 甚至 \(\hat P_{t+\Delta}\)  
≈ **VideoMAE + VGGT + 4D recon / world model**

MuM/Muskie 已把「多视图 + MAE + 几何」做扎实；**动态时空 masked geometric foundation** 仍空。


## 6. 速读清单

1. **CroCo** — 为何跨视角 mask 能学 3D  
2. **CroCo v2 / DUSt3R** — MAE 预训练如何接到几何监督  
3. **VGGT** — 多视图几何预测 foundation 的架构与监督  
4. **Muskie** — native multi-view + MIM → pose / pointmap  
5. **MuM** — 任意视图 MAE；下游 VGGT-inspired recon（**优先**）  
6. **GeoMIM / POMA-3D / Video-GMAE** — 旁支对照（检测 / pointmap JEPA / 4D Gaussian MAE）


## 7. 与本仓库兴趣的衔接

| 兴趣 | 可挂钩工作 |
|------|------------|
| 静态多视图 feed-forward 重建 | MuM encoder → VGGT-style heads；对照 VGGT 全监督 |
| 动态 / streaming 4D | Muskie/MuM 仍偏静态多视图；Video-GMAE 偏 tracking；**时空 mask + pointmap/track 重建仍缺** |
| 全景 ERP | 上述工作几乎都是透视；全景版 multi-view MAE / VGGT 见 `pano_3drecon.md`（PanoVGGT 等），**尚无「Pano-MuM」公开工作** |

相关笔记：`4drecon_tracking.md`（DUSt3R 系动态）、`pano_3drecon.md`（全景几何基础模型）。
