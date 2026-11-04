# 不动点与不动点语义：从直觉到理论

**Fixed Points and Fixed-Point Semantics: From Intuition to Theory**

---

## 摘要（Abstract）

**不动点（Fixed Point）** 是数学中的一个基本概念：若 $f(x)=x$，则称 $x$ 是 $f$ 的不动点。**不动点语义（Fixed-Point Semantics）** 是建立在这一概念上的 **语义方法论（Semantic Methodology）** 。它把**递归定义（Recursive Definition）** 理解为一个"答案必须满足"的方程，再从这个方程的众多解中选出**最小不动点（Least Fixed Point）** 作为程序的意义。这个最小不动点可以从"一无所知"出发，逐轮补充信息，以极限的方式求得。

本文按"直觉、定义、定理"三步展开。每个概念先用"逐轮填表"的类比和可运行的代码讲清楚，再给出形式定义与证明。全文从不动点的基本概念、递归方程的"无解"与"多解"问题讲起，引入**信息序（Information Order）**、**完全偏序（Complete Partial Order, CPO）** 与**连续性（Continuity）**，证明 **Kleene 不动点定理**与 **Knaster–Tarski 定理**，并由"最小性"推出 **Park 归纳**与 **Scott 归纳（不动点归纳）** 等推理原理。随后以 While 语言和 PCF 为例展示不动点语义的完整做法，讨论它与**操作语义（Operational Semantics）** 的**充分性（Adequacy）** 联系。最后介绍**递归域方程（Recursive Domain Equations）**，以及不动点在**程序分析（Program Analysis）**、**逻辑程序（Logic Programming）**、**模型检测（Model Checking）** 和**余归纳（Coinduction）** 中的应用，并说明它与 **初始代数（Initial Algebra）** 理论的统一关系。

**关键词（Keywords）**：不动点（Fixed Point）；最小不动点（Least Fixed Point）；完全偏序（CPO）；Kleene 不动点定理（Kleene Fixed-Point Theorem）；Knaster–Tarski 定理（Knaster–Tarski Theorem）；不动点归纳（Fixed-Point Induction）；指称语义（Denotational Semantics）；域论（Domain Theory）

---

## 阅读指南与记号约定（Reading Guide and Conventions）

**全文结构**

| 部分 | 章节 | 内容 | 前置知识 |
|---|---|---|---|
| 第一部分：直觉与基础 | §1–§5 | 填表类比、不动点、递归方程的困难、信息序与 CPO | 能读懂简单的 Python |
| 第二部分：理论与方法 | §6–§9 | Kleene 定理、Tarski 定理、推理原理、While 与 PCF 的不动点语义 | 了解函数、集合与数学归纳法 |
| 第三部分：进阶 | §10–§12 | 递归域方程、程序分析与验证中的应用、推广与边界 | 有一定序论或范畴论基础，**首次阅读可跳过** |
| 总结 | §13 | 常见误解、术语总表 | — |

**排版约定**：直觉性讲解用正文书写。形式化内容放在引用块中，以"**定义**""**定理**""**引理**"等开头。

**记号约定**

- 语义括号统一写作 $\lbrack\!\lbrack e \rbrack\!\rbrack$，读作"$e$ 的意义"。
- $\sqsubseteq$ 表示**信息序（Information Order）**，读作"信息不多于"；$\bigsqcup$ 表示**上确界（Least Upper Bound）**。
- $\bot$ **只**表示序中的**最小元（Bottom）**，即"尚无任何信息"，用于刻画非终止。它不是一个可以被检测的错误值。
- $\mathrm{fix}(\Phi)$、$\mathrm{lfp}(\Phi)$、$\mu x.\,\Phi(x)$ 都表示最小不动点；$\mathrm{gfp}(\Phi)$、$\nu x.\,\Phi(x)$ 表示**最大不动点（Greatest Fixed Point）**。
- 用于定义递归对象的高阶函数，例如 $\Phi$，称为**泛函（Functional）**。
- 程序状态记作 $\mathit{st}$。对 $g:A\to B_\bot$，其**严格扩展（Strict Extension）** $g^\dagger:A_\bot\to B_\bot$ 定义为 $g^\dagger(\bot)=\bot$，$g^\dagger(a)=g(a)$。
- 本文称满足 $f(x)\sqsubseteq x$ 的 $x$ 为**前不动点（Pre-Fixed Point）**，满足 $x\sqsubseteq f(x)$ 的 $x$ 为**后不动点（Post-Fixed Point）**。文献中这两个名称的用法并不统一，阅读时需留意各自的定义。

---

# 第一部分：直觉与基础

## 1. 引言（Introduction）

### 1.1 一句话版本

先给出全文的一句话版本：

> **递归定义不是一条"去执行"的指令，而是一个"答案必须满足"的方程。方程可能无解，也可能有很多解；不动点语义规定：取那个只包含"有限步就能确定的信息"的解。它就是从"一无所知"出发、一轮轮补充信息所逼近的极限，即最小不动点。**

本文的全部内容，都是在把这句话讲清楚，再把它证明出来。

### 1.2 两个问题与一个答案

程序语言语义学在处理递归与循环时，必须回答两个问题：

1. 像 `fact(n) = if n == 0 then 1 else n * fact(n - 1)` 这样"用自己定义自己"的定义，**数学上到底指什么**？等号两边都出现了 `fact`，它并不是一个普通的定义。
2. 像 `f(x) = f(x)` 这样的定义同样能通过编译，运行时永不停止。它的"意义"是什么？又怎样让这个意义与程序的实际行为一致？

1969—1971 年间，**Dana Scott** 与 **Christopher Strachey** 给出了一个统一的答案（Scott, 1970；Scott & Strachey, 1971）：

- 把递归定义看作方程 $f=\Phi(f)$，它的解就是泛函 $\Phi$ 的**不动点**；
- 在一个按"信息多少"排序的空间，即 **域（Domain）** 中求解；
- 选取其中**最小**的那个解。

这一思路的数学基础是两个经典定理：序论中的 **Knaster–Tarski 定理**（Knaster, 1928；Tarski, 1955），以及递归论中由 Kleene 的**第一递归定理（First Recursion Theorem）** 发展而来的 **Kleene 不动点定理**（Kleene, 1952）。二者的署名与历史渊源较为复杂，可参见 Lassez、Nguyen 与 Sonenberg（1982）。

- 作为**概念**，不动点刻画了"自我指涉的定义"的解。
- 作为**方法**，不动点语义用最小不动点给递归赋予意义，从而自动得到存在性、与执行过程一致的逼近性，以及一套称为**不动点归纳（Fixed-Point Induction）** 的推理原理。

### 1.3 全文路线

```
一张自我指涉的表（填表类比） → 方程 x = f(x)（不动点）
   → 递归方程会无解或多解（为什么需要 ⊥ 和"最小"）
   → 按信息多少排序（信息序、CPO、单调、连续）
   → 从 ⊥ 出发逐轮逼近（Kleene 定理） / 取所有"够用的猜测"之交（Tarski 定理）
   → 由最小性推出推理原理（Park 归纳、Scott 归纳）
   → 给程序语言下定义（While、PCF）并与执行对齐（充分性）
   → 递归域方程、程序分析、逻辑与验证、与初始代数的统一
```

---

## 2. 一个贯穿全文的类比：逐轮填表（An Analogy: Filling in a Table Round by Round）

老师布置了一道题：填一张关于 $n!$ 的表，表有无穷多格，编号 $0,1,2,\dots$。老师只给了一条规则：

> **第 0 格写 1；第 $n$ 格写 $n$ 乘以第 $n-1$ 格。**

这条规则有一个特点：它**提到了表本身**。要填第 5 格，得先知道第 4 格。规则不是"怎么算"，而是"填好之后的表必须满足什么"。

一个谨慎的填表人会这样做：

1. **第 0 轮**：表是空的，什么都不知道。
2. **每一轮**：照着规则，**只依据上一轮已经填好的格子**，看还能新填哪些格子。已填的格子**只增不改**。
3. 第 1 轮能填第 0 格（写 1）；第 2 轮能填第 1 格（$1\times1=1$）；第 3 轮能填第 2 格（$2\times1=2$）……
4. 第 $k$ 轮之后，第 $0$ 到 $k-1$ 格都填好了。把所有轮次汇总，就得到一张完整的表。


> **第 $n$ 格写第 $n+1$ 格的内容。**

谨慎的填表人从空表出发，第一轮什么也填不了，因为每个格子都依赖一个还没填的格子。第二轮、第三轮依然如此，表永远是空的。

这时有人插话："全部填 7 不就行了？第 $n$ 格是 7，第 $n+1$ 格也是 7，规则完全满足！"确实满足，全部填 42 也满足。但谨慎的填表人不会这么做，因为规则里**没有任何根据**说应该是 7。他只填被规则**逼出来**的内容。

这个类比包含了本文的全部要素：

| 类比 | 术语 | 章节 |
|---|---|---|
| 一张（可能没填完的）表 | 部分函数；域中的元素 | §5.1 |
| 空表 | 最小元 $\bot$ | §5.1 |
| "表 B 包含表 A 的所有内容，可能还多填了些" | 信息序 $A\sqsubseteq B$ | §5.1 |
| 一轮填表的规则 | 泛函 $\Phi$ | §4.1 |
| 填表填到不再变化 | 不动点 $\Phi(f)=f$ | §3.1 |
| 只填有根据的格子 | 最小不动点 | §4.3, §6 |
| 所有轮次的汇总 | 上确界 $\bigsqcup_k\Phi^k(\bot)$ | §5.2, §6 |
| 上一轮填得越多，这一轮也至少填得一样多 | 单调性（Monotonicity） | §5.3 |
| 每个格子只依赖有限多个格子 | 连续性（Continuity） | §5.3 |
| 永远空着的格子 | 非终止（Non-Termination） | §4.2 |

还有两种"坏规则"，后文会反复出现：

- **"如果整张表都填满了，就在表头写'完成'。"** 无论到了第几轮，表都没填满，这句话永远写不上去；但"所有轮次的汇总"却是满的。这条规则需要看**无穷多个格子**才能下结论，它违反了连续性（§5.3）。
- **"如果第 5 格是空的，就在第 6 格写 0。"** 一旦第 5 格后来被填上，第 6 格就得改写，违反了"只增不改"。它违反了单调性（§12.3）。

---

## 3. 什么是不动点（What Is a Fixed Point）

### 3.1 定义与例子

> **定义 3.1（不动点）**：设 $f:X\to X$。若 $x\in X$ 满足 $f(x)=x$，则称 $x$ 是 $f$ 的**不动点（Fixed Point）**。

| 函数 | 不动点 | 说明 |
|---|---|---|
| $f(x)=x^2$（实数上） | $0,\ 1$ | 两个 |
| $f(x)=x+1$（整数上） | 无 | 每次都"挪动" |
| $f(x)=x$ | 所有 $x$ | 无穷多个 |
| $f(x)=\cos x$（实数上） | 约 $0.739085$ | 恰好一个 |
| $f(S)=\{0\}\cup\{n+2\mid n\in S\}$（自然数子集上） | 偶数集，以及偶数集与任意一个对 $+2$ 封闭的集合之并……其中最小的是偶数集 | 许多个，有一个最小 |

最后一个例子已经是一个递归定义："偶数集是包含 0、并且对加 2 封闭的集合"。

一个直观的例子：把一张城市地图平铺在这座城市的地面上，地图上**恰好有一点**正好压在它所代表的那个真实位置上方。这就是 **Brouwer 不动点定理（Brouwer Fixed-Point Theorem）**（Brouwer, 1911）的一个特例。

### 3.2 四个问题

面对方程 $x=f(x)$，总是要问四个问题：

1. **存在（Existence）**：有没有解？
2. **唯一（Uniqueness）**：如果有多个，取哪个？
3. **构造（Construction）**：能不能算出来？
4. **推理（Reasoning）**：不显式求解，能否证明解具有某种性质？

不同的不动点定理在不同的前提下回答这些问题：

| 类型 | 定理 | 前提 | 结论 | 在语义学中的用途 |
|---|---|---|---|---|
| 度量型（Metric） | Banach（1922） | 完备度量空间上的**压缩映射（Contraction）** | 恰有一个不动点；从任意点迭代都收敛到它 | 度量语义、保护递归（§12.2） |
| 拓扑型（Topological） | Brouwer（1911） | 闭球到自身的连续映射 | 存在不动点（非构造性） | 较少直接使用 |
| 序型（Order-Theoretic） | Knaster–Tarski（1928/1955） | **完全格（Complete Lattice）**上的单调映射 | 不动点构成完全格，有最小与最大不动点 | 归纳定义、程序分析、余归纳（§7, §11） |
| 序型（Order-Theoretic） | Kleene | **CPO** 上的连续映射 | 最小不动点 $=\bigsqcup_n f^n(\bot)$ | 递归程序的语义（§6, §9） |

程序语义学主要使用**序型**定理。原因在于程序的计算方式：程序每运行一步，就多确定一点信息，并且已经确定的信息不会被推翻。"信息逐步增长"正是一种序结构，而计算本身并没有一个自然的"距离"。

### 3.3 一个迭代求解的例子

Banach 定理给出了一种求不动点的方法：反复代入。

```python
import math

x = 1.0
for _ in range(100):
    x = math.cos(x)
print(x)    # 0.7390851332151607，满足 cos(x) == x
```

$\cos$ 在 $[0,1]$ 上是压缩映射：$\lvert\sin x\rvert\le\sin 1<1$，并且 $\cos$ 把 $[0,1]$ 映到 $[\cos 1,1]\subseteq[0,1]$。所以无论从哪里出发，迭代都会收敛到唯一的不动点。

后文的 Kleene 定理也是"反复代入"，但有两点关键区别：起点固定为"一无所知" $\bot$；迭代不是在距离上越来越近，而是在**信息**上越来越多。

---

## 4. 递归定义：方程，而非指令（Recursive Definitions as Equations）

### 4.1 把递归定义写成不动点方程

阶乘的递归定义是

$$
\mathit{fact}(n)=\begin{cases}1 & n=0\\ n\times \mathit{fact}(n-1) & n>0\end{cases}
$$

把右边看作一个"以函数为输入、以函数为输出"的变换，即**泛函（Functional）**：

$$
\Phi(f)=\lambda n.\ \text{if } n=0 \text{ then } 1 \text{ else } n\times f(n-1)
$$

于是阶乘的定义就是方程

$$
\mathit{fact}=\Phi(\mathit{fact})
$$

**$\mathit{fact}$ 是 $\Phi$ 的不动点。** 一般地，任何递归定义 $f=\cdots f\cdots$ 都可以写成 $f=\Phi(f)$，其中 $\Phi$ 由右边的表达式得到。$\Phi$ 本身**不是递归的**，它只是一轮填表的规则：给它一张旧表 $f$，它按规则返回一张新表。

### 4.2 第一个困难：可能没有（全函数）解

考虑定义

$$
f(n)=f(n)+1
$$

如果 $f$ 是自然数上的全函数，那么对每个 $n$ 都有 $f(n)=f(n)+1$，这不可能成立。**这个方程在全函数中无解。**

但这个程序能写出来，运行时会永不停止。语义必须给它一个意义，否则"每个程序都有意义"就不成立。

出路是允许**部分函数（Partial Function）**：在某些输入上**没有定义**的函数。处处无定义的函数 $\bot=\lambda n.\ \bot$ 满足这个方程，因为两边都无定义。用填表的话说：空表也是一张表。规则"第 $n$ 格等于第 $n$ 格加 1"永远无法填任何格子，空表就是它的答案。

> **教训一：语义域必须包含"尚无信息"的元素 $\bot$，否则有些递归定义没有意义。**

### 4.3 第二个困难：可能有很多解

再看两个定义：

$$
\text{(a)}\quad f(n)=f(n)
\qquad\qquad
\text{(b)}\quad f(n)=f(n+1)
$$

- 对 (a)，**每一个**部分函数都是解。
- 对 (b)，每个常函数 $\lambda n.\,c$ 都是解，处处无定义的函数也是解。

可是对应的程序

```python
def f(n): return f(n)        # (a)
def g(n): return g(n + 1)    # (b)
```

在任何输入上都永不停止。程序的实际行为只对应其中**一个**解，即处处无定义的那个。"全填 7"虽然满足方程，却是"无中生有"：计算过程永远不会产生 7。

> **教训二：方程的解不唯一时，应该选择"信息最少"的那个，也就是只包含被方程逼出来的信息的那个。**

### 4.4 一个代码实验

把表表示为 Python 字典，键是已填的格号，值是格中的内容。缺少的键就是空格。

```python
N = 8                                # 只看前 8 格，便于演示

def Phi_fact(f):                     # 一轮填表规则；f 是上一轮的表
    g = {}
    for n in range(N):
        if n == 0:
            g[n] = 1
        elif n - 1 in f:             # 只依据上一轮已填好的格子
            g[n] = n * f[n - 1]
    return g

f = {}                               # 第 0 轮：空表，即 ⊥
for k in range(5):
    print(k, f)
    f = Phi_fact(f)
# 0 {}
# 1 {0: 1}
# 2 {0: 1, 1: 1}
# 3 {0: 1, 1: 1, 2: 2}
# 4 {0: 1, 1: 1, 2: 2, 3: 6}
```

把"一直填到不再变化"写成通用函数：

```python
def kleene(Phi, bottom):
    x = bottom
    while True:
        y = Phi(x)
        if y == x:
            return x
        x = y

print(kleene(Phi_fact, {}))
# {0: 1, 1: 1, 2: 2, 3: 6, 4: 24, 5: 120, 6: 720, 7: 5040}

def Phi_shift(f):                    # 规则 (b)：第 n 格 = 第 n+1 格
    return {n: f[n + 1] for n in range(N) if n + 1 in f}

print(kleene(Phi_shift, {}))         # {}：从空表出发，永远填不了任何格子
```

`kleene` 对 `Phi_shift` 给出空表，与程序 `g` 的行为一致。这正是第 2 节中谨慎的填表人：从空表出发，只填被逼出来的格子。

剩下的问题是：这个做法在无穷的表上是否总有意义？极限是否真是不动点？是否真是"最小"的？要回答这些问题，需要先把"信息多少"精确化。

---

## 5. 信息序与域（Information Order and Domains）

### 5.1 信息序（Information Order）

> **定义 5.1（偏序）**：**偏序集（Partially Ordered Set, Poset）** $(D,\sqsubseteq)$ 是一个集合配上一个自反、反对称、传递的二元关系。若存在元素 $\bot$ 使得对所有 $x$ 都有 $\bot\sqsubseteq x$，则称 $\bot$ 为**最小元（Bottom）**。

在语义学中，$x\sqsubseteq y$ 读作"$x$ 的信息不多于 $y$"，或"$y$ 是 $x$ 的一个**改进（Refinement）**"。它**不是**数值上的大小。

**例 1：平坦域（Flat Domain）。** 在整数集上添加一个 $\bot$，令 $x\sqsubseteq y$ 当且仅当 $x=\bot$ 或 $x=y$：

```
 ...  -2   -1    0    1    2  ...
        \    \   |   /    /
              ⊥
```

记作 $\mathbb{Z}_\bot$。一个整数类型表达式的意义，要么是"还不知道"（$\bot$），要么是某个确定的整数。不同的整数之间**不可比较**：知道答案是 3，并不比知道答案是 5 "信息更多"，二者只是不同。

**例 2：部分函数（Partial Functions）。** 从 $\mathbb{N}$ 到 $\mathbb{N}$ 的部分函数等价于全函数 $\mathbb{N}\to\mathbb{N}_\bot$，"无定义"即取值 $\bot$。按**逐点（Pointwise）**比较：

$$
f\sqsubseteq g\iff \forall n.\ f(n)\sqsubseteq g(n)
$$

也就是说，凡是 $f$ 有定义的地方，$g$ 都有定义且值相同。换成函数的图像，就是 $\mathrm{graph}(f)\subseteq\mathrm{graph}(g)$。最小元是处处无定义的函数 $\lambda n.\,\bot$。这正是填表类比中"表 $g$ 包含表 $f$ 的所有内容"。

### 5.2 链与上确界（Chains and Least Upper Bounds）

> **定义 5.2**：
> - **ω-链（ω-Chain）**：一列元素 $d_0\sqsubseteq d_1\sqsubseteq d_2\sqsubseteq\cdots$。
> - $u$ 是集合 $S$ 的**上界（Upper Bound）**：对所有 $s\in S$，$s\sqsubseteq u$。
> - **上确界（Least Upper Bound）** $\bigsqcup S$：$S$ 的上界中最小的那个（若存在）。
> - **完全偏序（Complete Partial Order, CPO）**：带最小元 $\bot$、且每条 ω-链都有上确界的偏序集。

（文献中"CPO"的定义有几种变体：只要求 ω-链完备的称为 ω-CPO，要求所有**有向集（Directed Set）**完备的称为 **dcpo**；有时也不要求最小元。本文的 CPO 统一指"带最小元的 ω-CPO"。）

一条链就是一轮轮填表的记录，上确界就是"所有轮次的汇总"。在部分函数的例子中，上确界就是所有图像的并：

$$
\Big(\bigsqcup_k f_k\Big)(n)=\begin{cases} v & \text{若某个 } f_k(n)=v\neq\bot\\ \bot & \text{若所有 } f_k(n)=\bot\end{cases}
$$

由于链是递增的，一个格子一旦在某一轮被填上，以后各轮都保持同一个值，所以这个定义是良定义的。

平坦域中的链都是**最终恒定（Eventually Constant）**的：最多从 $\bot$ 跳到某个值一次。函数空间中的链却可以严格递增无穷多次，例如阶乘的近似序列。正是后者让"无穷的极限"有了意义。

### 5.3 单调性与连续性（Monotonicity and Continuity）

> **定义 5.3**：设 $D,E$ 是 CPO，$f:D\to E$。
> - $f$ 是**单调的（Monotone）**：$x\sqsubseteq y\Rightarrow f(x)\sqsubseteq f(y)$。
> - $f$ 是**连续的（Continuous）**：$f$ 单调，并且对每条 ω-链有 $f\big(\bigsqcup_n d_n\big)=\bigsqcup_n f(d_n)$。
> - $f$ 是**严格的（Strict）**：$f(\bot)=\bot$。

**单调性的直觉**：输入的信息越多，输出的信息至少不会减少。用填表的话说：上一轮填得越多，这一轮也至少填得一样多，**已经写下的东西永远不需要擦掉**。所有可计算的函数都是单调的：程序不可能因为"知道得更多"而推翻已经给出的输出。

**连续性的直觉**：输出中的每一点有限信息，都只依赖输入中的**有限**一部分信息。所以"对极限求值"等于"对近似值分别求值后取极限"。用填表的话说：每个格子只依赖有限多个格子。

**单调但不连续的反例。** 定义 $T:(\mathbb{N}\to\mathbb{N}_\bot)\to\{\bot,\mathsf{tt}\}$（其中 $\bot\sqsubseteq\mathsf{tt}$）：

$$
T(f)=\begin{cases}\mathsf{tt} & f \text{ 是全函数}\\ \bot & \text{否则}\end{cases}
$$

$T$ 是单调的：若 $f\sqsubseteq g$ 且 $f$ 全，则 $g=f$，也是全的。但它不连续：阶乘的每个近似 $f_k$ 都不是全函数，所以 $\bigsqcup_k T(f_k)=\bot$；它们的上确界却是全函数，$T\big(\bigsqcup_k f_k\big)=\mathsf{tt}$。

这就是第 2 节的第一种坏规则："如果整张表都填满了，就在表头写'完成'"。要确认一个函数是全函数，必须检查无穷多个输入，**这样的 $T$ 是不可计算的**。连续性正是"可计算性"在序论中的影子：可计算的函数一定连续。

### 5.4 构造新的 CPO（Constructing New CPOs）

CPO 对常见的构造是封闭的：

| 构造 | 定义 | 用途 |
|---|---|---|
| 提升（Lifting） $D_\bot$ | 在 $D$ 下方添加新的 $\bot$ | 让"可能不终止的计算"有意义 |
| 积（Product） $D\times E$ | 分量逐个比较 | 多个参数、多个结果 |
| 分离和（Separated Sum） $D+E$ | 两部分并列，下方再添加 $\bot$ | 变体类型、布尔值 $\mathbb{B}_\bot$ |
| 连续函数空间 $[D\to E]$ | 所有连续函数，逐点比较；最小元 $\lambda x.\,\bot$ | 高阶函数、程序的意义 |

> **命题 5.4**：若 $D,E$ 是 CPO，则连续函数空间 $[D\to E]$ 在逐点序下也是 CPO，链的上确界逐点计算：$\big(\bigsqcup_n f_n\big)(x)=\bigsqcup_n f_n(x)$。

这条命题让我们可以在"函数的空间"里讨论"函数的链"和"函数的极限"，泛函 $\Phi$ 就是 $[D\to E]$ 上的一个映射。

---

# 第二部分：理论与方法

## 6. Kleene 不动点定理（The Kleene Fixed-Point Theorem）

### 6.1 定理与证明

> **定理 6.1（Kleene 不动点定理）**：设 $D$ 是 CPO，$\Phi:D\to D$ 连续，则
> $$
> \mathrm{fix}(\Phi)=\bigsqcup_{n\ge0}\Phi^n(\bot)
> $$
> 是 $\Phi$ 的不动点。并且它是**最小前不动点**：对任何满足 $\Phi(e)\sqsubseteq e$ 的 $e$，都有 $\mathrm{fix}(\Phi)\sqsubseteq e$。特别地，它是最小不动点。
>
> **证明**：
> 1. **这是一条链。** $\bot\sqsubseteq\Phi(\bot)$，因为 $\bot$ 是最小元。若 $\Phi^n(\bot)\sqsubseteq\Phi^{n+1}(\bot)$，由单调性有 $\Phi^{n+1}(\bot)\sqsubseteq\Phi^{n+2}(\bot)$。由数学归纳法，$\Phi^0(\bot)\sqsubseteq\Phi^1(\bot)\sqsubseteq\cdots$ 是 ω-链，它在 CPO 中有上确界，记为 $d$。
> 2. **$d$ 是不动点。** 由连续性，
> $$
> \Phi(d)=\Phi\Big(\bigsqcup_n\Phi^n(\bot)\Big)=\bigsqcup_n\Phi^{n+1}(\bot)=\bigsqcup_n\Phi^n(\bot)=d
> $$
> 倒数第二个等号成立，是因为在链的开头去掉 $\bot$ 不改变上确界。
> 3. **$d$ 是最小前不动点。** 设 $\Phi(e)\sqsubseteq e$。$\bot\sqsubseteq e$；若 $\Phi^n(\bot)\sqsubseteq e$，则 $\Phi^{n+1}(\bot)\sqsubseteq\Phi(e)\sqsubseteq e$。故 $e$ 是整条链的上界，$d\sqsubseteq e$。每个不动点都是前不动点，所以 $d$ 也是最小不动点。∎

### 6.2 三个步骤的直觉

| 证明步骤 | 用到的性质 | 填表类比 |
|---|---|---|
| ① 构成链 | 单调性 | 每一轮至少保留上一轮的内容，只增不改 |
| ② 极限是不动点 | 连续性 | 汇总表再填一轮不会多出东西，因为任何新格子只依赖有限多个旧格子，而这些旧格子早在某一轮就已经填好了 |
| ③ 最小 | $\bot$ 是最小元 + 单调性 | 任何"自洽的表"（满足规则的表）都包含谨慎填表人的每一轮成果，所以也包含它们的汇总 |

第 ③ 步是整个理论中最重要的一步。它说明最小不动点**不包含任何没有根据的信息**：只要某个信息出现在 $\mathrm{fix}(\Phi)$ 中，它就必然出现在**每一个**自洽的解中。§8 的全部推理原理都来自这一步。

### 6.3 回到 §4 的例子

| 定义 | 泛函 | Kleene 链 | 最小不动点 | 程序行为 |
|---|---|---|---|---|
| 阶乘 | $\Phi(f)(n)=$ if $n=0$ then $1$ else $n\cdot f(n-1)$ | $f_k$ 在 $0..k-1$ 上有定义 | $n!$（全函数） | 对所有 $n$ 终止 |
| $f(n)=f(n)+1$ | $\Phi(f)(n)=f(n)+1$（规定 $\bot+1=\bot$） | 恒为 $\bot$ | $\lambda n.\,\bot$ | 永不终止 |
| $f(n)=f(n)$ | $\Phi=\mathrm{id}$ | 恒为 $\bot$ | $\lambda n.\,\bot$ | 永不终止 |
| $f(n)=f(n+1)$ | $\Phi(f)(n)=f(n+1)$ | 恒为 $\bot$ | $\lambda n.\,\bot$ | 永不终止 |

每一行中，最小不动点都恰好与程序的实际行为一致。§9.4 会把这一观察提升为一个定理。

### 6.4 第 $k$ 个近似就是"最多递归 $k$ 层"

$\Phi^k(\bot)$ 有一个具体的操作含义：**它就是把递归调用展开 $k$ 层、在第 $k+1$ 层直接放弃（返回 $\bot$）所得到的函数。** 对阶乘：

$$
\Phi^3(\bot)(n)=\text{if }n=0\text{ then }1\text{ else }n\cdot\big(\text{if }n-1=0\text{ then }1\text{ else }(n-1)\cdot(\text{if }n-2=0\text{ then }1\text{ else }\bot)\big)
$$

一次真实的运行，只要在有限步内停止，就只用到了有限深度的递归，因此它的结果已经出现在某个 $\Phi^k(\bot)$ 中。不停止的运行在每一层都"还要再往下"，所以结果永远是 $\bot$。

> **不动点语义把"运行一个递归程序"理解为"计算越来越好的近似"，把"程序的意义"理解为"所有近似的极限"。**

### 6.5 Haskell 中的 `fix`

Haskell 标准库直接提供了不动点算子：

```haskell
import Data.Function (fix)          -- fix f = let x = f x in x

fact :: Integer -> Integer
fact = fix (\rec n -> if n == 0 then 1 else n * rec (n - 1))

ones :: [Integer]
ones = fix (1 :)                    -- [1,1,1,...]

loop :: a
loop = fix id                       -- ⊥：任何类型中的最小元
```

`fact` 里的 `rec` 不是对 `fact` 的引用，而是泛函的参数，即"上一轮的表"。`fix` 负责把泛函变成它的最小不动点。

`ones` 的例子值得注意。泛函是 $\Phi(xs)=1:xs$，Kleene 链是

$$
\bot\ \sqsubseteq\ 1:\bot\ \sqsubseteq\ 1:1:\bot\ \sqsubseteq\ \cdots
$$

在惰性列表的域中，这条链的上确界是**无穷列表** $[1,1,1,\dots]$。最小不动点不是"什么都没有"，而是一个无穷的对象，因为惰性列表的域本身就包含部分列表与无穷列表。**"最小"是相对于域的信息序而言的，不是"最空"的意思。**

---

## 7. Knaster–Tarski 定理与归纳定义（The Knaster–Tarski Theorem and Inductive Definitions）

### 7.1 定理与证明

> **定义 7.1**：若偏序集 $L$ 的**每个**子集都有上确界与下确界，则称 $L$ 为**完全格（Complete Lattice）**。最典型的例子是**幂集格（Powerset Lattice）** $(\mathcal{P}(U),\subseteq)$：上确界是并，下确界是交。

> **定理 7.2（Knaster–Tarski）**：设 $L$ 是完全格，$f:L\to L$ 单调。则
> $$
> \mathrm{lfp}(f)=\bigsqcap\{x\mid f(x)\sqsubseteq x\},\qquad
> \mathrm{gfp}(f)=\bigsqcup\{x\mid x\sqsubseteq f(x)\}
> $$
> 分别是 $f$ 的最小不动点与最大不动点。更进一步，$f$ 的全体不动点本身构成一个完全格（Tarski, 1955）。
>
> **证明（最小不动点）**：令 $P=\{x\mid f(x)\sqsubseteq x\}$，$m=\bigsqcap P$。
> - 对任意 $x\in P$，有 $m\sqsubseteq x$，于是 $f(m)\sqsubseteq f(x)\sqsubseteq x$。所以 $f(m)$ 是 $P$ 的下界，$f(m)\sqsubseteq m$。
> - 由单调性，$f(f(m))\sqsubseteq f(m)$，即 $f(m)\in P$，所以 $m\sqsubseteq f(m)$。
> - 二者结合得 $f(m)=m$。任何不动点都在 $P$ 中，所以 $m$ 是最小的。
>
> 最大不动点的证明是对偶的。∎

**直觉**：前不动点 $x$（$f(x)\sqsubseteq x$）是一个"足够大的猜测"：再按规则推一步，不会推出 $x$ 以外的东西。最小不动点就是所有足够大的猜测的公共部分，即"**无论怎么猜，都必然包含的内容**"。这和 Kleene 定理第 ③ 步说的是同一件事，只是换了一个角度：Kleene 从下往上逼近，Tarski 从上往下取交。

### 7.2 归纳定义就是最小不动点

**由规则定义的集合（Inductively Defined Set）**是计算机科学中最常见的定义方式。例如：

```
                  n ∈ Even
  ─────────     ──────────────
  0 ∈ Even      n + 2 ∈ Even
```

"Even 是满足这两条规则的**最小**集合"。用不动点的话说，令

$$
R(S)=\{0\}\cup\{n+2\mid n\in S\}
$$

则 $\mathrm{Even}=\mathrm{lfp}(R)$。一般地（Aczel, 1977）：

- 一组推理规则确定一个幂集上的单调算子 $R$：$R(S)$ 是"从 $S$ 出发，用一次规则能推出的全部结论"；
- **前不动点** $R(S)\subseteq S$ 就是"对规则封闭的集合"；
- 由规则**归纳定义**的集合，就是最小前不动点，也就是最小不动点 $\mathrm{lfp}(R)$。

**类型判断（Typing Judgement）**、**操作语义的求值关系（Evaluation Relation）**、**可达性（Reachability）**、语法本身（所有合法的语法树），都是这样定义的。它们都是最小不动点。

由 $\mathrm{lfp}$ 是最小前不动点，立即得到**规则归纳原理（Rule Induction）**：

> **推论 7.3**：若集合 $S$ 对规则封闭，即 $R(S)\subseteq S$，则 $\mathrm{lfp}(R)\subseteq S$。

例如，要证明"所有偶数都能被 2 整除"，只需验证"能被 2 整除的数"这个集合包含 0、并对加 2 封闭。这就是通常的结构归纳与规则归纳。

### 7.3 最大不动点与余归纳

对偶地，**最大不动点**是"所有自洽的、足够小的猜测的并"，即"**无法被反驳的一切**"。

> **推论 7.4（余归纳原理，Coinduction Principle）**：若 $S\subseteq f(S)$（$S$ 是后不动点），则 $S\subseteq\mathrm{gfp}(f)$。

要证明某个元素属于 $\mathrm{gfp}(f)$，只需找一个包含它的后不动点 $S$：$S$ 中的每个元素，经过一步观察都还落在 $S$ 中。**互模拟（Bisimulation）**就是这样定义和使用的（§11.4）。

| | 最小不动点 $\mu$ | 最大不动点 $\nu$ |
|---|---|---|
| 刻画 | 有限步能推出的东西 | 永远推不出矛盾的东西 |
| 构造 | 从 $\bot$ 往上迭代 | 从 $\top$ 往下迭代 |
| 证明原理 | 归纳：$f(S)\subseteq S\Rightarrow\mu f\subseteq S$ | 余归纳：$S\subseteq f(S)\Rightarrow S\subseteq\nu f$ |
| 典型对象 | 有限数据、可达性、终止、推导 | 无穷数据、不变性、互模拟、无穷执行 |
| 规则 $x\in S$ 当且仅当 $x\in S$ | $\emptyset$ | 全集 |

最后一行很能说明问题：对"$x$ 是 $x$"这种循环论证，归纳的回答是"推不出来，所以不成立"，余归纳的回答是"驳不倒，所以成立"。

### 7.4 Kleene 与 Tarski 的比较

| | Kleene 定理 | Knaster–Tarski 定理 |
|---|---|---|
| 空间 | CPO（只要求链有上确界） | 完全格（要求所有子集有上下确界） |
| 函数 | 连续 | 单调即可 |
| 得到 | 最小不动点 | 最小与最大不动点，以及不动点构成的完全格 |
| 构造方式 | 显式迭代 $\bigsqcup_n\Phi^n(\bot)$，ω 步 | 对所有前不动点取交，不给出算法 |
| 典型用途 | 递归函数（函数空间不是格） | 归纳 / 余归纳定义、程序分析（幂集与格） |

二者的适用场合不同。函数空间 $\mathbb{N}\to\mathbb{N}_\bot$ 不是完全格：$\lambda n.\,1$ 和 $\lambda n.\,2$ 没有上界，所以递归程序的语义用 Kleene 定理。幂集是完全格，所以归纳定义与程序分析常用 Tarski 定理。

**单调而不连续时，ω 步不一定够。** 在序 $0<1<2<\cdots<\omega<\omega+1$ 上定义 $f(n)=n+1$、$f(\omega)=\omega+1$、$f(\omega+1)=\omega+1$。$f$ 单调，Kleene 链 $0,1,2,\dots$ 的上确界是 $\omega$，但 $f(\omega)=\omega+1\neq\omega$，还需要再迭代一步。一般地，单调函数的最小不动点可以通过**超限迭代（Transfinite Iteration）**得到：在**极限序数（Limit Ordinal）**处取上确界，迭代到某个序数为止（Cousot & Cousot, 1979）。

更糟的是，在只要求 ω-链完备的序中，单调函数**可能根本没有不动点**：所有可数序数组成的集合 $\omega_1$ 中，每条可数链都有上确界，最小元是 0，$f(\alpha)=\alpha+1$ 单调，却没有不动点。这说明 Kleene 定理中的"连续"不能简单地换成"单调"。

---

## 8. 推理原理与计算律（Reasoning Principles and Calculational Laws）

不动点语义的一大好处，是不必真的算出 $\mathrm{fix}(\Phi)$，就能证明它的性质。这些原理全部来自最小性。

### 8.1 Park 归纳（Park Induction）

> **定理 8.1（Park, 1969）**：若 $\Phi(e)\sqsubseteq e$，则 $\mathrm{fix}(\Phi)\sqsubseteq e$。

这就是 Kleene 定理的第 ③ 步。它的用法是：**要证明递归定义的对象"不超过"某个规格 $e$，只需验证 $e$ 经过一轮规则后不会变大。**

**例：阶乘程序的部分正确性（Partial Correctness）。** 真正的阶乘函数 $n\mapsto n!$ 是全函数，并且满足 $\Phi(\mathit{fact})=\mathit{fact}$。由 Park 归纳，

$$
\mathrm{fix}(\Phi)\sqsubseteq\mathit{fact}
$$

按逐点序展开，就是：**只要程序在 $n$ 上有输出，输出就一定是 $n!$。** 这一步完全不需要知道程序是否终止。

**终止性（Termination）**需要另外证明：对 $n$ 归纳可知 $\Phi^{n+1}(\bot)(n)=n!\neq\bot$，所以 $\mathrm{fix}(\Phi)$ 处处有定义。部分正确性与终止性合起来，得到 $\mathrm{fix}(\Phi)=\mathit{fact}$，即**完全正确性（Total Correctness）**。

### 8.2 Scott 归纳 / 不动点归纳（Scott Induction / Fixed-Point Induction）

更一般的性质不一定能写成"$\sqsubseteq e$"的形式。这时用 **Scott 归纳（Scott Induction）**，也称**不动点归纳（Fixed-Point Induction）**（de Bakker & Scott, 1969；Park, 1969）：

> **定义 8.2**：$D$ 的子集 $P$ 称为**可容许的（Admissible）**，也称**归纳的（Inclusive）**，如果 $\bot\in P$，并且对 $P$ 中的每条 ω-链 $(d_n)$，都有 $\bigsqcup_n d_n\in P$。

> **定理 8.3（Scott 归纳）**：若 $P$ 可容许，且对所有 $x\in P$ 都有 $\Phi(x)\in P$，则 $\mathrm{fix}(\Phi)\in P$。
>
> **证明**：由数学归纳法，每个 $\Phi^n(\bot)\in P$。它们构成一条 ω-链，由可容许性，上确界 $\mathrm{fix}(\Phi)\in P$。∎

它的结构与普通数学归纳法完全平行：

| 数学归纳法 | Scott 归纳 |
|---|---|
| 基础：$P(0)$ | 基础：$P(\bot)$ |
| 步骤：$P(n)\Rightarrow P(n+1)$ | 步骤：$P(x)\Rightarrow P(\Phi(x))$ |
| 结论：对所有 $n$，$P(n)$ | **额外条件**：$P$ 对链的极限封闭；结论：$P(\mathrm{fix}\,\Phi)$ |

**例**：令 $P(f)\equiv\forall n.\ f(n)\neq\bot\Rightarrow f(n)=n!$。
- $\bot\in P$：处处无定义，前提永远不成立。
- 可容许：若链中每个 $f_k$ 都满足 $P$，且 $(\bigsqcup_k f_k)(n)=m\neq\bot$，则在平坦域中必有某个 $f_k(n)=m$，于是 $m=n!$。
- 对 $\Phi$ 封闭：$\Phi(f)(0)=1=0!$；对 $n>0$，若 $\Phi(f)(n)\neq\bot$，则 $f(n-1)\neq\bot$，从而 $\Phi(f)(n)=n\cdot(n-1)!=n!$。

所以 $\mathrm{fix}(\Phi)\in P$，与 §8.1 用 Park 归纳得到的结论相同。实际上，Park 归纳是 Scott 归纳的特例：$\{x\mid x\sqsubseteq e\}$ 总是可容许的。

### 8.3 可容许性不能省略

**反例**：令 $P(f)\equiv$"$f$ 不是全函数"。
- $\bot\in P$，因为空表显然不是全函数。
- 对阶乘的 $\Phi$ 封闭：若 $f$ 在 $m$ 处无定义，则 $\Phi(f)$ 在 $m+1$ 处无定义。

如果忽略可容许性，就会"证明"出阶乘程序不是全函数，这显然是错的。错误出在 $P$ 不可容许：每个近似都不是全函数，极限却是全函数。这与 §5.3 中不连续的 $T$ 是同一个现象：**一个性质如果要看到无穷多信息才会被打破或成立，就不能沿着近似链传递到极限。**

实用的判别法：由 $\sqsubseteq$、等式、合取、全称量词以及**连续函数**构造出的性质通常是可容许的；含否定、存在量词或"全函数""有限"这类全局性条件的性质，需要格外小心。

### 8.4 计算律（Calculational Laws）

以下等式可以直接用于程序变换与推导（设所有函数连续）：

| 名称 | 规律 | 含义 |
|---|---|---|
| 展开律（Unfolding） | $\mathrm{fix}\,f=f(\mathrm{fix}\,f)$ | 递归可以展开一层 |
| Park 律 | $f(x)\sqsubseteq x\Rightarrow\mathrm{fix}\,f\sqsubseteq x$ | 最小性（§8.1） |
| 滚动律（Rolling） | $\mathrm{fix}(f\circ g)=f(\mathrm{fix}(g\circ f))$ | 递归中的一段计算可以挪到外面 |
| 融合律（Fusion） | 若 $h$ **严格**且 $h\circ f=g\circ h$，则 $h(\mathrm{fix}\,f)=\mathrm{fix}\,g$ | 把后处理并入递归 |
| 对角律（Diagonal） | $\mathrm{fix}(\lambda x.\,f(x,x))=\mathrm{fix}(\lambda x.\,\mathrm{fix}(\lambda y.\,f(x,y)))$ | 嵌套递归可以合并 |
| Bekić 律（Bekić, 1969） | 同时递归可拆成逐个递归（见下） | 互递归的语义 |

**融合律中的严格性不能省略**：证明过程是对 $n$ 归纳 $h(f^n\bot)=g^n(\bot)$，基础情形要求 $h(\bot)=\bot$。直觉上：如果 $h$ 能"凭空"从 $\bot$ 产生信息，就会在 $\mathrm{fix}\,g$ 之外多出东西。

**Bekić 律**给出了**互递归（Mutual Recursion）**的语义。设 $f:D\times E\to D$，$g:D\times E\to E$，则同时方程 $x=f(x,y)$，$y=g(x,y)$ 的最小解为

$$
\hat x=\mathrm{fix}\big(\lambda x.\ f(x,\ \mathrm{fix}(\lambda y.\ g(x,y)))\big),\qquad
\hat y=\mathrm{fix}\big(\lambda y.\ g(\hat x,y)\big)
$$

也就是先把 $y$ 看作 $x$ 的函数解出来，代回 $x$ 的方程，再解 $x$。这让任意多个互相引用的递归定义都可以化归为单个不动点。

> **命题 8.4**：不动点算子 $\mathrm{fix}:[D\to D]\to D$ 本身是连续的。

这条看似技术性的命题保证了"$\mathrm{fix}$ 套 $\mathrm{fix}$"仍有意义，对角律和 Bekić 律都依赖它。

---

## 9. 不动点语义：方法（Fixed-Point Semantics: The Method）

### 9.1 三步法

不动点语义为带递归或循环的语言定义意义，分三步：

| 步骤 | 内容 | 填表类比 |
|---|---|---|
| ① 选域（Choose Domains） | 为每类语法选一个 CPO 作为语义域，用 $\bot$ 表示"不终止" | 决定表的格式 |
| ② 写方程（Write Equations） | 对非递归的构造直接写出意义；对递归的构造写出泛函 $\Phi$ | 写出一轮填表规则 |
| ③ 取最小不动点（Take Least Fixed Points） | 令递归构造的意义为 $\mathrm{fix}(\Phi)$；验证 $\Phi$ 连续 | 只填有根据的格子 |

第 ③ 步中的"验证连续"通常不需要逐个去做：只要泛函是由连续函数用复合、λ-抽象、条件表达式等组合而成的，它就自动连续（Winskel, 1993；Abramsky & Jung, 1994）。

### 9.2 例一：While 语言

**语法**

$$
\begin{aligned}
a &::= n \mid x \mid a_1+a_2 \mid a_1-a_2\\
b &::= \mathsf{true}\mid a_1<a_2\mid a_1\neq a_2\mid\neg b\\
c &::= \mathsf{skip}\mid x:=a\mid c_1;c_2\mid\mathsf{if}\ b\ \mathsf{then}\ c_1\ \mathsf{else}\ c_2\mid\mathsf{while}\ b\ \mathsf{do}\ c
\end{aligned}
$$

**语义域**

$$
\mathrm{State}=\mathrm{Var}\to\mathbb{Z},\qquad
\lbrack\!\lbrack a \rbrack\!\rbrack:\mathrm{State}\to\mathbb{Z},\qquad
\lbrack\!\lbrack b \rbrack\!\rbrack:\mathrm{State}\to\mathbb{B},\qquad
\lbrack\!\lbrack c \rbrack\!\rbrack:\mathrm{State}\to\mathrm{State}_\bot
$$

命令的意义是一个**可能不终止的状态变换器**：$\lbrack\!\lbrack c \rbrack\!\rbrack\mathit{st}=\bot$ 表示从状态 $\mathit{st}$ 出发，$c$ 不终止。表达式在这里总是终止，所以不需要 $\bot$。

**语义方程**

$$
\begin{aligned}
\lbrack\!\lbrack \mathsf{skip} \rbrack\!\rbrack\mathit{st} &= \mathit{st}\\
\lbrack\!\lbrack x:=a \rbrack\!\rbrack\mathit{st} &= \mathit{st}[x\mapsto\lbrack\!\lbrack a \rbrack\!\rbrack\mathit{st}]\\
\lbrack\!\lbrack c_1;c_2 \rbrack\!\rbrack\mathit{st} &= \lbrack\!\lbrack c_2 \rbrack\!\rbrack^\dagger(\lbrack\!\lbrack c_1 \rbrack\!\rbrack\mathit{st})\\
\lbrack\!\lbrack \mathsf{if}\ b\ \mathsf{then}\ c_1\ \mathsf{else}\ c_2 \rbrack\!\rbrack\mathit{st} &= \text{if }\lbrack\!\lbrack b \rbrack\!\rbrack\mathit{st}\text{ then }\lbrack\!\lbrack c_1 \rbrack\!\rbrack\mathit{st}\text{ else }\lbrack\!\lbrack c_2 \rbrack\!\rbrack\mathit{st}\\
\lbrack\!\lbrack \mathsf{while}\ b\ \mathsf{do}\ c \rbrack\!\rbrack &= \mathrm{fix}(\Phi_{b,c})
\end{aligned}
$$

其中

$$
\Phi_{b,c}(f)=\lambda\mathit{st}.\ \text{if }\lbrack\!\lbrack b \rbrack\!\rbrack\mathit{st}\text{ then }f^\dagger(\lbrack\!\lbrack c \rbrack\!\rbrack\mathit{st})\text{ else }\mathit{st}
$$

顺序组合中的 $^\dagger$ 表示**严格复合（Strict Composition）**：$c_1$ 不终止时，$c_1;c_2$ 也不终止。

**while 为什么要用不动点？** 循环满足展开等式 $\mathsf{while}\ b\ \mathsf{do}\ c\equiv\mathsf{if}\ b\ \mathsf{then}\ (c;\mathsf{while}\ b\ \mathsf{do}\ c)\ \mathsf{else}\ \mathsf{skip}$。右边又出现了循环自身，所以它的意义 $w$ 必须满足 $w=\Phi_{b,c}(w)$。这个方程可能有多个解，我们取最小的。注意 $\Phi_{b,c}$ 只依赖 $\lbrack\!\lbrack b \rbrack\!\rbrack$ 和 $\lbrack\!\lbrack c \rbrack\!\rbrack$，所以语义仍然是**组合的（Compositional）**：整体意义只由各部分的意义决定。

**为什么必须是最小的？** 考虑 $\mathsf{while}\ \mathsf{true}\ \mathsf{do}\ \mathsf{skip}$。泛函是 $\Phi(f)=\lambda\mathit{st}.\,f(\mathit{st})$，即恒等映射，**每个**状态变换器都是它的不动点。只有最小不动点 $\lambda\mathit{st}.\,\bot$ 符合"这个循环永不停止"的事实。

### 9.3 用代码观察近似链

```python
BOT = None                      # ⊥：尚无信息

def bottom(st):                 # 处处未定义的状态变换器
    return BOT

def approx(Phi, k):             # 计算 Φ^k(⊥)
    f = bottom
    for _ in range(k):
        f = Phi(f)
    return f

def while_functional(cond, body):
    """给定 ⟦b⟧ 与 ⟦c⟧，返回泛函 Φ_{b,c}"""
    def Phi(f):
        def g(st):
            if not cond(st):
                return st
            st2 = body(st)
            return BOT if st2 is BOT else f(st2)   # 严格复合 f†
        return g
    return Phi

# while x != 0 do x := x - 2
cond = lambda st: st["x"] != 0
body = lambda st: {**st, "x": st["x"] - 2}
Phi  = while_functional(cond, body)

show = lambda r: "⊥" if r is BOT else r["x"]
for k in range(6):
    f_k = approx(Phi, k)
    print(k, [show(f_k({"x": x})) for x in (0, 2, 4, 6, 5)])
# 0 ['⊥', '⊥', '⊥', '⊥', '⊥']
# 1 [0, '⊥', '⊥', '⊥', '⊥']
# 2 [0, 0, '⊥', '⊥', '⊥']
# 3 [0, 0, 0, '⊥', '⊥']
# 4 [0, 0, 0, 0, '⊥']
# 5 [0, 0, 0, 0, '⊥']
```

从 $x=6$ 出发需要循环 3 次，所以从 $\Phi^4(\bot)$ 起有了答案。从 $x=5$ 出发，$x$ 依次变为 $3,1,-1,-3,\dots$，永远不等于 0，所以无论 $k$ 多大，结果都是 $\bot$。表中每一列都是一条平坦域中的链，每一行都比上一行"多填了一格"。

**真正的 `fix`。** 上确界无法在有限时间内算完，但可以**按需展开**：

```python
def fix(Phi):
    def f(st):
        return Phi(f)(st)       # 每次调用时才展开一层
    return f

loop = fix(Phi)
print(loop({"x": 6}))           # {'x': 0}
# loop({"x": 5})                # 永不返回（在 Python 中最终抛出 RecursionError）
```

对比一个看起来更直接的写法：

```python
def fix_naive(Phi):
    return Phi(fix_naive(Phi))  # 定义时就无限递归，什么都算不出来
```

`fix_naive` 在严格求值的语言中立即无限递归，因为它试图在使用之前先算出整个极限。正确的 `fix` 把展开推迟到调用时，每次调用只展开一层。这正是 §6.4 的结论在实现上的体现：**一次终止的运行只用到有限深度的展开。** Haskell 是惰性语言，所以可以直接写 `fix f = let x = f x in x`。

### 9.4 例二：PCF 与递归函数

**PCF（Programming Computable Functions）**是 Scott（1969）与 Plotkin（1977）研究的一个带类型 λ-演算，相当于"带递归的最小函数式语言"：

$$
\begin{aligned}
\tau &::= \iota\mid o\mid\tau\to\tau\\
M &::= x\mid n\mid \mathsf{true}\mid\mathsf{false}\mid\mathsf{succ}\,M\mid\mathsf{pred}\,M\mid\mathsf{zero?}\,M\mid\mathsf{if}\ M\ \mathsf{then}\ M\ \mathsf{else}\ M\mid\lambda x{:}\tau.\,M\mid M\,M\mid\mathsf{fix}\,M
\end{aligned}
$$

其中 $\iota$ 是自然数类型，$o$ 是布尔类型。

**语义域**：$\lbrack\!\lbrack \iota \rbrack\!\rbrack=\mathbb{N}_\bot$，$\lbrack\!\lbrack o \rbrack\!\rbrack=\mathbb{B}_\bot$，$\lbrack\!\lbrack \sigma\to\tau \rbrack\!\rbrack=[\lbrack\!\lbrack \sigma \rbrack\!\rbrack\to\lbrack\!\lbrack \tau \rbrack\!\rbrack]$（连续函数空间）。这些都是 CPO（§5.4）。

**关键方程**：

$$
\lbrack\!\lbrack \mathsf{fix}\,M \rbrack\!\rbrack\rho=\mathrm{fix}(\lbrack\!\lbrack M \rbrack\!\rbrack\rho)=\bigsqcup_n(\lbrack\!\lbrack M \rbrack\!\rbrack\rho)^n(\bot)
$$

其余方程与普通的 λ-演算语义相同，$\rho$ 是变量环境。Haskell 的 `fix` 正是这个构造的直接对应。

在带类型的 λ-演算中，没有 $\mathsf{fix}$ 就写不出无限循环，因为所有程序都会终止（**强规范化，Strong Normalization**）。所以 PCF 必须把 $\mathsf{fix}$ 作为基本构造加入，它是"一般递归"的唯一来源。

### 9.5 Y 组合子

在**无类型 λ-演算（Untyped λ-Calculus）**中，不动点可以由语法构造出来：

$$
Y=\lambda f.\,(\lambda x.\,f(x\,x))\,(\lambda x.\,f(x\,x)),\qquad Y\,F=_\beta F\,(Y\,F)
$$

$Y$ 的存在说明每个 λ-项在语法上都有不动点。但"有不动点"和"有哪个不动点"是两件事。要给 $Y$ 一个指称意义，需要一个满足 $D\cong[D\to D]$ 的域（§10）。Park（1970）证明：在 Scott 的 $D_\infty$ 模型中，$Y$ 恰好被解释为最小不动点算子。这说明语法上的递归技巧，与语义上"取最小解"的选择是一致的。

### 9.6 与操作语义的联系：充分性（Adequacy）

不动点语义是否"正确"，需要与程序的实际执行比对。程序的执行由**操作语义（Operational Semantics）**描述，记 $M\Downarrow v$ 表示"程序 $M$ 求值得到值 $v$"。

> **定理 9.1（计算充分性，Computational Adequacy；Plotkin, 1977）**：对 PCF 中基类型的封闭项 $M$ 和值 $v$，
> $$
> \lbrack\!\lbrack M \rbrack\!\rbrack=\lbrack\!\lbrack v \rbrack\!\rbrack\neq\bot\iff M\Downarrow v
> $$
> 特别地，$\lbrack\!\lbrack M \rbrack\!\rbrack=\bot$ 当且仅当 $M$ 不终止。

它的两个方向分别用到不动点理论的两面：

- **"$\Leftarrow$"（可靠性，Soundness）**：对求值推导归纳，每一步求值都保持意义不变。$\mathsf{fix}$ 的求值规则 $\mathsf{fix}\,M\to M\,(\mathsf{fix}\,M)$ 对应展开律 $\mathrm{fix}\,f=f(\mathrm{fix}\,f)$。
- **"$\Rightarrow$"**：若意义不是 $\bot$，由 Kleene 定理，它在某个有限近似 $\Phi^k(\bot)$ 处就已经出现，而 $\Phi^k(\bot)$ 对应"最多展开 $k$ 层"的程序，这个程序可以被证明真的会求值出结果。这一方向通常需要借助**逻辑关系（Logical Relations）**，证明中的关键性质恰好是可容许性（§8.2）。

**充分性正是"取最小不动点"的最终理由**：最小不动点不多不少，恰好记录了程序实际计算出来的东西。如果取更大的不动点，`while true do skip` 就会被赋予某个确定的结果，与执行不符。

**完全抽象（Full Abstraction）**是一个更强的要求：语义相等当且仅当两个程序在所有上下文中都不可区分。Scott 模型对 PCF **不是**完全抽象的，原因是模型中包含一个 PCF 无法定义的函数，即**并行或（Parallel Or）**：只要任何一个参数为真就返回真，即使另一个参数不终止（Plotkin, 1977）。在 PCF 中加入并行或之后，Scott 模型就是完全抽象的。为原本的 PCF 构造完全抽象模型，直到**博弈语义（Game Semantics）**才得到解决（Abramsky, Jagadeesan & Malacaria, 2000；Hyland & Ong, 2000）。

---

# 第三部分：进阶

> 本部分数学门槛较高，首次阅读可以跳过，直接阅读 §13。

## 10. 递归域方程（Recursive Domain Equations）

### 10.1 问题：在类型层面求不动点

到目前为止，不动点都是在一个**固定的**域中求**元素**。但很多语言需要在**域本身**的层面求解方程：

| 语言特性 | 域方程 |
|---|---|
| 无类型 λ-演算 | $D\cong[D\to D]$ |
| 惰性列表 | $L\cong(1+A\times L)_\bot$ |
| 带过程的命令式语言 | $\mathrm{Val}\cong\mathbb{Z}+[\mathrm{Val}\to\mathrm{Val}_\bot]$ |
| 递归类型 `data T = T (T -> Int)` | $T\cong[T\to\mathbb{Z}_\bot]$ |

这些方程的右边都包含未知的域本身，所以它们是"域上的不动点方程"。

### 10.2 集合中无解

在集合中，方程 $D\cong D^D$ 只有平凡解：若 $\lvert D\rvert\ge2$，则 $\lvert D^D\rvert\ge2^{\lvert D\rvert}>\lvert D\rvert$，这是 **Cantor 定理（Cantor's Theorem）**的直接推论。所以"每个函数都能当作值"的模型，在集合论里根本不存在。

Scott 的洞见在于：**只取连续函数。** 连续函数由它在"有限信息"上的行为完全确定，所以比任意函数"少得多"，基数论证不再适用。

### 10.3 逆极限构造（Inverse Limit Construction）

> **定理 10.1（Scott, 1969/1972）**：存在一个非平凡的 CPO $D_\infty$，满足 $D_\infty\cong[D_\infty\to D_\infty]$。

构造的思路与 Kleene 定理如出一辙，只是对象从"元素"换成了"域"：

1. 从一个简单的域 $D_0$ 出发，令 $D_{n+1}=[D_n\to D_n]$。
2. 在相邻的域之间建立**嵌入-投影对（Embedding-Projection Pair）** $(e_n,p_n)$：$e_n:D_n\to D_{n+1}$ 把小域嵌入大域，$p_n:D_{n+1}\to D_n$ 把大域投影回小域，满足 $p_n\circ e_n=\mathrm{id}$ 和 $e_n\circ p_n\sqsubseteq\mathrm{id}$。也就是说，嵌入不丢信息，投影只丢信息、不造信息。
3. 令 $D_\infty$ 为所有"协调的序列"组成的域：$D_\infty=\{(x_n)_{n}\mid x_n\in D_n,\ p_n(x_{n+1})=x_n\}$。每个元素就是一列越来越精细的近似。

$D_n$ 可以理解为"最多考察 $n$ 层函数调用"所能区分出的行为，$D_\infty$ 是它们的极限。

### 10.4 范畴论的一般方法

Smyth 与 Plotkin（1982）把上述构造推广为一般方法：

- 把域方程 $D\cong F(D)$ 看作作用在 CPO 范畴上的**函子（Functor）** $F$ 的不动点方程；
- 对 $F$ 中逆变出现的位置（如函数空间的定义域），使用形如 $F:\mathbf{CPO}^{op}\times\mathbf{CPO}\to\mathbf{CPO}$ 的**混合变异函子（Mixed-Variance Functor）**；
- 在嵌入-投影对构成的范畴中，若 $F$ 是**局部连续的（Locally Continuous）**，则链 $1\to F1\to F^21\to\cdots$ 的**余极限（Colimit）**就是方程的解。

这条链与 Kleene 链 $\bot\sqsubseteq\Phi(\bot)\sqsubseteq\Phi^2(\bot)\sqsubseteq\cdots$ 是同一个模式，只是提升到了范畴的层面。

所得的解 $D$ 及同构 $i:F(D,D)\to D$ 还满足**最小不变性（Minimal Invariance）**（Freyd, 1991；Pitts, 1996）：

$$
\mathrm{id}_D=\mathrm{fix}\big(\lambda e.\ i\circ F(e,e)\circ i^{-1}\big)
$$

它说的是：恒等映射是"按 $F$ 的结构逐层复制"这一泛函的**最小**不动点，即 $D$ 中没有任何"不能由有限次展开逼近"的多余元素。这是域层面的"只填有根据的格子"，也是对递归类型做归纳推理的基础。Pitts（1996）由此导出了针对递归域的关系推理原理。

---

## 11. 应用：程序分析、逻辑与验证（Applications: Analysis, Logic and Verification）

### 11.1 数据流分析与抽象解释（Dataflow Analysis and Abstract Interpretation）

静态分析要回答"程序运行到某一点时，变量可能取哪些值"这类问题。对带循环的程序，每个程序点的信息依赖于循环回来的信息，这又是一个不动点方程。

- **数据流分析（Dataflow Analysis）**（Kildall, 1973；Kam & Ullman, 1977）：在每个程序点放一个**格（Lattice）**中的元素，例如"可能已定义的变量集合"，每条语句对应一个单调的**转移函数（Transfer Function）**。分析结果是整个方程组的最小不动点，用**工作表算法（Worklist Algorithm）**迭代求得。格的高度有限时，迭代必然终止。
- **抽象解释（Abstract Interpretation）**（Cousot & Cousot, 1977）：程序的具体语义是某个最小不动点 $\mathrm{lfp}(F)$；在**抽象域（Abstract Domain）**中求一个"覆盖"它的不动点，即可得到可靠的近似。

**格的高度无穷时怎么办？** 以区间分析为例：

```python
INF = float("inf")
BOT = None                                  # 空区间：这个程序点还没被到达

def join(a, b):                             # 区间的并（取包络）
    if a is BOT: return b
    if b is BOT: return a
    return (min(a[0], b[0]), max(a[1], b[1]))

def widen(a, b):                            # 加宽算子 a ▽ b
    if a is BOT: return b
    if b is BOT: return a
    lo = a[0] if b[0] >= a[0] else -INF     # 下界还在变小：直接推到 -∞
    hi = a[1] if b[1] <= a[1] else INF      # 上界还在变大：直接推到 +∞
    return (lo, hi)

def guard_lt(a, c):                         # a ∩ (-∞, c-1]，即条件 i < c
    if a is BOT or a[0] > c - 1: return BOT
    return (a[0], min(a[1], c - 1))

def add(a, k):
    return BOT if a is BOT else (a[0] + k, a[1] + k)

# 程序：i = 0; while i < 100: i = i + 1
# 循环头处 i 的取值范围 X 满足方程  X = [0,0] ⊔ ((X ∩ (-∞,99]) + 1)
F = lambda X: join((0, 0), add(guard_lt(X, 100), 1))

def iterate(F, step, x=BOT):
    rounds = 0
    while True:
        y = step(x, F(x))
        rounds += 1
        if y == x:
            return x, rounds
        x = y

print(iterate(F, lambda x, y: y))   # ((0, 100), 102)：Kleene 迭代，约一百轮
print(iterate(F, widen))            # ((0, inf), 3)：加宽，三轮即止
X = (0, INF)
print(F(X))                         # (0, 100)：再做一步收窄（Narrowing）
```

- 纯 Kleene 迭代得到精确结果 $[0,100]$，但轮数与循环次数成正比。如果条件是 `while True`，迭代将永不终止。
- **加宽（Widening）**算子 $\triangledown$ 在发现某个界还在变化时，直接把它推到无穷，从而保证有限步内停止。得到的 $[0,+\infty]$ 是一个**前不动点**：$F([0,+\infty])=[0,100]\sqsubseteq[0,+\infty]$。由 Tarski 定理，最小不动点包含在每一个前不动点中，所以这个结果是**可靠的过近似（Sound Over-Approximation）**。
- **收窄（Narrowing）**从前不动点出发再迭代 $F$，可以在不失可靠性的前提下恢复精度，这里一步就回到了 $[0,100]$（Cousot & Cousot, 1992）。

这个例子同时展示了 Tarski 定理的两种用法：最小不动点是"真值"，任何前不动点都是它的可靠上界。

### 11.2 逻辑程序与 Datalog（Logic Programs and Datalog）

逻辑程序

```
path(X, Y) :- edge(X, Y).
path(X, Z) :- edge(X, Y), path(Y, Z).
```

的语义由**直接后承算子（Immediate Consequence Operator）** $T_P$ 给出：$T_P(I)$ 是"由当前已知事实 $I$ 和每条规则推一步所得的全部事实"。van Emden 与 Kowalski（1976）证明，对不含否定的**确定子句程序（Definite Clause Program）**，$T_P$ 连续，程序的**最小 Herbrand 模型（Least Herbrand Model）**恰为

$$
\mathrm{lfp}(T_P)=\bigsqcup_n T_P^n(\emptyset)
$$

并且它与逻辑推导所得的结论完全一致。Datalog 数据库的**朴素求值（Naive Evaluation）**就是这条 Kleene 链：

```python
def lfp(F, bottom):
    x = bottom
    while (y := F(x)) != x:
        x = y
    return x

edge = {(1, 2), (2, 3), (3, 4)}
T = lambda P: edge | {(x, z) for (x, y) in edge for (y2, z) in P if y == y2}
print(sorted(lfp(T, set())))
# [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
```

工业界的**半朴素求值（Semi-Naive Evaluation）**每轮只用"上一轮新增的事实"推导，避免重复计算，但得到的仍是同一个最小不动点。

### 11.3 μ-演算与模型检测（The μ-Calculus and Model Checking）

**模态 μ-演算（Modal μ-Calculus）**（Kozen, 1983）把最小与最大不动点直接写进逻辑公式。在一个**转移系统（Transition System）**上，令 $\Diamond X$ 表示"存在一个后继在 $X$ 中"，$\Box X$ 表示"所有后继都在 $X$ 中"：

| 性质 | 自然语言 | μ-演算公式 | 不动点 |
|---|---|---|---|
| 可达（$\mathsf{EF}\,p$） | 存在一条路径，最终到达 $p$ | $\mu X.\ p\vee\Diamond X$ | 最小：必须在有限步内找到见证 |
| 不变（$\mathsf{AG}\,p$） | 所有路径上，$p$ 始终成立 | $\nu X.\ p\wedge\Box X$ | 最大：永远找不到反例即可 |

```python
def gfp(F, top):
    x = top
    while (y := F(x)) != x:
        x = y
    return x

succ  = {1: {2}, 2: {3}, 3: {2}, 4: {4}, 5: {1, 4}}
nodes = set(succ)
dia = lambda X: {v for v in nodes if succ[v] & X}    # ◇X：存在后继在 X 中
box = lambda X: {v for v in nodes if succ[v] <= X}   # □X：所有后继都在 X 中

EF = lfp(lambda X: {3} | dia(X), set())              # 能到达状态 3
AG = gfp(lambda X: {1, 2, 3, 5} & box(X), nodes)     # 永远不进入状态 4
print(EF, AG)   # {1, 2, 3, 5} {1, 2, 3}
```

状态 5 能到达 3（经过 1），但它有一个后继是 4，所以不满足"永远不进入 4"。

一般规律是：**活性（Liveness）**性质，即"好事终将发生"，用 $\mu$；**安全性（Safety）**性质，即"坏事永不发生"，用 $\nu$。μ 与 ν 交替嵌套可以表达更复杂的性质，例如"无穷多次经过某状态"，但模型检测的复杂度也随交替深度增加（Emerson & Lei, 1986）。

### 11.4 互模拟与余归纳（Bisimulation and Coinduction）

两个进程"行为相同"，是指它们能做同样的动作，并且做完之后仍然行为相同。这又是一个自我指涉的定义。Park（1981）与 Milner（1989）把它定义为一个最大不动点：设关系上的算子

$$
B(R)=\{(p,q)\mid \forall p\xrightarrow{a}p'.\ \exists q\xrightarrow{a}q'.\ (p',q')\in R,\ \text{且反之亦然}\}
$$

则**互模拟等价（Bisimilarity）** $\sim\ =\nu B$。由余归纳原理（推论 7.4），要证明 $p\sim q$，只需构造一个包含 $(p,q)$ 的关系 $R$，满足 $R\subseteq B(R)$，即一个**互模拟（Bisimulation）**。这里必须用最大不动点：两个都永远做动作 $a$ 的进程应当被视为等价，而最小不动点无法在有限步内"证明"这一点。Sangiorgi（2009）对这一概念的历史有详细考证。

### 11.5 Kahn 进程网络（Kahn Process Networks）

Kahn（1974）把确定性的并发进程网络建模为**流（Stream）**上的方程组：每个通道的历史是一条有限或无限的流，按**前缀序（Prefix Order）**排序，每个进程是从输入流到输出流的连续函数。网络的行为是整个方程组的最小不动点。前缀序上"信息越多 = 流越长"，连续性对应"输出的每个前缀只依赖输入的有限前缀"，也就是**因果性（Causality）**。这是不动点语义在并发领域最早、也最优雅的应用之一。

---

## 12. 推广与边界（Generalisations and Boundaries）

### 12.1 与初始代数的统一（Unification with Initial Algebras）

把偏序集 $(P,\sqsubseteq)$ 看作一个**范畴（Category）**：对象是元素，从 $x$ 到 $y$ 有唯一一个态射当且仅当 $x\sqsubseteq y$。这时，单调函数就是**函子（Functor）**，而初始代数理论中的各个概念恰好退化为本文的概念：

| 初始代数理论 | 偏序集中的特例 | 本文对应 |
|---|---|---|
| F-代数 $FA\to A$ | 前不动点 $f(x)\sqsubseteq x$ | 对规则封闭的集合（§7.2） |
| 初始代数 $\mu F$ | 最小前不动点 | $\mathrm{lfp}(f)$ |
| Lambek 引理：$F(\mu F)\cong\mu F$ | 最小前不动点是不动点 | Tarski 定理证明的后半（§7.1） |
| Adámek 链 $0\to F0\to F^20\to\cdots$ | Kleene 链 $\bot\sqsubseteq f(\bot)\sqsubseteq\cdots$ | Kleene 定理（§6.1） |
| 下态射的存在与唯一 | $f(x)\sqsubseteq x\Rightarrow\mathrm{lfp}(f)\sqsubseteq x$ | Park 归纳（§8.1） |
| "无冗余"（No Junk） | 最小不动点中没有无根据的元素 | 只填有根据的格子 |
| F-余代数 $A\to FA$ | 后不动点 $x\sqsubseteq f(x)$ | 互模拟（§11.4） |
| 终余代数 $\nu F$ 与上态射 | 最大后不动点与余归纳原理 | $\mathrm{gfp}(f)$（§7.3） |

换句话说，**初始代数就是"范畴化的最小不动点"**。在偏序集中，从 $\mu f$ 到 $x$ 的态射"唯一"是自动的，所以只剩下"存在"，即 Park 归纳；在一般范畴中，态射可以有很多，"唯一"就变成了一个有实质内容的条件，它给出了 fold 和结构归纳。§10.4 的 Smyth–Plotkin 构造则是两者的交汇：在域的范畴中求函子的不动点。

### 12.2 度量方法与保护递归（Metric Methods and Guarded Recursion）

序型不动点给出"最小解"，度量型不动点给出"唯一解"。后者在以下场合很有用：

- **度量语义（Metric Semantics）**（de Bakker & Zucker, 1982；America & Rutten, 1989）：把进程的行为空间配上度量，两个行为"在越晚的时刻才出现区别，距离就越近"。**保护的（Guarded）**递归定义，即每次递归调用前都至少执行一个动作，对应压缩映射，由 Banach 定理有唯一解，无需选择"最小"。
- **保护递归（Guarded Recursion）**（Nakano, 2000；Birkedal et al., 2012）：在类型系统中加入"稍后（Later）"模态 $\triangleright$。类型为 $\triangleright A\to A$ 的函数总有唯一不动点，因为递归调用只能在"一步之后"使用自身。

**例**：流方程 `ones = 1 : ones` 是保护的，递归出现在构造子 `:` 之后，所以有唯一解；`xs = xs` 不是保护的，它的解不唯一，序型方法给出 $\bot$。

与之相关的**步数索引（Step-Indexing）**技术（Appel & McAllester, 2001）用"剩余步数"作为近似的层级，在操作语义上实现了与 Kleene 链类似的逐层逼近，是现代程序逻辑（如 Iris）处理递归类型与高阶状态的基础。

### 12.3 非单调的情形（Non-Monotone Operators）

不动点理论的核心前提是单调性。一旦违反，存在性与最小性都会失效。逻辑程序中的**否定（Negation）**是典型例子：

```
p :- not q.
q :- not p.
r :- not r.
```

规则"若 $q$ 不成立，则 $p$ 成立"中，已知的事实越多，能推出的结论反而可能越少，$T_P$ 不再单调。第一组规则有两个"自洽解" $\{p\}$ 和 $\{q\}$，但没有最小的；第三条规则在二值意义下根本没有自洽的解。

对此有几种处理方式：

- **分层（Stratification）**（Apt, Blair & Walker, 1988）：如果否定只作用于"更低层"已经算完的谓词，就逐层求最小不动点，每一层内部仍然单调。
- **稳定模型（Stable Models）**（Gelfond & Lifschitz, 1988）：接受多个解，或无解。这是**回答集编程（Answer Set Programming）**的基础。
- **良基语义（Well-Founded Semantics）**（Van Gelder, Ross & Schlipf, 1991）：引入第三个真值"未知"，在三值的信息序下重新获得单调性，取唯一的最小解。上面的 $p,q,r$ 在良基语义下都是"未知"。

良基语义的做法再一次说明了本文的主题：**扩充信息序、引入"未知"，单调性就回来了，最小不动点也就回来了。**这和 §4.2 引入 $\bot$ 是同一个思路。

### 12.4 类型论中的不动点（Fixed Points in Type Theory）

在依赖类型的证明助手（Coq/Rocq、Agda、Lean）中，"类型即命题"，一个类型有元素即表示对应的命题成立。如果允许不受限制的 $\mathsf{fix}:(A\to A)\to A$，那么 $\mathsf{fix}\,\mathrm{id}$ 就是**任意**类型的元素，包括"假"这个命题，逻辑因此不一致。

所以这些系统只允许**结构递归（Structural Recursion）**，即对初始代数的 fold（见《初始代数与初始代数语义》），或经过终止性检查的递归。一般递归需要显式地引入"可能不终止"：

- **部分性单子（Partiality Monad）**（Capretta, 2005）：用余归纳类型表示"可能需要无穷多步的计算"；
- **Bove–Capretta 方法**（Bove & Capretta, 2005）：把终止性条件作为一个归纳谓词，与函数一起定义。

这与本文的主线一致：$\bot$ 必须**显式地**出现在类型中，不动点才是安全的。

---

## 13. 常见误解与总结（Common Misconceptions and Summary）

### 13.1 八个常见误解

**误解一："最小不动点就是数值最小的那个解。"**
不是。"最小"是在**信息序**中最小，而不是数值最小。`ones = 1 : ones` 的最小不动点是无穷列表（§6.5）；在平坦域中，3 和 5 根本不可比较（§5.1）。

**误解二："$\bot$ 就是错误。"**
不是。错误（如除零）是一个可以检测、可以处理的普通值；$\bot$ 是"尚无任何信息"，无法在有限时间内与"还在计算"区分开来。

**误解三："不动点语义描述的是程序一层层展开的过程。"**
不完全对。意义是近似链的**极限**，是一个数学对象。近似 $\Phi^k(\bot)$ 与"最多递归 $k$ 层"的执行一一对应（§6.4），但语义本身并不规定执行步骤，执行步骤由操作语义规定，二者由充分性定理联系（§9.6）。

**误解四："递归方程的解是唯一的。"**
不是。方程可能无解（在全函数中），也可能有无穷多解（§4.2、§4.3）。"取最小解"是一个选择，它的正当性来自充分性定理。

**误解五："只要函数单调，就有 $\mathrm{lfp}=\bigsqcup_n f^n(\bot)$。"**
不是。ω 步迭代需要**连续性**。单调而不连续时，可能需要超限迭代；在仅 ω-完备的序中，单调函数甚至可能没有不动点（§7.4）。

**误解六："Scott 归纳对任何性质都成立。"**
不是。性质必须**可容许**，否则会"证明"出错误结论，例如"阶乘程序不是全函数"（§8.3）。

**误解七："Y 组合子定义了递归的语义。"**
不是。$Y$ 是语法上的构造，它保证不动点存在于语法中；它在模型中代表**哪一个**不动点，由语义决定。在 Scott 的 $D_\infty$ 中它恰好是最小不动点（§9.5）。

**误解八："能写出 `fix`，就能安全地使用它。"**
在程序语言中可以，因为语义域中有 $\bot$。在把类型当命题的系统中不行，`fix id` 会证明任何命题（§12.4）。

### 13.2 术语总表：从直觉到定义

| 术语 | English | 一句话直觉 | 形式对应 | 章节 |
|---|---|---|---|---|
| 不动点 | Fixed Point | 规则作用后不再变化的东西 | $f(x)=x$ | §3.1 |
| 泛函 | Functional | 一轮填表的规则 | $\Phi:[D\to E]\to[D\to E]$ | §4.1 |
| 信息序 | Information Order | 表 B 包含表 A 的全部内容 | $\sqsubseteq$ | §5.1 |
| 最小元 | Bottom | 空表，一无所知 | $\bot$ | §5.1 |
| 平坦域 | Flat Domain | 要么不知道，要么知道确切答案 | $\mathbb{Z}_\bot$ | §5.1 |
| 上确界 | Least Upper Bound | 所有轮次的汇总 | $\bigsqcup$ | §5.2 |
| 完全偏序 | CPO | 每条链都有汇总的空间 | 带 $\bot$ 的 ω-CPO | §5.2 |
| 单调 | Monotone | 只增不改 | $x\sqsubseteq y\Rightarrow f(x)\sqsubseteq f(y)$ | §5.3 |
| 连续 | Continuous | 每个格子只依赖有限多个格子 | 保持链的上确界 | §5.3 |
| 最小不动点 | Least Fixed Point | 只填有根据的格子 | $\mathrm{fix}\,\Phi=\bigsqcup_n\Phi^n(\bot)$ | §6 |
| 前不动点 | Pre-Fixed Point | 一个"足够大的猜测" | $f(x)\sqsubseteq x$ | §7.1 |
| 最大不动点 | Greatest Fixed Point | 驳不倒的一切 | $\mathrm{gfp}\,f$ | §7.3 |
| Park 归纳 | Park Induction | 最小解不超过任何自洽的规格 | $f(e)\sqsubseteq e\Rightarrow\mathrm{fix}\,f\sqsubseteq e$ | §8.1 |
| 可容许性质 | Admissible Predicate | 能从近似传递到极限的性质 | 含 $\bot$、对链上确界封闭 | §8.2 |
| Scott 归纳 | Scott Induction | 对近似链做数学归纳 | 定理 8.3 | §8.2 |
| 充分性 | Adequacy | 语义恰好记录实际计算出的结果 | $\lbrack\!\lbrack M \rbrack\!\rbrack=\lbrack\!\lbrack v \rbrack\!\rbrack\neq\bot\iff M\Downarrow v$ | §9.6 |
| 递归域方程 | Recursive Domain Equation | 在"表的格式"层面求不动点 | $D\cong F(D)$ | §10 |
| 加宽 | Widening | 迭代太慢就大胆跳到一个可靠的上界 | $\triangledown$ | §11.1 |

### 13.3 结论

不动点与不动点语义的关系可以概括为一句话：**不动点理论提供了"最小解存在、可逼近、可推理"这一数学事实，不动点语义则把这一事实用作给递归赋予意义的方法。**

$$
\underbrace{x=\Phi(x)}_{\text{递归定义：方程}}
\ \xrightarrow{\ \text{Kleene / Tarski：在信息序中取最小解}\ }\
\underbrace{\lbrack\!\lbrack \mathsf{rec} \rbrack\!\rbrack=\mathrm{fix}(\Phi)=\textstyle\bigsqcup_n\Phi^n(\bot)}_{\text{不动点语义：意义}}
$$

最小不动点的三个性质，分别对应语义学的三项基本要求：

| 性质 | 理论来源 | 语义学要求 | 填表类比 |
|---|---|---|---|
| 存在性（Existence） | Kleene / Tarski 定理 | 每个递归定义都有意义（Well-Definedness） | 总能得到一张汇总表 |
| 最小性（Leastness） | 最小前不动点；Park 归纳 | 不擅自补充信息，可做部分正确性推理（Reasoning） | 只填有根据的格子 |
| 可逼近性（Approximability） | 连续性；Kleene 链；Scott 归纳 | 语义与有限执行一致（Adequacy） | 第 $k$ 轮的表 = 最多递归 $k$ 层 |

从 Knaster 与 Tarski 的格论、Kleene 的递归论，到 Scott 与 Strachey 的指称语义，再到抽象解释、Datalog、μ-演算、互模拟以及保护递归，"取最小（或最大）不动点"始终是处理"自我指涉"的核心工具。它与初始代数理论共享同一个结构：初始代数是范畴化的最小不动点，终余代数是范畴化的最大不动点（§12.1）。两者共同构成了程序语义学处理递归与无穷的数学基础。

最后，把开头那句话再读一遍，此时其中每个词都应该有了着落：

> **递归定义不是一条"去执行"的指令，而是一个"答案必须满足"的方程。方程可能无解，也可能有很多解；不动点语义规定：取那个只包含"有限步就能确定的信息"的解。它就是从"一无所知"出发、一轮轮补充信息所逼近的极限，即最小不动点。**

---

## 参考文献（References）

正文按"作者, 年份"引用，以下按第一作者姓氏字母排序。

1. Abramsky, S., Jagadeesan, R., Malacaria, P. *Full Abstraction for PCF*. Information and Computation, 163(2), 2000.
2. Abramsky, S., Jung, A. *Domain Theory*. In Handbook of Logic in Computer Science, Vol. 3, Oxford University Press, 1994.
3. Aczel, P. *An Introduction to Inductive Definitions*. In Handbook of Mathematical Logic, North-Holland, 1977.
4. America, P., Rutten, J. *Solving Reflexive Domain Equations in a Category of Complete Metric Spaces*. Journal of Computer and System Sciences, 39(3), 1989.
5. Appel, A. W., McAllester, D. *An Indexed Model of Recursive Types for Foundational Proof-Carrying Code*. ACM TOPLAS, 23(5), 2001.
6. Apt, K. R., Blair, H. A., Walker, A. *Towards a Theory of Declarative Knowledge*. In Foundations of Deductive Databases and Logic Programming, Morgan Kaufmann, 1988.
7. de Bakker, J. W., Scott, D. *A Theory of Programs*. Unpublished notes, IBM Seminar, Vienna, 1969.
8. de Bakker, J. W., Zucker, J. I. *Processes and the Denotational Semantics of Concurrency*. Information and Control, 54(1/2), 1982.
9. Banach, S. *Sur les opérations dans les ensembles abstraits et leur application aux équations intégrales*. Fundamenta Mathematicae, 3, 1922.
10. Bekić, H. *Definable Operations in General Algebras, and the Theory of Automata and Flowcharts*. IBM Laboratory Vienna, 1969. Reprinted in Programming Languages and Their Definition, LNCS 177, 1984.
11. Birkedal, L., Møgelberg, R. E., Schwinghammer, J., Støvring, K. *First Steps in Synthetic Guarded Domain Theory: Step-Indexing in the Topos of Trees*. Logical Methods in Computer Science, 8(4), 2012.
12. Bove, A., Capretta, V. *Modelling General Recursion in Type Theory*. Mathematical Structures in Computer Science, 15(4), 2005.
13. Brouwer, L. E. J. *Über Abbildung von Mannigfaltigkeiten*. Mathematische Annalen, 71, 1911.
14. Capretta, V. *General Recursion via Coinductive Types*. Logical Methods in Computer Science, 1(2), 2005.
15. Cousot, P., Cousot, R. *Abstract Interpretation: A Unified Lattice Model for Static Analysis of Programs by Construction or Approximation of Fixpoints*. POPL, 1977.
16. Cousot, P., Cousot, R. *Constructive Versions of Tarski's Fixed Point Theorems*. Pacific Journal of Mathematics, 82(1), 1979.
17. Cousot, P., Cousot, R. *Comparing the Galois Connection and Widening/Narrowing Approaches to Abstract Interpretation*. PLILP, LNCS 631, 1992.
18. Davey, B. A., Priestley, H. A. *Introduction to Lattices and Order*. 2nd ed., Cambridge University Press, 2002.
19. Emerson, E. A., Lei, C.-L. *Efficient Model Checking in Fragments of the Propositional Mu-Calculus*. LICS, 1986.
20. van Emden, M. H., Kowalski, R. A. *The Semantics of Predicate Logic as a Programming Language*. Journal of the ACM, 23(4), 1976.
21. Freyd, P. *Algebraically Complete Categories*. In Category Theory (Como 1990), LNM 1488, Springer, 1991.
22. Gelfond, M., Lifschitz, V. *The Stable Model Semantics for Logic Programming*. ICLP/SLP, 1988.
23. Gunter, C. A. *Semantics of Programming Languages: Structures and Techniques*. MIT Press, 1992.
24. Hyland, J. M. E., Ong, C.-H. L. *On Full Abstraction for PCF*. Information and Computation, 163(2), 2000.
25. Kahn, G. *The Semantics of a Simple Language for Parallel Programming*. IFIP Congress, 1974.
26. Kam, J. B., Ullman, J. D. *Monotone Data Flow Analysis Frameworks*. Acta Informatica, 7, 1977.
27. Kildall, G. A. *A Unified Approach to Global Program Optimization*. POPL, 1973.
28. Kleene, S. C. *Introduction to Metamathematics*. North-Holland, 1952.
29. Knaster, B. *Un théorème sur les fonctions d'ensembles*. Annales de la Société Polonaise de Mathématique, 6, 1928.
30. Kozen, D. *Results on the Propositional μ-Calculus*. Theoretical Computer Science, 27(3), 1983.
31. Lassez, J.-L., Nguyen, V. L., Sonenberg, E. A. *Fixed Point Theorems and Semantics: A Folk Tale*. Information Processing Letters, 14(3), 1982.
32. Milner, R. *Fully Abstract Models of Typed λ-Calculi*. Theoretical Computer Science, 4(1), 1977.
33. Milner, R. *Communication and Concurrency*. Prentice Hall, 1989.
34. Nakano, H. *A Modality for Recursion*. LICS, 2000.
35. Nielson, F., Nielson, H. R., Hankin, C. *Principles of Program Analysis*. Springer, 1999.
36. Nielson, H. R., Nielson, F. *Semantics with Applications: An Appetizer*. Springer, 2007.
37. Park, D. *Fixpoint Induction and Proofs of Program Properties*. Machine Intelligence 5, Edinburgh University Press, 1969.
38. Park, D. *The Y-Combinator in Scott's Lambda-Calculus Models*. Theory of Computation Report 13, University of Warwick, 1970.
39. Park, D. *Concurrency and Automata on Infinite Sequences*. 5th GI-Conference on Theoretical Computer Science, LNCS 104, 1981.
40. Pitts, A. M. *Relational Properties of Domains*. Information and Computation, 127(2), 1996.
41. Plotkin, G. D. *LCF Considered as a Programming Language*. Theoretical Computer Science, 5(3), 1977.
42. Sangiorgi, D. *On the Origins of Bisimulation and Coinduction*. ACM TOPLAS, 31(4), 2009.
43. Scott, D. *A Type-Theoretical Alternative to ISWIM, CUCH, OWHY*. Manuscript, 1969. Published in Theoretical Computer Science, 121, 1993.
44. Scott, D. *Outline of a Mathematical Theory of Computation*. Proceedings of the 4th Annual Princeton Conference on Information Sciences and Systems, 1970.
45. Scott, D. *Continuous Lattices*. In Toposes, Algebraic Geometry and Logic, LNM 274, Springer, 1972.
46. Scott, D., Strachey, C. *Toward a Mathematical Semantics for Computer Languages*. Technical Monograph PRG-6, Oxford University Computing Laboratory, 1971.
47. Smyth, M. B., Plotkin, G. D. *The Category-Theoretic Solution of Recursive Domain Equations*. SIAM Journal on Computing, 11(4), 1982.
48. Stoy, J. E. *Denotational Semantics: The Scott–Strachey Approach to Programming Language Theory*. MIT Press, 1977.
49. Tarski, A. *A Lattice-Theoretical Fixpoint Theorem and Its Applications*. Pacific Journal of Mathematics, 5(2), 1955.
50. Van Gelder, A., Ross, K. A., Schlipf, J. S. *The Well-Founded Semantics for General Logic Programs*. Journal of the ACM, 38(3), 1991.
51. Winskel, G. *The Formal Semantics of Programming Languages: An Introduction*. MIT Press, 1993.

---

## 附录 A：符号表（Notation）

| 符号 | 含义 | English | 章节 |
|---|---|---|---|
| $f(x)=x$ | 不动点 | Fixed Point | §3.1 |
| $\Phi$ | 泛函 | Functional | §4.1 |
| $\sqsubseteq$ | 信息序 | Information Order | §5.1 |
| $\bot$ | 最小元（尚无信息，刻画非终止） | Bottom | §5.1 |
| $\mathbb{Z}_\bot,\ D_\bot$ | 平坦域；提升 | Flat Domain; Lifting | §5.1, §5.4 |
| $\bigsqcup,\ \bigsqcap$ | 上确界；下确界 | Least Upper Bound; Greatest Lower Bound | §5.2, §7.1 |
| $[D\to E]$ | 连续函数空间 | Continuous Function Space | §5.4 |
| $g^\dagger$ | 严格扩展 | Strict Extension | 记号约定, §9.2 |
| $\Phi^n(\bot)$ | 第 $n$ 个 Kleene 近似 | $n$-th Kleene Approximant | §6.1 |
| $\mathrm{fix}(\Phi),\ \mathrm{lfp}(f),\ \mu x.f(x)$ | 最小不动点 | Least Fixed Point | §6, §7 |
| $\mathrm{gfp}(f),\ \nu x.f(x)$ | 最大不动点 | Greatest Fixed Point | §7.3 |
| $\lbrack\!\lbrack-\rbrack\!\rbrack$ | 意义函数 | Meaning Function | §9 |
| $\mathit{st}$ | 程序状态 | Program State | §9.2 |
| $\rho$ | 变量环境 | Environment | §9.4 |
| $M\Downarrow v$ | 操作语义中的求值 | Evaluation | §9.6 |
| $D_\infty$ | Scott 的逆极限模型 | Scott's Inverse Limit Model | §10.3 |
| $(e_n,p_n)$ | 嵌入-投影对 | Embedding-Projection Pair | §10.3 |
| $\triangledown$ | 加宽算子 | Widening Operator | §11.1 |
| $T_P$ | 直接后承算子 | Immediate Consequence Operator | §11.2 |
| $\Diamond,\ \Box$ | 存在后继 / 所有后继模态 | Diamond / Box Modalities | §11.3 |
| $\sim$ | 互模拟等价 | Bisimilarity | §11.4 |
| $\triangleright$ | "稍后"模态 | Later Modality | §12.2 |

---

## 附录 B：术语对照表（Glossary）

### B.1 序论与域论

| 中文 | English | 中文 | English |
|---|---|---|---|
| 偏序集 | Partially Ordered Set (Poset) | 信息序 | Information Order |
| 最小元 / 最大元 | Bottom / Top | 平坦域 | Flat Domain |
| ω-链 | ω-Chain | 有向集 | Directed Set |
| 上界 / 上确界 | Upper Bound / Least Upper Bound | 下确界 | Greatest Lower Bound |
| 完全偏序 | Complete Partial Order (CPO) | 有向完备偏序 | dcpo |
| 完全格 | Complete Lattice | 幂集格 | Powerset Lattice |
| 单调 | Monotone | 连续 | Continuous |
| 严格 | Strict | 逐点序 | Pointwise Order |
| 提升 | Lifting | 分离和 | Separated Sum |
| 连续函数空间 | Continuous Function Space | 前缀序 | Prefix Order |
| 域 | Domain | 域论 | Domain Theory |

### B.2 不动点理论

| 中文 | English | 中文 | English |
|---|---|---|---|
| 不动点 | Fixed Point | 泛函 | Functional |
| 最小 / 最大不动点 | Least / Greatest Fixed Point | 前 / 后不动点 | Pre- / Post-Fixed Point |
| Kleene 不动点定理 | Kleene Fixed-Point Theorem | 第一递归定理 | First Recursion Theorem |
| Knaster–Tarski 定理 | Knaster–Tarski Theorem | Banach 不动点定理 | Banach Fixed-Point Theorem |
| Brouwer 不动点定理 | Brouwer Fixed-Point Theorem | 压缩映射 | Contraction Mapping |
| 超限迭代 | Transfinite Iteration | 极限序数 | Limit Ordinal |
| Park 归纳 | Park Induction | Scott 归纳 / 不动点归纳 | Scott / Fixed-Point Induction |
| 可容许 / 归纳的 | Admissible / Inclusive | 规则归纳 | Rule Induction |
| 归纳定义 | Inductive Definition | 余归纳 | Coinduction |
| 展开律 / 滚动律 | Unfolding / Rolling Rule | 融合律 / 对角律 | Fusion / Diagonal Rule |
| Bekić 律 | Bekić's Theorem | 互递归 | Mutual Recursion |

### B.3 语义学

| 中文 | English | 中文 | English |
|---|---|---|---|
| 不动点语义 | Fixed-Point Semantics | 指称语义 | Denotational Semantics |
| 操作语义 | Operational Semantics | 组合性 | Compositionality |
| 状态变换器 | State Transformer | 严格复合 | Strict Composition |
| 部分函数 | Partial Function | 非终止 | Non-Termination |
| 部分正确性 | Partial Correctness | 完全正确性 | Total Correctness |
| 计算充分性 | Computational Adequacy | 完全抽象 | Full Abstraction |
| 并行或 | Parallel Or | 博弈语义 | Game Semantics |
| 逻辑关系 | Logical Relations | 强规范化 | Strong Normalization |
| Y 组合子 | Y Combinator | 无类型 λ-演算 | Untyped λ-Calculus |
| 递归域方程 | Recursive Domain Equation | 逆极限 | Inverse Limit |
| 嵌入-投影对 | Embedding-Projection Pair | 混合变异函子 | Mixed-Variance Functor |
| 局部连续函子 | Locally Continuous Functor | 最小不变性 | Minimal Invariance |

### B.4 应用

| 中文 | English | 中文 | English |
|---|---|---|---|
| 数据流分析 | Dataflow Analysis | 转移函数 | Transfer Function |
| 工作表算法 | Worklist Algorithm | 抽象解释 | Abstract Interpretation |
| 加宽 / 收窄 | Widening / Narrowing | 可靠的过近似 | Sound Over-Approximation |
| 直接后承算子 | Immediate Consequence Operator | 最小 Herbrand 模型 | Least Herbrand Model |
| 朴素 / 半朴素求值 | Naive / Semi-Naive Evaluation | 确定子句程序 | Definite Clause Program |
| 模态 μ-演算 | Modal μ-Calculus | 模型检测 | Model Checking |
| 活性 / 安全性 | Liveness / Safety | 互模拟 | Bisimulation |
| Kahn 进程网络 | Kahn Process Network | 因果性 | Causality |
| 度量语义 | Metric Semantics | 保护递归 | Guarded Recursion |
| 步数索引 | Step-Indexing | 部分性单子 | Partiality Monad |
| 分层 | Stratification | 稳定模型 | Stable Model |
| 良基语义 | Well-Founded Semantics | 回答集编程 | Answer Set Programming |

---

## 附录 C：与《初始代数与初始代数语义》的对应（Correspondence with *Initial Algebras and Initial Algebra Semantics*）

本文与《初始代数与初始代数语义：从直觉到理论》是姊妹篇。前者回答"如何按语法结构组织语义"，后者回答"如何解出语义中的递归方程"。下表供同时阅读两篇的读者对照：

| 《初始代数》章节 | 内容 | 本文对应章节 |
|---|---|---|
| §5 初始性；§6.8 结构归纳 | 唯一同态；归纳原理 | §7.2 规则归纳；§8.1 Park 归纳；§12.1 统一 |
| §6.6 Lambek 引理 | $\mathrm{in}$ 是同构，$\mu F\cong F(\mu F)$ | §7.1 Tarski 证明的后半；§12.1 |
| §6.7 融合律 | fold 融合 | §8.4 不动点融合（需要严格性） |
| §8.5 非终止与不动点 | while 的意义是页内的不动点 | §9.2 While 语言的完整不动点语义 |
| §8.6 连续代数 | 在 $CT_\Sigma$ 中求语法展开的不动点 | §6.4 近似即有限展开；§10.4 |
| §8.7 与指称语义的联系 | Scott–Strachey 风格 | §9 全节 |
| §9.4 初始 / 终语义 | "能证明才相同"与"观察不出差别就相同" | §7.3 最小与最大不动点 |
| §10.2 Adámek 定理 | $0\to F0\to F^20\to\cdots$ 的余极限 | §6.1 Kleene 链；§10.4 Smyth–Plotkin 构造 |
| §10.3–§10.5 终余代数与余归纳 | 观察、互模拟 | §7.3 余归纳原理；§11.4 互模拟 |
| §10.6 代数紧致性 | $\mathbf{CPO}_\bot$ 中 $\mu F\cong\nu F$；hylo 的最小解 | §6.5 惰性列表的最小不动点是无穷列表；§10 |
| §11.4 依赖类型中的消去规则 | 结构递归 | §12.4 不受限的 `fix` 导致逻辑不一致 |

两篇的核心关系可以用一句话概括：**初始代数是范畴化的最小不动点，Park 归纳是"唯一同态"在偏序中的影子；而不动点语义中"取最小解"的选择，与初始代数中"无冗余"的要求，是同一个思想在两个层面的体现。**