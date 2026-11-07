# Rice 并行编译学派

## 零、一句话定位

> **Rice 学派把"自动并行化"从一堆启发式技巧，变成了一门以依赖分析为公理、以循环变换为推理规则的学科**——并且在它自己最雄心的产品（HPF）失败之后，留下的依赖理论成了此后三十年所有循环优化（包括今天的多面体编译、Halide、MLIR affine dialect）的共同地基。

它和你现在手上的格论/不动点那条线**用的是完全不同的数学**。第七节会说清这个分野，那是本文最值得看的部分。

---

## 一、Ken Kennedy（1945–2007）

| | |
|---|---|
| 学术出身 | NYU Courant，Jack Schwartz 门下（SETL 项目）—— 所以他的底子是**语言实现 + 程序变换**，不是体系结构 |
| 到 Rice | 1971 年，一直到去世；**创建了 Rice 的计算机系**（1984） |
| 组织层面 | 1989 年创建 **CRPC**（Center for Research on Parallel Computation），NSF 科学技术中心；这是把 Rice、Caltech、Argonne、Syracuse、Tennessee（Dongarra）串起来的枢纽 |
| 政策层面 | 克林顿时期与 Bill Joy 共同主持 **PITAC**（总统信息技术顾问委员会），1999 年的 PITAC 报告直接推动了美国对高性能计算与网络的持续投入 |
| 荣誉 | NAE 院士、ACM Fellow、W. Wallace McDowell 奖、SIGPLAN 成就奖 |
| 身后 | **ACM-IEEE CS Ken Kennedy Award**（2009 设立）以他命名，是高性能计算/编译领域的最高个人奖项之一 |

⭐ **要理解这个"学派"，得先理解 Kennedy 不只是研究者，更是一个机构建造者。** Rice 的影响力有一半来自 CRPC 这个平台：它把编译器研究者、数值库作者（LAPACK）、应用科学家强制放在同一个房间里。这造就了 Rice 的方法论特征——**不做纯理论，一切以真实 Fortran 代码为检验**。

---

## 二、技术主线

### ① 自动向量化：PFC 与 Allen–Kennedy 算法

**PFC（Parallel Fortran Converter，1980s 初）**是 Rice 的第一个系统，Randy Allen 的博士工作。核心产出：

> **Allen & Kennedy, "Automatic Translation of FORTRAN Programs to Vector Form," TOPLAS 1987**

算法思想（至今仍是教科书讲法）：

```
1. 建依赖图（节点 = 语句，边 = 依赖，标注 level = 由哪层循环携带）
2. 对当前层：求依赖图的强连通分量 SCC
3. SCC 只有单个节点且无自环  ⇒  该语句可向量化，发射向量指令
   SCC 有多个节点或有自环    ⇒  该层必须保持串行，剥掉这层，对 SCC 内部递归
4. 按 SCC 的拓扑序发射（这一步隐含了 loop distribution）
```

⭐ **这个算法的美在于它把"能不能向量化"化归为一个纯图论判定**：SCC 的存在就是递归依赖的存在，就是串行性的来源。与 Illinois 的 Parafrase（模式匹配式的变换序列）相比，Rice 第一次给了**可证明完备**的结论——在依赖信息精确的前提下，Allen–Kennedy 发射出的向量化是最优的。

### ② 依赖测试：从理论到工程的分级决策

依赖分析要回答的问题：循环

```fortran
do i = 1, n
  A(2*i)   = A(3*i + 1) + 1
end do
```

中，是否存在 $i_1, i_2 \in [1,n]$ 使 $2i_1 = 3i_2+1$？这是一个**带约束的丢番图方程**。

Rice 的贡献不是发明某个测试（GCD 测试很早就有，Banerjee 不等式来自 Illinois 的 Utpal Banerjee），而是**把测试体系化**：

> **Goff, Kennedy & Tseng, "Practical Dependence Testing," PLDI 1991**

这篇论文的做法是建一棵决策树：按下标的形态分类（ZIV / SIV / MIV——零、单、多个归纳变量），对每类用最便宜的精确测试，只在必要时退到昂贵的通用方法。其中 **Delta test** 处理 SIV 的情形，覆盖了真实科学代码里的绝大多数下标。

| 测试 | 代价 | 精确性 |
|---|---|---|
| **GCD** | $O(1)$ | 不完备（忽略循环边界） |
| **Banerjee** | 多项式 | 不完备（实数松弛，忽略整数性） |
| **Delta / SIV**（Rice） | 常数 | 在其适用的下标形态上**精确** |
| **Omega**（Pugh, Maryland） | 最坏指数 | 精确（Presburger 判定） |
| **I-test, λ-test, …** | 中间 | 中间 |

⭐ **"分级决策 + 对常见情形做精确判定"是 Rice 方法论的典型切片**：不追求单一的通用算法，而是经验驱动地分解问题。这个思路后来被 LLVM 的 `DependenceAnalysis`、GCC 的 `tree-data-ref` 原样继承。

### ③ 循环变换与合法性判据

有了依赖向量（distance / direction vector），变换的合法性就有了统一判据：

> **一个重排变换合法 $\iff$ 它不反转任何依赖**（变换后所有依赖向量仍 lexicographically 非负）

于是 interchange、fusion、fission、skewing、tiling、unroll-and-jam 都从"经验技巧"变成了可验证的定理。Rice 这边的代表作：

- **Allen & Kennedy, "Automatic Loop Interchange"**（1984）——交换的合法性条件
- **Carr & Kennedy, "Improving the Ratio of Memory Operations to Floating-Point Operations in Loops," TOPLAS 1994** —— **unroll-and-jam + 标量替换（scalar replacement）**，即把数组引用提升到寄存器。这篇是"寄存器级数据重用"的奠基工作。

### ④ 存储层次：从"并行"转向"局部性"

1990 年前后，Rice 做了一个关键的判断转向：**向量机时代结束了，瓶颈从算力转到了内存**。代表作：

> **McKinley, Carr & Tseng, "Improving Data Locality with Loop Transformations," TOPLAS 1996**

它的做法是建一个 cache 代价模型（估算每种循环置换下的 cache line 引用次数），然后在合法置换空间里搜最优。

⭐ **这篇论文的历史意义：它把循环优化的目标函数从"并行度"换成了"访存代价"。** 今天 tiling 之所以是所有编译器的标配，源头在这里。

### ⑤ Fortran D 与 HPF：数据分布

Rice 承认了一件事：**全自动并行化在分布式内存机器上做不到**。因为编译器无法猜出数组应该怎么切分到各节点。于是：

> **Fortran D**（Fox, Hiranandani, Kennedy, Koelbel, Kremer, Tseng, Wu, 1990 起）
> 程序员用指令声明数据如何**分解（decompose）**与**对齐（align）**，编译器负责生成通信。

核心机制：

| 概念 | 含义 |
|---|---|
| **owner-computes rule** | 谁拥有被赋值的数据，谁执行这条语句 ⇒ 计算划分由数据划分唯一导出 |
| 通信生成 | 由依赖分析 + 分布函数算出需要交换哪些边界元素 |
| 通信优化 | **message vectorization**（把循环内的逐元素通信提升到循环外批量发送）、聚合、流水 |

Fortran D（Rice）与 **Vienna Fortran**（Hans Zima 的欧洲同期工作）共同成为 **HPF（High Performance Fortran，1993）** 的基础。Charles Koelbel（Rice）是 HPF 手册的第一作者。

### ⑥ ParaScope：承认自动化的失败

> **ParaScope Editor**（Cooper, Hall, Hood, Kennedy, McKinley, Mellor-Crummey, Torczon, Warren, Proc. IEEE 1993）

一个**交互式**并行化环境：编译器把依赖图算出来展示给程序员，程序员判断哪些依赖是假的（编译器因保守而误报的）、哪些变换该做，工具负责保证正确性。

⭐ 这是 Rice 学派最诚实的一次自我评价：**依赖分析的精度上限决定了自动化的上限，剩下的缺口只能由人补。** 第六节会说这个判断后来如何被历史验证。

### ⑦ 后期：telescoping languages、Coarray Fortran 2.0、HPCToolkit

- **Telescoping languages**（Kennedy 最后的大构想）：把库函数提前编译成多个特化变体，调用点按上下文选最优的。这是今天 **autotuning / kernel library**（ATLAS、oneDNN、cuBLAS 的 heuristic dispatch）的思想先驱。
- **Coarray Fortran 2.0**（Mellor-Crummey）：PGAS 路线，HPF 失败后的另一条路。
- **HPCToolkit**（Mellor-Crummey）：至今仍是 HPC 领域主流的采样式性能分析工具。
- **Habanero**（Vivek Sarkar，2007 年从 IBM 加入 Rice）：任务并行、async-finish 模型，影响了 Java 的 Fork/Join 与 Habanero-Java。

---

## 三、Rice 的另一半：Cooper & Torczon 线

你会注意到我在书单里同时推荐了 **Allen & Kennedy** 和 **Cooper & Torczon**，两本书风格迥异却同出一门。因为 Rice 实际上有**两条并行的研究线**：

| | Kennedy 线 | **Cooper & Torczon 线** |
|---|---|---|
| 对象 | 循环嵌套、数组、迭代空间 | 标量、SSA、寄存器、过程 |
| 数学 | 整数线性代数、多面体 | **序论格、不动点、图着色** |
| 代表成果 | PFC、Fortran D、locality | 寄存器分配、值编号、支配树 |
| 代表书 | *Optimizing Compilers for Modern Architectures* | *Engineering a Compiler* |

Cooper–Torczon 线的关键论文：

- **Briggs, Cooper, Kennedy & Torczon, "Coloring Heuristics for Register Allocation," PLDI 1989** 与 **Briggs, Cooper & Torczon, "Improvements to Graph Coloring Register Allocation," TOPLAS 1994** —— ⭐ **乐观着色（optimistic coloring）**。Chaitin 的做法是度数 $\ge k$ 就立刻 spill；Briggs 的洞察是先推入栈、等真着色时再看——很多时候邻居用了重复颜色，根本不必 spill。这是图着色寄存器分配从"可用"到"好用"的转折点，也是 **Chaitin–Briggs** 这个连字符名字的来源。还顺带引入了 **rematerialization**（重算比 spill 便宜时就重算）。
- **Cooper, Harvey & Kennedy, "A Simple, Fast Dominance Algorithm"（2001）** —— 迭代式算支配者。渐进复杂度不如 Lengauer–Tarjan，但**实测更快、代码短十倍**，LLVM/GCC 实际用的就是它的变体。
- **Cooper & Kennedy, "Interprocedural Side-Effect Analysis in Linear Time," PLDI 1988** —— 过程间 MOD/USE 集合。
- **Simpson 的 SCC-based value numbering** 与 Cooper–Simpson 的 **GVN** 系列。
- **Click & Cooper, "Combining Analyses, Combining Optimizations," TOPLAS 1995** —— ⭐ 这篇我在书单里单独列过：**分开跑两个 pass 会丢精度**，因为 pass A 的结果本可以让 pass B 发现更多机会，反之亦然，顺序固定就只能取一个方向的闭包。正确做法是把两个分析的格做乘积，一起求不动点。（Cliff Click 后来去做了 HotSpot Server 编译器的 Sea-of-Nodes IR。）

> 两条线在 Rice 的教学体系里合并成了一门完整的编译后端课程，这就是 *Engineering a Compiler* 后端部分质量明显高于龙书的原因。

---

## 四、学派对比

| 学派 | 领袖 | 系统 | 特征标志 | 工业化路径 |
|---|---|---|---|---|
| **Rice** | Ken Kennedy | PFC, ParaScope, Fortran D, dHPF | 依赖分析体系化、**分级精确测试**、locality 代价模型、承认人机协作 | HPF（失败）；依赖理论进入所有编译器 |
| **Illinois** | David Kuck | Parafrase, Cedar | **Banerjee 不等式**、向量机导向、变换的目录式枚举 | **KAI → Intel 编译器**（1979 创立，2000 被 Intel 收购），Michael Wolfe → **PGI/NVIDIA** |
| **Stanford** | Monica Lam | **SUIF** | **unimodular / 仿射变换**的统一框架、cache blocking 理论、affine partitioning | SUIF 成为学术界十年的公共基础设施；Amarasinghe → MIT → **Halide / TACO** |
| **Maryland** | Bill Pugh | Omega Library | **Omega test**：Presburger 判定，精确依赖分析 | Omega 的整数集机制 → 后来的 isl |
| **IBM** | Fran Allen / John Cocke | PTRAN, PL.8 | 控制流分析、变换目录、**SSA**、**Chaitin 着色** | 直接进入 IBM 商用编译器；SSA 成为全行业标准 |
| **Vienna** | Hans Zima | SUPERB, Vienna Fortran | 分布式内存、数据分布语言 | 与 Fortran D 共同促成 HPF；Barbara Chapman → **OpenMP** |
| **INRIA/多面体** | Paul Feautrier | PIP, CLooG, isl, Pluto, Polly | ⭐ **把所有循环变换统一为一个仿射调度的优化问题** | **GCC Graphite、LLVM Polly、MLIR affine** |

### ⭐ Rice 与多面体学派的根本分歧

这是整张表里最重要的一条：

| | Rice（变换序列） | 多面体（统一搜索） |
|---|---|---|
| 优化的形式 | 一串**具名变换**：interchange, fusion, tile, skew… | **一个**仿射调度函数 $\theta(\vec i) = A\vec i + \vec b$ |
| 怎么找最优 | 启发式 + 代价模型，在变换序列空间里试 | 把"保持依赖 + 最小化某目标"写成 ILP，**解出来** |
| 优势 | 可解释、可调试、工程可控 | 能发现复合变换（如 skew+tile+fuse 的组合），搜索空间完整 |
| 代价 | 组合爆炸、phase ordering 问题 | ILP 规模爆炸、只能处理静态仿射控制流（SCoP） |

Rice 的 Allen–Kennedy 是**算法式**的；Feautrier–Bondhugula 的 Pluto 是**求解式**的。Michael Wolfe 和 Banerjee 的 unimodular 变换是两者之间的桥梁（用矩阵统一描述重排，但仍是离散变换）。

**今天的局面**：MLIR 的 affine dialect 用多面体表示，但实际 pass 大量是 Rice 风格的具名变换；Halide / TVM 用"调度语言"让程序员指定变换序列——**这反而是 ParaScope 和 Fortran D 的精神回归**。

---

## 五、⭐ 什么让它成为一个"学派"

不是某个定理，而是**一套可传授的方法论**：

1. **先建精确的程序表示（依赖图），再在表示上做变换。** 不做窥孔式的模式匹配。
2. **合法性与收益分离。** 依赖分析回答"能不能"，代价模型回答"该不该"。这个分离让两半可以独立改进——至今仍是循环优化器的标准架构。
3. **精度/代价分级。** 不追求单一通用算法，承认 90% 的真实代码落在简单情形里，为它们做精确判定。
4. **真实代码驱动。** 一切用 Fortran 科学计算基准（后来的 SPEC、Perfect Club）检验，不靠构造例子。
5. **承认自动化的边界，设计人机接口。** ParaScope、Fortran D 指令、telescoping languages 都是这一条的产物。
6. **工程与教学的闭环。** Rice 两本书都是系统实现的副产品。

---

## 六、⚠️ 诚实评价：HPF 为什么失败

HPF 在 1993 年被视为并行计算的未来，所有大厂都实现了编译器。**五年后它基本死了。** MPI 赢了，后来 OpenMP 赢了共享内存那半。

失败原因（这是编译器史上最值得研究的案例之一）：

| 原因 | 说明 |
|---|---|
| **性能不可预测** | 同样的代码，改一个指令、换一个编译器，性能差 10 倍。程序员无法建立心智模型 |
| **抽象泄漏** | 为了调性能，程序员必须猜编译器怎么生成通信——于是还不如直接写 MPI |
| **编译器质量参差** | 标准复杂，各家实现的优化水平差异巨大，可移植性承诺落空 |
| **不规则问题支持差** | 稀疏矩阵、自适应网格、粒子法等不满足仿射假设，而这些恰是真实应用的大头 |
| **MPI 太成功** | 显式、可预测、可移植、库而非语言——不需要编译器厂商配合 |

⭐ **教训的提炼**：**当编译器的自动决策影响性能一个数量级，而程序员无法观察或干预这个决策时，抽象就会被绕过。** 这个教训后来被 Halide 精确吸收——Halide 的核心设计是 **algorithm 与 schedule 分离**：算法由程序员写，调度**也**由程序员写（或由 autotuner 搜），编译器只保证"按这个调度生成的代码是正确的"。这正是 HPF 失败换来的设计原则。

**但依赖理论活下来了。** Rice 的依赖分析、循环变换合法性判据、locality 代价模型，今天在 GCC、LLVM、ICC、MLIR、Halide、TVM 里无一例外地在跑。**HPF 是产品，依赖理论是科学——前者死了，后者成了基础设施。**

---

## 七、⭐ 接回你的格/不动点线：一个编译器里的两种 lattice

这是本文对你最有用的一节。

### (1) 同一个编译器里，"lattice" 这个词真的有两种意思

还记得你笔记里那条 ⚠️ 术语歧义警告——序论的格 vs $\mathbb R^n$ 里的离散子群？**它们在同一个优化编译器里共存**：

| | 前端/标量优化 | 循环嵌套优化 |
|---|---|---|
| lattice 指 | **序论格** $(L,\sqcup,\sqcap)$ | **数论格**：$\mathbb Z^n$ 的子群 |
| 出现在 | 数据流分析、SSA、SCCP、值编号、抽象解释 | GCD 测试、Omega/isl 的 Hermite 标准形 |
| 典型问题 | $\mathrm{lfp}\,F$ | $A\vec x = \vec b$ 有无整数解 |

**GCD 测试字面上就是一个 $\mathbb Z$-格的成员判定问题**：

```fortran
A(2*i) = ... A(2*j + 1) ...
```
依赖需要 $2i - 2j = 1$ 有整数解，即 $1 \in 2\mathbb{Z} + 2\mathbb{Z} = 2\mathbb{Z}$。$\gcd(2,2)=2 \nmid 1$，故无解 ⇒ 无依赖。**这是在问"某个点是否落在一个子格里"**，和 LLL/LWE 用的是同一种格。

而 **isl（integer set library）** 的名字和内部机制同时包含两者：它处理的对象是"仿射多面体 ∩ $\mathbb Z$-格"，Hermite 标准形是其核心算法之一。

> 所以你那条警告不是"两个无关概念撞名"，而是**两种数学工具在编译器里的分工**：一种管"事实的合并"，一种管"整点的存在"。

### (2) 为什么数据流分析做不了循环并行化

这个问题的答案，正是你前面那条"**程序点是上下文不敏感分析的下标集合**"的直接推广。

数据流分析的下标集合是 **program point**。而一个循环头**只有一个程序点**，却对应 $n$ 次迭代：

```c
for (i = 0; i < n; i++)       // • p —— 唯一的程序点
    A[i] = A[i-1] + 1;        //        但有 n 个迭代实例
```

于是在 $p$ 处的 join **把所有迭代合并成一个格值**。而"第 $i$ 次迭代写的是 $A[i]$、第 $i+1$ 次读的是 $A[i]$"这个信息，**恰恰在这次 join 中被彻底销毁**。

这就是你前面遇到的"提前 join 损失精度"的极端形态：**循环头的 join 把整个迭代空间压成一个点。**

| 敏感性 | 下标集合 | 解决什么 |
|---|---|---|
| 流敏感 | program point | 语句顺序 |
| 上下文敏感 | $(\text{point}, \text{context})$ | 递归/调用点混淆 |
| ⭐ **迭代敏感** | $(\text{point}, \vec i)$，$\vec i$ = 迭代向量 | **循环携带的依赖** |

**依赖分析的做法就是把下标精细化到 $(\text{语句}, \text{迭代向量})$。** 但这里有个关键困难：

> 迭代空间 $\{\vec i \mid 1 \le i \le n\}$ 的大小**依赖于运行时参数 $n$**，不可枚举。

所以**不能**用"有限格 + Kleene 迭代"这套机器。必须改用**符号化的仿射表示**（多面体、Presburger 公式），把"对所有 $\vec i$"变成一个约束而不是一个枚举。

⭐ **这就是两种数学的分工点**：

| | 下标集合有限 | 下标集合参数化无限 |
|---|---|---|
| 表示 | 格元素的映射表 $L^{\text{Points}}$ | 仿射约束 / 多面体 |
| 求解 | **Kleene 迭代至不动点** | **整数线性规划 / Presburger 判定** |
| 终止性来自 | 格的 ACC | Presburger 算术可判定 |
| 精度上限由 | **分配性**（Kildall） | **依赖测试的完备性** |

### (3) Feautrier 的 array dataflow analysis：把 MOP 搬到参数化情形

有一个漂亮的交汇点。Feautrier 的 **"Dataflow Analysis of Array and Scalar References"（1991）** 要算的是：

> 对每一个读 $\langle S, \vec i\rangle$，**是哪一次写**产生了它读到的值？

形式上是

$$\mathrm{source}(S,\vec i) = \max_{\prec_{\text{lex}}} \{\langle T,\vec j\rangle \mid T \text{ 写了同一元素},\ \langle T,\vec j\rangle \prec \langle S,\vec i\rangle\}$$

⭐ **这是逐迭代、逐路径的精确答案——即"参数化版本的 MOP"**，而不是在程序点上 join 之后的 MFP。它之所以精确，正因为它**没有**在循环头做 join；它之所以昂贵（需要参数化整数规划 PIP），也正因为如此。

于是三条线对上了：

| 方法 | 相当于 | 精度 | 代价 |
|---|---|---|---|
| 到达定值（标量数据流） | MFP，下标 = program point | 数组整体当一个变量，几乎无用 | 线性，位向量 |
| 依赖分析（Rice） | 判定两个迭代实例间**是否**有依赖 | 够做变换合法性判定 | 多项式（分级测试） |
| array dataflow（Feautrier） | **MOP**，下标 = $(\text{stmt}, \vec i)$ | 精确到"哪次写供给哪次读" | 参数化 ILP |

**你的 `lfp` 求解器能做第一行；第二三行需要换一整套数学。** 这个边界值得记住——它说明"万物皆不动点"是有适用范围的，而范围的边界就是"下标集合是否有限"。

---

## 八、人员谱系（为什么说"学派"）

**Kennedy 线的学生与同事**：

| 人 | 后来 | 做了什么 |
|---|---|---|
| **Randy Allen** | 工业界（Ardent、Catalytic） | PFC、Allen–Kennedy 算法、合著 2001 年那本书 |
| **Kathryn McKinley** | UMass → UT Austin → MSR → Google | ⭐ locality 变换 → 转向内存管理：**Immix GC**、**DaCapo benchmark**（与 Steve Blackburn）。从循环跳到 GC，是领域迁移的典型 |
| **Mary Hall** | Stanford(SUIF) → USC/ISI → Utah | 过程间并行化 → **CHiLL**、autotuning。是 Rice 传统与多面体/自动调优的接口 |
| **Chau-Wen Tseng** | Maryland | Fortran D 编译器、Delta test、locality |
| **Steve Carr** | Michigan Tech | unroll-and-jam、标量替换 |
| **Charles Koelbel** | NSF | HPF 手册第一作者 |
| **Preston Briggs** | Tera/Cray → Google | ⭐ 乐观着色 |
| **Keith Cooper / Linda Torczon** | 留 Rice | 标量优化线、*Engineering a Compiler* |
| **John Mellor-Crummey** | 留 Rice | ⭐ **MCS 锁**（与 Michael Scott，TOCS 1991）、HPCToolkit、Coarray Fortran 2.0 |
| **Vivek Sarkar** | IBM → Rice(2007) → Georgia Tech | PTRAN(IBM) → Habanero、任务并行 |

⭐ 注意 **Mellor-Crummey** 这条：MCS 锁是并发领域引用最多的成果之一，和编译器没关系——Rice 的 CRPC 环境让编译、运行时、性能工具的人在一起工作，这类跨界成果就是副产品。

---

## 九、读什么

接续我之前给你的书单，针对这一支的具体路径：

**入口（必读）**
- **Allen & Kennedy, *Optimizing Compilers for Modern Architectures*（2001）**——学派的教科书化总结。前 5 章（依赖理论）是永恒的；后半的向量机内容读作历史。
- **Cooper & Torczon, *Engineering a Compiler*（3rd ed.）**——同一学派的另一半。

**论文（按主题）**
- 向量化：Allen & Kennedy, TOPLAS 1987
- 依赖测试：Goff, Kennedy & Tseng, PLDI 1991 ⭐（读这一篇就懂"分级精确"的工程哲学）
- 局部性：McKinley, Carr & Tseng, TOPLAS 1996 ⭐
- 寄存器级重用：Carr & Kennedy, TOPLAS 1994
- 寄存器分配：Briggs, Cooper & Torczon, TOPLAS 1994 ⭐
- 数据分布：Hiranandani, Kennedy & Tseng, CACM 1992
- 人机协作：ParaScope, Proc. IEEE 1993（读它的动机部分）

**对照阅读（理解分歧）**
- **Wolfe, *High Performance Compilers for Parallel Computing*（1995）**——Illinois 视角，unimodular 变换，与 Allen–Kennedy 并读最有收获
- **Pugh, "A Practical Algorithm for Exact Array Dependence Analysis," CACM 1992**——Omega test，看"精确但指数"的另一极
- **Feautrier (1991, 1992)** + **Bondhugula et al., "A Practical Automatic Polyhedral Parallelizer and Locality Optimizer," PLDI 2008（Pluto）**——⭐ 看"变换序列"如何被"统一求解"替代
- **Ragan-Kelley et al., "Halide," PLDI 2013**——看 HPF 的教训如何变成设计原则

**历史与反思**
- Kennedy, Koelbel & Zima, **"The Rise and Fall of High Performance Fortran: An Historical Object Lesson," HOPL III (2007)** ⭐⭐ —— **Kennedy 本人（去世前）对 HPF 失败的复盘**。这是整份清单里最该读的一篇：一个学派领袖公开剖析自己最大项目为何失败，在计算机科学文献里极为罕见。

---

## 十、一句话总结

> **Rice 学派的核心资产不是任何一个系统，而是"依赖分析 → 变换合法性 → 代价模型"这条三段式推理链**：它把循环优化从技巧变成了可证明的学科，并确立了"合法性与收益分离"的架构，这个架构今天仍在 GCC、LLVM、MLIR、Halide 里原样运行。
>
> 它的两次失败同样有价值：**HPF 证明了"当编译器的自动决策影响性能一个数量级而程序员无法干预时，抽象必然被绕过"**（Halide 的 algorithm/schedule 分离就是这条教训的制度化）；**而"变换序列"被多面体学派的"统一仿射求解"部分取代，说明启发式搜索终会让位给形式化优化问题**——但代价是只能处理仿射控制流。
>
> 对你当前的线索来说，最值得带走的是第七节那个分野：**数据流分析之所以做不了循环并行化，是因为它的下标集合（program point）把整个迭代空间压成一个点；而迭代空间是参数化无限的，于是"有限格 + Kleene 迭代"这套机器失效，必须换成仿射约束 + 整数规划。** Rice 的依赖分析与 Feautrier 的 array dataflow analysis，就是这条边界之外的另一种数学——同一个编译器里，序论的格管事实合并，数论的格管整点存在。