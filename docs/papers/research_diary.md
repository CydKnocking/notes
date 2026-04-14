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

- [MambaVO: Deep Visual Odometry Based on Sequential Matching Refinement and Training Smoothing](https://arxiv.org/pdf/2412.20082)<br>
  用manba做VO，有纯VO版和加了回环的两个版本。用Mamba加强matching，做更好的初始化。
- [RoMeO: Robust Metric Visual Odometry](https://arxiv.org/pdf/2412.11530)<br>
  DPVO加了metric，主要是用了带metric的预训练网络来估计depth。
- [**Leveraging Consistent Spatio-Temporal Correspondence for Robust Visual Odometry**](https://arxiv.org/pdf/2412.16923)<br>
  在droid-vo上加了时序连续性，用depthanything v2加入了空间约束。
- [KeyGS: A Keyframe-Centric Gaussian Splatting Method for Monocular Image Sequences](https://arxiv.org/pdf/2412.20767)<br>
  在video上做，SfM+3dgs，并同时优化相机位姿和地图。
- [SCENES: Subpixel Correspondence Estimation With Epipolar Supervision](https://arxiv.org/pdf/2401.10886)<br>
  matching的模型在新的数据集上做finetune，只需要pose提供epipolar line，loss指导匹配的点朝epipolar line靠近就行。
- [YOLOPoint: Joint Keypoint and Object Detection](https://arxiv.org/pdf/2402.03989)<br>
  把YOLOv5和SuperPoint网络结合，可以实时的同时检测keypoints和objects（low-level和high-level特征）
- [Incorporating Point Uncertainty in Radar SLAM](https://arxiv.org/pdf/2402.16082)<br>
- [VOOM: Robust Visual Object Odometry and Mapping using Hierarchical Landmarks](https://arxiv.org/pdf/2402.13609)<br>
  视觉-物体slam，用了high-level objects和low-level points作为多层次的landmarks。
- [Compact 3D Gaussian Splatting for Dense Visual SLAM](https://arxiv.org/pdf/2403.11247)<br>
  RGBD+3dgs SLAM。
- [CodedVO: Coded Visual Odometry](https://arxiv.org/pdf/2407.18240)<br>
  发表在RAL。用了特殊的光学元件把带scale的深度信息给编码到image中。
- [SCIPaD: Incorporating Spatial Clues into Unsupervised Pose-Depth Joint Learning](https://arxiv.org/pdf/2407.05283)<br>
  非监督学depth和pose，为了解决动态物体，用了带confidence的optical flow作引导。
- [Self-supervised Pretraining and Finetuning for Monocular Depth and Visual Odometry](https://arxiv.org/pdf/2406.11019)<br>
  自监督学depth和pose，用了在cross-view completion objective上学习的pretrained的模型，再finetune到无标注的数据上。
- [Self-Supervised Geometry-Guided Initialization for Robust Monocular Visual Odometry](https://arxiv.org/pdf/2406.00929)<br>
  自监督VO，主要解决自动驾驶场景（driod-slam表现很差）的动态物体、高速行驶、急转弯等表现不好的问题。用了个frozen large-scale pre-trained单目深度估计的网络，来初始化BA的深度。
- [TAMBRIDGE: Bridging Frame-Centered Tracking and 3D Gaussian Splatting for Enhanced SLAM](https://arxiv.org/pdf/2405.19614)<br>
  应对传感器噪声，运动模糊，长时slam。缝了ORB VO和online 3dgs。
- [MGS-SLAM: Monocular Sparse Tracking and Gaussian Mapping with Depth Smooth Regularization](https://arxiv.org/pdf/2405.06241)<br>
  稀疏VO，用关键帧做fast MVS用以稠密3DGS。
- [**Multi-Session SLAM with Differentiable Wide-Baseline Pose Optimization**](https://openaccess.thecvf.com//content/CVPR2024/papers/Lipson_Multi-Session_SLAM_with_Differentiable_Wide-Baseline_Pose_Optimization_CVPR_2024_paper.pdf)<br>
  普林斯顿Jia Deng组的，multi-session slam。可以考虑把已有的框架给扩成multi-session的。可以了解一下multi-session的设定。相关文章[Asynchronous Multi-View SLAM](https://arxiv.org/pdf/2101.06562) ICRA2021
- [**Matching 2D Images in 3D: Metric Relative Pose from Metric Correspondences**](https://openaccess.thecvf.com//content/CVPR2024/papers/Barroso-Laguna_Matching_2D_Images_in_3D_Metric_Relative_Pose_from_Metric_CVPR_2024_paper.pdf)<br>
  把2d-2d的匹配给拓展到了加入3d metric，可以出带metric的相对位姿。
- [**Salient Sparse Visual Odometry with Pose-only Supervision**](https://arxiv.org/pdf/2404.04677)<br>
  RAL的文章，在DPVO基础上改的，用自监督的光流引导选择稳定的特征点。
- [Incremental Joint Learning of Depth, Pose and Implicit Scene Representation on Monocular Camera in Large-scale Scenes](https://arxiv.org/pdf/2404.06050)<br>
  NeRF slam，video的增量式构建nerf。

以下的需整理：

- [InCrowd-VI: A Realistic Visual-Inertial Dataset for Evaluating SLAM in Indoor Pedestrian-Rich Spaces for Human Navigation](https://arxiv.org/pdf/2411.14358)<br>
- [**MPVO: Motion-Prior based Visual Odometry for PointGoal Navigation**](https://arxiv.org/pdf/2411.04796)<br>
- [Enhanced Monocular Visual Odometry with AR Poses and Integrated INS-GPS for Robust Localization in Urban Environments](https://arxiv.org/pdf/2411.08231)<br>
- [BEV-ODOM: Reducing Scale Drift in Monocular Visual Odometry with BEV Representation](https://arxiv.org/pdf/2411.10195)<br>
- [MAC-VO: Metrics-aware Covariance for Learning-based Stereo Visual Odometry](https://arxiv.org/pdf/2409.09479)<br>
- [ORB-SfMLearner: ORB-Guided Self-supervised Visual Odometry with Selective Online Adaptation](https://arxiv.org/pdf/2409.11692)<br>
- [GEVO: Memory-Efficient Monocular Visual Odometry Using Gaussians](https://arxiv.org/pdf/2409.09295)<br>
- [Panoramic Direct LiDAR-assisted Visual Odometry](https://arxiv.org/pdf/2409.09287)<br>
- [Deep Patch Visual SLAM](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/00272.pdf)<br>
- [Str-L Pose: Integrating Point and Structured Line for Relative Pose Estimation in Dual-Graph](https://arxiv.org/pdf/2408.15750)<br>
- [Towards Real-Time Gaussian Splatting: Accelerating 3DGS through Photometric SLAM](https://arxiv.org/pdf/2408.03825)<br>
- [Correspondence-Free SE(3) Point Cloud Registration in RKHS via Unsupervised Equivariant Learning](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/12030.pdf)<br>
- [GLIM: 3D Range-Inertial Localization and Mapping with GPU-Accelerated Scan Matching Factors](https://arxiv.org/pdf/2407.10344)<br>
- [Semi-Supervised Pipe Video Temporal Defect Interval Localization](https://arxiv.org/pdf/2407.15170)<br>
- [Attenuation-Aware Weighted Optical Flow with Medium Transmission Map for Learning-based Visual Odometry in Underwater terrain](https://arxiv.org/pdf/2407.13159)<br>
- [Robust Monocular Visual Odometry using Curriculum Learning](https://arxiv.org/pdf/2411.13438)<br>


### 0203

- [Dense-SfM: Structure from Motion with Dense Consistent Matching](https://arxiv.org/pdf/2501.14277)<br>
  2025/1挂在arxiv，看上去像是投cvpr的。稠密、多帧SfM，用了3DGS帮助做多帧的匹配。先初始化一个SfM和一个高斯，然后优化高斯+进行稠密化，从高斯中将SfM的3D点给投影到新的帧，建立新的match关系，最后再用网络对点的tracks进行refinement，用BA得到refined SfM。<br>
  可以学学：怎么结合GS做的track extension；可以参考track refinement的网络设计。<br>
  没开源。<br>
  可以从这篇了解一下sfm的几类方法：detector-based(colmap, pixsfm etc.), semi-dense matching(detector-free)(LoFTR/AspanTrans/MatchFormer + PixSfM/DFSfM), dense matching(RoMa/DKM + DFSfM/ours)，同时顺便可以了解匹配的方法。

### 0301

- [MambaGlue: Fast and Robust Local Feature Matching With Mamba](https://arxiv.org/pdf/2502.00462)<br>
  核心设计了MambaAttention，一种基于mamba的self-attention层。提高了运行效率。

### 0313 CVPR'25

#### SLAM相关

- [MAGiC-SLAM: Multi-Agent Gaussian Globally Consistent SLAM](https://arxiv.org/pdf/2411.16785)<br>
  多智能体3dgs SLAM。
- [MNE-SLAM: Multi-Agent Neural SLAM for Mobile Robots]()<br>
- [SLAM3R: Real-Time Dense Scene Reconstruction from Monocular RGB Videos](https://www.arxiv.org/pdf/2412.09401)<br>
  陈宝权老师组的工作。把DUSt3R扩展成了SLAM。主要用sliding window构建submap，然后做对齐。
- [MASt3R-SLAM: Real-Time Dense SLAM with 3D Reconstruction Priors]()

#### 其他

- [**VGGT: Visual Geometry Grounded Transformer**](https://www.arxiv.org/pdf/2503.11651)<br>
  feed-forward network，同时对任意数量的图像输入，输出相机参数、点云、深度图、3D点跟踪。在64张A100上训练9天。<br>
  用tapvid_davis的一些序列测了下，failure case有soapbox, scooter-black, pigs, parkour, motocross-jump, mbike-trick等<br>
  还行的序列loading, libby等<br>

  不能有效的去除动态物体的影响，对于一些非结构化场景（野外等）重建不好，对于像parkour这样还算有结构的，但无纹理较大，视角转动较大的重建得也不好。<br>
  感觉对于视角转动过大的，重建效果都不太好。<br>
  对于室外场景，当包含一些深度较远的部分，效果不好。

- [**MATCHA: Towards Matching Anything**](https://arxiv.org/pdf/2501.14945)<br>
  提出了一种统一的“融合了几何特征、语义特征、对象特征”的视觉特征，在几何匹配、语义匹配、点的时序tracking任务上表较好。主要基于了DIFT和DINOv2这两个工作。<br>
  回头读一下：当前视觉特征的相关工作，matching相关的（几何、语义）、point tracking、以及视觉基础模型。


### 0422

- [**TAPIP3D: Tracking Any Point in Persistent 3D Geometry**](https://www.arxiv.org/abs/2504.14717v1)<br>
  把图像的2d特征unproject成3d特征云，在特征云上用knn做attention。用了Moge做depth estimator，MegaSaM估计相机内外参。point tracks的iterative更新参考了CoTracker3。<br>
  在3d点云上取knn比较慢，可以优化(比如参考MASt3R-SLAM的优化方法？)<br>

### 0423

- [**Back on Track: Bundle Adjustment for Dynamic Scene Reconstruction**](https://arxiv.org/pdf/2504.14516)<br>
  LEAP-VO作者的新作，继续用TAP做动态VO。用了depth估计网络(ZoeDepth)，对于动态物体上的point在估计track时，多估计了一个dynamic motion，把动态物体的track给解耦/恢复成静态场景的track。，再结合深度做BA。<br>
- [**Relative Pose Estimation through Affine Corrections of Monocular Depth Priors**](https://www.arxiv.org/pdf/2501.05446)<br>
  CVPR2025 highlight<br>
  当前深度估计模型，在使用的时候仅仅考虑了scale factor，没考虑shift factor。所以这篇文章提出在求解/匹配的时候，同时要考虑scale和shift factor。这个想法或许不是它第一个提出的，但是它用这个想法设计了几种情况下的求解器（calibrated和uncalibrated等）<br>
  （这篇文章说）这个问题应该是由训练时的损失函数设计问题引入的。<br>
  之前的工作，比如MonoSDF中，设计的depth估计网络其实就是affine invariant的。<br>

### 0503

单目动态场景4d重建相关:

- [**MegaSaM: Accurate, Fast and Robust Structure and Motion from Casual Dynamic Videos**](https://mega-sam.github.io/)<br>
  在大量数据上训练，对任意动态视频进行重建+相机位姿估计。<br>
  cvpr2025 best paper。<br>
- [**TAPIP3D: Tracking Any Point in Persistent 3D Geometry**](https://www.arxiv.org/abs/2504.14717v1)<br>
  把图像的2d特征unproject成3d特征云，在特征云上用knn做attention。用了Moge做depth estimator，MegaSaM估计相机内外参。point tracks的iterative更新参考了CoTracker3。<br>
  在3d点云上取knn比较慢，可以优化(比如参考MASt3R-SLAM的优化方法？)<br>
  效果看上去还行，

### 0614

Point tracking in CVPR2025

- [GS-DiT: Advancing Video Generation with Dynamic 3D Gaussian Fields through Efficient Dense 3D Point Tracking](https://arxiv.org/pdf/2501.02690)
- [Exploring Temporally-Aware Features for Point Tracking](https://arxiv.org/pdf/2501.12218)<br>
  一个针对point tracking问题改进的DIVOv2网络，可以聚合时序的feature，得到的feature可以直接拿来算correlation map。<br>
- [Tracktention: Leveraging Point Tracking to Attend Videos Faster and Better](https://arxiv.org/pdf/2503.19904)
- [TimeTracker: Event-based Continuous Point Tracking for Video Frame Interpolation with Non-linear Motion](https://arxiv.org/pdf/2505.03116)


### 0628

- [LiVOS: Light Video Object Segmentation with Gated Linear Matching](https://www.alphaxiv.org/abs/2411.02818v1)<br>
  视频物体分割。改进了空间-时间记忆网络（STM），其中用linear matching替代了传统stm中的softmax；同时引入了gated linear matching机制。<br>
  网络结构和改动思路可以参考一下。
- [MINIMA: Modality Invariant Image Matching](https://arxiv.org/abs/2412.19412)<br>
  多模态图像匹配。用了一个生成模型去生成多模态图像，提出了一套框架可以微调loftr/lightglue等稀疏/半稀疏/稠密方法。开源的。<br>
  和薛飞的matcha考虑的任务类似，但是思路不同。<br>


### 0703

要不要试试track-on做vo，解决纯旋转问题？场景是头戴式设备，数据集是egopoints或者epic-fields。

https://data.bris.ac.uk/data/dataset/3l8eci2oqgst92n14w2yqi5ytu<br>
https://data.bris.ac.uk/data/dataset/3h91syskeag572hl6tvuovwv4d<br>
https://epic-kitchens.github.io/2025<br>

纯旋转相关的文章：

- [Equivalent Constraints for Two-View Geometry: Pose Solution/Pure Rotation Identification and 3D Reconstruction](https://arxiv.org/pdf/1810.05863v1)<br>
  2019年的文章<br>
- [RD-VIO: Robust Visual-Inertial Odometry for Mobile Augmented Reality in Dynamic Environments](https://www.alphaxiv.org/html/2310.15072v3)<br>
  24年的文章，章国峰老师组的。对于视觉有纯旋转判定+延迟三角化的操作，可以参考一下。


### 0705

找一下头戴相机/vr/ar之类的数据集

- epic-fields
- [WHU-Helmet Dataset](https://github.com/kafeiyin00/WHU-HelmetDataset?tab=readme-ov-file)
- [Aria系列](https://www.projectaria.com/datasets/aea/)
- [Roller Coaster SLAM Dataset](https://github.com/Factor-Robotics/Roller-Coaster-SLAM-Dataset)
- [SimXR](https://arxiv.org/pdf/2403.06862v1)
- [ADVIO](https://github.com/AaltoVision/ADVIO)<br>
  DPVO在advio_01序列上很差，这个序列中间有一段坐电梯，画面中只有扶梯台阶，dpvo以为相机没有移动，实际上在上升。<br>
  python demo.py --imagedir="/media/knocking/Expansion/datasets/advio/advio-01/iphone/frames.mov" --calib="/media/knocking/Expansion/datasets/advio/ADVIO/calibration/iphone-02.txt" --name advio_01 --viz --save_trajectory <br>
- [TUM-VIE](https://cvg.cit.tum.de/data/datasets/visual-inertial-event-dataset)<br>
  DPVO在running-hard序列上很差，这个序列运动模糊很多，人拿着相机跑得很快。<br>
  python demo.py --imagedir /media/knocking/Expansion/datasets/TUM_VIE/running-hard-vi_gt_data/left_images --calib /media/knocking/Expansion/datasets/TUM_VIE/calibB_left_1024x1024.txt --name "running-hard" --viz --save_trajectory <br>
  track-on在运动极度模糊的情况下也很差，以及在这种场景下如何选择query需要好好选一下。


### 0716

[ICCV'25 paperlist](https://iccv.thecvf.com/Conferences/2025/AcceptedPapers)

**Track相关：**

- [BlinkTrack: Feature Tracking over 80 FPS via Events and Images](https://arxiv.org/pdf/2409.17981)
- A Linear N-Point Solver for Structure and Motion from Asynchronous Tracks
- [SpatialTrackerV2: Advancing 3D Point Tracking with Explicit Camera Motion](https://arxiv.org/pdf/2507.12462)
- [Tracking Tiny Drones against Clutter: Large-Scale Infrared Benchmark with Motion-Centric Adaptive Algorithm]
- [Language Decoupling with Fine-grained Knowledge Guidance for Referring Multi-object Tracking]
- [GSOT3D: Towards Generic 3D Single Object Tracking in the Wild](https://arxiv.org/pdf/2412.02129)
- [Is Tracking really more challenging in First Person Egocentric Vision?]
- [XTrack: Multimodal Training Boosts RGB-X Video Object Trackers](https://arxiv.org/pdf/2405.17773)
- LA-MOTR: End-to-End Multi-Object Tracking by Learnable Association
- MVTrajecter: Multi-View Pedestrian Tracking with Trajectory Motion Cost and Trajectory Appearance Cost
- [**Online Dense Point Tracking with Streaming Memory**](https://arxiv.org/pdf/2503.06471)<br>
  [github](https://github.com/DQiaole/SPOT)
- [**TrackAny3D: Transferring Pretrained 3D Models for Category-unified 3D Point Cloud Tracking**](http://www.cssclab.cn/downloadfile/2025/TrackAny3D_Transferring%20Pretrained%203D%20Models%20for%20Category-unified%203D%20Point%20Cloud%20Tracking.pdf)
- Inter Inertial Poser: Multi-Human Motion Tracking from Sparse Inertial Sensors and Pairwise Inter-Sensor Distances 
- SMSTracker: Tri-path Score Mask Sigma Fusion for Multi-Modal Tracking
- [St4RTrack: Simultaneous 4D Reconstruction and Tracking in the World](https://arxiv.org/pdf/2504.13152)
- [General Compression Framework for Efficient Transformer Object Tracking](https://arxiv.org/pdf/2409.17564)
- [Street Gaussians without 3D Object Tracker](https://arxiv.org/pdf/2412.05548)
- [Event-aided Dense and Continuous Point Tracking: Everywhere and Anytime](https://openreview.net/pdf?id=1GIVx7COef)
- [CoTracker3: Simpler and Better Point Tracking by Pseudo-Labelling Real Videos](https://arxiv.org/pdf/2410.11831)
- COVTrack: Continuous Open-Vocabulary Multi-Object Tracking via Adaptive Multi-Cue Fusion
- [UMDATrack: Unified Multi-Domain Adaptive Tracking Under Adverse Weather Conditions](https://arxiv.org/pdf/2507.00648)
- CAT: A Unified Click-and-Track Framework for Realistic Tracking
- [Attention to Trajectory: Trajectory-Aware Open-Vocabulary Tracking](https://arxiv.org/pdf/2503.08145)
- [What You Have is What You Track: Adaptive and Robust Multimodal Tracking]
- [Multi-View 3D Point Tracking](https://arxiv.org/pdf/2508.21060)
- MATE: Motion-Augmented Temporal Consistency for Event-based Point Tracking
- M$^2$EIT:Multi-Domain Mixture of Experts for Robust Neural Inertial Tracking
- [Efficient Track Anything](https://arxiv.org/pdf/2411.18933)<br>
  [github](https://github.com/yformer/EfficientTAM)<br>
- [AllTracker: Efficient Dense Point Tracking at High Resolution](https://arxiv.org/pdf/2506.07310)<br>
  [github.io](https://alltracker.github.io/)<br>
- ASCENT: Annotation-free Self-supervised Contrastive Embeddings for 3D Neuron Tracking in Fluorescence Microscopy
- [Temporal Unlearnable Examples: Preventing Personal Video Data from Unauthorized Exploitation by Object Tracking](https://arxiv.org/pdf/2507.07483)
- [VOVTrack: Exploring the Potentiality in Raw Videos for Open-Vocabulary Multi-Object Tracking](https://arxiv.org/pdf/2410.08529)
- [**Back on Track: Bundle Adjustment for Dynamic Scene Reconstruction**](https://arxiv.org/pdf/2504.14516)
- ReTracker: Exploring Image Matching for Robust Online Any Point Tracking
- [Decouple and Track: Benchmarking and Improving Video Diffusion Transformers For Motion Transfer](https://arxiv.org/pdf/2503.17350)
- [TrackVerse: A Large-scale Dataset of Object Tracks for Visual Representation Learning](https://github.com/MMPLab/TrackVerse)
- [TAPNext: Tracking Any Point (TAP) as Next Token Prediction](https://arxiv.org/pdf/2504.05579)
- [CoopTrack: Exploring End-to-End Learning for Efficient Cooperative Sequential Perception](https://github.com/zhongjiaru/CoopTrack)

**Odometry相关:**

- [Splat-LOAM: Gaussian Splatting LiDAR Odometry and Mapping](https://arxiv.org/pdf/2503.17491)

**SLAM相关：**

- [SuperEvent: Cross-Modal Learning of Event-based Keypoint Detection for SLAM](https://arxiv.org/pdf/2504.00139)
- [Outdoor Monocular SLAM with Global Scale-Consistent 3D Gaussian Pointmaps](https://arxiv.org/pdf/2507.03737)
- [SEGS-SLAM: Structure-enhanced 3D Gaussian Splatting SLAM with Appearance Embedding](https://segs-slam.github.io/)
- [DyGS-SLAM: Real-Time Accurate Localization and Gaussian Reconstruction for Dynamic Scenes]()
- [ToF-Splatting: Dense SLAM using Sparse Time-of-Flight Depth and Multi-Frame Integration](https://arxiv.org/pdf/2504.16545)
- [Benchmarking Egocentric Visual-Inertial SLAM at City Scale]()
- [4D Gaussian Splatting SLAM](https://arxiv.org/pdf/2503.16710)
- [Underwater Visual SLAM with Depth Uncertainty and Medium Modeling]()

**keypoint相关：**

- [RIPE: Reinforcement Learning on Unlabeled Image Pairs for Robust Keypoint Extraction](https://arxiv.org/pdf/2507.04839)
- SuperEvent: Cross-Modal Learning of Event-based Keypoint Detection for SLAM
- Towards Annotation-Free Evaluation: KPAScore for Human Keypoint Detection
- VoxelKP: A Voxel-based Network Architecture for Human Keypoint Estimation in LiDAR Data
- [ZeroKey: Point-Level Reasoning and Zero-Shot 3D Keypoint Detection from Large Language Models](https://arxiv.org/pdf/2412.06292)
- [ReassembleNet: Learnable Keypoints and Diffusion for 2D Fresco Reconstruction](https://arxiv.org/pdf/2505.21117)
- [Sequential keypoint density estimator: an overlooked baseline of skeleton-based video anomaly detection](https://arxiv.org/pdf/2506.18368)
- [Doodle Your Keypoints: Sketch-Based Few-Shot Keypoint Detection](https://arxiv.org/pdf/2507.07994)

**matching相关：**

- [Towards Open-World Generation of Stereo Images and Unsupervised Matching](https://arxiv.org/pdf/2503.12720)
- Focal Plane Visual Feature Generation and Matching on a Pixel Processor Array
- [Diving into the Fusion of Monocular Priors for Generalized Stereo Matching](https://arxiv.org/pdf/2505.14414)
- Partially Matching Submap Helps: Uncetainty Modeling and Propagation for Text to Point Cloud Localization
- [Learning Few-Step Diffusion Models by Trajectory Distribution Matching](https://arxiv.org/pdf/2503.06674)
- [MAVFlow: Preserving Paralinguistic Elements with Conditional Flow Matching for Zero-Shot AV2AV Multilingual Translation](https://arxiv.org/pdf/2503.11026)
- [RobuSTereo: Robust Zero-Shot Stereo Matching under Adverse Weather](https://arxiv.org/pdf/2507.01653v1)
- [EMatch: A Unified Framework for Event-based Optical Flow and Stereo Matching](https://arxiv.org/pdf/2407.21735)
- MDP-Omni: Parameter-free Multimodal Depth Prior-based Sampling for Omnidirectional Stereo Matching
- SGAD: Semantic and Geometric-aware Descriptor for Local Feature Matching
- [Learning Dense Feature Matching via Lifting Single 2D Image to 3D Space]()
- [BANet: Bilateral Aggregation Network for Mobile Stereo Matching](https://arxiv.org/pdf/2503.03259)
- [Learning Robust Stereo Matching in the Wild with Selective Mixture-of-Experts](https://arxiv.org/pdf/2507.04631)
- [**Stereo Any Video: Temporally Consistent Stereo Matching**](https://arxiv.org/pdf/2503.05549)
- [Global Regulation and Excitation via Attention Tuning for Stereo Matching]()
- [ZeroStereo: Zero-shot Stereo Matching from Single Images](https://github.com/Windsrain/ZeroStereo?tab=readme-ov-file)
- CasP: Improving Semi-Dense Feature Matching Pipeline Leveraging Cascaded Correspondence Priors for Guidance
- [POMATO: Marrying Pointmap Matching with Temporal Motions for Dynamic 3D Reconstruction](https://arxiv.org/pdf/2504.05692)
- [ArgMatch: Adaptive Refinement Gathering for Efficient Dense Matching]()
- [**CoMatch: Dynamic Covisibility-Aware Transformer for Bilateral Subpixel-Level Semi-Dense Image Matching**](https://arxiv.org/pdf/2503.23925)
- [**EDM: Efficient Deep Feature Matching**](https://arxiv.org/pdf/2503.05122)
- [**Mind the Gap: Aligning Vision Foundation Models to Image Feature Matching**](https://www.arxiv.org/pdf/2507.10318v1)
- [Fast Globally Optimal and Geometrically Consistent 3D Shape Matching](https://arxiv.org/pdf/2504.06385)
- ReTracker: Exploring Image Matching for Robust Online Any Point Tracking

### 0719

得看看IROS和ICRA的list

- [Self-supervised Pretraining and Finetuning for Monocular Depth and Visual Odometry](https://arxiv.org/pdf/2406.11019)
- [Self-Supervised Learning of Monocular Visual Odometry and Depth with Uncertainty-Aware Scale Consisten](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10610075)


### 0721

这个得看一下<br>

- [$\pi^3$: Scalable Permutation-Equivariant Visual Geometry Learnin](https://arxiv.org/pdf/2507.13347)<br>


### 0722

清华最近出了个StreamVGGT，好像是video输入范式/增量式的，可以看一下<br>

- [Streaming 4D Visual Geometry Transformer](https://arxiv.org/pdf/2507.11539), [主页](https://wzzheng.net/StreamVGGT/)<br>

这个组好像比较多online memory的文章，一作[Wenzhao Zheng的主页](https://wzzheng.net/)


### 0807

VLA的一个综述<br>

- [A Survey on Vision-Language-Action Models: An Action Tokenization Perspective](https://www.arxiv.org/pdf/2507.01925)


### 0901

- [Efficient Motion Prompt Learning for Robust Visual Tracking](https://www.arxiv.org/pdf/2505.16321v1)<br>
  里面关于空间位置编码和时间位置编码的小trick回头可以试试（Eq.(3)）。<br>


### 0904

#### [SpatialTrackerV2: 3D Point Tracking Made Easy](https://github.com/henry123-boy/SpaTrackerV2)

tag: `ICCV'25`, `3D`, `multi-view`

详细读一下SpatialTrackerv2的论文。

3. 估计查询点的3D轨迹$\mathcal{T}$时，将其分解成了相机运动$\mathcal{T}_{ego}$和物体运动$\mathcal{T}_{object}$两部分。<br>
   
   1. $\mathcal{T}_{ego}$
      
      初始的深度估计和相机运动：基于VGGT。
  
   2. 联合位姿优化
      
      提出**SyncFormer**，迭代地同时优化：UV空间的轨迹$\mathcal{T}^{2d}$；相机坐标系的轨迹$\mathcal{T}^{3d}$；可见度权重$p^{vis}$；动态权重$p^{dyn}$。相机的位姿$\mathcal{P}$用BA得到。

      2D embeddings和Cotracker3一样，3D embeddings包含3d相关性特征等。其中，3d相关性特征是在归一化point map中当前的点与邻居点的相对位移进行harmonic positional encoding得到的，并且在多分辨率上都进行了特征编码。

      SyncFormer调整完一轮$\mathcal{T}_{k+1}^{2d}, \mathcal{T}_{k+1}^{3d}, p_{k+1}^{dyn}, p_{k+1}^{vis}$后，通过Procrustes analysis对齐3d轨迹到世界坐标系，构建BA优化得到相机位姿$\mathcal{P}_{k+1}$。
    
   3. 训练

      在17个数据集上训练。（啊……好多😍好喜欢）分为三大类：带track gt, pose gt的RGB-D数据；带pose gt的RGB-D数据；仅有pose gt或无标注的。

      训练分三个阶段。一阶段，训练前端的网络（VGGT改的估计视频深度和初始相机位姿），64张H20。二阶段，训练SyncFormer，8张H20训3天。三阶段，固定前端网络中的交替注意力层，训整个框架。

4. 实验结果
   
   主要结果是在TAPIP-3D上对比3d tracking的精度。在3d point tracking上是sota。

   深度估计，在室内(tum dyn, bonn, sintel)和室外(kitti, sintel)含动态物体的数据集，比VGGT和MegaSam好（各有优劣）。

   相机位姿估计，在室内外（tum dyn, lightspeed, sintel），和MegaSam差不多。

   2D tracking也是SOTA。




#### Related works about point tracking

Refer to `papers/point_tracking`


### 1005

- [TTT3R: 3D RECONSTRUCTION AS TEST-TIME TRAINING](https://www.arxiv.org/pdf/2509.26645v1)
  
  解决长序列的动态重建问题。在transformer的权重更新里，给memory做更新时，加了个weight，使得每一步更新的量减少。
  
  栋爷说很trick，Cut3r是这篇文章主要对比的工作之一，cut3r是rnn式的，如果update次数过多，会忘记之前的东西（比如训练的时候是30次，但测试更长序列就不行），但是可以用关键帧的更新策略，对于长序列而言不用每步都更新，这种情况下cut3r也能跑下来。这篇文章里，它可以给更新量加很小的weight，也能达到“不忘记历史信息”的效果。

今日完成：

- [x] 用SpaTrackerV2原本的可视化，把tapvid-3d benchmark gt给可视化了。adt和pstudio基本是对的，drivetrack的外参处理不太对，回头再看看。以及tapvid-3d的depth感觉不太好啊，scale在飘，而且和tracked point的tracks有一点点合不上，可能是visualization的问题（里面对depth做了rescale）。


### 1006

**paper reading:**

- [Dense Optical Tracking: Connecting the Dots](https://www.alphaxiv.org/pdf/2312.00786)
  
  CVPR'24

  用tracker做稀疏追踪，然后做最邻近插值插出密集光流，然后再做光流优化。

  在CVO光流的benchmark，和TAP point tracking两个benchmark上对比。在TAP上，first模式的tracking和cotracker相当，strided模式下是sota。（*这个感觉可以理解，因为直观上光流对于构建长时tracking不如point tracking的方法*）

  选点策略：
  - 用一个预训练的光流模型先估计两帧的运动场，用Sobel filter监测运动边界
  - 50\%的点随机采样在运动边界附近5个px内，另一半在整个图像中随机采样。


**今日：**

- SpaTrackerV2的代码只给了demo，没有给training和evaluation，而这两部分有特别多的细节，不太好弄
- 3d tracker还没在EgoPoints这种长时（虽然2d）的benchmark上测过。

- TAPIP3D可以load npz进行inference:
  - video: (72, 480, 640, 3), uint8, 0, 255
  - intrinsics: (72, 3, 3), float32, 0.0, 615.357421875
  - extrinsics: (72, 4, 4), float32, 0.0, 1.0
  - depths: (72, 480, 640), float32, 0.0, 65.53500366210938

**明天TODO：**

- [ ] TAPIP3D感觉比较好follow，看看能不能在这上面搞定训练？
- [ ] 在EgoPoints这个benchmark上测一下？


### 1007

**今日：**

- EgoPoints没有相机位姿、内外参标注。


### 1008

**今日：**

SpaTrackerV2的对比实验，对于query点出画面又进画面的情况：
- 将视频中间的帧给删掉，只保留了开头和末尾query点都在画面里的片段。依然track不上。
- 不管是否删除中间的帧，前端VGGT给出的结果都是好的。位姿是后面track网络里优化过程中出错了。

- 把Pi3加到SpatialTrackerV2里了，正在测✌


### 1009

**今日：**

Track-On2出了，用了DINOv3做特征。
- track-on2代码搞定✌
- track-on2的训练集是cotracker3的kubric_movi_f (120 frames/seq)，和cotracker之前的kubric_movi_f不一样，以前是24帧的序列。在下载了。


### 1013

用到了memory的方法：
Spann3R, CUT3R, TTT3R, PreF3R


### 1014

1. St4RTrack的代码跑通了，但我的故事是否要用这个code base修改，还得再看看。
2. 如果只是为了target online 3d point tracking in ego-motion sequences，感觉可以用RGBD的输入（加一个zoedepth之类的），固定相机坐标系，不用那么纠结位姿的问题，只需要show online 3d tracking并且能处理ego-motion中点消失又出现的问题
   1. 要么也可以用3r来估计两帧的correspondences，利用这个结果来做re-identifying，同时也能得到depth和相对位姿。

Depth现在用了ZoeDepth，也可以用moge？


### 1015

飞哥严选：[WorldMirror: Universal 3D World Reconstruction with Any-Prior Prompting](https://www.arxiv.org/pdf/2510.10726)


### 1016

在往track-on2网络里的feature map里加一个3d的positional encoding。

其他工作的做法：
- [MBPTrack: Improving 3D Point Cloud Tracking with Memory Networks and Box Priors](https://openaccess.thecvf.com/content/ICCV2023/papers/Xu_MBPTrack_Improving_3D_Point_Cloud_Tracking_with_Memory_Networks_and_ICCV_2023_paper.pdf)<br>
  纯3d点云tracking的。只在attention层的query和key上，给coordinates加了positional embeddings.<br>
  它的前作是[CXTrack: Improving 3D Point Cloud Tracking with Contextual Information](https://www.arxiv.org/pdf/2211.08542)，也是这么做的。<br>
  不过这两篇文章本身的输入是3d点云，用的是DGCNN对点云进行的encoding。


### 1028

读读论文：
- [POMATO: Marrying Pointmap Matching with Temporal Motions for Dynamic 3D Reconstruction](https://www.alphaxiv.org/abs/2504.05692v2)
  ICCV'25，Dust3r网络改的。


### 1106

MapAnything在本地测试，512*512图像，6帧0.88秒重建，20帧1.79秒重建。


### 1109

在offset head上动动手脚，多加一些trajectory的/3d的信息作为输入：
- 考虑把2d/3d trajectory(的offset)给encode
- 要不要把camera pose / ray也给encode，或者把MapAnything的相应token给用起来

想起了eccv2022 SimpleRecon加metadata……
- feature dot product: 图像特征的相似度
- ray directions (normalized): 相机坐标系下的3d信息
- reference plane depth: 单目的3d信息
- reference frame reprojected depths
- relative ray angles: ray directions之间的角度
- relative pose distance: 目标帧和源帧之间的相机坐标距离
- depth validity masks


### 1111

Goal: 把tapvid-3d benchmark写进evaluation里
- [x] 加载tapvid-3d数据集
- [ ] 用mapanything给tapvid-3d生成depth等3d信息
- [x] 把2d结果给lift到3d
- [x] 测试

Goal: 在训练中加入3d的记忆和约束
- [x] 加载movi_f时，加载depth和extrinsics等信息
- [x] data augmentation on depth ...
- [ ] 把2d track正确投影到3d world coordinate
- [ ] 添加新的网络，处理3d的记忆


### 1117

Brain Storming

要学到point在3d空间中的运动和时空连续性，在方法/任务建模上尝试两个改动
1. 目前的3d point tracker网络输出是(x_t, y_t, z_t)，要预测运动，应该学到的是(dx, dy, dz)的信息。更进一步，可以从动力学的角度，学point运动的(direction, distance)。在此基础上，可以基于历史的(direction, distance)来修正当前帧的估计。
2. 可不可以把点在3d的运动给建模成分类+回归问题，比如用**存有若干个稀疏运动方向的codebook+refiner**这种框架来做。


### 1121

Brain Storming

预测confidence/uncertainty 改成 预测图像二维空间中的不确定性(2x2协方差矩阵)/世界三维空间中的不确定性(3x3协方差矩阵)。RoMa v2用了这个，在有运动模糊的情况下，误差在模糊的方向上可能更大。


### 1222

**3D fundamental models, tracking**

- [**DePT3R: Joint Dense Point Tracking and 3D Reconstruction of Dynamic Scenes in a Single Forward Pass**](https://arxiv.org/pdf/2512.13122)
  输入rgb视频，输出相机位姿、深度、点云、稠密3d点跟踪。<br>
  有链接，但未开源。<br>
  数值结果，稠密3d点跟踪和重建都很好。<br>

- [**Any4D: Unified Feed-Forward Metric 4D Reconstruction**](https://arxiv.org/pdf/2512.10935)
  CMU的工作。<br>
  输入：和MapAnything一样，RGB + 一堆可选输入（rays, pose, depth, doppler）<br>
  输出：metric + 相机位姿 + 几何（ray directions / predicted depth） + 场景流<br>
  
- [SyncTrack4D: Cross-Video Motion Alignment and Video Synchronization with Multi-Video 4D Gaussian Splatting](https://arxiv.org/pdf/2512.04315)
  输入：多视角的rgb视频(unsynchronized)，dinov3特征，2dtrack，2d光流，估计的/真值的pose+depth<br>
  输出：4DGS。<br>
  方法概述：一个多阶段的处理方法，1. 给每段视频单独搞出4d track，2. cross-video 4d track matching，3. 做synchronization，4. 优化一个统一的4dgs。<br>
  这是有了3d+track结果的后续工作。<br>
  
- [MV-TAP: Tracking Any Point in Multi-View Videos](https://arxiv.org/pdf/2512.02006)
  输入：多视角的rgb视频(synchronized)，query point<br>
  输出：2d的多视角tracks（没有深度没有3d）<br>
  方法：经典的co-tracker一样的iterative方法，不过有不同视角之间的cross-attention。中间有对不同camera视角的encoding（Plucker coordinates）。<br>
  结果还行，在主要的数据集上是sota，在附录里是comparable，比了2d和3d的方法。<br>

- [K-Track: Kalman-Enhanced Tracking for Accelerating Deep Point Trackers on Edge Devices](https://arxiv.org/pdf/2512.10628)
  目的：2d point tracking的加速。<br>
  方法：对关键帧用网络估计，对非关键帧用匀速模型+卡尔曼滤波。对点的位置+速度+不确定性（协方差矩阵）进行了建模，可能可以看看。<br>

- [Generative Video Motion Editing with 3D Point Tracks](https://arxiv.org/pdf/2512.02015)
  用源视频 + pose + 估计好的3d tracks做视频编辑，用的diffusion，3d track做的condition。<br>

- [Tracking-Guided 4D Generation: Foundation-Tracker Motion Priors for 3D Model Animation](https://arxiv.org/pdf/2512.06158)
  在diffusion的特征空间中做track（基于correspondence tracking loss），保持生成的一致性；改进了4dgs。<br>

- [Joint 3D Geometry Reconstruction and Motion Generation for 4D Synthesis from a Single Image](https://www.arxiv.org/pdf/2512.05044)
  生成的工作，从single image直接生成4d点云轨迹，来实现视频生成。<br>

- [Tracking Everything Everywhere across Multiple Cameras](https://ojs.aaai.org/index.php/AAAI/article/view/32839)
  **把Omnimotion给扩展到了多视角**，学习一个双射，把不同视角不同时间戳的像素点映射到一个统一的3d canonical space。这个双射可以自监督学习。<br>

- [DiTracker: Repurposing Video Diffusion Transformers for Robust Point Tracking](https://arxiv.org/pdf/2512.20606)

- [Look Around and Pay Attention: Multi-camera Point Tracking Reimagined with Transformers](https://arxiv.org/pdf/2512.04213)
  多视角point tracking（synchronized）。39fps。<br>


## 2026

### 0101

之前老颜说的[KV-Tracker: Real-Time Pose Tracking with Transformers](https://arxiv.org/pdf/2512.22581)是把pi^3改成stream模式的工作，核心是用了kv-cache。

读了Any4D，一些想法：
- 从测试效果看，动态区域的tracking不够平滑。是否考虑加入平滑项约束作为正则项进行微调？
- 静态区域理论上的scene flow应该是0，然而结果并不是。是否考虑加入静态区域的静止约束作为正则项？
- 作为以上两点的替代方案，如果暂时不能微调网络的话，是否给输出的结果加个后处理？

看了Any4D代码，TODO：
- [x] 改成stream的、基于window的输入，并且把前面已经处理过的帧的结果给再次扔进下一次处理(已经得到的ray_directions, depth_along_ray, cam_trans, cam_quats都可以复用)
- [ ] 把每个window的结果在世界坐标系下对齐（但是如果前面已经复制了cam_trans和cam_quats，那就已经是世界坐标系了？行吧，不太对。）
- [x] 试试把前面已经得到的scale token给继续复用？（其实scale token是训练阶段训好的，测试阶段不变了）

### 0102

跑了下Any4D代码：
- 在本地3090上
  - 显存原因最多只能跑42帧，且已经做了精度量化，花了2秒左右；
  - 25帧化1.1秒。
  - 欸但是改称window_based的处理方式后，windowsize=24，第一个window花了1.1s，后面都只花了0.
- 在服务器的A100-80G上
  - 92帧花52GB显存（应该是没做量化的，因为在40G卡上也能跑但是慢一些），花了3秒多。

发现的一些问题：
- 同一个batch的输出，每一帧的内参不一样，这个是否可以做约束


### 0103

需要被转换坐标的输出：
- pts3d
- cam_trans
- cam_quats
- scene_flow
- *camera_poses*

几个可以用的函数：
- transform_pts3d(pts3d, transformation)
- transform_pose_using_quats_and_trans_2_to_1(quats1, trans1, quats2, trans2)
- relative_pose_transformation(trans_01, trans_02)

Any4D输出的相机位姿T是cam2world，可以把世界坐标系的三维点给转换到相机坐标系中：P_cam = T @ P_world

不对！如果输入的是有intrinsics（ray map）的，输出的raymap依然会变，和输入不一样。


### 0127

V-DPM很慢。在本机（3090）上测，17帧25.78秒。相比之下，Any4D 20帧2秒。


### 0220

Vincent Sitzmann的博客文章：[The flavor of the bitter lesson for computer vision](https://www.vincentsitzmann.com/blog/bitter_lesson_of_cv/)，2026年2月1日。

Rich Sutton的博客文章：[The Bitter Lesson](http://www.incompleteideas.net/IncIdeas/BitterLesson.html)，2019年3月13日。


### 0221

- [VGGT-Motion: Motion-Aware Calibration-Free Monocular SLAM for Long-Range Consistency](https://arxiv.org/pdf/2602.05508)<br>
  把VGGT改成长序列SLAM，针对自动驾驶场景。用上了关键帧、sliding window、对齐、图优化等技术。<br>
  在token阶段，对于车的不同运动模式进行了embedding。<br>
  暂未开源。

- [**TrajVG: 3D Trajectory-Coupled Visual Geometry Learning**](https://xingy038.github.io/TrajVG/)<br>
  在pi^3的网络上多加了个Track head，用来估计3D correspondences。<br>
  暂未开源。

- [**Flow4R: Unifying 4D Reconstruction and Tracking with Scene Flow**](https://shenhanqian.github.io/flow4r)<br>
  暂未开源。<br>
  网络输入图像对，对称处理，估计（相机坐标系下的）场景流和（静态区域）权重。<br>
  用了8张A100/H100，训练大概4天。

- [LongStream: Long-Sequence Streaming Autoregressive Visual Geometry](https://www.arxiv.org/abs/2602.13172)<br>
  暂未开源。<br>
  基于VGGT网络，做Streaming的自回归3D重建。用了关键帧、kvcache等技术。<br>
  18fps，用了32张A100训至少3天（stage1就花了3天）。

- [TTSA3R: Training-Free Temporal-Spatial Adaptive Persistent State for Streaming 3D Reconstruction](https://www.arxiv.org/abs/2601.22615)<br>
  暂未开源。<br>
  解决在长序列3d重建时的灾难性遗忘问题。通过TAUM区分稳定区域和动态区域，从而选择性保留历史信息；通过SCUM识别需要更新的空间区域，避免对稳定几何区域的错误更新。<br>
  效果一般？


### 0222

**VDPM**

- 网络结构主要就是aggregator, decoder, point head, camera head。

- 测一下各个部分的耗时:

aggregator time: 1.765446 seconds
decode time: 4.525165 seconds, avg 0.377097 s/frame
point head time: 1.645535 seconds, avg 0.137128 s/frame
camera head time: 0.083022 seconds
Execution time: 8.021015 seconds for 12 images

aggregator time: 1.841392 seconds
decode time: 9.641138 seconds, avg 0.567126 s/frame
point head time: 0.807591 seconds, avg 0.047505 s/frame
camera head time: 0.119050 seconds
model inference finished
Execution time: 12.411482 seconds for 17 images

aggregator time: 2.119548 seconds
decode time: 22.632245 seconds, avg 0.943010 s/frame
point head time: 0.952443 seconds, avg 0.039685 s/frame
camera head time: 0.191697 seconds
Execution time: 25.898921 seconds for 24 images

aggregator time: 6.110203 seconds
decode time: 94.476820 seconds, avg 1.968267 s/frame
point head time: 19.817495 seconds, avg 0.412864 s/frame
camera head time: 0.114886 seconds
Execution time: 120.525079 seconds for 48 images

aggregator time: 12.515195 seconds
decode time: 527.383065 seconds, avg 5.493574 s/frame
point head time: 142.252627 seconds, avg 1.481798 s/frame
camera head time: 1.118869 seconds
Execution time: 683.297737 seconds for 96 images
GPU: 58274 MB

- aggregator包含了image encoding的backbone，camera token + time token + register token + 图像 patch token的concat，以及帧内self-attention和帧间cross-attention。
  
  - 这个耗时吗？如果不耗时，那直接把整个序列给处理了吧。
  
  - 如果是处理streaming input，比较trick的做法是，aggregator直接对所有帧提取token（但是cross-attention的时候前帧会从后帧中获得信息）。如果要严谨点，那就只能加个mask。

- decoder中用到了time embedding作为attention层的condition（参考文章3.3）

- 网络的输出是：
- result: ['pose_enc', 'pose_enc_list', 'pointmaps']
  - pose_enc: <class 'torch.Tensor'>, torch.Size([1, 17, 9]), torch.float32, -0.03974273428320885, 1.0005029439926147
  - pose_enc_list: <class 'list'>, 4, torch.Size([1, 17, 9]), torch.float32, -0.040348976850509644, 1.0002468824386597
  - pointmaps: <class 'list'>, 17, ['pts3d', 'conf']
    - pointmaps[pts3d]: torch.Size([1, 17, 294, 518, 3]), torch.float32, -0.5402331352233887, 2.065545082092285
    - pointmaps[conf]: torch.Size([1, 17, 294, 518]), torch.float32, 1.0000206232070923, 25.831775665283203
  - 其中，pointmaps是一个长度为S的list，其中第i个元素是一个dict，保存的是所有帧**在第i帧时刻下，在第0帧视角下**的point map和confidence。
  - 其中，pose_enc可以通过pose_encoding_to_extri_intri()提取出extrinsic和intrinsic。其中，extrinsic本来是world to camera，但在visualise.py的实例中inv成 camera to world 4x4 matrix了。

PointOdyssey数据集处理好了。尝试在test / val上面评价3d point map、poses、3d point tracking。

考虑：
- 评测相关问题
  - 如何评测3d
  - 如何评测poses
  - 如何在window之间将correspondence连起来，用来评测3d point tracking
- sliding window相关问题
  - VDPM在sliding window下，如何在window间进行对齐？（乘一个sim3？）
  - 长序列下是否有drifting问题，是否要加BA之类的优化？
  - 是否要加关键帧？


### 0223

PointOdyssey用来测试benchmark的Dataset写好了。

PointOdyssey中，anno.npz中的extrinsics是world to camera transformation matrix。

沿用0222的任务，继续。


### 0224

VDPM网络的输出，通过转化后的extrinsic是world to camera，但是在visualize.py中的compute_predictions()中转换成了camera to world。

或许把point map的evaluation给搞定了。沿用0222的任务，继续。


### 0225

把poses的evaluation给搞定了。

考虑3d point tracking的evaluation：
- 可以先用只在第一帧里visible的点来eval。它们的tracks是 $P_{0}(t_i, \pi_0)$ ，其中t_i是所有的时间戳。
- 再好好想想correspondences如何在window之间连起来？如果要靠overlap的P_{t_i}(t_i, \pi_i)的话，那如何处理


### 0312

St4RTrack的infer.py的保存文件：
- conf1_p0.npy, conf2_p0.npy: (H, W), float32
- img1_p0.png, img2_p0.png
- pts3d1_p0.npy, pts3d2_p0.npy: (H, W, 6), float32. 最后一维(x, y, z, r, g, b).

cab_e_3rd_6
dancingroom1_3rd1_14
dancingroom1_3rd2_5
seminar_g110_0315_ego1_18


### 0326

- [Track4World](arxiv.org/abs/2603.02573)

- [DROID-W](arxiv.org/abs/2603.19076)


### 0402

- [MotionCrafter: Dense Geometry and Motion Reconstruction with a 4D VAE](https://arxiv.org/abs/2602.08961)
  一个生成式4d重建+scene flow。

  主要模块：
  1. 一个4D VAE，将geometry和motion同时encode进4D latent空间。用合成数据集的gt geometry和scene flow做训练。
  2. 一个基于Stable Video Diffusion微调的扩散模型，在4D latent空间里进行扩散。
  
  用的是diffusion，是不是可以自然地用去做3d一致的世界模型？

  **需要调研一下stable video diffusion相关的文章和方法**

- [RayMap3R](https://arxiv.org/abs/2603.20588)
  
  training-free。基于CUT3R的工作。

  两个分支。
  1. 原分支输入图像特征和RayMap特征，预测完整的场景深度和置信度
  2. RayMap分支只输入RayMap特征（因为缺乏图像外观信息，这个分支会利用memory中的长期一致性结构进行预测），会预测出更偏向于静态背景的深度
  3. 将上述两个深度，计算相对深度差异，得到动态区域mask。
  4. 在更新latent时，采用门控更新，抑制动态区域的memory更新
  5. 由于要防止内存漂移，要每50帧要重置一次memory，会导致scale不一致。在重置时算一次Sim(3)。

- [FILT3R](https://arxiv.org/abs/2603.18493)
  
  CUT3R和TTT3R的后续工作，training-free。

  把latent space的更新视为在token空间的随机状态估计问题，用了卡尔曼滤波。并证明CUT3R和TTT3R是卡尔曼滤波的特解。


### 0407

- [Geo4D](https://arxiv.org/abs/2504.07961)


### 0413

- [Self-Improving 4D Preception via Self-Distillation](http://arxiv.org/abs/2604.08532)
  
  对3d fundamental model的自蒸馏方法，可用于VGGT、pi3等。

  1. teacher模型
     1. 输入的帧数更多，上下文更丰富。输入帧数在24-64帧。
     2. 输出伪标签。（梯度截断）
  2. student模型
     1. 输入的帧数更少（teacher的子集）。帧数在2-12帧。随机帧丢弃。
     2. 以teacher的输出为监督目标。
  3. 损失函数：点图预测对齐 + 特征匹配损失（但无一致性增益，故不用）
  4. 更新方式
     1. student通过损失函数直接更新。
     2. teacher通过EMA更新，lambda设为0.995(VGGT)和0.99(pi3)。

- [Mem3R](https://arxiv.org/abs/2604.07279)
  
  长序列流式重建，解决误差积累和时序遗忘问题。基于CUT3R改的。

  1. 隐式记忆：轻量级SwiGLU MLP层，记为f(·)，其权重是test-time training。
     1. 可以通过query q_t，得到位姿先验$\hat{p}_t = f(q_t)$，$\hat{p}_t$替代了CUT3R中的可学习位姿token z_t。
     2. 后面的解码器产生后验位姿p_t后，通过$L(\hat{p}_t, p_t)= <\hat{p}_t, p_t>$更新。
  2. 显式记忆：一组固定数量的token。通过通道级门控更新。

- [Scal3R](https://arxiv.org/abs/2604.08542)
  
  公里级长序列重建，test-time training。基于VGGT加的TTT。

  1. 分段处理（分sliding window），多GPU并行
  2. 在global attn层后加了个轻量的神经全局上下文记忆模块GCM：
     1. GCM学习的是从key映射到value，学好后就可以用query直接查询得到output
     2. GCM需要和VGGT一块的端到端离线训练。32张A800训练3天。
     3. GCM的在线更新阶段，会通过全局上下文同步GCS，通过all-reduce在不同GPU之间同步。

- [HyVGGT-VO](https://arxiv.org/abs/2604.02107)
  
  异步VO。
  
  前端：基于KLT稀疏光流的高效VO + VGGT增加鲁棒性。

  分层后端：第一阶段，基于共视关系的local BA；第二阶段，将VGGT预测的相对位姿作为结构约束，进行局部位姿图优化。

- [PTC-Depth](https://arxiv.org/abs/2604.01791)
  
  针对移动机器人和自动驾驶的单目深度估计。

  1. 利用光流计算相对运动，结合轮式odometry提供的baseline，通过recursive Bayesian update修正深度的绝对尺度。
  2. 从光流中估计相机相对位姿
  3. 将三角测量的稀疏深度，和深度估计fundation model的相对深度进行融合。


### 0414

- [VGGT-SLAM++](https://arxiv.org/abs/2604.06830)
  
  前端：RGB按照视差分成子图（每个子图最多32帧），用VGGT输出深度图、点云、位姿；相邻子图通过Sim(3)对齐。

  DEM子地图构建：

  1. 对VGGT输出的3D点，用RANSAC + SVD拟合主平面（地面/地板）
  2. 将所有点变换到平面对齐的标准正交坐标系(u,v,h)，h为相对平面高度
  3. 高度场光栅化。
  4. 全局DEM切分成2x2米的小tile，每个tile独立索引。
  
  共视图构建：

  1. 每个DEM tile送入DINOv2，加了高斯位置权重（抑制边界噪声）和可见性掩码。
  2. 新查询子地图的chip和全局DEM tile通过余弦相似度算相似性，得分高的认为是共视邻居，在共视图里连边。
  
  后端：对共视图的所有回环边，通过Sim(3)进行优化。
  
- [ViBA](https://arxiv.org/abs/2604.03377)
  
  把可微分BA融合到feature matching框架。

- [StereoVGGT](https://arxiv.org/abs/2603.29368)
  
  基于VGGT的training free，在encoding阶段融合了VGGT(多视角几何)、moge-2(单目深度)、DINOv2(语义)三种特征，保留结构细节和相机几何先验。

  1. 熵最小化权重合并。几种特征通过线性加权得到最终特征，权重通过最小化信息熵得到。
  2. 通过VGGT的frame attention对特征进行调制并加权。

- [Reliev3R](https://www.arxiv.org/abs/2604.00548)
  
  弱监督训练feed-forward recon model，无需3d真值标注。基于pi3做的修改。

  伪标签来源是depth pro估计的深度、cotracker生成的稀疏2d点对应。

- [Robust 4D Visual Geometry Transformer with Uncertainty-Aware Priors](https://arxiv.org/abs/2604.09366)
  
  基于VGGT的training free。动态场景重建框架，解决VGGT因运动物体导致的几何歧义和姿态漂移问题。

  动态区域的本质是多视图几何中表现的**高不确定性**：注意力方差大、局部几何不一致、投影置信度低。

- [Who Handles Orientation? Investigating Invariance in Feature Matching](https://arxiv.org/abs/2604.11809)
  
- [Online3R](https://arxiv.org/abs/2604.09480)

- [Point2Pose](https://arxiv.org/abs/2604.10415)

- [LoMa](https://arxiv.org/abs/2604.04931)
  
- [TAPNext++](https://arxiv.org/abs/2604.10582)

- [IncVGGT](https://www.scholar-inbox.com/paper/p2rlao/detail)
  
- [DINO-VO](https://arxiv.org/abs/2604.04055)
  
- [ReFlow](https://arxiv.org/abs/2604.01561)
