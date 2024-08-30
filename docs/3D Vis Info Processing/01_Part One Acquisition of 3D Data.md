# Part One: Acquisition of 3D Data

2D -> 3D: ill-posed problem

Representation of 3D data:

- 3D data clouds. 点云。一堆三维点，并没有相对关系，并没有组织起来。空间的欧氏距离往往不work，往往需要用到所在平面拓扑的测地距离。
- range images/ depth images. 深度图。h*w的二维矩阵，每个元素的像素值表示深度。可绘制出shaded image，灰度图。
- needle maps (2.5D data，这种描述只是含义上的，非准确). 法向图。单位法向量长度为1，有2个自由度，所以图中每个元素可以有2个信息组成法向信息。相对于其他方式，少了深度信息，因为它是一种一阶微分量，需要加边界条件才能积分出真实信息。

Approaches to 3D Data Sensing

- Numbers of data:
  - one-point sensing
  - dense data sensing
- Sensing methods:
  - touching sensing 接触式
  - non-touching methods 非接触式
    - passive methods
      - shading and texture analysis （shape from shading，拍摄灰度/深度信息，恢复出三维结构）
      - stereo cameras （立体摄像机）
      - motion analysis （shape from motion，通过移动传感器获得序列信息，恢复出三维结构）
      - lens focusing （调整焦距来获得深度信息。关键问题在于如何判断在当前焦距下聚焦在了哪些位置）
    - active methods （区别于active vision，即可以自由控制相机观测视角的视觉方式）
      - photometric stereo （进行光照的干扰，变换角度等）
      - structured lights （结构光）
      - radar sensing （雷达）





## Chapter Two: Recovery of 3D Features from Intensity Image — Shape-from-Shading 由图像灰度恢复物体表面几何信息

光源属性（角度、点/线/面光源），物体表面的反射特性

light -> object surfaces -> camera

### 2.1 辐射学

- 辐射度：测定光源的亮度

  单位投影面积向单位立体角发射的能量流

- 辐照度：测定物体表面的被辐射状态

  物体表面单位面积接收的能量流

- 立体角：从远处观察某一面片时所看到此面的大小

设有离$s_0$距离为$r$的面积元$dA$，其发现方向于该点方向之间的夹角为$\theta$，则$dA$与$s_0$形成的立体角为：

$$d_\omega=\frac{dA\cos{\theta}}{r^2}$$

#### 2.1.1 光源辐射度与物体表面辐照度的关系

$L_i$：光源的辐射度

$r$：光源至物体表面的距离

$\theta_1$：物体表面法线与AB间的夹角

$\theta_2$：光源面法线与AB间的夹角

此时，到达物体表面的能量流为$\phi=l\cdot d\omega$。

$l$：从光源向物体面积元方向单位立体角所辐射的能量，$l=L_i\cdot dB\cdot\cos\theta_2$。

$d\omega$：从光源所看到的物体面积元所形成的立体角，$d\omega_1=(dA\cdot\cos\theta_1)/r^2$。

这里，

$\phi=(L_i\cdot dB\cos\theta_2)(dA\cos\theta_1)/r^2$

$=L_i\cdot dA\cos\theta_1(dB\cos\theta_2)/r^2=L_i\cdot dA\cos\theta_1 d\omega_2$

其中$d\omega_2$：从物体看到的光源面积元的立体角。

这事，物体表面的辐照度为$E_i=\frac{\phi}{dA}=L_i\cdot d\omega_2\cos\theta_1$。

假定光源为点光源，则$d\omega_2$为$\delta$函数，则有：$E_i\propto L_i\cdot\cos\theta_1$。

#### 2.1.2 物体入射辐照度与反射辐射度的关系

一般物体表面的反射特性可用反射辐射度与入射辐照度的比来表示。这个比值就称作**双向反射分布函数（BRDF, Bidirectional Reflection Distribution Function）**：

$$f(\theta_i,\phi_i,\theta_e,\phi_e)=\frac{L_e(\theta_i,\phi_i,\theta_e,\phi_e)}{E_i(\theta_i,\phi_i)}$$

- 朗伯反射（Lambertian reflection）：乱反射

  在一个固定点光源的照射下，从所有的视线方向观测都具有相同的亮度。

  此时$f_e=\frac{1}{\pi}$，分母为常数，只需要满足各个方向的反射积分起来满足能量守恒即可。

- 镜面反射：

  $f_s=\frac{\delta(\theta_e-\theta_i)\delta(\phi_e-\phi_i-z)}{\sin\theta_i\cos\theta_i}$

  

#### 2.1.3 物体反射辐射度与图像辐照度的关系

$z$：物体与凸透镜之间的距离。

$f$：焦距，凸镜与图像面之间的距离。

设物体面积元$dA$的辐射度为$L_e$。凸镜的面积为$s_l=\pi(d/2)^2$。

从$dA$看到的凸镜所形成的立体角为：$d\omega=s_l\cos\alpha/(z/\cos\theta)^2$

$dI$的辐照度为：$E=\frac{\phi}{dI}=L_e\pi(d/2)^2\frac{\cos^2\alpha}{z^2}\cos\theta\frac{dA}{dI}$

从成像结构来看，$dA$与$dI$所形成的立体角必须相等：$\omega_a=\omega_i$

$\omega_a=dA\cos\theta/(\frac{z}{\cos\alpha})^2=\frac{dA}{z^2}\cos\theta\cos^2\alpha$

$\omega_i=dI\cos\alpha/(\frac{f}{\cos\alpha})^2=\frac{dI}{f^2}\cos^3\alpha$

由$\omega_a=\omega_i$则有：$\frac{dA}{dI}=\frac{z^2\cos\alpha}{f^2\cos\theta}$

则$E=L_e\frac{\pi}{4}(\frac{d}{f})^2\cos^4\alpha$。当摄像机离物体足够远时，$\alpha$近似为0。





将三个过程整合起来，则有：$E=\rho L_i\cos\theta_1$。条件为：理想点光源，朗伯反射，摄像机离物体足够远。

不过，尽管可以通过灰度$E$反解得到物体表面法向与光源的夹角$\theta_1$，但是三维的法向量本身依然不是唯一的。



### 2.2 反射图（reflectance map）

前面所得到的成像方程有两个问题：

1. 这个方程式是以光源方向为基准的。应该将其转换成以摄像机坐标系为基准的描述。
2. 方程式中的$\cos\theta_1$是对象物表面几何特性的隐式表示。

#### 2.2.1 三维形状的表示：梯度空间

对于物体表面的每一点（x,y,z），可表示为$z=f(x,y)$，其中$x,y$是参数，即（成像平面上）像素点的坐标。
则此点的梯度为$(p,q)=\left(\dfrac{df(x,y)}{dx},\dfrac{df(x,y)}{dy}\right)=(\dfrac{dz}{dx},\dfrac{dz}{dy})$

物体表面上所有梯度向量$(p,q)$的集合就是形状的梯度空间。

由面上的单位法线向量则为$\vec{n}(x,y)=\frac{(-p,-q,1)^T}{\sqrt{1+p^2+q^2}}$

设摄像机方向为$(p_c,q_c)=(0,0)$

光源方向也是梯度空间中的一点，定义为$(p_s,q_s)$，是已知的。

这时，$\cos\theta_i=\frac{1+p\cdot p_s+q\cdot q_s}{\sqrt{1+p^2+q^2}\cdot\sqrt{1+p_s^2+q_s^2}}$。

那么，物体表面的辐射度与光源辐射度的关系为$R(p,q)=\frac{L_e}{E_i}=\frac{1}{\pi}\cos\theta_i=\frac{1}{\pi}\frac{1+p\cdot p_s+q\cdot q_s}{\sqrt{1+p^2+q^2}\cdot\sqrt{1+p_s^2+q_s^2}}$。$R(p,q)$则称为此场景设定中的反射函数。

一般所得到的是灰度图像，即图像辐照度，需要一个线性变换$E(x,y)=\rho R(x,y)$。

将$R(p,q)$用等高线的形式表示，即得到反射图的离散型。



### 2.3 光度立体视觉法（photometric stereo method）

通过设置两个光源，先后得到两幅图像，则可得到两个反射图，再将这两个反射图联合求解，即可得到物体表面法线方向的唯一解。



## Chapter Three: 3D Data Acquisition —Stereoscopic Vision and Range Finders 立体视觉与深度扫描仪

### 3.1 立体视觉的原理

对于三位空间中的某一点，如果从以某一间距设置的两台摄像机可以同时观测到其图像，则根据三角测量的原理，可以计算出这一点相对于摄像机系统的三维坐标。以这种原理构造的视觉系统就称作双目立体视觉系统。

该图是从上往下看到的立体视觉系统的例子。

这里有两个摄像机分别以$O_l$与$O_r$作为投影重心，而$I_l$与$I_r$是对应的两幅图像，有两个问题需要解决：
1. 两幅图像中的对应像素匹配，即对于空间中物体表面上的任意一点，怎样找到它在左右两幅图像中的对应点。

2. 三维位置计算。根据已知摄像机的参数，计算空间中点的三维坐标。

   已知参数：

   - $T$：两幅图像投影中心$O_l$与$O_r$间的距离。通常称作立体视觉系统的基线(baseline)。
   - $f$：摄像机的焦距。
   - $z$：$P$相对于基线的距离（待求的变量）

   从三角形$\Delta P_lPP_r$和$\Delta O_lpO_r$的相似性，有$\dfrac{T+x_l-x_r}{T}=\dfrac{z-f}{z}$

   则有$z=f\cdot\dfrac{T}{d}$。这里$d=x_l-x_r$，为视差。

   通常可以得到三维信息的条件是：

   1. 已知摄像机的内部、外部参数，则可以实现完全确定的三维计算。
   2. 只知道内部参数，则重建的尺度不可确定：可计算相对深度。
   3. 对摄像机系统的参数完全未知，则重建结果存在射影几何的不确定性。

### 3.2 对应像素的匹配

1. 平滑区域的灰度变化不明显，很难将其中一点与其相邻点区分开。
2. 遮挡问题：从一台摄像机能够看到的物体的一部分，由于视线的改变在另一台摄像机中看不到。

#### 3.2.1 相关法

对于左侧图像中的任意一点，在右侧图像中寻找一点，使其邻域内的灰度分布与左侧图像点的相应灰度分布具有最大的相关值。

假设在左、右两侧图像中个有一点$P_l$与$P_r$选取以各自为中心的窗口($n\times m$)。令其窗口邻域内的灰度值分别为$I_l(i,j)$和$I_r(i,j)$，则灰度分布的相似性可定义为$D=\dfrac{1}{N}\sum_{i=1}^{n}\sum_{j=1}^{m}\left(I_l(i,j)-I_r(i,j)\right)^2$。$D$为窗口邻域内相应像素灰度差的平方和(SSD)。

考虑到灰度图像中噪声模型的影响，应进行归一化处理。

设各自窗口内灰度分布的平均值$\mu_l,\mu_r$，设方差值$\sigma_l^2,\sigma_r^2$，则有$D^{norm}=\dfrac{1}{N}\sum_{i=1}^{n}\sum_{j=1}^{m}\left(\dfrac{I_l(i,j)-\mu_l}{\sigma_l}-\dfrac{I_r(i,j)-\mu_r}{\sigma_r}\right)^2$

$=\dfrac{1}{N}\sum_{i=1}^{n}\sum_{j=1}^{m}\left\{\dfrac{(I_l(i,j)-\mu_l)^2}{\sigma_l^2}+\dfrac{(I_r(i,j)-\mu_r)^2}{\sigma_r^2}-2\dfrac{(I_l(i,j)-\mu_l)(I_r(i,j)-\mu_r)}{\sigma_l\sigma_r}\right\}=2-2C$

其中$C=\dfrac{1}{N}\sum_{i=1}^{n}\sum_{j=1}^{m}\dfrac{(I_l(i,j)-\mu_l)(I_r(i,j)-\mu_r)}{\sigma_l\sigma_r}$，为两个窗口内灰度分布的相关系数。（可以类比看作是两个向量归一化后求夹角大小）

相关法没办法解决“开口问题”。

#### 3.2.2 特征匹配法

特征匹配法是在抽取图像特征的基础上进行匹配，由于图像特征往往位于信息变化剧烈的地方，又有对于视点、光照的不变性，所以具有较好的鲁棒性。

特征：边界点、线段、边角点

优化的对应关系计算：图模型(graph model)。（在一张图片中将所有特征用图模型给组织起来）

在优化过程中可使用以下启发式约束条件：

1. 兼容性。特征间的相互关系相似。
2. 唯一性。一方的特征不能与另一方两个以上的特征相对应。
3. 连续性。作为结果得到的平滑区域的视差应该是平滑的。

#### 3.2.3 基于极线约束的匹配

对于一个双目立体视觉系统来说，两条投影直线$O_lP$与$O_rP$必须在$P$点相交，即$O_lPO_r$在一个平面上，称作该系统的极平面(epipolar plane)。极平面与图像面相交，交线为一直线，称作极线(epipolar line)

基线与两图像面的交点称作极点(epipoles)，它是对方投影中心的投影。

从中可以看出，右侧图像中的极线就是左侧摄像机中$O_lP$在右侧图像中的投影。那么对应点一定存在于右侧图像中的极线上。

### 3.3 深度扫描仪

