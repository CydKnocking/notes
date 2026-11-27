# 从点轨迹到世界模型与具身控制

**文献笔记 · 截至 2026 年 11 月 23 日**  
精选 26 篇应用论文，重点是 2025–2026 年的工作，保留 2024 年几篇奠定问题设定的论文。选文围绕一个问题：**知道同一个物理点去了哪里，究竟能让生成模型或机器人多做什么？** 正文按论文在系统中实际使用的信号组织，每篇给出论文或作者项目链接。标为 arXiv 的条目按所引预印本的首发年月标注，涉及多版时采用截至检索日的版本。下文数字均来自各论文自己的实验。

## 一、先看三个问题

以“拉开抽屉”为例。给视频模型画一条把手向外移动的轨迹，是在**指定想看到的运动**。给机器人一个向外移动 5 cm 的动作，让模型预测抽屉和柜体各自会怎样动，是在**预测动作的后果**。在机器人已经伸手后发现把手几乎没动，再调整抓取或拉动方向，是在**用轨迹做反馈**。三者都画得出彩色轨迹，却需要不同的训练数据，也要用不同的实验来验证。

| 想回答的问题 | 点或重建在系统中的作用 | 优先阅读 |
|---|---|---|
| 怎样让生成的视频既按要求运动，又能从另一个相机看？ | 将同一批点投影到源、目标视角，作为视频扩散模型的条件 | [Edit-by-Track][edit]、[Track2View][t2v] |
| 能否先观察一段视频，再预判某个点未来会去哪里？ | 用整段视频恢复的轨迹作训练标签，测试时只给过去的观测；也可用语言指定目标 | [MotionForesight][mf]、[MolmoMotion][mol] |
| 同一场景中，换一个机器人动作会有什么不同？ | 把候选动作编码为夹爪或机器人表面的 3D 运动，预测环境点的响应，供规划器打分 | [PointWorld][pw] |
| 让模型学未来轨迹，对生成视频和输出动作是否都有收益？ | 在同一骨干上同时学习多视角视频和持久 3D 点轨迹，再对照有无轨迹监督的动作模型 | [Video-Point Model（VPM）][vpm] |
| 跟踪器必须在机器人上运行吗？ | 可仅在训练期间教策略理解运动，也可在部署期间实时测量物体偏差 | [4D-WAM][wam]、[Dex4D][dex] |
| 只有人类示范，没有逐步动作奖励，怎样知道机器人有没有做好？ | 跟踪示范与执行视频中的物体点，按两段物体运动的相似度构造奖励 | [HuDOR][hudor] |

**读论文时保留三个区别。** ① 跟踪用已观测视频估计历史轨迹，预测只能用过去信息推断未来。② 逐帧点图记录各帧像素对应的 3D 位置，跨时间的点身份还要靠对应关系确定。③ 语言目标限定“想完成什么”，低层动作指定“实际怎么做”。只有模型接收候选动作，才可以直接比较两个动作在其预测中造成的不同后果。[V-DPM][vdpm] · [MolmoMotion][mol] · [PointWorld][pw]

## 二、生成任务：轨迹可以是用户输入、训练监督或跨视角对应

| 论文 | 重建 / 跟踪怎样进入模型 | 作者展示的应用 |
|---|---|---|
| **Motion Prompting**，Geng 等，CVPR 2025 | 用 BootsTAP 为训练视频提取带可见性的 2D 点轨迹，训练一个接收稀疏到稠密轨迹的扩散控制分支。推理时轨迹也可来自鼠标拖动或参考运动。 | 一套模型控制局部物体、全局相机运动及运动迁移。控制量在图像平面，适合指定“画面里的点怎么走”。[论文][mp] |
| **Track4Gen**，Jeong 等，CVPR 2025 | 在视频扩散训练中增加跨帧点对应损失，让中间特征能在不同帧认出同一位置对应的内容。 | 改善图生视频的外观一致性，减少物体随时间变形或更换外观。轨迹在这里承担辅助监督，生成时用户无需画轨迹。[论文][t4g] |
| **GEN3C**，Ren 等，CVPR 2025 | 将初始图像或已生成帧的深度反投影成可复用的 3D 点云；沿目标相机轨迹渲染点云，再以渲染结果引导生成。 | 精确相机控制、稀疏视图新视角合成。这里复用的是场景表面的位置与外观，并未为每个运动物体建立跨帧点身份。[项目与代码][gen3c] |
| **Edit-by-Track**，Lee 等，CVPR 2026 | 从源视频估计相机位姿和 3D 点轨迹。用户可以编辑相机和物体运动，模型把原轨迹、编辑轨迹分别投影成两组 2D 对应。 | 对已有视频同时改机位、改物体运动，还可控制形变。保留源轨迹可以告诉生成器，被移动位置的外观应该从哪里取。[论文与演示][edit] |
| **Track2View**，Qiao 等，arXiv 2026-06 | 同一组稀疏 3D 轨迹同时投影到源视角和指定的新视角，让视频 Transformer 沿对应关系传递信息。 | 保留已经发生的场景运动，只改变观察路径。在作者的 400 段视频评测上，相对所比较的领先基线，相机旋转、平移误差分别降低 30–65% 和 61–72%。这里评的是机位控制。[论文][t2v] |
| **4DStreamCtrl**，Li 等，arXiv 2026-08 | 从自然视频提取 3D 轨迹和相机信息，统一表达前景运动、深度和视角控制，再将生成器蒸馏为因果流式模型。 | 允许视频边生成边接收新的相机或物体控制。作者报告单张 H100 上 480p 生成达到 20 FPS；该数字度量生成器，在线使用时还需计入上游跟踪和控制延迟。[项目][stream] |

**和动态重建最贴近的一组对照是 GEN3C、Track2View 和 Edit-by-Track。** 假设相机绕到抽屉侧面：场景点云能说明柜体从新机位看应该出现在哪；持久点轨迹进一步说明拉出的把手在每一帧出现在哪；编辑把手轨迹则允许改变原视频里的事件。追踪持续点身份有什么额外价值，可以在同一个生成任务里逐级检验。[GEN3C][gen3c] · [Track2View][t2v] · [Edit-by-Track][edit]

## 三、世界模型：要预测谁的未来，以及未来由什么决定

| 工作 | 预测时给什么 | 模型输出什么 | 论文验证到哪一步 |
|---|---|---|---|
| **MotionForesight**，Bharadhwaj、Jangir，arXiv 2026-07 | 一小段已经发生的单目人–物交互视频 | 被操作物体表面点未来的 3D 轨迹 | 完整视频的离线跟踪结果提供伪标签，预测器只看前缀；在未见物体、视角和交互上评估。适合研究无动作标注的运动先验。[论文与方法][mf] |
| **MolmoMotion**，Zhang 等，arXiv 2026-06 | 短 RGB 历史、物体上的 3D 查询点、语言目标 | 米制世界系中的物体点轨迹 | 作者从 116 万段视频构建训练集，在人工核验的 PointMotionBench 上评估，还将运动先验用于视频生成和机器人抓放。项目列出的限制是每个物体使用 8 个查询点，复杂局部形变的覆盖有限。[论文][mol] · [资源与局限][molsite] |
| **VPM**，Jeon 等，arXiv 2026-10 | 有相机参数的多视角视频历史、语言指令，以及所需输出视角 | 各视角未来 RGB 与跨时间、跨视角保持身份的 3D 点轨迹；扩展版联合生成动作 | 用相同训练预算比较有无轨迹监督，既测视频质量，也测 3D 运动与真机抓放。所监督的点集中在机器人和有标注的对象，且推理使用已知相机参数。[论文][vpm] · [实验与限制][vpmfull] |
| **PointWorld**，Huang 等，CVPR 2026 | 一张或少量 RGB-D 观测，加上候选低层机器人动作；利用机器人运动学把动作转换为 3D 表面点运动 | 动作作用下，场景观测点未来的 3D 位移 | 将模型放入模型预测控制（MPC），按点的预测位置筛选动作；在真实 Franka 上展示推物、形变物体、铰接物体和工具操作。训练数据约 200 万条轨迹、500 小时。[论文][pwpaper] · [代码][pwcode] |
| **TesserAct**，Zhen 等，ICCV 2025 | 初始图像和任务指令 | 未来 RGB、深度、法线视频，继而重建动态 3D 场景 | 展示新视角渲染，并从生成的 4D 场景学习逆动力学、恢复动作。核心监督是逐帧 RGB-DN，适合与显式预测同一点未来位置的方法作比较。[论文][tes] · [项目][tessite] |
| **JEPA4R**，Dong 等，arXiv 2026-11 | 单深度相机点云，以及动力学预测时的动作 | 未来的点云潜在表征；另训解码器把冻结表征还原成点云序列 | 在仿真与真实机械臂上评估策略。事后解码器使用 Chamfer 等集合损失，因此论文中的点云重建误差不能读作“同一物理点”的轨迹误差。[论文][jepa] · [方法 §4.4][jepafull] |

### 三篇值得对照着精读

**MotionForesight 和 PointWorld 分别回答“接下来大概会怎样”和“我这么做会怎样”。** 前者用完整片段产生监督，再显式遮住未来的 RGB 和几何输入。它适合大量只有视频的人类操作数据。后者把待测试的机器人动作放在输入端，因此规划器可以在同一初始状态下分别尝试向左、向右推，比较预测的物体位移。即便两者都输出 `[点数, 未来时刻数, 3]`，所需数据和可支持的决策也不同。[MotionForesight][mf] · [PointWorld][pw]

**VPM 给出了点身份对生成和动作都有帮助的受控实验。** 同一个场景点只有一条 3D 轨迹，不同摄像机应同时看到这条轨迹的不同投影。作者据此比较仅学视频与同时学轨迹的模型，并进一步比较“视频＋动作”和“视频＋轨迹＋动作”。真机部分为三种抓放任务，每种 24 次。论文还展示了直接把预测轨迹经逆运动学生成指令的定性例子，作者指出这种执行的稳定性尚不足以量化评估。写 related work 时，后者应与上面的策略成功率分开引用。[实验 §6.3–6.5][vpmfull]

## 四、具身智能：同一条轨迹怎样变成动作、奖励和反馈

### 4.1 从示范视频提取可执行的信息

| 论文 | 点到底表示什么 | 从视频到机器人执行的关键一步 |
|---|---|---|
| **RoboTAP**，Vecerik 等，ICRA 2024 | 示范与执行过程中和当前任务有关的 2D 物体点 | 用 TAPIR 跟踪，选出当前阶段应移动的点，根据点的当前位置和目标位置计算控制。每项任务 4–6 次示范，真机展示插入、堆叠、涂胶等。适合从视觉伺服角度入门。[项目][rt] |
| **ATM**，Wen 等，RSS 2024 | 当前画面任意查询点的未来 2D 轨迹提案 | 从无动作标签视频预训练轨迹预测器，再用少量带动作示范学习视觉运动策略。作者在 LIBERO 的 130 个任务及真实 UR5 厨房任务上评估。[论文][atm] |
| **Track2Act**，Bharadhwaj 等，ECCV 2024 | 以目标为条件预测的物体 2D 点轨迹 | 从轨迹推断物体的刚体变换序列，得到末端执行器计划，再用少量机器人示范学到的残差策略闭环修正。互联网视频教“物体该怎么动”，机器人数据教“该怎样执行”。[论文][track2] |
| **General Flow**，Yuan 等，CoRL 2024 | 语言指令下，目标物体表面点的一段 3D 运动 | 从人类 RGB-D 视频学习可供机器人执行的物体运动，将预测放进闭环控制。作者报告 6 个场景、18 项任务的人到机器人零样本迁移成功率为 81%。[论文][gf] |
| **Im2Flow2Act**，Xu 等，CoRL 2024 | 多个物体点的图像平面运动，共同描述任务效果 | 用人类示范训练“图像与任务 → 物体运动”，用仿真机器人自由交互训练“物体运动 → 动作”。两个模块通过物体运动连接，作者展示真实机器人迁移。[论文与项目][imf] |
| **Point Policy**，Haldar、Pinto，CoRL 2025 | 具有语义的物体和手部关键点，以及由其得到的未来 3D 轨迹 | 从离线人类视频估计手与物体状态，经 Transformer 预测点轨迹，通过刚体几何恢复机器人动作；在 8 项真机任务上评估。这是稀疏语义点的路线。[论文][pp] |
| **HuDOR**，Guzey 等，ICRA 2025 | 人类示范与机器人尝试中，被操作物体表面点的运动 | 比较两段物体运动来定义奖励，在线微调多指手策略。作者用单段人类示范，在约一小时真机交互后让 Allegro 手打开八音盒。点跟踪在这里解决了“操作是否取得进展”的问题。[论文][hudor] |

### 4.2 全局计划、训练教师、在线反馈的三个近期实例

**3PoinTr｜把一整段任务压成可复用的几何计划。** 从初始点云预测完整任务中的稠密 3D 轨迹，再压缩成少量固定的计划 token。执行时每一步都重新读取当前观测和机器人状态，但计划 token 在这一回合内保持固定。这使策略可以吸收人类视频中有用的物体运动，即使人手动作无法被机器人原样执行。在四项真机任务中，每项使用 20 段机器人示范和 50 段人类视频，平均成功率比最强基线 DP3 高 **25 个百分点**。Hung 等，arXiv 2026-03，引用 9 月修订版。[论文][p3] · [实验设置][p3site]

**4D-WAM｜几何教师只在训练期间提供轨迹场特征。** 冻结的 Trace Anything 为视频与动作模型提供两种对齐信号：相邻帧特征变化约束局部运动，起点与终点的相似度分布约束长程去向。动作模型因此能在自身特征中保留运动信息，部署时可直接输出动作。与同一 FastWAM-Joint 基线相比，在仅用 LIBERO 训练、用 LIBERO-Plus 的七种未见扰动测试时，平均成功率从 **62.21% 到 71.01%**；其中相机扰动一项从 **27.89% 到 45.15%**。这是检验“几何监督能否改善视角泛化”的直接参照。Yang 等，arXiv 2026-08。[论文与实验表][wam] · [代码仓库][wamcode]

**Dex4D｜先从生成视频给出目标，再用真机跟踪纠偏。** 仿真策略学习根据当前与目标物体点的对应关系，将刚体从当前位姿移到目标位姿。部署时，从生成示范视频提取物体中心的目标点轨迹；执行时继续在线跟踪真实物体，根据观测更新控制。生成轨迹表达意图，真实轨迹提供反馈。这篇尤其适合判断在线跟踪的遮挡恢复、延迟和点身份切换是否会影响任务成功率。Kuang 等，CoRL 2026。[论文][dex] · [项目与仿真、视觉、硬件代码][dexsite]

### 4.3 重建怎样进一步用于策略、示范生成和闭环仿真

| 论文 | 重建的具体用途 | 几何与跟踪的边界 |
|---|---|---|
| **Geometric Action Model（GAM）**，Han 等，ECCV 2026 的 3D World Models Workshop | 拆开预训练几何骨干，在中间插入因果预测器；根据观测、指令、本体状态和动作历史预测潜在表征，再解码未来几何与动作。在仿真和真机摄像机扰动下评估。 | 重建骨干直接成为策略骨干；它回答了“几何预训练本身能贡献多少”，适合作为显式点轨迹监督的对照。[项目与代码][gam] |
| **GRAIL**，Xie 等，CoRL 2026 | 从具有已知尺度、相机与物体资产的场景出发生成交互视频，重建 4D 人–物运动，再重定向到人形机器人，形成训练示范；在 Unitree G1 上验证抓取和上楼。 | 核心是人体运动、物体位姿与接触的一致恢复。资产和场景提供额外几何信息，区别于无约束单目视频中的任意点跟踪。[论文][grail] |
| **HUGSIM**，Zhou 等，IEEE TPAMI 2026 | 把带位姿的道路图像重建为静态与动态 3D Gaussians。驾驶策略给出控制后，仿真器更新自车、其他交通参与者与相机观测，让策略体验自己偏离原采集路线的后果。 | 重建产生可交互环境。车辆运动模型和渲染器承担闭环状态更新，评测对象是驾驶策略。[项目与代码][hug] |

## 五、怎样验证“点轨迹有用”

**PDI-Bench 把跟踪器当成视频生成的评测工具。**它在**已经生成的视频**上分割对象、跟踪点并做单目 3D 重建，再根据尺度与深度的关系、3D 运动一致性和结构刚性计算几何残差。由此可以区分画面看似平滑的两种失败：物体只是随透视变小，还是其恢复出的 3D 尺寸也在变化。评测器本身依赖深度、位姿与跟踪质量，遮挡或非刚体形变应单独分析。Wu 等，arXiv 2026-05。[论文][pdi]

| 要支持的研究结论 | 合适的指标或实验 | 可用起点 |
|---|---|---|
| 在观测过的视频中，持续认对同一物理点 | 按可见性与遮挡分别报告轨迹误差、阈值内准确率、可见性判断；移动相机下明确使用相机系还是世界系 | [TAPVid-3D][tap3d] 可检验跟踪；未来预测另设截断时刻 |
| 只看视频前缀，也能预判未来物体运动 | 固定输入前缀长度，按预测时距报告米制 3D ADE（平均轨迹误差）与 FDE（终点误差）；对照静止、恒速度，并分开动点和背景 | [PointMotionBench][motionbench] 含人工核验的物体运动；[VP-WorldBench][vpbench] 可同时检查视频和点 |
| 点的监督确实改善生成 | 固定视频骨干、训练预算和输入视角，对照有无轨迹监督；分开报告视觉质量、跨视角一致性和几何运动误差 | [VPM §6 与附录][vpmfull] 同时区分从生成视频重新跟踪得到的轨迹与模型轨迹头直接输出的轨迹 |
| 几何改善最终有利于机器人 | 固定动作头与机器人数据量，对照任务成功率；加入相机移动、短时遮挡、初始物体偏移，并记录执行时延 | [4D-WAM][wam] 适合训练监督对照；[Dex4D][dexsite] 适合闭环观测对照；[PointWorld][pw] 适合候选动作规划 |

## 六、对流式 Dynamic Point Maps 最值得检验的三个问题

下面是基于文献提出的实验设想。SDPM 的切入点是从单目视频在线获得相机运动与场景点运动。若源帧像素为 $u$，其对应物理点在目标时刻的世界坐标可写为 $X_{s\rightarrow t}(u)$。固定 $s,u$，改变 $t$，得到同一点的一条轨迹。沿用这一表示，最值得区分的是**哪些时刻已被观测、未来由谁指定、对应身份是否跨窗口保留**。[V-DPM][vdpm]

1. **成本最低的切入点是未来 3D 点轨迹预测。** 让离线教师读取完整训练片段产生未来标签，流式编码器只读取前缀；先固定未来预测头，比较单目深度＋2D 跟踪反投影、逐帧点图、带跨帧身份的动态点图三种输入。用独立标注或合成真值评估动态点 ADE/FDE，并画误差随预测时距的曲线。若单目输出需要 Sim(3) 对齐，只用历史或已知标定估计变换，再冻结到未来，避免把未来的尺度和位姿泄漏给模型。[MotionForesight][mf] · [MolmoMotion][mol] · [PointMotionBench][motionbench]
2. **最能体现流式特性的切入点是遮挡后的闭环纠偏。** 固定策略和目标轨迹，分别提供真实标注轨迹、离线跟踪结果（事后参考）、实时 SDPM 结果。让相机平移，或让夹爪短时挡住把手，记录重现后点身份恢复率、恢复耗时、重投影误差和任务成功率。若局部窗口各自做 Sim(3) 对齐，应在机器人坐标系里额外记录重叠段跳变；同一把手相对夹爪跳动几厘米，可能比整段平均误差更影响控制。[RoboTAP][rt] · [Dex4D][dexsite] · [PointWorld][pw]
3. **对世界模型最有辨识度的问题是持久点身份有没有独立收益。** 固定相机条件、视频骨干与训练预算，比较仅 RGB、RGB＋逐帧点云、RGB＋带身份的 3D 轨迹。再做一次身份消融：保留每一帧完全相同的 3D 点集，只打乱跨帧对应；为三组提供相同的数据可见性与监督时距。如果逐帧几何指标相近，而正确对应改善了跨视角未来预测或摄像机扰动后的机器人成功率，才有直接证据支持“持续追踪同一物理点”这项设计。[Track4Gen][t4g] · [VPM][vpmfull] · [4D-WAM][wam]

**按研究目标选阅读顺序。** 想最快把现有 SDPM 接到一个离线实验，先读 **MotionForesight → MolmoMotion**。想在论文中论证点身份对生成有独立价值，读 **Track4Gen → Track2View → VPM**。想证明在线几何能改善真实动作，读 **RoboTAP → Dex4D → PointWorld**。三条路线分别需要未来轨迹标签、可对照的生成实验和可接入的控制环，实验代价差别很大。

## 附录 · 英文题名索引

| 方向 | 英文题名与一手来源 |
|---|---|
| 生成 | [Motion Prompting: Controlling Video Generation with Motion Trajectories][mp] |
| 生成 | [Track4Gen: Teaching Video Diffusion Models to Track Points Improves Video Generation][t4g] |
| 生成 | [GEN3C: 3D-Informed World-Consistent Video Generation with Precise Camera Control][gen3c] |
| 生成 | [Generative Video Motion Editing with 3D Point Tracks][edit] |
| 生成 | [Track2View: 4D-Consistent Camera-Controlled Video Generation via Paired 3D Point Tracks][t2v] |
| 生成 | [4DStreamCtrl: Interactive Video Generation with Online 4D Control][stream] |
| 预测 | [MotionForesight: Re-purposing Video Models for Future 3D Scene-Flow Prediction][mf] |
| 预测 | [MolmoMotion: Forecasting Point Trajectories in 3D with Language Instruction][mol] |
| 世界模型 | [Learning the 4D World through Point Trajectory Forecasting][vpm] |
| 世界模型 | [PointWorld: Scaling 3D World Models for In-The-Wild Robotic Manipulation][pw] |
| 世界模型 | [TesserAct: Learning 4D Embodied World Models][tes] |
| 世界模型 | [JEPA4R: Embodied JEPA World Models with 4D Point Planning][jepa] |
| 具身 | [RoboTAP: Tracking Arbitrary Points for Few-Shot Visual Imitation][rt] |
| 具身 | [Any-point Trajectory Modeling for Policy Learning][atm] |
| 具身 | [Track2Act: Predicting Point Tracks from Internet Videos enables Generalizable Robot Manipulation][track2] |
| 具身 | [General Flow as Foundation Affordance for Scalable Robot Learning][gf] |
| 具身 | [Flow as the Cross-Domain Manipulation Interface][imf] |
| 具身 | [Point Policy: Unifying Observations and Actions with Key Points for Robot Manipulation][pp] |
| 具身 | [Bridging the Human to Robot Dexterity Gap through Object-Oriented Rewards][hudor] |
| 具身 | [3PoinTr: From Human Videos to Robot Policies with 3D Point-Track Plans][p3] |
| 具身 | [4D-WAM: Infusing Spatiotemporal Awareness into World Action Models through Trajectory Fields][wam] |
| 具身 | [Dex4D: Task-Agnostic Point Track Policy for Zero-Shot Dexterous Manipulation][dex] |
| 具身 | [Geometric Action Model for Robot Policy Learning][gam] |
| 具身 | [GRAIL: Generating Humanoid Loco-Manipulation from World Models][grail] |
| 闭环仿真 | [HUGSIM: A Real-Time, Photo-Realistic and Closed-Loop Simulator for Autonomous Driving][hug] |
| 生成评测 | [Quantitative Video World Model Evaluation for Geometric-Consistency][pdi] |

[mp]: https://arxiv.org/abs/2412.02700
[t4g]: https://arxiv.org/abs/2412.06016
[gen3c]: https://research.nvidia.com/labs/toronto-ai/GEN3C/
[edit]: https://edit-by-track.github.io/
[t2v]: https://arxiv.org/abs/2606.15534
[stream]: https://4dstreamctrl.github.io/
[mf]: https://motionforesight.github.io/
[mol]: https://arxiv.org/abs/2606.18558
[molsite]: https://molmomotion.github.io/
[vpm]: https://arxiv.org/abs/2610.28594
[vpmfull]: https://arxiv.org/html/2610.28594v1
[pw]: https://point-world.github.io/
[pwpaper]: https://openaccess.thecvf.com/content/CVPR2026/papers/Huang_PointWorld_Scaling_3D_World_Models_for_In-The-Wild_Robotic_Manipulation_CVPR_2026_paper.pdf
[pwcode]: https://github.com/NVlabs/PointWorld
[tes]: https://arxiv.org/abs/2504.20995
[tessite]: https://tesseractworld.github.io/
[jepa]: https://arxiv.org/abs/2611.19771
[jepafull]: https://arxiv.org/html/2611.19771v1
[rt]: https://robotap.github.io/
[atm]: https://roboticsproceedings.org/rss20/p092.html
[track2]: https://arxiv.org/abs/2405.01527
[gf]: https://proceedings.mlr.press/v270/yuan25a.html
[imf]: https://im-flow-act.github.io/
[pp]: https://proceedings.mlr.press/v305/haldar25a.html
[hudor]: https://georgysavva.github.io/assets/pdf/HuDOR_ICRA_2025.pdf
[p3]: https://arxiv.org/abs/2603.08485
[p3site]: https://adamhung60.github.io/3PoinTr/
[wam]: https://lishanyqy.github.io/4DWAM/
[wamcode]: https://github.com/lishanyqy/4DWAM
[dex]: https://arxiv.org/abs/2602.15828
[dexsite]: https://dex4d.github.io/
[gam]: https://cvlab-kaist.github.io/Geometric-Action-Model/
[grail]: https://arxiv.org/abs/2606.05160
[hug]: https://xdimlab.github.io/HUGSIM/
[pdi]: https://arxiv.org/abs/2605.15185
[vdpm]: https://www.robots.ox.ac.uk/~vgg/research/vdpm/
[tap3d]: https://arxiv.org/abs/2407.05921
[motionbench]: https://huggingface.co/datasets/allenai/PointMotionBench
[vpbench]: https://huggingface.co/datasets/rooty2020/VP-WorldBench/blob/main/README.md
