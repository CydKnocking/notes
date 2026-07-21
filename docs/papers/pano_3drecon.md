本文档为全景相机做三位重建/四维重建的相关论文的整理。


## 相关工作


- [PanoVGGT](https://arxiv.org/abs/2603.17571)
  
  全景相机版本VGGT，上海科大。静态场景，离线。

  构造了新的数据集PanoCity: 超过120000张带位姿和深度标注的全景图。虚拟数据集、室外场景、主要静态场景、不同天气条件。

  方法：

  1. DINOv2编码。和VGGT类似的交替注意力模块。

  2. 从标准的 2D 网格编码改为球感位置编码 (Spherical-aware PE)

  3. 数据增强改用了SO(3)旋转增强，并随机定target frame。
  
  8张A100训练10天。用的数据集：PanoCity、Matterport3D、Stanford2D3D 和 Structured3D。

- [VGGT-360](https://arxiv.org/abs/2603.18943)
  

## 数据集

- [360+x](https://x360dataset.github.io/)

  动态场景。无3D标注。室内室外。

- [Pano3D](https://vcl3d.github.io/Pano3D/)

  静态场景。有3D标注。室内。

- [Panorama_498](https://github.com/CrazyPhilip/Panorama_498)

- [H-OmniStereo](https://github.com/JIANG-CX/H-OmniStereo)

  合成数据集。双全景相机。动态场景。室内外。暂未开源。

- [OmniStereo](https://sites.google.com/view/snu-rvlab/research/omnistereo)

  合成数据集。动态场景。有depth标注，室外驾驶场景。

- [SUN360](https://3dvision.princeton.edu/projects/2012/SUN360/)

  静态场景。

- [Matterport3D](https://huggingface.co/datasets/Gen3DF/Matterport3d/tree/main/matterport3d)

  静态场景。benchmark。

- [Holo360D](https://huggingface.co/datasets/ouou123/Holo360D)

  静态场景。室内外。真实数据集。有depth，camera poses。2.66T。ECCV2026。

- [OmniHorizon](https://omnihorizon.github.io/)

  暂未开源。

- [Structured3D](https://huggingface.co/datasets/Gen3DF/Structured3D)

- [Stanford 2D-3D-S](https://github.com/alexsax/2D-3D-Semantics)



## 方法方案

### 实验

评测数据集

- [PanoCity]

  相机位姿、深度、点云重建

- [Matterport3D]

  相机位姿、深度、点云重建

- [2D-3D-S](https://github.com/alexsax/2D-3D-Semantics)

  相机位姿、深度、室内点云重建。[下载链接](https://sdss.redivis.com/datasets/f304-a3vhsvcaf)

  test split是area_5b序列。

- [Structured3D](https://zju-kjl-jointlab-azure.kujiale.com/Structured3D/README.txt)

  弹幕深度估计

- [Pano3D]

  zero-shot测深度



