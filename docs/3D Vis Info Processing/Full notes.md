
## Part One: Acquisition of 3D Data

### Chapter One: Introduction

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





### Chapter Two: Recovery of 3D Features from Intensity Image — Shape-from-Shading 由图像灰度恢复物体表面几何信息

光源属性（角度、点/线/面光源），物体表面的反射特性

light -> object surfaces -> camera

#### 2.1 辐射学

- 辐射度：测定光源的亮度

  单位投影面积向单位立体角发射的能量流

- 辐照度：测定物体表面的被辐射状态

  物体表面单位面积接收的能量流

- 立体角：从远处观察某一面片时所看到此面的大小

设有离$s_0$距离为$r$的面积元$dA$，其发现方向于该点方向之间的夹角为$\theta$，则$dA$与$s_0$形成的立体角为：

$$d_\omega=\frac{dA\cos{\theta}}{r^2}$$

##### 2.1.1 光源辐射度与物体表面辐照度的关系

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

##### 2.1.2 物体入射辐照度与反射辐射度的关系

一般物体表面的反射特性可用反射辐射度与入射辐照度的比来表示。这个比值就称作**双向反射分布函数（BRDF, Bidirectional Reflection Distribution Function）**：

$$f(\theta_i,\phi_i,\theta_e,\phi_e)=\frac{L_e(\theta_i,\phi_i,\theta_e,\phi_e)}{E_i(\theta_i,\phi_i)}$$

- 朗伯反射（Lambertian reflection）：乱反射

  在一个固定点光源的照射下，从所有的视线方向观测都具有相同的亮度。

  此时$f_e=\frac{1}{\pi}$，分母为常数，只需要满足各个方向的反射积分起来满足能量守恒即可。

- 镜面反射：

  $f_s=\frac{\delta(\theta_e-\theta_i)\delta(\phi_e-\phi_i-z)}{\sin\theta_i\cos\theta_i}$

  

##### 2.1.3 物体反射辐射度与图像辐照度的关系

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



#### 2.2 反射图（reflectance map）

前面所得到的成像方程有两个问题：

1. 这个方程式是以光源方向为基准的。应该将其转换成以摄像机坐标系为基准的描述。
2. 方程式中的$\cos\theta_1$是对象物表面几何特性的隐式表示。

##### 2.2.1 三维形状的表示：梯度空间

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



#### 2.3 光度立体视觉法（photometric stereo method）

通过设置两个光源，先后得到两幅图像，则可得到两个反射图，再将这两个反射图联合求解，即可得到物体表面法线方向的唯一解。



### Chapter Three: 3D Data Acquisition —Stereoscopic Vision and Range Finders 立体视觉与深度扫描仪

#### 3.1 立体视觉的原理

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

#### 3.2 对应像素的匹配

1. 平滑区域的灰度变化不明显，很难将其中一点与其相邻点区分开。
2. 遮挡问题：从一台摄像机能够看到的物体的一部分，由于视线的改变在另一台摄像机中看不到。

##### 3.2.1 相关法

对于左侧图像中的任意一点，在右侧图像中寻找一点，使其邻域内的灰度分布与左侧图像点的相应灰度分布具有最大的相关值。

假设在左、右两侧图像中个有一点$P_l$与$P_r$选取以各自为中心的窗口($n\times m$)。令其窗口邻域内的灰度值分别为$I_l(i,j)$和$I_r(i,j)$，则灰度分布的相似性可定义为$D=\dfrac{1}{N}\sum_{i=1}^{n}\sum_{j=1}^{m}\left(I_l(i,j)-I_r(i,j)\right)^2$。$D$为窗口邻域内相应像素灰度差的平方和(SSD)。

考虑到灰度图像中噪声模型的影响，应进行归一化处理。

设各自窗口内灰度分布的平均值$\mu_l,\mu_r$，设方差值$\sigma_l^2,\sigma_r^2$，则有$D^{norm}=\dfrac{1}{N}\sum_{i=1}^{n}\sum_{j=1}^{m}\left(\dfrac{I_l(i,j)-\mu_l}{\sigma_l}-\dfrac{I_r(i,j)-\mu_r}{\sigma_r}\right)^2$

$=\dfrac{1}{N}\sum_{i=1}^{n}\sum_{j=1}^{m}\left\{\dfrac{(I_l(i,j)-\mu_l)^2}{\sigma_l^2}+\dfrac{(I_r(i,j)-\mu_r)^2}{\sigma_r^2}-2\dfrac{(I_l(i,j)-\mu_l)(I_r(i,j)-\mu_r)}{\sigma_l\sigma_r}\right\}=2-2C$

其中$C=\dfrac{1}{N}\sum_{i=1}^{n}\sum_{j=1}^{m}\dfrac{(I_l(i,j)-\mu_l)(I_r(i,j)-\mu_r)}{\sigma_l\sigma_r}$，为两个窗口内灰度分布的相关系数。（可以类比看作是两个向量归一化后求夹角大小）

相关法没办法解决“开口问题”。

##### 3.2.2 特征匹配法

特征匹配法是在抽取图像特征的基础上进行匹配，由于图像特征往往位于信息变化剧烈的地方，又有对于视点、光照的不变性，所以具有较好的鲁棒性。

特征：边界点、线段、边角点

优化的对应关系计算：图模型(graph model)。（在一张图片中将所有特征用图模型给组织起来）

在优化过程中可使用以下启发式约束条件：

1. 兼容性。特征间的相互关系相似。
2. 唯一性。一方的特征不能与另一方两个以上的特征相对应。
3. 连续性。作为结果得到的平滑区域的视差应该是平滑的。

##### 3.2.3 基于极线约束的匹配

对于一个双目立体视觉系统来说，两条投影直线$O_lP$与$O_rP$必须在$P$点相交，即$O_lPO_r$在一个平面上，称作该系统的极平面(epipolar plane)。极平面与图像面相交，交线为一直线，称作极线(epipolar line)

基线与两图像面的交点称作极点(epipoles)，它是对方投影中心的投影。

从中可以看出，右侧图像中的极线就是左侧摄像机中$O_lP$在右侧图像中的投影。那么对应点一定存在于右侧图像中的极线上。

#### 3.3 深度扫描仪



## Part Two: Integration of 3D data

### Chapter Four: 三维数据的运动恢复

视点的差异与对象物的移动是一个可逆过程。一般将通过数据序列的分析来求解传感器运动的过程称为运动恢复。而将不同视点采集到的数据整合到同一坐标系的处理称作配准（registration）。

#### 4.1 不同视点所得到点群的刚体运动

假设三维空间的两个点群：$P={\vec{P_i}},P'={\vec{P'_i}},i=1,2,\cdots$。$P'$是$P$通过某种运动而得到两点群之间的关系满足$\vec{P_i'}=R\vec{P_i}+\vec{T}+\vec{N_i}$。

这里，$R$为旋转矩阵，$\vec{T}$为平移向量，$\vec{N_i}$为测量噪声向量，$\vec{N_i}=(N_{ix},N_{iy},N_{iz})^T$通常$\vec{N_i}$是白色噪声。

#### 4.2 三维空间中的旋转

首先考虑在$z$轴周围旋转$\theta$角的情况。$R_{z\theta}=\left[\matrix{\cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1}\right]=\left[\matrix{c\theta & -s\theta & 0 \\ s\theta & c\theta & 0 \\ 0 & 0 & 1}\right]$。

考虑两个坐标系：

- $OXYZ$：固定的基准坐标系。
- $OUVW$：随物体（点群）而旋转的坐标系

##### 4.2.1 基于欧拉角的旋转表示

旋转的合成规则：

1. 在$OZ$轴周围旋转$\phi$角
2. 在$OU$轴周围旋转$\theta$角
3. 在$OW$轴周围旋转$\psi$角

旋转矩阵为：$R_{\phi,\theta,\psi}=R_{z\phi}R_{u\theta}R_{w\psi}=\left[\matrix{c\phi & -s\phi & 0 \\ s\phi & c\phi & 0 \\ 0 & 0 & 1}\right]\left[\matrix{1 & 0 & 0 \\ 0 & c\theta & -s\theta \\ 0 & s\theta & c\theta}\right]\left[\matrix{c\psi & -s\psi & 0 \\ s\psi & c\psi & 0 \\ 0 & 0 & 1}\right]$。（这里的左右反了，mark一下）

##### 4.2.2 RPY法

合成规则：

1. 绕$OX$轴旋转$\psi$角  yaw
2. 绕$OY$轴旋转$\theta$角  pitch
3. 绕$OZ$轴旋转$\theta$角  roll

因此，$R_{\phi,\theta,\psi}=R_{z\phi}R_{y\theta}R_{x\psi}$，从左到右是Roll，Pitch，Yaw

##### 4.2.3 绕空间中任意轴的旋转

首先构造一个平面$V$与旋转中心轴$\vec{w}$组成的坐标系。这里$V$与$\vec{w}$垂直，同时通过$\vec{R}$与$\vec{R'}$的平面，并将$\vec{PR}$方向以及与此垂直的$\vec{PR}$方向作为$V$上的坐标轴，分别用$\vec{u}$与$\vec{v}$来表示，则有$\vec{R'}=\vec{OP}+\vec{PR}\cos\theta+\vec{PQ}\sin\theta$。

用向量表示，则有：$\vec{OP}=(\vec{R}\cdot\vec{w})\cdot\vec{w},\vec{PQ}=\vec{w}\times\vec{R},\vec{PR}=\vec{R}-(\vec{R}\cdot\vec{w})\cdot\vec{w}$

$\vec{R'}=(\vec{R}\cdot\vec{w})\cdot\vec{w}+\cos\theta\left\{\vec{R}-(\vec{R}\cdot\vec{w})\cdot\vec{w}\right\}+\sin\theta(\vec{w}\times\vec{R})=\cos\theta\vec{R}+\sin\theta\vec{w}\times\vec{R}+(1-\cos\theta)(\vec{R}\cdot\vec{w})\cdot\vec{w}$

设$\vec{w}=(\lambda,\mu,\nu)^T$，这里$\lambda^2+\mu^2+\nu^2=1$

$\vec{R'}=R_{\cos\theta}\vec{R}$

$R_{\cos\theta}=\left[\matrix{c\theta+\lambda^2(1-c\theta) & \lambda\mu(1-c\theta)-\nu s\theta & \nu\lambda(1-c\theta)+\mu s\theta \\ \lambda\mu(1-c\theta)+\nu s\theta & c\theta+\mu^2(1-c\theta) & \mu\nu(1-c\theta)-\lambda s\theta \\ \nu\lambda(1-c\theta)-\mu s\theta & \mu\nu(1-c\theta)+\lambda s\theta & c\theta+\nu^2(1-c\theta) }\right]$

**四元数（quaternion）**

四元数是由四个元素组成的一个数组。

给定一个标量$q_0$以及一个向量$\vec{q}=(q_x,q_y,q_z)^T$，可将其形成一个四元数$\breve{q}=(q_0,\vec{q})$。

这里$\breve{q}=q_0+iq_x+jq_y+kq_z$，这里$i^2=j^2=k^2=-1,ij=k,jk=i,ki=j$。

四元数乘积的定义为：设$\breve{q_1}=(q_{10},\vec{q_1}),\breve{q_2}=(q_{20},\vec{q_2})$，$\breve{q_1}\cdot \breve{q_2}=(q_{10}q_{20}-\vec{q_1}\cdot\vec{q_2},\vec{q_1}\times\vec{q_2}+q_{20}\vec{q_1}+q_{10}\vec{q_2})$，并且$\breve{q}=(q_0,\vec{q})$的共轭为$\bar{\breve{q}}=(q_0,-\vec{q})$。

四元数具有以下性质：

1. $|\breve{q}|^2=\breve{q}\cdot\bar{\breve{q}}=q_0^2+|\vec{q}|^2$
2. $|\breve{q}\cdot \breve{q}'|^2=|\breve{q}|^2\cdot|\breve{q}'|^2$

使用四元数可以有效地表示空间中的旋转。

设$\breve{r}=(0,\vec{R}),\breve{r}'=(0,\vec{R'})$，同时设$\breve{q}=\left(\cos\dfrac{\theta}{2},\sin\dfrac{\theta}{2}\vec{w}\right)$，通过使用罗德里格斯公式，可得$\breve{r}'=\breve{q}\cdot \breve{r}\cdot\bar{\breve{q}}$

#### 4.3 点群运动的计算

对于两个点群$P,P_i$，$\vec{P}=R\vec{P_i}+\vec{T}+\vec{N_i}$。利用最小二乘法，可将此问题转化为使$E^2=\sum_{i=1}^N|\vec{P_i'}-(R\vec{P_i}+\vec{T})|^2$。

最小的$R$与$\vec{T}$的估计问题。

设$\vec{P}=\dfrac{1}{N}\sum\vec{P_i},\vec{P'}=\dfrac{1}{N}\sum\vec{P_i'}$，并做变换$\vec{d_i}=\vec{P_i}-\vec{P},\vec{d_i'}=\vec{P_i'}-\vec{P'}$，则有$E^2=\sum|(d_i'+\vec{P'})-[R(\vec{d_i}+\vec{P})+\vec{T}]|^2=\sum|(\vec{d_i}-R\vec{d_i})+(\vec{P'}-(R\vec{P}+T))|^2=\sum|\vec{d_i'}-R\vec{d_i}|^2$。

这时，优化问题可分解为

- 求使$E^2$最小的$\hat{R}$
- 求$\vec{T}$，$\vec{T}=\vec{P'}-\vec{P}$

##### 4.3.1 利用四元数求$R$

用四元数表示$\vec{d_i'},\vec{d_i}$：$\breve{d_i'}=(0,\vec{d_i'}),\breve{d_i}=(0,\vec{d_i})$。

同时$\breve{q}=(\cos\dfrac{\theta}{2},\sin\dfrac{\theta}{2}\vec{\omega})\rightarrow R$

$E^2=\sum|\breve{d_i'}-\breve{q}\cdot\breve{d_i}\cdot\breve{\bar{q}}|^2|\breve{q}|^2=\sum|\breve{d_i'}\cdot\breve{q}-\breve{q}\cdot\breve{d_i}|^2=\sum|\breve{O_i}|^2$

这时，$\breve{O_i}=\breve{d_i'}\cdot\breve{q}-\breve{q}\cdot\breve{d_i}=(\vec{q}\cdot(\vec{d_i'}-\vec{d_i}),(\vec{d_i'}+\vec{d_i})\times\vec{q}+q_0(\vec{d_i'}-\vec{d_i}))$

设$\vec{u}=(u_1,u_2,u_3)^T,\vec{x}=(x_1,x_2,x_3)^T$，有$\vec{u}\times\vec{x}=\vec{x}U^M$，这里$U^M=\left[\matrix{ 0 & u_3 & -u_2 \\ -u_3 & 0 & u_1 \\ u_2 & -u_1 & 0 }\right]$

利用向量外积的这个性质，有$\breve{O}=\vec{q_4}A_i$，这里$\vec{q_4}$是将四元数转换成向量的表示$A_i=\left[\matrix{0 & (\vec{d_i'}-\vec{d_i}) \\ (\vec{d_i}-\vec{d_i'})^T & D_i^M }\right]$。

$D_i^M$为$(\vec{d_i}+\vec{d_i'})$对应于$U^M$的矩阵。

这里，$A_i$只与数据$\vec{d_i},\vec{d_i'}$有关。根据以上结果，有

$E^2=\sum|\breve{0}|^2=\sum\vec{q_4}A_iA_i^T\vec{q_4}^T=\sum\vec{q_4}B_i\vec{q_4}^T=\vec{q_4}(\sum B_i)\vec{q_4}^T=\vec{q_4}B\vec{q_4}^T$，其中$B_i=A_iA_i^T,B=\sum B_i$

$\hat{\vec{q_4}}$是$B$的最小特征值的对应的特征向量。$\hat{\vec{q_4}}=(\cos\dfrac{\theta}{2},\sin\dfrac{\theta}{2}\vec{\omega})^T$

### Chapter Five: 三维数据的配准（registration）

将从不同视点采集的数据整合起来，形成对象物的完整模型。

计算各个视点的位置关系：

1. 使用辅助传感器
2. 在场景中设置靶标（landmark）
3. 手工选取对应点
4. 自动配准

实际场景中的难点：

1. 三维点云间的对应关系未知。同时，点群中点的数量不相等
2. 由于视点的遮挡可能不存在对应点
3. 很难找到物理上完全吻合的对应点

#### 5.1 迭代最近点法的基本原理 ICP

假定已知两个点群$P,Q$，$\vec{p_i}\in P,\vec{q_i}\in Q$。这里，下标不在隐含数据间的对应关系。

设$T$为将$P$变换到$Q$的变换，其中包含平行移动与旋转的运动参数。这时假定$P$与$Q$之间的对应关系为$f:P\to Q,\quad \forall\vec{p_i}\in P,f(\vec{p_i})\in Q$。

这样，点群间运动参数的计算问题可转化为以下目标函数最小的优化问题：$D(P,Q)=\sum|T\vec{p_i}-f(\vec{p_i})|^2$

这时，可以考虑以下策略求解这个问题：根据某种几何特性对数据进行匹配，并将匹配点设为假象对应点，再根据这种对应关系求解运动参数。再利用这些参数将数据进行变换。

在新的情况下，重复上述过程。这是一个迭代的计算过程。

在确定上述假象对应点时，使用在空间位置上最近的点。

——Iterative Closest Point Method

将此过程公式化后，有求解使下式最小的优化问题$E=\sum_i^N|T\vec{p_i}-\vec{q_i}|^2$，这里$\vec{q_i}=q|\min_{\vec{q}}|T\vec{p_i}-\vec{q}||$最近点匹配。

这里，必须同时满足以下两个条件：

1. 通过$T$将$P$与$Q$整合
2. $\vec{p_i}$与$\vec{q_j}$通过$T$建立对应关系



求解配准问题，必须完成以下的优化过程：

$E=\sum_{i=1}^{N}|T\vec{p_i}-\vec{q_j}|^2$，这里$\vec{q_j}=\arg\min_{\vec{q}}|T\vec{p_i}-\vec{q}|$，即最近点匹配

这时可将整个优化过程用迭代方式求解。在某一步$k$利用前一步所得到的$T^{k-1}$，求下述问题的最优解：

$E^k=\sum_{i=1}^{N}|T^k\vec{p_i}-\vec{q_j^k}|^2$，这里$\vec{q_j^k}=\arg\min_\vec{q}|T^{k-1}\vec{p_i}-\vec{q}|$

在这一步，将$\vec{q_j^k}$看作是$\vec{p_i}$的假想对应点。

那么，三维点云的**ICP配准算法**如下：

1. 在左边点云里选择控制点$\vec{p_i}\in P$，设置$T$的初始值$T^0$。

2. 重复执行以下各步骤$k=1,2,\dots$，直到满足收敛条件。

   1. 对各个控制点$\vec{p_i}$，使其通过运动变换为$\vec{p_i}'=T^{k-1}\vec{p_i}$，求$\vec{p_i}'$的最近点$\vec{q_j}'^k$
   2. 对于此时所确定的假象对应关系$(\vec{p_i'},\vec{q_j}'^k)$，求以下优化问题的解：$E^k=\sum_{i=1}^{N}|T\cdot T^{k-1}\vec{p_i}-\vec{q_j'^k}|^2$
   3. $T^k=T\cdot T^{k-1}$

   算法收敛条件：$\delta=\dfrac{|E^k-E^{k-1}|}{M}\leq\varepsilon_e$

#### 5.2 算法求解的注意事项

##### 5.2.1 最近点

在实际求解过程中，仅仅是欧氏距离最近点不能保证两个曲面点在空间位置上最近，有种更可靠的方法是：将点$\vec{p_i}$转换成$T^{k-1}\vec{p_i}$，然后使用$T^{k-1}\vec{p_i}$的法线与$Q$的交点作为对应点$\vec{q_j}'^k$，$\vec{q_j}'^k=(T^{k-1}\vec{p_i}\cap Q)$，其中$\cap$为求交点。

这时，求$\vec{l^k}=\{\vec{a}|(T^{k-1}\vec{p_i}-\vec{a})\times\vec{n_{p_i}}=0\}$，这里$\vec{n_{p_i}}$为$T^{k-1}\vec{p_i}$的法线方向向量。

再得到$\vec{q_j}'^k=(T^{k-1}\vec{l_i})\cap Q'$，$Q'$为右边曲面的切平面。

##### 5.2.2 算法的收敛性

在此算法中，执行了两个优化过程：

- 确定假想对应关系：$d_k=\min\sum|T^{k-1}\vec{p_i}-\vec{q}'^k|^2$
- 求运动参数$T$，$E_k=\min\sum|T\cdot T^{k-1}\vec{p_i}-\vec{q}'k|^2$

首先证明$E_k\leq d_k$。

设$T=I$，则有$E_k=d_k$。

如果最小化的结果是$T\neq I$，则只能是$E_k\leq d_k$。

下一步，显示$d_{k+1}\leq E_k$

如果在$(k+1)$步与$k$步的对应关系不变，则有$d_{k+1}=E_k$。

但是在$(k+1)$步中，如果点$\vec{p_i}$的对应关系发生了变化，则说明有新的点$\vec{q_j}'^{(k+1)}$比$\vec{q_j}'^k$更靠近$\vec{p_i}$。

$|T\cdot T^k\vec{p_i}-\vec{q_j}'^{(k+1)}|\leq |T\cdot T^k\vec{p_i}-\vec{q_j}'k|$

即$d_{k+1}$变小了，$d_{k+1}\leq E_k$。

因此，得到$d_0\geq E_0\geq d_1\cdots\geq d_k\geq E_k\geq d_{k+1}\geq\cdots$，误差在不断地减小，算法是收敛的。

##### 5.2.3 控制点的选择

1. 计算量

2. 收敛速度

   尽量避免在数据中的平坦区域寻找控制点

3. 计算精度

   避免噪声多的数据区域

4. 遮挡问题

##### 5.2.4 控制点的自动选择

$E_k=\dfrac{1}{W}\sum_{i=1}^Nw_i|T\cdot T^{k-1}\vec{p_i}-\vec{q_j^k}|^2,\quad W=\sum w_i$。

$w_i$定义如下：

设$d_i=|T^{k-1}\vec{p_i}-\vec{q_j}'^{k-1}|$，$w_i=\left\{\begin{aligned}&1 & 0\leq d_i\leq \varepsilon_1 \\&\rho(\dfrac{1}{d_i}) & \varepsilon_1\leq d_i\leq \varepsilon_2 \\ &0 & \varepsilon_2\leq d_i \end{aligned}\right.$，其中$\rho(x)$为$x$的单纯增长函数，$0<\rho(x)<1$。



## Part Three: Descriptions of 3D Objects and Scenes

3D 点云的问题：

- 点与点之间没用相互关系
- 数据中的冗余量很大
- 图形硬件处理的困难（处理三角形面片会更加容易，处理点云比较复杂）
- 。。。

### Chapter Six: 曲面曲率及其计算方法

#### 6.1 曲面的几何特性

在三维空间$(x,y,z)$中，一般可用参数$u,v$将曲面表示为$S=\{\vec{x}\in R^3,[x,y,z]^T=[x(u,v),y(u,v),z(u,v)]^T,(u,v)\in D\subset R^2\}$

各坐标函数$x(u,v),y(u,v),z(u,v)$至少应具有二阶连续偏微分。

1. 曲面的第一基本形式

   因为$\vec{dx}=\dfrac{\vec{\partial x}}{\partial u}du+\dfrac{\vec{\partial x}}{\partial v}dv$，有

   $I(u,v,du,dv)=\vec{dx}\cdot\vec{dx}=Edu^2+2Fdudv+Gdv^2=\left[\matrix{du&dv}\right]\left[\matrix{g_{11} & g_{12} \\ g_{21} & g_{22}}\right]\left[\matrix{du \\ dv}\right]=\vec{du}^T[g]\vec{du}$

   其中，$g_{11}=E=\vec{x}_u\cdot\vec{x}_u,g_{12}=g_{21}=F=\vec{x}_u\cdot\vec{x}_v,g_{22}=G=\vec{x}_v\cdot\vec{x}_v$。

   矩阵$[g]$称作曲面的测度张量，同时，$[g]$是一对称矩阵，只有三个独立要素。$I(u,v,du,dv)$为在参数$(u,v)$发生微小变化$(du,dv)$时，在曲面上出现对应变化的曲线长度。

   一般，可将曲面的面积要素写为$|\vec{x}_u\cross\vec{x}_v|dudv=\sqrt{EG-F^2}dudv$

2. 曲面的第二基本形式

   $\vec{n}(u,v)=\dfrac{\vec{x}_u\times\vec{x}_v}{|\vec{x}_u\times\vec{x}_v|}$

   $II(u,v,du,dv)=-\vec{dx}\cdot\vec{dn}=Ldu^2+2Mdudv+Ndv^2=\left[\matrix{du & dv}\right]\left[\matrix{b_{11} & b_{12} \\ b_{21} & b_{22}}\right]\left[\matrix{du \\ dv}\right]=\vec{du}^T[b]\vec{du}$

#### 6.2 曲面曲率

对于曲面上的任意一点，可以给出通过此点的无数条曲线。可以计算无数个对应于这些曲线的曲率。一般可通过改变$(du,dv)$来产生这些曲线。

$k(u,v,du,dv)=\dfrac{-\vec{dx}\cdot\vec{dn}}{\vec{dx}\cdot\vec{dx}}=\dfrac{II(u,v,du,dv)}{I(u,v,du,dv)}=\dfrac{Ldu^2+2Mdudv+Ndv^2}{Edu^2+2Fdudv+Gdv^2}$。法曲率$(du,dv)$。

在对应于所有的$(du,dv)$的法曲率中，其最大值与最小值$k_1,k_2$是唯一确定的。最大值与最小值称作曲面点$(u,v)$的主曲率。对应于主曲率的方向$(du,dv)$就称作主方向。

利用第一与第二基本形式的矩阵要素，可知主曲率$k_1$与$k_2$是方程式$(EG-F^2)\lambda^2-(EN+GL-2FM)\lambda+(LN-M^2)=0$的两个根。设主方向为$\vec{\omega}=\zeta\vec{x}_u+\eta\vec{x}_v$，并设$\phi=\zeta/\eta$，$\phi$即为方程式$(LF-EM)\phi^2+(LG-FN)\phi+(MG-FN)=0$的两个根。

可以证明任意曲面点的两个主方向总是相互垂直的。

由主曲率的求解方程式，可知$K=k_1k_2=\dfrac{LN-M^2}{EG-F^2},H=\dfrac{k_1+k_2}{2}=\dfrac{EN+GL-2FM}{2(EG-F^2)}$，前者为高斯曲率，后者为平均曲率。

#### 6.3 图曲面的曲率计算

深度图像中的曲面可以表示为$\vec{x}(u,v)=(u,v,f(u,v))^T$

通常，这种曲面称作图曲面（Graph Surface）或Monge Patch。则有$\vec{x}_u=(1,0,f_u)^T,\vec{x}_v=(0,1,\vec{f}_v)^T,\vec{x}_{uu}=(0,0,f_{uu})^T,\vec{x}_{vv}=(0,0,f_{vv})^T,\vec{x}_{uv}=(0,0,f_{uv})^T$

同时，$\vec{n}=\dfrac{(f_u, f_v, 1)^T}{\sqrt{1+f_u^2+f_v^2}},E=g_{11}=1+f_u^2,F=g_{12}=f_uf_v,G=g_{22}=1+f_v^2$

$L=b_{11}=\dfrac{f_{uu}}{\sqrt{1+f_u^2+f_v^2}},M=b_{12}=\dfrac{f_{uv}}{\sqrt{1+f_u^2+f_v^2}},N=b_{22}=\dfrac{f_{vv}}{\sqrt{1+f_u^2+f_v^2}}$

则$K=\dfrac{f_{uu}f_{vv}-f_{uv}^2}{(1+f_u^2+f_v^2)^2},H=\dfrac{1}{2}\cdot\dfrac{(1+f_v^2)f_{uu}+(1+f_u^2)f_{vv}-2f_uf_vf_{uv}}{(1+f_u^2+f_v^2)^{3/2}}$







