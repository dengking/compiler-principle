# 编译器中端：原理、架构与实践

> **标注说明**：术语在正文中**首次出现**时，以"中文术语（English Term）"的形式附上英文；有通用缩写的写作"中文（English, 缩写）"。之后再出现时一般只用中文或缩写。代码块中的内容不做标注。

## 导读

编译器（Compiler）通常分为**前端（Front End）**、**中端（Middle End）** 和**后端（Back End）** 三部分。前端读懂源程序，后端生成机器码（Machine Code），中端则在两者之间把程序**变好**：更快、更小，同时语义保持不变。

**中端**是编译器中理论最丰富、工程最复杂、对性能影响最大的部分。现代编译器能把高级语言写的程序优化到接近甚至超过手写汇编（Assembly）的水平，主要依靠**中端**。

本文按以下顺序展开：

```
第一部分  中端是什么          定位、目标、边界
第二部分  中端的基石：IR       程序在中端"长什么样"
第三部分  理论基础            为什么分析一定正确、一定终止
第四部分  分析体系            中端如何"理解"程序
第五部分  变换体系            中端如何"改写"程序
第六部分  分析与变换的协作     各技术之间的关系
第七部分  工程组织            Pass 管理器与优化流水线
第八部分  跨越边界            LTO 与 PGO
第九部分  完整案例            一个函数的优化之旅
第十部分  正确性              未定义行为与编译器验证
第十一部分 工业实现            主流编译器的中端设计
第十二部分 发展趋势与学习路线
```

---

# 第一部分　中端是什么

## 1.1 编译器的三段式结构（Three-Phase Compiler Design）

```
源代码 ──→ [ 前端 ] ──→ IR ──→ [ 中端 ] ──→ 优化后的 IR ──→ [ 后端 ] ──→ 机器码
          词法/语法分析         分析 + 变换                    指令选择
          语义检查                                            寄存器分配
          生成 IR                                             指令调度
```

前端完成词法分析（Lexical Analysis）、语法分析（Parsing / Syntax Analysis）和语义检查（Semantic Analysis），生成中间表示（Intermediate Representation, IR）；后端负责指令选择（Instruction Selection）、寄存器分配（Register Allocation）和指令调度（Instruction Scheduling）。

|          | 前端                                  | 中端                           | 后端        |
| -------- | ----------------------------------- | ---------------------------- | --------- |
| 处理对象     | 源码、抽象语法树（Abstract Syntax Tree, AST） | 目标无关（Target-Independent）的 IR | 机器指令      |
| 主要目标     | 正确理解程序，发现错误                         | 目标无关的优化                      | 生成高效的目标代码 |
| 是否依赖源语言  | 是                                   | 基本否                          | 否         |
| 是否依赖目标机器 | 否                                   | 基本否（需要查询**代价模型**）            | 是         |

## 1.2 为什么要有独立的中端

**第一个原因是复用。** 假设有 M 种语言、N 种目标机器（Target Machine）：

```
没有中端：每种语言 × 每种机器各写一个编译器 → M × N 个
有中端：  M 个前端 + 1 个中端 + N 个后端      → M + N 个
```

LLVM 的同一个中端同时服务于 C/C++、Rust、Swift、Julia、Zig 等语言，以及 x86、ARM、RISC-V、GPU 等目标。这是 LLVM 成功的关键。

**第二个原因是抽象层次（Abstraction Level）合适。** 源代码层次太高，语法糖（Syntactic Sugar）、作用域（Scope）、重载（Overloading）等细节会干扰分析；机器码层次太低，寄存器数量、指令格式等约束会束缚变换。中端 IR 两边的包袱都不背，适合做通用的分析和优化。

## 1.3 中端的根本任务

一句话概括：

> **在保持语义不变（Semantics Preservation）的前提下，把程序变换成执行更高效的等价形式。**

这句话里有三个关键词，贯穿全文：

| 关键词      | 对应的问题     | 由谁回答                                |
| -------- | --------- | ----------------------------------- |
| **保持语义** | 这个变换安全吗？  | 分析（Analysis）：数据流、别名、依赖……            |
| **更高效**  | 这个变换值得做吗？ | 代价模型（Cost Model）、剖析数据（Profile Data） |
| **变换**   | 具体怎么改？    | 变换 Pass（Transform Pass）             |

## 1.4 边界其实是模糊的

三段式是理想模型，实际编译器中的边界并不清晰：

- **前端也做数据流分析（Data Flow Analysis）**：Java 的"明确赋值（Definite Assignment）"检查、Clang 的 `-Wuninitialized`、Rust 的借用检查（Borrow Checking），本质上都是数据流分析，只是目的是**诊断（Diagnostics）** 而不是优化。
- **后端也做数据流分析**：寄存器分配依赖活跃变量分析，指令调度依赖数据依赖图（Data Dependence Graph）。
- **中端会查询目标信息**：向量化需要知道向量寄存器（Vector Register）有多宽，内联需要估计代码大小。
- **存在多层中端**：Rust 的 MIR、Swift 的 SIL 位于前端和 LLVM IR 之间，MLIR 更是把"中端"变成了一个由多层 IR 组成的**谱系**。

本文讨论的"中端"，指**在目标无关 IR 上进行的分析与优化**，并在合适的地方指出它与前后端的联系。

---

# 第二部分　中端的基石：中间表示（IR）

所有分析和变换都在 IR 上进行，IR 的设计决定了中端能做什么、做得多容易。

## 2.1 从三地址码到控制流图

**三地址码（Three-Address Code, TAC）**：每条指令最多一个运算、三个操作数（Operand）。

```c
// 源代码
x = a + b * c;

// 三地址码
t1 = b * c
x  = a + t1
```

**基本块（Basic Block）**：一段只能从开头进入、只能从结尾离开的指令序列，内部没有跳转。

**控制流图（Control Flow Graph, CFG）**：以基本块为节点、以跳转关系为边的有向图（Directed Graph）。

```c
int f(int n) {
    int s = 0;
    for (int i = 0; i < n; i++)
        s += i;
    return s;
}
```

```
        ┌─────────────┐
        │ B1: s = 0   │
        │     i = 0   │
        └──────┬──────┘
               ▼
        ┌─────────────┐
   ┌───→│ B2: i < n ? │────┐
   │    └──────┬──────┘    │ 否
   │           ▼ 是         ▼
   │    ┌─────────────┐  ┌──────────────┐
   │    │ B3: s = s+i │  │ B4: return s │
   │    │     i = i+1 │  └──────────────┘
   │    └──────┬──────┘
   └───────────┘   （B3→B2 是回边，构成循环）
```

图中 B3→B2 这样的边称为回边（Back Edge）。一个块的上游块叫前驱（Predecessor），下游块叫后继（Successor）。CFG 是中端最基本的数据结构，几乎所有分析都在它上面进行。

## 2.2 静态单赋值形式（Static Single Assignment Form, SSA）

SSA 是现代中端最重要的表示方法。它的规则很简单：

> **每个变量只被赋值一次。**

如果原程序中一个变量被多次赋值，就给每次赋值一个新名字。在控制流汇合（Merge / Join Point）的地方，用 **φ 函数（Phi Function / Phi Node）** 选择来自不同路径的值：

```c
// 原始代码              // SSA 形式
x = 1;                   x1 = 1;
if (c)                   if (c)
    x = 2;                   x2 = 2;
y = x;                   x3 = φ(x1, x2);   // 从哪条路径来，就取哪个值
                         y1 = x3;
```

上面循环的例子转成 SSA 后：

```
B1:  s1 = 0
     i1 = 0
B2:  i2 = φ(i1, i3)      // 第一次进入取 i1，之后从 B3 回来取 i3
     s2 = φ(s1, s3)
     if i2 < n goto B3 else B4
B3:  s3 = s2 + i2
     i3 = i2 + 1
     goto B2
B4:  return s2
```

**SSA 的价值：**

| 优点 | 说明 |
|---|---|
| 定义—使用关系（Def-Use Chain）一目了然 | 每个名字只有一个定义点，看到 `s3` 就知道它在哪里被定义 |
| 分析可以"稀疏（Sparse）"进行 | 信息沿定义—使用边直接传播，不必经过无关的基本块 |
| 很多优化变得简单 | 名字相同就是值相同，常量传播、值编号、死代码消除都更容易 |
| 天然区分同一变量的不同"版本" | 消除了重新赋值带来的歧义 |

SSA 需要在离开中端时被消除，即退出 SSA（SSA Destruction / Out-of-SSA Translation）：把 φ 转换为拷贝指令（Copy Instruction），这项工作通常在后端完成。

## 2.3 现代 IR 的特征

以 LLVM IR 为例：

```llvm
define i32 @f(ptr %p, i32 %x) {
entry:
  %a = add nsw i32 %x, 1        ; nsw：有符号溢出时结果为 poison
  store i32 %a, ptr %p
  ret i32 %a
}
```

| 特征 | 说明 |
|---|---|
| SSA 形式 | `%a` 只被定义一次 |
| 类型化（Typed IR） | 每个值都有类型（`i32`、`ptr`） |
| 显式控制流 | 基本块以终结指令（Terminator Instruction）如 `br`、`switch`、`ret` 结尾 |
| 语义精确 | 对溢出（Overflow）、未定义行为、内存访问都有严格定义 |
| 可序列化（Serializable） | 有文本和二进制（位码，Bitcode）两种格式，支持保存、检查和 LTO |

**语义精确化是近年 IR 设计的重点。** LLVM 引入了 **毒值（Poison Value）**（违反假设时产生的特殊值）和 **`freeze` 指令**（把 poison 固定为某个任意但确定的值，LLVM 10 引入）；LLVM 15 起默认使用**不透明指针（Opaque Pointers）**，指针统一为 `ptr`，不再携带所指类型，简化了 IR。这些细节看似琐碎，却直接决定了哪些优化合法（详见第十部分）。

## 2.4 其他形式的 IR

| IR 形式 | 代表 | 特点 |
|---|---|---|
| CFG + SSA | LLVM IR、GCC GIMPLE、Cranelift CLIF（Cranelift IR Format） | 当前主流 |
| 节点之海（Sea of Nodes） | HotSpot C2、早期 V8 TurboFan | 值和控制都表示为图中的节点，指令没有固定位置，便于代码移动（Code Motion）；但实现复杂，V8 已转向基于 CFG 的 Turboshaft |
| 多层级 IR（Multi-Level IR） | MLIR | 不是一种 IR，而是构建 IR 的框架，用不同"方言（Dialect）"表示不同抽象层次 |
| 语言专属中层 IR | Rust MIR（Mid-level IR）、Swift SIL（Swift Intermediate Language） | 保留所有权（Ownership）、引用计数（Reference Counting）、泛型（Generics）等高层语义，供语言相关的分析使用 |

---

# 第三部分　理论基础：格、不动点与抽象解释

中端的分析必须同时满足两个要求：**结果正确**（基于它做的优化不会出错）和**一定终止（Termination）**（不能无限运行）。这两点由一套统一的数学理论保证。本部分尽量用直观的方式介绍。

## 3.1 问题：程序路径无穷无尽

在有循环的程序中，执行路径（Execution Path）可能有无穷多条：

```c
x = 0;
while (cond())
    x = x + 1;
// 这里 x 可能是 0, 1, 2, 3, ……
```

不可能逐条路径去检查。分析的核心思想是：**放弃精确，改用"近似（Approximation）"描述所有可能情况，并保证这种近似是安全的。**

比如可以说"这里的 x ≥ 0"，或者"这里的 x 不是常量"。这些描述不精确，但对所有执行路径都成立。

## 3.2 格（Lattice）：描述"信息"的结构

分析中的信息需要满足一种偏序（Partial Order）结构，称为**格**。以**常量传播**为例：

```
              ⊤  （未知，还没有看到任何赋值）
         ╱   ╱  │  ╲   ╲
      … -1   0   1   2  …   （确定为某个常量）
         ╲   ╲  │  ╱   ╱
              ⊥  （不是常量，可能有多个值）
```

其中 ⊤ 称为顶元素（Top），⊥ 称为底元素（Bottom）。两条路径汇合时，用**交汇运算（Meet Operator）** 合并信息：

| 路径 1 | 路径 2 | 合并结果 |
|---|---|---|
| 3 | 3 | 3 |
| 3 | 5 | ⊥（不是常量） |
| ⊤ | 3 | 3 |
| ⊥ | 任意 | ⊥ |

信息在合并时只会"往下走"（变得更不确定），不会往上走。

## 3.3 数据流分析框架（Data Flow Analysis Framework）

经典的数据流分析框架（Kildall 1973，Kam & Ullman 1977 发展为单调框架（Monotone Framework））由以下几个要素组成：

| 要素 | 含义 |
|---|---|
| **方向（Direction）** | 前向（Forward，沿控制流传播）或后向（Backward，逆控制流传播） |
| **值域（Domain）** | 一个格，描述要计算的信息 |
| **交汇运算** | 汇合点如何合并信息（∪ 或 ∩ 等） |
| **传递函数（Transfer Function）** | 一个基本块如何改变信息 |
| **边界条件（Boundary Condition）** | 入口（Entry）或出口（Exit）的初始值 |

前向分析的方程：

```
IN[B]  = ⋀ OUT[P]      对 B 的所有前驱 P 做交汇
OUT[B] = f_B(IN[B])    经过 B 的传递函数
```

求解方法是**迭代（Iterative Algorithm）**：先给所有块赋初值，然后反复更新，直到所有值不再变化，这个状态称为**不动点（Fixed Point）**。实际实现常用工作表算法（Worklist Algorithm），只重新处理信息发生变化的块。

## 3.4 四种经典数据流分析

| 分析                                             | 回答的问题              | 方向  | 交汇  | 传递函数                 | 主要用途                       |
| ---------------------------------------------- | ------------------ | --- | --- | -------------------- | -------------------------- |
| **到达定值（Reaching Definitions）**                 | 哪些赋值能到达这里？         | 前向  | ∪   | `gen ∪ (in − kill)`  | 常量传播、未初始化检查                |
| **活跃变量（Live Variables / Liveness）**            | 哪些变量以后还会被用到？       | 后向  | ∪   | `use ∪ (out − def)`  | 死代码消除、寄存器分配                |
| **可用表达式（Available Expressions）**               | 哪些表达式已经算过且没失效？     | 前向  | ∩   | `gen ∪ (in − kill)`  | 公共子表达式消除                   |
| **预期表达式（Anticipated / Very Busy Expressions）** | 哪些表达式在后续每条路径上都会计算？ | 后向  | ∩   | `use ∪ (out − kill)` | 部分冗余消除、代码提升（Code Hoisting） |

表中 gen 为生成集（Gen Set），kill 为杀死集（Kill Set）。

**交汇用 ∪ 还是 ∩，取决于问题的性质：**

- **"可能"问题（May Analysis）用 ∪**：只要有一条路径满足就算。例如"这个变量**可能**还会被使用"，只要一条路径用到它，就不能删。
- **"必然"问题（Must Analysis）用 ∩**：所有路径都满足才算。例如"这个表达式**一定**已经算过"，必须每条路径都算过，才能复用。

两者背后是同一个原则——**保守近似（Conservative Approximation）**：**宁可错过优化，不能做错优化。**

## 3.5 为什么一定终止、一定正确

- **终止性**：如果格的高度（Height）有限，传递函数是**单调（Monotone）** 的（输入信息越多，输出信息不会越少），那么每个值只能沿格下降有限次，迭代必然停止。
- **正确性**：数据流分析求得的结果是所有路径信息的安全近似。在传递函数满足**分配律（Distributivity）** 时，迭代结果（最大不动点解，Maximal Fixed Point, MFP）等于"所有路径合并"的精确解（全路径交汇解，Meet Over All Paths, MOP）；不满足时（如常量传播），结果更保守，但仍然安全。

**迭代顺序影响效率**：前向分析按逆后序（Reverse Postorder, RPO）访问基本块，后向分析按逆 CFG 的逆后序访问，通常几轮就能收敛（Converge）。

## 3.6 抽象解释（Abstract Interpretation）：统一的理论

Cousot 夫妇在 1977 年提出**抽象解释**，把上述思想推广为一般理论：

> 用"抽象值（Abstract Value）"代替真实值，在抽象域（Abstract Domain）上模拟执行程序。

数据流分析是抽象解释的一种特例。不同的抽象域在精度（Precision）与开销之间做不同取舍：

| 抽象域 | 能表达的信息 | 示例 |
|---|---|---|
| 符号域（Sign Domain） | 正、负、零 | x > 0 |
| 常量域（Constant Domain） | 是否为常量 | x = 5 |
| 区间域（Interval Domain） | 取值范围 | x ∈ [0, 100] |
| 八边形域（Octagon Domain） | ±x ± y ≤ c | x − y ≤ 5 |
| 多面体域（Polyhedra Domain） | 任意线性不等式组 | 精度最高，开销最大 |

**区间域的高度是无限的**（区间可以无限扩大），迭代可能不终止。抽象解释用**加宽（Widening）** 强制收敛（比如发现上界一直在增长，就直接设为 +∞），再用**收窄（Narrowing）** 找回部分精度。

## 3.7 一个统一的视角

几乎所有中端分析都可以写成"格上的不动点求解"：

| 分析 | 格 | 不动点的含义 |
|---|---|---|
| 到达定值 | 定义集合的幂集（Power Set） | 所有可能到达的定义 |
| 常量传播 | 常量格 | 每个变量的常量性 |
| 范围分析 | 区间格 | 每个变量的取值范围 |
| 指针分析（Andersen） | 指向集合的幂集 | 满足所有约束的最小解 |
| 支配关系 | 节点集合的幂集 | 每个节点的支配者集合 |

甚至支配关系也能写成数据流方程：

```
Dom(entry) = {entry}
Dom(B)     = {B} ∪ ⋂ Dom(P)    （P 为 B 的所有前驱）
```

**这就是中端各种分析的"公共语言"**：掌握了格和不动点，就掌握了理解所有分析的钥匙。

---

# 第四部分　分析体系：中端如何"理解"程序

分析本身不改变程序，只是收集信息，供变换使用。按回答的问题，可以分成以下几类。

## 4.1 控制流分析（Control Flow Analysis）：程序可能怎么执行？

控制流分析是所有其他分析的前提。

### 支配关系（Dominance）

> 如果从入口到 B 的**每条路径**都经过 A，就称 **A 支配（Dominate）B**。

- **支配树（Dominator Tree）**：把每个节点挂在它最近的支配者——直接支配者（Immediate Dominator, idom）——下面，形成一棵树。
- **支配边界（Dominance Frontier, DF）**：B 的支配边界是那些"B 支配它的某个前驱，但不严格支配（Strictly Dominate）它本身"的节点，直观上就是"B 的控制范围结束、与其他路径汇合"的地方。
- **后支配（Post-Dominance）**：在逆 CFG 上的支配关系，用于计算控制依赖。

计算方法有经典的 Lengauer-Tarjan 算法，以及实现简单、实践中同样高效的 Cooper-Harvey-Kennedy 迭代算法。

### 循环识别（Loop Detection）

- **回边**：从 B 指向 A 的边，且 A 支配 B。
- **自然循环（Natural Loop）**：由回边确定，A 是循环头（Loop Header）。
- **循环嵌套树（Loop Nest Tree）**：描述循环的嵌套层次。
- **可归约性（Reducibility）**：所有循环都只有一个入口的 CFG 称为可归约的（Reducible）。结构化语言写出的程序一般都是可归约的，很多算法依赖这一点。

### 用途

构造 SSA、循环优化、代码移动的合法性判断、控制依赖计算、确定分析的迭代顺序。

## 4.2 数据流分析：每个点上数据处于什么状态？

见第三部分。在现代中端中，经典的"稠密（Dense）"数据流分析很多已被**基于 SSA 的稀疏分析（SSA-based Sparse Analysis）** 取代，但其框架思想仍然是基础。

## 4.3 基于 SSA 的稀疏分析

传统数据流分析需要在每个基本块入口和出口为**所有变量**维护状态，开销大。在 SSA 上，信息可以**沿定义—使用边直接传播**：

```
稠密分析：信息流经每一个基本块，即使这个块与变量无关
稀疏分析：信息只沿"定义 → 使用"的边流动
```

代表性算法：

- **稀疏条件常量传播（Sparse Conditional Constant Propagation, SCCP）**：同时推断常量值和分支可达性（Reachability）（详见 5.2）。
- **全局值编号（Global Value Numbering, GVN）**：判断两个表达式是否计算同一个值。
- **范围分析（Range Analysis）**：在 SSA 上传播区间。为了利用分支条件，常扩展为扩展 SSA（Extended SSA, e-SSA），在分支后插入 π 节点（Pi Node）：

```c
if (i < 10) {
    i2 = π(i1);     // 在此分支内，i2 ≤ 9
    a[i2] = 0;      // 结合 i2 ≥ 0 和数组长度，可能消除越界检查
}
```

这类信息可用于边界检查消除（Bounds Check Elimination）。

## 4.4 别名分析（Alias Analysis, AA）：两个指针是否指向同一块内存？

```c
int f(int *p, int *q) {
    *p = 1;
    *q = 2;
    return *p;      // 一定返回 1 吗？取决于 p 和 q 是否指向同一处
}
```

别名分析的回答有三种：**一定别名**（MustAlias）、**可能别名**（MayAlias）、**一定不别名**（NoAlias）。只有能证明 NoAlias，编译器才能放心地把 `return *p` 优化为 `return 1`。

| 方法 | 原理 | 特点 |
|---|---|---|
| 基础规则 | 不同的局部变量、不同的全局变量不会别名 | 快速、精确，覆盖常见情况 |
| 基于类型的别名分析（Type-Based Alias Analysis, TBAA） | 按语言类型规则，`int*` 和 `float*` 不别名 | 对应 C/C++ 严格别名规则（Strict Aliasing Rule） |
| Andersen 分析（Andersen's Analysis） | 基于包含约束（Inclusion Constraint）`pts(p) ⊇ pts(q)` | 精度较高，开销较大 |
| Steensgaard 分析（Steensgaard's Analysis） | 基于合并（Unification），指向同一处的就合并为一类 | 近线性速度，精度较低 |
| 语言标注 | C 的 `restrict` 限定符、Rust 的 `&mut` 唯一性 | 程序员或语言保证不别名 |

其中 `pts(p)` 表示指针 p 的指向集（Points-to Set）。求解指向集的分析也称指针分析（Pointer Analysis / Points-to Analysis）。

**精度维度**：分析可以是流敏感（Flow-Sensitive，考虑语句顺序）、上下文敏感（Context-Sensitive，区分不同调用点）、字段敏感（Field-Sensitive，区分结构体的不同字段）的。越敏感越精确，开销也越大。

**别名分析的重要性在于：它几乎影响所有其他分析的精度。** 没有别名信息时，一次 `*p = ...` 就可能修改任何变量，所有已知信息都要作废。

**MemorySSA** 把别名分析与 SSA 结合起来：给内存操作建立 MemoryDef、MemoryUse、MemoryPhi，像对待寄存器值一样表示内存的定义—使用关系，从而加速 LICM、DSE、GVN 等优化。

## 4.5 依赖分析（Dependence Analysis）：语句能否重排或并行？

| 依赖类型 | 含义 | 示例 |
|---|---|---|
| 真依赖 / 流依赖（True / Flow Dependence, RAW） | 先写后读（Read After Write） | `a = 1; b = a;` |
| 反依赖（Anti-Dependence, WAR） | 先读后写（Write After Read） | `b = a; a = 1;` |
| 输出依赖（Output Dependence, WAW） | 先写后写（Write After Write） | `a = 1; a = 2;` |
| 控制依赖（Control Dependence） | 一条语句是否执行取决于另一条 | `if (c) x = 1;` |

循环中最关键的是**跨迭代依赖（Loop-Carried Dependence）**：

```c
for (i = 1; i < n; i++)
    a[i] = a[i-1] + 1;      // 第 i 次依赖第 i-1 次，距离为 1，不能直接并行
```

依赖分析计算**距离向量（Distance Vector）** 和**方向向量（Direction Vector）**，常用的判定方法有 GCD 测试（GCD Test）、Banerjee 测试（Banerjee Test）、Omega 测试（Omega Test）；更一般的框架是**多面体模型（Polyhedral Model）**，把循环迭代空间（Iteration Space）和数组访问表示成整数多面体。

**控制依赖**通过后支配树（Post-Dominator Tree）计算（Ferrante 等，1987）。数据依赖和控制依赖合在一起构成**程序依赖图（Program Dependence Graph, PDG）**，可用于程序切片（Program Slicing）。

## 4.6 标量演化（Scalar Evolution, SCEV）：归纳变量如何变化？

**标量演化** 用"递推表达式（Add Recurrence）"描述循环中变量的变化规律，其理论基础是递推链（Chains of Recurrences）：

```
{0, +, 1}<L>          从 0 开始，每次迭代加 1          （i）
{0, +, 4}<L>          从 0 开始，每次迭代加 4          （i * 4，即字节偏移）
{0, +, 0, +, 1}<L>    二阶递推                        （0, 0, 1, 3, 6……即 i(i-1)/2）
```

SCEV 能够回答：循环执行多少次（迭代次数，Trip Count）？变量的终值是什么？两个地址相差多少？它是分析归纳变量（Induction Variable, IV）、进行循环优化和向量化最重要的工具之一。

## 4.7 过程间分析（Interprocedural Analysis, IPA）：函数之间如何相互影响？

单个函数内的分析（过程内分析，Intraprocedural Analysis）遇到函数调用时，只能假设被调用函数（Callee）读写了所有可访问的内存。过程间分析打破这一限制：

| 内容 | 说明 |
|---|---|
| 调用图（Call Graph）构建 | 确定谁调用谁；遇到函数指针（Function Pointer）和虚函数（Virtual Function）时，借助指针分析、类层次分析（Class Hierarchy Analysis, CHA）、快速类型分析（Rapid Type Analysis, RTA） |
| 副作用分析（Mod/Ref Analysis） | 函数会读取、修改哪些内存 |
| 函数属性推断（Function Attribute Inference） | `readonly`、`nounwind`、`noreturn`、参数是否被捕获（Pointer Capture）等 |
| 上下文敏感 | 区分同一函数在不同调用点（Call Site）的行为 |
| 函数摘要（Function Summary） | 用摘要代替函数体，避免重复分析 |

**调用图与指针分析相互依赖**：构建调用图需要知道函数指针指向哪里，而精确的指针分析又需要调用关系，实践中常常两者同时求解（即时调用图构建，On-the-Fly Call Graph Construction）。

## 4.8 其他分析

| 分析 | 回答的问题 | 用途 |
|---|---|---|
| 逃逸分析（Escape Analysis） | 对象是否会逃出当前函数或线程？ | 栈上分配（Stack Allocation）、锁消除（Lock Elision）（JVM、Go） |
| 已知位分析（KnownBits Analysis） | 一个值的哪些二进制位确定为 0 或 1？ | 指令简化、消除冗余掩码（Mask） |
| 需求位分析（DemandedBits Analysis） | 一个值的哪些位真正被使用？ | 缩小运算位宽 |
| 形状分析（Shape Analysis） | 堆（Heap）上数据结构是链表、树还是有环？ | 高级优化与验证 |

## 4.9 分析一览

| 分析 | 核心问题 |
|---|---|
| 控制流分析 | 程序可能**怎么执行**？ |
| 数据流分析 | 每个点上**数据处于什么状态**？ |
| 别名分析 | 两个指针**是否指向同一处**？ |
| 依赖分析 | 语句之间**能否重排或并行**？ |
| 标量演化 | 循环变量**如何变化**？ |
| 过程间分析 | 函数之间**如何相互影响**？ |

---

# 第五部分　变换体系：中端如何"改写"程序

## 5.1 规范化（Canonicalization）：现代中端的设计哲学

同一个计算可以有许多写法：

```llvm
%a = sub i32 %x, -1      →   %a = add i32 %x, 1
%b = mul i32 %x, 8       →   %b = shl i32 %x, 3
%c = add i32 1, %x       →   %c = add i32 %x, 1     ; 常量放右边
```

如果每个优化都要识别所有等价写法，复杂度会爆炸。现代中端的做法是**规范化**：先把等价写法统一成一种标准形式——规范形式（Canonical Form），后续优化只需识别这一种。

LLVM 中最重要的两个规范化 Pass：

- **InstCombine（Instruction Combining，指令合并）**：指令层面的代数化简（Algebraic Simplification）和规范化，包含数千条规则。
- **SimplifyCFG（控制流简化）**：控制流层面的规范化，如合并基本块、删除空块、把简单分支转换为 `select` 指令（条件选择指令）。

它们在优化流水线中会被**反复调用**，每次大变换之后都要"清理现场"。

> 规范化形式不一定是"最快"的形式。最终的性能考虑留给后端，比如后端可能再把 `shl` 换回 `lea` 或其他指令。

## 5.2 标量优化（Scalar Optimization）

| 优化 | 作用 | 依赖的分析 |
|---|---|---|
| 常量折叠（Constant Folding） | `3 * 4 → 12` | 无 |
| 常量传播（Constant Propagation）/ SCCP | 把确定为常量的变量替换为常量 | 常量格 + SSA |
| 死代码消除（Dead Code Elimination, DCE）/ 激进死代码消除（Aggressive DCE, ADCE） | 删除结果不被使用的计算 | 活跃性 / 定义—使用链 |
| 公共子表达式消除（Common Subexpression Elimination, CSE）/ GVN | 相同计算只做一次 | 值编号（Value Numbering）、可用表达式 |
| 部分冗余消除（Partial Redundancy Elimination, PRE） | 消除部分路径上的冗余计算 | 可用 + 预期表达式 |
| 重结合（Reassociation） | 调整运算顺序，暴露更多常量和公共子表达式 | 代数性质 |
| 跳转线程化（Jump Threading） | 已知分支结果时，直接跳到目标 | 值的相关性 |
| 条件值传播（Correlated Value Propagation, CVP） | 利用分支条件推断值 | 范围分析 |
| 强度削弱（Strength Reduction） | 用便宜的运算代替昂贵的运算 | SCEV |

**SCCP 的例子** 很好地说明了"组合分析（Combined Analysis）"的威力：

```c
x1 = 1;
if (x1 == 1) y1 = 5;      // 可达
else         y2 = 7;      // 推断为不可达
y3 = φ(y1, y2);           // 只考虑可达路径 → y3 = 5
```

单独做常量传播，会因为 φ 合并了 5 和 7 而得到"非常量"；单独做不可达代码消除（Unreachable Code Elimination），又因为不知道 `x1 == 1` 为真而无法删除分支。SCCP **同时**推断值和可达性，才得到 `y3 = 5`。

## 5.3 内存优化（Memory Optimization）

内存访问比寄存器运算慢得多，也更难分析，是中端优化的重点。

| 优化 | 作用 |
|---|---|
| **SROA**（Scalar Replacement of Aggregates，聚合体标量替换） | 把结构体、数组、栈上变量拆分为独立标量，再提升为 SSA 值。这是 C/C++ 和 Rust 优化的起点：前端生成的代码充满了栈上读写，SROA 之后才变成干净的 SSA |
| **mem2reg**（Memory to Register Promotion） | 把 `alloca` 分配的栈上局部变量提升为 SSA 寄存器 |
| **DSE**（Dead Store Elimination，死存储消除） | 删除被覆盖且中间没有被读取的写入 |
| **存储到加载转发（Store-to-Load Forwarding）/ 冗余加载消除（Redundant Load Elimination）** | 刚写入的值可以直接使用，不必重新读取 |
| **MemCpyOpt**（Memcpy Optimization） | 合并、消除冗余的内存拷贝 |

```c
// SROA 之前：前端生成的典型代码
struct P { int x, y; } p;
p.x = a;   p.y = b;
return p.x + p.y;

// SROA 之后：结构体被拆为两个 SSA 值，内存访问全部消失
return a + b;
```

## 5.4 内联（Inlining）：最重要的优化

内联把函数调用替换为函数体。**它本身的收益（省去调用开销，Call Overhead）不大，真正的价值在于为其他优化创造机会**：

```c
int square(int x) { return x * x; }
int f() { return square(3); }

// 内联后：return 3 * 3;
// 常量折叠后：return 9;
```

内联后，调用点的具体信息（常量参数、已知的别名关系）和被调函数的代码放到了一起，原本跨函数无法进行的优化都可以进行了。

**代价模型是内联的核心**：内联会增大代码体积（代码膨胀，Code Bloat），可能降低指令缓存（Instruction Cache）命中率。内联器（Inliner）会估计"内联后函数体会缩小多少"（例如常量参数能删掉多少分支），并结合函数大小、调用频率（PGO 数据）、`always_inline` / `noinline` 等属性，与内联阈值（Inline Threshold）比较后做决策。

## 5.5 循环优化（Loop Optimization）

程序的大部分时间花在循环中，循环优化收益最大。

### 规范化

| 形式 | 要求 |
|---|---|
| LoopSimplify（循环规范形式） | 循环有唯一的前置块（Preheader）、唯一的回边、专用的退出块（Exit Block） |
| LCSSA（Loop-Closed SSA，循环闭合 SSA） | 循环内定义、循环外使用的值，在出口处用 φ 表示 |
| LoopRotate（循环旋转，Loop Rotation） | 把 `while` 形式转换为 `do-while` 形式，便于外提代码 |

### 主要变换

| 变换 | 作用 |
|---|---|
| LICM（Loop-Invariant Code Motion，循环不变代码外提） | 每次迭代结果都相同的计算（循环不变量，Loop Invariant）移到循环外 |
| 循环判断外提（Loop Unswitching） | 循环内不变的条件判断移到循环外，生成两个版本的循环 |
| 归纳变量简化（IndVarSimplify） | 规范化归纳变量，用 SCEV 计算终值 |
| 循环惯用法识别（Loop Idiom Recognition, LoopIdiom） | 把"逐元素清零"的循环识别为 `memset` |
| 循环删除（Loop Deletion） | 删除没有副作用的循环 |
| 循环展开（Loop Unrolling） | 减少循环控制开销，暴露更多指令级并行（Instruction-Level Parallelism, ILP） |
| 循环交换（Loop Interchange）、分块（Loop Tiling）、融合（Loop Fusion）、分布（Loop Distribution） | 改善数据局部性（Data Locality），需要依赖分析证明合法 |

**LICM 示例：**

```c
// 变换前
for (i = 0; i < n; i++)
    a[i] = x * y + i;

// 变换后
t = x * y;
for (i = 0; i < n; i++)
    a[i] = t + i;
```

**循环交换示例：** C 语言数组按行主序（Row-Major Order）存储，按列遍历会造成大量缓存缺失（Cache Miss）：

```c
// 变换前：内层循环按列访问，步长为 N
for (j = 0; j < N; j++)
    for (i = 0; i < N; i++)
        a[i][j] = 0;

// 变换后：内层循环按行连续访问
for (i = 0; i < N; i++)
    for (j = 0; j < N; j++)
        a[i][j] = 0;
```

## 5.6 向量化（Vectorization）

现代 CPU 提供单指令多数据（Single Instruction, Multiple Data, SIMD）指令，一条指令处理多个数据。向量化把标量代码转换为 SIMD 代码。

- **循环向量化（Loop Vectorization）**：把循环的多次迭代合并成一条向量操作。LLVM 使用 **VPlan（Vectorization Plan）** 表示多种候选方案（不同的向量化因子（Vectorization Factor, VF）、交织因子（Interleave Factor）），再由代价模型选择。

```c
for (i = 0; i < n; i++)
    a[i] = b[i] + c[i];
// 向量化后（宽度为 4）：每次处理 a[i..i+3]，剩余部分用标量尾循环处理
```

剩余元素由尾循环（Epilogue Loop / Remainder Loop）处理。

- **SLP 向量化（Superword-Level Parallelism Vectorization，超字级并行向量化）**：把直线代码（Straight-Line Code）中相似的标量操作组合成向量操作。

```c
a[0] = b[0] + c[0];
a[1] = b[1] + c[1];
a[2] = b[2] + c[2];
a[3] = b[3] + c[3];
// → 一条四宽度的向量加法
```

向量化需要多项分析共同支持：**依赖分析**证明没有阻碍并行的依赖，**别名分析**证明数组不重叠（无法证明时插入运行时检查（Runtime Check），生成两个版本，即循环多版本化（Loop Versioning）），**SCEV** 计算访问步长（Stride），**目标代价模型**判断是否划算。

## 5.7 过程间优化（Interprocedural Optimization, IPO）

| 优化 | 作用 |
|---|---|
| IPSCCP（Interprocedural SCCP） | 跨函数的常量传播 |
| GlobalOpt（全局变量优化） | 优化全局变量，如只被赋值一次的全局变量变为常量 |
| 函数属性推断 | 推断 `readonly`、`nounwind` 等，帮助调用者（Caller）优化 |
| 参数提升（Argument Promotion） | 把只读的指针参数改为按值传递 |
| 死参数消除（Dead Argument Elimination） | 删除未使用的参数和返回值 |
| 函数特化（Function Specialization） | 为常量参数生成专门的函数版本 |
| 函数合并（MergeFunctions） | 合并完全相同的函数，减小体积 |
| GlobalDCE（全局死代码消除） | 删除未使用的函数和全局变量 |

---

# 第六部分　分析与变换的协作

前两部分分别介绍了分析和变换，本部分说明它们如何组成一个整体。

## 6.1 层次关系

```
⑤ 理论层      格 + 不动点 + 抽象解释（保证终止与正确）
                           │
① 结构层      控制流分析（CFG、支配树、循环）
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
② 核心层  SSA 构造      数据流分析        依赖分析
          │                │                │
          └───────┬────────┘                │
                  ▼                         ▼
③ 应用层  SCCP / GVN / 范围分析 ...      循环变换 / 向量化
                  ▲                         ▲
                  └────────────┬────────────┘
④ 精度层          别名分析 + 过程间分析
```

各条关系的本质：

| 关系 | 本质 |
|---|---|
| 控制流分析 → SSA 构造（SSA Construction） | **支配边界**决定 φ 插入的位置（更准确地说是迭代支配边界，Iterated Dominance Frontier），沿**支配树**遍历完成变量重命名（Variable Renaming）（Cytron 等，1991） |
| 控制流分析 → 数据流分析 | CFG 定义了数据流方程中的"前驱"和"后继"，循环结构决定迭代效率 |
| 控制流分析 → 依赖分析 | **后支配树**产生控制依赖，**循环信息**支撑跨迭代依赖分析 |
| SSA + 数据流 → 稀疏分析 | 数据流提供"格 + 不动点"框架，SSA 提供高效的稀疏表示 |
| 依赖分析 → 循环变换 | 依赖关系是**守门人**，决定变换是否合法 |
| 别名 + 过程间分析 → 其他所有 | 去除指针和函数调用带来的不确定性，避免最坏假设（Worst-Case Assumption） |

## 6.2 每个优化都要回答三个问题

| 问题 | 含义 | 回答者 | 失败的后果 |
|---|---|---|---|
| **能做吗？**（合法性，Legality） | 变换是否保持语义 | 各种分析 | 生成错误代码（Miscompilation，最严重） |
| **值得做吗？**（收益性，Profitability） | 变换是否让程序更快、更小 | 代价模型、PGO 数据 | 性能下降 |
| **认得出吗？**（可识别性，Pattern Recognizability） | 能否找到可以变换的模式 | 规范化 | 错过优化机会 |

这三个问题对应中端的三大支柱：**分析**、**代价模型**、**规范化**。

## 6.3 变换会让分析失效（Analysis Invalidation）

关系图是自上而下画的，实际上存在大量反向影响：

- SCCP 删除了不可达分支，CFG 改变，支配树和循环信息失效。
- 内联改变了调用图。
- 循环展开改变了循环结构，SCEV 的结果失效。

现代中端通过**分析缓存（Analysis Caching）+ 失效机制**管理这个问题：每个变换声明自己**保留了哪些分析结果**（Preserved Analyses），未保留的标记为失效，下次需要时重新计算。一些变换还会**增量更新（Incremental Update）** 分析（例如 LLVM 的 `DomTreeUpdater` 在修改 CFG 的同时更新支配树），以避免重算的开销。

## 6.4 优化相互创造机会：阶段顺序问题（Phase Ordering Problem）

```
内联 → 暴露常量参数
     → 常量传播 → 某个分支条件变为常量
               → 删除不可达分支 → 循环结构变简单
                                → 可以向量化
```

优化之间互相"喂养"，执行顺序会影响最终效果，这就是**阶段顺序问题**。理论上最优顺序很难找，实践中的解决办法有：

1. **重复执行**关键的简化 Pass（InstCombine、SimplifyCFG 在流水线中出现多次）。
2. **组合分析**：像 SCCP 那样把多个分析合并成一个，同时求解。
3. **精心设计的流水线**：基于大量实验调整顺序（第七部分）。
4. **等式饱和**：用 e-graph 同时保留所有等价形式，最后再选择（第十二部分）。

---

# 第七部分　工程组织：Pass 管理器与优化流水线

## 7.1 Pass（遍）：中端的基本单元

中端被拆分为许多独立的 **Pass**，每个 Pass 完成一件事：

- **分析 Pass（Analysis Pass）**：计算信息，不修改 IR（如 DominatorTree、LoopInfo、ScalarEvolution）。
- **变换 Pass**：修改 IR（如 GVN、LICM、LoopVectorize）。

这种设计使每个 Pass 都易于理解、测试和替换。

## 7.2 Pass 管理器（Pass Manager）

LLVM 的新 Pass 管理器（New Pass Manager, NPM，LLVM 13 起成为 Clang 默认）按 IR 的层级组织：

```
ModulePass             整个模块
  └─ CGSCCPass         调用图的强连通分量（自底向上）
       └─ FunctionPass 单个函数
            └─ LoopPass 单个循环（由内向外）
```

这里的模块（Module）对应一个编译单元的 IR，CGSCC 指调用图强连通分量（Call Graph Strongly Connected Component）。

**CGSCC 层是关键设计。** 它按调用图**自底向上（Bottom-Up）** 处理：先把被调用函数优化好，再处理调用者。这样内联器决策时看到的是**已经简化过的函数体**，代价估计更准确；内联之后立刻对调用者进行简化，又可能暴露新的内联机会。

## 7.3 典型优化流水线（Optimization Pipeline）：LLVM -O2/-O3

```
┌─────────────────────── 阶段一：模块级简化 ───────────────────────┐
│ InferFunctionAttrs   推断库函数属性                               │
│ IPSCCP               过程间常量传播                               │
│ GlobalOpt            全局变量优化                                 │
│ ...                                                             │
└─────────────────────────────────────────────────────────────────┘
                                ▼
┌──────────── 阶段二：CGSCC 内联 + 函数简化（核心） ────────────────┐
│ 对调用图自底向上，每个 SCC：                                       │
│   Inliner                                                       │
│   函数简化流水线：                                                 │
│     SROA → EarlyCSE → InstCombine → SimplifyCFG                 │
│     → JumpThreading → CorrelatedValuePropagation → Reassociate  │
│     → 循环流水线：LoopRotate、LICM、SimpleLoopUnswitch、            │
│                  IndVarSimplify、LoopIdiom、LoopDeletion、        │
│                  LoopFullUnroll                                 │
│     → SCCP → GVN → BDCE → DSE → ADCE                            │
│     → InstCombine → SimplifyCFG（再次清理）                        │
│   FunctionAttrs     推断函数属性，供上层调用者使用                   │
└─────────────────────────────────────────────────────────────────┘
                                ▼
┌─────────────────────── 阶段三：模块级优化 ───────────────────────┐
│ LoopVectorize → SLPVectorizer → LoopUnroll                      │
│ InstCombine / SimplifyCFG（清理）                                 │
│ GlobalDCE                                                       │
└─────────────────────────────────────────────────────────────────┘
```

图中 EarlyCSE 为早期公共子表达式消除，BDCE 为位跟踪死代码消除（Bit-Tracking Dead Code Elimination）。

## 7.4 为什么分"简化"和"优化"两个阶段

| | 简化阶段（Simplification Pipeline） | 优化阶段（Optimization Pipeline） |
|---|---|---|
| 目标 | 去除冗余，让代码更简单、更规范 | 针对性能做变换，可能让代码变大 |
| 典型 Pass | 内联、SROA、GVN、InstCombine | 向量化、展开 |
| 对目标的依赖 | 弱 | 强（依赖代价模型） |

原因有两点：一是展开和向量化会让代码变大、变复杂，过早进行会妨碍其他优化（比如让函数变大而不再被内联）；二是在 **ThinLTO** 中，编译单个文件时只做简化，等链接阶段看到全局信息、完成跨模块内联后，再做优化。

## 7.5 不同优化等级（Optimization Level）

| 等级 | 特点 |
|---|---|
| `-O0` | 几乎不优化，便于调试 |
| `-O1` | 基本优化，编译快 |
| `-O2` | 默认的发布级优化，平衡编译时间（Compile Time）与性能 |
| `-O3` | 更激进的内联、展开和向量化，代码可能变大 |
| `-Os` / `-Oz` | 优先减小代码体积（Code Size） |

---

# 第八部分　跨越边界：LTO 与 PGO

传统编译有两个局限：**一次只能看到一个文件（编译单元，Translation Unit）**，**不知道程序实际如何运行**。LTO 和 PGO 分别解决这两个问题。

## 8.1 链接时优化（Link-Time Optimization, LTO）

```
传统编译：  a.c → a.o ─┐
           b.c → b.o ─┼→ 链接 → 可执行文件      （中端看不到跨文件的调用）
           c.c → c.o ─┘

LTO：      a.c → a.bc ─┐
           b.c → b.bc ─┼→ 链接时运行中端 → 后端 → 可执行文件
           c.c → c.bc ─┘
```

| 方式 | 做法 | 优缺点 |
|---|---|---|
| **完全 LTO（Full LTO）** | 把所有模块的 IR 合并成一个大模块再优化 | 优化最充分，但内存占用大、难以并行 |
| **ThinLTO**（LLVM） | 每个模块生成摘要；链接时基于摘要做全局分析；然后**并行**地对每个模块导入需要的函数（Function Importing）并优化 | 可扩展到大型项目，支持增量编译 |
| **WHOPR**（WHOle Program optimizeR，GCC） | 先做全程序分析（Whole Program Analysis, WPA），再分区并行优化（Local Transformation, LTRANS） | GCC 的可扩展 LTO 方案 |

LTO 带来的典型收益：跨文件内联、全程序死代码删除、更精确的过程间常量传播、去虚拟化（Devirtualization）。

## 8.2 基于剖析的优化（Profile-Guided Optimization, PGO）

静态分析不知道哪些分支常走、哪些函数热。PGO（也称反馈导向优化，Feedback-Directed Optimization, FDO）用真实运行数据回答这些问题：

| 方式 | 做法 | 特点 |
|---|---|---|
| 插桩式 PGO（Instrumentation-based PGO） | 编译带计数器的版本 → 运行典型负载（Workload）→ 用数据重新编译 | 数据精确，流程繁琐 |
| 采样式 PGO（Sampling-based PGO，如 AutoFDO） | 用硬件性能计数器（Hardware Performance Counter）在生产环境采样 | 开销小，可持续收集 |
| CSSPGO（Context-Sensitive Sample PGO） | 上下文敏感的采样 PGO | 区分不同调用上下文 |

剖析数据影响的中端决策：

- **内联**：热点（Hot Spot）调用优先内联，冷调用不内联
- **代码布局（Code Layout）**：热块放在一起，冷代码（Cold Code）移到函数末尾或单独分区（冷热分离，Hot/Cold Splitting）
- **循环展开与向量化**：只对热循环积极优化
- **间接调用提升（Indirect Call Promotion）**：把常见的间接调用目标转换为直接调用加判断

> BOLT（Binary Optimization and Layout Tool）、Propeller 等是在链接之后对二进制进行优化（链接后优化，Post-Link Optimization）的工具，不属于中端，但常与 PGO 配合使用。

---

# 第九部分　完整案例：一个函数的优化之旅

把前面的内容串起来，看一个函数如何经过中端的各个环节。

```c
int sum(int *a, int *b, int n) {
    int k = 4;
    int s = 0;
    for (int i = 0; i < n; i++) {
        int t = k * 2;
        a[i] = b[i] + t;
        s += a[i];
    }
    return s;
}
```

| 步骤 | 技术 | 发生了什么 |
|---|---|---|
| 1 | 前端生成 IR | `k`、`s`、`i`、`t` 都是栈上变量（Stack Variable），每次使用都要从内存读写 |
| 2 | 控制流分析 | 构建 CFG，计算支配树，识别出一个循环 |
| 3 | SROA / mem2reg | 把栈变量提升为 SSA 值，在循环头（支配边界）插入 `i1 = φ(0, i2)`、`s1 = φ(0, s2)` |
| 4 | InstCombine / SCCP | `k = 4` 是常量，`t = 8`，循环体变为 `a[i] = b[i] + 8` |
| 5 | LoopRotate | 把循环转为 `do-while` 形式，在前面加上 `n > 0` 的判断（循环守卫，Loop Guard） |
| 6 | SCEV | 识别 `i` 为 `{0, +, 1}`，迭代次数为 `n` |
| 7 | GVN / 存储转发 | `s += a[i]` 中的 `a[i]` 刚刚写入，直接使用写入的值，省去一次读内存 |
| 8 | 别名分析 | `a` 和 `b` 是否重叠？无法静态证明 |
| 9 | 依赖分析 | 若不重叠，则 `a[i]`、`b[i]` 无跨迭代依赖；`s` 通过 φ 环（Phi Cycle）被识别为**归约变量（Reduction Variable）** |
| 10 | 循环向量化 | 生成运行时重叠检查：不重叠时走向量版本，一次处理多个元素，`s` 使用向量累加（Vector Accumulation）、最后做水平归约（Horizontal Reduction）合并；重叠时走标量版本 |
| 11 | 清理 | InstCombine、SimplifyCFG 整理代码，交给后端 |

这个过程体现了中端的典型特征：**没有 CFG 就没有 SSA，没有 SSA 就难以高效地传播常量和识别归约，没有别名和依赖分析就无法安全地向量化**。每一步都建立在前面的结果上，单个优化单独看并不神奇，组合在一起才产生了巨大的效果。

---

# 第十部分　正确性：未定义行为与编译器验证

## 10.1 优化必须正确

一个优化如果在 99.99% 的情况下都对，但有 0.01% 的情况会改变程序行为，那它就是错误的。中端最大的挑战之一就是**在极其复杂的变换中保证正确性（Correctness）**。

## 10.2 未定义行为（Undefined Behavior, UB）：优化的依据

C/C++ 等语言规定某些操作是**未定义行为**，例如有符号整数溢出（Signed Integer Overflow）、空指针解引用（Null Pointer Dereference）、越界访问（Out-of-Bounds Access）。编译器可以**假设程序中不发生 UB**，并据此优化：

```c
// 例 1：利用"有符号数不溢出"
for (int i = 0; i <= n; i++) { ... }
// 若 i 可能溢出，循环可能不终止，迭代次数无法计算
// 有符号溢出是 UB → 编译器假设不溢出 → 迭代次数为 n + 1 → 可以向量化
```

```c
// 例 2：利用"不会解引用空指针"
int x = *p;
if (p == NULL) return 0;   // 前面已经解引用了 p，编译器可推断 p 非空，删除这个判断
```

例 2 也说明了 UB 的危险：如果程序本身有错误，优化会让错误的表现变得出乎意料。这也是 Linux 内核等项目使用 `-fno-delete-null-pointer-checks` 等选项的原因。

## 10.3 IR 语义的精确化

为了准确表达"假设不发生某事"，LLVM IR 设计了专门的语义：

| 概念 | 含义 |
|---|---|
| `nsw` / `nuw`（No Signed Wrap / No Unsigned Wrap） | 有符号 / 无符号运算不溢出，若溢出则结果为 poison |
| `poison` | 违反假设时产生的值，只要被用于有副作用的操作就是 UB |
| `undef`（未定值） | 每次使用可以取任意值（语义难以推理，正逐渐被 poison 取代） |
| `freeze` | 把 poison/undef 固定为某个任意但确定的值 |

这些语义看起来很学术，但它们直接决定了一个优化是否合法。过去 LLVM 中很多优化错误，根源就在于 `undef` 语义不清。

## 10.4 如何验证编译器

| 方法 | 代表 | 说明 |
|---|---|---|
| 翻译验证（Translation Validation） | **Alive2** | 用 SMT 求解器（Satisfiability Modulo Theories Solver）自动检查 LLVM 优化前后的 IR 是否语义等价，已发现大量错误优化 |
| 形式化证明（Formal Verification） | **CompCert** | 用证明助手（Proof Assistant）Coq 证明整个编译器的正确性，是经过验证的编译器（Verified Compiler） |
| 随机测试 / 差分测试（Random Testing / Differential Testing） | **Csmith**、YARPGen | 随机生成合法程序，比较不同编译器、不同优化等级的结果 |
| IR 验证器（IR Verifier） | LLVM `Verifier` | 检查每个 Pass 之后 IR 是否仍然结构合法 |

---

# 第十一部分　工业实现：主流编译器的中端

| 编译器 | 中端 IR | 特点 |
|---|---|---|
| **LLVM** | LLVM IR（SSA） | 模块化、Pass 丰富、生态最广；Clang、Rust、Swift、Julia、Zig 等共用 |
| **GCC** | GIMPLE（SSA 形式的三地址码） | 历史悠久，过程间分析（IPA）成熟；之后降级（Lowering）到 RTL（Register Transfer Language，寄存器传输语言）进入后端 |
| **MLIR** | 多层级方言 | 构建 IR 的框架，支持逐级降级，广泛用于 AI 编译器 |
| **Cranelift** | CLIF（SSA） | 面向 WebAssembly 和即时编译（Just-In-Time Compilation, JIT），强调编译速度；中端使用基于 e-graph 的 aegraph（Acyclic E-Graph） |
| **HotSpot C2** | Sea of Nodes | 基于图的 IR，结合运行时剖析做推测优化（Speculative Optimization），假设失效时去优化（Deoptimization） |
| **GraalVM** | Graal IR | 用 Java 编写，支持部分求值（Partial Evaluation）（Truffle 框架） |
| **V8** | TurboFan → Turboshaft | 逐步放弃 Sea of Nodes，回到基于 CFG 的 IR，理由是图 IR 复杂度和编译开销过高 |
| **rustc** | MIR | 借用检查和 Rust 特有的优化，之后生成 LLVM IR |
| **Swift** | SIL | 自动引用计数（Automatic Reference Counting, ARC）优化、泛型特化（Generic Specialization）等，之后生成 LLVM IR |
| **Go** | SSA IR | 自研中端，追求快速编译 |

**LLVM 中各技术对应的组件：**

| 技术 | LLVM 中的分析 / Pass |
|---|---|
| 控制流分析 | `DominatorTree`、`PostDominatorTree`、`LoopInfo` |
| SSA 构造 | `mem2reg`、`SROA` |
| 内存 SSA | `MemorySSA` |
| 常量传播与死代码消除 | `SCCP`、`IPSCCP`、`ADCE`、`BDCE` |
| 值编号 | `GVN`、`NewGVN`、`EarlyCSE` |
| 范围与位分析 | `LazyValueInfo`（惰性值信息，LVI）、`ValueTracking`（KnownBits）、`DemandedBits` |
| 标量演化 | `ScalarEvolution` |
| 别名分析 | `AAResults`（汇总 `BasicAA`、`TBAA`、`ScopedNoAlias` 等） |
| 依赖分析 | `DependenceAnalysis`、`LoopAccessAnalysis`（循环访问分析，LAA） |
| 规范化 | `InstCombine`、`SimplifyCFG` |
| 循环与向量化 | `LICM`、`LoopUnroll`、`LoopVectorize`（VPlan）、`SLPVectorizer` |
| 过程间 | `CallGraph`、`Inliner`、`FunctionAttrs`、`GlobalOpt` |
| 目标代价查询 | `TargetTransformInfo`（目标变换信息，TTI） |

**一个值得注意的趋势是多层中端：**

```
Rust:   AST → HIR → MIR（所有权相关的分析与优化）→ LLVM IR（通用优化）→ 机器码
Swift:  AST → SIL（ARC、泛型特化）              → LLVM IR              → 机器码
AI:     模型图 → 张量方言 → linalg → affine/scf → vector → llvm 方言 → LLVM IR
```

其中 HIR 为 rustc 的高层 IR（High-Level IR）。原因在于 LLVM IR 层次较低，已经丢失了所有权、引用计数、张量（Tensor）运算等高层语义。相关优化必须在更高层完成，否则信息一旦丢失就无法恢复。MLIR 正是把这种思路系统化的产物。

---

# 第十二部分　发展趋势与学习路线

## 12.1 发展趋势

### 1. 多层级 IR

MLIR 让每一层都能做最适合该层的优化：张量层做算子融合（Operator Fusion），仿射（Affine）层做多面体循环变换，向量层做 SIMD 映射。它已被 IREE、Triton、XLA、Flang（Fortran）、CIRCT（硬件设计）等项目采用。

### 2. 等式饱和（Equality Saturation）与 e-graph

为解决阶段顺序问题，**e-graph（等价图，Equivalence Graph）** 用等价类（E-Class）同时保存表达式的所有等价形式：先尽可能应用所有改写规则（Rewrite Rule），再用代价函数提取（Extraction）最优形式。研究工具有 `egg`（e-graphs good），工业应用有 Cranelift 的 aegraph。

### 3. 机器学习引导的决策

用机器学习模型替代手工启发式规则（Heuristic）。Google 的 **MLGO（Machine Learning Guided Optimization）** 已集成进 LLVM，用于内联决策（优化体积）和寄存器分配中的驱逐决策（Eviction Decision），训练方法包括强化学习（Reinforcement Learning, RL）。其他研究方向包括 Pass 顺序选择、代价模型学习等。

### 4. 形式化与正确性

Alive2 推动 LLVM 语义的精确化，越来越多的优化在加入前先经过形式化检查。

### 5. 编译速度

Cranelift、Go 等编译器选择牺牲部分代码质量换取编译速度；LLVM 社区持续跟踪和优化编译时间；ThinLTO 和增量编译（Incremental Compilation）让大型项目也能负担全程序优化（Whole-Program Optimization）。

### 6. 安全加固（Security Hardening）

中端不仅做性能优化，也负责插入安全检查：AddressSanitizer（ASan）、ThreadSanitizer（TSan）、UndefinedBehaviorSanitizer（UBSan）等消毒器（Sanitizer）在中端插桩（Instrumentation），控制流完整性（Control-Flow Integrity, CFI）依赖 LTO 提供的全程序类型信息。

## 12.2 学习路线

| 阶段 | 内容 | 资源 |
|---|---|---|
| 1. 理论基础 | CFG、数据流分析、格与不动点、SSA | 《Engineering a Compiler》、《编译原理》（龙书，Dragon Book）第 9 章、《SSA-based Compiler Design》 |
| 2. 阅读 IR | 用 `clang -O0 -emit-llvm -S` 生成 IR，用 `opt -passes=...` 逐个运行 Pass 观察变化 | LLVM Language Reference Manual |
| 3. 观察流水线 | `opt -O2 -print-pipeline-passes`、`-print-after-all` | 编译器浏览器 Compiler Explorer（godbolt.org）可直接查看每个 Pass 前后的 IR |
| 4. 编写 Pass | 实现一个简单的分析或变换 Pass | LLVM 官方 "Writing an LLVM Pass" 教程 |
| 5. 深入子系统 | SCEV、MemorySSA、InstCombine、VPlan、Inliner | LLVM Developers' Meeting 演讲视频 |
| 6. 了解前沿 | MLIR、e-graph、MLGO、Alive2 | MLIR Toy 教程、egg 论文、Alive2 论文 |

---

# 结语

回顾全文，现代编译器中端可以概括为以下几个要点：

| 方面 | 要点 |
|---|---|
| **定位** | 位于前端与后端之间，在目标无关的 IR 上做保持语义的优化 |
| **表示** | 以 CFG + SSA 为核心，语义精确定义，逐渐走向多层级 |
| **理论** | 格 + 单调传递函数 + 不动点迭代，抽象解释提供统一框架；"宁可错过，不可做错" |
| **分析** | 控制流、数据流、别名、依赖、标量演化、过程间分析，各自回答一个关于程序的问题 |
| **变换** | 规范化、标量优化、内存优化、内联、循环优化、向量化、过程间优化 |
| **协作** | 每个优化都要回答"能做吗、值得做吗、认得出吗"；变换会让分析失效，优化之间相互创造机会 |
| **组织** | Pass 管理器按层级组织，流水线先简化再优化，内联与简化在调用图上交替进行 |
| **扩展** | LTO 突破文件边界，PGO 引入运行时信息 |
| **正确性** | 依托精确的 IR 语义，借助翻译验证和随机测试保障 |
| **趋势** | 多层 IR、e-graph、机器学习、形式化验证、编译速度与安全 |

用一句话总结：

> **中端以 SSA 形式的 IR 为舞台，以格与不动点理论为保障：控制流分析搭好骨架，数据流分析和 SSA 推理数据，别名与过程间分析消除不确定性，依赖分析约束执行顺序，规范化让模式易于识别，代价模型判断是否值得，最终由大量可组合的 Pass 在精心设计的流水线中反复协作，把程序改写为更高效的等价形式。**

理解中端，关键不在于记住每个 Pass 的名字，而在于把握这条主线：**先理解程序（分析），再安全地改写程序（变换），并让两者在工程上高效地协同工作。**