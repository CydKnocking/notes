本文档为4d reconstruction + 3d tracking相关论文的整理。目标为处理stream的4d recon with dense temporal correspondence，一种时空一致的表示。

## xxx3R/xxx4R 相关

baseline: St4RTrack


## VGGT 相关

baseline: VDPM

- [StreamVGGT](https://arxiv.org/abs/2507.11539)
  解决动态视频/实时应用中，模型需要反复重算导致的延迟问题，实现实时、增量式的4D重建。

  1. 时序因果注意力：处理序列时只允许关注当前帧和过去的帧。
  2. cached memory token
  3. 用原版VGGT作为教师模型，进行知识蒸馏。

- [DynamicVGGT](https://arxiv.org/pdf/2603.08254)
  自动驾驶场景的动态4d场景重建。

  1. MTA，感知时间注意力模块，并且于VGGT原先的alternative attn模块并行。
  2. 增加了Future point head用于预测未来点图。
  3. 动态3dgs头

- [VGGT-World](https://arxiv.org/abs/2603.12655)
  把VGGT改成可以“预测未来3D几何演变的几何世界模型”，在geometry fundation model的高维特征空间中预测未来的几何状态（相比预测视频外观，更能保证3d结构的一致性）。

  冻结了部分VGGT网络，预测部分用diffusion。

- [GGPT](https://arxiv.org/abs/2603.11174)
  在VGGT的结果加了SfM, BA等模块优化点云。



