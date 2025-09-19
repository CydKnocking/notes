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

      在17个数据集上训练。分为三大类：带track gt, pose gt的RGB-D数据；带pose gt的RGB-D数据；仅有pose gt或无标注的。

      训练分三个阶段。一阶段，训练前端的网络（VGGT改的估计视频深度和初始相机位姿），64张H20。二阶段，训练SyncFormer，8张H20训3天。三阶段，固定前端网络中的交替注意力层，训整个框架。

4. 实验结果
   
   主要结果是在TAPVid-3D上对比3d tracking的精度。在3d point tracking上是sota。

   深度估计，在室内(tum dyn, bonn, sintel)和室外(kitti, sintel)含动态物体的数据集，比VGGT和MegaSam好（各有优劣）。

   相机位姿估计，在室内外（tum dyn, lightspeed, sintel），和MegaSam差不多。

   2D tracking也是SOTA。


## Related works about point tracking

整理一下tracking any point最近的related works

### 2D point tracking

- [CoTracker: It is Better to Track Together](https://www.arxiv.org/pdf/2307.07635)<br>
  `ECCV'24`, `2d`, **`阶段性代表作`**<br>
  23年7月cotracker挂arxiv上。24年10月这一版应该是cotracker2。一般都叫cotracker了。meta+牛津<br>
  
  故事核心是，同时跟踪多个点比只关注一个点要好，因为可以通过交换信息理解场景/物体的整体运动。

  - 用Transformer进行联合跟踪，并对track进行迭代更新。中间用了每个点周围的correlation features进行更新。
  
  - 处理长视频用的是sliding window。
  
  - 使用了Proxy tokens作为attention的信息中转，提高了计算效率（如果点的个数很多那attention会开销很大）。
  
  - 用了Support points，为被追踪点提供信息。
  
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
  
  实验：
  
  - baseline是2d point tracking。
  
  - 在tapvid，RoboTAP（一个真实序列，涉及机器人操作），DynamicReplica（合成数据集）上测试。
  
  - 两种测试模式，first query和strided query。
  
    - first模式，以物体上的点第一次出现的时间为query，后面一直追踪。
  
    - strided模式，追踪点每隔5帧被查询一次。
  
    - 所以一般first的结果要比strided要稍差。

  局限
  
  - offline模型受计算资源限制，online模型又无法从更全局的视角更好处理遮挡和长时间track
  
  - 选什么点进行track会稍微影响精度（tab6），并且对于“更好track的点”的结果更好（因为半监督时选的sift）
  
  - 精度上限受teacher models的bound。
  
  - 用于微调的真实数据集主要包含人类和动物，对于其它场景的表现还有待观察。

- [Local All-Pair Correspondence for Point Tracking (LocoTrack)](https://arxiv.org/pdf/2407.15420v1)<br>
  `ECCV'24`, `2d`, **`阶段性代表作`**<br>
  
  方法上：
  
  - 提出4d correlation，即把查询点周围小区域与目标帧的周围小区域计算匹配关系。
  
  - 针对4d correlation设计了一个轻量的编码器。
  
  - 代码用JAX实现。
  
  实验上：
  
  - 主要测的是2d point tracking。
  
  - 4天8张3090训练。在Kubric上训。在kinetics, davis, rgb-stacking上测。
  
  - 速度比cotracker快。1w个点花一两秒，10w个点花十几二十秒。

- [Tracking Everything Everywhere All at Once](https://arxiv.org/pdf/2306.05422)<br>
  `ICCV'23 Best student paper`, `2d`, **`阶段性代表作`**<br>

  方法上：
  
  - 引入了quasi-3d canontical volume。
  
  - 有点迷没看懂，回头仔细看看。

- [PointOdyssey: A Large-Scale Synthetic Dataset for Long-Term Point Tracking](https://www.arxiv.org/pdf/2307.15055)<br>
  `ICCV'23`, `2d`, `dataset`, `PIPs++`<br>
  提出了个更长序列的2d合成数据集。<br>
  提出了个方法叫PIPs++，用1d卷积代替了mlp-mixer，能处理任意长序列的特征。

### 3D point tracking

- [SpatialTracker: Tracking Any 2D Pixels in 3D Space](https://arxiv.org/pdf/2404.04319)<br>
  `CVPR'24 highlight`, `3d`, **`阶段性代表作`**<br>

  方法上：
  
  - 将2d的图像特征，通过predicted depth (ZoeDepth)给lift到3d，并将它们投影到triplane进行高效表示。
  
  - 是在相机坐标系下进行的表示，没有考虑相机位姿，也没有把所有帧都warp到统一的世界坐标系。（在spatialtrackerv2的分类属于type II。）
  
  - 用了ARAP(as-rigid-as-possible)约束，约束各个运动部分尽可能保持刚性。具体来说，给每个轨迹估计了一个rigidity embedding，然后两个embedding之间来算刚性相似度，进而进行带权的约束。
  
  实验上：
  
  - 2d tracking结果和3d tracking结果。
  
  - 2d tracking中，用gt depth比ZoeDepth要好一点。
  
  - 是3d tracking的baseline。不过也可以把2d的方法lift。

- [Multi-View 3D Point Tracking](https://www.arxiv.org/pdf/2508.21060)<br>
  `ICCV'25`, `3D`, `multi-view`<br>
  将多视角的2d特征给lift到3d进行融合，再根据查询点的kNN的特征对track进行迭代更新。<br>
  特征提取的模块和CoTracker系列+SpatialTrackerv1一样的，就是一个CNN提取金字塔特征。<br>
  迭代更新的模块是follow CoTracker2。<br>
  在multiview-kubric上进行训练。3d tracking实验结果似乎比spatialtrackerv2要好（PStudio这个序列）。但是其用了多个视角进行融合，设定更偏向MVS，所以感觉合理。<br>
  但是2d tracking的结果没CoTracker3好。

- [TAPIP3D: Tracking Any Point in Persistent 3D Geometry](https://arxiv.org/pdf/2504.14717)<br>
  `3D`, **`阶段性代表作`**<br>
  用MegaSAM对RGB序列给出depth和camera pose，将2d feature map给lift到3d，并且变换到统一的世界坐标系下（一般是第一帧），再在3d中以kNN作为query point的邻域，与其他帧的邻域进行融合。<br>
  在spatialtrackerv2的分类属于type III。


## 其他领域的相关工作

### vggt

- [FastVGGT: Training-Free Acceleration of Visual Geometry Transformer](https://www.arxiv.org/abs/2509.02560v1)<br>
  在vggt中选择token，只在这些token中做attention，加快速度，节省开销，并且不用重新训练。有可能可以抑制误差累积。<br>

## 数据集

### Point tracking 类

- [TAPVid-3d](https://tapvid3d.github.io/)<br>
  [github](https://github.com/google-deepmind/tapnet/tree/main/tapnet/tapvid3d), [paper](https://arxiv.org/pdf/2407.05921)<br>
  3dtracking的。有adt, panoptic studio(pstudio), drivetrack三个子集。时长从几秒到十秒不等，4569个clip，25-300帧/clip<br>
  
  drivetrack数据集，应该是waymo数据集转换后的名字，waymo数据集的motion数据集至少要4.3T或更多。

  mdwc了下载这个数据集预处理怎么要这么大空间。

  https://huggingface.co/datasets/ZhengGuangze/TAPVid-3D/tree/main，这个好像是预处理后的，一共480G。

  但是根据[issue](https://github.com/google-deepmind/tapnet/issues/110)，tapvid3d作者说它的电脑上只占了138GB。

- [DexYCB-Pt](https://dex-ycb.github.io/)<br>
  [paper](https://www.arxiv.org/abs/2104.04631v1)<br>
  手部-物体互动场景，3d。有8个视角，但序列不长，有手部+物体的位姿真值。<br>

- [PointOdyssey](https://pointodyssey.com/)<br>
  
  [paper](https://www.arxiv.org/pdf/2307.15055), [dataset](https://github.com/google-deepmind/tapnet/blob/main/tapnet/tapvid/README.md#downloading-robotap)<br>

  合成数据集，是长序列，但是是2d。30fps，平均2k+帧一个序列。<br>

  数据集[在这](https://drive.google.com/drive/folders/1W6wxsbKbTdtV8-2TwToqa_QgLqRY3ft0)下载。

  **下好了。**

- [TAPVid-DAVIS](https://github.com/google-deepmind/tapnet/tree/main/tapnet/tapvid)

  2d point tracking主要的benchmark。测试集和训练集不一样。

  **本地已经有可供cotracker3的测试集。已在cotracker3上成功evaluate.**

- [RoboTAP](https://robotap.github.io/)<br>
  [paper](https://www.arxiv.org/pdf/2308.15975)<br>
  机械臂操作物体，相机在机械臂上。TAP-Vid系列数据集之一。2d。

- [Dynamic Replica](https://dynamic-stereo.github.io/)

  2d point tracking的benchmark。

### Video depth类

- [KITTI]
  
- [TUM-dynamic]
  
- [Bonn](https://www.ipb.uni-bonn.de/data/rgbd-dynamic-dataset/index.html)
  
- [Sintel]

### Camera pose

- [TUM-dynamic]

- [Lightspeed]

- [Sintel]

## 评价指标

- OA, Occlusion Accuracy.
  
  预测的遮挡与否的标签的准确率，$OA=\#_{correct_label}/\#_{points}$

- APD, APD3d.
  
  对所有可见点的轨迹，计算在设定的距离误差阈值(1, 2, 5, 10cm...)内的点的比例。对所有距离阈值下的APD取平均。

- AJ, Average Jaccard.
  
  设置距离阈值$\delta$，统计以下三类点的数量：
  1. True Positive: 点的gt是可见，模型预测是可见，并且误差小于等于$\delta$。
  2. False Positive: 点的gt是遮挡，模型预测可见；或者，点的gt是可见，模型预测可见，但误差大于$\delta$。
  3. False Negative: 点的gt是可见，模型预测被遮挡。
  
  计算$AJ=TP/(TP+FP+FN)$，并对所有设定阈值下的AJ取平均。
