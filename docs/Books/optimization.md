# 编译器后端优化：权威书单

## 零、先说一件要紧的事

"后端优化"实际上是**五个耦合不深、文献分布极不均衡**的子领域：

| 子领域 | 有好书吗 |
|---|---|
| 数据流分析 / 静态分析理论 | ✅ 书很多很好 |
| SSA 与标量优化（GVN/PRE/SCCP） | ✅ 有专门的权威书 |
| 循环变换 / 依赖分析 | ✅ 有经典（但偏 Fortran 时代） |
| **寄存器分配 / 指令调度 / 指令选择** | ⚠️ **书都落后 15 年以上，必须读论文** |
| **多面体编译 / 自动向量化 / MLIR** | ❌ **没有权威教材** |

所以下面不只给书，也标明哪里必须转向论文和源码。

---

## 一、核心四本

| 书 | 评价 |
|---|---|
| **Cooper & Torczon, *Engineering a Compiler*** (3rd ed., 2022) | ⭐ **后端部分优于龙书的首选**。指令选择（树覆盖 / peephole）、指令调度（list scheduling）、寄存器分配（图着色全链条）讲得清楚且现代。Keith Cooper 本人就是 Briggs-Chaitin 着色、SSA 支配边界快速算法的作者。**如果只读一本，读这本。** |
| **Muchnick, *Advanced Compiler Design and Implementation*** (1997) | ⭐ **"鲸鱼书"**。后端优化的百科全书，覆盖度至今无人超越（PRE、强度削弱、过程间分析、别名分析、代码布局……）。缺点诚实讲：1997 年，SSA 处理单薄、无多面体、伪代码风格老派。**定位是"查手册"，不是通读。** 中译《高级编译器设计与实现》质量可以。 |
| **Rastello & Bouchez Tichadou (eds.), *SSA-based Compiler Design*** (Springer, 2022) | ⭐ **现代后端的核心就是 SSA，这本不可替代**。章节作者是该领域本人：Zadeck、Cytron、Sebastian Hack、Bouchez、Rastello、Sebastian Pop。含 SSA 构造/销毁、SSA 上的寄存器分配、谓词化、Hashed SSA、SSI。**早期草稿 PDF（ssabook）长期免费流传，可先读草稿。** |
| **Appel, *Modern Compiler Implementation in ML*** (1998) | "虎书"。后端讲得**最干净**：活跃分析、图着色、maximal munch / 动态规划指令选择。ML 版是正统，Java/C 版是移植（代码风格受损）。**适合动手实现一遍。** |

> **搭配建议**：Cooper&Torczon 打底 → SSA Book 补现代 → Muchnick 当词典。

---

## 二、专题权威

### 循环变换 / 依赖分析

| 书 | 说明 |
|---|---|
| **Allen & Kennedy, *Optimizing Compilers for Modern Architectures*** (2001) | 该领域圣经。依赖分析、方向/距离向量、unimodular 变换、fusion/fission/interchange/tiling。Ken Kennedy 是 Rice 并行编译学派的奠基人。**偏向 Fortran/向量机时代，但依赖理论是永恒的。** |
| **Wolfe, *High Performance Compilers for Parallel Computing*** (1995) | 与上书互补，更偏实践直觉。Michael Wolfe 后来做了 PGI 编译器。 |

### 静态分析理论（接续你当前在读的龙书第 9 章）

| 书 | 说明 |
|---|---|
| **Khedker, Sanyal & Karkare, *Data Flow Analysis: Theory and Practice*** (2009) | ⭐ **精确对应你现在的兴趣点**。MFP/MOP 的严格处理、复杂度分析、双向数据流（bidirectional，龙书几乎没讲）、格的高度与收敛趟数。专书级深度。 |
| **Rival & Yi, *Introduction to Static Analysis: An Abstract Interpretation Perspective*** (MIT Press, 2020) | ⭐ **抽象解释的现代入门首选**。Xavier Rival 是 Cousot 的学生。比 NNH 可读得多，格论/Galois 连接/widening 讲得清楚。 |
| **Nielson, Nielson & Hankin, *Principles of Program Analysis*** (1999) | "NNH"。覆盖数据流 + 抽象解释 + 类型系统 + 约束分析，严格但**难且勘误多**。定位是参考，不是入门。 |
| **Wilhelm, Seidl & Hack, *Compiler Design: Analysis and Transformation*** (Springer, 2013) | 德国学派，简洁严谨。Sebastian Hack 就是 SSA 寄存器分配那篇突破性论文的作者。篇幅小、信息密度高。 |

### 目标机器与 ILP

| 书 | 说明 |
|---|---|
| **Hennessy & Patterson, *Computer Architecture: A Quantitative Approach*** (6th ed., 2017) | 后端优化的前提是懂机器。流水线、cache、乱序执行、向量/SIMD。 |
| **Fisher, Faraboschi & Young, *Embedded Computing: A VLIW Approach*** (2004) | Josh Fisher 是 trace scheduling 发明人。VLIW/ILP 调度、软件流水的权威处理。 |
| **Agner Fog, *Optimization manuals*** (免费在线，持续更新) | 微架构级真实延迟/吞吐表。**这是书里永远给不了的东西。** |

### 相邻领域

| 书 | 说明 |
|---|---|
| **Jones, Hosking & Moss, *The Garbage Collection Handbook*** (2nd ed., 2023) | GC 领域唯一权威，且后端要为 GC 生成 stack map / write barrier。 |
| **Levine, *Linkers and Loaders*** (1999) | 后端下游。老但基础不变；LTO/重定位要懂。 |
| **Jones, Gomard & Sestoft, *Partial Evaluation and Automatic Program Generation*** (1993) | 免费在线。JIT / 特化 / Futamura 投影的理论源头。 |

---

## 三、⚠️ 书覆盖不到的：必读论文

**寄存器分配**（书基本停在 Briggs-Chaitin）
- Chaitin, "Register Allocation & Spilling via Graph Coloring" (1982)
- Briggs, Cooper & Torczon, "Improvements to Graph Coloring Register Allocation" (TOPLAS 1994) — 乐观着色
- Poletto & Sarkar, "Linear Scan Register Allocation" (TOPLAS 1999) — JIT 的事实标准
- Wimmer & Franz, "Linear Scan Register Allocation on SSA Form" (CGO 2010) — HotSpot/V8 实际用的
- **Hack, *Register Allocation for Programs in SSA Form*** (PhD, 2007) — ⭐ SSA 形式下干涉图是 chordal，着色变多项式时间。**范式转移级别的工作。**

**SSA 与标量优化**
- Cytron et al., "Efficiently Computing SSA Form and the Control Dependence Graph" (TOPLAS 1991) — 支配边界
- Cooper, Harvey & Kennedy, "A Simple, Fast Dominance Algorithm" (2001) — 实践中比 Lengauer–Tarjan 更常用
- Wegman & Zadeck, "Constant Propagation with Conditional Branches" (TOPLAS 1991) — **SCCP**，LLVM 里的 `SCCP` pass
- Knoop, Rüthing & Steffen, "Lazy Code Motion" (PLDI 1992) — PRE 的正确做法
- Click & Cooper, "Combining Analyses, Combining Optimizations" (TOPLAS 1995) — ⭐ 为什么分开跑 pass 会丢精度

**指令选择与调度**
- Aho & Johnson, "Optimal Code Generation for Expression Trees" (1976)
- Fraser, Hanson & Proebsting, "Engineering a Simple, Efficient Code Generator Generator" (iburg, 1992)
- Ertl, "Optimal Code Selection in DAGs" (POPL 1999)
- Lam, "Software Pipelining" (PLDI 1988) / Rau, "Iterative Modulo Scheduling" (1994)

**过程间分析**（接你上一轮的 "stack frames below the top"）
- Reps, Horwitz & Sagiv, "Precise Interprocedural Dataflow Analysis via Graph Reachability" (POPL 1995) — ⭐ **IFDS**，正是把"call/return 必须配对"形式化为 CFL-reachability
- Sagiv, Reps & Horwitz, "Precise Interprocedural Dataflow Analysis with Applications to Constant Propagation" (1996) — IDE

**理论源头**
- Kildall (POPL 1973)、Kam & Ullman (1976/1977) — MFP、分配性、收敛趟数
- Cousot & Cousot (POPL 1977) — 抽象解释

**现代实践**（只有源码和文档）
- LLVM：官方文档 + `lib/Transforms`、`lib/CodeGen` 源码 + LLVM Dev Meeting 录像。**没有权威书**（Lopes & Auler 2014 已严重过时；Min-Yih Hsu 的 *LLVM Techniques, Tips, and Best Practices* 2021 较新但是 cookbook）。
- MLIR / 多面体：只有论文（Verdoolaege 的 isl、Grosser 的 Polly、Bondhugula 的 Pluto）+ 官方文档。

---

## 四、不建议作为主线的

| 书 | 理由 |
|---|---|
| 龙书第 2 版第 10–11 章 | 第 9 章（数据流）扎实，**第 10 章 ILP 偏弱、第 11 章（Lam 的多面体工作）深但孤立**，寄存器分配/指令选择的讲法明显落后于 Cooper&Torczon |
| Grune et al., *Modern Compiler Design* | 覆盖面广但每处都浅 |
| 各类"自制编译器/手写编译器"书 | 前端练手可以，后端优化一律跳过 |

---

## 五、给你的具体路径

鉴于你已经在龙书第 9 章、且对格论/不动点有超出教材的理解：

1. **横向补现代实现**：Cooper & Torczon 第 11–13 章（指令选择、调度、寄存器分配）—— 这是龙书最弱、你最缺的部分。
2. **纵向补理论深度**：Khedker 的 *Data Flow Analysis*（你现在的兴趣点正中靶心）+ Rival & Yi（抽象解释）。
3. **转向 SSA**：SSA Book 前 5 章 + Cytron 1991 + Cooper-Harvey-Kennedy 2001。**现代后端的一切都建立在 SSA 上，这是绕不过去的分水岭。**
4. **动手**：把你写的通用 `lfp` 求解器接到真实 IR 上 —— 建议用 LLVM 的 `opt` 插件（C++）或 Python 的 `llvmlite`，实现一遍 SCCP。SCCP 的妙处在于它**同时**做常量传播和不可达分支消除，正是 Click & Cooper 那篇"合并分析"的最小例证，也会让你亲眼看到"分开跑两个 pass 丢掉的精度"。
5. **按需查** Muchnick。