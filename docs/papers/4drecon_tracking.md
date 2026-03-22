本文档为4d reconstruction + 3d tracking相关论文的整理。目标为处理stream的4d recon with dense temporal correspondence，一种时空一致的表示。

## xxx3R/xxx4R 相关

这篇文章主要做了什么工作？它基于什么已有的工作？和它基于的工作相比，关系和不同在哪？

baseline: [St4RTrack](https://arxiv.org/abs/2504.13152)

- [DUSt3R](https://arxiv.org/abs/2312.14132)
  提出了用transformer估计pointmap，可以做到像素级匹配、估计相机参数、场景几何。pair-wise。

### 动态场景重建 / 跟踪

- [MonST3R](https://arxiv.org/abs/2410.03825)
  基于dust3r做动态场景。

  1. 冻结encoder进行了重新训练
  2. sliding window.

- [POMATO](https://arxiv.org/pdf/2504.05692)
  动态场景3d重建。

  引入：
  1. 新的matching head，预测第2帧图像在第1帧时刻下的pointmap
  2. 时间运动模块，在时间维度上加注意力机制

- [Flow3r](https://arxiv.org/abs/2602.20157)
  4d重建+光流。

  因式分解流预测：
  1. 用现有光流方法生成pseudo-gt
  2. 以不同的token组合作为输入，可以生成不同帧的光流

- [Flow4R](https://arxiv.org/abs/2602.14021)
  4d重建+场景流。对称设计。处理流的模式和st4rtrack一样，都是固定第一帧，滑第二帧。

- [DDUSt3R](https://arxiv.org/abs/2504.06264)
  动态场景重建。
  
  1. 利用已有的方法(SEA-RAFT)或数据集的光流真值，分别针对动态-静态区域的3d预测设计了监督目标。
  2. 多了两个预测头：动态mask预测头（基于DPT），光流预测头（基于RAFT）。

- [PointSt3R](https://arxiv.org/abs/2510.26443)
  动态重建+点跟踪（2d3d都可以）。其实可以看作是点匹配问题，因为输入是两帧，网络做的是2-frame dense correspondence。基于mast3r。

  1. 添加动态点匹配的损失函数，和一个visibility head。




### 增量式 / 序列 / SLAM / 实时

- [Spann3R](https://arxiv.org/abs/2408.16061)
  引入Spatial Memory增量式重建。基于dust3r。

  基于memory，实现每一帧都在全局坐标系下进行估计，同时能够对齐点云。

  记忆分为
  1. 工作记忆。保存最近5帧的特征。短期记忆
  2. 长期记忆。记录每个token被“关注”(attn)的累积权重，只保留top-k。

- [CUT3R](https://arxiv.org/pdf/2501.12387)
  在线、连续的密集3d重建。支持动态场景。基于dust3r。十几fps。

  基于persistent state。

- [Point3R](https://arxiv.org/abs/2507.02863)
  streaming 3d recon。基于spann3r和cut3r。

  基于显式空间指针内存。
  1. 不存储历史帧，而是探索过的物理位置的feature。
  2. 动态扩展，会将物理距离相近的新旧指针进行合并。

- [TTT3R](https://arxiv.org/abs/2509.26645)
  解决在线3d recon处理长序列的灾难性遗忘问题。基于cut3r。training-free。对hidden state进行带权重的更新。

- [MASt3R-SLAM](https://arxiv.org/abs/2412.12392)
  基于mast3r构建slam。15fps。

  基于射线角度进行局部优化；基于射线误差；引入sim(3)的二阶全局优化器。

- [SLAM3R](https://arxiv.org/abs/2412.09401)
  20+FPS。基于dust3r。

  1. Image-to-Points：对sliding window预测局部坐标系下的3d。把dust3r从两帧改到多帧，引入多视角交叉注意力。
  2. local-to-world：通过feed-forward网络增量式将局部点云融合到全局。

- [STream3R](https://arxiv.org/pdf/2508.10893)
  streaming处理。重点改造decoder。有基于dust3r和vggt的两种变体

  1. 因果注意力
  2. kv-cache




### 其他改进

- [Pow3R](https://arxiv.org/abs/2503.17316)
  支持rgb，内参，外参等多种输入。

- [Human3R](https://arxiv.org/pdf/2510.06219)
  4d人物+场景重建框架。feed-forward输出所有人体的3d人体网格+3d点云+相机位姿。

  3d人体网格是基于Multi-HMR这个工作。

- [Test3R](https://arxiv.org/abs/2506.13750)
  test-time training。基于dust3r。

  在测试时，用不同的输入图像组合的结果（1+2, 1+3），用“一致性”来监督网络。在dust3r的Transformer编码器层插入少量可学习的token进行微调。


- [Rig3R](https://arxiv.org/pdf/2506.02265)

- [WinT3R](https://arxiv.org/pdf/2509.05296)

- [MUT3R](https://arxiv.org/pdf/2512.03939)

- [PAD3R](https://arxiv.org/pdf/2509.25183)

- [Regist3R](https://arxiv.org/abs/2504.12356)

- [SIU3R](https://arxiv.org/pdf/2507.02705)

- [SING3R-SLAM](https://arxiv.org/pdf/2511.17207)

- [Evict3R](https://arxiv.org/abs/2509.17650)

- [Mono3R](https://arxiv.org/abs/2504.13419)

- [NOVA3R](https://arxiv.org/abs/2603.04179)


## VGGT 相关

baseline: VDPM

### 处理序列输入 / SLAM

- [StreamVGGT](https://arxiv.org/abs/2507.11539)
  解决动态视频/实时应用中，模型需要反复重算导致的延迟问题，实现实时、增量式的3D重建。在动态场景表现不佳。将VGGT改造成了支持流式、增量输入的网络。

  1. 时序因果注意力：处理序列时只允许关注当前帧和过去的帧。
  2. cached memory token
  3. 多了2d track head。
  
  训练阶段
  1. 用原版VGGT作为教师模型，进行知识蒸馏。
  2. 用13个数据集，4张A800训练。
  
- [VGGT-SLAM](https://arxiv.org/pdf/2505.12549)
  把VGGT构建成SLAM系统。training-free。子图，因子图在SL(4)上优化，回环。

- [VGGT-Long](https://arxiv.org/pdf/2507.16443)
  基于VGGT构建处理超长序列（公里级，自动驾驶）的系统。Training-free。

  1. 分块处理（chunks / sliding window），用加权Sim(3)进行拼接
  2. 用DINOv2特征检测闭环。
  3. 不用BA，用全局的轻量LM算法对分块的Sim(3)变化进行非线性优化。

- [InfiniteVGGT](https://arxiv.org/pdf/2601.02281)
  处理长序列问题。引入了“滚动记忆”架构。Training-free。

  1. kv-cache也会随着帧数线性增长，而相邻帧的key非常相似。
  2. 通过key的多样性进行剪枝：如果某个key和所有key均值的余弦相似度很高（很相似）就丢弃。
  3. 不同层的kv-cache保存大小是不同的，浅层多，深层少。
  4. 将第一帧所有token设为不可变。
  5. 基于StreamVGGT的改造，永乐因果时间注意力

- [OVGGT](https://arxiv.org/abs/2603.05959)
  Training-free。O(1)的显存复杂度。（静态场景）

  把kv cache压缩到固定大小。
  1. 用transformer中间残差的幅度，评价token几何重要性。
  2. 引入spatial gaussian smoothing确保留下来的token有空间连贯性。
  3. 结合当前帧激活值+历史缓存的特征多样性，淘汰冗余token
  4. 把第一帧token保存。
  5. 时空注意力

- [XStreamVGGT](https://arxiv.org/abs/2601.01204)
  Training-free。基于StreamVGGT继续改进。

  kv-cache
  1. 保留首帧和当前帧
  2. 中间帧的token通过query pooling进行压缩，基于压缩后的q和key的相似度保留top-k token。
  3. 精度量化：对key张量采用per-channel量化；对value采用per-token量化

- [FrameVGGT](https://arxiv.org/abs/2603.07690)
  Training-free。基于infiniteVGGT。

  1. 不用token级别的兼职，而将每一帧的kv-cache作为完整的块进行保留/丢弃，能够保证局部几何结构。（类似关键帧）
  2. 中短期即以苦：将每帧的块进行压缩，基于距离的贪心策略，选择块的去留。
  3. 全局锚点层。

- [SwiftVGGT](https://arxiv.org/abs/2511.18290)
  大规模场景（自动驾驶公里级）。保证3d重建和跟踪精度，降低推理时间。主要与VGGT-Long对比。

  1. 块对齐时，基于深度图对齐差异和置信度的采样，采样的点直接用SVD对齐。
  2. loop closure的时候，直接用DINO图像块token转换成全局描述符，无需其他模型。

- [LongStream](https://arxiv.org/pdf/2602.13172)
  3D重建长序列，解决轨迹崩溃、尺度漂移、外推失败。18FPS。

  “规范解耦”
  1. 预测当前帧相对局部关键帧的相对位姿（而不是相对第一帧）
  2. 引入scale token和尺度预测头。将几何形状和尺度预测解耦，减少尺度漂移。
  3. StreamVGGT遇到“注意力下沉”问题，导致长序列跟踪失败 -> 缓存一致性训练（Cache-consistent training），训练时截断并传递kv-cache。在推理时采用周期性缓存刷新策略。
  
  重新训练了
  1. 一阶段32张A100，3天
  2. CCT训练


### 效率提升，减少开销

- [FastVGGT](https://arxiv.org/pdf/2509.02560)
  Training-free。原版VGGT计算瓶颈在全局注意力，且注意力稀疏，本文改造了token merging技术。

- [Faster VGGT with Block-Sparse Global Attention](https://arxiv.org/pdf/2509.07120)
  Training-free。原版VGGT全局注意力非常稀疏。
  
  1. 引入自适应block-sparse attention机制
  2. 引入特殊token(相机参数，registor token)只在特殊token上做密集注意力；在图像块上做稀疏注意力。

- [FlashVGGT](https://arxiv.org/pdf/2512.01540)
  原版VGGT全局注意力非常稀疏。

  1. 通过插值压缩k v token，用原先的所有token做查询。
  2. 辅助token：把相机token，第一帧所有token，聚类选出的关键token保留。
  3. 输入的帧进行分段处理，把之前的压缩token作为memory传给下一个块。

  微调训练：
  1. 4张H800，16个小时
  2. 冻结encoder和reconstruction head，只训练修改过的alternating attn部分。

- [AVGGT](https://arxiv.org/pdf/2512.02541)
  Training-free。提出推理加速策略。

  1. 早期层特征缺乏3d信息，无法建立对应关系 -> 把早期层(前9层)的global attn换成单帧attn。
  2. 中间层负责跨视角对齐，晚期层负责微小的特征细化 -> 类似“稀疏点云对齐”，在有global attn的层对key value用2d网格均匀稀疏采样，保留所有query。（还有对角线保留、均值填补）

- [LiteVGGT](https://arxiv.org/abs/2512.04939)
  
  1. 通过融合像素梯度和token方差，评估token的“几何重要性”
  2. 保留前10%的token作为“global-aware tokens”
  3. 相邻层的token相似度非常稳定 -> 每6层才计算一次
  4. FP8量化
  
  微调网络：
  1. 微调aggregator、camera head、depth head
  2. 8张H20，3天



### 精度提高

- [VGG-T^3](https://arxiv.org/pdf/2602.23361)
  加入Test-Time Training，用来压缩token数量，将attention的复杂度从O(n^2)，用MLP压缩到O(n)。

  训练：
  1. 冻结encoder, per-image attention, 所有的heads。只微调全局注意力层。
  2. 移除了LayerNorm，引入ShortConv2D。
  3. 用MLP对k-v进行压缩。训练目标是L=T_\theta(k_i) - v_i，应用时直接o_i=T_\theta(q_i)。（因为MLP是线性空间，直接对应qk相乘算权重）

- [GGPT](https://arxiv.org/abs/2603.11174)
  后处理。在VGGT的结果加了SfM, BA等模块优化点云。


### 特殊场景

- [DynamicVGGT](https://arxiv.org/pdf/2603.08254)
  自动驾驶场景的动态4d场景重建。

  1. MTA，感知时间注意力模块，并且于VGGT原先的alternative attn模块并行。
  2. 增加了Future point head用于预测未来点图。
  3. 动态3dgs头

- [VGGT4D](https://arxiv.org/abs/2511.19971)
  动态4D场景重建。Training-free。

  1. 发现attn层的Gram相似度隐式的编码了物体运动信息 -> 跨帧聚合浅层、中层、深层的gram相似度统计数据，可以直接提取动态物体的初始mask（不依赖其他模块）
  2. mask细化阶段，利用点云投影的几何和广度残差梯度。
  3. 在1-5层主动屏蔽动态图像token，防止运动信息干扰后续的几何推理过程。

### 其他任务

- [VGGT-World](https://arxiv.org/abs/2603.12655)
  把VGGT改成可以“预测未来3D几何演变的几何世界模型”，在geometry fundation model的高维特征空间中预测未来的几何状态（相比预测视频外观，更能保证3d结构的一致性）。

  冻结了部分VGGT网络，预测部分用diffusion。

- [Dense Dynamic Scene Reconstruction and Camera Pose Estimation from Multi-View Videos](https://arxiv.org/abs/2603.12064)
  multi-view的4d重建+cam pose。只用VGGT做初始化，后面是基于多帧graph的SLAM系统。

- [Multi-View 3D Point Tracking](https://arxiv.org/abs/2508.21060)
  任务就是标题。feed-forward的。用了VGGT提取3d。iterative的优化点tracks，用的kNN找correlation features。

- [On Geometric Understanding and Learned Priors in Feed-forward 3D Reconstruction Models](https://arxiv.org/pdf/2512.11508)
  对VGGT进行可解释性分析和鲁棒性评估。构建了一个ShapeNet合成数据集来探究。

  1. 从大概12层开始的latent特征，已经可以解码出Fundamental Matrix。
  2. 第10-16层的注意力头在进行图像之间的点对应匹配。

- [Reloc-VGGT](https://arxiv.org/pdf/2512.21883)
  基于VGGT做视觉重定位。

- [VGGT-X](https://arxiv.org/pdf/2509.25191)
  基于VGGT做新视角合成。
  
  也做了VGGT的效率优化：
  1. float32降成BFloat16
  2. 引入分块帧级注意力处理

- [Dense Semantic Matching with VGGT Prior](https://arxiv.org/abs/2509.21263)
  用VGGT做密集语义匹配。保留VGGT早期的3D几何先验，微调后续层来提取语义token，用DPT做语义匹配头。



## 其他模型相关

- [KV-Tracker: Real-Time Pose Tracking with Transformers](https://arxiv.org/abs/2512.22581)
  基于$\pi^3$模型，流式处理，能达到25～30FPS。**Training-free**。

  在产生新的关键帧时：将所有关键帧用pi3完整算一遍（完整的双向注意力），并保存kv-cache。<br>
  在新帧进来时：将新帧和关键帧的kv-cache用pi3算一遍，得到相机位姿和3d。

- [Any4D](https://arxiv.org/pdf/2512.10935)


- [Video World Models with Long-term Spatial Memory](https://arxiv.org/pdf/2506.05284)

- [4DNeX](https://arxiv.org/pdf/2508.13154)

- [MoRe](https://openaccess.thecvf.com/content/WACV2026/papers/Jung_MoRe_Monocular_Geometry_Refinement_via_Graph_Optimization_for_Cross-View_Consistency_WACV_2026_paper.pdf)

- [MuBe4D](https://mube4d.github.io/)

- [MoRE](https://arxiv.org/pdf/2510.27234)


