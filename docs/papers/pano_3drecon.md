本文档为全景相机做三位重建/四维重建的相关论文的整理。

- [PanoVGGT](https://arxiv.org/abs/2603.17571)
  
  全景相机版本VGGT，上海科大。静态场景，离线。

  构造了新的数据集PanoCity: 超过120000张带位姿和深度标注的全景图。虚拟数据集、室外场景、主要静态场景、不同天气条件。

  方法：

  1. DINOv2编码。和VGGT类似的交替注意力模块。

  2. 从标准的 2D 网格编码改为球感位置编码 (Spherical-aware PE)

  3. 数据增强改用了SO(3)旋转增强，并随机定target frame。
  
  8张A100训练10天。用的数据集：PanoCity、Matterport3D、Stanford2D3D 和 Structured3D。

