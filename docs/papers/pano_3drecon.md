本文档为全景相机做三位重建/四维重建的相关论文的整理。

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

- [OmniStereo](https://sites.google.com/view/snu-rvlab/research/omnistereo)

  合成数据集。动态场景。有depth标注，室外驾驶场景。

- [SUN360]()

- [Matterport3D](https://niessner.github.io/Matterport/)

- [Holo360D](https://huggingface.co/datasets/ouou123/Holo360D)

- [OmniHorizon](https://omnihorizon.github.io/)

- [Stanford2D3D]()

- [Structured3D]()

