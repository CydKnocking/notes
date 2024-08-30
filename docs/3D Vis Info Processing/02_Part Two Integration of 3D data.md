# Part Two: Integration of 3D data

## 第4章 三维数据的运动恢复

视点的差异与对象物的移动是一个可逆过程。一般将通过数据序列的分析来求解传感器运动的过程称为运动恢复。而将不同视点采集到的数据整合到同一坐标系的处理称作配准（registration）。

### 4.1 不同视点所得到点群的刚体运动

假设三维空间的两个点群：$P={\vec{P_i}},P'={\vec{P'_i}},i=1,2,\cdots$。$P'$是$P$通过某种运动而得到两点群之间的关系满足$\vec{P_i'}=R\vec{P_i}+\vec{T}+\vec{N_i}$。

这里，$R$为旋转矩阵，$\vec{T}$为平移向量，$\vec{N_i}$为测量噪声向量，$\vec{N_i}=(N_{ix},N_{iy},N_{iz})^T$通常$\vec{N_i}$是白色噪声。

### 4.2 三维空间中的旋转

首先考虑在$z$轴周围旋转$\theta$角的情况。$R_{z\theta}=\left[\matrix{\cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1}\right]=\left[\matrix{c\theta & -s\theta & 0 \\ s\theta & c\theta & 0 \\ 0 & 0 & 1}\right]$。

考虑两个坐标系：

- $OXYZ$：固定的基准坐标系。
- $OUVW$：随物体（点群）而旋转的坐标系

#### 4.2.1 基于欧拉角的旋转表示

旋转的合成规则：

1. 在$OZ$轴周围旋转$\phi$角
2. 在$OU$轴周围旋转$\theta$角
3. 在$OW$轴周围旋转$\psi$角

旋转矩阵为：$R_{\phi,\theta,\psi}=R_{z\phi}R_{u\theta}R_{w\psi}=\left[\matrix{c\phi & -s\phi & 0 \\ s\phi & c\phi & 0 \\ 0 & 0 & 1}\right]\left[\matrix{1 & 0 & 0 \\ 0 & c\theta & -s\theta \\ 0 & s\theta & c\theta}\right]\left[\matrix{c\psi & -s\psi & 0 \\ s\psi & c\psi & 0 \\ 0 & 0 & 1}\right]$。（这里的左右反了，mark一下）

#### 4.2.2 RPY法

合成规则：

1. 绕$OX$轴旋转$\psi$角  yaw
2. 绕$OY$轴旋转$\theta$角  pitch
3. 绕$OZ$轴旋转$\theta$角  roll

因此，$R_{\phi,\theta,\psi}=R_{z\phi}R_{y\theta}R_{x\psi}$，从左到右是Roll，Pitch，Yaw

#### 4.2.3 绕空间中任意轴的旋转

首先构造一个平面$V$与旋转中心轴$\vec{w}$组成的坐标系。这里$V$与$\vec{w}$垂直，同时通过$\vec{R}$与$\vec{R'}$的平面，并将$\vec{PR}$方向以及与此垂直的$\vec{PR}$方向作为$V$上的坐标轴，分别用$\vec{u}$与$\vec{v}$来表示，则有$\vec{R'}=\vec{OP}+\vec{PR}\cos\theta+\vec{PQ}\sin\theta$。

用向量表示，则有：$\vec{OP}=(\vec{R}\cdot\vec{w})\cdot\vec{w},\vec{PQ}=\vec{w}\times\vec{R},\vec{PR}=\vec{R}-(\vec{R}\cdot\vec{w})\cdot\vec{w}$

$\vec{R'}=(\vec{R}\cdot\vec{w})\cdot\vec{w}+\cos\theta\left\{\vec{R}-(\vec{R}\cdot\vec{w})\cdot\vec{w}\right\}+\sin\theta(\vec{w}\times\vec{R})=\cos\theta\vec{R}+\sin\theta\vec{w}\times\vec{R}+(1-\cos\theta)(\vec{R}\cdot\vec{w})\cdot\vec{w}$

设$\vec{w}=(\lambda,\mu,\nu)^T$，这里$\lambda^2+\mu^2+\nu^2=1$

$\vec{R'}=R_{\cos\theta}\vec{R}$

$R_{\cos\theta}=\left[\matrix{c\theta+\lambda^2(1-c\theta) & \lambda\mu(1-c\theta)-\nu s\theta & \nu\lambda(1-c\theta)+\mu s\theta \\ \lambda\mu(1-c\theta)+\nu s\theta & c\theta+\mu^2(1-c\theta) & \mu\nu(1-c\theta)-\lambda s\theta \\ \nu\lambda(1-c\theta)-\mu s\theta & \mu\nu(1-c\theta)+\lambda s\theta & c\theta+\nu^2(1-c\theta) }\right]$

**四元数（quaternion）**

四元数是由四个元素组成的一个数组。

给定一个标量$q_0$以及一个向量$\vec{q}=(q_x,q_y,q_z)^T$，可将其形成一个四元数$\circ{q}=(q_0,\vec{q})$。

这里$\circ q=q_0+iq_x+jq_y+kq_z$，这里$i^2=j^2=k^2=-1,ij=k,jk=i,ki=j$。

四元数乘积的定义为：设$q_1=(q_{10},\vec{q_1}),q_2=(q_{20},\vec{q_2})$，$q_1\cdot q_2=(q_{10}q_{20}-\vec{q_1}\cdot\vec{q_2},\vec{q_1}\times\vec{q_2}+q_{20}\vec{q_1}+q_{10}\vec{q_2})$，并且$q=(q_0,\vec{q})$的共轭为$\bar{q}=(q_0,-\vec{q})$。

四元数具有以下性质：

1. $|q|^2=q\cdot\bar{q}=q_0^2+|\vec{q}|^2$
2. $|q\cdot q'|^2=|q|^2\cdot|q'|^2$

使用四元数可以有效地表示空间中的旋转。

设$r=(0,\vec{R}),r'=(0,\vec{R'})$，同时设$q=\left(\cos\dfrac{\theta}{2},\sin\dfrac{\theta}{2}\vec{w}\right)$，通过使用罗德里格斯公式，可得$r'=q\cdot r\cdot\bar{q}$

### 4.3 点群运动的计算

对于两个点群$P,P_i$，$\vec{P}=R\vec{P_i}+\vec{T}+\vec{N_i}$。利用最小二乘法，可将此问题转化为使$E^2=\sum_{i=1}^N|\vec{P_i'}-(R\vec{P_i}+\vec{T})|^2$。

最小的$R$与$\vec{T}$的估计问题。

设$\vec{P}=\dfrac{1}{N}\sum\vec{P_i},\vec{P'}=\dfrac{1}{N}\sum\vec{P_i'}$，并做变换$\vec{d_i}=\vec{P_i}-\vec{P},\vec{d_i'}=\vec{P_i'}-\vec{P'}$，则有$E^2=\sum|(d_i'+\vec{P'})-[R(\vec{d_i}+\vec{P})+\vec{T}]|^2=\sum|(\vec{d_i}-R\vec{d_i})+(\vec{P'}-(R\vec{P}+T))|^2=\sum|\vec{d_i'}-R\vec{d_i}|^2$。

这时，优化问题可分解为

- 求使$E^2$最小的$\hat{R}$
- 求$\vec{T}$，$\vec{T}=\vec{P'}-\vec{P}$

#### 4.3.1 利用四元数求$R$

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

## 第五章 三维数据的配准（registration）

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

### 5.1 迭代最近点法的基本原理 ICP

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

### 5.2 算法求解的注意事项

#### 5.2.1 最近点

在实际求解过程中，仅仅是欧氏距离最近点不能保证两个曲面点在空间位置上最近，有种更可靠的方法是：将点$\vec{p_i}$转换成$T^{k-1}\vec{p_i}$，然后使用$T^{k-1}\vec{p_i}$的法线与$Q$的交点作为对应点$\vec{q_j}'^k$，$\vec{q_j}'^k=(T^{k-1}\vec{p_i}\cap Q)$，其中$\cap$为求交点。

这时，求$\vec{l^k}=\{\vec{a}|(T^{k-1}\vec{p_i}-\vec{a})\times\vec{n_{p_i}}=0\}$，这里$\vec{n_{p_i}}$为$T^{k-1}\vec{p_i}$的法线方向向量。

再得到$\vec{q_j}'^k=(T^{k-1}\vec{l_i})\cap Q'$，$Q'$为右边曲面的切平面。

#### 5.2.2 算法的收敛性

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

#### 5.2.3 控制点的选择

1. 计算量

2. 收敛速度

   尽量避免在数据中的平坦区域寻找控制点

3. 计算精度

   避免噪声多的数据区域

4. 遮挡问题

#### 5.2.4 控制点的自动选择

$E_k=\dfrac{1}{W}\sum_{i=1}^Nw_i|T\cdot T^{k-1}\vec{p_i}-\vec{q_j^k}|^2,\quad W=\sum w_i$。

$w_i$定义如下：

设$d_i=|T^{k-1}\vec{p_i}-\vec{q_j}'^{k-1}|$，$w_i=\left\{\begin{aligned}&1 & 0\leq d_i\leq \varepsilon_1 \\&\rho(\dfrac{1}{d_i}) & \varepsilon_1\leq d_i\leq \varepsilon_2 \\ &0 & \varepsilon_2\leq d_i \end{aligned}\right.$，其中$\rho(x)$为$x$的单纯增长函数，$0<\rho(x)<1$。





