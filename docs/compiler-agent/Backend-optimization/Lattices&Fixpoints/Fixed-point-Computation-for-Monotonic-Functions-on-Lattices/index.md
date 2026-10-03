# Fixed-point Computation for Monotonic Functions on Lattices

### 格上的单调函数求不动点（Fixed-point Computation for Monotonic Functions on Lattices）

这是**序理论（Order Theory）**与理论计算机科学的核心基础工具，也是编译器静态分析、抽象解释、模型检测的数学底层框架。它的核心逻辑是：利用格的序结构性质与函数的单调性，严格保证不动点的存在性，并通过可计算的迭代方法高效求解。

---

## 一、基础概念定义

### 1. 格（Lattice）

设 $(L, \le)$ 是一个**偏序集（Partially Ordered Set, Poset）**，若对任意两个元素 $a,b \in L$，都存在唯一的**最小上界（Least Upper Bound，又称 join，记作 $\vee$ / 并）**和**最大下界（Greatest Lower Bound，又称 meet，记作 $\wedge$ / 交）**，则称 $(L, \le)$ 是一个格。

- 若 $L$ 的**任意子集**都存在最小上界和最大下界，则称为**完全格（Complete Lattice）**。完全格必然包含全局最小元**底元（bottom，记作 $\perp$）**和全局最大元**顶元（top，记作 $\top$）**。
- 计算机科学中的绝大多数应用场景都基于完全格，例如程序数据流分析的值域、有限状态集合、抽象解释的抽象域都是典型的完全格。

### 2. 单调函数（Monotonic Function）

设 $f: L \to L$ 是格 $L$ 上的自映射，若对任意 $x,y \in L$，只要 $x \le y$ 就一定有 $f(x) \le f(y)$，则称 $f$ 是单调函数。

> 单调性的核心意义：输入的偏序关系不会被函数反转，迭代过程只会单向演进，不会出现震荡，这是迭代收敛的根本前提。

### 3. 不动点（Fixed Point）

若元素 $x \in L$ 满足等式 $f(x) = x$，则称 $x$ 是函数 $f$ 的一个不动点。

- 所有不动点中偏序最小的，称为**最小不动点（Least Fixed Point, LFP）**；
- 所有不动点中偏序最大的，称为**最大不动点（Greatest Fixed Point, GFP）**。

---

## 二、核心理论基础：Knaster-Tarski 不动点定理

**Knaster-Tarski 不动点定理（Knaster-Tarski Fixed-Point Theorem）**是整个方法的理论基石，也是程序分析中数据流方程解的存在性依据：

> 设 $L$ 是完全格，$f: L \to L$ 是单调函数，则 $f$ 的全体不动点构成的集合本身也是一个完全格；特别地，$f$ 一定存在唯一的最小不动点和唯一的最大不动点。

该定理的条件极弱——仅要求单调性，不要求连续性、线性等强约束，因此编译器中几乎所有数据流转移函数、状态转移函数都天然满足，从数学上保证了静态分析解的存在性。

---

## 三、标准求解方法：迭代不动点算法

工程上最通用的求解方法是**迭代不动点算法（Iterative Fixed-Point Algorithm）**，利用单调性从格的边界元出发逐步迭代逼近，最终收敛到目标不动点。

### 1. 求解最小不动点（LFP）

从完全格的底元 $\perp$ 出发，反复迭代应用函数 $f$，得到一条严格递增的链：
$$
\perp \le f(\perp) \le f(f(\perp)) \le f^3(\perp) \le \dots
$$
由于函数单调且格是完全的，该序列最终必然收敛，收敛的极限就是 $f$ 的最小不动点：
$$
\text{lfp}(f) = \bigvee_{n=0}^{\infty} f^n(\perp)
$$

- **有限格性质**：如果格的高度有限（计算机中绝大多数工程场景都是有限格），则迭代一定会在有限步内终止，得到精确的最小不动点。
- **典型应用**：编译原理中的**前向数据流分析（Forward Data Flow Analysis）**，例如到达-定值分析、可用表达式分析，都是通过该方法求解。

### 2. 求解最大不动点（GFP）

与最小不动点对称，从顶元 $\top$ 出发迭代，得到一条严格递减的链：
$$
\top \ge f(\top) \ge f(f(\top)) \ge f^3(\top) \ge \dots
$$
收敛的极限就是最大不动点：
$$
\text{gfp}(f) = \bigwedge_{n=0}^{\infty} f^n(\top)
$$

- **典型应用**：后向数据流分析（如活跃变量分析）、程序安全性属性验证、共归纳性质的模型检测。

### 3. 无限格的加速：加宽算子

对于高度无限的格（如整数区间域），朴素迭代可能永远不收敛。此时会引入**加宽算子（Widening Operator）**，通过外推加速迭代过程，在有限步内得到一个安全的上近似不动点，这是**抽象解释（Abstract Interpretation）**的核心技术之一。

---

## 四、编译与编程语言领域的典型应用

1. **数据流分析（Data Flow Analysis）**：到达-定值、常量传播、死代码检测、活跃变量等经典编译器静态分析，本质都是将程序点的抽象值构造为格、将控制流转移构造为单调函数，通过求不动点得到全程序的分析结果。
2. **抽象解释（Abstract Interpretation）**：程序抽象语义的正确性、收敛性完全建立在单调函数不动点理论之上，是现代静态代码分析工具的底层数学框架。
3. **类型推导**：Hindley-Milner 类型系统、控制流敏感的类型约束求解，本质都是格上的不动点计算问题。
4. **模型检测（Model Checking）**：CTL 等时序逻辑的模型检测算法，核心就是计算状态转移函数的最小/最大不动点，以验证程序的时态属性。





## TODO

wikipedia [Knaster–Tarski theorem](https://en.wikipedia.org/wiki/Knaster%E2%80%93Tarski_theorem) 

wikipedia [Kleene fixed-point theorem](https://en.wikipedia.org/wiki/Kleene_fixed-point_theorem) 

wikipedia [Fixed-point theorem](https://en.wikipedia.org/wiki/Fixed-point_theorem) 
