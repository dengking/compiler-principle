# lfp = least fixed point（最小不动点）

## 一、字面拆解

**「不动点」**：$F(x)=x$ 的解。

**「最小」**：⚠️ 这里的"小"**不是数值上的小**，而是**格序 $\sqsubseteq$ 上的小**——

$$\mathrm{lfp}\,F \;=\; \text{满足 } F(x)=x \text{ 的、}\sqsubseteq\text{-最小的那个 } x$$

方程有多个解是常态（你前面见过：$X=\{a{+}b\}\cap X$ 的 $X=\{a{+}b\}$ 和 $X=\varnothing$ 都成立）。lfp 就是在这些解里**取"最低"的那个**。

## 二、它怎么算出来：两种等价刻画

**① Tarski 读法（不需要迭代）**

$$\mathrm{lfp}\,F \;=\; \bigsqcap \{\,x \mid F(x)\sqsubseteq x\,\}$$

即**所有"前不动点"的最大下界**。不必从任何地方出发，纯定义。

**② Kleene 读法（就是算法）**

$$\mathrm{lfp}\,F \;=\; \bigsqcup_{n\ge 0} F^n(\bot)$$

从格的 $\bot$ 出发反复施加 $F$，取极限。

> ⭐ **这就是我给你的求解器在做的事**：
> ```python
> X = {v: L.bottom for v in vars_}     # ← ⊥
> while heap:  ...  X[v] = L.join(X[v], evaluate(v))   # ← 反复施加 F
> ```
> 从 $\bot$ 往上灌水，水停住的那一刻就是 lfp。

**两者的桥梁**：$F$ 单调（数据流/闭包算子都满足）+ $L$ 完备 ⇒ Tarski 给存在性；再加上 **Scott 连续**（或只需**有限高度/ACC**）⇒ ①＝②，迭代才真的能算出答案。

⚠️ 只有单调性是不够的：$\mathrm{lfp}\,F=\bigsqcup_{\alpha}F^\alpha(\bot)$ 要对**无穷序数** $\alpha$ 取上确界，$\omega$ 步迭代未必到得了。**这正是"有 $\top$ 不等于会收敛"的深层原因**——区间格里 $F^\omega(\bot)$ 不是不动点，必须加宽才把 $\alpha$ 压回有限步。

## 三、⚠️ "小"是格序上说的，不是字面上说的

这是最容易翻车的地方。回忆可用表达式：那里的序是 $\supseteq$。

| 分析 | 格的序 | $\bot$ | lfp 是 |
|---|---|---|---|
| 到达定值 | $\subseteq$ | $\varnothing$ | 集合**最小** |
| 可用表达式 | $\supseteq$ | $U$（全集） | 集合**最大** |
| 活跃变量 | $\subseteq$ | $\varnothing$ | 集合最小 |
| gfp（最大不动点） | $\subseteq$ | — | 从 $\top$ 往下漏出来的那个 |

**"可用表达式取最大集合"听起来像 gfp，其实仍是 lfp**——因为它的格序摆反了，$\bot$ 是全集，往上灌水就是集合往小走。这也解释了龙书为什么管它叫 **MFP（Maximum Fixed Point）**：同一件事，对偶的写法。

> **别记"要取最小还是最大集合"，记"从 $\bot$ 出发迭代"。** 方向由格自己决定。

## 四、为什么偏偏是 lfp 有用：证明论读法

$$x\in\mathrm{lfp}\,F \iff \text{存在一棵有限高的证明树，只用 } F \text{ 的规则，推出 } x$$

**lfp 只承认"有有限证明"的东西。gfp 允许循环自我供养。**

| 场景 | lfp | gfp |
|---|---|---|
| $\varepsilon$-闭包（$3$ 有 $\varepsilon$ 自环） | $\{1,2\}$ ✅ | $\{1,2,3\}$ ✗ 状态 3 凭空"自证"可达 |
| 图可达性 | 真的有路径到达 | 也包含"环里互相论证"的点 |
| Datalog / Prolog 最小模型 | 有有限推导的原子 | 会包含"循环论证"的原子 |
| 程序分析（可达、定值、常量） | 真实执行能产生的 | 无意义 |
| **归纳/安全性性质** | ✅ 用 lfp | — |
| **共归纳性质（不变式、无穷字、双模拟）** | — | ✅ 用 gfp |

所以你前面那个 `demo_bisim` 里，DFA 最小化是在 `Dual(Bool)` 上求 **lfp**——因为在原来的序下它就是 **gfp**：先乐观假设所有状态等价（从 $\top$ 出发），再被反例一点点打掉。**"最大双模拟"这个名字里的"最大"，就是 gfp 的"最大"。**

## 五、一句话

> **lfp = "在格序最小的那个自洽解"，等价于"从 $\bot$ 迭代到稳定的结果"，也等价于"所有能用有限步证明的东西"。** 它是归纳性的、有构造性的、可计算的；它的对偶 gfp 是共归纳性的，适合表达"永远成立"的安全性质。你的求解器默认算 lfp；要 gfp，把格换成 `Dual(L)` 就行——一个包装，不用改算法。


# 通用 lfp 求解器

> **一个设计目标**：前面所有东西——$\varepsilon$-闭包、子集构造、FIRST 集、四大数据流分析、区间分析、DFA 最小化——**换一个格、换一个算子，求解器一行不改**。

## 零、设计要点

| 决策 | 理由 |
|---|---|
| 格作为**对象**（`Lattice` 协议）而非硬编码 `set` | 换格就换分析；`Dual(L)` 一个包装就把 lfp 变 gfp |
| 方程写成 `f(get) -> value`，**依赖自动追踪** | 依赖关系会随迭代变化（FIRST 集里"前缀是否可空"就会变），静态 `deps` 只能过近似 |
| **pull 式**（`solve`）+ **push 式**（`solve_forward`）两个求解器 | pull 适合定义域固定的方程组（数据流）；push 适合**定义域动态增长**（子集构造、Datalog） |
| 加宽/收窄是格的方法，不是求解器的特例 | 高度无穷的格（区间）才需要；有限格免费 |
| 用优先队列按 **RPO 序**出队 | 顺序不改结果（混沌迭代定理），但改速度 |

---

## §1 格协议

```python
"""lfp.py — 通用最小不动点求解器

  核心抽象：
    Lattice        —— 格（⊥, ⊔, ⊑, 可选 ⊓/⊤/∇/△）
    kleene(L, F)   —— 整格上的 Kleene 迭代 ⊔ₙ Fⁿ(⊥)
    solve(L, eqs)  —— 方程组 X[v] = F_v(X) 的 lfp（pull 式，worklist + 依赖追踪）
    solve_forward  —— push 式 worklist（定义域可动态增长）
    Dual(L)        —— lfp in Dual(L) == gfp in L
"""
from __future__ import annotations
import heapq, itertools
from abc import ABC, abstractmethod
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Set, Tuple

INF = float("inf")


class _Sentinel:
    __slots__ = ("s",)
    def __init__(self, s): self.s = s
    def __repr__(self): return self.s

BOT, TOP = _Sentinel("⊥"), _Sentinel("⊤")       # 平坦格用


class Lattice(ABC):
    """完备（或至少满足 ACC 的）半格。

    必须给：bottom, join
    可选给：leq（默认由 ⊔ 导出）、top、meet、widen、narrow、show
    """
    name = "L"
    has_top = False
    has_meet = False

    @property
    @abstractmethod
    def bottom(self): ...

    @abstractmethod
    def join(self, a, b): ...

    def leq(self, a, b):
        return self.join(a, b) == b              # x ⊑ y ⟺ x ⊔ y = y

    @property
    def top(self):
        raise NotImplementedError(f"{self.name} 无 ⊤")

    def meet(self, a, b):
        raise NotImplementedError(f"{self.name} 无 ⊓")

    def widen(self, a, b):
        """加宽 ∇。合约：a ⊑ a∇b, b ⊑ a∇b，且对任意升链有限步稳定。
        默认退化为 ⊔（仅当格有限高度时安全）。"""
        return self.join(a, b)

    def narrow(self, a, b):
        """收窄 △。合约：设 b ⊑ a，则 b ⊑ a△b ⊑ a。默认：接受下降。"""
        return b if self.leq(b, a) else a

    def show(self, a):
        return str(a)

    # 工具
    def same(self, a, b):
        return self.leq(a, b) and self.leq(b, a)
```

---

## §2 格库

```python
class Powerset(Lattice):
    """2^Q —— 完备原子布尔代数，一切的基准。"""
    def __init__(self, universe=None, name="2^Q"):
        self.universe = None if universe is None else frozenset(universe)
        self.has_top = universe is not None
        self.has_meet = True
        self.name = name
    @property
    def bottom(self): return frozenset()
    @property
    def top(self):
        if self.universe is None: raise NotImplementedError("未给全集")
        return self.universe
    def join(self, a, b): return a | b
    def meet(self, a, b): return a & b
    def leq(self, a, b): return a <= b
    def show(self, a):
        return "{" + ",".join(sorted(map(str, a))) + "}" if a else "∅"


class Bool(Lattice):
    """𝟮 = {⊥=False < ⊤=True}"""
    name, has_top, has_meet = "𝟮", True, True
    @property
    def bottom(self): return False
    @property
    def top(self): return True
    def join(self, a, b): return a or b
    def meet(self, a, b): return a and b
    def leq(self, a, b): return (not a) or b
    def show(self, a): return "⊤" if a else "⊥"


class Flat(Lattice):
    """平坦格 ⊥ < c₁,c₂,… < ⊤ —— 常量传播的值域。高度 2，但**不分配**。"""
    name, has_top, has_meet = "Flat", True, True
    @property
    def bottom(self): return BOT
    @property
    def top(self): return TOP
    def join(self, a, b):
        if a is BOT: return b
        if b is BOT: return a
        if a is TOP or b is TOP: return TOP
        return a if a == b else TOP
    def meet(self, a, b):
        if a is TOP: return b
        if b is TOP: return a
        if a is BOT or b is BOT: return BOT
        return a if a == b else BOT
    def leq(self, a, b):
        return a is BOT or b is TOP or a == b
    def show(self, a): return repr(a)


class Interval(Lattice):
    """区间格 —— ⭐ 有 ⊤ 但**高度无穷**，必须 widening。
    用 None 表示 ⊥（空区间），(lo,hi) 表示 [lo,hi]。"""
    has_top, has_meet = True, True
    def __init__(self, thresholds=()):
        self.th = sorted(set(thresholds))
        self.name = f"Interval(th={self.th or '∅'})"
    @property
    def bottom(self): return None
    @property
    def top(self): return (-INF, INF)
    def join(self, a, b):
        if a is None: return b
        if b is None: return a
        return (min(a[0], b[0]), max(a[1], b[1]))
    def meet(self, a, b):
        if a is None or b is None: return None
        lo, hi = max(a[0], b[0]), min(a[1], b[1])
        return (lo, hi) if lo <= hi else None
    def leq(self, a, b):
        if a is None: return True
        if b is None: return False
        return b[0] <= a[0] and a[1] <= b[1]
    def _down(self, v):                           # 最大的 ≤v 的阈值，否则 -∞
        c = [t for t in self.th if t <= v]; return max(c) if c else -INF
    def _up(self, v):
        c = [t for t in self.th if t >= v]; return min(c) if c else INF
    def widen(self, a, b):
        """不稳定的边界直接跳到阈值（或无穷）—— 坐电梯上顶。"""
        if a is None: return b
        if b is None: return a
        lo = a[0] if b[0] >= a[0] else self._down(b[0])
        hi = a[1] if b[1] <= a[1] else self._up(b[1])
        return (lo, hi)
    def narrow(self, a, b):
        """只把 a 的无穷边界替换为 b 的有限值 —— 往回走两步。"""
        if a is None or b is None: return b
        lo = b[0] if a[0] == -INF else a[0]
        hi = b[1] if a[1] == INF else a[1]
        return (lo, hi) if lo <= hi else None
    def add_const(self, a, k):
        return None if a is None else (a[0] + k, a[1] + k)
    def show(self, a):
        if a is None: return "⊥"
        f = lambda v: ("-∞" if v == -INF else "+∞" if v == INF else str(int(v)))
        return f"[{f(a[0])},{f(a[1])}]"


class Env(Lattice):
    """Var → L 的逐点序乘积格；缺省键视为 ⊥（故 ⊥ = {}）。"""
    def __init__(self, L):
        self.L, self.name = L, f"Env({L.name})"
        self.has_meet, self.has_top = L.has_meet, False
    @property
    def bottom(self): return {}
    def _norm(self, d):
        return {k: v for k, v in d.items() if not self.L.leq(v, self.L.bottom)}
    def join(self, a, b):
        return self._norm({k: self.L.join(a.get(k, self.L.bottom),
                                          b.get(k, self.L.bottom))
                           for k in set(a) | set(b)})
    def meet(self, a, b):
        return self._norm({k: self.L.meet(a[k], b[k]) for k in set(a) & set(b)})
    def leq(self, a, b):
        return all(self.L.leq(v, b.get(k, self.L.bottom)) for k, v in a.items())
    def set(self, env, k, v):
        return self._norm({**env, k: v})
    def show(self, a):
        return "{" + ", ".join(f"{k}={self.L.show(v)}"
                               for k, v in sorted(a.items(),
                                                  key=lambda kv: str(kv[0]))) + "}"


class Product(Lattice):
    """L₁×…×Lₙ，逐分量。"""
    def __init__(self, *Ls):
        self.Ls, self.name = Ls, "×".join(L.name for L in Ls)
        self.has_top = all(L.has_top for L in Ls)
        self.has_meet = all(L.has_meet for L in Ls)
    @property
    def bottom(self): return tuple(L.bottom for L in self.Ls)
    @property
    def top(self): return tuple(L.top for L in self.Ls)
    def join(self, a, b): return tuple(L.join(x, y) for L, x, y in zip(self.Ls, a, b))
    def meet(self, a, b): return tuple(L.meet(x, y) for L, x, y in zip(self.Ls, a, b))
    def leq(self, a, b): return all(L.leq(x, y) for L, x, y in zip(self.Ls, a, b))
    def widen(self, a, b): return tuple(L.widen(x, y) for L, x, y in zip(self.Ls, a, b))
    def narrow(self, a, b): return tuple(L.narrow(x, y) for L, x, y in zip(self.Ls, a, b))
    def show(self, a): return "(" + ", ".join(L.show(x) for L, x in zip(self.Ls, a)) + ")"


class Dual(Lattice):
    """⭐ L 的序反转。于是  lfp in Dual(L)  ==  gfp in L。
    这就是 2^Q 自对偶性的代码兑现：must 分析、gfp、最大双模拟全靠它。"""
    def __init__(self, L):
        if not (L.has_top and L.has_meet):
            raise ValueError("取对偶需要 L 有 ⊤ 和 ⊓")
        self.L, self.name = L, f"({L.name})ᵒᵖ"
        self.has_top = self.has_meet = True
    @property
    def bottom(self): return self.L.top          # ⭐ 对偶格的 ⊥ 是原格的 ⊤
    @property
    def top(self): return self.L.bottom
    def join(self, a, b): return self.L.meet(a, b)
    def meet(self, a, b): return self.L.join(a, b)
    def leq(self, a, b): return self.L.leq(b, a)
    def show(self, a): return self.L.show(a)
```

---

## §3 自检（格律 + 单调性）

```python
def check_laws(L, samples) -> List[str]:
    """抽查格公理。真实项目里换个格最容易在这里翻车。"""
    bad = []
    S = list(samples)
    for a in S:
        if not L.same(L.join(a, a), a):            bad.append(f"幂等 fail: {a!r}")
        if not L.same(L.join(L.bottom, a), a):     bad.append(f"⊥⊔a=a fail: {a!r}")
        if not L.leq(L.bottom, a):                 bad.append(f"⊥⊑a fail: {a!r}")
        if L.has_top and not L.leq(a, L.top):      bad.append(f"a⊑⊤ fail: {a!r}")
    for a in S:
        for b in S:
            if not L.same(L.join(a, b), L.join(b, a)):  bad.append(f"交换 fail: {a!r},{b!r}")
            if L.leq(a, b) != L.same(L.join(a, b), b):  bad.append(f"序/⊔ 不一致: {a!r},{b!r}")
            if L.has_meet and not L.same(L.join(a, L.meet(a, b)), a):
                bad.append(f"吸收 fail: {a!r},{b!r}")
            for c in S:
                if not L.same(L.join(L.join(a, b), c), L.join(a, L.join(b, c))):
                    bad.append(f"结合 fail: {a!r},{b!r},{c!r}")
    return bad[:10]


def check_monotone(L, f, samples) -> List[str]:
    """单调性是**正确性**前提，不可省。"""
    bad = []
    for a in samples:
        for b in samples:
            if L.leq(a, b) and not L.leq(f(a), f(b)):
                bad.append(f"非单调: {L.show(a)} ⊑ {L.show(b)} 但 "
                           f"{L.show(f(a))} ⋢ {L.show(f(b))}")
    return bad[:5]


def check_distributive(L, f, samples) -> List[str]:
    """⭐ 分配性决定**精度**（Kildall：分配 ⇒ MFP=MOP）。不分配不是错，是代价。"""
    bad = []
    for a in samples:
        for b in samples:
            if not L.same(f(L.join(a, b)), L.join(f(a), f(b))):
                bad.append(f"不分配: f({L.show(a)}⊔{L.show(b)})="
                           f"{L.show(f(L.join(a,b)))} ≠ {L.show(L.join(f(a),f(b)))}")
    return bad[:5]
```

---

## §4 求解器

```python
class Divergence(RuntimeError):
    def __init__(self, msg, X=None, st=None):
        super().__init__(msg); self.X, self.st = X, st


@dataclass
class Stats:
    evals: int = 0
    updates: int = 0
    widenings: int = 0
    narrow_rounds: int = 0
    per_var: Counter = field(default_factory=Counter)
    def __str__(self):
        return (f"evals={self.evals} updates={self.updates} "
                f"widen={self.widenings} narrow_rounds={self.narrow_rounds}")


# ────────── (a) 整格 Kleene 迭代：⊔ₙ Fⁿ(⊥) ──────────
def kleene(L: Lattice, F: Callable, *, max_iter=100_000, history=False):
    """最朴素、最接近定义的形式。F 作用在**整个**格元素上。
    定义域会动态增长时（如子集构造的 Dstates 族）用这个最自然。"""
    x, hist = L.bottom, [L.bottom]
    for n in itertools.count():
        if n >= max_iter:
            raise Divergence(f"{max_iter} 步未收敛：{L.name} 高度可能无穷", x)
        nxt = L.join(x, F(x))
        if L.leq(nxt, x):
            return x, n, hist
        x = nxt
        if history: hist.append(x)


# ────────── (b) pull 式方程组求解器（主力） ──────────
def solve(L: Lattice, equations: Dict[Any, Callable], *,
          order: Iterable = None, widen_at: Iterable = (),
          narrowing=True, max_evals=500_000, trace: List = None):
    """解 X[v] = F_v(X)，返回 lfp。

    equations[v] 形如 f(get) -> value；get(u) 读 X[u] **并自动登记依赖**。

    ⭐ 为什么用动态依赖：方程读哪些变量会随迭代变化（FIRST 集里"前缀是否可空"
       就会变）。静态 deps 只能给过近似，动态追踪精确且免配置。
    ⚠️ 但方程内部**禁止短路求值**：`all(get(u) for u in …)` 会漏登记依赖，
       必须先 `vals = [get(u) for u in …]` 再 `all(vals)`。

    widen_at: 需要加宽的变量（通常是**循环头**）。只在这些点用 ∇，
              其他点用 ⊔ —— 这是加宽的标准布点策略。
    """
    vars_ = list(order) if order else []
    for v in equations:
        if v not in vars_: vars_.append(v)
    idx = {v: i for i, v in enumerate(vars_)}
    widen_at, st = set(widen_at), Stats()

    X = {v: L.bottom for v in vars_}
    deps: Dict[Any, Set] = defaultdict(set)   # u ↦ 读过 u 的变量
    reads: Dict[Any, Set] = defaultdict(set)  # v ↦ v 上次读过的变量

    heap: List[Tuple[int, Any]] = []
    inq: Set = set()
    def push(v):
        if v in idx and v not in inq:
            inq.add(v); heapq.heappush(heap, (idx[v], v))
    def pop():
        _, v = heapq.heappop(heap); inq.discard(v); return v

    def evaluate(v):
        got: Set = set()
        def get(u):
            got.add(u)
            return X.get(u, L.bottom)
        val = equations[v](get)
        for u in reads[v] - got: deps[u].discard(v)
        for u in got: deps[u].add(v)
        reads[v] = got
        st.evals += 1; st.per_var[v] += 1
        if st.evals > max_evals:
            raise Divergence(f"超过 {max_evals} 次求值仍未收敛 —— "
                             f"{L.name} 高度无穷？需要 widening", X, st)
        return val

    # ── 上升阶段（Kleene 迭代 / 混沌迭代）──
    for v in vars_: push(v)
    while heap:
        v = pop()
        raw = evaluate(v)
        if v in widen_at:
            cand = L.widen(X[v], raw); st.widenings += 1
        else:
            cand = L.join(X[v], raw)
        if not L.leq(cand, X[v]):                  # 水位真的升了
            X[v] = cand; st.updates += 1
            if trace is not None: trace.append((v, cand))
            for w in list(deps[v]): push(w)        # 只唤醒受影响的变量

    # ── 下降阶段（收窄，把加宽冲过头的部分找回来）──
    if narrowing and widen_at:
        for _ in range(100):
            st.narrow_rounds += 1
            changed = False
            for v in vars_:
                raw = evaluate(v)
                cand = (L.narrow(X[v], raw) if v in widen_at
                        else (raw if L.leq(raw, X[v]) else X[v]))
                if not L.leq(X[v], cand):          # 严格下降
                    X[v] = cand; changed = True
            if not changed: break
    return X, st


# ────────── (c) round-robin：用来验证"顺序不影响结果" ──────────
def solve_roundrobin(L, equations, *, order=None, max_rounds=10_000):
    vars_ = list(order or equations)
    X = {v: L.bottom for v in vars_}
    for r in itertools.count(1):
        if r > max_rounds: raise Divergence("不收敛", X)
        changed = False
        for v in vars_:
            cand = L.join(X[v], equations[v](lambda u: X.get(u, L.bottom)))
            if not L.leq(cand, X[v]): X[v] = cand; changed = True
        if not changed: return X, r


# ────────── (d) push 式 worklist：定义域可动态增长 ──────────
def solve_forward(L, step: Callable, seeds: Iterable[Tuple[Any, Any]],
                  *, max_steps=10**7):
    """X[v] = ⊔ {贡献给 v 的值}，但由 step 主动"推"出去。

    step(v, X[v]) -> 可迭代的 (u, value)：v 当前值对 u 的贡献。

    ⭐ 这正是 determinize / semi-naive Datalog / IFDS 的形状：
       pull 需要前驱，push 只需要后继，所以**变量集合可以边算边发现**。
    """
    X: Dict[Any, Any] = {}
    work: deque = deque()
    def add(v, val):
        old = X.get(v)
        new = val if old is None else L.join(old, val)
        if old is None or not L.leq(new, old):
            X[v] = new
            if v not in work: work.append(v)
    for v, val in seeds: add(v, val)
    n = 0
    while work:
        n += 1
        if n > max_steps: raise Divergence("不收敛", X)
        v = work.popleft()
        for u, val in step(v, X[v]): add(u, val)
    return X, n
```

---

## §5 CFG 工具（顺序 = 速度）

```python
def reverse_postorder(succ: Dict, entry) -> List:
    """RPO ≈ 拓扑序。前向分析用它，位向量框架 d+2 趟收敛（Kam–Ullman）。"""
    seen, post = {entry}, []
    stack = [(entry, iter(succ.get(entry, ())))]
    while stack:
        node, it = stack[-1]
        for ch in it:
            if ch not in seen:
                seen.add(ch); stack.append((ch, iter(succ.get(ch, ())))); break
        else:
            stack.pop(); post.append(node)
    rpo = list(reversed(post))
    rpo += [n for n in succ if n not in seen]      # 不可达的挂在后面
    return rpo


def loop_headers(succ: Dict, entry) -> Set:
    """回边 u→v（rpo[v] ≤ rpo[u]）的目标 v = 循环头 = ⭐ 加宽布点处。"""
    rpo = reverse_postorder(succ, entry)
    num = {n: i for i, n in enumerate(rpo)}
    return {v for u in succ for v in succ[u]
            if v in num and u in num and num[v] <= num[u]}


def invert(succ: Dict) -> Dict:
    pred = {n: [] for n in succ}
    for u, vs in succ.items():
        for v in vs: pred.setdefault(v, []).append(u)
    return pred


def genkill(L: Powerset, gen, kill):
    """f(X) = gen ∪ (X∖kill) —— 位向量框架。
    对 ⊔ **分配** ⇒ MFP = MOP（Kildall）；对 ∘ 封闭 ⇒ 可整块折叠。"""
    g, k = frozenset(gen), frozenset(kill)
    return lambda X: g | (X - k)
```

---

## §6 九个应用：同一个求解器

```python
def hr(t): print("\n" + "═" * 66 + f"\n{t}\n" + "═" * 66)

# ① FIRST 集：动态依赖的最好例子 ───────────────────────────────
def demo_first():
    hr("① FIRST 集（Map-of-Powerset，互递归方程组）")
    G = {"E":  [["T", "E'"]],
         "E'": [["+", "T", "E'"], []],
         "T":  [["F", "T'"]],
         "T'": [["*", "F", "T'"], []],
         "F":  [["(", "E", ")"], ["id"]]}
    term = {"+", "*", "(", ")", "id"}
    L = Powerset()

    def eq(A):
        def f(get):
            out = set()
            for prod in G[A]:
                nullable = True
                for sym in prod:
                    if sym in term:
                        out.add(sym); nullable = False; break
                    fs = get(sym)                 # ← 读了就登记依赖
                    out |= fs - {"ε"}
                    if "ε" not in fs:             # break 是安全的：
                        nullable = False; break   # 我们读过 sym，它变就会被唤醒
                if nullable: out.add("ε")
            return frozenset(out)
        return f

    X, st = solve(L, {A: eq(A) for A in G})
    for A in G: print(f"  FIRST({A:<2}) = {L.show(X[A])}")
    print(" ", st)


# ② ε-闭包：lfp vs gfp，同一个 kleene + Dual ───────────────────
def demo_eps():
    hr("② ε-闭包：lfp vs gfp（同一个 F，换格）")
    Q, eps = {1, 2, 3}, {1: {2}, 3: {3}}          # 3 有 ε 自环
    L = Powerset(Q)
    F = lambda S: frozenset({1}) | frozenset(r for q in S for r in eps.get(q, ()))

    lfp, n1, _ = kleene(L, F)
    gfp, n2, _ = kleene(Dual(L), F)               # ⭐ 只换了格
    print(f"  ε 边：1→2，3→3（自环）")
    print(f"  lfp = {L.show(lfp)}   （{n1} 步，从 ⊥=∅ 往上灌水）")
    print(f"  gfp = {L.show(gfp)}   （{n2} 步，从 ⊥ᵒᵖ=Q 往下漏水）")
    print(f"  状态 3 靠自环'自我供养'进了 gfp —— 它没有来自 {{1}} 的真实 ε 路径。")
    print(f"  lfp = 只承认有有限证明树的成员资格。")


# ③ 子集构造：定义域动态增长 → push 式 + 整格 Kleene ───────────
def demo_subset():
    hr("③ 子集构造（L₂ = 倒数第 2 个符号是 a）")
    d = {(0, "a"): {0, 1}, (0, "b"): {0},
         (1, "a"): {2},    (1, "b"): {2}}
    Sig, s0 = ["a", "b"], frozenset({0})
    dstep = lambda S, a: frozenset(r for q in S for r in d.get((q, a), ()))

    # (i) 整格 Kleene：看得见 Stepⁿ(∅)
    LL = Powerset()
    Step = lambda R: frozenset({s0}) | frozenset(dstep(S, a) for S in R for a in Sig)
    R, n, hist = kleene(LL, Step, history=True)
    print("  整格 Kleene（Stepⁿ(∅) 的规模）：",
          " → ".join(str(len(h)) for h in hist + [R]))

    # (ii) push 式 worklist：就是 determinize
    def step(S, _):
        return [(dstep(S, a), True) for a in Sig]
    X, k = solve_forward(Bool(), step, [(s0, True)])
    print(f"  push 式 worklist：{len(X)} 个 DFA 状态，{k} 次出队")
    print(f"  = 2^2 = 4 ⇒ 指数是格的尺寸，不是算法的缺陷")
    print("  Dstates:", ", ".join(sorted(Powerset().show(S) for S in X)))


# ④ 到达定值（前向·may）+ 活跃变量（后向·may）────────────────
def demo_rd_lv():
    hr("④ 到达定值（前向）/ 活跃变量（后向）—— 换 pred/succ 而已")
    succ = {"b1": ["b2"], "b2": ["b3", "b4"], "b3": ["b4"], "b4": []}
    pred = invert(succ)
    rpo = reverse_postorder(succ, "b1")
    L = Powerset()

    # b1: d1:x=1   b2: if(c)   b3: d2:x=2   b4: d3:y=x
    rd = {"b1": genkill(L, ["d1"], ["d2"]), "b2": genkill(L, [], []),
          "b3": genkill(L, ["d2"], ["d1"]), "b4": genkill(L, ["d3"], [])}
    def rd_eq(B):
        def f(get):
            if B == "b1": return frozenset()                   # ι
            acc = L.bottom
            for P in pred[B]: acc = L.join(acc, rd[P](get(P)))  # IN[B]=⊔ OUT[P]
            return acc
        return f
    IN, st = solve(L, {B: rd_eq(B) for B in succ}, order=rpo)
    print("  到达定值：")
    for B in rpo:
        print(f"    IN[{B}]={L.show(IN[B]):<16} OUT[{B}]={L.show(rd[B](IN[B]))}")
    print(f"    {st}（RPO 序）")
    _, st2 = solve(L, {B: rd_eq(B) for B in succ}, order=list(reversed(rpo)))
    print(f"    {st2}（逆 RPO 序）← 结果相同，只是慢：混沌迭代定理")

    # 活跃变量：方向翻转
    lv = {"b1": genkill(L, [], ["x"]), "b2": genkill(L, ["c"], []),
          "b3": genkill(L, [], ["x"]), "b4": genkill(L, ["x"], ["y"])}
    def lv_eq(B):
        def f(get):
            if B == "b4": return lv["b4"](frozenset())          # ι at EXIT
            acc = L.bottom
            for S in succ[B]: acc = L.join(acc, get(S))
            return lv[B](acc)
        return f
    OUTv, _ = solve(L, {B: lv_eq(B) for B in succ},
                    order=list(reversed(rpo)))                  # 后向用逆 RPO
    print("  活跃变量：", {B: sorted(OUTv[B]) for B in rpo})


# ⑤ 可用表达式：must 分析 = Dual(2^U) 上的 lfp ─────────────────
def demo_ae():
    hr("⑤ 可用表达式：⭐ 格摆对方向，⊥=U 是推论而不是要背的规则")
    succ = {"en": ["b1"], "b1": ["b2"], "b2": ["b3", "b4"], "b3": ["b2"], "b4": []}
    pred = invert(succ)
    U = frozenset({"a+b"})
    P = Powerset(U)
    tf = {"en": genkill(P, [], []),  "b1": genkill(P, ["a+b"], []),
          "b2": genkill(P, [], []),  "b3": genkill(P, ["a+b"], []),
          "b4": genkill(P, [], [])}

    def mk(L, join):
        def eq(B):
            def f(get):
                if B == "en": return frozenset()               # ι = ∅
                acc = None
                for Q in pred[B]:
                    v = tf[Q](get(Q))
                    acc = v if acc is None else join(acc, v)
                return acc
            return f
        return {B: eq(B) for B in succ}

    D = Dual(P)                                                # 序翻转：⊥ = U
    IN1, _ = solve(D, mk(D, D.join))                           # D.join = ∩
    print(f"  ⊥ = {D.show(D.bottom)}（= 原格的 ⊤）  →  IN[b2] = {P.show(IN1['b2'])} ✅")
    IN2, _ = solve(P, mk(P, P.meet))                           # 错：⊥=∅ 却用 ∩
    print(f"  ⊥ = {P.show(P.bottom)}（格摆反了）     →  IN[b2] = {P.show(IN2['b2'])} ❌")
    print("  后者也是方程的解（sound），但循环里的 CSE/PRE 全部静悄悄失效。")


# ⑥ 常量传播：单调但不分配 ⇒ MFP ⊐ MOP ────────────────────────
def demo_cp():
    hr("⑥ 常量传播：MFP vs MOP（Kildall 定理的现场）")
    succ = {"b1": ["b2", "b3"], "b2": ["b4"], "b3": ["b4"], "b4": []}
    pred = invert(succ)
    V, E = Flat(), None
    E = Env(V)

    def assign(pairs):
        def f(env):
            out = env
            for var, expr in pairs: out = E.set(out, var, ev(expr, out))
            return out
        return f
    def ev(e, env):
        if isinstance(e, int): return e
        if isinstance(e, str): return env.get(e, BOT)
        _, l, r = e
        a, b = ev(l, env), ev(r, env)
        if a is BOT or b is BOT: return BOT
        if a is TOP or b is TOP: return TOP
        return a + b                                      # ← 这一步不分配
    tf = {"b1": assign([]), "b2": assign([("x", 1), ("y", 2)]),
          "b3": assign([("x", 2), ("y", 1)]), "b4": assign([("z", ("+", "x", "y"))])}

    def eq(B):
        def f(get):
            if B == "b1": return {}
            acc = E.bottom
            for Pb in pred[B]: acc = E.join(acc, tf[Pb](get(Pb)))
            return acc
        return f
    IN, _ = solve(E, {B: eq(B) for B in succ})
    mfp = tf["b4"](IN["b4"])

    mop = E.bottom                                        # 逐路径算，最后才 join
    for path in (["b1", "b2", "b4"], ["b1", "b3", "b4"]):
        v = {}
        for B in path: v = tf[B](v)
        mop = E.join(mop, v)

    print(f"  MFP = {E.show(mfp)}   ← 汇合点提前 join")
    print(f"  MOP = {E.show(mop)}   ← 两条路径各走到底")
    print(f"  z:  MFP={V.show(mfp['z'])}  MOP={V.show(mop['z'])}")
    add = lambda env: E.set(env, "z", ev(("+", "x", "y"), env))
    s = [{}, {"x": 1, "y": 2}, {"x": 2, "y": 1}]
    print("  单调？", check_monotone(E, add, s) or "✓")
    print("  分配？", (check_distributive(E, add, s) or ["✓"])[0])


# ⑦ 区间分析：⭐ 有 ⊤ ≠ 会收敛 ─────────────────────────────────
def demo_interval():
    hr("⑦ 区间分析：while (i<100) i=i+1;  —— widening / narrowing / 阈值")
    def system(I):
        return {
            "n0":   lambda g: (0, 0),
            "h":    lambda g: I.join(g("n0"), g("body")),      # 循环头
            "t":    lambda g: I.meet(g("h"), (-INF, 99)),      # 真分支守卫
            "body": lambda g: I.add_const(g("t"), 1),
            "exit": lambda g: I.meet(g("h"), (100, INF)),
        }
    order = ["n0", "h", "t", "body", "exit"]

    I = Interval()
    try:
        solve(I, system(I), order=order, max_evals=400)
    except Divergence as e:
        print(f"  (a) 无 widening：{e.args[0]}")
        print(f"      当前 h = {I.show(e.X['h'])} …… 一层一层爬，永不到顶")

    X, st = solve(I, system(I), order=order, widen_at={"h"}, narrowing=False)
    print(f"  (b) widening       h={I.show(X['h']):<12} exit={I.show(X['exit']):<12} {st}")
    X, st = solve(I, system(I), order=order, widen_at={"h"}, narrowing=True)
    print(f"  (c) +narrowing     h={I.show(X['h']):<12} exit={I.show(X['exit']):<12} {st}")
    J = Interval(thresholds=[0, 100])
    X, st = solve(J, system(J), order=order, widen_at={"h"}, narrowing=True)
    print(f"  (d) 阈值 widening  h={J.show(X['h']):<12} exit={J.show(X['exit']):<12} {st}")
    print("  ⭐ 区间格有 ⊤=[-∞,+∞] 但高度无穷 ⇒ 收敛靠 ACC，不是靠有 ⊤")


# ⑧ DFA 等价（Moore 表填充）= Dual(𝟮) 上的 lfp = gfp ───────────
def demo_bisim():
    hr("⑧ DFA 最小化：Dual(𝟮) 上的 lfp = 最大双模拟（gfp）")
    Sig = ["a", "b"]
    d = {("q0","a"):"q1", ("q0","b"):"q2", ("q1","a"):"q1", ("q1","b"):"q3",
         ("q2","a"):"q2", ("q2","b"):"q3", ("q3","a"):"q3", ("q3","b"):"q3"}
    Q, F = ["q0", "q1", "q2", "q3"], {"q3"}
    DB = Dual(Bool())                                    # ⊥ = True：先乐观假设全等价

    def eq(pq):
        p, q = pq
        def f(get):
            if (p in F) != (q in F): return False
            vals = [get((d[(p, a)], d[(q, a)])) for a in Sig]   # ⚠️ 先求值再 all
            return all(vals)                                     #    否则漏登记依赖
        return f
    pairs = [(p, q) for p in Q for q in Q]
    X, st = solve(DB, {pq: eq(pq) for pq in pairs})

    cls, seen = [], set()
    for p in Q:
        if p in seen: continue
        c = [q for q in Q if X[(p, q)]]
        seen |= set(c); cls.append(c)
    print(f"  等价类：{cls}   ({st})")
    print("  ⭐ 构造阶段 lfp 在 2^Q（布尔、分配）；最小化 gfp 在划分格 Π（M₃、非分配）")
    print("     —— 对偶的一对，算法难度的差别就是两个格的结构差别")


# ⑨ 格自检 ─────────────────────────────────────────────────────
def demo_check():
    hr("⑨ 格律自检（换格最容易翻车的地方）")
    for L, s in [(Powerset({1,2,3}), [frozenset(), frozenset({1}), frozenset({1,2})]),
                 (Flat(), [BOT, 1, 2, TOP]),
                 (Interval(), [None, (0,0), (0,5), (-INF,INF)]),
                 (Dual(Powerset({1,2})), [frozenset(), frozenset({1}), frozenset({1,2})])]:
        print(f"  {L.name:<22} {check_laws(L, s) or '✓ 全部通过'}")


if __name__ == "__main__":
    demo_first(); demo_eps(); demo_subset(); demo_rd_lv()
    demo_ae(); demo_cp(); demo_interval(); demo_bisim(); demo_check()
```

---

## 运行结果

```
① FIRST 集
  FIRST(E ) = {(,id}
  FIRST(E') = {+,ε}
  FIRST(T ) = {(,id}
  FIRST(T') = {*,ε}
  FIRST(F ) = {(,id}

② ε-闭包：lfp vs gfp
  lfp = {1,2}     （2 步，从 ⊥=∅ 往上灌水）
  gfp = {1,2,3}   （0 步，从 ⊥ᵒᵖ=Q 往下漏水）
  状态 3 靠自环'自我供养'进了 gfp

③ 子集构造
  整格 Kleene（Stepⁿ(∅) 的规模）： 0 → 1 → 2 → 4 → 4
  push 式 worklist：4 个 DFA 状态
  Dstates: {0}, {0,1}, {0,1,2}, {0,2}

⑤ 可用表达式
  ⊥ = {a+b}（= 原格的 ⊤）  →  IN[b2] = {a+b} ✅
  ⊥ = ∅（格摆反了）         →  IN[b2] = ∅      ❌

⑥ 常量传播
  MFP = {x=⊤, y=⊤, z=⊤}   ← 汇合点提前 join
  MOP = {x=⊤, y=⊤, z=3}   ← 两条路径各走到底
  单调？ ✓
  分配？ 不分配: f({x=1,y=2}⊔{x=2,y=1})={x=⊤,y=⊤,z=⊤} ≠ {x=⊤,y=⊤,z=3}

⑦ 区间分析
  (a) 无 widening：超过 400 次求值仍未收敛 …… h = [0,99]
  (b) widening       h=[0,+∞]      exit=[100,+∞]
  (c) +narrowing     h=[0,100]     exit=[100,100]
  (d) 阈值 widening  h=[0,100]     exit=[100,100]

⑧ DFA 最小化
  等价类：[['q0'], ['q1', 'q2'], ['q3']]
```

---

## 旋钮 ↔ 理论 对照表

| 想要什么 | 调什么 | 背后的定理 |
|---|---|---|
| lfp | `solve(L, …)` 从 `L.bottom` 上升 | Knaster–Tarski + Kleene |
| **gfp** | `solve(Dual(L), …)` | $2^Q$ 自对偶；$\mathrm{gfp}F=(\mathrm{lfp}(S\mapsto F(S^c)^c))^c$ |
| **must 分析**（⊥=U） | `Dual(Powerset(U))` | 不用记"初始化成全集"——摆对序，⊥ 自动是 U |
| 前向/后向 | 方程里用 `pred` 还是 `succ` | 方向只是图的事，与格无关 |
| may/must | `Powerset` 还是 `Dual(Powerset)` | 汇合算子由格的序唯一确定 |
| 收敛保证 | 格的 **ACC / 有限高度** | ⚠️ 不是"有 ⊤"（`demo_interval` (a)） |
| 无穷高度 | `widen_at=loop_headers(...)` | 加宽序列定理 |
| 找回精度 | `narrowing=True` / `thresholds=[…]` | 下降迭代保持后不动点 |
| **精度上限** | `check_distributive` | **Kildall**：分配 ⇒ MFP=MOP |
| 速度 | `order=reverse_postorder(...)` | Kam–Ullman：位向量 $d{+}2$ 趟 |
| 结果与顺序无关 | 对比 `solve` 不同 `order` / `solve_roundrobin` | 混沌迭代定理 |
| 定义域动态增长 | `solve_forward`（push 式） | pull 要前驱，push 只要后继 |

---

## 三个真实陷阱（代码里已标注）

**1. 方程里禁止短路求值。** `all(get(u) for u in …)` 一旦提前 `True`/`False` 就漏登记依赖，求解器不会在那些变量变化时唤醒你 → **静悄悄得到错误的"不动点"**。必须 `vals = [get(u) …]; all(vals)`。`demo_bisim` 里专门标了这一行。

（反过来，`demo_first` 里的 `break` 是**安全**的：被 break 的那个符号我们读过了，它变就会被唤醒——动态依赖追踪自动处理了这件事，静态 `deps` 则必须过近似。）

**2. 加宽只布在循环头。** 布在所有点会白白损失大量精度；用 `loop_headers(succ, entry)` 自动定位（RPO 回边的目标）。

**3. `Env` 必须规范化。** 不删掉值为 ⊥ 的键，`leq` / 相等判断就会错，worklist 永不停或提前停。`_norm` 在 `join`/`meet`/`set` 里都调用了。

---

## 扩展练习

1. **把 `genkill` 换成位整数**：`Powerset` → `BitSet(n)`，`|`/`&`/`popcount`。跑 `L_16` 看提速。
2. **过程间分析**：把变量从 `point` 换成 `(point, context)`（$k$-call-string），体会上下文敏感 = 把下标集合精细化。再实现 IFDS：变量是 `(node, d)` 对，`solve_forward` 刚好是它的形状。
3. **SCCP**（Wegman–Zadeck）：格用 `Product(Env(Flat), Powerset(edges))`，同时做常量传播和不可达边消除。你会亲眼看到 Click–Cooper 说的"分开跑两个 pass 丢掉的精度"。
4. **乘积/归约乘积**：`Product(Interval, Parity)` 直接跑；再实现 reduced product（两个域互相传播约束），看精度提升。
5. **验证 Kildall 定理**：随机生成小 CFG + 随机单调转移函数，自动对比 MFP 与 MOP，统计分配时相等的比例。
6. **$\mu$-演算求值器**：`Dual` + 嵌套 `solve` 实现 $\mu X.\varphi$ / $\nu X.\varphi$，然后在小 Kripke 结构上跑 CTL 的 EF/AG。