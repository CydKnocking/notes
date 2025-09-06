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
