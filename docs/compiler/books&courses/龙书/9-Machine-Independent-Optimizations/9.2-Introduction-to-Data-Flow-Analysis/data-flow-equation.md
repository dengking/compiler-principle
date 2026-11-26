# 数据流方程（Data-Flow Equations）

## 零、一句话

> **数据流方程 = 把"每个程序点上的事实"当未知数，把 CFG 的结构翻译成一组联立方程；解不是算出来的，是取不动点取出来的。**

$$\boxed{\;\text{IN}[B]=\bigsqcup_{P\in\mathrm{pred}(B)}\text{OUT}[P],\qquad \text{OUT}[B]=f_B\big(\text{IN}[B]\big)\;}$$

上一节说"程序点是方程组的下标"，这一节就是把那组方程完整写出来。

---

## 一、标准形式：四条方程

一个前向分析的全部内容就是下面四行：

$$
\begin{aligned}
&\text{(1) 边界}\quad && \text{IN}[\text{ENTRY}]=\iota\\
&\text{(2) 汇合}\quad && \text{IN}[B]=\bigsqcup_{P\in\mathrm{pred}(B)}\text{OUT}[P] && (B\neq\text{ENTRY})\\
&\text{(3) 转移}\quad && \text{OUT}[B]=f_B(\text{IN}[B])\\
&\text{(4) 块内}\quad && f_B=f_{s_n}\circ\cdots\circ f_{s_2}\circ f_{s_1}
\end{aligned}
$$

每一行都对应上一节的一个概念：

| 方程 | 管什么 | 对应的结构 |
|---|---|---|
| (1) | 起点 | ENTRY 这个人造程序点 |
| (2) | **图的形状** | 汇合点 —— $\sqcup$ 唯一登场处，**唯一的精度损失点** |
| (3) | **语句的语义** | 语句 = 边，$f$ 住在边上 |
| (4) | 块内无分叉 | 纯函数复合，无 $\sqcup$，无损失 |

> **分工要记牢：$\sqcup$ 只知道图，$f$ 只知道语义，两者完全正交。** 换一种分析 = 换 $(L,\sqcup,f)$，方程的骨架 (1)(2)(3) 一字不改。这就是"数据流框架"能被抽象成一个库的原因。

若以**语句**为粒度，方程写成

$$\text{OUT}[s]=f_s(\text{IN}[s]),\qquad \text{IN}[s]=\bigsqcup_{s'\in\mathrm{pred}(s)}\text{OUT}[s']$$

块级形式只是把块内那一串复合成 $f_B$ 的**工程优化**（未知量少一个数量级，且因为块内没有 $\sqcup$ 所以不损失任何精度）。

---

## 二、⭐ 为什么是"方程"，不是"定义"

无环时，这组式子可以按拓扑序**从左到右直接代入**求值，根本不需要"方程"这个词。

一旦有循环，就出现**自我引用**：

```
        ENTRY
          │
         B1                    IN[B2] = OUT[B1] ⊔ OUT[B3]
          │                    OUT[B2] = f₂(IN[B2])
          ▼                    IN[B3] = OUT[B2]
     ┌── B2 ◀──┐               OUT[B3] = f₃(IN[B3])
     │    │    │
     │   B3 ───┘               ⇒ IN[B2] = OUT[B1] ⊔ f₃(f₂(IN[B2]))
     ▼                                    ╰───── 自己依赖自己 ─────╯
   EXIT
```

**$\text{IN}[B_2]$ 出现在自己的定义右边。** 这不是可以求值的表达式，是一个方程。

所以整组方程的真身是：把所有未知数打包成一个向量 $X\in L^{\text{Points}}$，得到一个**单个函数**

$$F:L^{\text{Points}}\to L^{\text{Points}},\qquad F(X)(p)=\begin{cases}\iota & p=\text{ENTRY}\\[2pt]\displaystyle\bigsqcup_{q\xrightarrow{\,s\,}p}f_s\big(X(q)\big)&\text{否则}\end{cases}$$

**数据流方程组 $\;\Longleftrightarrow\;$ 求 $X=F(X)$，即 $F$ 的不动点。**

到这里，你前面所有的积累全部接上了：$L^{\text{Points}}$ 是乘积格（仍是完备格），$F$ 单调，于是 Knaster–Tarski 保证不动点存在，Kleene 迭代给出算法。**和 $\varepsilon$-闭包、子集构造是同一台机器，只是换了格和算子。**

---

## 三、框架四元组

龙书把一个分析抽象成 $(D,V,\wedge,F)$，用现代记号是 $(\text{dir},L,\sqcup,\mathcal F)$：

| 成分 | 内容 | 约束 |
|---|---|---|
| **方向** dir | forward / backward | 决定方程用 pred 还是 succ |
| **值域** $L$ | 半格（通常只需 join-semilattice + $\bot$） | ⭐ **有限高度 / ACC**，否则不收敛 |
| **汇合算子** $\sqcup$ | 幂等、交换、结合 | 由 $L$ 的序唯一确定 |
| **转移函数族** $\mathcal F$ | $\{f_s\}$ | ⭐ **单调**（必需）；**分配**（可选，换精度）；含 $\mathrm{id}$；对 $\circ$ 封闭 |

三条要求的地位完全不同：

- **单调性**是**正确性**的前提（保证迭代序列是链，且 lfp 是安全的）。
- **有限高度**是**终止性**的前提（回忆：**有 $\top$ 不等于会收敛**，区间格有 $\top$ 但高度无穷，必须 widening）。
- **分配性**是**精度**的分水岭（Kildall，见第八节）。

> 注意 $\mathcal F$ 要求含恒等、对复合封闭：前者用于"空边/ε 边"，后者用于把块内复合成 $f_B$。

---

## 四、四象限：前向/后向 × may/must

方向和 may/must 是**两个独立的维度**，交叉出四个经典分析：

| | **may**（$\sqcup=\cup$，"某条路径上成立"） | **must**（$\sqcup=\cap$，"所有路径上都成立"） |
|---|---|---|
| **前向** | **到达定值** Reaching Definitions | **可用表达式** Available Expressions |
| **后向** | **活跃变量** Live Variables | **忙碌表达式** Very Busy / Anticipated |

完整方程：

### ① 到达定值（前向 + may）
$$\text{OUT}[\text{ENTRY}]=\varnothing,\qquad
\text{IN}[B]=\bigcup_{P\in\mathrm{pred}(B)}\text{OUT}[P],\qquad
\text{OUT}[B]=\mathrm{gen}_B\cup(\text{IN}[B]\setminus \mathrm{kill}_B)$$
格：$2^{\text{Defs}}$，$\bot=\varnothing$。

### ② 活跃变量（后向 + may）
$$\text{IN}[\text{EXIT}]=\varnothing,\qquad
\text{OUT}[B]=\bigcup_{S\in\mathrm{succ}(B)}\text{IN}[S],\qquad
\text{IN}[B]=\mathrm{use}_B\cup(\text{OUT}[B]\setminus \mathrm{def}_B)$$
格：$2^{\text{Vars}}$，$\bot=\varnothing$。

### ③ 可用表达式（前向 + must）
$$\text{OUT}[\text{ENTRY}]=\varnothing,\qquad
\text{IN}[B]=\bigcap_{P\in\mathrm{pred}(B)}\text{OUT}[P],\qquad
\text{OUT}[B]=\mathrm{egen}_B\cup(\text{IN}[B]\setminus \mathrm{ekill}_B)$$
格：$(2^{\text{Exprs}},\supseteq)$ ⭐ **序是反的**，$\bot=U$（全集）。

### ④ 忙碌表达式（后向 + must）
$$\text{IN}[\text{EXIT}]=\varnothing,\qquad
\text{OUT}[B]=\bigcap_{S\in\mathrm{succ}(B)}\text{IN}[S],\qquad
\text{IN}[B]=\mathrm{egen}_B\cup(\text{OUT}[B]\setminus \mathrm{ekill}_B)$$

**四者的转移函数长得一模一样**，全是 $f(X)=\mathrm{gen}\cup(X\setminus \mathrm{kill})$。差别只在**方向**和**汇合算子**。

> ⭐ 注意 must 分析里 $\sqcup=\cap$ 这件事。这不是笔误：**join 永远是"汇合处的保守合并"，而在可用表达式里，保守 = 说得更少 = 交集**。于是格的序必须翻转成 $\supseteq$，$\bot$ 变成全集 $U$。
>
> 这正是我们之前反复提醒的"**先问哪头是不知道**"：可用表达式里，$\bot=U$ 表示"乐观地假设一切都可用"，是迭代的起点，不是答案。

---

## 五、gen/kill：位向量框架，以及它为什么"好"

$$f(X)=\mathrm{gen}\cup(X\setminus \mathrm{kill})$$

**这个形式有四条极好的性质**，也正是四大经典分析都长这样的原因：

**1. 对 $\circ$ 封闭**（可以把整块折叠成一个 $f_B$）：
$$f_2\circ f_1(X)=\mathrm{gen}_2\cup\big((\mathrm{gen}_1\cup(X\setminus \mathrm{kill}_1))\setminus \mathrm{kill}_2\big)
=\underbrace{\big(\mathrm{gen}_2\cup(\mathrm{gen}_1\setminus \mathrm{kill}_2)\big)}_{\mathrm{gen}}\cup\Big(X\setminus\underbrace{(\mathrm{kill}_1\cup \mathrm{kill}_2)}_{\mathrm{kill}}\Big)$$

**2. 分配** ⇒ **MFP = MOP**，迭代解就是最优解：
$$f(X\cup Y)=\mathrm{gen}\cup((X\cup Y)\setminus \mathrm{kill})=f(X)\cup f(Y)\;\checkmark$$
（对 $\cap$ 同样分配。）

**3. 位向量实现**：$f(X)=\texttt{gen | (x \& \textasciitilde kill)}$，一条指令处理 64 个事实。这就是"bit-vector framework"这个名字的由来。

**4. 快速收敛**：用逆后序（RPO）遍历，$d+2$ 趟内收敛（$d$ = 循环嵌套深度，Kam–Ullman）。

> ⚠️ **反面**：常量传播、指针分析、区间分析的转移函数都**不是** gen/kill 形式，因此**不分配**（$f(x,y)=x+y$ 就是经典反例），只能得到 $\text{MFP}\sqsupseteq\text{MOP}$。gen/kill 是幸运的特例，不是通例。

---

## 六、⚠️ 边界条件与初始化：最经典的 bug

方程组里有两种"初始值"，**它们是不同的东西，混淆会直接出错**：

| | 用在哪 | 取什么 | 含义 |
|---|---|---|---|
| **边界条件 $\iota$** | 只在 ENTRY（或 EXIT） | 分析特定的具体值 | 真实的先验事实 |
| **初始化值** | 所有**其他**程序点 | $\bot$（框架格的底） | 迭代起点，会被覆盖 |

对四大分析：

| 分析 | $\iota$（边界） | $\bot$（内部初始化） |
|---|---|---|
| 到达定值 | $\varnothing$ | $\varnothing$ |
| 活跃变量 | $\varnothing$ | $\varnothing$ |
| **可用表达式** | $\varnothing$ | ⭐ **$U$（全集）** |
| **忙碌表达式** | $\varnothing$ | ⭐ **$U$（全集）** |

**注意 must 分析的两个值不同**：ENTRY 处真的什么都不可用（$\varnothing$），但内部点必须初始化为 $U$。

### 为什么？看一个最小例子

```
   ENTRY ──▶ B1: t = a+b ──▶ B2 ──┐
                              ▲    │  (B2 自环)
                              └────┘
```

方程：$\text{IN}[B_2]=\text{OUT}[B_1]\cap\text{OUT}[B_2]=\{a{+}b\}\cap \text{IN}[B_2]$

记 $X=\text{IN}[B_2]$，方程是 $X=\{a{+}b\}\cap X$。**两个解**：

- $X=\{a{+}b\}$ ← 正确（$a{+}b$ 在到达 $B_2$ 的每条路径上都算过）
- $X=\varnothing$ ← 也是不动点，但**丢掉了一个可优化的机会**

| 初始化 | 迭代结果 | 评价 |
|---|---|---|
| $\bot=U=\{a{+}b\}$ | $\{a{+}b\}$ ✅ | 正确、最精确 |
| $\varnothing$ | $\varnothing$ ❌ | 仍然 sound，但**循环里所有公共子表达式全部丢失** |

> ⭐ **口诀：must 分析要"乐观地从全集出发，被证据一点点打掉"。**
> 初始化成 $\varnothing$ 不会出错误代码（结果仍然安全），但会**静悄悄地让循环里的 CSE/PRE 全部失效**——这是编译器里最难发现的一类性能 bug，因为程序跑得对，只是慢。

---

## 七、解的存在性与唯一性

**存在性**：$L^{\text{Points}}$ 完备 + $F$ 单调 ⇒ Knaster–Tarski 保证不动点存在，且不动点集本身是完备格。

**唯一性：不成立。** 上一节的例子就有两个解。有环 ⇒ 一般有多个。

所以"数据流方程的解"这个说法是不完整的，必须说清要哪一个：

$$\text{我们要的是}\quad \mathrm{lfp}\,F=\bigsqcup_{n\ge 0}F^n(\bot)$$

- **Tarski 读法**：最小的**前不动点**，$\mathrm{lfp}\,F=\bigsqcap\{X\mid F(X)\sqsubseteq X\}$。
- **Kleene 读法**：从 $\bot$ 迭代到稳定 —— 这就是算法。
- **为什么 lfp 不是 gfp**：和你 `demo_epsilon_lfp()` 里那个 $\varepsilon$ 自环的理由**一模一样**——更高的不动点允许循环"自我供养"，把没有真实有限执行轨迹支持的事实论证成立。lfp 只承认有**有限证明树**（= 真实路径前缀）的事实。

> ⚠️ 别被"可用表达式要取最大集合"绕晕：在它的格里序是 $\supseteq$，最大的集合正是 $\bot$ 方向，所以**仍然是 lfp**。**把格的方向摆对，四大分析就统一成"求 lfp、从 $\bot$ 迭代"。** 这是选择这套方向约定的全部好处。
>
> 龙书用 meet $\wedge$ 和 **MFP（Maximum FixedPoint）** 是完全对偶的写法，指同一个东西。读文献时先确认：**汇合算子叫什么？$\bot$ 是哪头？**

### 顺带：方程 vs 不等式

很多论文写**约束（不等式）**而不是方程：

$$\text{IN}[B]\;\sqsupseteq\;f_P(\text{IN}[P])\quad\text{对每条边 }P\to B$$

由 Tarski，**不等式组的最小解 = 方程组的最小解 = $\mathrm{lfp}\,F$**。两种写法完全等价，不等式形式在描述"来自多处的约束"时更自然（集合约束、类型推断常用）。

---

## 八、解方程：迭代算法 = 混沌迭代

⭐ **方程和算法是两回事**：方程**规定**答案是什么（$\mathrm{lfp}$），算法**计算**它。

```python
# 朴素迭代（round-robin）
for p in points: X[p] = ⊥
X[entry] = ι
while changed:
    for p in points (按某个顺序):       # ← 顺序只影响速度，不影响结果
        X[p] = ⊔ { f_s(X[q]) : q --s--> p }

# worklist（混沌迭代 / semi-naive）
work = deque(all points)
while work:
    p = work.popleft()
    new = ⊔ { f_s(X[q]) : q --s--> p }
    if new != X[p]:
        X[p] = new
        work.extend(succ(p))            # ← 只重算受影响的点
```

**这和你写的 `epsilon_closure`、`determinize` 是字面意义上的同一个循环**——只推进"新变化的"，这就是 Datalog 里的 semi-naive evaluation。

### 三个性质

| 性质 | 理由 |
|---|---|
| **结果与顺序无关** | 混沌迭代定理：任何公平的更新顺序都收敛到同一个 $\mathrm{lfp}$ |
| **终止** | $L^{\text{Points}}$ 有限高度 $=\vert\text{Points}\vert\times \text{height}(L)$ |
| **复杂度** | 最坏 $O(\vert E\vert\times \text{height}(L))$ 次转移函数求值 |

### 顺序影响速度（很大）

| 分析方向 | 推荐顺序 | 效果 |
|---|---|---|
| 前向 | **逆后序 RPO**（近似拓扑序） | 位向量框架 $d+2$ 趟收敛 |
| 后向 | 后序（RPO on reverse CFG） | 同上 |

$d$ = **loop connectedness**（任一无环路径上后向边的最大数目），实践中 $\le 3$。**所以"迭代几趟就好"是遍历顺序的功劳，不是格白送的。**

---

## 九、方程的解有多好：MFP vs MOP vs IDEAL

$$\underbrace{\mathrm{IDEAL}}_{\text{只沿可执行路径}}\ \sqsubseteq\ \underbrace{\mathrm{MOP}}_{\text{所有图路径}}\ \sqsubseteq\ \underbrace{\mathrm{MFP}}_{\textbf{方程的解}}$$

（$\sqsubseteq$ = "更精确"；越往右越保守。**注意：方程解在最右边，是三者中最保守的。**）

$$\mathrm{MOP}[p]=\bigsqcup_{\text{路径 }P:\,\text{entry}\to p} f_P(\iota)$$

MOP **先沿每条路径独立走完，最后才 join**；MFP **在每个汇合点就 join**。差别只在"何时 join"。

> ⭐ **Kildall / Kam–Ullman 定理**
> - 所有 $f_s$ **分配** $\Rightarrow$ $\mathrm{MFP}=\mathrm{MOP}$（方程的解是最优的）
> - 仅**单调** $\Rightarrow$ $\mathrm{MFP}\sqsupseteq\mathrm{MOP}$（安全但可能更松）

而 MOP 本身**不可计算**（路径无穷多），MFP 可计算。**数据流方程的全部价值，就是用一个可算的 lfp 去逼近一个不可算的 MOP；而分配性决定这个逼近是否无损。**

```c
if (c) { x=1; y=2; } else { x=2; y=1; }
z = x + y;
```
- MOP：两条路径都得 $z=3$ ✅
- MFP：汇合点提前 join 得 $x=\top,y=\top$，于是 $z=\top$ ❌

损失**精确地发生在一个汇合点上**，原因**精确地是 $+$ 不分配**。

---

## 十、代码：一个通用求解器

```python
"""dataflow.py — 数据流方程的统一求解器
   四大经典分析 = 同一组方程 + 不同的 (方向, 格, ⊔, f)
"""
from collections import deque


def solve(nodes, preds, succs, *, forward, bottom, join,
          transfer, boundary_node, boundary_value, order=None):
    """求 lfp F，其中
         IN[n]  = ⊔ OUT[p] for p in preds(n)     （forward）
         OUT[n] = f_n(IN[n])
       backward 时 IN/OUT 与 preds/succs 互换。

       bottom: 内部点的初始化值（must 分析里是全集 U！）
       boundary_value: 边界点的 ι（与 bottom 常常不同）
    """
    up, down = (preds, succs) if forward else (succs, preds)
    # A = 转移函数的输入侧，B = 输出侧
    A = {n: bottom for n in nodes}
    B = {n: bottom for n in nodes}
    A[boundary_node] = boundary_value
    B[boundary_node] = transfer[boundary_node](boundary_value)

    work = deque(order or nodes)
    n_eval = 0
    while work:                                   # ← 混沌迭代 / worklist
        n = work.popleft()
        if n != boundary_node:
            acc = bottom
            for p in up[n]:                       # ← 汇合：唯一的精度损失点
                acc = join(acc, B[p])
            A[n] = acc
        new = transfer[n](A[n]); n_eval += 1
        if new != B[n]:                           # ← 只推进有变化的
            B[n] = new
            work.extend(s for s in down[n] if s not in work)

    IN, OUT = (A, B) if forward else (B, A)
    return IN, OUT, n_eval


def genkill(gen, kill):
    """f(X) = gen ∪ (X ∖ kill) —— 位向量框架，分配 ⇒ MFP = MOP"""
    g, k = frozenset(gen), frozenset(kill)
    return lambda X: g | (X - k)


# ═════════ 示例 CFG ═════════
#   ENTRY → B1 → B2 ⇄ B3
#                 └→ B4 → EXIT
nodes = ["ENTRY", "B1", "B2", "B3", "B4", "EXIT"]
succs = {"ENTRY": ["B1"], "B1": ["B2"], "B2": ["B3", "B4"],
         "B3": ["B2"], "B4": ["EXIT"], "EXIT": []}
preds = {n: [] for n in nodes}
for u, vs in succs.items():
    for v in vs:
        preds[v].append(u)

#  B1: t = a+b      B3: s = a+b        （a、b 均未被重定义）
U = frozenset({"a+b"})
ae_tf = {"ENTRY": genkill([], []), "B1": genkill(["a+b"], []),
         "B2": genkill([], []),    "B3": genkill(["a+b"], []),
         "B4": genkill([], []),    "EXIT": genkill([], [])}

print("【可用表达式：must 分析，⊔ = ∩，⊥ = U】")
for name, bot in [("⊥ = U（正确）", U), ("⊥ = ∅（经典 bug）", frozenset())]:
    IN, OUT, k = solve(nodes, preds, succs, forward=True,
                       bottom=bot, join=lambda a, b: a & b,
                       transfer=ae_tf,
                       boundary_node="ENTRY",
                       boundary_value=frozenset())
    print(f"  {name:<18} IN[B2] = {set(IN['B2']) or '∅'}   ({k} 次 f 求值)")
print("  两者都是方程的解，但只有前者是 lfp —— 后者让循环里的 CSE 全部失效\n")

# ── 活跃变量：后向 + may ──
lv_tf = {"ENTRY": genkill([], []),
         "B1": genkill(["a", "b"], ["t"]),      # t = a+b
         "B2": genkill(["c"], []),              # if (c)
         "B3": genkill(["a", "b"], ["s"]),      # s = a+b
         "B4": genkill(["t"], []),              # use t
         "EXIT": genkill([], [])}
IN, OUT, _ = solve(nodes, succs, preds, forward=False,
                   bottom=frozenset(), join=lambda a, b: a | b,
                   transfer=lv_tf,
                   boundary_node="EXIT", boundary_value=frozenset())
print("【活跃变量：may 分析，⊔ = ∪，⊥ = ∅】")
for n in nodes:
    print(f"  IN[{n:<5}] = {sorted(IN[n]) or '∅':<20} "
          f"OUT[{n:<5}] = {sorted(OUT[n]) or '∅'}")
```

输出：

```
【可用表达式：must 分析，⊔ = ∩，⊥ = U】
  ⊥ = U（正确）        IN[B2] = {'a+b'}   (10 次 f 求值)
  ⊥ = ∅（经典 bug）    IN[B2] = ∅          (8 次 f 求值)
  两者都是方程的解，但只有前者是 lfp —— 后者让循环里的 CSE 全部失效
```

> 把 `solve` 和你上一轮的 `determinize` 并排放：**同一个 worklist，同一个"只推进变化"，同一个 lfp**。差别只有格和算子。这就是练习 #7 里"通用 lfp"的成品。

---

## 十一、坑速查

| 坑 | 后果 | 正解 |
|---|---|---|
| must 分析内部点初始化成 $\varnothing$ | 循环内优化机会全丢（程序对但慢） | $\bot=U$ |
| 把边界 $\iota$ 和内部 $\bot$ 混为一谈 | ENTRY 处凭空多出事实 | 两者分开设 |
| 转移函数只保序不单调？ | 单调是最低要求，不可省 | 检查 $X\sqsubseteq Y\Rightarrow f(X)\sqsubseteq f(Y)$ |
| 以为格有 $\top$ 就会收敛 | 区间格不停机 | 要 **ACC/有限高度**，否则 widening |
| 以为方程解唯一 | 得到 sound 但很差的解 | 明确要 **lfp**，从 $\bot$ 迭代 |
| 以为 MFP 就是真值 | 误判优化合法性 | MFP $\sqsupseteq$ MOP $\sqsupseteq$ IDEAL，三层损失 |
| 后向分析忘了翻转块内复合 | 结果完全错 | $f_B=f_{s_1}\circ\cdots\circ f_{s_n}$（反序） |
| 关键边上没处挂信息 | PRE/SSA 消除失败 | **边分裂**，造新程序点 |
| 随便选遍历顺序 | 慢数倍 | 前向用 RPO，后向用逆图 RPO |

---

## 十二、一句话总结

> **数据流方程把"程序点 → 格元素"当未知向量，用三条规则写死：边界给 $\iota$、汇合用 $\sqcup$（图的信息）、转移用 $f$（语义的信息）。有循环时它是真方程而非定义，于是整组方程坍缩成单个单调函数 $F:L^{\text{Points}}\to L^{\text{Points}}$，我们要的答案是 $\mathrm{lfp}\,F$——Knaster–Tarski 给存在性，有限高度给终止性，worklist 混沌迭代给算法，Kildall 定理给精度（分配则 MFP = MOP，否则只能保守）。**
>
> 而四大经典分析的差别，仅仅是**方向**（pred/succ）与**汇合算子**（$\cup$/$\cap$，连带把格的序和 $\bot$ 翻转）这两个旋钮——转移函数 $f(X)=\mathrm{gen}\cup(X\setminus\mathrm{kill})$ 是共用的，而它恰好分配，这就是位向量分析又快又准的全部原因。


# Data-Flow Equations 技术文档

## 1. 概述

**Data-flow equations（数据流方程）**是一组描述程序分析信息如何在控制流图中传播、合并和更新的数学方程，是编译器静态分析的基础。

典型应用包括：

- **到达定义分析（Reaching Definitions）**：某个变量定义可能到达哪些程序位置。
- **活跃变量分析（Live Variable Analysis）**：变量的当前值是否可能在后续被使用。
- **可用表达式分析（Available Expressions）**：某个表达式是否已在所有相关路径上计算，且其操作数未被修改。
- **常量传播（Constant Propagation）**：某个程序位置的变量能否确定为常量。

数据流方程通常由三部分组成：

1. **合并方程**：如何汇总不同控制流路径的信息。
2. **传递方程**：语句或基本块如何改变信息。
3. **边界条件**：程序入口或出口处已知的信息。

> 数据流方程是一种数学描述，不是一门独立的编程语言。它可以通过工作列表算法、Datalog 规则或其他分析框架实现。

---

## 2. 基础模型

### 2.1 控制流图

控制流图（Control-Flow Graph，CFG）表示为：

\[
G=(N,E)
\]

其中：

- \(N\)：基本块集合。
- \(E\)：控制流边集合。
- \((B_1,B_2)\in E\)：执行可能从 \(B_1\) 转移到 \(B_2\)。

**基本块（Basic Block）**是具有单一入口、内部没有控制流分支出口的顺序指令序列。

例如：

```text
        Entry
          |
          B1
         /  \
        B2  B3
         \  /
          B4
          |
         Exit
```

对于基本块 \(B\)：

\[
pred(B)=\{P\mid(P,B)\in E\}
\]

\[
succ(B)=\{S\mid(B,S)\in E\}
\]

分别表示其直接前驱和直接后继。

### 2.2 数据流状态

每个基本块关联两个状态：

| 符号 | 含义 |
|---|---|
| \(IN[B]\) | 进入基本块时的数据流信息 |
| \(OUT[B]\) | 离开基本块时的数据流信息 |
| \(f_B\) | 基本块的传递函数 |
| \(\operatorname{merge}\) | 控制流汇合处的合并操作 |

这些信息不一定是普通集合，也可以是：

- 变量到抽象值的映射。
- 指针到可能指向对象的关系。
- 变量的数值区间。
- 多种抽象信息的组合。

---

## 3. 数据流方程的一般形式

### 3.1 前向分析

前向分析沿程序执行方向传播信息：

\[
IN[B]
=
\operatorname{merge}
\{OUT[P]\mid P\in pred(B)\}
\]

\[
OUT[B]=f_B(IN[B])
\]

即：

```text
前驱 OUT → 当前 IN → 当前传递函数 → 当前 OUT
```

典型应用：

- 到达定义。
- 可用表达式。
- 常量传播。

### 3.2 后向分析

后向分析逆着程序执行方向传播信息：

\[
OUT[B]
=
\operatorname{merge}
\{IN[S]\mid S\in succ(B)\}
\]

\[
IN[B]=f_B(OUT[B])
\]

即：

```text
后继 IN → 当前 OUT → 当前反向传递函数 → 当前 IN
```

典型应用：

- 活跃变量。
- 非常忙表达式（Very Busy Expressions）。

这里的 \(f_B\) 表示相应分析方向上的传递函数，**后向传递函数通常不是前向函数的数学逆函数**。

---

## 4. GEN/KILL 形式

许多集合型数据流分析的传递函数可以表示为：

\[
f_B(X)=GEN[B]\cup(X-KILL[B])
\]

其中：

- \(GEN[B]\)：基本块生成的、在分析所关注边界上有效的事实。
- \(KILL[B]\)：基本块使其失效的事实。
- \(X-KILL[B]\)：移除失效事实后的输入。

对于前向分析：

\[
OUT[B]=GEN[B]\cup(IN[B]-KILL[B])
\]

对于采用此形式的后向分析：

\[
IN[B]=GEN[B]\cup(OUT[B]-KILL[B])
\]

### 示例

假设：

\[
IN[B]=\{d_1,d_2\}
\]

\[
GEN[B]=\{d_3\}
\]

\[
KILL[B]=\{d_1\}
\]

则：

\[
OUT[B]
=
\{d_3\}\cup(\{d_1,d_2\}-\{d_1\})
=
\{d_2,d_3\}
\]

**注意：GEN 不是“块中出现过的所有生成事实”。** 如果某个事实在同一个块内随后失效，它通常不应进入该块的最终 GEN 集合。

GEN/KILL 是一种常用形式，但不能直接涵盖所有分析；常量传播、区间分析等通常需要更一般的传递函数。

---

## 5. 合并操作与 May/Must 分析

### 5.1 May 分析

May 分析回答：

> 某个事实是否可能沿至少一条相关路径成立？

对于以“可能成立的事实集合”为状态的分析，通常使用并集：

\[
IN[B]
=
\bigcup_{P\in pred(B)}OUT[P]
\]

例如，到达定义分析中，只要一个定义能够从任一前驱传播过来，就需要保留它。

### 5.2 Must 分析

Must 分析回答：

> 某个事实是否沿所有相关路径都成立？

对于以“必然成立的事实集合”为状态的分析，通常使用交集：

\[
IN[B]
=
\bigcap_{P\in pred(B)}OUT[P]
\]

例如，一个表达式只有在所有相关前驱的出口处都可用，才可认为它在当前块入口处可用。

### 5.3 关于 \(\bigwedge\)、Meet 与 Join

文献中常见：

\[
IN[B]
=
\bigwedge_{P\in pred(B)}OUT[P]
\]

这里的 \(\bigwedge\) 通常表示格上的 **meet** 运算，不能脱离格的顺序定义直接理解为集合交集。

例如，对于幂集：

- 在包含序 \(\subseteq\) 下，meet 是交集，join 是并集。
- 在反向包含序 \(\supseteq\) 下，meet 是并集，join 是交集。

因此，技术文档应明确给出：

1. 分析域。
2. 偏序关系。
3. 合并操作的具体含义。

若暂时不讨论格理论，直接使用 \(\bigcup\)、\(\bigcap\) 或 \(\operatorname{merge}\) 往往更清晰。

---

## 6. 示例一：到达定义分析

### 6.1 分析目标

定义 \(d\) 到达某个程序位置，表示存在一条从该定义到该位置的控制流路径，并且沿途没有对同一变量重新赋值。

这是一个**前向 May 分析**。

### 6.2 数据流方程

\[
IN[B]
=
\bigcup_{P\in pred(B)}OUT[P]
\]

\[
OUT[B]
=
GEN[B]\cup(IN[B]-KILL[B])
\]

其中：

- \(GEN[B]\)：块内生成且能到达块出口的定义。
- \(KILL[B]\)：因块内赋值而失效的其他定义。

### 6.3 分支示例

```text
        Entry
          |
     B1: d1: x = 1
         /       \
B2: d2: x = 2   B3: skip
         \       /
      B4: use(x)
```

假设入口没有外部定义，得到：

| 基本块 | IN | GEN | KILL | OUT |
|---|---|---|---|---|
| B1 | ∅ | {d1} | {d2} | {d1} |
| B2 | {d1} | {d2} | {d1} | {d2} |
| B3 | {d1} | ∅ | ∅ | {d1} |
| B4 | {d1, d2} | ∅ | ∅ | {d1, d2} |

在 B4 入口：

\[
IN[B4]
=
OUT[B2]\cup OUT[B3]
=
\{d_1,d_2\}
\]

因此，`use(x)` 可能使用 `d1` 或 `d2` 的值。

这不是说二者同时执行，而是分析保留了来自不同路径的可能性。

---

## 7. 示例二：活跃变量分析

### 7.1 分析目标

如果一个变量的当前值可能在后续路径上被读取，并且在读取前未被重新定义，则该变量在当前位置是活跃的。

这是一个**后向 May 分析**。

### 7.2 数据流方程

\[
OUT[B]
=
\bigcup_{S\in succ(B)}IN[S]
\]

\[
IN[B]
=
USE[B]\cup(OUT[B]-DEF[B])
\]

其中：

- \(USE[B]\)：在块内任何对该变量的定义之前就被读取的变量。
- \(DEF[B]\)：块内被定义的变量。

### 7.3 示例

基本块包含：

```text
x = y + 1
```

则：

\[
USE[B]=\{y\}
\]

\[
DEF[B]=\{x\}
\]

如果：

\[
OUT[B]=\{x,z\}
\]

则：

\[
IN[B]
=
\{y\}\cup(\{x,z\}-\{x\})
=
\{y,z\}
\]

解释：

- `y` 的旧值被当前语句读取，因此入口处活跃。
- `x` 的旧值被覆盖，因此不会因出口处的新 `x` 活跃而在入口处活跃。
- `z` 没有被修改，其活跃性继续向前传播。

---

## 8. 示例三：可用表达式分析

### 8.1 分析目标

表达式 \(e\) 在某个位置可用，通常表示：

1. 沿所有相关入口路径，\(e\) 都已经被计算。
2. 从相应计算位置到当前位置，\(e\) 的操作数没有被重新定义。

这是一个**前向 Must 分析**。

### 8.2 数据流方程

\[
IN[B]
=
\bigcap_{P\in pred(B)}OUT[P]
\]

\[
OUT[B]
=
GEN[B]\cup(IN[B]-KILL[B])
\]

对于表达式 `a + b`：

- 对 `a` 或 `b` 赋值会使其失效。
- 计算 `a + b` 可能使其成为可用表达式，但必须确认其操作数随后未被修改。

例如：

```text
t = a + b
a = 0
```

块出口处不能认为原先计算的 `a + b` 仍可用于当前的 `a` 和 `b`，因此它不应属于该块出口意义上的 GEN。

类似地：

```text
a = a + b
```

虽然右侧计算了 `a + b`，但赋值更新了 `a`，该次计算结果通常不能作为赋值后表达式 `a + b` 的可用值。

实际实现还需要考虑表达式的副作用、内存别名和异常语义。

---

## 9. 边界条件与初始化

数据流方程本身不足以完整定义分析，还必须指定边界条件和初始状态。

### 9.1 边界条件

常见选择：

| 分析 | 典型边界条件 |
|---|---|
| 到达定义 | 入口为空，或包含参数、外部输入等初始定义 |
| 活跃变量 | 出口为空，或包含外部可观察的变量 |
| 可用表达式 | 程序入口没有已计算的表达式，即为空集 |

边界条件应根据分析对象确定，不能机械地全部设为空。

工程上可以增加虚拟 `Entry` 或 `Exit` 节点，使边界信息通过普通控制流边进入计算。

### 9.2 初始化方向

对于经典有限集合分析：

- **并集型 May 分析**：通常从空集开始，逐步增加事实。
- **交集型 Must 分析**：通常将非边界节点初始化为候选全集 \(U\)，逐步删除事实。

这样分别选择集合包含序下的最小或最大固定点。

例如，可用表达式分析通常采用：

\[
OUT[Entry]=\varnothing
\]

其他块初始为：

\[
OUT[B]=U
\]

然后反复应用方程。

### 9.3 不可达基本块

应明确是否分析从入口不可达的代码。

否则，不可达块中的 GEN 事实可能通过某些控制流边干扰可达位置的结果，Must 分析也可能受到不恰当前驱的影响。

常见处理方式是：

- 预先计算入口可达块，仅在可达子图上分析。
- 或在抽象域中显式区分“不可达”和“可达但没有事实”。

特别注意：

> 在许多分析中，空集合并不等价于不可达。

---

## 10. 固定点求解

### 10.1 为什么需要迭代？

CFG 中可能存在循环：

```text
B1 → B2 → B3
     ↑     |
     └─────┘
```

此时，各块的 IN 和 OUT 相互依赖，无法仅通过一次顺序遍历求出结果。

需要不断更新，直到：

\[
IN_{k+1}[B]=IN_k[B]
\]

且：

\[
OUT_{k+1}[B]=OUT_k[B]
\]

对所有基本块成立。这个稳定状态称为**固定点**。

### 10.2 工作列表算法

以前向分析为例：

```text
根据分析要求初始化 IN、OUT
设置并保持边界条件
worklist ← 所有待分析的普通基本块

while worklist 非空:
    B ← 取出一个基本块

    newIN  ← merge({OUT[P] | P ∈ pred(B)})
    newOUT ← transfer(B, newIN)

    IN[B] ← newIN

    if newOUT != OUT[B]:
        OUT[B] ← newOUT

        for S in succ(B):
            将 S 加入 worklist
```

后向分析的主要区别是：

- 从后继的 IN 计算当前 OUT。
- 当前 IN 改变时，将前驱加入工作列表。

**初始化时不能总是只把入口放入队列。** 某些基本块即使收到空输入，也可能通过 GEN 产生事实。将所有待分析块加入初始工作列表是一种稳妥实现。

### 10.3 收敛条件

常见充分条件包括：

1. 状态域具有有限高度。
2. 传递函数和合并操作具有适当的单调性。
3. 初始化使迭代沿单一方向变化。
4. 所有受影响的节点最终都会被处理。

在集合包含序下，单调性表示：

\[
X\subseteq Y
\Rightarrow
f_B(X)\subseteq f_B(Y)
\]

GEN/KILL 传递函数满足这一性质。

对于区间等可能存在无限上升链的抽象域，通常还需要 **widening（加宽）** 等机制保证终止。

---

## 11. 固定点结果与路径精度

数据流分析通常在汇合点先合并状态，再继续传播：

\[
f_B(\operatorname{merge}(X,Y))
\]

另一种概念性做法是分别沿路径传播，最后再合并：

\[
\operatorname{merge}(f_B(X),f_B(Y))
\]

如果传递函数对合并操作具有分配性：

\[
f_B(\operatorname{merge}(X,Y))
=
\operatorname{merge}(f_B(X),f_B(Y))
\]

那么在经典有限分配框架及相应边界条件下，迭代固定点解与路径合并解（MOP，Meet/merge Over all Paths）一致。

如果只有单调性而没有分配性，提前合并可能损失精度，但仍可得到保守结果。

此外，**CFG 路径不一定是真实可执行路径**。即使与 CFG 上的 MOP 一致，分析仍可能因包含不可行路径而产生额外近似。

---

## 12. 使用 Datalog 表达数据流方程

Datalog 使用关系表示事实，用递归规则表达传播，其固定点求值机制非常适合许多集合型数据流分析。

### 12.1 关系映射

| 数据流概念 | Datalog 关系 |
|---|---|
| 控制流边 | `edge(P, B)` |
| \(D\in IN[B]\) | `in(B, D)` |
| \(D\in OUT[B]\) | `out(B, D)` |
| \(D\in GEN[B]\) | `gen(B, D)` |
| \(D\in KILL[B]\) | `kill(B, D)` |

### 12.2 到达定义规则

以下使用 Soufflé 风格语法，并假设：

- 输入 CFG 已过滤不可达块。
- `gen` 和 `kill` 已经计算完成。
- `kill` 不依赖递归的 `in`、`out`。

```prolog
// 合并：来自任一前驱的定义都属于输入
in(B, D) :-
    edge(P, B),
    out(P, D).

// 生成：当前块产生的定义属于输出
out(B, D) :-
    gen(B, D).

// 保留：未被当前块消除的输入定义继续传播
out(B, D) :-
    in(B, D),
    !kill(B, D).
```

若存在入口定义，可通过虚拟入口的输出事实或额外的种子关系提供。

### 12.3 表达能力的边界

Datalog 很适合：

- 并集型传播。
- 关系连接与投影。
- 可达性和传递闭包。
- 到达定义、活跃变量、许多 points-to 分析。

需要更谨慎处理：

- 对所有前驱进行交集合并。
- 递归过程中使用否定或聚合。
- 复杂格上的状态更新。
- widening 等收敛策略。

两个固定关系的交集很容易表达，但“所有前驱都满足”的递归 Must 分析并不等价于简单的关系连接。通常需要对偶编码、专门扩展或其他求解机制。

---

## 13. 工程实现建议

### 13.1 使用位向量存储有限事实集

若候选事实全集为：

\[
U=\{d_0,d_1,\ldots,d_{n-1}\}
\]

可将集合编码为位向量：

```text
集合 {d0, d2} → 对应位为 1
```

集合运算转化为：

| 集合操作 | 位运算 |
|---|---|
| 并集 | OR |
| 交集 | AND |
| 差集 | AND NOT |

传递函数可以实现为：

```text
OUT = GEN | (IN & ~KILL)
```

补集操作应限制在有效事实位范围内。

### 13.2 改善处理顺序

常见优化包括：

- 前向分析使用 CFG 的逆后序。
- 后向分析使用反向图上的相应顺序。
- 工作列表去重。
- 按强连通分量组织循环区域。
- 只有输出状态变化时才通知依赖节点。

这些策略通常影响性能，不应改变正确实现所选取的固定点。

### 13.3 保证局部语义正确

求解器正确并不意味着分析一定正确。还需要正确建模：

- 指针写入及别名。
- 函数调用的副作用。
- 异常控制流。
- 全局变量和内存状态。
- 并发访问等语言特性。

例如，`*p = 1` 可能修改某个表达式依赖的变量；若忽略别名关系，可用表达式分析可能错误地保留该表达式。

### 13.4 测试策略

建议至少覆盖：

1. 无分支的顺序代码。
2. 分支后汇合。
3. 循环。
4. 同块内重复定义。
5. 不可达块。
6. 非空入口或出口边界。
7. 指针与函数调用副作用。

还可以在算法结束后重新应用所有方程，验证每个块均满足固定点条件。

---

## 14. 总结

数据流方程将静态分析分解为几个清晰的设计问题：

1. **分析什么事实？**——定义抽象域。
2. **向哪个方向传播？**——前向或后向。
3. **路径汇合时如何处理？**——定义合并操作。
4. **基本块如何改变信息？**——定义传递函数。
5. **边界处知道什么？**——设置边界条件。
6. **如何选择并求得结果？**——初始化并计算固定点。

最常见的前向 GEN/KILL 方程为：

\[
\boxed{
IN[B]
=
\operatorname{merge}
\{OUT[P]\mid P\in pred(B)\}
}
\]

\[
\boxed{
OUT[B]
=
GEN[B]\cup(IN[B]-KILL[B])
}
\]

理解这组方程后，可以进一步学习单调框架、抽象解释、过程间分析，以及基于 Datalog 的声明式程序分析。