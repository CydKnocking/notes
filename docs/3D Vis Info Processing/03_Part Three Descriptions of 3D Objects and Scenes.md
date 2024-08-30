# Part Three: Descriptions of 3D Objects and Scenes

3D 点云的问题：

- 点与点之间没用相互关系
- 数据中的冗余量很大
- 图形硬件处理的困难（处理三角形面片会更加容易，处理点云比较复杂）
- 。。。

## 第六章 曲面曲率及其计算方法

### 6.1 曲面的几何特性

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

### 6.2 曲面曲率

对于曲面上的任意一点，可以给出通过此点的无数条曲线。可以计算无数个对应于这些曲线的曲率。一般可通过改变$(du,dv)$来产生这些曲线。

$k(u,v,du,dv)=\dfrac{-\vec{dx}\cdot\vec{dn}}{\vec{dx}\cdot\vec{dx}}=\dfrac{II(u,v,du,dv)}{I(u,v,du,dv)}=\dfrac{Ldu^2+2Mdudv+Ndv^2}{Edu^2+2Fdudv+Gdv^2}$。法曲率$(du,dv)$。

在对应于所有的$(du,dv)$的法曲率中，其最大值与最小值$k_1,k_2$是唯一确定的。最大值与最小值称作曲面点$(u,v)$的主曲率。对应于主曲率的方向$(du,dv)$就称作主方向。

利用第一与第二基本形式的矩阵要素，可知主曲率$k_1$与$k_2$是方程式$(EG-F^2)\lambda^2-(EN+GL-2FM)\lambda+(LN-M^2)=0$的两个根。设主方向为$\vec{\omega}=\zeta\vec{x}_u+\eta\vec{x}_v$，并设$\phi=\zeta/\eta$，$\phi$即为方程式$(LF-EM)\phi^2+(LG-FN)\phi+(MG-FN)=0$的两个根。

可以证明任意曲面点的两个主方向总是相互垂直的。

由主曲率的求解方程式，可知$K=k_1k_2=\dfrac{LN-M^2}{EG-F^2},H=\dfrac{k_1+k_2}{2}=\dfrac{EN+GL-2FM}{2(EG-F^2)}$，前者为高斯曲率，后者为平均曲率。

### 6.3 图曲面的曲率计算

深度图像中的曲面可以表示为$\vec{x}(u,v)=(u,v,f(u,v))^T$

通常，这种曲面称作图曲面（Graph Surface）或Monge Patch。则有$\vec{x}_u=(1,0,f_u)^T,\vec{x}_v=(0,1,\vec{f}_v)^T,\vec{x}_{uu}=(0,0,f_{uu})^T,\vec{x}_{vv}=(0,0,f_{vv})^T,\vec{x}_{uv}=(0,0,f_{uv})^T$

同时，$\vec{n}=\dfrac{(f_u, f_v, 1)^T}{\sqrt{1+f_u^2+f_v^2}},E=g_{11}=1+f_u^2,F=g_{12}=f_uf_v,G=g_{22}=1+f_v^2$

$L=b_{11}=\dfrac{f_{uu}}{\sqrt{1+f_u^2+f_v^2}},M=b_{12}=\dfrac{f_{uv}}{\sqrt{1+f_u^2+f_v^2}},N=b_{22}=\dfrac{f_{vv}}{\sqrt{1+f_u^2+f_v^2}}$

则$K=\dfrac{f_{uu}f_{vv}-f_{uv}^2}{(1+f_u^2+f_v^2)^2},H=\dfrac{1}{2}\cdot\dfrac{(1+f_v^2)f_{uu}+(1+f_u^2)f_{vv}-2f_uf_vf_{uv}}{(1+f_u^2+f_v^2)^{3/2}}$



## Chapter Seven: Global Description of Surfaces of 3D Objects – Parametric Representation 曲面的参数表示与超二次曲面

参数表示的优点：

1. 能用少量的参数表示大量的数据
2. 便于用解析的方法进行处理
3. 能够将数据转换为高层的符号形式

### 7.1 二次曲面

$f(x,y,z)=a_{11}x^2+a_{22}y^2+a_{33}z^2+2a_{12}xy+2a_{13}xz+2a_{23}yz+2a_{41}x+2a_{42}y+2a_{43}z+a_{44}$

令$f(x,y,z)=0$。

通过平行移动、旋转、尺度变换等处理，可将上述形式转换成标准形。

$p_1x^2+p_2y^2+p_3z^2=1\quad(p_1\leq p_2\leq p_3,\ p_1,p_2,p_3>0)$，椭球

$p_1x^2+p_2y^2-p_3z^2=1$，单叶双曲面

$p_1x^2-p_2y^2-p_3z^2=1$，双叶双曲面

$p_1x^2+p_2y^2=z$，椭圆抛物面

这种曲面还可以退化为一些特种曲面

$p_1x^2+p_2y^2=1$，椭圆柱

$p_1x^2-p_2y^2=1$，双曲柱

$p_1x^2=y$，抛物柱

### 7.2 一般化圆柱（generalized cylinder）

使用一般化圆柱表示物体形状需定义两个函数

- 中心轴曲面
- 沿中心轴变化的截面曲线

上述截面与中心轴始终垂直。

在$(x,y,z)$空间中，$\vec{a}(s)=(x(s),y(s),z(s))^T$，$\vec{a}(s)$表示一般化圆柱的中心轴，$s$是曲线的弧长。

定义截面坐标系$\vec{t}(s)=\dfrac{\vec{a}'(s)}{|\vec{a}'(s)|}$，$\vec{n(s)}=\dfrac{\vec{a}''(s)}{|\vec{a}''(s)|}$，$\vec{b}(s)=\vec{t}(s)\times\vec{n}(s)$，分别为切向量，主法线向量，从法线向量。

在截面坐标系中，则可在$(\vec{n}(s),\vec{b}(s))$平面上定义截面形状曲线为$(x(s,r),y(s,r))^T$。

则得到一般化圆柱为$\vec{B}(r,s)=\vec{a}(s)+x(s,r)\vec{n}(s)+y(s,r)\vec{b}(s)$

Geon，用一般化圆柱构成基本物体。

### 7.3 超二次曲面（super quadircs）

#### 7.3.1 球面外积

设有二维曲线

$\vec{m}(\eta)=(m_1(\eta)\quad m_2(\eta))^T,\ \eta_0\leq\eta\leq\eta_1$

$\vec{h}(\omega)=(h_1(\omega)\quad h_2(\omega))^T,\ \omega_0\leq\omega\leq\omega_1$

定义$\vec{x}(\eta,\omega)=\vec{m}(\eta)\circ\times\vec{h}(\omega)=(m_1(\eta)h_1(\omega)\quad m_1(\eta)h_2(\omega)\quad m_2(\eta))^T$

这种运算称作$\vec{m}(\eta)$与$\vec{h}(\omega)$的球面外积（Spherical product）

例：

1. $\vec{m}(\eta)=\left(\matrix{\cos\eta \\ \sin\eta}\right),\quad-\dfrac{\pi}{2}\leq\eta\leq\dfrac{\pi}{2}$

   $\vec{h}(\omega)=\left(\matrix{\cos\omega \\ \sin\omega}\right),\quad -\pi\leq\omega\leq\pi$

   则有$\vec{x}(\eta,\omega)=(\cos\eta\cos\omega\quad \cos\eta\sin\omega\quad \sin\eta)^T=(x\quad y\quad z)^T,\quad x^2+y^2+z^2=1$

2. $\vec{m}(\eta)=\left(\matrix{1+\cos\eta \\ \sin\eta}\right),\quad -\pi\leq\eta\leq\pi$

   $\vec{h}(\omega)=\left(\matrix{\cos\omega \\ \sin\omega}\right),\quad -\pi\leq\omega\leq\pi$

#### 7.3.2 超二次曲面(superquadriccs)

设$c_\eta=\cos\eta,s_\eta=\sin\eta,c_\omega=\cos\omega,s_\omega=\sin\omega$。

在球面外积的定义中，设$\left\{\matrix{\vec{m}(\eta)=\left(\matrix{c_\eta^{\varepsilon_1}\\a_3s_\eta^{\varepsilon_1}}\right),-\dfrac{\pi}{2}\leq\eta\leq\dfrac{\pi}{2}\\\vec{h}(\omega)=\left(\matrix{a_1c_\omega^{\varepsilon_2}\\a_2s_\omega^{\varepsilon_2}}\right),-\pi\leq\omega\leq\pi}\right.$，则有曲面$\vec{\pi}(\eta,\omega)=\left(\matrix{a_1c_\eta^{\varepsilon_1}c_\omega^{\varepsilon_2}\\a_2c_\eta^{\varepsilon_1}s_\omega^{\varepsilon_2}\\a_3s_\eta^{\varepsilon_1}}\right)$为超二次曲面。

消除显示表示中的参数$\eta,\omega$，则得到曲面的隐式表示：

$f(x,y,z)=\left(\left(\dfrac{x}{a_1}\right)^{\frac{2}{\varepsilon_2}}+\left(\dfrac{y}{a_2}\right)^{\frac{2}{\varepsilon_2}}\right)^{\frac{\varepsilon_2}{\varepsilon_1}}+\left(\dfrac{z}{a_3}\right)^{\frac{2}{\varepsilon_1}}=1$

通过改变$\varepsilon_1,\varepsilon_2$的取值，可得到不同的曲面。当$\varepsilon_1<1,\varepsilon_2<1$，曲面逼近立方体。当$\varepsilon_1>>1,\varepsilon_2>>1$，则曲面接近于星形。

对于空间中的一点，可以判断其在超二次曲面上的位置。

$f(x_0,y_0,z_0)=1$，$(x_0,y_0,z_0)$在这个超二次曲面上。$>1$，在外部。$<1$在内部。

这时可定义，对于实测数据$\vec{P_i}=(x_i,y_i,z_i),i=1,\cdots,N$，$E=\sum_{i=1}^N|f(x_i,y_i,z_i)-1|^2$。$E$为优化曲面的误差函数。

在实际求解过程中，需要求解11个未知变量：$a_1,a_2,a_3,\varepsilon_1,\varepsilon_2,T_x,T_y,T_z,\theta,\phi,\varphi$

变形（deformation）：全局变形，局部变形

## Chapter Eight: 三维模型表面的网格化表示

### 8.1 标量数据的边界抽取：Marching Squares法

**标量数据**：数据的每一点都附加了一个标量值

边界抽取：寻找标量数据中具有某一标量值的点的连线。

算法的基本思想：

1. 将数据平面分成局部四方块（squares，cells）

2. 然后在每个四方块内独立分析边界的存在情况

   对每个顶点：$s_i<c$，在边界$C$的外部，取0；反之取1。

   通过顶点的编码，查找该四方块内边界的连接关系。$2^4=16$种连接方式

3. 确定相交位置：线性插值

4. 对每一个四方块进行处理后即可将得到完整连线。

这个算法在上世纪被发明时，研究者用串行处理的方法思考，实际上这个方法可以对每个四方块并行计算。

在某些情况下具有歧义。

### 8.2 三维标量数据的边界抽取：Marching Cubes法

三维标量数据（三维体数据）

方法与上一节大同小异，不过在第2步中有$2^8=256$种连接方式。上世纪，每个cube都要查找256种连接方式是一件十分耗计算量的事，不过有研究者发现其中只有15种连接方式是独立的。

同样，也存在歧义性。

SDF：Signed Distance Function，点在面上为0，在体外为+，在体内为-。

从点云数据转换为三维空间的SDF标量场，用SDF标量场应用Marching Cubes法。





