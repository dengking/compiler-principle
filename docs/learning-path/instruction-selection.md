# 现代编译器指令选择：从入门到精通的学习路径与资源指南

## 一、先把问题界定清楚

指令选择（instruction selection，IS）要解决的是：把抽象 IR 映射到目标 ISA 的机器指令，同时满足三件事——

1. **覆盖**：每个 IR 节点都必须被某个模式匹配到，并且各模式的覆盖范围不能重叠、不能有遗漏。
2. **合法**：寄存器类是否匹配、立即数是否编码得下、寻址模式是否合法、标志位/副作用/内存序是否被破坏。
3. **代价低**：指令数、延迟、寄存器压力、编码长度，其中任意一个都可以当目标。

一个关键事实决定了学习重心：**树覆盖可以多项式时间最优求解（动态规划 / BURS），DAG 覆盖是 NP-hard**（Bruno & Sethi）。所以真实的编译器都在“最优”和“能跑”之间做各种妥协——这就是这片领域大半的工程内容。理解这一点，你就不会把 IS 当成一个“照书上算法实现一遍”的题目。

**必须逐个搞懂的概念清单：**

- 树匹配 vs DAG 匹配
- pattern 语言与匹配器生成（表驱动、递归下降、术语重写）
- 代价模型及其来源
- Sethi–Ullman 寄存器需求与权重
- peephole / combine / split 与 IS 的边界
- chains & glue（LLVM SelectionDAG 特有）
- IS 与寄存器分配、指令调度的 phase ordering

有一点需要提前说明：**没有任何一门公开课是专门讲 instruction selection 的**。IS 在标准编译原理课里通常只占 1–2 讲，在研究生课里占 2–4 讲。正确的用法是从每门课里只摘取相关几讲，配合自己写实现，而不是从头看到尾。整个学习路径也应该按这个逻辑组织。

---

## 二、分阶段学习路径

### 阶段 0：前置（1–2 周）

- **编译器后端流水线全景**：IR → legalize → isel → RA → scheduling → emit。先有这张地图，后面每个环节才知道自己在哪。
- **至少熟一门 ISA 的汇编，建议 x86-64 与 RISC-V 各一**。x86-64 让你体会 CISC 的寻址模式和隐式操作数有多麻烦；RISC-V 让你看清三地址加立即数范围约束有多干净。同一个 IR 在两者上各做一次 IS，感受差异是最快的教学。
- **数据结构与理论准备**：树自动机、动态规划、图匹配的基本概念。

### 阶段 1：经典理论与算法（3–4 周）

按顺序读，每一步配一个小实现：

1. **贪心 maximal munch**（最简单的树覆盖）→ 自己写 200 行。
2. **Sethi–Ullman 权重 + 树 DP 最优覆盖** → 理解“代价可以是寄存器需求而不只是指令数”。
3. **BURS / bottom-up rewrite system**：把模式集编译成自底向上树自动机，`iburg`/`burg` 是范本。核心是“表驱动匹配器生成”这个思想。
4. **DAG 覆盖**：为什么 NP-hard，实际用什么启发式（拆树、共享子表达式导致的重复选择、near-optimal 的做法）。
5. **peephole 与 combine 的定位**：为什么很多“选择”其实是在更晚的 pass 里做的。

### 阶段 2：读真实实现（4–6 周，最值钱的一段）

由易到难：

- **CompCert 的 `backend/Selection.v`**：规模小、逻辑干净、还带 Coq 证明。能看到“一个可证明正确的选择器”长什么样，包括 `SelectOp`（除/取模、移位、比较的算子选择）。
- **QBE**：几千行的完整后端，IS 部分直白，适合整体把握。
- **Cranelift 的 ISLE**：用术语重写 DSL 描述 lowering，编译器把规则生成成 Rust 代码，带优先级。这是“模式描述语言”这个话题的现代答案，值得完整读一遍语法与规则组织。
- **LLVM SelectionDAG**：`CodeGenerator.html` 加上 `llc -debug-only=isel`。重点看 type/op legalization → DAG combine → 选择 → 调度这条链，以及 chains/glue 为什么存在。然后写几条 `.td` 的 `Pat<>`，加一个自定义指令跑通。
- **LLVM GlobalISel**：Legalizer / RegBankSelect / InstructionSelect 三段，理解它为什么要摆脱 SelectionDAG 的 per-basic-block 限制和 glue hack。
- **GCC**：`define_insn` + `match_operand` 谓词/约束 + `genrecog` 生成的匹配器 + `combine`/`peephole2`/`split`。GCC 表达力更强（任意 C 谓词），也更难推理。
- **V8 TurboFan 的 instruction-selector**：逐节点访问 + 规则表 + 与 `MachineOperatorReducer` 配合，是 JIT 场景下最实用的写法，代码非常好读。

### 阶段 3：前沿与困难问题（长期，按兴趣挑）

- **精确解**：把 IS 建模成 ILP / CP / SAT，对小函数求真正最优，用来评估启发式差多远。
- **SSA 上的 IS**：在 SSA 图上做覆盖，天然获得全局视野（Buchwald、Ebner 等人的工作）。
- **IS 与 RA/scheduling 的联合优化**：为什么分阶段会互相拖累，PBQP 与集成式方法做到什么程度。
- **代价模型的获取**：静态表是怎么来的、`llvm-exegesis` 这类测量工具、多目标代价（吞吐 vs 延迟 vs 代码大小）。
- **可验证 IS**：CompCert 路线，把选择器正确性变成定理。
- **ML 辅助**：学习代价模型或选择策略（这块文献噪声大，谨慎读）。

### 阶段 4：动手做完整项目

见第五节的里程碑，那才是把上面一切粘起来的地方。

---

## 三、资源清单

### 书

- **Gabriel Hjort Blindell, *Instruction Selection: Principles, Methods, and Applications*（Springer, 2016）**——这个题目唯一一本专著，树覆盖、DAG 覆盖、精确方法都有系统整理。核心读物。
- **Cooper & Torczon, *Engineering a Compiler***——“Instruction Selection”一章（第 11 章，版本略有差异）把树模式匹配和 peephole 讲得最清楚。
- **Muchnick, *Advanced Compiler Design and Implementation***（中译《高级编译器设计与实现》）——IS 专章 + 极完整的后端视角。
- **Appel, *Modern Compiler Implementation***（ML 版最佳）——maximal munch、动态规划、Sethi–Ullman 讲得最直观，配 MiniJava 后端。
- **龙书**——代码生成章入门够用，深度不如上面几本。
- **Comon 等, *Tree Automata Techniques and Applications***（免费在线）——BURS 背后的树自动机理论，需要时再翻。

### 经典论文

- Sethi & Ullman, “The Generation of Optimal Code for Arithmetic Expressions” (JACM 1970)
- Aho & Johnson, “Optimal Code Generation for Expression Trees” (JACM 1976)
- Hoffmann & O'Donnell, “Pattern Matching in Trees” (JACM 1982)
- Glanville & Graham / Cattell 的代码生成器自动推导工作（1978–1980）
- Fraser, Hanson, Proebsting, “Engineering Efficient Code Generators Using Tree Matching and Dynamic Programming”（iburg）及 BURG 系列
- Bruno & Sethi 的 DAG 覆盖复杂度结果
- Koes & Goldstein, “Near-Optimal Instruction Selection on DAGs” (CGO 2008)
- Ebner 等关于 SSA 图上广义 IS、IS 与调度结合的论文

### 一手文档与源码

- LLVM：`llvm.org/docs/CodeGenerator.html`、GlobalISel 文档、TableGen 的 `Pattern`/`Pat` 章节
- Cranelift/ISLE：`github.com/bytecodealliance/wasmtime` 下 `cranelift/codegen` 的 `isle/` 与各 ISA 的 `.isle` 文件
- CompCert：`compcert.org`，`backend/Selection.v`
- QBE、V8 的 `src/compiler/backend/`
- GCC 的 `machine.md` 风格目标描述——挑一个小的后端读（比如 msp430 或 avr），比 x86 好懂十倍

### 工具与实验手段

- **Godbolt / Compiler Explorer**：直接对比 clang/gcc 对同一段 C 生成的选择结果，改一行看变化。
- `llc -debug-only=isel`；GlobalISel 的 `-debug-only=legalizer,regbankselect,instruction-select`；`-print-after=*`。看每个 pass 后的 DAG/MIR。
- `llvm-exegesis`：测真实指令代价，检验你的静态代价表。
- **自己写一个 pattern → matcher 生成器**（哪怕只支持几十条规则），这一步的理解收益远超读论文。

---

## 四、公开课程

按“能给你多少 IS”排序。A 类值得认真跟，B 类只取几讲，C 类最贴近工业实现，D 类用作中文锚点。

### A 类：IS 内容真正有分量的课

**CMU 15-411 / 15-411 Compiler Design（Frank Pfenning）**
讲义公开（`cs.cmu.edu/~fp/courses/15411-*`）。后端几讲讲得相当实：树模式匹配、BURG/动态规划、x86-64 的寻址模式与合法化、与寄存器分配的衔接。课程项目是从零写 C0（C 的子集）到 x86-64 的完整编译器，所以它的 IS 讲义是“必须能落地”的那种，不是概念介绍。**如果只挑一门课认真跟，挑这门。**

**Cambridge Part III, Optimising Compilers（Timothy Jones）**
讲义和 slides 公开。IS 部分覆盖 tree pattern matching、BURS，以及 IS 与寄存器分配、指令调度的相互作用。理论味道比 CMU 重一点，适合补齐“为什么分阶段会互相拖累”这层理解。

**Saarland, Compiler Design / Code Generation（Sebastian Hack）**
讲义公开（`compile.cs.uni-saarland.de`）。代码生成讲义质量很高，IS、寄存器分配、指令调度（含 SSA 上的处理）都讲得系统且偏实现，图例和代价分析做得细。缺点是德语体系下的课，部分材料语言不统一，需要挑英文 slides。

**Edinburgh, Compiler Optimisation（Michael O'Boyle）**
slides 公开，年代偏早（PowerPC/Alpha 时代的例子），但 IS 与优化 pass 的交互、以及“代价模型从哪来”讲得清楚。适合当第二遍的补充读物。

### B 类：通用编译课，只取代码生成那几讲

**MIT OCW 6.035 Computer Language Engineering**
完全公开，含讲义、作业、项目（Decaf → x86）。代码生成与 IS 部分偏基础（基本块、DAG、简单模式匹配），价值主要在于有一份完整可跑的 x86 后端作业可以照着做。

**UIUC CS426 Compiler Construction（Vikram Adve）**
讲义公开，IS 讲得中规中矩，legalization 与 ISA 约束讲得比较实在。

**Stanford CS143 / Coursera “Compilers”（Alex Aiken）**
最好的入门课之一，但 **IS 内容很浅**——止步于栈式代码生成和基础寄存器分配。想学 IS，这门课的价值只在于把前端和 IR 打牢。

**Berkeley CS164 Programming Languages and Compilers**
部分年份讲义公开，含 instruction selection 一讲，走的是“IR 到 x86”的具体路径，可以当补充视角。

**Cornell CS6120 Advanced Compilers（Adrian Sampson）**
不针对 IS，但它的“lessons”系列公开、且是边讲边写代码的形式。与 IS 相关的价值在 SSA、数据流、IR 设计的思维方式——你在阶段 3 做 SSA 图上的覆盖时会反复用到。

**NPTEL, Compiler Design（Y.N. Srikant, IISc）**
印度 NPTEL 平台的公开视频课。Srikant 是 *The Compiler Design Handbook* 的主编，其中代码生成/指令选择章节很扎实，他在 IS 与 retargetable code generation 上比一般 MOOC 深。视频节奏慢，建议 1.5–2 倍速并只挑代码生成段。

### C 类：会议演讲与实操 tutorial

这类不是课程，但对“现代做法”的收益最大：

- **LLVM Developers' Meeting 的 GlobalISel 系列演讲**（Amara Emerson、Volkan Keles 等）：三段式设计、为什么弃用 SelectionDAG 的 glue 机制。配合 `llvm.org/docs/GlobalISel` 一起看。
- **TableGen 相关演讲**（“TableGen deep dive”类）：`.td` 里 `Pat`、`ComplexPattern`、`Predicate` 的语义，是理解“模式描述语言如何编译成匹配器”的最短路径。
- **“Writing an LLVM Backend” tutorial**（文档 + Dev Meeting 录像）：跟着加一条指令、跑通 `llc`，比读十篇论文有用。
- **Cranelift / ISLE 的相关 talk**（Bytecode Alliance 场合）：术语重写式 lowering 与 BURS 的异同，是目前最现代的一种表达方式。

### D 类：中文资源

- **中科大 张昱《编译原理》**（B 站有完整录像）：后端部分（目标代码生成、基本块与 DAG、寄存器分配）比多数国内课程细，术语对照清晰，适合作为英文讲义的中文锚点。
- **哈工大 陈鄞《编译原理》**（中国大学 MOOC）：前端极好、极适合入门，但后端只有“目标代码生成”一章的入门量，不足以支撑 IS 学习，别指望它。
- **清华 王生原《编译原理》**（学堂在线）：体系完整，代码生成部分中规中矩。
- 中科院系统的高级编译技术类课程视频零散、质量参差，不如直接读 LLVM 文档和源码。

---

## 五、常见误区

- **把 IS 当成孤立的 pass**。它和 legalization、combine、RA、scheduling 纠缠在一起，很多“选择结果不好”的根因在上下游。
- **只学树覆盖**。树 DP 是最优的，但真实 IR 是 DAG，重复计算的取舍才是工程难点。
- **忽视代价模型**。算法一样，代价表错了结果全错；这是真实编译器里最需要测量和调参的地方。
- **只读不写匹配器**。BURS 的“把规则集编译成自动机”这个想法，不亲手实现一遍很难真正内化。
- **试图找一门“指令选择课”从头看到尾**。不存在这样的课，只会浪费时间。

---

## 六、里程碑项目

建议按序完成，每一步都有明确的产出物：

1. **玩具 ISA + maximal munch**：定义 15 条左右指令，对三地址 IR 做贪心覆盖。
2. **iburg 风格 DP 选择器**：写规则 DSL，生成匹配表，实现最优树覆盖 + 寄存器需求代价。
3. **DAG 版本对照实验**：同一批函数，比较“拆树后各自最优”与“共享节点合并”的指令数差异，量化贪心的损失。
4. **给 LLVM 加一条指令**：在 RISC-V 或自定义 target 上定义指令、写 TableGen pattern、跑通 `llc`，再用 `-debug-only=isel` 看清匹配过程。
5. **用 Cranelift ISLE 写一组 lowering 规则**：体会规则优先级和 term rewriting 与 BURS 的异同。
6. **精确解对比**：对 5–10 个小函数用 ILP/CP 求最优，和你的启发式比，画出差距分布。

---

## 七、怎么把它们组合起来

一条具体的搭配线：

1. 用 **CS143 或陈鄞** 快速补齐 IR 与前端（已有基础就跳过）。
2. **CMU 15-411** 的后端几讲 + 项目，作为 IS 主干。
3. **Cambridge / Saarland** 的对应讲义，补理论（BURS、代价、与 RA/scheduling 的耦合）。
4. **LLVM Dev Meeting 的 GlobalISel + TableGen 演讲**，把课堂模型对上工业实现。
5. 回头读 **Blindell 那本书**，你会发现课堂和源码里那些“约定俗成”都有出处。

时间分配上，第 2 步约占一半，第 4 步约三成，其余是补充。课的视频不必全看——每门课你真正需要的往往就 3–5 讲。

**总体时间估计**（业余投入）：阶段 0–1 约两个月，阶段 2 约两个月，里程碑 1–3 单独再算四到六周，阶段 3 按兴趣长期跟进。

做到里程碑 4 并读懂 SelectionDAG 与 GlobalISel 的差异，基本就可以说在这块能独立干活了。