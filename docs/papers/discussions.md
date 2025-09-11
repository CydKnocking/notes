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