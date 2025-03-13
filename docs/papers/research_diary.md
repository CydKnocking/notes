---
password: password
---

# Research diary

## 2024

### 0704

- 用stable diffusion做finetune，可以用低开销和不多的数据集做finetune。

- 做depth的：Repurposing Diffusion-Based Image Generators for Monocular Depth Estimation (CVPR 2024)，可以从里面借鉴conditional的用法，以及如何把depth image转换到适合diffusion的框架；做dense matching的：DIFFUSION MODEL FOR DENSE MATCHING (ICLR 2024)，他用两张图的global cost作为condition，但是框架设计上还是有点暴力。

### 0705

- DOT（Matching 2D Images in 3D: Metric Relative Pose from Metric Correspondences）为啥比RAFT和CoTracker效果还好？DOT的实验设计和故事是怎么讲的，值得看一看。

### 0706

- 用covariance建模point tracks之间的关联性？
  
  三个好处：鲁棒（从图像中对点做track，学的是$\delta I$；而学习track之间的covariance，学的是$\delta I$整体的分布特性）；高效（减轻数据冗余和学习负担，可以用少量的稳定的点，表达整张图里其他点的运动趋势，同时也可以表达相机的运动趋势）；可以做预测（学到的covariance可以用作预测point在下一帧里的移动）
  
  数学方法上参考Learning a Depth Covariance Function，看看他怎么进行的随机过程建模
  
  坏处：那这样就要讲point track的故事了？不管是point tracking还是optical flow，都非常关注动态物体。那要做动态物体？

- 考虑用covariance function做optical flow？还是做keypoint matching？

- Image encoder可以考虑用预训练的DIVOv2。

- 如果做covariance function+optical flow，那难点就在于：depth covariance function是用的UNet cnn网络，RAFT用的是GRU，这个怎么调通。

### 0708

- dust3r：能否做到online，能否做到sparse

### 0729

- rotation-invariant PPF (RIGA: Rotation-Invariant and Globally-Aware Descriptors for Point Cloud Registration sec3.2).

### 0731

- SuperPoint + Co-Tracker + COTR ?

### 0810

- COTR takes too much time... Consider using LoFTR/LightGlue?

### 0824

ECCV24 相关的论文

- Grounding Image Matching in 3D with MASt3R (NAVER LABS Europe)
- **Learning to Make Keypoints Sub-Pixel Accurate** (Marc Pollefeys Group)
- X-Pose: Detecting Any Keypoints
- SRPose: Two-view Relative Pose Estimation with Sparse Keypoints


## 2025

### 0110

从Scholar Inbox上找了2024的和VO相关的文章。简单做个笔记。

- [MambaVO: Deep Visual Odometry Based on Sequential Matching Refinement and Training Smoothing](https://arxiv.org/pdf/2412.20082)  
  用manba做VO，有纯VO版和加了回环的两个版本。用Mamba加强matching，做更好的初始化。
- [RoMeO: Robust Metric Visual Odometry](https://arxiv.org/pdf/2412.11530)  
  DPVO加了metric，主要是用了带metric的预训练网络来估计depth。
- [**Leveraging Consistent Spatio-Temporal Correspondence for Robust Visual Odometry**](https://arxiv.org/pdf/2412.16923)  
  在droid-vo上加了时序连续性，用depthanything v2加入了空间约束。
- [KeyGS: A Keyframe-Centric Gaussian Splatting Method for Monocular Image Sequences](https://arxiv.org/pdf/2412.20767)  
  在video上做，SfM+3dgs，并同时优化相机位姿和地图。
- [SCENES: Subpixel Correspondence Estimation With Epipolar Supervision](https://arxiv.org/pdf/2401.10886)  
  matching的模型在新的数据集上做finetune，只需要pose提供epipolar line，loss指导匹配的点朝epipolar line靠近就行。
- [YOLOPoint: Joint Keypoint and Object Detection](https://arxiv.org/pdf/2402.03989)  
  把YOLOv5和SuperPoint网络结合，可以实时的同时检测keypoints和objects（low-level和high-level特征）
- [Incorporating Point Uncertainty in Radar SLAM](https://arxiv.org/pdf/2402.16082)  
- [VOOM: Robust Visual Object Odometry and Mapping using Hierarchical Landmarks](https://arxiv.org/pdf/2402.13609)  
  视觉-物体slam，用了high-level objects和low-level points作为多层次的landmarks。
- [Compact 3D Gaussian Splatting for Dense Visual SLAM](https://arxiv.org/pdf/2403.11247)  
  RGBD+3dgs SLAM。
- [CodedVO: Coded Visual Odometry](https://arxiv.org/pdf/2407.18240)  
  发表在RAL。用了特殊的光学元件把带scale的深度信息给编码到image中。
- [SCIPaD: Incorporating Spatial Clues into Unsupervised Pose-Depth Joint Learning](https://arxiv.org/pdf/2407.05283)  
  非监督学depth和pose，为了解决动态物体，用了带confidence的optical flow作引导。
- [Self-supervised Pretraining and Finetuning for Monocular Depth and Visual Odometry](https://arxiv.org/pdf/2406.11019)  
  自监督学depth和pose，用了在cross-view completion objective上学习的pretrained的模型，再finetune到无标注的数据上。
- [Self-Supervised Geometry-Guided Initialization for Robust Monocular Visual Odometry](https://arxiv.org/pdf/2406.00929)  
  自监督VO，主要解决自动驾驶场景（driod-slam表现很差）的动态物体、高速行驶、急转弯等表现不好的问题。用了个frozen large-scale pre-trained单目深度估计的网络，来初始化BA的深度。
- [TAMBRIDGE: Bridging Frame-Centered Tracking and 3D Gaussian Splatting for Enhanced SLAM](https://arxiv.org/pdf/2405.19614)  
  应对传感器噪声，运动模糊，长时slam。缝了ORB VO和online 3dgs。
- [MGS-SLAM: Monocular Sparse Tracking and Gaussian Mapping with Depth Smooth Regularization](https://arxiv.org/pdf/2405.06241)  
  稀疏VO，用关键帧做fast MVS用以稠密3DGS。
- [**Multi-Session SLAM with Differentiable Wide-Baseline Pose Optimization**](https://openaccess.thecvf.com//content/CVPR2024/papers/Lipson_Multi-Session_SLAM_with_Differentiable_Wide-Baseline_Pose_Optimization_CVPR_2024_paper.pdf)  
  普林斯顿Jia Deng组的，multi-session slam。可以考虑把已有的框架给扩成multi-session的。可以了解一下multi-session的设定。相关文章[Asynchronous Multi-View SLAM](https://arxiv.org/pdf/2101.06562) ICRA2021
- [**Matching 2D Images in 3D: Metric Relative Pose from Metric Correspondences**](https://openaccess.thecvf.com//content/CVPR2024/papers/Barroso-Laguna_Matching_2D_Images_in_3D_Metric_Relative_Pose_from_Metric_CVPR_2024_paper.pdf)  
  把2d-2d的匹配给拓展到了加入3d metric，可以出带metric的相对位姿。
- [**Salient Sparse Visual Odometry with Pose-only Supervision**](https://arxiv.org/pdf/2404.04677)  
  RAL的文章，在DPVO基础上改的，用自监督的光流引导选择稳定的特征点。
- [Incremental Joint Learning of Depth, Pose and Implicit Scene Representation on Monocular Camera in Large-scale Scenes](https://arxiv.org/pdf/2404.06050)  
  NeRF slam，video的增量式构建nerf。

以下的需整理：

- [InCrowd-VI: A Realistic Visual-Inertial Dataset for Evaluating SLAM in Indoor Pedestrian-Rich Spaces for Human Navigation](https://arxiv.org/pdf/2411.14358)  
- [**MPVO: Motion-Prior based Visual Odometry for PointGoal Navigation**](https://arxiv.org/pdf/2411.04796)  
- [Enhanced Monocular Visual Odometry with AR Poses and Integrated INS-GPS for Robust Localization in Urban Environments](https://arxiv.org/pdf/2411.08231)  
- [BEV-ODOM: Reducing Scale Drift in Monocular Visual Odometry with BEV Representation](https://arxiv.org/pdf/2411.10195)  
- [MAC-VO: Metrics-aware Covariance for Learning-based Stereo Visual Odometry](https://arxiv.org/pdf/2409.09479)  
- [ORB-SfMLearner: ORB-Guided Self-supervised Visual Odometry with Selective Online Adaptation](https://arxiv.org/pdf/2409.11692)  
- [GEVO: Memory-Efficient Monocular Visual Odometry Using Gaussians](https://arxiv.org/pdf/2409.09295)  
- [Panoramic Direct LiDAR-assisted Visual Odometry](https://arxiv.org/pdf/2409.09287)  
- [Deep Patch Visual SLAM](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/00272.pdf)  
- [Str-L Pose: Integrating Point and Structured Line for Relative Pose Estimation in Dual-Graph](https://arxiv.org/pdf/2408.15750)  
- [Towards Real-Time Gaussian Splatting: Accelerating 3DGS through Photometric SLAM](https://arxiv.org/pdf/2408.03825)  
- [Correspondence-Free SE(3) Point Cloud Registration in RKHS via Unsupervised Equivariant Learning](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/12030.pdf)  
- [GLIM: 3D Range-Inertial Localization and Mapping with GPU-Accelerated Scan Matching Factors](https://arxiv.org/pdf/2407.10344)  
- [Semi-Supervised Pipe Video Temporal Defect Interval Localization](https://arxiv.org/pdf/2407.15170)  
- [Attenuation-Aware Weighted Optical Flow with Medium Transmission Map for Learning-based Visual Odometry in Underwater terrain](https://arxiv.org/pdf/2407.13159)  
- [Robust Monocular Visual Odometry using Curriculum Learning](https://arxiv.org/pdf/2411.13438)  


### 0203

- [Dense-SfM: Structure from Motion with Dense Consistent Matching](https://arxiv.org/pdf/2501.14277)  
  2025/1挂在arxiv，看上去像是投cvpr的。稠密、多帧SfM，用了3DGS帮助做多帧的匹配。先初始化一个SfM和一个高斯，然后优化高斯+进行稠密化，从高斯中将SfM的3D点给投影到新的帧，建立新的match关系，最后再用网络对点的tracks进行refinement，用BA得到refined SfM。  
  可以学学：怎么结合GS做的track extension；可以参考track refinement的网络设计。  
  没开源。  
  可以从这篇了解一下sfm的几类方法：detector-based(colmap, pixsfm etc.), semi-dense matching(detector-free)(LoFTR/AspanTrans/MatchFormer + PixSfM/DFSfM), dense matching(RoMa/DKM + DFSfM/ours)，同时顺便可以了解匹配的方法。

### 0301

- [MambaGlue: Fast and Robust Local Feature Matching With Mamba](https://arxiv.org/pdf/2502.00462)    
  核心设计了MambaAttention，一种基于mamba的self-attention层。提高了运行效率。

### 0313 CVPR'25




