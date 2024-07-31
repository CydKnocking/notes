---
password: password
---

# 2024

## 0704

- 用stable diffusion做finetune，可以用低开销和不多的数据集做finetune。

- 做depth的：Repurposing Diffusion-Based Image Generators for Monocular Depth Estimation (CVPR 2024)，可以从里面借鉴conditional的用法，以及如何把depth image转换到适合diffusion的框架；做dense matching的：DIFFUSION MODEL FOR DENSE MATCHING (ICLR 2024)，他用两张图的global cost作为condition，但是框架设计上还是有点暴力。

## 0705

- DOT（Matching 2D Images in 3D: Metric Relative Pose from Metric Correspondences）为啥比RAFT和CoTracker效果还好？DOT的实验设计和故事是怎么讲的，值得看一看。

## 0706

- 用covariance建模point tracks之间的关联性？
  
  三个好处：鲁棒（从图像中对点做track，学的是$\delta I$；而学习track之间的covariance，学的是$\delta I$整体的分布特性）；高效（减轻数据冗余和学习负担，可以用少量的稳定的点，表达整张图里其他点的运动趋势，同时也可以表达相机的运动趋势）；可以做预测（学到的covariance可以用作预测point在下一帧里的移动）
  
  数学方法上参考Learning a Depth Covariance Function，看看他怎么进行的随机过程建模
  
  坏处：那这样就要讲point track的故事了？不管是point tracking还是optical flow，都非常关注动态物体。那要做动态物体？

- 考虑用covariance function做optical flow？还是做keypoint matching？

- Image encoder可以考虑用预训练的DIVOv2。

- 如果做covariance function+optical flow，那难点就在于：depth covariance function是用的UNet cnn网络，RAFT用的是GRU，这个怎么调通。

## 0708

- dust3r：能否做到online，能否做到sparse


## 0729

- rotation-invariant PPF (RIGA sec3.2).


## 0731

- SuperPoint + Co-Tracker + COTR ?







