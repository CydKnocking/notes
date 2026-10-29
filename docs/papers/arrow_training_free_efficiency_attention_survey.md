# 面向 ARROW 长序列与稠密查询的免训练加速：注意力、可解释性与推理机制综述

更新日期：2026-10-29。检索截至该日；重点核对论文正文中的分析、消融和方法，而非只引用摘要的加速倍数。本文以已有 `4drecon_tracking.md` 为线索，补充了 HeSS、HTTM、Co-Me、RetrieveVGGT、GPA-VGGT、VGGT-Prime 等工作。

**核心判断：ARROW 值得同时研究编码器的跨帧交互和解码器的 query-to-context 访问。最优先的组合是“保持 query 独立与完整、按层/头压缩 K/V、保护查询相关帧与身份信息”，再用窗口和历史检索扩展序列长度。** 这些是基于文献提出的研究建议，尚未在 ARROW 上验证。

本文区分四种成本：①既有权重直接改推理；②不更新权重但需要校准；③冻结主干、额外训练小模块；④微调主干或重新训练。Test-time training 另区分“更新当前场景的小参数”和“以 fast weights 实现场景记忆”，不能把带 TTT 的模型都称为免训练插件。

## 1. ARROW 的问题定位

### 1.1 已知事实与证据边界

[ARROW 论文](https://arxiv.org/html/2610.01314v1) §3 的结构是：DA3 初始化的多视图编码器产生全局 patch context 和逐帧 ID token；查询由源像素外观、坐标及 source/target/reference 三个 ID 组成；解码器让每个 query 独立 cross-attend 全局 context，query 之间没有 self-attention。ID token 来自相机 token，但已被重新用于观测身份，不能直接当作相机位姿。

[lab05 arrow 开发](thread://01a1396b-9001-7030-be86-e4fa87e88b9d?hostId=local) 的已有代码检查记录表明：当前推理对选中的全部帧一次联合编码，再以 `decode-chunk-size` 分块解码；没有自动时间滑窗。每块 query 仍访问整段编码。该记录只报告过四帧样例的实际运行，因此本文不会把几百帧的瓶颈推断冒充已完成的 profiling。

### 1.2 长序列与稠密 query 是两个相乘的维度

设帧数为 $F$、每帧 patch 数为 $T$、编码 context 长度为 $N\approx FT$、跟踪种子数为 $P$、查询总数为 $Q$。忽略层数、通道数和特殊 token 的常数：

| 部分 | 主要 attention 计算量 | 需要解决的问题 |
|---|---:|---|
| 编码器 frame attention | $O(FT^2)$ | 单帧空间成本 |
| 编码器 global attention | $O(F^2T^2)$ | 跨帧交互随长度二次增长 |
| 解码器 cross-attention | $O(QFT)$ | 每个 query 访问多少 context |
| 固定 $P$ 个种子跟踪全部帧 | $Q=PF$，解码为 $O(PTF^2)$ | query 数和 context 长度同时随帧数增加 |
| 输出、传输和保存 | 至少 $O(Q)$ | 即便 attention 很快，稠密结果仍有成本 |

例如，假设输入为 $504\times504$、patch 为 $14\times14$，每帧约 1296 个 patch；首帧以 2 像素间隔播种约 63,504 点，查询 300 个目标帧就有约 **1905 万个 query**。这是说明数量级的算例，不是运行测量。`all_pixels` 还会在后续帧补种，其种子数也可能随长度增加。

减小 query chunk 主要降低峰值工作集，不减少总 query 数，也不减少每个 query 要读取的 context。FlashAttention 类精确算子避免显式存储完整注意力矩阵，但不消除上述全连接计算量。因此应分开报告计算量、峰值显存和实际延迟，不能简单声称显存必为 $O(N^2)$。

### 1.3 两条迁移边界

1. **ARROW 不是原版 VGGT。** DA3 的全局层分布、ARROW 微调后的 head 功能及 ID 表示均可能不同。VGGT 的“第 9 层”“第 10–16 层”只是候选分析区间，不能直接成为 ARROW 配置。
2. **静态重建不等于动态点跟踪。** 有些方法把动态区域当作几何异常去除；ARROW 恰恰需要这些区域。相似外观不保证同一物理点，静态极线约束也不能直接约束任意跨时刻的运动点。

## 2. 直接分析 attention，并据此设计免训练加速

本节的“ARROW 启发”均为迁移推论；论文原结论与推论分开陈述。

### 2.1 On Geometric Understanding and Learned Priors in Feed-forward 3D Reconstruction Models

来源：[论文，2026-03-17 v2](https://arxiv.org/html/2512.11508v2)，重点 §4 与附录 C/D。旧版标题只提 VGGT，新版还分析 DUSt3R、DA3。

- **做了什么、如何挖掘：** 在中间表示上训练小型 fundamental-matrix probe；逐层逐头用 QK 最大响应检验真实对应；再对对应相关 head、图像间子矩阵、局部块及 patch 做干预。
- **发现：** VGGT 的强对应 head 主要在中段，约 10–16 层；对极线几何的解码能力随后明显增强。DA3 也有相应现象，DUSt3R 更早出现且方向不对称。干预这些 head 比干预随机早/晚层破坏更大。
- **加速关系：** 本文没有提出加速模块；价值是证明“可视化相关性 → 对应准确率 → 因果干预”的分析路径。Probe 本身需要训练，冻结被分析网络不等于整个实验零训练。
- **ARROW 启发：** 先寻找承担匹配的 head，再分配稀疏预算。用静态背景研究相机几何，用动态轨迹真值研究运动对应；不能只凭亮度热图判断 token 可删。

### 2.2 FastVGGT

来源：[论文](https://arxiv.org/html/2509.02560)，重点 §3；**既有 VGGT 权重直接改推理**。

- **观察与证据：** profile 显示长输入时 global attention 占主导；不同 token 的 attention map 高度相似。直接随机/固定步长合并会明显伤害重建。
- **设计：** 首帧 token 作为锚点，保留显著 token，再按空间区域选择代表；相似 token merge 后计算 global attention，之后 unmerge 恢复稠密布局。
- **效率来源：** 减少参与注意力的 Q/K/V 数量；1000 图设置报告约 4× 加速，但匹配和 merge/unmerge 本身有成本。
- **ARROW 启发：** 可作为编码器基线。unmerge 恢复的是布局，不是被合并 token 各自的 attention 输出；不宜直接合并承担不同点身份的解码 query。其“相似/塌缩”观察也不能推广成所有 head 都冗余。

### 2.3 SparseVGGT / Faster VGGT with Block-Sparse Global Attention

来源：[论文，2026-05-20 v2](https://arxiv.org/html/2509.07120v2)。新版标题为 *Block-Sparse Global Attention for Efficient Multi-View Geometry Transformers*；这些名称指向同一论文演进，勿重复计数。**免训练**，实验覆盖 VGGT、π³、MapAnything。

- **观察与证据：** patch-to-patch 注意力质量集中在少数几何对应；中间层选择性最强，删中间层比删早晚层更危险；特殊 token 与 patch 的交互性质不同。
- **设计：** 池化 Q/K 预测粗粒度块分数，以累计概率阈值和最少保留块数联合选择，再运行真正的 block-sparse kernel。
- **关键细节：** 仅 patch–patch 稀疏；special–special、special–patch、patch–special 都保留稠密连接，不只是特殊 token 彼此稠密。新版报告超过 3× 的设置。
- **ARROW 启发：** 编码器和矩形的 query-to-context 注意力均可尝试。必须把构造 mask 的开销算入延迟，并保留统一 softmax 归一化；用稠密矩阵乘后再置零不会获得同样加速。

### 2.4 AVGGT

来源：[论文，2026-03-10 v2](https://arxiv.org/html/2512.02541v2)，重点 §3–4；**免训练**，覆盖 VGGT 与 π³。

- **观察与证据：** 早层偏位置或少数 hub，中层出现对应和自连接，晚层偏细化；用图像旋转、早层替换及 K/V 子采样消融检验解释。
- **设计：** 早期 global 改为 frame attention；其余层保留全部 Q，对 patch K/V 做空间网格子采样，保护特殊 token。增强版补回自注意力对角项，并用带数量权重的均值项近似丢弃部分，三部分共同归一化。
- **适用边界：** 默认转换 VGGT 前 9 个 global block、π³ 前 10 个；VGGT 保护首帧，π³ 各帧统一处理。固定比例采样主要降低常数，并不自动变成关于帧数的线性复杂度。
- **ARROW 启发：** “全部 query + 稀疏 K/V”很适合稠密解码；但 cross-attention 没有自然的同位置对角线，不能照搬 diagonal preservation。早层替换还需对照下节的新证据。

### 2.5 GPA-VGGT：2026-10-27 的新补充

来源：[论文 v1](https://arxiv.org/html/2610.37000v1)；**免训练，近期预印本**。

- **观察与证据：** 严格位姿指标暴露了宽松指标下不明显的损失；Q 合并损害逐 token 输出，省略 merge size 会扭曲注意力质量，完全去掉早期跨帧交互也会损伤精度。
- **设计：** 只 merge K/V、保留全部 Q；给代表 $s$ 个 token 的 key 加 $\log s$；早层采用 frame attention 加共享跨帧 K/V 摘要；敏感中间 block 少压缩；用固定 128 维随机投影降低匹配成本。
- **结果口径：** 文中报告 200 帧约 34 秒，对照 VGGT 约 87 秒，并强调 AUC@3 的保真；不是 ARROW 的实测收益。
- **ARROW 启发：** 比直接 Q/K/V 合并更符合独立点查询。早层保留少量全局摘要是 AVGGT 纯 frame 替换的重要对照；相关精度结论仍需独立复现。

### 2.6 HTTM：Head-wise Temporal Token Merging

来源：[论文](https://arxiv.org/html/2511.21317)，重点 §3；**免训练**。

- **观察与证据：** head 内的 Q/K 相似性具有局部空间和相邻视图结构，与 RoPE 及输入连续性有关；所有 head 共用 merge 分组会压低输出多样性。相似度矩阵不等同于 softmax attention map。
- **设计：** 逐 head 分别合并 Q 与 K，V 跟随 K 的分组；将相邻帧对应空间块重排到固定大小候选块内，限制匹配开销；过滤不适合合并的离群 token，最后逐头 unmerge、拼接。
- **效率来源：** 同时压缩 attention 和搜索 merge 对象的成本；1000 帧设置报告最高约 7×。
- **ARROW 启发：** 重点借鉴逐头和局部候选搜索。连续视频适合时间重排，多相机或无序输入需改成按共视关系分组；快速运动时不能把同一二维位置视为同一目标。

### 2.7 HeSS：Head Sensitivity Score

来源：[论文](https://arxiv.org/html/2603.25336)，重点 §3、§4.6 与校准附录；**不微调模型，但需要小规模校准和梯度计算**。

- **观察与证据：** 不同 head 对稀疏化的敏感性差异很大；统一压缩率会把关键 head 压坏。反转重要性排序的消融验证了排序的作用。
- **设计：** 根据相机和点云误差，用 Fisher/Hessian 近似估计 head sensitivity；测试时将固定总预算重新分配给各头，敏感头更稠密，稳健头更稀疏。
- **效率来源：** 相同 attention 预算下提高精度，或在精度约束下允许更高稀疏率；不是简单“删掉不重要的头”。
- **ARROW 启发：** 校准目标应加入动态轨迹误差、遮挡与重现，而非仅使用静态 pose/pointmap。用稠密 ARROW 输出做保真代理是可行候选，但与论文原校准协议不同，应单独验证。

### 2.8 这一组工作的共同点与分歧

| 证据 | 更稳妥的解释 | 对设计的影响 |
|---|---|---|
| 同些 token attention 很相似 | 某些交互可共享，不代表每个 token 的任务输出可共享 | 优先 K/V 压缩，单独检验 Q 合并 |
| 中层对应明显、删层敏感 | 中层承担重要匹配；其中仍可能存在可跳过连接 | 保留关键交互，不必保留全部连接 |
| 早晚层较均匀 | 可能在做背景聚合或校准，而非完全无用 | frame-only、frame+summary、原层三方比较 |
| 高 attention 或大激活 | 是重要性候选代理，不是因果贡献的定义 | 用匹配准确率与干预验证 |
| 极高稀疏率仍有好分数 | 取决于数据、任务及评价阈值 | 同时报严格位姿、边界、动态轨迹指标 |

特别是 AVGGT 与 GPA-VGGT 不应被拼成一句“早期全局注意力无用”。目前证据更支持：**早期有较大压缩空间，但是否能完全去掉跨帧通道取决于模型与精度要求。**

## 3. 动态线索与轻量训练：值得借鉴，但须注明训练成本

### 3.1 VGGT4D：把中间表示中的运动线索显式化

来源：[论文](https://arxiv.org/html/2511.19971)，重点 §3 与附录 §6；**冻结 VGGT，无额外网络训练**。

- **观察与证据：** camera-to-image 注意力的动态响应不稳定；普通 QK 同时混合纹理与语义。跨帧 $QQ^\top$、$KK^\top$ Gram 相似度在不同深度层提供互补运动线索。
- **设计：** 聚合浅/中/深层及邻近时刻的统计量产生动态 mask，结合投影残差梯度细化，并在早期推理层施加 mask 以稳定几何。
- **加速关系：** 主要贡献是动态区域发现与重建质量，不是通用 attention 降复杂度。Gram 构造和细化也有成本。
- **ARROW 启发：** 用来划分静态/动态区域并分别统计 attention，很有价值；直接屏蔽动态 token 可能毁掉跟踪。更合理的候选是给动态点、遮挡边界和重现点额外预算，而不是统一丢弃。

### 3.2 Co-Me：冻结主干，蒸馏一个置信度预测器

来源：[论文](https://arxiv.org/abs/2511.14751)、[作者项目页](https://co-me-tokens.github.io/)；**需要训练辅助模块，不能称为整个方法零训练**。

- **观察：** 模型置信度提供了比纯相似度更贴近任务的合并线索；低置信度区域适合更强压缩。
- **设计：** 从中间特征预测 token confidence，按置信度生成 merge mask，保护特殊 token；merge/split 用于 attention 与 MLP，使计算缩减不局限于注意力乘法。
- **效率来源：** 一次廉价预测替代昂贵的全局相似度匹配。主干不重训，但该预测器由蒸馏获得。
- **ARROW 启发：** 可研究其置信度代理能否迁移；ARROW 的低置信度也可能对应难跟踪运动或遮挡，必须防止删掉最需要上下文的点。相同位置的重建置信度与跨时刻跟踪置信度也不是一回事。

### 3.3 LiteVGGT

来源：[论文](https://arxiv.org/html/2512.04939)，重点 §3.3–3.5；**完整报告方案包含离线微调与 FP8**。

- **观察与证据：** 边缘输入仍能产生合理几何；梯度与 token 方差可以辅助定位结构信息；相邻层的 merge 关系较稳定，反复匹配会成为新瓶颈。
- **设计：** 融合像素梯度和 token 方差保护几何信息，缓存并周期复用 merge indices，再结合微调和低精度推理。
- **成本边界：** 文中微调 aggregator/heads，报告 8 张 H20、约三天。因此完整方案的最高约 10× 收益不能全部归因于免训练 token 合并。
- **ARROW 启发：** 可独立测试“缓存路由/合并索引”是否有效；细运动边界、重复纹理及低纹理区域均需单独评估，边缘强度只是启发式代理。

### 3.4 FlashVGGT

来源：[论文](https://arxiv.org/html/2512.01540)，重点 §3；**离线微调**。

- **观察与设计：** 全分辨率 query 需要的全局信息可由较少 descriptor 提供。双线性插值压缩 patch descriptor，补充所有 camera/register、首帧及聚类选出的关键帧 token，再做 full-Q 对 compressed-KV 的 cross-attention。
- **长序列：** chunk-recursive 推理复用过去的压缩 descriptor。
- **训练边界：** 冻结图像 encoder 和输出头，训练 alternating-attention aggregator；论文报告 4 张 H800、约 16 小时。它不是 FlashAttention 的别名，也不是原 VGGT 的纯免训练替换。
- **ARROW 启发：** 借鉴局部稠密与全局摘要并存；动态点身份可能需要比静态 descriptor 更精细的时刻区分。

### 3.5 TurboVGGT

来源：[论文](https://arxiv.org/html/2605.14315)，重点 §3.2–3.3；**需要离线训练**。

- **观察：** 高响应 token 的分布随层和帧变化，统一压缩率未必合理；低纹理背景也可能承担全局几何作用。
- **设计：** gating 网络按帧和层选择不同稀疏分支，学习 representative tokens，再以 cross-attention 聚合全局信息；frame attention 保持局部细节。
- **优化：** 用重建任务损失和鼓励稀疏的正则共同训练。
- **ARROW 启发：** 可把“按帧/层动态分配预算”转换成免训练启发式实验；直接复现其 learned router 则超出严格免训练范围。

### 3.6 VGGT-Prime：2026 年 9 月的 head 级分析

来源：[论文](https://arxiv.org/html/2609.23733)，重点 §3–4；**冻结教师，训练 router 和 surrogate attention**。

- **观察与证据：** 用 integrated gradients、最大 attention 和删头实验研究 head saliency；还比较注意力集中度及不同 query 的响应多样性。
- **设计：** 高重要性 head 用完整 attention，中等 head 用学习到的聚合和逐 token 修正，低重要性 head 采用廉价近似；避免仅做“保留/删除”二元选择。
- **成本边界：** router 与替代模块通过蒸馏训练，附录列出多数据集和十个 epoch，不能叫无需训练。
- **ARROW 启发：** 为“哪类头需要精确对应、哪类头只做公共信息广播”提供分析模板。几何主干的 head 排名不能直接用于 ARROW 动态 decoder。

## 4. 流式缓存：从保留全部历史到保留有效几何证据

### 4.1 先区分 StreamVGGT 和它的免训练后续方法

[StreamVGGT](https://arxiv.org/html/2507.11539) 把全局双向注意力改为时序因果注意力，并通过教师蒸馏训练；历史 KV 可复用，避免新帧到来时重算全部过去帧。**它本身需要训练。** 无限保留 KV 时，单步 attention 与缓存仍随历史增长。

以下多篇工作的“training-free”，意为直接使用**已经训练好的 StreamVGGT**，仅改变缓存管理；并不证明原版 VGGT、DA3 或 ARROW 加一个 causal mask 就能保持精度。ARROW 的双向编码也有同样边界。

### 4.2 Evict3R

来源：[论文](https://arxiv.org/html/2509.17650)，重点 §IV、§V-A；**基于 StreamVGGT 的免训练缓存管理**。

- **观察与证据：** 早晚层注意力更均匀，中段更选择性；一些 token 的重要性跨步骤持续。按层分配预算，以累积 attention 衡量历史 token 价值，并进行曝光次数等归一化。
- **设计：** 缓存达到预算后淘汰低分 token，保护首帧和特殊 token；不同层采用不同预算。
- **实际限制：** 论文实验关闭了 FlashAttention 来取得注意力图。因此其结果不能直接理解为“在最优 fused kernel 上仍有同样收益”。无限保护不断新增的特殊 token 时，还需检查实际实现如何满足硬预算。
- **ARROW 启发：** 适合作为 attention-based eviction 分析基线；部署方案应尝试采样、池化或融合统计，避免为了选 token 先完整计算最昂贵的矩阵。

### 4.3 InfiniteVGGT

来源：[论文](https://arxiv.org/html/2601.02281)，重点 §3.2–3.4；**基于 StreamVGGT，免训练**。

- **观察与证据：** 相邻视图和缓存 key 高度冗余；PCA/QK 分布分析提示可用 key 空间多样性替代完整 attention 评分。
- **设计：** 保留首帧全部 KV；可淘汰集合内，按 key 与归一化均值方向的差异保留多样 token；按层/头管理，依据层间多样性分配预算。
- **效率来源：** 不需提取完整 attention map，可与 fused attention 共存，控制活跃 KV 的长度。
- **ARROW 启发：** key diversity 是廉价对照，但“离群 key”不自动等于有用运动证据。ARROW 应保护查询指定的 reference/source/target 角色，而不是机械地保护输入数组首帧。

### 4.4 OVGGT

来源：[论文，2026-04-29 v3](https://arxiv.org/html/2603.05959v3)，重点 §3；**基于 StreamVGGT，免训练**。

- **观察与证据：** FFN 残差幅度随层呈现纹理、几何结构、语义边界等响应；直接 top-k 会破坏空间连续性，论文比较多种评分与平滑消融。
- **设计：** 新 token 用 FFN 残差评分加空间 Gaussian 平滑，历史 token 用 key diversity，归一化后联合选取；另维护永久首帧锚点及数量受限的历史锚点。
- **新版细节：** 历史锚点根据投影覆盖下降触发，保护高置信度部分，并用容量限制避免持续增长。仅说“保留首帧”不完整。
- **ARROW 启发：** 可测试残差幅度加动态/空间覆盖约束。$O(1)$ 指固定分辨率、固定预算下的单步工作量与缓存；整段视频总时间和输出不是常数。

### 4.5 XStreamVGGT

来源：[论文](https://arxiv.org/html/2601.01204)，重点 §3；**基于 StreamVGGT，免训练剪枝与 KV 量化**。

- **观察：** 当前帧只需部分历史；K 和 V 的幅值分布不同，K 存在明显的 channel outlier。
- **设计：** 保留首帧与当前帧；将当前 Q 分组池化，用低成本 QK 分数选择中间历史 token；K 采用 per-channel、V 采用 per-token 量化。
- **效率来源：** 同时减少读取 token 数和每 token 字节数；论文报告特定设置下约 4.42× 内存收益及 5.48× 加速，不能与其他论文直接排名。
- **ARROW 启发：** 解码器可按 query 角色/空间块池化 Q，选择共享 context。需注意跨 head 平均可能掩盖少数专门负责遮挡或匹配的 head。

### 4.6 FrameVGGT

来源：[论文](https://arxiv.org/html/2603.07690)，重点 §3–4；**免训练，属于 StreamVGGT/InfiniteVGGT 的缓存管理路线**。

- **观察与证据：** token 级剪枝会造成每帧证据稀薄、结构碎片化，以及 key 方向集中；固定预算下，单纯 recent-K 也会挤占互补历史。
- **设计：** 每帧每层 KV 作为整体单元；用 mean-key 描述子计算帧间差异，贪心 farthest-first 保留互补中期帧，另设稀疏长期 anchor。
- **必须区分：** 压缩的是用于选择的描述子，选中帧保留完整 KV；不是把每帧 KV 全部压成均值。
- **ARROW 启发：** 很适合比较“相同预算的完整帧 vs 零散 token”。ARROW 解码可能需要 source 外观、target 时刻和其他视角共同支持，保留完整证据组有望更稳，但这尚不是动态跟踪结论。

### 4.7 RetrieveVGGT：2026 年 5 月补充

来源：[论文](https://arxiv.org/html/2605.09644)，重点 §3；**基于 StreamVGGT，免训练**。

- **观察与证据：** 固定裁剪对所有未来 query 提供同一缓存；纯 top-k 又容易选中同一相似度峰的一堆冗余帧。
- **设计：** 在首次历史交互前提取 pooled Q/K 帧描述子；按当前 query 检索相关历史，Segment Sampling 将预算分配到多个高相关片段；结合 pose-aware spatial memory 控制历史冗余。一次帧选择复用于后续层。
- **效率来源：** 只有选中的帧参与大规模注意力；描述子检索和完整 KV 访问分离。
- **ARROW 启发：** 将检索 query 从“当前图像”拓展为“source/target/reference + 点区域”很有针对性。活跃 attention 有界不等于历史索引、备份 KV 和检索总成本天然为常数，需另外记录。

### 4.8 IncVGGT

来源：[论文](https://openreview.net/pdf?id=CezA1eLa1Y)；**免训练的增量系统**。

- **观察：** 冗余不仅在缓存里，也在高度重叠的输入图像里。
- **设计：** 输入侧注册并融合重叠图像为 composite views；历史侧保留相关的 top-k slots 和最新 slot，控制缓存。
- **效率来源：** 同时减少输入重复 token 与历史 attention 范围；区别于只改变注意力算子的方案。
- **ARROW 启发：** 静态背景可以考虑合成视图；运动区域合成会混合不同时刻，破坏 target ID 的意义。ARROW 更适合先实验静态背景复用，动态区域仍按原始观测保存。

### 4.9 KV-Tracker：最直接的 π³ 免训练在线化参照

来源：[论文](https://arxiv.org/html/2512.22581)，重点 §3.3–3.6；**使用既有 π³ 权重，无需训练因果模型**。

- **推理洞察：** 建图和实时 tracking 可分频运行；关键帧间需要充分交互，但每个到来的普通帧未必都要重建整个关键帧集合。
- **设计：** 建图时对关键帧集合做完整双向推理并缓存逐层 KV；跟踪时只计算新帧，让其读取缓存和自身 KV；插入关键帧后重新构建缓存。
- **效率来源：** 新帧使用矩形 attention，省去关键帧彼此的重复计算。缓存是充分融合后的场景表示，而非独立帧特征随意拼接。
- **ARROW 启发：** 可尝试关键帧联合编码、普通帧条件推理，但它并非完整双向推理的数学等价变形。论文中的 pose/object tracking 不等于 ARROW 的任意动态点轨迹；ID 与 patch context 的兼容性必须验证。

### 4.10 LongStream：为什么只管 cache 大小还不够

来源：[论文](https://arxiv.org/html/2602.13172)；**需要重新训练，作为机制对照**。

- **观察：** 长序列失效涉及第一帧坐标系下的外推、尺度耦合，以及短训练和长缓存推理之间的分布差异；注意力向少数历史位置集中也会使有效上下文缩小。
- **设计：** 关键帧相对位姿、尺度解耦，配合 cache-consistent training 和推理缓存刷新。
- **ARROW 启发：** 监测长期 anchor 的注意力占比、缓存年龄和尺度漂移。缓存装得下，不代表模型用得好；移除有害 sink 和保留坐标锚点之间需要实验平衡。

## 5. 切块与几何后端：能处理长序列，但不是 attention 可解释性论文

这类方法主要挖掘网络的**局部预测能力、重叠一致性和坐标误差结构**，并非每篇都分析内部 attention。它们可与第 2–4 节组合。

### 5.1 VGGT-Long

来源：[论文](https://arxiv.org/html/2507.16443)，重点 §3；**冻结主干、允许几何优化**。

- **设计动机：** 网络在有限窗口内可预测合理几何；超长联合推理既昂贵又不一定稳定。
- **模块：** 重叠 chunks 独立重建，利用置信度加权的重叠点云估计 Sim(3)，检测回环后做全局 Sim(3) 图优化。
- **效率来源：** 固定窗口限制模型工作集，避免整段全连接；代价是重复编码重叠帧和后端优化。
- **ARROW 启发：** 最务实的长序列基线。但局部点云对齐不自动解决全程 point identity、长遮挡后的重现，以及 source 帧不在新窗口时如何查询。CPU 地图与输出也继续增长。

### 5.2 SwiftVGGT

来源：[论文](https://arxiv.org/html/2511.18290)，重点 §3；**免网络训练**。

- **观察：** 深度不一致和低置信度区域会拖累窗口配准；独立 VPR 模型又重复提取已有的视觉信息。
- **设计：** 用深度差和置信度筛选稳定重叠点，以一次 Umeyama/SVD 代替局部 IRLS；复用 VGGT encoder 的 DINO patch 特征，经归一化、PCA 等构造回环描述子；保留全局图优化。
- **效率来源：** 降低配准迭代和额外特征提取开销，而非改造 attention。
- **ARROW 启发：** 复用已编码特征进行窗口检索、选锚点；ARROW 的动态输出需先区分同一时刻的重叠观测与不同时间的运动点。

### 5.3 VGGT-SLAM

来源：[论文](https://arxiv.org/html/2505.12549)；**不重训 VGGT，带显式优化后端**。

- **观察：** 不同子图的误差不一定仅为统一尺度和刚体变换，弱几何条件下还可能存在投影歧义。
- **设计：** 关键帧/子图推理、回环及 SL(4) 流形上的因子图优化，以更一般的变换注册子图。
- **加速关系：** 通过控制前端子图规模处理长序列，重点是全局一致性，并不是直接降低网络每层 FLOPs。
- **ARROW 启发：** 用于理解窗口间失配的类型；若后处理引入非刚性或投影变形，必须检查轨迹速度、位移和法向的物理含义是否仍一致。

### 5.4 LASER

来源：[论文](https://arxiv.org/html/2512.13680)，重点 §3；**冻结 VGGT/π³ 等模型，免训练窗口扩展**。

- **观察与证据：** 全局 Sim(3) 对齐后，近景和远景仍可能具有不同尺度误差，尤其在低视差场景。
- **设计：** 将点图划分为深度相近、空间连续的 depth layers，建立跨窗口及跨时间的 layer graph，传播和修正层级尺度。
- **效率来源：** 小窗口推理加较轻的几何修正。标题的 layer 指场景深度层，**不是 Transformer 层**。
- **ARROW 启发：** 当窗口拼接出现前后景相对变形时，是比继续调 attention 更直接的诊断路线。但 4D 重建结果不等于具备任意 source-to-target 稠密轨迹；层级修正对动态运动的影响还需单独评估。

## 6. Test-time training 与适配：哪些符合当前预算

### 6.1 TTT3R：由注意力推导状态更新权重

来源：[论文](https://arxiv.org/html/2509.26645)，重点 §3.3；**在 CUT3R 上免重训，主干不做测试时梯度微调**。

- **机制解释：** 将 recurrent state 的更新理解为在线学习；无差别持续写入会让短序列训练出的状态快速遗忘。
- **设计：** 根据状态 query 与观测 key 的对齐置信度，为每个 state token 构造自适应更新率，控制稳定性与可塑性。
- **效率关系：** 保持固定状态的推理形式，主要改善长序列质量；不是把一个二次 attention 算子直接替换成更快算子。
- **ARROW 启发：** 可启发“何时刷新/写入历史记忆”，但 ARROW 原本没有 CUT3R 的 recurrent state；不能只复制一个更新公式就得到可用的流式 ARROW。

### 6.2 Test3R：真正的场景级轻量适配

来源：[论文](https://arxiv.org/html/2506.13750)，重点 §4；**测试时优化 prompt token**。

- **观察：** 同一图像在不同配对中产生的 pointmap 不一致，提供无需真值的自监督信号。
- **设计：** 用共享图像的 triplets 构建跨 pair 几何一致性损失，冻结主干，以 visual prompt tuning 适配测试场景。
- **效率关系：** 少量可训练参数减少适配成本，但反复前向/反向通常增加总时间，主要目标是质量。
- **ARROW 启发：** 可研究重叠子集上的同 query 一致性；必须保持同一 source、target 时刻和 reference，并处理坐标尺度。跨时刻强迫运动点静止会产生错误监督。

### 6.3 Self-Geometry：2026 年 8–9 月的直接相关 TTA

来源：[论文 v2](https://arxiv.org/html/2608.10708v2)，重点 §III；**测试时 LoRA 适配**，实验覆盖 VGGT、π³、DA3 多尺寸。

- **观察：** 预测深度/相机的任务监督并不保证严格的跨视图一致性。
- **设计：** 外部匹配器给出伪对应，结合点到点和极线一致性，处理两种损失在相机参数上的梯度冲突，并选取角度多样的视图；仅更新 attention 中的 LoRA。
- **成本边界：** 作者报告单场景两分钟以内的特定硬件设置；仍需匹配、反向传播和适配时间，不是纯推理加速。
- **ARROW 启发：** 可用于静态背景或同步多视角的几何适配；任意动态跨时刻对应不满足同一静态场景的极线约束。应先证明适配成本可被后续大量查询摊销。

### 6.4 VGG-T³：TTT 作为全局场景记忆

来源：[论文](https://arxiv.org/html/2602.23361)，重点 §3、实现细节；**离线 post-training + 推理 fast-weight 更新**。

- **表示洞察：** 变长 KV 本身就是场景记忆。把 K→V 映射写入固定大小 MLP，再以 Q 查询它，可替代全局 softmax attention。
- **设计：** 修改 Q/K 归一化，加入局部空间混合，使 MLP 的写入和读取有效；保留离线集合的全局聚合能力。
- **关键纠正：** 论文包含 8 张 A100 上 100k 步的全局层训练。因此它不是“拿原 VGGT 在测试时拟合一个 MLP 就等价”。MLP 也不是因为“在线性空间”便与 softmax attention 相同。
- **ARROW 启发：** “一次写场景、反复回答 query”很契合使用方式，但把原 decoder context 压成 fast weights 是新研究问题，需要保真验证，不能据此声称免训练可行。

### 6.5 ZipMap

来源：[论文](https://arxiv.org/abs/2603.04385)、[作者代码说明](https://github.com/Haian-Jin/ZipMap)；**训练出的新模型及 TTT 层，非免训练插件**。

- **设计：** 将多视图集合写入紧凑 scene state，支持双向重建及对状态的快速查询，目标是线性长度扩展。
- **效率关系：** 论文报告单 H100 上 700+ 帧低于十秒；这是专门训练的状态表示，不是原始 VGGT/ARROW 的速度承诺。
- **流式边界：** 作者公开代码将 streaming 作为另行微调的分支，并说明训练长度及探索仍有限；不要把离线结果当成无限流式稳定性的证明。
- **ARROW 启发：** 是“可查询、固定大小 4D scene memory”的架构参照。若当前坚持 training-free，应把它放在长期方向而非首批实现。

## 7. 量化：另一条由网络推理分布得到的加速路径

### 7.1 QuantVGGT

来源：[论文](https://arxiv.org/abs/2509.21302)；**PTQ，需要校准**。

- **发现：** 数据无关的特殊 token 引入重尾激活，多视图校准样本选择不稳定。
- **设计：** global 前的 Hadamard 旋转和 local 后的通道平滑处理分布；过滤异常并选择多样校准视图，稳定量化范围。
- **效率：** 论文报告 4-bit 设置下约 3.7× 内存收益、2.5× 实际硬件加速。节省字节数与减少 attention 连接是不同维度。
- **ARROW 启发：** 先测 ID token、patch、decoder Q/K/V 的分布，再决定精度；不要把静态 pointmap 校准集当作动态 tracking 的充分校准。

### 7.2 QVGGT

来源：[论文](https://arxiv.org/abs/2605.31124)；**PTQ，需要校准与量化 scale 搜索**。

- **发现：** 各 block 对量化误差敏感性不一致；camera/register token 的异常幅度既影响统计，又承载必要几何信息。
- **设计：** 敏感 block 保持更高精度；校准时处理特殊 token 异常，并以 PCA 得到的补偿 token 补回几何信息；scale 搜索考虑多个任务头及几何一致性。
- **效率边界：** 文中最高加速比较含 FP32 基线，不能直接当作相对优化 BF16/FlashAttention 的额外收益。
- **ARROW 启发：** 更适合后续联合优化；ID token 的身份信息与原 camera token 功能不同，不能直接删掉后以全局 PCA 摘要代替。

## 8. 统一对照：这些方法究竟减少什么

| 路线 | 代表工作 | 减少的主要成本 | 额外学习/校准 | 对 ARROW 的直接程度 |
|---|---|---|---|---|
| 连接稀疏 | SparseVGGT | QK/PV 的有效块 | 无 | 高，编码/解码均可做原型 |
| 全 Q、稀疏/合并 KV | AVGGT、GPA-VGGT | 每个 query 读取的 context | 无 | 高，优先解码端验证 |
| Q/K/V 合并 | FastVGGT、HTTM | attention 序列长度 | 无 | 编码器较直接；decoder Q 合并风险高 |
| 按头分预算 | HeSS | 非关键 head 的连接 | 梯度校准 | 中高，须重新评估 tracking 敏感性 |
| 置信度/几何合并 | Co-Me、LiteVGGT | attention，部分还含 MLP | 辅助训练或微调 | 中，先拆出不训练的代理做对照 |
| 学习摘要/路由 | FlashVGGT、TurboVGGT、VGGT-Prime | 全局交互或 head 计算 | 离线训练 | 机制相关，超出严格免训练 |
| 有界缓存 | Evict3R、InfiniteVGGT、OVGGT、XStreamVGGT | 历史 KV 读写/attention | 不重训 StreamVGGT | 需先解决 ARROW 的流式表示兼容性 |
| 完整帧记忆/检索 | FrameVGGT、RetrieveVGGT | 活跃历史范围 | 不重训 StreamVGGT | 适合窗口选择和 query-conditioned context |
| 分频建图/跟踪 | KV-Tracker | 历史特征重复计算 | 无 | 值得验证，非原双向模型等价计算 |
| 窗口与对齐 | VGGT-Long、SwiftVGGT、VGGT-SLAM、LASER | 一次模型调用的帧数 | 无网络训练，可能有优化 | 高，但需增加轨迹身份衔接 |
| 状态写入控制 | TTT3R | 长期遗忘，非直接 FLOPs | 无重训 | 原 ARROW 缺少相同状态结构 |
| 场景适配 | Test3R、Self-Geometry | 几何不一致 | 测试时优化 | 主要补精度，需摊销适配成本 |
| fast-weight scene memory | VGG-T³、ZipMap | 变长全局 KV 查询 | 专门训练 + 测试时状态更新 | 长期架构方向 |
| 低比特 | QuantVGGT、QVGGT | 权重/激活或缓存字节数 | PTQ 校准 | 可叠加，需检验动态几何精度 |

不能把各篇最高倍数相乘。若编码占总时间比例为 $\alpha$，只让编码加速 $s$ 倍，总加速最多是

$$
S=\frac{1}{(1-\alpha)+\alpha/s}.
$$

对于极稠密 query，解码、CPU 传输与结果保存可能占主导；编码器的十倍加速也可能只带来很小的端到端收益。

## 9. 面向 ARROW 的可执行分析方案

**以下是本文提出的实验设计，不是以上论文已在 ARROW 上验证的结果。** 目标是用最小改动区分“真正的冗余”“对当前 query 无用”与“表面权重小但几何必需”。

### 9.1 先分解运行时间，保持任务不变

建议先做一个可承受的矩阵：帧数 16/32/64/128，再根据显存扩到 256；固定分辨率，分别使用稀疏点、中等网格、稠密网格。记录真正的 $F,T,P,Q$，不要只写视频时长或 `stride`。

每组测量：

- 图像读入与预处理、encoder、query embedding、context K/V 投影、cross-attention、query MLP/输出头、GPU→CPU、保存的耗时。
- GPU allocated/reserved 峰值、CPU RSS、最终输出大小、KV/descriptor/索引各自大小。
- warm-up 后同步计时；相同 GPU、dtype、分辨率、kernel 和输出任务；离线方法报整段延迟，流式方法另报首帧、平均及 P95 单帧延迟。
- 固定 query 集合比较模型加速；减少 query 数、降低分辨率、跳过目标帧另列为任务预算变化。

建议保存一份可复现清单：ARROW checkpoint/revision、代码 commit、输入帧列表、source/target/reference 配置、query 集、dtype、seed、kernel 与所有压缩预算。先建立未经近似修改的基线，不应把调小 query chunk 当作算法加速结论。

### 9.2 Encoder：检查跨视图对应在什么层、什么头产生

| 分析问题 | 具体统计/实验 | 支持什么设计 |
|---|---|---|
| attention 是否集中？ | 逐层逐头的 entropy、top-k mass、达到 90%/95% mass 的 key 数 | layer/head 自适应稀疏率 |
| 集中到哪些角色？ | 同帧、其他帧、特殊 token 分别占多少质量 | 特殊连接保护，局部/全局预算 |
| 是真实匹配还是语义相似？ | attention argmax 对 GT 对应的命中率；重复纹理、相同类别不同实例对照 | 识别不能合并的歧义区域 |
| 层是否可替代？ | 原层、frame-only、frame+global summary；保留其他残差/MLP | AVGGT 与 GPA 路线的公平比较 |
| head 是否关键？ | 同预算删头/删连接，对比随机、按强度、按敏感性选择 | HeSS 式预算分配 |
| 跨层关系是否稳定？ | top-k 集合 Jaccard、merge index 一致率、Q/K 子空间变化 | 减少每层重算路由 |
| 历史是否冗余？ | 帧间 key 相似度与共视/视差的联合统计 | 多样性与完整帧选择 |

记录真实 block 编号和 global-attention 序号，防止把 DA3 的总层编号与 VGGT 的 global block 编号混用。ARROW 已经过动态任务训练，几何 head 的位置甚至用途都可能发生变化。

### 9.3 Decoder：ARROW 最有区分度的分析对象

对 query $q=(u,v,s,t,r)$，按 head 和 decoder layer 取其 attention 行 $a_{q,j}$，将 context token 按来源帧组织：

$$
m_f(q)=\sum_{j\in\text{patches of frame }f}a_{q,j}.
$$

重点比较以下条件，而非只看平均热图：

| 条件 | 待回答的问题 |
|---|---|
| $s=t$ 的重建 vs $s\ne t$ 的跟踪 | 两种任务是否读取不同帧、不同层？ |
| 静态背景 vs 运动物体 | 动态 query 是否更依赖目标附近的时刻和其他视角？ |
| 可见、遮挡、重新出现 | 低置信度时需要更广 context，还是更多局部细节？ |
| 大/小时间跨度 | 需要远期证据，还是仅需要 source 和 target？ |
| 单目 vs 同步多视角 | 同时刻的其他视角能否替代更多时间邻帧？ |
| 固定 $s,t$、改变 $r$ | reference 只影响坐标变换，还是改变整个检索？ |
| 相邻源像素、相同 $s,t,r$ | 是否可共享 K/V 候选集合而保留独立 Q？ |
| 增加无关帧、打乱输入顺序 | 模型是否受到 attention 稀释，修改是否破坏集合性质？ |

单独汇总 source、target、reference 的质量及其他帧质量；若 $s=t$ 或 $t=r$，先对角色对应帧取并集，避免重复计数。帧级熵为

$$
H_{\mathrm{frame}}(q)=-\sum_f m_f(q)\log(m_f(q)+\epsilon),
\qquad n_{\mathrm{eff}}(q)=\exp(H_{\mathrm{frame}}(q)).
$$

只有这些 $m_f$ 覆盖完整 key 集合、和为 1 时，$n_{\mathrm{eff}}$ 才可如此解释；若另有非 patch key，需纳入一类或先说明条件归一化。ARROW 的 ID token 首先用于 query embedding，是否也是实际 decoder key，应按实现确认，不能因为编码器有 ID 就假定 decoder 也有同类特殊连接。

### 9.4 统计量之后必须有干预

至少设置三类对照：

1. **固定 encoded context，只修改 decoder。** 比较全部 K/V、角色帧 K/V、角色帧+检索帧、均匀稀疏 K/V、合并 K/V。先隔离解码误差。
2. **固定原 decoder，只修改 encoder。** 比较层替换、block sparse、K/V 合并，测输出保真与任务精度。
3. **两者组合。** 检查误差是否叠加，防止两个单独有效的模块同时启用后失效。

删掉注意力最大的区域、删掉最小的区域、随机删掉相同数量区域，分别测最终 tracking/pose 变化。删 head 时说明是在输出投影前将该 head 输出置零，还是改变 logits；两种干预含义不同。稀疏 attention 中排除的 logits 应在 softmax 前屏蔽为负无穷，不能简单把 logit 设为 0。

若训练几何 probe，应把训练集/测试集分离，并说明它只是分析工具；probe 可解码某种信息并不证明原网络实际使用它，还需上述干预。

### 9.5 获取注意力时避免把分析程序变成新瓶颈

- 保留正常推理的 fused attention 路径；另对少数层、头和 query 行重算诊断用 logits，不在全部帧上保存完整 $N\times N$ 或 $Q\times N$ map。
- 重算时使用与原网络一致的 QK normalization、RoPE、scale 和 mask；对比少量输出验证诊断实现。
- 可以只保存 Q/K 或按 key block 累积分母、top-k 和帧级统计。**只对抽样 key 做 softmax 会改变分母**，不能把结果冒充原 attention 的概率质量。
- 诊断采样覆盖动态、边界、遮挡、重复纹理、远距离对应；仅随机采样容易被静态背景淹没。
- profiling 运行和诊断运行分开，报告额外统计成本。若部署时仍需要评分，其成本必须重新计入端到端时间。

## 10. 推荐的 training-free 原型路线

### 10.1 优先级 0：先检查可精确复用的计算

ARROW 已经复用整段编码；进一步检查现有实现是否已做到：

1. **逐 decoder layer 复用 context K/V 投影。** 固定 context 下，若其归一化与 K/V 投影不依赖 query，可在多个 query chunk/任务间复用。不要重复实现已有缓存。
2. **按依赖项复用 query embedding。** 同一源点跨多个 target 的 RGB crop/坐标分量可复用；source-target-reference 的组合项按组合复用。以论文的加法分解为起点，再核对代码实际算子。
3. **限制结果驻留。** 逐块写出结果，避免 GPU/CPU 同时保留多份大张量；在相同输出集合下优化数据组织。

这组优化保持模型计算定义，先做数值误差检查，再测实际节省。K/V 缓存会增加持久显存，应按 query 数和复用次数权衡，不能默认所有层全部常驻都更好。

### 10.2 优先级 1：全部 query + 分层 K/V 压缩

建议按下列顺序试验：

- **基线 A：** 每帧均匀子采样 K/V，保留全部 Q，先扫保留率。
- **基线 B：** 对编码器采用 SparseVGGT 式 block sparse，特殊连接单独保护。
- **候选 C：** 对 decoder 做 GPA 式 K/V-only merge，保留每个点的独立 query。
- **候选 D：** 根据干预得到的敏感性分配层/头预算；不要仅按相似性最高的 head 先删。

若一组 key 足够接近，可用代表 key 和平均 value，并考虑其代表数量 $s_j$：

$$
\tilde a_j\propto\exp\left(\frac{q^\top\bar k_j}{\sqrt d}+\log s_j\right).
$$

当组内 key 完全相同时，这一质量补偿与相应平均 value 可以恢复该组的聚合贡献；一般情况下仍是近似。它修正的是“代表多少 token”，不能恢复已经被混合的运动身份、时刻和细节。merge 时至少测试是否禁止跨 source/target/reference 角色及不同时间的动态区域合并。

### 10.3 优先级 2：由 query 角色决定 context

借鉴 RetrieveVGGT、FrameVGGT、XStreamVGGT，构建候选集合：

$$
\mathcal C(q)=\mathcal C_{s,t,r}\cup\mathcal C_{\mathrm{retrieved}}(q)
\cup\mathcal C_{\mathrm{coverage}}.
$$

这里各部分分别保护查询相关角色帧、检索到的相关历史、空间或视角覆盖。它只是候选设计，**不能先假定只用 source/target/reference 就足够**；遮挡和重复外观可能依赖其他观测。

若每个 query 最终只访问固定 $B$ 个 token，attention 部分从 $O(QFT)$ 降到 $O(QB)$。但全历史检索、索引构建、encoder 和输出成本仍存在。为得到实际加速，宜按相同 $(s,t,r)$ 和小空间 tile 共享候选集合，而不是每个点做独立昂贵检索；同时给难点回退到更大 context 的机制。

共享候选集合不要求共享 query 输出，也不意味着把同一 tile 的所有点合并成一个轨迹。它可以保持 $Q$ 不变，更适合公平验证稠密查询加速。

### 10.4 优先级 3：窗口 + 关键帧，处理编码阶段的长度

**只在 encoder 之后压缩 decoder context，不会解决 encoder 的长序列计算。** 若 encoder 已超预算，需要窗口/关键帧策略。

先以 VGGT-Long 风格的重叠窗口为基线，在静态背景或相同时间的重叠观测上估计窗口变换。然后明确选择跨窗轨迹方案：

- 持续保留原 source 观测及其合法 ID，使新窗口仍能引用原物理点；其成本是源帧随跟踪任务增多。
- 或在重叠区用可见、可靠的预测位置重新播种并维护外部 track ID；此时是轨迹接力，会累计误差，且不能用不可靠遮挡位置盲目接力。
- 对长遮挡后的重现保留历史检索能力；单纯滑窗不具备这个保证。

窗口生成的 ID 和 patch features 依赖当次输入集合。不同窗口分别编码后，直接拼接 latent context、混用旧 ID 与新 patch features，通常不等价于共同编码。需要先证明兼容，或周期性联合重编码关键帧，参考 KV-Tracker 的建图/跟踪分频思想。

ARROW 的 reference 可以自由指定，因此保持的是**被查询角色及坐标约定**，而不是不分场景地锁定输入顺序中的第一帧。若每窗用局部 reference，应明确把 3D 点和位移变换到全局；法向仅旋转并重新归一化，不能照搬点的平移变换。

### 10.5 暂不优先：直接把原 cross-attention 拟合成 MLP

VGG-T³/ZipMap 说明 fast-weight memory 很有潜力，但不构成“原 ARROW 的 softmax 可直接免训练替换”的证据。特别是 decoder 的 query 表示与 context key 表示可能有明显分布差异，仅拟合 K→V 并不能保证在真实 query 上泛化。

若探索每场景小 MLP/adapter，应把它单列为轻量测试时学习：测拟合耗时、真实 query 分布上的误差、少数困难动态点、以及大量 query 下能否摊销成本。总收益条件是

$$
T_{\mathrm{fit}}+T_{\mathrm{encode,new}}+T_{\mathrm{decode,new}}
<T_{\mathrm{encode,base}}+T_{\mathrm{decode,base}},
$$

不能只报告拟合完成后的查询速度。

## 11. 如何评价，才不会把“更快”建立在任务缩水上

| 维度 | 必须记录的内容 |
|---|---|
| 跟踪 | WorldTrack 的 APD/EPE 或选用数据集的官方指标；静态与动态分别报；可见、遮挡、重现分组 |
| 几何 | 相机 ATE/RPE、严格位姿阈值、深度与点云误差；不能只用宽松 AUC |
| 长期一致性 | 窗口接缝、尺度漂移、长遮挡再识别、回环、运动边界及细物体 |
| 计算 | 固定 query 数/输出任务；编码与解码分开计时；校准、路由、检索、CPU 搬运和写盘另报 |
| 内存 | GPU 活跃 KV、临时 workspace、CPU 历史库、索引与输出各自增长率 |
| 泛化 | 静态/动态、低纹理/重复纹理、小/大视角、短/长时间跨度、单/多相机 |
| 因果性 | 严格在线实验只能使用当前与过去帧；离线/有窗口延迟的结果单列 |

建议以“相同精度下吞吐/显存”及“相同预算下质量”的 Pareto 曲线比较，而非只摘单个最高加速倍数。窗口实验可使用序列级统一尺度/坐标对齐，但不要用逐窗口真值对齐消除算法本身的漂移。

至少保留以下消融组：完整模型；均匀采样；随机同预算；K/V-only；Q/K/V 同时压缩；关键角色保护开/关；token 级与完整帧级同预算；评分/检索成本计入前后；encoder-only、decoder-only、二者组合。

## 12. 阅读与复现顺序，以及原笔记的关键修正

对当前 ARROW 目标，建议顺序是：

1. **可解释性论文 → SparseVGGT → AVGGT → GPA-VGGT。** 建立对应、稀疏和全 Q/压缩 KV 的分析框架，特别注意早期跨帧信息的分歧。
2. **HTTM → HeSS。** 将统一压缩率改为逐头机制，并控制匹配/评分开销。
3. **KV-Tracker → FrameVGGT → RetrieveVGGT。** 研究完整关键帧证据、缓存重建和 query-conditioned 历史选择。
4. **InfiniteVGGT → OVGGT → XStreamVGGT。** 比较无需完整 attention map 的评分，以及缓存量化。
5. **VGGT4D + VGGT-Long/LASER。** 前者帮助分析动态区域，后两者建立窗口与对齐基线；它们解决不同环节。
6. **Co-Me、Test3R、Self-Geometry。** 在纯免训练方案的精度上限明确后，再衡量辅助训练或测试时适配是否划算。

对原 `4drecon_tracking.md` 中相关条目，本文需要保留的修正是：

- SparseVGGT 保护的不只是 special–special，还包括特殊 token 与 patch 的双向交互。
- AVGGT 保留全 Q；第一帧保护针对 VGGT，π³ 的处理不同；对角线策略属于 self-attention。
- FrameVGGT 的 mean-key 用于帧选择，被选中帧的完整 KV 仍保留。
- OVGGT 新版包含有容量限制的历史锚点，而不只是首帧保护。
- TTT3R 的免训练状态更新、Test3R 的场景 prompt 优化、VGG-T³ 的专门训练加 fast-weight 机制是三类不同事情。
- FlashVGGT、LiteVGGT、TurboVGGT、VGGT-Prime 不能归入完整零训练方案；Co-Me 是冻结主干但训练小模块。
- 解释性论文新版不只分析 VGGT，也直接分析 DA3；这比只凭 VGGT 类比 ARROW 更有参考价值，但仍未直接覆盖 ARROW 微调后的网络。

**当前最值得检验的研究假设：ARROW 的独立 query 解码是否具有随 source/target/reference 角色变化的稀疏 context 需求；若成立，能否以全 query、共享候选 K/V、逐头预算和困难点回退实现加速，同时保留动态点身份和长遮挡重现能力。** 这一假设比单纯套用 VGGT 的统一 token merging 更贴近 ARROW 的接口和实际瓶颈。


