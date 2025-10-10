## 20250909 with 老颜

Related work以下几个方向

- 3d point tracking
  
- 处理长序列视频的问题，比如vggt-slam之于vggt；long3r等。
  

贡献：

- 现有的方法基于batch进行优化，如果用在长序列with sliding window的fashion的话，3d point track精度会下降（验证一下）。核心问题就是通过streaming的方式解决长序列的track精度问题。

问题：

- 导致显存炸的问题是什么，是否帧数增大/query point增多会导致空间开销变大。
- 3d point tracking相对于2d point tracking 特有的问题是什么？如果3dpt=2dpt+depth estimation，那3dpt就没有它独有的科研问题，解决好2dpt的方法就可以很manner的用过来解决好3dpt。比如，这两个问题的建模有什么不同；3dpt在特征融合的时候，是否有因为方法建模引起的问题。

## 20250911 with 飞哥

- **memory bank的设计**，history information保存哪些，如何更新，如何retreve。*track-on，sam2*
  
- encoder part：*$\pi^3$或者fastvggt*
  
- sliding window方式做长序列window内的BA，sliding window的size是否可以flexible和adaptive等可以挖掘的小点。
  
- training / testing dataset，主要的benchmark，与各个方法的接口。


## 20250919 with 飞哥

TODO：

1. cotracker3 spatialtrackerv2的evaluation，evaluation dataset都准备好，跑出现有工作论文里的指标。

2. 测一测long sequence，有没有performance drop

3. 加自己的

Brain storming：

1. 对track做grouping，对motion pattern做分类

2. 多少个track的选择，怎么选择，有没有elegent的设计

3. 有没有较极端场景（动态物体多，运动速度过快）（所有的query point基本都在动态物体上，spatialtrackerv2会完全垮掉 => 如何用local/global context解决long-term error accumulate的问题），可以和第二点辅助query的选择结合起来做了


## 20251006

Brain storming:

1. 自适应的query策略能不能从高斯/nerf里搞一搞？

2. DOT, dense optical tracking: connecting the dots里，有比较初步的query点选择策略（从光流中提取运动边界）。


## 20251007 with 老颜

1. $pi^3$作前端的重建，能保证视角变化引起的scale问题。
2. query point出画面的过程中，能不能选一些支撑点，保证之前的点不要乱飘（能不能利用上之前的tracker里能够在track之间share信息的inductive bias，使得看得见的点的track能引导被遮挡/出画面的点的track）
3. feature extractor换成dinov3这种invariant的


## 20251010 with 飞哥

梳理故事：
3d online tracking

方法(todo)：
1. memory的设计
   1. track-on做基本的参考。
2. query的选择，adaptively的filter out。（brain storming：online的filter out，motion prediction+reprojection loss...）
3. query selection with memory


