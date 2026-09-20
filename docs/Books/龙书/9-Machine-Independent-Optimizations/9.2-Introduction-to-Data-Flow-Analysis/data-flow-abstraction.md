# 数据流抽象：从"一个状态"到"一集状态"

这段话（龙书 9.2.1）只有三句，但它完成了整个数据流分析中**最关键的一次概念跃迁**。而且——你会发现——它和你上一轮写的子集构造，是**字面意义上的同一个构造**。

---

## 一、逐句解剖

| 原文                                                                                  | 精确含义                                                               | 容易漏掉的点                                     |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------ |
| program state = 所有变量的值                                                              | 一个函数 $\sigma:\mathrm{Var}\to\mathrm{Val}$（store / environment）     | 完整的状态其实还含堆、pc、调用栈；龙书此处聚焦变量                 |
| **including those associated with stack frames below the top**                      | 不只是当前栈帧的局部变量，而是**整条运行时栈上所有活动记录中的变量**                               | ⭐ 这句是全段最重的一句，见第六节                          |
| a series of transformations                                                         | 执行 = 状态的一串变换                                                       | 是**确定性**的：同一个 $\sigma$ 进去，同一个 $\sigma'$ 出来 |
| each execution of a statement transforms input state → output state                 | 语句 $s$ 的指称 $[\![s]\!]:\mathrm{State}\rightharpoonup\mathrm{State}$ | **偏函数**：可能不停机、可能异常                         |
| input state 关联 **before** 的 program point，output state 关联 **after** 的 program point | **事实住在点上，变换住在语句上**                                                 | ⭐ 点 ≠ 语句，见第二节                              |

用一张图钉死：

```
        ● p₀        ← program point（事实 IN[s₁] 住这里）
        │
     [ s₁ ]         ← statement（转移函数 f_{s₁} 住这里）
        │
        ● p₁        ← 既是 OUT[s₁]，也是 IN[s₂]  —— 同一个点！
        │
     [ s₂ ]
        │
        ● p₂
```

---

## 二、program point 是"缝隙"，不是"语句"

这是初学者第一个卡点。**一个含 $n$ 条语句的基本块有 $n+1$ 个程序点**，语句之间的缝隙被**共享**：

$$
\mathrm{OUT}[s_i]=\mathrm{IN}[s_{i+1}]\qquad(\text{块内相邻})
$$

这个"共享"不是约定，而是原文第一句的直接推论：$s_i$ 之后的点和 $s_{i+1}$ 之前的点**就是同一个点**。正因如此，块内的**数据流**是纯粹的函数复合，不需要任何 join：

$$
f_B=f_{s_n}\circ\cdots\circ f_{s_2}\circ f_{s_1}
$$

**这就是"基本块"存在的全部理由**：块内无分叉无汇合 ⇒ 无 join ⇒ 无精度损失 ⇒ 可以整块打包成一个转移函数，只在块边界上存储事实。实现里只保存 $\mathrm{IN}[B],\mathrm{OUT}[B]$，块内用一次线性扫描重算。

> 类比你上一轮的代码：程序点 ↔ 自动机的**状态**；语句 ↔ **转移边**。龙书把事实挂在点上，正如你把 `frozenset` 挂在 DFA 状态上。

---

## 三、⭐ 核心跃迁：一个状态 → 一集状态（Collecting Semantics）

原文说的是**单次执行**：一个 $\sigma$ 进，一个 $\sigma'$ 出。但**编译器**面对的是**所有可能的执行**（所有输入、所有分支走法）。于是必须做一次提升：

$$
\text{具体语义 }[\![s]\!]:\mathrm{State}\rightharpoonup\mathrm{State}\quad\Longrightarrow\quad \mathrm{post}_s:2^{\mathrm{State}}\to 2^{\mathrm{State}}
$$

$$
\boxed{\ \mathrm{post}_s(\Sigma)=\{[\![s]\!]\sigma \mid \sigma\in\Sigma,\ [\![s]\!]\sigma\ \text{有定义}\}\ }
$$

**这一步不是"一种设计选择"，它是被逼出来的。** 因为 $2^{\mathrm{State}}$ 是 $\mathrm{State}$ 上的**自由完备并半格**：任何 $f:\mathrm{State}\to L$ 唯一地扩张为保并的 $\hat f(\Sigma)=\bigvee_{\sigma\in\Sigma}f(\sigma)$。

### 和你刚写的代码一模一样

| 子集构造                                          | 收集语义                                                                   |
| --------------------------------------------- | ---------------------------------------------------------------------- |
| $\delta(q,a)\subseteq Q$                      | $[\![s]\!]\sigma\in\mathrm{State}$                                     |
| $\hat\delta(S,a)=\bigcup_{q\in S}\delta(q,a)$ | $\mathrm{post}_s(\Sigma)=\bigcup_{\sigma\in\Sigma}\{[\![s]\!]\sigma\}$ |
| DFA 状态 = "NFA 现在可能在哪些状态"                      | 程序点的事实 = "运行到这里时 $\sigma$ 可能是哪些"                                       |
| $\varepsilon$-闭包 = lfp                        | 可达状态集 = lfp                                                            |
| 分支合并 = $\cup$                                 | 控制流汇合 = $\cup$                                                         |
| 格：$2^Q$（有限）                                   | 格：$2^{\mathrm{State}}$（**无限**）                                         |

> **数据流分析 = 在一个无限状态自动机上做子集构造，然后把结果抽象掉。**
> 你的 `determinize` 和收集语义是同一个 lfp，唯一的差别是底下的格从 $2^Q$（$|Q|<\infty$）换成了 $2^{\mathrm{State}}$（无限、无限高度）。

### 形式化

给程序点 $p$，定义

$$\mathrm{CS}(p)=\{\sigma \mid \text{存在一次从 entry 出发的执行，到达 }p\text{ 时状态为 }\sigma\}$$

它是 $\big(2^{\mathrm{State}}\big)^{\mathrm{Points}}$（逐点序的乘积格，仍是幂集格）上的最小不动点：

$$\mathrm{CS}=\mathrm{lfp}\ F,\qquad
F(X)(p)=\begin{cases}
\mathrm{Init} & p=\text{entry}\\[2pt]
\displaystyle\bigcup_{q\xrightarrow{\ s\ }p}\mathrm{post}_s\big(X(q)\big) & \text{否则}
\end{cases}$$

**为什么是 lfp 而不是 gfp？** 完全是你 `demo_epsilon_lfp()` 里那个理由的重演：gfp 会允许一个"自我供养"的循环——一组状态互相把对方论证为可达，但没有任何一条从 entry 出发的**有限**执行前缀真正到达它们。lfp 只承认有有限证明树（= 真实执行轨迹）的状态。

$\mathrm{post}_s$ 保任意并（它是左伴随，$\mathrm{post}_s\dashv\widetilde{\mathrm{pre}}_s$），所以这个 lfp 行为良好、Kleene 迭代有意义。

**关键：到此为止，一点精度都没丢。** 两个分支汇合处取 $\cup$ 是**精确**的——可能的状态集恰好就是两边的并。这就是幂集格"最饱满"的现实价值。

---

## 四、路径：无穷多条，且无长度上界

龙书接着定义**执行路径** $p_1,p_2,\dots,p_n$：每一步要么是"语句前点 → 同一语句后点"，要么是"某块末尾 → 后继块开头"。

三个必须记住的事实：

**1. 路径条数无穷，长度无上界**（只要有循环）。所以不可能"枚举所有路径"。

**2. 图上的路径 ⊋ 真实可执行的路径。** CFG 丢掉了分支条件，于是

```c
if (x > 0)  a = 1;  else  a = 2;
if (x > 0)  b = a;  else  b = 0;
```

CFG 里有 4 条路径，真实可执行的只有 2 条。**这个损失发生在"把程序画成流图"的那一刻，早于任何算法。** 龙书为此引入 IDEAL（只沿可执行路径）：

$$\mathrm{IDEAL}(p)=\bigsqcup_{\text{可执行路径 }P:\ \text{entry}\to p} f_P(\iota)$$

判定一条路径是否可执行是**不可判定**的，所以 IDEAL 只是理论标杆，不是算法。

**3. $\mathrm{CS}(p)$ 本身不可计算。** $\mathrm{State}$ 无限（整数无界、递归深度无界），$2^{\mathrm{State}}$ 高度无穷，且由 Rice 定理，$\mathrm{CS}(p)$ 的任何非平凡性质都不可判定。

于是原文最后那句话就是必然结论：

> "Program analyses summarize all the possible program states that can occur at a point with a **finite set of facts**."

**把 $2^{\mathrm{State}}$ 换成一个"小"格 $L$**，通过 Galois 连接 $\alpha:2^{\mathrm{State}}\rightleftarrows L:\gamma$ 相联系。这就是抽象解释，也是"data-flow **abstraction**"里 abstraction 一词的确切所指。

---

## 五、精度阶梯：三处损失，各有名字

$$\underbrace{\mathrm{CS}(p)}_{\text{真实，不可算}}\ \xrightarrow{\ \alpha\ }\ \underbrace{\mathrm{IDEAL}}_{\text{抽象后的最好结果}}\ \sqsubseteq\ \underbrace{\mathrm{MOP}}_{\text{所有图路径}}\ \sqsubseteq\ \underbrace{\mathrm{MFP}}_{\text{迭代解}}$$

（$\sqsubseteq$ 读作"至少和……一样精确"；越往右越保守。）

| 损失                              | 来源                           | 何时消失                                  |
| ------------------------------- | ---------------------------- | ------------------------------------- |
| $\mathrm{CS}\to\mathrm{IDEAL}$  | **抽象域表达力不够**（区间装不下"$x$ 是偶数"） | 抽象域够精确时                               |
| $\mathrm{IDEAL}\to\mathrm{MOP}$ | **不可行路径**（CFG 丢了分支条件）        | 路径敏感分析 / 加断言                          |
| $\mathrm{MOP}\to\mathrm{MFP}$   | **提前 join**（循环处不得不合并）        | ⭐ **转移函数分配时相等**（Kildall / Kam–Ullman） |

最后一条就是你前几轮反复遇到的分配律，这里第一次兑换成**真金白银的精度**：

```c
if (c) { x=1; y=2; } else { x=2; y=1; }
z = x + y;
```

- **MOP**：两条路径分别算，都得 $z=3$，join 后 $z=3$ ✓
- **MFP**：先在汇合点 join 得 $x=\top,y=\top$，再算 $z=\top$ ✗

$+$ 在常量格上**单调但不分配**，精度就在那一次提前 join 中漏掉了。而到达定值的转移函数 $f(S)=(S\setminus\mathrm{kill})\cup\mathrm{gen}$ 对 $\cup$ **分配**，所以 $\mathrm{MFP}=\mathrm{MOP}$，迭代解是最优的。

> ⚠️ **命名陷阱**：龙书第 9.3 节用 **meet** $\wedge$ 表示汇合算子（对到达定值，$\wedge$ 竟然是 $\cup$！），于是它的序是"集合越大越低"，迭代得到的解叫 **MFP = Maximum FixedPoint**。抽象解释文献（Cousot、NNH）用 $\sqcup$ 和 **lfp**。**两者是同一个东西的对偶写法。** 读文献时先确认："哪头是不知道？汇合算子叫什么？"——这正是我之前提醒的方向陷阱在实战中的样子。

---

## 六、⭐ "including stack frames below the top" 到底在说什么

这半句常被跳读，但它埋着整个**过程间分析**的难点。

**(1) 状态的规模无界。** 递归意味着同名局部变量可以有任意多份活动实例：

```c
int fact(int n) { if (n<=1) return 1; return n * fact(n-1); }
```

执行到最深处时，$n$ 有 100 个不同的副本。所以"所有变量的值"这个状态不是固定维度的向量，$\mathrm{State}$ 天然无限。

**(2) 如果只看栈顶帧，语义会失真。** 一次 `return` 会让"所有变量"瞬间变成另一套值。只有把下层帧也算进状态，"执行 = 状态的一串变换"才是自洽的。

**(3) 过程间路径不是任意路径——这是最深的一层。** 原文预告了"paths that jump among the flow graphs"。关键约束：**call 和 return 必须配对**。

```
   main ──call──→ f ──return──→ main     ✓ 合法
   main ──call──→ f ──return──→ g        ✗ 非法（返回错了地方）
```

合法路径的 call/return 序列必须是**平衡括号串**（Dyck 语言）。于是过程间分析不再是"图可达性"，而是 **CFL-reachability**（上下文无关语言可达性），这正是 IFDS/IDE 框架（Reps–Horwitz–Sagiv）的技术核心，也是 "context-sensitive" 的确切含义。

> 用你熟悉的语言说：过程内分析是**正则**的（NFA、$2^Q$、幂集格、多项式时间）；过程间分析是**上下文无关**的（下推自动机、栈、CFL-reachability）。**从正则跳到 CFL 的那一步，就藏在 "stack frames below the top" 这半句里。**
> 
> 过程内分析之所以还能做，是因为它**假装其他帧冻结不动**——而这个假装的代价，就是必须对全局变量、指针别名、被调用函数的副作用统统做最保守的处理。

---

## 七、代码：把这段话变成可运行的东西

复用你上一轮练习 #7 的思路——**同一个 `lfp`，换个格换个算子**。

```python
"""dataflow.py — 龙书 9.2.1 的可执行版本
   收集语义（精确，但只能在小状态空间上算） vs MOP vs MFP
"""
from collections import defaultdict, deque
from itertools import product

# ═══════════════════════════════════════════════════════════════
#  通用 worklist 求解器 = 你的 determinize 换个格
# ═══════════════════════════════════════════════════════════════
def solve_mfp(nodes, preds, transfer, join, bottom, entry, init):
    """MFP：(L^Points, ⊑) 上的 lfp，混沌迭代。

    与 determinize 的对应：
      DFA 状态 ↔ 程序点         δ̂(S,a) ↔ transfer[node]
      ∪        ↔ join           worklist ↔ worklist（同一个东西）
    终止性来自格的有限高度 —— 不是来自"有 ⊤"（区间格有 ⊤ 但高度无穷）。
    """
    IN  = {n: bottom for n in nodes}
    OUT = {n: bottom for n in nodes}
    IN[entry] = init
    work = deque(nodes)
    while work:
        n = work.popleft()
        if n != entry:
            new_in = bottom
            for p in preds[n]:
                new_in = join(new_in, OUT[p])      # ← 汇合：唯一的精度损失点
            IN[n] = new_in
        new_out = transfer[n](IN[n])
        if new_out != OUT[n]:
            OUT[n] = new_out
            work.extend(s for s in nodes if n in preds[s])
    return IN, OUT


def solve_mop(paths, transfer, join, bottom, init):
    """MOP：先沿每条路径独立走完，最后才 join。
    仅对无环 CFG 可枚举 —— 有环就是无穷多条路径，这正是 MFP 存在的理由。"""
    acc = bottom
    for path in paths:
        v = init
        for n in path:
            v = transfer[n](v)
        acc = join(acc, v)
    return acc


# ═══════════════════════════════════════════════════════════════
#  格 1：到达定值 —— 幂集格 2^Defs，转移函数分配 ⇒ MFP = MOP
# ═══════════════════════════════════════════════════════════════
def rd_transfer(gen, kill):
    return lambda S: (S - kill) | gen                # f(S) = (S∖kill) ∪ gen


# ═══════════════════════════════════════════════════════════════
#  格 2：常量传播 —— 单调但不分配 ⇒ MFP ⊐ MOP
# ═══════════════════════════════════════════════════════════════
BOT, TOP = "⊥", "⊤"                                  # 平坦格 ⊥ < c < ⊤

def val_join(a, b):
    if a is BOT: return b
    if b is BOT: return a
    return a if a == b else TOP

def env_join(e1, e2):                                # 逐点序的乘积格
    return {v: val_join(e1.get(v, BOT), e2.get(v, BOT))
            for v in set(e1) | set(e2)}

def cp_eval(expr, env):
    """expr: int | str（变量）| ('+', e1, e2)"""
    if isinstance(expr, int):  return expr
    if isinstance(expr, str):  return env.get(expr, BOT)
    _, l, r = expr
    a, b = cp_eval(l, env), cp_eval(r, env)
    if a is BOT or b is BOT:  return BOT
    if a is TOP or b is TOP:  return TOP
    return a + b                                     # ← 这里不分配！

def cp_transfer(assigns):
    def f(env):
        out = dict(env)
        for var, expr in assigns:
            out[var] = cp_eval(expr, out)
        return out
    return f


# ═══════════════════════════════════════════════════════════════
#  演示 CFG：       b1
#                  ╱  ╲
#                b2    b3        b2: x=1,y=2    b3: x=2,y=1
#                  ╲  ╱
#                   b4           b4: z = x+y
# ═══════════════════════════════════════════════════════════════
nodes = ["b1", "b2", "b3", "b4"]
preds = {"b1": [], "b2": ["b1"], "b3": ["b1"], "b4": ["b2", "b3"]}
paths = [["b1", "b2", "b4"], ["b1", "b3", "b4"]]

# ── 到达定值 ──────────────────────────────────────────────────
rd_tf = {
    "b1": rd_transfer(set(), set()),
    "b2": rd_transfer({"d1:x=1", "d2:y=2"}, {"d3:x=2", "d4:y=1"}),
    "b3": rd_transfer({"d3:x=2", "d4:y=1"}, {"d1:x=1", "d2:y=2"}),
    "b4": rd_transfer({"d5:z"}, set()),
}
_, OUT = solve_mfp(nodes, preds, rd_tf, set.union, frozenset(),
                   "b1", frozenset())
mop_rd = solve_mop(paths, rd_tf, set.union, frozenset(), frozenset())

print("【到达定值】f(S)=(S∖kill)∪gen 对 ∪ 分配")
print("  MFP(b4) =", sorted(OUT["b4"]))
print("  MOP(b4) =", sorted(mop_rd))
print("  相等？", OUT["b4"] == mop_rd, " ← Kildall：分配 ⇒ MFP = MOP ✓\n")

# ── 常量传播 ──────────────────────────────────────────────────
cp_tf = {
    "b1": cp_transfer([]),
    "b2": cp_transfer([("x", 1), ("y", 2)]),
    "b3": cp_transfer([("x", 2), ("y", 1)]),
    "b4": cp_transfer([("z", ("+", "x", "y"))]),
}
_, OUT = solve_mfp(nodes, preds, cp_tf, env_join, {}, "b1", {})
mop_cp = solve_mop(paths, cp_tf, env_join, {}, {})

print("【常量传播】'+' 单调但不分配")
print("  MFP(b4) =", OUT["b4"])
print("  MOP(b4) =", mop_cp)
print(f"  z: MFP={OUT['b4']['z']!r}  MOP={mop_cp['z']!r}"
      "   ← 精度就漏在提前 join 这一步 ✗")

# ── 收集语义：把 z 的"所有可能具体值"精确算出来做对照 ──────────
concrete = set()
for path in paths:
    env = {}
    for n in path:
        for var, expr in {"b1": [], "b2": [("x",1),("y",2)],
                          "b3": [("x",2),("y",1)],
                          "b4": [("z",("+","x","y"))]}[n]:
            env[var] = cp_eval(expr, env)
    concrete.add(env["z"])
print("\n【收集语义】CS(b4) 中 z 的所有可能取值 =", concrete,
      " ← α 后正是 MOP 的 3，说明这里的损失纯由'提前 join'造成")
```

输出：

```
【到达定值】f(S)=(S∖kill)∪gen 对 ∪ 分配
  MFP(b4) = ['d1:x=1', 'd2:y=2', 'd3:x=2', 'd4:y=1', 'd5:z']
  MOP(b4) = ['d1:x=1', 'd2:y=2', 'd3:x=2', 'd4:y=1', 'd5:z']
  相等？ True  ← Kildall：分配 ⇒ MFP = MOP ✓

【常量传播】'+' 单调但不分配
  MFP(b4) = {'x': '⊤', 'y': '⊤', 'z': '⊤'}
  MOP(b4) = {'x': '⊤', 'y': '⊤', 'z': 3}
  z: MFP='⊤'  MOP=3   ← 精度就漏在提前 join 这一步 ✗

【收集语义】CS(b4) 中 z 的所有可能取值 = {3}  ← ...
```

---

## 八、五个常见误解

| 误解               | 纠正                                               |
| ---------------- | ------------------------------------------------ |
| "程序点就是语句"        | 点是语句之间的**缝隙**；$n$ 条语句 $n+1$ 个点，相邻语句共享一个点         |
| "状态就是当前作用域的变量"   | 原文明说包含**下层栈帧**；这是过程间分析变成 CFL-reachability 的根源    |
| "分析在跟踪一个状态"      | 分析跟踪的是**状态的集合**（收集语义），再抽象成有限事实                   |
| "分析结果就是运行时会发生的事" | 结果是**过近似**：包含了不可行路径、提前 join 的损失、抽象域的损失           |
| "有 $\top$ 就会收敛"  | 收敛靠**升链条件 / 有限高度**。区间格有 $\top$ 但高度无穷，需要 widening |

---

## 九、一句话总结

> 龙书这段话把"执行"定义为**单个状态沿程序点的确定性变换**；而分析必须对**所有执行**负责，于是唯一的出路是把 $[\![s]\!]:\mathrm{State}\to\mathrm{State}$ 沿"$2^{\mathrm{State}}$ 是自由完备并半格"提升为 $\mathrm{post}_s$，取 lfp 得到**收集语义**——这一步和你写的子集构造是同一个构造，只是格从有限的 $2^Q$ 变成了无限的 $2^{\mathrm{State}}$。
> 
> 因为它不可计算，才有后续的三级退让：**Galois 连接**换掉格（抽象域损失）、**忽略分支条件**（不可行路径损失）、**汇合处提前 join**（非分配时的损失）。前两级是必付的代价，第三级由 Kildall 定理刻画——**分配则免费，不分配则必须付**。
> 
> 而 "including stack frames below the top" 这半句提前告诉你：一旦跨过程，路径必须括号配对，问题就从正则升级到上下文无关。


