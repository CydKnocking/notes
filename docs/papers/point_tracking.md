## [SpatialTrackerV2: 3D Point Tracking Made Easy](https://github.com/henry123-boy/SpaTrackerV2)

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


## Related works about point tracking

整理一下tracking any point最近的related works

- [CoTracker: It is Better to Track Together](https://www.arxiv.org/pdf/2307.07635)<br>
  `ECCV'24`, `2d`, **`阶段性代表作`**<br>
  23年7月cotracker挂arxiv上。24年10月这一版应该是cotracker2。一般都叫cotracker了。meta+牛津<br>
  
  故事核心是，同时跟踪多个点比只关注一个点要好，因为可以通过交换信息理解场景/物体的整体运动。<br>
  - 用Transformer进行联合跟踪，并对track进行迭代更新。中间用了每个点周围的correlation features进行更新。<br>
  - 处理长视频用的是sliding window。<br>
  - 使用了Proxy tokens作为attention的信息中转，提高了计算效率（如果点的个数很多那attention会开销很大）。<br>
  - 用了Support points，为被追踪点提供信息。<br>
  
  实验，在TAPVid-Kubric上训练，在tapvid-davis, tapvid-rgb-stacking和pointodyssey上测试。另外也在dynamic replica上测试。主要结果是2d point tracking。<br>
- [CoTracker3: Simpler and Better Point Tracking by Pseudo-Labelling Real Videos](https://arxiv.org/pdf/2410.11831)<br>
  `2d`, **`阶段性代表作`**<br>
  24年10月挂arxiv上。meta+牛津<br>

  有offline和online两个版本：
  - offline版本是把整个video一起处理，支持正向+反向两个方向估计track，并且能更好处理遮挡问题和估计长时间的track。但是受计算资源限制。
  - online版本以sliding window对video处理，只能对点进行正向track的估计。
  
  方法上提出了更精简高效的框架：
  - 借鉴了LocoTrack的4d correlation概念，在此基础上进行了简化，只用一个MLP来处理相关性特征。
  - 特征提取，迭代更新，proxy token等与cotracker没啥差别。
  
  提出生成伪标签的方式增大训练数据量：
  - 之前很多是用的合成数据Kubric，需要给真实数据生成gt。
  - 用了多个teacher models，包括Cotracker3(online+offline), Cotracker, TAPIR。学生模型就是一个在合成数据集上进行了预训练的CoTracker3。
  - 在真实数据上，先用sift等选出“更容易track”的点，然后随机选一个教师模型生成伪标签。
  
  实验：baseline是2d point tracking。在tapvid，RoboTAP（一个真实序列，涉及机器人操作），DynamicReplica（合成数据集）上测试。

  局限
  - offline模型受计算资源限制，online模型又无法从更全局的视角更好处理遮挡和长时间track
  - 选什么点进行track会稍微影响精度（tab6），并且对于“更好track的点”的结果更好（因为半监督时选的sift）
  - 精度上限受teacher models的bound。
  - 用于微调的真实数据集主要包含人类和动物，对于其它场景的表现还有待观察。

- [Local All-Pair Correspondence for Point Tracking (LocoTrack)](https://arxiv.org/pdf/2407.15420v1)<br>
  `ECCV'24`, `2d`, **`阶段性代表作`**<br>


- [SpatialTracker: Tracking Any 2D Pixels in 3D Space](https://arxiv.org/pdf/2404.04319)<br>
  `CVPR'24 highlight`, `3d`, **`阶段性代表作`**<br>

- [Multi-View 3D Point Tracking](https://www.arxiv.org/pdf/2508.21060)<br>
  `ICCV'25`, `3D`, `multi-view`<br>
  将多视角的2d特征给lift到3d进行融合，再根据查询点的kNN的特征对track进行迭代更新。<br>
  特征提取的模块和CoTracker系列+SpatialTrackerv1一样的，就是一个CNN提取金字塔特征。<br>
  迭代更新的模块是follow CoTracker2。<br>
  在multiview-kubric上进行训练。3d tracking实验结果似乎比spatialtrackerv2要好（PStudio这个序列）。但是其用了多个视角进行融合，设定更偏向MVS，所以感觉合理。<br>
  但是2d tracking的结果没CoTracker3好。

数据集

- [TAPVid-3d](https://github.com/google-deepmind/tapnet/tree/main/tapnet/tapvid3d)<br>
  有adt, panoptic studio(pstudio), drivetrack三个子集。<br>
