# 编译器领域的其他“万能锤”：十把跨领域通用的核心技术

> **摘要**：本系列前文确认了编译器中的两把“万能锤”（Universal Hammer）：前端的 **NFA → DFA 确定化**（Determinization），以及后端的 **格上单调不动点迭代**（Monotone Fixed-Point Iteration over Lattices）。前文还指出两者其实是同一把：子集构造（Subset Construction）等价于在幂集格（Powerset Lattice）上求最小不动点（Least Fixed Point, lfp）。
>
> 编译器的工作远不止“前端识别 + 后端优化”。类型系统（Type System）、中间表示设计（IR Design）、控制流降级（Control-Flow Lowering）、增量编译（Incremental Compilation）、正确性保证（Correctness Assurance）、语言运行时（Language Runtime）等子领域，各自都有反复使用的“万能锤”。本文介绍十把我认为**真正达到“万能锤”标准**的技术，另附四把“小锤”，最后把全部锤子归并为**五种基本机制**和**三条元原则**。

---

## 总览：十把锤子

|       | 锤子 | 一句话 | 统一了什么 |
| ----- | ---- | ------ | ---------- |
| **A** | **合一与约束求解**（Unification & Constraint Solving） | 把“推导”变成“解方程” | 类型推导、重载决议、泛型实例化、trait 求解、模式匹配、别名分析 |
| **B** | **控制流即数据**（Control as Data：CPS / 状态机化） | 任何控制结构都能变成“显式状态 + 分派循环” | CPS、闭包转换、去函数化、async/await、生成器、协程、异常、SSA |
| **C** | **偏求值与分阶段**（Partial Evaluation & Staging，Futamura 投影） | 编译 = 对解释器做偏求值 | 常量折叠、内联、单态化、模板实例化、宏、循环展开、JIT、Truffle |
| **D** | **归纳结构上的折叠**（Folds over Inductive Structures） | 程序是归纳定义的，所以一切关于程序的计算都是折叠 | 属性文法、语法制导翻译、类型检查、代码生成、recursion schemes |
| **E** | **唯一化与记忆化**（Hash-Consing & Memoization） | 用共享把“结构相等”降为“指针相等”，顺带把指数规模压成 DAG | 符号表、类型内部化、GVN、BDD、e-graph、packrat、增量编译 |
| **F** | **SCC 分解 + 拓扑序**（SCC Decomposition + Topological Order） | 把“需要迭代”的部分局部化到强连通分量内部 | 依赖顺序、递归绑定组、自然循环、过程间分析顺序、Datalog 分层 |
| **G** | **判定树与分派**（Decision Trees & Dispatch） | 一切多路选择都归约为构造判定树，权衡是表大小与判定深度 | 模式匹配编译、switch 降级、虚表、PIC、指令选择匹配器 |
| **H** | **模拟关系**（Simulation Relations） | 一切“变换正确”的证明都是构造一个模拟关系 | CompCert、翻译验证、Alive2、差分测试，以及 `L(D)=L(N)` 本身 |
| **I** | **需求驱动 / 查询式架构**（Demand-Driven / Query-Based Architecture） | 把编译器从 push 式的 pass 流水线改成 pull 式的查询 DAG | rustc queries、Salsa、Roslyn、增量解析、按需分析、构建系统 |
| **J** | **归约与逐层降级**（Reduction & Progressive Lowering，nanopass） | 不直接解决问题，而是把它翻译成一个已解决的问题 | 异常→CPS、OO→闭包、泛型→字典、协程→状态机、MLIR 渐进降级 |

最后 §11 会说明：**这十把锤子，加上前文的八把，归根结底只有五种机制。**

---

## 目录

- [0. 什么算“万能锤”：三条判据](#0-什么算万能锤三条判据)
- [A. 合一与约束求解](#a-合一与约束求解)
- [B. 控制流即数据：CPS 与状态机化](#b-控制流即数据cps-与状态机化)
- [C. 偏求值与分阶段：Futamura 投影](#c-偏求值与分阶段futamura-投影)
- [D. 归纳结构上的折叠，以及它与后端主锤的同一性](#d-归纳结构上的折叠以及它与后端主锤的同一性)
- [E. 唯一化与记忆化：hash-consing](#e-唯一化与记忆化hash-consing)
- [F. SCC 分解 + 拓扑序：不动点的通用加速器](#f-scc-分解--拓扑序不动点的通用加速器)
- [G. 判定树与分派：NFA→DFA 的孪生兄弟](#g-判定树与分派nfadfa-的孪生兄弟)
- [H. 模拟关系：正确性的万能锤](#h-模拟关系正确性的万能锤)
- [I. 需求驱动与查询式架构](#i-需求驱动与查询式架构)
- [J. 归约与逐层降级：最“元”的一把锤子](#j-归约与逐层降级最元的一把锤子)
- [K. 小锤集](#k-小锤集)
- [11. 全局归并：十八把锤子只有五种机制](#11-全局归并十八把锤子只有五种机制)
- [12. 锤子的反面：什么时候该放下它](#12-锤子的反面什么时候该放下它)
- [13. 自检、学习路径与文献](#13-自检学习路径与文献)

---

## 0. 什么算“万能锤”：三条判据

在继续之前，先确立标准，否则“万能锤”很容易退化为一份“技术清单”。

> **判据一：跨领域复现（Cross-Domain Recurrence）。** 至少在编译器的三个互不相邻的子领域中独立出现，例如类型系统、优化、运行时。
>
> **判据二：有统一的数学骨架（Unified Mathematical Skeleton）。** 不能只是“手法相似”，而要能写出一段**参数化的代码或一条定理**，各处应用只是它的不同实例化（Instantiation）。
>
> **判据三：解释力与预测力（Explanatory & Predictive Power）。** 能*事后解释*为什么某些看似无关的技术其实是同一个东西，并能**预测**新技术会长成什么样。

按这三条筛选，下面这些不算万能锤：

| 不算万能锤 | 原因 |
| ---------- | ---- |
| “位向量优化”（Bit-Vector Optimization） | 只是编码技巧，没有统一骨架（判据二不过） |
| “内联”（Inlining） | 单个变换，不跨领域（判据一不过） |
| “用哈希表加速” | 没有解释力（判据三不过） |
| “启发式 + 调参”（Heuristics + Tuning） | 这是**放弃**使用锤子之后的兜底方案，本身不是锤子 |

后文的十把锤子都能通过这三条判据。每一把都按同一结构展开：**骨架 → 钉子表（应用实例）→ 深层洞察 → 与已讨论锤子的连线**。

---

## A. 合一与约束求解

### A.1 骨架

**合一（Unification）**：给定两个含变量的项（Term）`t₁` 和 `t₂`，求一个**最一般合一子**（Most General Unifier, MGU），即代换（Substitution）`σ`，使得 `σ(t₁) = σ(t₂)`。

工业实现通常结合**并查集**（Union-Find，也称 Disjoint-Set）来维护等价类：

```python
def unify(a, b, subst, uf):
    a, b = uf.find(resolve(a, subst)), uf.find(resolve(b, subst))
    if a is b: return
    if is_var(a):
        occurs_check(a, b)            # ← 出现检查：防止 α = α → α 这种循环
        uf.union(a, b); return
    if is_var(b): return unify(b, a, subst, uf)
    if a.ctor != b.ctor or a.arity != b.arity:
        raise TypeError(f"cannot unify {a} with {b}")
    uf.union(a, b)                    # ★ 先合并再递归：打断循环 + 记忆化
    for x, y in zip(a.args, b.args):  # 同余规则（Congruence Rule）：结构相同则逐个合一
        unify(x, y, subst, uf)
```

**注意 `uf.union` 出现在递归之前。** 同样的技巧还出现在 §E 的 hash-consing、e-graph 的重建（rebuilding），以及 Braun 等人惰性 SSA 构造（Lazy SSA Construction）中“先写入占位 φ 节点、再递归填充操作数”的做法里。它们的共同点是：**先承诺假设，再验证，以此处理环**。这种“先假设后验证”的思路在逻辑上对应**协归纳**（Coinduction）。

**约束求解**（Constraint Solving）是合一的推广：不仅求解等式 `t₁ = t₂`，还求解：

- 包含约束（Inclusion Constraint）`t₁ ⊆ t₂`；
- 子类型约束（Subtyping Constraint）`t₁ <: t₂`；
- 谓词约束（Predicate Constraint）`C(t₁,…,tₙ)`，如类型类约束、trait 约束。

### A.2 钉子表

| 应用 | 约束形式 | 求解器 |
| ---- | -------- | ------ |
| **Hindley–Milner 类型推导**（HM Type Inference） | `τ₁ = τ₂` | 合一 + Union-Find；泛化（Generalization）/ 实例化（Instantiation） |
| **重载决议 / C++ 模板实参推导**（Overload Resolution / Template Argument Deduction） | `τ = f(?)`，带偏序 | 合一 + 偏特化排序（Partial Ordering of Specializations） |
| **Rust trait 求解 / Haskell 类型类**（Trait Solving / Type Classes） | `C τ₁ … τₙ` | **归约（Prolog 式 SLD 消解，SLD Resolution）** + 一致性检查（Coherence Check） |
| **局部类型推断**（Local Type Inference，Java/C#/Scala/TypeScript） | `τ₁ <: τ₂` | 双向定型（Bidirectional Typing）+ 约束图 + 变型求解（Variance Solving） |
| **GADT / 局部等式假设**（OutsideIn(X)） | 分层：先解简单约束，困难的推迟 | 约束生成与求解**分离** |
| **区域推断**（Region Inference，MLKit、早期 Rust） | 区域包含 `ρ₁ ⊆ ρ₂` | 包含约束的传递闭包（Transitive Closure） |
| **借用检查**（Borrow Checking，NLL） | 生命周期约束 `'a: 'b` | CFG 上的约束图 + 可达性（Reachability） |
| **模式匹配**（Pattern Matching） | **单向合一**（One-Way Unification，只有一侧有变量） | 匹配（Matching），线性时间 |
| **项重写 / 指令选择**（Term Rewriting / Instruction Selection） | 左部（LHS）匹配 | 判别网络（Discrimination Net）、e-matching |
| **e-graph 的 e-matching** | 模式 → e-class | 关系式查询，编译成 join 计划（Relational E-Matching） |
| **Steensgaard 指向分析**（Points-to Analysis） | **等式** `pts(p) = pts(q)` | **合一**，`O(n α(n))` |
| **Andersen 指向分析** | **包含** `pts(p) ⊇ pts(q)` | 约束图上的传递闭包，`O(n³)` |
| **SMT 求解器的 EUF 理论**（Equality with Uninterpreted Functions） | 等式 + 同余 | 同余闭包（Congruence Closure，§E） |
| **多面体调度**（Polyhedral Scheduling） | 仿射不等式（Affine Inequalities） | Farkas 引理 + 整数线性规划（ILP，后端大锤⑤） |

### A.3 深层洞察

> **洞察一：合一是“最快但最粗”的等价推导，包含约束是“更慢但更细”的版本。这又是一级近似阶梯（Approximation Ladder）。**
>
> |       | 合一（等式） | 包含（子集） |
> | ----- | ------------ | ------------ |
> | 指向分析 | **Steensgaard** `O(n α(n))` | **Andersen** `O(n³)` |
> | 类型系统 | HM（无子类型） | 带子类型的推断（`<:`） |
> | 精度损失 | `p = q` 强行**合并**两侧，方向信息丢失 | 保留方向 |
> | 前端对应物 | **SLR 使用全局 `FOLLOW` 集**（合并所有上下文） | **LR(1)** 的精确前看上下文 |
>
> 这与前文出现过的 `SLR → LALR → LR(1)`、`线性近似前看 → 完整前看`、`SLL → LL`、`MFP → MOP`（最大不动点解与全路径交汇解）、`上下文不敏感 → k-CFA` 是**同一条阶梯的第六次出现**。
>
> **合一就是把“有向的包含关系”塌缩成“无向的等价关系”。** 这正是反复出现的“把笛卡尔积压扁成投影”这一手法在**关系方向**维度上的版本。

> **洞察二：约束生成与约束求解分离，是现代类型系统的一次架构革命。**
>
> 传统 HM（Algorithm W）在遍历 AST 的同时进行合一。这带来几个问题：错误信息糟糕（错误常在离真实原因很远的地方报出）、无法处理 GADT 和局部等式、难以扩展。
>
> OutsideIn(X)（GHC）、Rust 的新 trait solver、Scala 3 的定型器都改成了两阶段：
>
> ```
> ① 遍历 AST，只生成约束（不求解），并记录每条约束的来源位置（provenance）
> ② 把约束集合整体交给求解器，按难度分层求解
> ```
>
> **好处**：错误信息可以归因（Blame Assignment）；约束可以推迟（Deferred Constraints）；求解器可插拔；还能与其他分析共享同一个求解器。
>
> 这与后端 SCCP（稀疏条件常量传播，Sparse Conditional Constant Propagation）所体现的原则相同：SCCP 把“常量”与“可达性”合并为一个积格（Product Lattice）联合求解，效果优于两者的顺序组合。也就是说，**耦合的决策应当交给一个统一求解器，而不是按顺序各自贪心**。

> **洞察三：出现检查（Occurs Check）就是在检测不动点计算中的非良基环（Non-Well-Founded Cycle）。**
>
> 关掉出现检查，得到的就是**递归类型**，更准确地说是等价递归类型（Equi-Recursive Types）。而判定递归类型是否相等，又需要**互模拟**（Bisimulation，§H），或者“Union-Find + 先假设后验证”。同一批工具再次出现。

### A.4 连线

```
合一的数据结构 = Union-Find = 后端大锤②的悲观合并方向（Pessimistic Merging）
合一的同余规则 = §E 的同余闭包（Congruence Closure）
合一处理环的技巧（先 union 再递归）= Braun 惰性 SSA 构造 = e-graph rebuilding
Steensgaard vs Andersen = 又一次“近似阶梯”母题
约束生成/求解分离 = SCCP 的“联合求解优于顺序组合”
模式匹配（单向合一）→ 编译成判定树 = §G
```

---

## B. 控制流即数据：CPS 与状态机化

### B.1 骨架

> **任何控制结构都可以被转换为“显式的状态数据 + 一个分派循环”（Dispatch Loop）。**

这句话有三种形态：

| 形态 | 把什么变成数据 |
| ---- | -------------- |
| **CPS 转换**（Continuation-Passing Style Transformation） | 把“接下来做什么”变成一个函数值，即续延（Continuation） |
| **去函数化**（Defunctionalization） | 把“函数值”变成标签加数据（tag + payload），函数调用变成 `switch` |
| **状态机化**（State-Machine Lowering） | 把“当前执行到哪里”变成一个整数状态变量，控制流变成 `loop { match state { … } }` |

三者是同一条流水线的三个阶段：

```
高阶控制流  ──CPS──>  续延作为一等函数  ──去函数化──>  标签 + 数据 + 分派循环
                                                         ↑
                                                    这就是一台状态机
```

### B.2 钉子表

| 应用 | 用到的阶段 | 备注 |
| ---- | ---------- | ---- |
| **CPS 转换**（Scheme/ML 编译器，如 SML/NJ、Orbit） | CPS | 尾调用（Tail Call）与 `call/cc` 几乎免费获得 |
| **ANF / 一元中间语言**（A-Normal Form / Monadic IR） | CPS 的“命名化”部分 | 所有操作数都变为原子（Atomic） |
| **SSA ≡ CPS**（Appel 1998；Kelsey 1995） | —— | φ 函数 ≡ 续延的参数；支配树（Dominator Tree）≡ 词法作用域嵌套 |
| **闭包转换**（Closure Conversion） | 去函数化的前半部分 | 把自由变量（Free Variables）打包成环境记录（Environment Record） |
| **去函数化**（Reynolds 1972） | 去函数化 | 高阶程序 → 一阶程序；也是偏求值（Futamura）的常见搭档 |
| **异常**（Exceptions） | CPS（双续延：正常 + 异常） | 也可降级为零成本方案：**表驱动的栈展开**（Table-Driven Unwinding），其中 `.gcc_except_table` 就是又一张判定表，见 §G |
| **生成器 / 迭代器**（Python `yield`、C# `yield return`） | 状态机化 | 每个 `yield` 点对应一个状态 |
| **async/await**（C#、Rust、Kotlin、JS） | 状态机化 | 每个 `await` 点对应一个状态 |
| **C++20 协程**（Coroutines） | 状态机化 | `coroutine_handle` + `resume` |
| **Kotlin 挂起函数**（Suspend Functions） | CPS + 状态机化 | 编译成额外的 `Continuation` 参数 + 状态字段 |
| **蹦床**（Trampolining） | 去函数化 + 分派循环 | 在没有尾调用优化（TCO）的平台上实现深递归 |
| **解释器的线索代码 / 计算 goto**（Threaded Code / Computed Goto） | 分派循环 | 把 `switch` 换成间接跳转，改善分支预测 |
| **效应处理器**（Effect Handlers，OCaml 5、Eff） | 分段 CPS | 一等续延（First-Class Continuations）的受限形式 |

### B.3 深层洞察：async/await 降级就是手写的 NFA → DFA

这是本文最强的一条连线。考虑下面这个 Rust 异步函数：

```rust
async fn f(x: u32) -> u32 {
    let a = g(x).await;          // 挂起点（Suspension Point）1
    let b = h(a).await;          // 挂起点 2
    a + b
}
```

编译器生成的代码（简化后）大致如下：

```rust
enum FState {
    Start { x: u32 },                     // 状态 0
    AwaitG { fut: GFut },                 // 状态 1：等待 g，只需保存 g 的 future
    AwaitH { a: u32, fut: HFut },         // 状态 2：等待 h，需额外保存 a ★
    Done,
}

impl Future for F {
    fn poll(&mut self, cx: &mut Context) -> Poll<u32> {
        loop {                                     // ← 分派循环
            match &mut self.state {                // ← 状态转移表
                Start { x } => {
                    let fut = g(*x);
                    self.state = AwaitG { fut };   // δ(0, ·) = 1
                }
                AwaitG { fut } => match fut.poll(cx) {
                    Poll::Pending  => return Poll::Pending,   // 让出：状态被保存
                    Poll::Ready(a) => {
                        let fut = h(a);
                        self.state = AwaitH { a, fut };       // δ(1, ready) = 2
                    }
                },
                AwaitH { a, fut } => match fut.poll(cx) {
                    Poll::Pending  => return Poll::Pending,
                    Poll::Ready(b) => { let r = *a + b;
                                        self.state = Done;
                                        return Poll::Ready(r); }  // 接受态
                },
                Done => panic!("polled after completion"),
            }
        }
    }
}
```

**逐项对照**：

| NFA → DFA / DFA 词法分析器 | async/await 降级 |
| -------------------------- | ---------------- |
| DFA 状态 | `enum FState` 的一个变体（Variant） |
| 转移表 `δ[state][char]` | `match state { … }` 分派 |
| 主循环 `while (c = next()) { state = δ[state][c]; }` | `loop { match &mut self.state { … } }` |
| 输入符号 | 一次 `poll` 调用（外部事件） |
| 接受态（Accepting State） | `Poll::Ready` |
| **DFA 状态携带的附加信息**（token 标签、优先级） | **状态变体携带的活跃变量**（`a` 必须存进 `AwaitH`） |
| 状态可以保存为一个整数（增量词法分析可以跨行续扫） | 状态机可以保存在堆上（协程可以跨线程恢复） |

> **关键问题**：“状态变体里要存哪些变量？”答案是**在该挂起点处活跃的变量集合**（Live Variables）。也就是说：
>
> ```
> async/await 降级 = 状态机化（锤 B）
>                  + 每个挂起点的活跃变量分析（后端主锤：数据流分析）
>                  + 状态布局 / 联合体优化（按状态求最大同时活跃集，类似 MAXLIVE）
> ```
>
> **三把锤子在同一个语言特性上组合。** 这也解释了两个现象：一是 Rust 的 `Future` 大小等于各挂起点活跃集的“并集式布局”（各变体共用存储，类似 union）；二是“在跨越 `.await` 的位置持有大对象”会让 Future 变大。后者其实就是**寄存器分配中的溢出问题（Spilling）在协程状态布局上的重演**。

> **洞察二：去函数化就是把高阶控制流“确定化”。**
>
> ```
> 高阶函数值 = “接下来可能做的事”，是一个不确定的集合
> 去函数化   = 枚举程序中所有可能的续延形态，编号，用 switch 分派
>            = 把“不确定的间接跳转”变成“有限、可枚举的多路分支”
> ```
>
> **这与子集构造做的是同一件事**：都把“运行时的不确定选择”换成“编译期枚举 + 表驱动分派”。代价也相同，即**控制流爆炸**：去函数化后的 `switch` 可能非常大，而且失去模块性，因为需要**全程序**（Whole-Program）信息才能枚举所有续延，就像子集构造需要完整的 NFA 才能确定化。
>
> 反方向的选择同样存在：**保留间接调用（不去函数化）对应直接模拟 NFA**；用 **PIC / 内联缓存**（Polymorphic Inline Cache / Inline Cache）在运行期按需特化，则对应 **lazy DFA**（惰性 DFA）。

### B.4 连线

```
CPS ≡ SSA            → 后端大锤①（同一表示的两种语法）
状态机化 ≡ NFA→DFA   → 前端主锤
去函数化 ≡ 确定化     → 前端主锤；其反面（PIC）≡ lazy DFA
挂起点活跃变量        → 后端主锤（数据流分析）
状态布局             → 后端大锤④（与寄存器分配同构的问题）
异常表 / unwind 表   → §G（判定表）
```

---

## C. 偏求值与分阶段：Futamura 投影

### C.1 骨架

**偏求值器**（Partial Evaluator，传统上记作 `mix`）的定义：

```
mix(p, s) = p_s        使得   ∀d.  p_s(d) = p(s, d)
                              ↑ 把已知的输入 s “烧进”程序里
```

其中 `p_s` 称为**残余程序**（Residual Program），`s` 是静态输入（Static Input），`d` 是动态输入（Dynamic Input）。

**Futamura 三投影**（Futamura Projections，1971）：

```
第一投影：  mix(interp, prog)  =  target        —— 编译！
           对解释器做偏求值 = 编译该程序

第二投影：  mix(mix, interp)   =  compiler      —— 编译器生成器！
           对 mix 自身做偏求值 = 从解释器自动得到编译器

第三投影：  mix(mix, mix)      =  cogen         —— 编译器生成器的生成器
```

> **这是编译原理中最深刻的定理之一**：它说明**编译器不是一个独立的东西，而是“解释器 + 偏求值”的自动产物**。GraalVM/Truffle 就是这条定理的工业实现：用户只写 AST 解释器，Graal 通过偏求值得到编译后的机器码。

### C.2 钉子表：这些“不同的优化”是同一个操作

| 优化 | 被“烧进”程序的已知输入 |
| ---- | ---------------------- |
| **常量折叠**（Constant Folding） | 操作数的值 |
| **常量传播**（Constant Propagation） | 变量在此处的值 |
| **内联**（Inlining） | 调用点的实参，尤其是常量实参和函数实参 |
| **循环展开**（Loop Unrolling） | 循环计数器的具体值 |
| **循环剥离**（Loop Peeling） | 前几次迭代的索引 |
| **单态化**（Monomorphization，Rust/C++ 模板） | **类型参数** |
| **字典传递的特化**（Dictionary-Passing Specialization） | 类型类实例 |
| **宏展开 / `constexpr` / `comptime`** | 编译期已知的一切（Zig 的 `comptime` 是显式的偏求值） |
| **模板实例化**（Template Instantiation） | 模板实参 |
| **去虚化 + 内联**（Devirtualization + Inlining） | 接收者的具体类型 |
| **JIT 值特化**（Value Specialization） | 运行时观测到的实参值 |
| **追踪 JIT**（Trace JIT） | 一整条已观测的执行路径（把分支结果烧进去，并加守卫 guard） |
| **Truffle / Graal** | **AST 解释器 + 用户程序 ⇒ 编译后代码**（字面意义上的第一投影） |
| **Halide/TVM 的调度应用**（Schedule Application） | 调度参数（tile 大小、展开因子） |
| **`printf` 格式串特化** | 格式字符串 |
| **正则表达式编译** | **正则式本身**（对 `match(regex, text)` 关于 `regex` 做偏求值 = 生成 DFA） |
| **数据库查询编译**（Query Compilation） | SQL 语句 |
| **simdjson / 结构索引**（Structural Indexing） | 输入的结构特征 |

> **注意“正则表达式编译”这一行**：正则匹配本身就是一个解释器 `interp(regex, text)`。对 `regex` 做偏求值，就得到一个专用的匹配程序，而这**正是 NFA→DFA + 代码生成**。
>
> 换句话说，**前端的万能锤是偏求值这把锤子的一个实例。** 词法分析器生成器相当于对“正则解释器”做第二投影；语法分析器生成器相当于对“通用 CFG 解析器（Earley/GLL）”做第二投影。这解释了为什么“生成器”（flex、bison、ANTLR、BURG）这种形态在编译器领域如此普遍。

### C.3 深层洞察

> **洞察一：绑定时间分析（Binding-Time Analysis, BTA）就是一种数据流分析。**
>
> 偏求值的第一步，是判断每个表达式是 **static**（编译期可计算）还是 **dynamic**（必须留到运行时）。这是在一个两点格 `static ⊑ dynamic` 上的正向单调不动点计算，是**后端主锤的直接实例**。
>
> ```
> BTA 的格：  {static, dynamic}，static ⊑ dynamic
> 传递函数：  一个操作是 static ⟺ 它的所有操作数都是 static
> 汇合：      join = 取 dynamic（只要有一个 dynamic，整体就是 dynamic）
> ```
>
> 它与常量传播的格 `⊤ ⊒ const ⊒ ⊥` 结构相同。事实上，**BTA 是常量传播的“是否已知”投影**：丢掉具体值，只保留“知不知道”。这又是一次投影近似。

> **洞察二：偏求值的核心难题是终止性，其解法与加宽（Widening）完全同构。**
>
> ```
> 偏求值的爆炸： 展开递归函数时，若参数始终是 static，可能无限展开
> 数据流的爆炸： 区间格高度无限，Kleene 迭代不收敛
> ```
>
> 两者的解法也相同：
>
> | 偏求值 | 数据流分析 | 共同动作 |
> | ------ | ---------- | -------- |
> | **泛化**（Generalization）：把某个 static 参数**主动降级为 dynamic** | **加宽 `∇`**：把区间**主动扩到 `±∞`** | 主动丢弃精度以保证终止 |
> | 展开预算 / 内联深度阈值 | `k`-limiting / `k`-CFA 截断 | 有界化（Bounding） |
> | Truffle 的 `@ExplodeLoop` 与编译边界 `@TruffleBoundary` | 手动指定加宽点 | 人工标注在哪里停止 |
>
> 前文讲过的 **LL(\*) 用 DFA 自环来抽象 `b*`**，也是同一个动作。这是“有界化 / 加速收敛”母题的第四次出现。

> **洞察三：JIT 就是以运行时值为 static 输入的在线偏求值（Online Partial Evaluation），再加上守卫。**
>
> ```
> 静态偏求值： static 输入必须在编译期已知 ⇒ 能特化的东西很少
> JIT：       把“运行期观测到的值/类型”当作 static ⇒ 能特化的东西极多
>             代价：观测可能失效 ⇒ 必须加守卫（Guard）+ 去优化（Deoptimization）
> ```
>
> **ANTLR 4 的 ALL(\*) 就是这件事在解析器上的实现**：它把“眼前这串 token 和当前具体的调用栈”当作 static 输入，在线特化出一个前看 DFA 并缓存起来。
>
> 因此，前文“JIT ≡ ALL(\*)”的说法可以升级为更准确的表述：**两者都是“以运行时信息为 static 输入的在线偏求值 + 记忆化 + 可检测失败的退路”。**

### C.4 连线

```
BTA                     → 后端主锤（数据流分析）
泛化 / 展开预算          → 加宽 / k-limiting（有界化母题）
第二投影                 → 解释了“生成器”（flex/bison/ANTLR/BURG）这种形态
对 regex 偏求值           → 前端主锤（NFA→DFA + 代码生成）
JIT = 在线偏求值          → 后端大锤⑥ + ALL(*)
记忆化（避免重复特化）     → §E
分阶段编程（Multi-Stage Programming，显式 static/dynamic）→ 把 §J 的“降级”交给用户控制
```

---

## D. 归纳结构上的折叠，以及它与后端主锤的同一性

### D.1 骨架

程序（AST、类型、IR）都是**归纳定义**（Inductively Defined）的。因此，一切关于程序的计算，都可以看作在其归纳结构上的**折叠**（Fold，范畴论中称 Catamorphism）：

```
fold : (代数 F A → A) → μF → A
```

这里 `μF` 是函子 `F` 的最小不动点（即归纳数据类型本身），“代数”（F-Algebra）规定了每种构造子如何组合子结果。

在编译器中，折叠最常见的具体形式是**属性文法**（Attribute Grammar, Knuth 1968）：

```
综合属性（Synthesized Attribute）：  自下而上 —— 子节点 → 父节点
继承属性（Inherited Attribute）：    自上而下 —— 父节点/兄弟节点 → 子节点
```

| 属性文法种类 | 遍历方式 | 与解析的关系 |
| ------------ | -------- | ------------ |
| **S-属性文法**（只有综合属性） | 一遍自底向上 | 可以在 **LR 规约动作**中直接求值 |
| **L-属性文法**（继承属性只依赖左兄弟和父节点） | 一遍从左到右深度优先 | 可以在 **LL 递归下降**中直接求值 |
| **一般属性文法** | 多遍，或按依赖排序 | 需要拓扑序（§F） |
| **循环属性文法**（Circular Attribute Grammar） | **需要不动点迭代** | 关键，见 §D.3 |

### D.2 钉子表

| 应用 | 综合属性 | 继承属性 |
| ---- | -------- | -------- |
| **类型检查** | 表达式的类型 | 期望类型（即双向定型的 checking 模式） |
| **常量折叠** | 子表达式的常量值 | —— |
| **代码生成** | 生成的指令序列、结果寄存器 | 目标寄存器、跳转标签 |
| **Sethi–Ullman 编号** | 所需寄存器数 | —— |
| **短路布尔表达式翻译**（Short-Circuit Translation） | —— | `trueLabel` / `falseLabel`（经典的 L-属性） |
| **作用域 / 符号表** | 声明的符号 | 当前环境（Environment） |
| **`nullable/firstpos/lastpos`**（龙书 §3.9.5，正则直接构造 DFA） | 全部是综合属性 | —— |
| **`FIRST` 集合** | 综合 | —— |
| **`FOLLOW` 集合** | —— | 继承（并且**有环 ⇒ 需要迭代**） |
| **树模式匹配 / BURS 标号**（Bottom-Up Rewrite System Labeling） | `cost[nt]` | 选中的规则（第二遍自顶向下） |
| **MLIR / LLVM 的模式重写**（Pattern Rewrite） | —— | 折叠 + 重写的组合 |
| **Recursion schemes**（Haskell） | cata | ana / para / histo… |
| **JastAdd / Silver / Kiama** | 引用属性文法（Reference Attribute Grammar, RAG），属性可以指向其他节点 | 支持循环属性 |

### D.3 深层洞察：树上的折叠 = 图上的不动点

> **这是本文最重要的洞察，它解释了为什么后端主锤是必然出现的。**

```
结构是树（无环）     ⇒  依赖关系是偏序  ⇒  一遍拓扑序遍历即可求值  = 折叠
结构是 DAG           ⇒  依赖仍是偏序    ⇒  拓扑序 + 记忆化         = 折叠 + hash-consing（§E）
结构有环（CFG/递归）  ⇒  依赖有环        ⇒  拓扑序不存在
                                        ⇒  **必须迭代到不动点**   = 后端主锤
```

**证据链**：

| 计算 | 结构 | 方法 |
| ---- | ---- | ---- |
| `FIRST` 集 | 文法依赖图（左递归会造成环） | 迭代到不动点 |
| `FOLLOW` 集 | 有环 | 迭代到不动点 |
| `ε-closure` | NFA 的 ε 转移图（有环） | 迭代到不动点（工作栈） |
| `nullable/firstpos/followpos` | 正则式的**语法树**（无环） | **一遍折叠** ✔ |
| 类型检查（非递归类型） | AST（树） | **一遍折叠** ✔ |
| 类型检查（递归类型 / 递归函数组） | 依赖图（有环） | **在 SCC 内迭代**（§F） |
| 数据流分析 | CFG（有环） | 迭代到不动点 |
| 支配关系 | CFG（有环） | 迭代到不动点 |
| Sethi–Ullman 编号 | 表达式树 | **一遍折叠** ✔ |
| BURS 标号 | 表达式树 | **一遍折叠** ✔ |
| e-graph 提取（Extraction） | e-graph（**有环**） | 迭代到不动点，或使用专门算法 |

> **结论**：**折叠与不动点迭代不是两把锤子，而是同一把锤子在“无环”与“有环”两种结构上的两种形态。**
>
> ```
> fold  =  在良基（Well-Founded）结构上的不动点计算，恰好一遍收敛
> lfp   =  在非良基结构上的折叠，需要多遍才收敛
> ```
>
> 由此得到一条实用的**设计诊断法**：**当你的分析“需要迭代”时，先问依赖图里的环从哪里来。** 如果能通过换表示消除环（例如 SSA 把变量间的环变成 φ 节点的显式边；SCC 分解把环局部化），迭代就退化为一遍折叠。

> **洞察二：双向定型（Bidirectional Typing）就是“综合属性 + 继承属性”的重新发现。**
>
> ```
> Γ ⊢ e ⇒ τ     （synthesis，推断/综合模式）   ← 综合属性
> Γ ⊢ e ⇐ τ     （checking，检查模式）         ← 继承属性
> ```
>
> 双向定型之所以能处理 HM 处理不了的东西（高阶多态 Higher-Rank Polymorphism、GADT、字面量重载），正是因为它**引入了继承属性**，让期望类型自上而下流动。而“哪种语法构造该用哪种模式”的设计原则，本质上是在设计一个 **L-属性文法**，以保证一遍从左到右即可求值。
>
> 反过来，**HM 之所以只需要综合属性**，是因为它把所有“自上而下的信息”都推迟成了合一变量（§A），也就是**用约束求解替代继承属性**。这是两条不同的设计路线：
>
> ```
> HM：       全部用综合属性 + 合一变量 + 全局求解   → 推断能力强，错误信息差
> 双向定型： 综合 + 继承属性，局部即时检查          → 推断能力受限，错误信息好，易扩展
> ```

### D.4 连线

```
折叠 ↔ 不动点               → 后端主锤（同一把锤子的两种结构形态）
L-属性 ↔ LL、S-属性 ↔ LR    → 前端（属性求值策略与解析策略相匹配）
双向定型 ↔ 继承/综合属性     → §A（约束求解是另一条路线）
循环属性文法                 → 后端主锤 + §F（SCC）
折叠 + 记忆化                → §E（DAG 上的折叠）
```

---

## E. 唯一化与记忆化：hash-consing

### E.1 骨架

**Hash-consing**（得名于 Lisp 的 `cons`，也称驻留 Interning、唯一化 Uniquing）的核心实现非常简短：

```python
class HashCons:
    def __init__(self): self.table = {}          # 结构 → 唯一实例
    def mk(self, op, *args):                     # args 已经是唯一实例（指针）
        key = (op, tuple(id(a) for a in args))   # ★ 用指针而非结构做 key
        if key not in self.table:
            self.table[key] = Node(op, args)
        return self.table[key]                   # 结构相同 ⇒ 返回同一个对象
```

**不变式**（Invariant）：`结构相等 ⟺ 指针相等`。

由于子节点已经唯一化，构造 key 只需要常数时间，不必递归比较结构。由此自动获得三个好处：

1. **相等判定从 `O(n)` 降到 `O(1)`**；
2. **表示从树变成 DAG**：共享子结构后，指数大小的项可能只占多项式空间；
3. **记忆化的天然键**：可以直接用指针做缓存表的 key。

### E.2 钉子表

| 应用 | 被唯一化的对象 | 收益 |
| ---- | -------------- | ---- |
| **字符串驻留 / 符号表**（String Interning） | 标识符 | 名字比较 `O(1)` |
| **类型内部化**（Type Interning：LLVM `Type`、rustc `Ty<'tcx>`、GHC） | 类型 | **类型相等 `O(1)`**，对泛型密集的代码至关重要 |
| **常量池 / `ConstantExpr`** | 常量 | 去重 + `O(1)` 比较 |
| **CSE / GVN**（公共子表达式消除 / 全局值编号） | 值 | 本质上就是对值做 hash-consing |
| **BDD / ZDD**（二元判定图 / 零抑制判定图） | 判定图节点 | 布尔函数的规范形式（Canonical Form）；`O(1)` 判定等价 |
| **E-graph** | e-node（在 e-class 意义下唯一化） | 见前文 §3.4；`rebuild` 就是在维护 hash-cons 不变式 |
| **DFA 状态去重**（子集构造中的 `if T not in index`） | NFA 状态子集 | **这就是 hash-consing** |
| **LR 项目集去重** | 项目集（Item Set） | 同上 |
| **GSS / SPPF**（图结构栈 / 共享压缩解析森林） | 栈节点 / 解析森林节点 | 把指数多的栈或树压成 DAG |
| **Packrat 备忘表** | `(规则, 位置)` | 线性时间的 PEG 解析 |
| **动态规划表**（DP Table） | 子问题 | 前文 §4 的所有动态规划 |
| **增量编译**（Salsa/rustc） | 查询结果 | 见 §I |
| **AST 去重 / 代码克隆检测**（Clone Detection） | 子树 | 后缀自动机（Suffix Automaton）也是一种最小 DFA |
| **ICF**（Identical Code Folding，相同代码折叠，链接器 lld/gold 提供） | 函数体 | 减小二进制体积 |

### E.3 深层洞察

> **洞察一：子集构造里的“状态去重”就是 hash-consing。**
>
> 回看前文的子集构造代码：
>
> ```python
> T = frozenset(eps_closure(move(S, a)))
> if T not in index:                    # ← hash-cons 查表
>     index[T] = len(dfa_states)        # ← 分配唯一 id
>     dfa_states.append(T)
> delta[(index[S], a)] = index[T]       # ← 之后只使用 id（相当于指针）
> ```
>
> **“DFA 状态 = NFA 状态子集”这句话之所以成立，完全依赖 hash-consing 保证“同一个子集只对应一个状态”。** 否则 DFA 会无限增长，因为每次重新算出同一个子集都会新建一个状态。
>
> 同理：
>
> - LR 项目集规范族构造中的 `if GOTO(I,X) ∉ C` 是 hash-consing；
> - ANTLR 4 的 `dfa.addState(D)`（已存在则复用）是 hash-consing；
> - e-graph 的 `hashcons` 表是 hash-consing；
> - GSS 的节点共享是 hash-consing。
>
> **结论：凡是“以状态集合作为状态”的构造，都必须配一张 hash-cons 表。** 这是判据三（解释力）的一个好例子：它解释了这些算法为什么长得这么像。

> **洞察二：hash-consing + 不动点 = 终止性保证。**
>
> ```
> 不动点迭代要终止，需要“格高度有限”
> hash-consing 保证“结构相同的对象只有一个”
> ⇒ 状态空间从“无限多的结构”降为“有限多的唯一实例”
> ⇒ 只要唯一实例数有上界，迭代就必然终止
> ```
>
> 这一组合被反复使用：e-graph 中 `rebuild` 维护同余不变式，使 e-class 数量单调有界；Datalog 对元组去重，在有限论域下必然终止；合一中 Union-Find 的等价类数量单调递减。

> **洞察三：代价是“全局表 + 弱局部性 + 难以并行”。**
>
> hash-consing 并不免费：
>
> | 代价 | 后果 | 应对 |
> | ---- | ---- | ---- |
> | 全局哈希表 | 并行编译时成为争用点（Contention） | 分片；每线程 arena + 合并；rustc 的 `Sharded<T>` |
> | 缓存不友好 | 指针追逐（Pointer Chasing） | Arena 分配 + 索引化（用 `u32` 索引代替指针） |
> | 无法原地修改 | 数据必须是持久化的（Persistent） | 与函数式 IR 天然契合，与可变 IR 冲突 |
> | 表本身占内存 | 长生命周期的编译器进程（如 IDE 后台）会不断累积 | GC、分代驱逐、`clearDFA()` 式清理 |
>
> **这解释了为什么 LLVM 只对 `Type` 和 `Constant`（不可变、体积小、比较频繁）做唯一化，而对 `Instruction` 不做。** 判断标准是：**“相等判定的频率” × “结构比较的代价”是否超过“维护全局表的代价”。**

### E.4 连线

```
hash-consing → 前端主锤的必要组件（状态去重）
             → 后端大锤②（GVN = 对值做 hash-cons；e-graph = 模等价意义下的 hash-cons）
             → §D（DAG 上的折叠 = 折叠 + 记忆化）
             → §I（增量编译 = 记忆化 + 失效）
             → 与不动点组合 ⇒ 终止性保证
```

---

## F. SCC 分解 + 拓扑序：不动点的通用加速器

### F.1 骨架

**Tarjan 强连通分量算法**（Tarjan's SCC Algorithm，1972）以 `O(V+E)` 的时间，用一遍深度优先搜索（DFS）求出所有强连通分量（Strongly Connected Component, SCC），并且**输出顺序恰好是逆拓扑序**（Reverse Topological Order）。

通用用法如下：

```python
def solve_by_scc(graph, transfer, join):
    sccs = tarjan_scc(graph)                  # 按逆拓扑序输出
    result = {}
    for comp in reversed(sccs):               # 按拓扑序处理
        if len(comp) == 1 and not self_loop(comp[0]):
            result[comp[0]] = transfer(comp[0], result)   # ★ 一遍即可，无需迭代
        else:
            iterate_to_fixpoint(comp, transfer, join, result)  # ★ 仅在环内迭代
    return result
```

> **核心价值**：**把“需要迭代”的部分从整个图缩小到单个 SCC 内部**，SCC 之间只需按拓扑序走一遍。对典型程序而言，大多数依赖是无环的，因此迭代次数可以从 `O(图直径)` 降到 `O(最大 SCC 直径)`。

### F.2 钉子表

| 应用 | 图是什么 | SCC 意味着什么 |
| ---- | -------- | -------------- |
| **模块 / 编译单元顺序** | import 图 | 循环依赖（需要报错或特殊处理） |
| **链接顺序 / 静态库** | 符号依赖图 | 循环依赖（需要 `--start-group`） |
| **构建系统**（make/ninja/Bazel） | 文件依赖图 | 循环依赖即错误 |
| **递归绑定组**（Recursive Binding Groups，ML/Haskell 的 `let rec`） | 变量引用图 | **必须一起做类型推导**，且**组内不泛化、组间才泛化** |
| **递归类型 / 类层次** | 类型引用图 | 递归类型；循环继承即错误 |
| **静态初始化顺序** | 初始化依赖图 | C++ 的静态初始化顺序问题（Static Initialization Order Fiasco） |
| **自然循环识别**（Natural Loop Detection） | CFG | **循环 = SCC**（不可归约流图 Irreducible CFG 只能依靠 SCC 识别，无法依靠支配关系的回边） |
| **循环嵌套森林**（Loop Nesting Forest） | CFG | 递归 SCC 分解（Havlak / Ramalingam） |
| **过程间分析顺序**（Interprocedural Analysis Order） | 调用图（Call Graph） | **自底向上分析非递归部分（每个函数一遍生成 summary），只在递归 SCC 内迭代** |
| **Datalog 求值** | 谓词依赖图 | **分层（Stratification）**；否定必须跨层 |
| **数据流分析的迭代顺序** | CFG | RPO 序 + SCC ⇒ 迭代次数最优 |
| **Andersen 指向分析加速** | 约束图（**动态变化**） | **在线 SCC 检测**（Pearce–Kelly）+ **环折叠**（Cycle Collapsing）是 Andersen 能扩展到大规模程序的关键 |
| **类型类实例一致性** | 实例依赖 | 循环即无法归约 |
| **rustc 的 trait 求解** | obligation 图 | 循环需要按协归纳（coinductive）处理，或者报错 |

### F.3 深层洞察

> **洞察一：SCC 分解是“迭代次数”这一母题的通用答案。**
>
> 前文讨论了“状态爆炸”和“NP 难”这两个效率维度，而**迭代次数**是第三个独立的效率维度：
>
> | 措施 | 效果 |
> | ---- | ---- |
> | 朴素工作表（Worklist） | 迭代次数取决于访问顺序，可能很糟 |
> | **RPO 序**（Reverse Post-Order，逆后序） | 对正向分析，迭代次数约等于循环嵌套深度 + 2 |
> | **SCC 分解 + 组内迭代** | 迭代被局部化；SCC 之间零迭代 |
> | **优先级工作表**（按 RPO 编号排序的 Worklist） | 实践中最快；LLVM 和 GCC 都采用 |
>
> **一个实用结论**：如果数据流分析很慢，**先检查迭代顺序**。这通常比优化传递函数（Transfer Function）收益大得多。

> **洞察二：Andersen 指向分析的“环折叠”是 SCC 与合一的汇合点。**
>
> ```
> Andersen 使用包含约束 pts(p) ⊇ pts(q)，比 Steensgaard 精确但更慢
> 但是：若约束图中 p 和 q 处在同一个 SCC 里（互相包含）
>     ⇒ pts(p) = pts(q) 必然成立
>     ⇒ 可以把它们“折叠”成一个节点（也就是合一）
>     ⇒ 不损失任何精度，却能大幅缩小图
> ```
>
> **这是“精确方法借用近似方法的技巧且不损失精度”的漂亮例子**：`包含约束 + SCC 折叠` 在环上退化为 `合一`，但只在**可证明等价**的地方退化。
>
> 前端有对应物吗？有：**Pager 的弱兼容合并**（Weak Compatibility，Menhir 使用）。它只在**可证明不会产生新冲突**时才合并 LR(1) 状态，从而得到“接近 LALR 的状态数 + LR(1) 的识别能力”。**两者是同一种策略：只在无损处合并。**

> **洞察三：递归绑定组解释了一个语言设计上的历史谜题。**
>
> ML 的 `let rec f … and g …` 为什么必须显式写 `and`？Haskell 为什么不需要？
>
> ```
> ML：  要求程序员显式给出绑定组 ⇒ 编译器不必求 SCC
> Haskell/Rust，以及 OCaml 的模块级： 编译器自动求 SCC ⇒ 程序员可以按任意顺序书写
> ```
>
> 而**组内不泛化、组间才泛化**是 HM 的关键规则，它直接对应于“按 SCC 拓扑序处理，组内迭代到不动点之后再泛化”。**语言的语法规则，往往是算法结构的外化。**

### F.4 连线

```
SCC → 后端主锤的加速器（迭代局部化）
    → §D（有环 ⇒ 需迭代；SCC 把环隔离出来，其余部分退化为折叠）
    → §A（环折叠 = 在可证明等价处退化为合一）
    → Pager 弱兼容合并（只在无损处合并，同一策略）
    → 自然循环 / 循环嵌套森林（后端大锤⑤的前提）
```

---

## G. 判定树与分派：NFA→DFA 的孪生兄弟

### G.1 骨架

**问题**：给定一个“值”和一组“候选”，尽快确定命中哪一个候选。

**通用解法**：构造一棵**判定树**（Decision Tree），或者它的表格化形式。每个内部节点测试一个“位置”，边按测试结果分叉。

**通用权衡**（本节的核心）：

```
        判定树 / 完全展开的表            回溯自动机 / 部分表
        ─────────────────────            ──────────────────
时间     每个位置最多测一次，O(depth)      可能重复测试，最坏 O(候选数 × depth)
空间     可能指数爆炸                      与候选总大小成线性
对应     DFA                              NFA 模拟
实例     Maranget 判定树 / flex -Cf       Le Fessant–Maranget 回溯自动机 / flex 默认压缩表
```

### G.2 深层洞察：模式匹配编译 ≡ 子集构造

这是本文第二强的连线。ML/Haskell/Rust 的模式匹配编译算法（Maranget 2008）如下：

```
输入：子句矩阵 P（Clause Matrix，每行是一个子句的模式向量），
      以及每一列对应的“位置”（Occurrence，即被匹配值中的访问路径）

① 若 P 没有行            ⇒ 匹配失败（编译期发出“非穷尽”警告）
② 若第一行全是通配符      ⇒ 成功，选择该子句                    ← 第一匹配语义（First-Match）
③ 否则：选择一列 i（启发式）
     对列 i 中出现的每个构造子 c：
         构造特化矩阵 S(c, P)（Specialized Matrix）：
             保留列 i 能匹配 c 的行，并把 c 的子模式展开为新列
         递归
     构造默认矩阵 D(P)（Default Matrix）：
             保留列 i 为通配符的行，删除列 i
         递归（处理未列出的构造子）
```

**与子集构造逐项对照**：

| 子集构造 / 词法分析器 | 模式匹配编译 |
| --------------------- | ------------ |
| DFA 状态 = **仍然可行的 NFA 状态集合** | 判定树节点 = **仍然可行的子句集合**（矩阵的行集） |
| `move(S, a)`：所有候选沿符号 `a` 推进一步 | **`S(c, P)`：所有候选沿构造子 `c` 特化一步** |
| `ε-closure`：展开可省略的中间步骤 | 子模式展开为新列 |
| “其他字符”的转移 | **默认矩阵 `D(P)`** |
| 接受态（子集包含某条规则的接受态） | 第一行全为通配符（该子句命中） |
| **规则优先：取子集中序号最小者** | **第一匹配语义：取矩阵中最上面的行** ✔ 完全一致 |
| DFA 状态去重（hash-consing） | 判定树节点共享（DAG 化）⇒ 代码体积可控 |
| **完全展开的表 vs 压缩表 + 失败链** | **判定树 vs 回溯自动机** |
| 状态爆炸 `2ⁿ` | **判定树体积爆炸**（同一列被多次测试） |
| —— | **列选择顺序影响树的大小，最优选择是 NP 难的** |

> **两个补充知识点**：
>
> 1. **“最优列选择是 NP 难的”与“BDD 最优变量顺序是 NP 难的”是同一个问题。** Maranget 给出了一组启发式（`needed prefix`、`small default`、`arity` 等），与 BDD 的 sifting 启发式在思路上一致。
> 2. **穷尽性检查（Exhaustiveness Checking）与冗余检查（Redundancy / Usefulness Checking）是同一个算法的副产品**：矩阵 `P` 为空但仍有构造子未被覆盖 ⇒ 非穷尽；某一行永远不会被选中 ⇒ 冗余（不可达模式，Unreachable Pattern）。
>    **这与词法分析器中“某条规则永远匹配不到”的诊断（flex 的 `rule cannot be matched` 警告）是同一种诊断**，含义都是：该候选在所有判定路径上都被更早的候选遮蔽了。

### G.3 钉子表

| 应用 | 测试什么 | 表格化形式 | 权衡 |
| ---- | -------- | ---------- | ---- |
| **模式匹配编译** | 构造子标签 | 判定树 / 回溯自动机 | 代码体积 vs 重复测试 |
| **`switch` 降级**（Switch Lowering） | 整数值 | 跳转表 / 二分树 / 位测试 / 完美哈希 | LLVM 按密度自动选择（见下） |
| **词法分析** | 字符 | DFA 表 | flex `-Cf` vs 压缩表 |
| **指令选择匹配** | 树形状 | BURG 表 / LLVM SelectionDAG 的 `MatcherTable` 字节码 | 见前文 §4.1 |
| **虚方法分派**（Virtual Dispatch） | 对象的类 | vtable（单继承下 `O(1)`） | 多继承 / 接口需要 itable 或搜索 |
| **接口分派**（Interface Dispatch） | 类 × 接口 | itable / 二维稀疏表 / 哈希 | Go 的 itab 缓存、JVM 的 `invokeinterface` |
| **PIC（多态内联缓存）** | 类 | **运行期逐步增长的小判定树** | **它是 lazy DFA 的对应物** |
| **类型测试 / `instanceof`** | 类层次 | 区间编码（Cohen/Schubert 编号）、位集 | 层次编码使判定为 `O(1)` |
| **异常表栈展开** | PC 范围 | `.gcc_except_table` / `.eh_frame` | 零成本异常处理（Zero-Cost EH）：正常路径无开销，异常路径查表 |
| **安全点 / GC 栈图**（Safepoint / Stack Map） | PC | 每个安全点的活跃指针位图 | 表大小 vs 精度 |
| **调试信息行号映射** | PC | DWARF 行号程序（**它本身就是一个字节码解释器**） | 极致压缩 |
| **CPU 分支预测器** | 分支历史 | —— | 同一权衡的硬件版本 |

**`switch` 降级的具体决策**（LLVM `SwitchLoweringUtils`）是“表 vs 树”权衡的教科书实例：

```
case 值集合的密度 = case 数 / (max - min + 1)

密度高（约 ≥ 40%）且 case 数 ≥ 4  ⇒ 跳转表（Jump Table）：O(1)，但有间接跳转（预测差）
所有 case 值能放进一个机器字       ⇒ 位测试（Bit Test）：O(1)，无间接跳转 ★
case 数少 / 分布稀疏              ⇒ 二分搜索树（Binary Search Tree）：O(log n)，分支可预测
case 集中包含大段连续区间          ⇒ 区间比较（Range Check）
某个 case 极热（有 profile 数据）  ⇒ 提到最前面做一次单独比较（PGO）
```

> **注意最后一条**：这是 §C 的偏求值 / JIT 母题在 `switch` 上的微型版本，即**用运行时频率信息把最可能命中的候选提前**。而 PIC 是它的完全动态版本。

### G.4 连线

```
模式匹配编译 ≡ 子集构造         → 前端主锤（第一匹配语义 ≡ 规则优先）
穷尽性/冗余检查 ≡ flex 的规则遮蔽警告
判定树 vs 回溯自动机 ≡ DFA vs NFA 模拟 ≡ 完全表 vs 失败链
列选择 NP 难 ≡ BDD 变量顺序 NP 难
PIC ≡ lazy DFA                  → §C（在线特化）
异常表 / GC 栈图 / DWARF        → 都是“用表换取正常路径零开销”
switch 的 PGO 重排               → 后端大锤⑥
判定树节点共享                   → §E（hash-consing）
```

---

## H. 模拟关系：正确性的万能锤

前面所有的锤子都在回答“怎么做”，这一把回答的是“**做对了吗**”，而它同样是万能的。

### H.1 骨架

要证明一个变换 `C : Src → Tgt` 是正确的，就构造一个**模拟关系**（Simulation Relation）`≈ ⊆ State_Src × State_Tgt`，并证明一个**图表交换**（Commuting Diagram）性质：

```
前向模拟（Forward Simulation）：

   s₁  ──────→  s₂          （源程序走一步）
   ≈            ≈
   t₁  ─ ─ ─→  t₂          （目标程序走 0 步、1 步或多步）

即：  s₁ ≈ t₁  ∧  s₁ → s₂   ⟹   ∃ t₂. t₁ →* t₂ ∧ s₂ ≈ t₂
```

**常见变体与用途**：

| 变体 | 条件 | 用途 |
| ---- | ---- | ---- |
| **同步模拟**（Lockstep Simulation） | 源走一步 ↔ 目标走一步 | 简单的一对一变换 |
| **Plus / Star 模拟** | 源走一步 ↔ 目标走一步以上 / 零步以上 | 内联、指令选择（一条 IR → 多条机器指令） |
| **带度量的 Star 模拟**（Star Simulation with Measure） | 目标走零步时，需要一个严格递减的度量（防止“目标永远不动”） | 死代码消除、常量折叠 |
| **后向模拟**（Backward Simulation） | 方向相反 | 目标可能比源更确定时 |
| **互模拟**（Bisimulation） | 双向 | 证明两个程序完全等价 |
| **细化**（Refinement） | 目标行为 ⊆ 源行为 | 允许目标“更确定”（如把未定义行为 UB 具体化） |

**关键定理**：若目标语言是确定性的（Deterministic）且源程序能安全执行（没有“出错”行为），则**前向模拟 ⟹ 语义保持**（Semantic Preservation），因为前向模拟可以“翻转”为后向模拟。若目标语言本身有不确定性，则需要直接证明后向模拟或附加条件。这是 CompCert 论文中反复讨论的技术点。

### H.2 深层洞察：`L(D) = L(N)` 的证明本身就是一个模拟关系

回到最开始的子集构造正确性证明：

```
定理：L(D) = L(N)
证明的核心引理：
    δ_D*(s₀, w) = ε-closure( δ_N*(q₀, w) )
    即：DFA 读完 w 后所处的“子集状态”，恰好等于 NFA 读完 w 后所有可能所处状态的集合
```

**这就是一个模拟关系**：

```
关系 ≈ ：  S ≈ Q    ⟺    S = Q    （DFA 状态 S 恰好就是 NFA 的可达状态集 Q）

图表：  Q  ──a──→  Q' = ε-clos(move(Q,a))     （NFA 一步）
        ≈                ≈
        S  ──a──→  S' = δ_D(S, a)             （DFA 一步）
        且 S' = Q'  ✔ 同步前向模拟
```

> **因此，在整个编译原理中，“证明正确”这件事从头到尾只用一把锤子。**
> 从子集构造的 `L(D)=L(N)`，到 LR 分析器的正确性（栈内容 ≈ 右句型的可行前缀 Viable Prefix），到 CompCert 的约 20 个 pass，再到 Alive2 的窥孔优化验证，**全都是构造模拟关系**。

### H.3 钉子表

| 应用 | 关系 `≈` 是什么 | 工具 / 项目 |
| ---- | --------------- | ----------- |
| **子集构造正确性** | DFA 状态 = NFA 可达集 | 教科书 |
| **LR 分析器正确性** | 栈内容 ≈ 右句型的可行前缀 | Knuth 1965 |
| **CompCert 的每个 pass** | 每个 pass 各自定义（内存注入 Memory Injection、寄存器映射等） | **CompCert**（Coq，端到端验证的 C 编译器） |
| **CakeML** | 类似 | CakeML（HOL4，验证的 ML 编译器） |
| **翻译验证**（Translation Validation，Necula 2000） | 自动推断（不必预先给出） | 事后验证，无需修改编译器 |
| **Alive / Alive2** | 位精确的 SMT 编码（含 UB、poison、undef） | 验证 LLVM 窥孔优化；发现了数百个真实 bug |
| **超级优化器的等价检查**（Superoptimizer） | SMT | STOKE、Souper |
| **重写规则的正确性** | 项重写的合流性（Confluence）+ 语义保持 | egg 的规则验证、Ruler |
| **数据流分析的可靠性**（Soundness） | **Galois 连接 + `α∘F_c ⊑ F_a∘α`** | 抽象解释的可靠性定理 |
| **类型系统的可靠性**（Type Soundness） | **进展 + 保持**（Progress + Preservation） | 类型系统的标准证明范式 |
| **差分测试 / 模糊测试**（Differential Testing / Fuzzing） | 观测行为一致（实用近似） | **Csmith**、EMI、YARPGen、`llvm-reduce` |
| **递归类型相等判定** | **互模拟**（协归纳） | 等价递归类型系统 |

### H.4 洞察二：抽象解释的可靠性定理是模拟关系的格版本

```
模拟关系：   s ≈ t  ∧  s → s'  ⟹  ∃t'. t →* t' ∧ s' ≈ t'
抽象解释：   α(c) ⊑ a  ∧  c' = F_c(c)  ⟹  α(c') ⊑ F_a(a)
             即：α ∘ F_c  ⊑  F_a ∘ α
```

**两者结构完全相同**：`≈` 变成了 `α(·) ⊑ ·`，“存在一条目标路径”变成了“抽象值更大（更保守）”。这里 `α` 是抽象函数（Abstraction Function），`F_c` 与 `F_a` 分别是具体语义与抽象语义的传递函数。

> **这解释了为什么“局部可靠 ⟹ 全局可靠”在两个场景中都成立**：
>
> - 抽象解释：只要每条指令的传递函数是可靠的，`lfp(F_a)` 自动是可靠的近似；
> - 编译器验证：只要每个 pass 都有模拟关系，而模拟关系可以**组合**（`≈₁ ∘ ≈₂` 仍是模拟关系），整个流水线自动正确。
>
> **模拟关系的可组合性（Compositionality），正是 CompCert 能够规模化的根本原因**，也是 nanopass 架构（§J）在正确性上的理论依据：小 pass 更容易证明，而且证明可以拼接起来。

### H.5 洞察三：`undef` / `poison` / UB 要求“细化关系”而非“等价关系”

LLVM 的 `undef` 和 `poison` 让“等价”变成了单向的：

```
优化可以把不确定的行为变得更确定（细化 Refinement），但不能反过来。

  x + 0  →  x                 ✔ 合法
  x      →  x + 0             ✔ 也合法（对整数恰好双向成立）

  freeze(undef)  →  0         ✔ 合法（细化）
  0  →  freeze(undef)         ✘ 非法（引入了不确定性）
```

**这就是 Alive2 必须使用“细化”而非“等价”作为验证条件的原因**，也是历史上大量 LLVM bug 的来源：把细化关系当作等价关系使用，于是在某个方向上用错了。

> **教学价值**：这说明“正确性”这把锤子中**关系的方向**必须精确，它与 §A 中“合一（无向）vs 包含（有向）”属于同一类问题。**把有向关系误当作无向关系，是编译器 bug 的一大类根源。**

### H.6 连线

```
模拟关系 → 前端主锤的正确性证明（L(D)=L(N)）
        → 抽象解释的可靠性定理（同一结构的格版本）
        → 类型系统的 progress + preservation
        → §J（模拟关系可组合 ⇒ nanopass 可验证）
        → §A（有向关系与无向关系的区分）
差分测试 → 模拟关系的工程近似版（不证明，只测试）
```

---

## I. 需求驱动与查询式架构

### I.1 骨架：把编译器从 push 改成 pull

```
传统架构（push / pass pipeline，推式流水线）：
    parse → typecheck → optimize₁ → … → optimizeₙ → codegen
    每个阶段处理“整个程序”，顺序固定，变更后全量重算

查询式架构（pull / query DAG，拉式查询图）：
    codegen("f") ──需要──> mir("f") ──需要──> typeck("f") ──需要──> hir("f")
                                   └─需要──> type_of("g")  ──需要──> …
    只计算被需要的东西；每个查询都记忆化；输入变化时按依赖关系失效
```

**三个必要组件**：

```
① 查询函数     query(key) → value          必须是纯函数（Pure Function）
② 记忆化表     key → (value, 依赖集合, 版本号)
③ 失效机制     输入变化 ⇒ 沿依赖图把下游标记为 dirty
```

**关键优化：红绿算法（Red-Green Algorithm）/ 提前截断（Early Cutoff）**：

```
被标记为 dirty 的查询重新求值后，若结果与旧值相同 ⇒ 不再向下游传播 dirty
⇒ “改一行注释”不会导致整个 crate 重新做代码生成
```

### I.2 钉子表

| 系统 | 领域 | 备注 |
| ---- | ---- | ---- |
| **rustc queries** | 整个 rustc（HIR 之后的阶段） | Rust 编译器的核心架构 |
| **Salsa** | 通用框架（rust-analyzer 使用） | 由 rustc 的思路抽象出的独立库 |
| **Roslyn** | C#/VB | 增量 + IDE 优先的设计 |
| **Sorbet / Sorbet LSP** | Ruby 类型检查 | —— |
| **Adapton / 自调整计算**（Self-Adjusting Computation） | 理论基础（Acar 等） | 变化传播的复杂度理论 |
| **Tree-sitter** | 增量解析（Incremental Parsing） | 编辑一处，只重新解析受影响的子树 |
| **增量词法分析** | —— | **DFA 状态可以保存在行末** ⇒ 只需重扫受影响的行（前端主锤的直接受益） |
| **按需别名 / 值域查询** | LLVM `LazyValueInfo`、需求驱动的指向分析 | 只回答被问到的查询 |
| **IFDS 摘要边**（Summary Edge） | 过程间分析 | 缓存“过程的输入输出关系” |
| **ANTLR 4 的 DFA 缓存** | 解析 | 同一机制的微型版本 |
| **Braun 惰性 SSA 构造** | SSA | 同上 |
| **RE2 lazy DFA** | 正则匹配 | 同上 |
| **构建系统**（make/ninja/Bazel/Buck） | 项目级 | 同一把锤子用在**文件粒度**上 |
| **Nix / 内容寻址存储**（Content-Addressed Storage） | 包级 | 用内容哈希做 key，相当于在文件上做 §E 的 hash-consing |

> **注意最后三行**：**构建系统就是“粒度粗到文件级的查询式编译器”。** Bazel 的 action graph 对应查询 DAG；内容哈希对应 hash-consing 的 key；远程缓存（Remote Cache）对应共享的记忆化表。这是判据一（跨领域）的极佳例证：同一把锤子从“DFA 状态”一直用到“整个 CI 流水线”。

### I.3 深层洞察

> **洞察一：查询式架构最大的难点是“纯性”与“循环”。**
>
> | 难点 | 表现 | 应对 |
> | ---- | ---- | ---- |
> | **纯性**（Purity） | 查询必须是 `key → value` 的纯函数；任何隐藏的可变状态（全局符号表、可变 IR）都会破坏记忆化 | 强制使用不可变 IR + 驻留器 `interner`（§E）；rustc 使用 `TyCtxt<'tcx>` 的 arena |
> | **循环查询**（Cyclic Queries） | `type_of(a)` 需要 `type_of(b)`，而 `type_of(b)` 又需要 `type_of(a)` | ① 检测并报错（大多数情况）② **在 SCC 内迭代到不动点**（§F）③ 按协归纳处理 |
> | **key 的粒度** | 太粗 ⇒ 失效范围大；太细 ⇒ 表开销大 | 依靠经验调优；rustc 花了多年调整查询边界 |
> | **诊断信息的归属** | 一个查询产生的警告该归给谁？重新运行时会不会重复报告？ | 把诊断作为查询结果的一部分 |
>
> **注意“循环查询在 SCC 内迭代”**：这正是 §F 的 SCC 锤子在架构层面的重现。递归类型或递归函数组的类型推导，在查询式编译器中表现为**循环查询**，其解法与 ML 处理递归绑定组完全相同。

> **洞察二：查询式架构是“何时承诺”母题在架构层面的答案。**
>
> 回顾前文的那条时间轴：
>
> ```
> 编译期静态决定 → 惰性/按需 → 推迟到运行期 → 永不承诺
> ```
>
> **查询式架构就是把“惰性/按需”从单个算法提升为整个编译器的架构原则。** 它的收益和代价与单点惰性一一对应：
>
> |       | 单点惰性（lazy DFA / 惰性 SSA） | 架构级惰性（查询式） |
> | ----- | ------------------------------- | -------------------- |
> | 收益 | 只为用到的部分付费 | 只为用到的部分付费；**在 IDE 场景下收益巨大** |
> | 缓存管理 | `clearDFA()` | LRU 驱逐、磁盘持久化、增量数据库 |
> | 首次访问慢 | 冷启动时做完整模拟 | 冷编译不比传统架构快（甚至更慢） |
> | 前提条件 | 状态可以去重（hash-consing） | 查询纯 + IR 不可变（hash-consing） |
>
> 两者都**以 §E 为前提**。这并非巧合：**记忆化需要可靠的 key，而可靠的 key 需要唯一化。**

> **洞察三：IDE 的需求正在反向重塑编译器设计。**
>
> 传统编译器的优化目标是“批量编译整个程序的吞吐量”。IDE 的目标则是“**改一个字符后，在 100ms 内给出该文件的诊断**”。这是一个完全不同的目标函数，导致了如下变化：
>
> | 传统设计 | IDE 驱动的设计 |
> | -------- | -------------- |
> | 全量 pass 流水线 | 查询 DAG + 增量 |
> | 遇错即停 / panic | **错误恢复（Error Recovery）+ 部分结果**（错误节点、`ErrorType`） |
> | 可变 IR（节省内存） | 不可变 + 持久化数据结构 |
> | AST 丢弃细节（空白、注释） | **无损语法树**（Lossless CST：Roslyn、rust-analyzer、tree-sitter） |
> | 单线程 | 可取消（Cancellation）+ 并行查询 |
>
> **无损语法树值得单独一提**：它要求解析器保留所有 trivia（空白、注释，甚至错误 token），以支持格式化、重构和代码操作（Code Action）。这与“编译用的 AST 只保留语义相关信息”是彼此冲突的目标。现代方案是**两层表示**（CST → AST），这又是一次“换表示”。

### I.4 连线

```
查询式架构 → §E（记忆化必须有可靠的 key ⇒ 需要 hash-consing）
          → §F（循环查询 = SCC，组内迭代）
          → 前文的“何时承诺”母题（架构级惰性）
          → ALL(*) / lazy DFA / 惰性 SSA（同一机制的不同粒度）
          → 构建系统（同一机制的更粗粒度）
```

---

## J. 归约与逐层降级：最“元”的一把锤子

### J.1 骨架

> **不要直接解决问题。把它翻译成一个你已经解决过的问题。**

这是编译器领域**使用频率最高**的技术，也最容易被忽视，因为它显得太理所当然了。

```
高级语言特性  ──降级──>  中级构造  ──降级──>  低级构造  ──降级──>  机器指令
     ↑                                                              ↑
表达力强、便于人书写                                    表达力弱、便于机器执行
信息多                                                            信息少
```

### J.2 钉子表：语言特性的归约谱系

| 高级特性 | 归约到 | 丢失了什么 |
| -------- | ------ | ---------- |
| **`for` / `while` / `foreach`** | 条件跳转 + 标签（CFG） | 循环结构（需要 `llvm.loop` 元数据，或重新识别自然循环） |
| **`switch`** | 判定树 / 跳转表（§G） | case 集合的整体结构 |
| **模式匹配** | 判定树（§G） | 穷尽性信息 |
| **异常** | CPS 双续延 / 表驱动栈展开（§B、§G） | 异常边（需用 `invoke` / `landingpad` 保留） |
| **async/await、生成器** | 状态机（§B） | “这是一个协程”（调试器难以还原逻辑调用栈） |
| **闭包 / lambda** | 结构体 + 函数指针（闭包转换，§B） | 词法作用域关系 |
| **高阶函数** | 去函数化 + `switch`（§B），或保留间接调用 | —— |
| **对象 / 方法** | 记录 + 函数 + vtable（§G） | 类层次（需要保留以便做类层次分析 CHA） |
| **泛型 / 类型类** | **单态化**（§C 偏求值）**或**字典传递（Dictionary Passing） | 单态化：代码膨胀；字典：运行时开销 |
| **trait 对象 / 接口** | vtable / itable（§G） | 具体类型（需要 PIC 或投机优化来恢复） |
| **多重继承** | 多个 vptr + this 指针调整（thunk） | —— |
| **`defer` / RAII / 析构** | 显式清理代码 + 异常路径 | 作用域结构 |
| **`unsafe` / UB** | 语义上的“细化关系”（§H） | 是 bug 的一大来源 |
| **GC** | 写屏障（Write Barrier）+ 安全点 + 栈图（§G） | —— |
| **原子操作 / 内存序**（Memory Ordering） | 屏障指令 + 优化限制 | 优化必须尊重的 fence |
| **`inline asm`** | 优化屏障（黑盒） | 编译器基本放弃对其优化 |
| **向量化 / SIMD 内建函数**（Intrinsics） | 目标指令 | 可移植性 |
| **多面体循环变换** | 带守卫的循环嵌套（CLooG 代码生成） | 仿射结构（之后无法再做多面体变换） |

**以及“归约到已解决的组合问题”（前文的大锤③④⑤）**：

```
寄存器分配 ──归约──> 图着色（Graph Coloring，已有大量启发式）
指令调度   ──归约──> 资源约束调度（已有表调度 List Scheduling）
指令选择   ──归约──> 树覆盖 DP / PBQP / ILP
PRE        ──归约──> 数据流 + 最小割（Min-Cut）
循环变换   ──归约──> 仿射 ILP
等价性     ──归约──> SMT
指向分析   ──归约──> Datalog / CFL-可达性（CFL-Reachability）
```

### J.3 深层洞察

> **洞察一：归约的代价永远是“信息丢失”，而现代编译器的主要演进方向就是“推迟丢失”。**
>
> ```
> 1970s–2000s： 尽早降到一个通用的低层 IR（如 LLVM IR），所有优化都在那里做
>               优点：一个后端服务所有语言
>               缺点：语言特有的高层信息被过早丢弃
>
> 2010s 至今：  保留高层 IR，在高层做语言特有的优化，然后逐层降级
>               Rust:   HIR → THIR → MIR → LLVM IR
>                       （借用检查、Drop 精化必须在 MIR 上做，LLVM IR 上信息已丢失）
>               Swift:  AST → SIL → LLVM IR
>                       （ARC 优化、独占性检查在 SIL 上做）
>               MLIR:   任意多个 dialect，渐进降级（Progressive Lowering）
>                       （linalg → affine → scf → vector → llvm）
>               Java:   保留字节码 + 运行期类型 profile
> ```
>
> **MLIR 是这条洞察的制度化**：它不预设一个“正确的抽象层次”，而是提供**基础设施，让你自由定义任意多层**，并把“在哪一层做什么优化”变成一个显式的设计决策。
>
> 前端也有对应的演进：
>
> ```
> 前端：AST 丢弃 trivia ⇒ 无法格式化/重构
>       ⇒ 现代方案：无损 CST → AST（两层）
> 后端：过早降级 ⇒ 丢失高层信息
>       ⇒ 现代方案：多层 dialect 渐进降级
> ```
>
> **这是同一条演进路线：从“一个正确的表示”走向“多层表示 + 显式的降级点”。**

> **洞察二：nanopass 架构是归约的极致，其可行性依赖于 §H 的可组合性。**
>
> ```
> Nanopass（Sarkar–Waddell–Dybvig 2004）：
>   把编译器分解为几十个“每个只做一件很小的事”的 pass
>   每个 pass 都有自己精确定义的输入/输出语言（用 DSL 声明）
>   ⇒ 每个 pass 都很容易理解、测试、验证
>   ⇒ 但 pass 数量多，而且 phase ordering 问题依然存在
> ```
>
> **为什么这可行？** 因为 §H 的模拟关系**可组合**：`≈₁ ∘ ≈₂` 仍是模拟关系。所以“每个小 pass 正确 ⟹ 整体正确”自动成立。CompCert 采用的正是这种架构（约 20 个 pass，每个单独证明）。
>
> **代价**：pass 之间的接口开销、编译时间，以及**归约顺序的选择**（这是 phase ordering 问题的另一副面孔）。

> **洞察三：归约有方向性，什么算“已解决的问题”取决于时代。**
>
> ```
> 1960s： “已解决” = 能用汇编手写          ⇒ 归约到汇编模板
> 1980s： “已解决” = 图着色、动态规划       ⇒ 归约到组合优化
> 2000s： “已解决” = ILP、SAT/SMT          ⇒ 归约到求解器
> 2010s： “已解决” = 大规模搜索、Datalog    ⇒ 归约到搜索 / 声明式规则
> 2020s： “已解决” = 神经网络能拟合的问题   ⇒ 归约到学习型代价模型（MLGO、Ithemal）
> ```
>
> **每一代编译器的“归约目标”，就是那一代最强的通用求解技术。** 这是判据三（预测力）的直接应用：**下一代编译器会把更多问题归约到 LLM / 学习系统上**。这已经在发生：学习型内联策略、学习型调度、LLM 辅助的优化规则发现。

### J.4 连线

```
归约 → 所有其他锤子的“元锤子”（决定用哪把锤子 = 决定归约到什么）
     → §H（模拟关系可组合 ⇒ nanopass 可验证）
     → 前文的 phase ordering（归约顺序的选择）
     → §C（单态化 = 归约到偏求值）
     → §B（异常/协程 = 归约到状态机）
     → §G（模式匹配/switch = 归约到判定树）
     → MLIR = 把“归约的层数”变成用户可配置的东西
```

---

## K. 小锤集

以下四把没有完全达到“万能锤”标准（各差一条判据），但足够重要，并且与前面的锤子有很强的连线。

### K.1 位并行：NFA 模拟的第三条路

前文说过，面对 NFA 有两条路：**确定化**（DFA，速度快但可能爆炸）或**直接模拟**（`O(nm)`）。其实还有**第三条**：

> **把整个 NFA 状态集合装进一个机器字，用位运算一次并行推进 `w` 个状态。** 这就是位并行（Bit-Parallelism）。

```c
// Shift-Or 算法：在 O(n·⌈m/w⌉) 时间内做精确字符串匹配
// D 的第 j 位 = 0 表示“模式的前 j+1 个字符恰好匹配到当前位置”
//               （即 NFA 状态 j 是活跃的）
uint64_t D = ~0ULL;                       // 初始：所有状态都不活跃
for (int i = 0; i < n; i++) {
    D = (D << 1) | B[text[i]];            // ★ 一条指令推进全部 64 个 NFA 状态
    if (!(D & (1ULL << (m-1)))) report(i - m + 1);
}
```

其中 `B[c]` 是预计算的字符掩码：模式第 `j` 位是字符 `c` 时，`B[c]` 的第 `j` 位为 0。

| 算法 | 用途 |
| ---- | ---- |
| **Shift-Or / Shift-And**（Baeza-Yates–Gonnet） | 精确匹配 |
| **BNDM / BOM** | 带跳跃的匹配 |
| **位并行编辑距离**（Myers 1999） | 近似匹配、`diff` |
| **Glushkov 位并行正则匹配** | 小正则式的极速匹配 |
| **Hyperscan** | Intel 的多正则引擎：大量 SIMD + 位并行 + 分解为小自动机 |
| **simdjson / SIMD 结构索引** | 用 SIMD 一次处理 64 字节，对引号、括号、空白做结构化索引 |
| **数据流分析的位向量** | 一个机器字并行处理 64 个变量的 meet |
| **用 BDD 表示指向集** | 指向集的紧凑表示（bddbddb） |

> **洞察**：这给出了处理 NFA 的完整图景：
>
> ```
> ① 确定化 → DFA          ：时间 O(n)，空间可能达 2^m           【前端主锤】
> ② 直接模拟状态集合       ：时间 O(nm)，空间 O(m)             【GLR / iburg 的选择】
> ③ 位并行模拟状态集合     ：时间 O(n⌈m/w⌉)，空间 O(m)        【Shift-Or】
> ④ 惰性确定化             ：摊销时间 O(n)，空间有界           【lazy DFA / ALL(*)】
> ```
>
> **①②③④ 是同一个权衡空间的四个角落。** ③ 的存在说明：**“状态集合”这个抽象如果编码得足够紧凑，“不做确定化”的代价可以小到可以忽略。**

### K.2 区域与所有权：把内存管理变成类型 / 数据流问题

| 技术 | 归约到 |
| ---- | ------ |
| **区域推断**（Tofte–Talpin、MLKit） | 包含约束求解（§A） |
| **逃逸分析**（Escape Analysis） | 数据流分析（后端主锤） |
| **Rust 的借用检查（NLL）** | **CFG 上的数据流 + 约束图可达性**（§A + 后端主锤） |
| **Rust Polonius** | **Datalog**（§A + 后端主锤 + §J） |
| **线性 / 仿射类型**（Linear / Affine Types） | 类型系统（§A） |
| **ARC 优化**（Swift） | 数据流分析 + 引用计数配对消除（retain/release pairing） |
| **Cyclone 的区域** | 区域多态 + 约束 |

> **洞察**：**“内存安全”这个看起来完全不同的问题，被归约成了本文已有的锤子**：约束求解 + 数据流分析 + Datalog。
>
> NLL（Non-Lexical Lifetimes，非词法生命周期）的历史尤其有教学价值：
>
> ```
> 旧借用检查：生命周期 = 词法作用域       ⇒ 折叠（§D，在 AST 上一遍）  ⇒ 过于保守
> NLL：      生命周期 = CFG 上的活跃范围  ⇒ 不动点（后端主锤）        ⇒ 精确得多
> ```
>
> **这是“从树上折叠升级到图上不动点”（§D.3）在真实语言演进中的一次体现。**

### K.3 类型即抽象解释

Cousot（1997）证明：**类型系统是抽象解释（Abstract Interpretation）的一个实例。**

```
具体域（Concrete Domain）：程序执行轨迹的集合
抽象域（Abstract Domain）：类型（一个类型表示一组值，即 γ(τ)，γ 为具体化函数 Concretization）
类型规则                 = 抽象传递函数
类型可靠性（Soundness）   = 抽象解释的可靠性定理
```

**由此得到的统一图景**：

|          | 类型检查 | 抽象解释 |
| -------- | -------- | -------- |
| 抽象域 | 类型 | 区间 / 多面体 / 指向集等 |
| 可靠性 | progress + preservation | `α∘F_c ⊑ F_a∘α` |
| 精度不足时 | 需要类型标注、类型断言 | 需要加宽提示、断言 |
| 提升精度的手段 | 依赖类型、精化类型、多态、流敏感类型（Flow-Sensitive Typing） | 关系域、路径敏感、上下文敏感 |
| 保证终止的手段 | 类型语法有限、秩限制（Rank Restriction） | 加宽、`k`-limiting |
| **两者合流** | **精化类型（Liquid Types）= 类型 + 抽象解释求解器** | |

> **洞察**：这解释了一个常见困惑：“类型系统和静态分析有什么区别？”
> **答案：没有本质区别，只是工程侧重不同。**
>
> ```
> 类型系统：  抽象域由语言语法固定，需要程序员标注，可组合（模块化），错误信息好
> 静态分析：  抽象域由分析器选择，全自动，通常不模块化，错误信息差（“可能有问题”）
> ```
>
> 现代趋势是两者融合：**精化类型**（Liquid Haskell、Flux）、**渐进类型**（Gradual Typing）、**Rust 的借用检查器**（一个内置于类型系统中的数据流分析）、**效应系统**（Effect Systems）。

### K.4 归纳与协归纳的对偶

| 归纳（Induction） | 协归纳（Coinduction） |
| ----------------- | --------------------- |
| 最小不动点 `lfp` | 最大不动点 `gfp` |
| 有限数据（列表、树、AST） | 无限数据（流、递归类型、无限执行） |
| 折叠（cata）、递归 | 展开（ana）、余递归（Corecursion） |
| 悲观合并的 Union-Find（§A、后端大锤②） | **乐观的划分精化**（Partition Refinement：Hopcroft、AWZ GVN） |
| 子集构造（可达子集组成的最小集合） | **DFA 最小化**（最粗的一致划分） |
| 终止性证明（递减度量） | **安全性 / 不变式证明**（互模拟） |
| 类型推导的通常情形 | **递归类型的相等判定** |
| Datalog 的最小模型 | Büchi 自动机的接受条件（ω-正则语言） |

> **洞察**：前文提到“最小不动点与最大不动点是对偶的两个方向”，其完整名称就是**归纳与协归纳的对偶**。
>
> **一个实用的判别法**：
>
> - 要证明“某件坏事**不会**发生”（安全性 Safety）⇒ 找不变式 ⇒ **最大不动点 / 协归纳**；
> - 要证明“某件好事**会**发生”（活性 Liveness / 终止）⇒ 找递减度量 ⇒ **最小不动点 / 归纳**。
>
> 这也解释了前文 §6.3 中 Büchi 自动机为什么不能用子集构造确定化：**它的接受条件是 ω-条件（协归纳的），而子集构造只保留了可达性（归纳的）信息。**

---

## 11. 全局归并：十八把锤子只有五种机制

现在把本系列的所有锤子放在一起：前端 1 把、后端 7 把（主锤 + 大锤①～⑥）、本文 10 把，再加 4 把小锤。**归并之后只剩五种机制。**

### 机制 I：归纳结构上的计算（折叠 ⟷ 不动点）

```
结构无环 ⇒ 一遍折叠                 结构有环 ⇒ 迭代到不动点
─────────────────────               ────────────────────────
S/L-属性文法（§D）                   数据流分析（后端主锤）
Sethi–Ullman、BURS 标号              子集构造 / LR 项目集（前端主锤）
类型检查（非递归）                    FIRST/FOLLOW、ε-closure
nullable/firstpos/followpos           支配关系、支配边界
                                     指向分析、Datalog
                                     同余闭包、e-graph rebuild
                                     重写到不动点
        ↑                                    ↑
        └────── SCC 分解（§F）把环隔离出来 ──────┘
                环外做折叠，环内做迭代
```

**统一签名**（工作表算法 Worklist Algorithm）：

```python
while worklist:
    x = worklist.pop()
    new = transfer(join(inputs(x)))
    if new != current[x]:
        current[x] = new
        worklist.extend(dependents(x))
```

**两个方向**（归纳 vs 协归纳，§K.4）：`lfp` 从 `⊥` 向上合并（Union-Find）；`gfp` 从 `⊤` 向下精化（划分精化 Partition Refinement）。

### 机制 II：等价性管理

```
                    ┌── 判定“是否等价” ──┐
                    │                    │
        合一（§A）              划分精化（Hopcroft / AWZ）
        Union-Find              同余闭包（§A、§E）
        包含约束                E-graph（后端大锤②）
        （Steensgaard/Andersen）
                    │                    │
                    └── 表示“唯一代表” ──┘
                              │
                    hash-consing（§E）
                    规范化 / 取代表元（Canonicalization）
                    GVN / CSE / ICF
                              │
                    ┌── 证明“确实等价” ──┐
                    │                    │
              模拟关系（§H）        SMT / Alive2
              抽象解释的可靠性        差分测试
```

### 机制 III：表示变换（换一个表示，消灭一类分析）

| 变换 | 消灭了什么 | 代价 |
| ---- | ---------- | ---- |
| NFA → **DFA** | 运行时的不确定性 | `2ⁿ` 爆炸风险 |
| 项目 NFA → **LR 自动机** | “CFL 需要无限栈”的困难 | 需要显式栈 + 冲突消解 |
| → **SSA** | 到达定值分析（Reaching Definitions） | 退出 SSA / 寄存器合并（Coalescing） |
| → **CPS / 状态机**（§B） | 隐式控制流 | 状态爆炸、调试困难 |
| → **去函数化**（§B） | 高阶间接调用 | 需要全程序信息、switch 巨大 |
| → **判定树**（§G） | 多路选择中的重复测试 | 代码体积爆炸 |
| → **多面体** | 十几种 ad-hoc 循环变换 | 只适用于仿射程序 |
| → **E-graph** | 重写层面的 phase ordering | 可能无法饱和（Saturation） |
| → **弦图**（SSA 干扰图，Chordal Graph） | 图着色的 NP 难 | 难度转移到 coalescing |
| → **无损 CST + AST**（§I） | “格式化 vs 编译”的冲突 | 两层的维护成本 |
| → **多层 dialect**（MLIR，§J） | 过早的信息丢失 | 层数管理复杂 |

**两条最漂亮的结构定理**：

```
活前缀（Viable Prefix）的集合是正则语言   ⇒ LR 分析可行（CFL 的难度被隔离进显式栈）
严格 SSA 的干扰图是弦图                   ⇒ 最优着色可在多项式时间完成（难度被隔离进 coalescing）
```

### 机制 IV：特化与摊销

```
                偏求值 / 特化（§C）
                        │
    ┌───────────────────┼───────────────────┐
    │                   │                   │
静态特化            惰性 + 记忆化          运行期特化
常量折叠/内联        hash-consing（§E）     JIT（后端大锤⑥）
单态化/模板          lazy DFA / ALL(*)      PIC（§G）
宏/comptime          惰性 SSA               Trace JIT
Futamura 第二投影    查询式架构（§I）       Truffle = 第一投影
（生成器：flex/      构建系统               PGO
 bison/BURG）
    │                   │                   │
    └── 共同难题：终止性 / 缓存管理 / 猜错时的退路 ──┘
        泛化 vs 加宽（有界化母题）
        必须配备“可检测的失败信号”
```

### 机制 V：归约与分层

```
归约（§J）：把问题翻译成已解决的问题
    ↓
本文与前文中所有“归约到 X”：
    图着色、资源约束调度、树覆盖 DP、最小割、ILP、PBQP、
    SMT、Datalog、CFL-可达性、判定树、状态机、学习型模型
    ↓
分层（nanopass / MLIR / 渐进降级）：
    每层只做一件事 ⇒ 易理解、易验证（由 §H 的可组合性保证正确性）
    代价：层数管理 + phase ordering
```

### 一张收束图

```
                          ┌──────────────────────┐
                          │       五种机制        │
                          └──────────┬───────────┘
        ┌──────────┬──────────┬──────┴─────┬──────────┐
        │          │          │            │          │
   I.归纳/不动点  II.等价性  III.表示变换  IV.特化摊销  V.归约分层
        │          │          │            │          │
   前端主锤       大锤②      大锤①⑤       大锤⑥      大锤③④
   后端主锤       §A §E §H    §B §G        §C §E §I    §J
   §D §F         §K.4        §K.2 §K.3     §K.1
        │          │          │            │          │
        └──────────┴──────────┴────────────┴──────────┘
                              │
              ┌───────────────┴────────────────┐
              │      贯穿全部的三条元原则         │
              │  ① 迭代到不动点                   │
              │  ② 换一个使问题变简单的表示        │
              │  ③ 决定何时承诺，并为承诺错误      │
              │     准备一条可检测的退路           │
              └────────────────────────────────┘
```

---

## 12. 锤子的反面：什么时候该放下它

万能锤的危险在于“手里拿着锤子，看什么都像钉子”。每把锤子都有明确的失效域，下面如实列出。

| 锤子 | 什么时候是错误的工具 | 症状 | 该换成什么 |
| ---- | -------------------- | ---- | ---------- |
| **不动点 / 抽象解释** | 用来回答**收益性**问题（“这个优化能让程序更快吗”） | 分析结果全是 `⊤`；或者分析很精确但不知道拿它做什么 | 代价模型 + 搜索 + PGO（大锤⑥） |
| **不动点** | 整个依赖图是一个巨大的 SCC | 迭代次数 ≈ 图直径，慢到不可用 | 换表示以打破环（SSA、SCC 折叠）；或改用需求驱动，只算被问到的部分 |
| **合一（§A）** | 需要子类型或方向性时 | 强行把 `p <: q` 当作 `p = q`，精度崩塌（Steensgaard 的困境） | 包含约束 / 双向定型 |
| **子集构造 / 确定化** | 只用一次、状态空间维度很高，或者理论上无法确定化 | 表爆炸；或构造成本无法摊销回来 | NFA 模拟、位并行（§K.1）、惰性确定化、GLR |
| **偏求值（§C）** | 缺乏终止控制 | 编译时间 / 代码体积爆炸（模板元编程的经典病） | 泛化、展开预算、显式分阶段 |
| **状态机化（§B）** | 状态数随程序结构指数增长；或需要良好的可调试性 | Future 体积巨大；调用栈无法还原 | 保留一等续延、分段栈（Segmented Stack）、绿色线程（Green Threads） |
| **hash-consing（§E）** | 对象需要频繁修改、生命周期短，或需要并行 | 全局表争用、缓存不友好 | Arena + 可变 IR + 局部 CSE |
| **判定树（§G）** | 候选极多且分布均匀 | 代码体积爆炸 | 表驱动 / 回溯自动机 / 哈希 / 运行期 PIC |
| **E-graph** | 规则集包含交换律、结合律且没有预算控制 | 无法饱和、内存爆炸、提取需要 ILP | 有界重写（如 Cranelift 的 aegraph）、精选规则集 |
| **多面体模型** | 非仿射程序（间接寻址、依赖数据的控制流） | 模型直接不适用 | 传统循环优化 + 运行时检查 |
| **查询式架构（§I）** | 只做批量 AOT 编译，没有 IDE 需求 | 冷编译更慢，架构复杂度得不偿失 | 传统 pass 流水线 |
| **形式验证（§H）** | 语言语义本身尚未稳定或尚未形式化 | 证明的工作量远超编译器本身 | 差分 / 模糊测试（Csmith）+ 翻译验证 |
| **归约（§J）** | 归约丢失了解决问题所必需的信息 | 在低层 IR 上“把高层结构再猜回来”（如从 CFG 重新识别循环、从指令序列识别 memcpy） | 保留高层 IR，在合适的层次处理（MLIR / MIR / SIL） |
| **搜索 / 机器学习（大锤⑥）** | 需要可解释性、可复现性，或编译时间受限 | 结果不可复现、无法调试、CI 时间爆炸 | 解析式代价模型 + 人工启发式 |

> **一条通用诊断法**：
> **如果你发现自己在“用一个分析把之前某个变换丢掉的信息猜回来”，说明归约做得太早了。**
>
> 经典实例：
>
> - 从 CFG 重新识别自然循环（因为 `for` 结构被过早降级）→ 解法：`llvm.loop` 元数据、在 MIR 中保留循环；
> - 从指令序列识别 `memcpy` 模式（因为循环被过早展开）→ 解法：惯用法识别（Idiom Recognition），或者不要过早展开；
> - 从 LLVM IR 反推借用关系（不可能做到）→ 解法：在 MIR 上做借用检查；
> - 从 AST 反推原始格式（不可能做到）→ 解法：无损 CST。
>
> **这是“何时承诺”母题的第三种表现形式**：不仅是“何时做决定”，还包括“**何时丢弃信息**”。

---

## 13. 自检、学习路径与文献

### 13.1 自检问题

**跨锤连线（最重要）**

1. 为什么说 `async/await` 降级是“手写的 NFA→DFA”？它还需要另外哪一把锤子提供什么信息？状态结构体变大对应后端的哪个经典问题？
2. Maranget 的模式匹配编译与子集构造可以逐项对应。请给出：`S(c,P)` ↔ ?、`D(P)` ↔ ?、第一匹配语义 ↔ ?、判定树 vs 回溯自动机 ↔ ?
3. 子集构造代码中的 `if T not in index` 是哪一把锤子？去掉它会发生什么？请再举出三个“以状态集合为状态”的算法，指出同一行代码在哪里。
4. `L(D) = L(N)` 的教科书证明与 CompCert 的 pass 证明是同一种论证。是哪一种？它与抽象解释的可靠性定理 `α∘F_c ⊑ F_a∘α` 在结构上如何对应？
5. Steensgaard vs Andersen、SLR vs LR(1)、MFP vs MOP、SLL vs LL、合一 vs 包含约束：用一句话概括这五组的共同点。
6. 为什么“树上的折叠”与“图上的不动点”是同一把锤子？举出两个从前者升级到后者的真实语言或编译器演进案例。
7. `正则匹配 = interp(regex, text)`。对 `regex` 做偏求值会得到什么？这说明前端主锤与哪一把锤子是什么关系？flex 是第几投影的产物？
8. Andersen 分析的“环折叠”与 Menhir 的 Pager 弱兼容合并是同一种策略。是什么策略？为什么它“不损失精度”？

**单锤深度**

9. 合一算法中的 `uf.union(a,b)` 为什么必须放在递归**之前**？请指出另外两个用同样技巧处理环的算法。
10. 偏求值中的“泛化”、区间分析中的加宽、LL(\*) 中的 DFA 自环是同一个动作。是什么动作？为什么它是**必需的**，而不是可选的优化？
11. HM 只使用综合属性，双向定型引入了继承属性。为什么这两条路线在能力上限和错误信息质量上呈现相反的趋势？
12. 为什么“循环 = SCC”比“循环 = 支配关系定义的回边”更通用？请给出一个后者失效的例子。
13. ML 的 `let rec … and …` 语法为什么存在？它把哪一把锤子的工作推给了程序员？
14. LLVM 为什么对 `Type` 和 `Constant` 做 hash-consing，而对 `Instruction` 不做？请给出判断标准。
15. Alive2 为什么必须用“细化”而非“等价”作为验证条件？这与 §A 的“合一 vs 包含”是同一类问题吗？
16. 查询式架构的两大难点是纯性和循环查询。循环查询的解法用到了哪一把锤子？

**元层面**

17. “当你在用分析把之前变换丢掉的信息猜回来时，说明归约做早了。”请举出三个真实实例及其现代解法。
18. 用 §11 的五种机制给下列技术分类：`PIC`、`GVN`、`去函数化`、`Polonius`、`Hopcroft 最小化`、`MLIR 渐进降级`、`Shift-Or`、`tree-sitter 增量解析`。
19. “好的近似必须配备一个可检测的失败信号。”本文十把锤子中，哪几把有这样的信号？哪几把没有？没有的该如何补救？
20. 用 §J.3 的洞察三来预测：下一代编译器最可能把哪三类问题归约到 LLM / 学习系统上？各自需要什么样的“可检测失败信号”？

### 13.2 学习路径

```
第一阶段：打通“折叠 ⟷ 不动点”（机制 I）
① 属性文法：S-属性 / L-属性，以及它们与 LR / LL 的匹配关系
② 亲手实现：nullable/firstpos/followpos（纯折叠）→ FIRST/FOLLOW（需要迭代）
   关键：亲身体会“环从哪里来”
③ 实现 Tarjan SCC + RPO 序，用它加速你已有的数据流分析
   关键：测量迭代次数的变化

第二阶段：等价性（机制 II）
④ 合一（Robinson + Union-Find + occurs check）→ 实现一个 HM 类型推导器
⑤ 同余闭包（Downey–Sethi–Tarjan）→ 与 GVN、e-graph 对照
⑥ 分别实现 Steensgaard 与 Andersen，比较精度与速度
   关键：确认“合一 = 把有向关系塌缩成无向关系”
⑦ hash-consing：给你的 AST / 类型加上唯一化，测量相等判定的加速效果

第三阶段：表示变换（机制 III）
⑧ CPS 转换 + 闭包转换 + 去函数化，各写一遍
⑨ 手写一次 async/await 降级（选一个小语言），亲手做活跃变量分析来决定状态字段
   关键：这一步会同时用上机制 I、机制 III 和前端主锤
⑩ Maranget 模式匹配编译（含穷尽性 / 冗余检查）
   关键：与你之前写的子集构造代码逐行对照
⑪ SSA 构造 + 退出 SSA（如果还没做过）

第四阶段：特化与摊销（机制 IV）
⑫ 阅读 Futamura 1971，以及 Jones–Gomard–Sestoft 偏求值专著的前三章
⑬ 写一个玩具偏求值器（含 BTA），观察泛化如何保证终止
⑭ 用 Salsa 搭建一个最小的增量编译器（3～4 个查询即可）
   关键：亲自遇到一次“循环查询”，然后用 SCC 解决它

第五阶段：正确性与归约（机制 II 的证明侧 + 机制 V）
⑮ 手写 L(D)=L(N) 的模拟关系证明，再读 CompCert 中一个 pass 的证明，对照两者结构
⑯ 用 Alive2 验证几条 InstCombine 规则，故意写一条错误的规则，看它如何报告
⑰ 阅读 nanopass 论文，并浏览 MLIR 的 dialect 列表
   关键：理解“层数是一个设计决策”

第六阶段：反面
⑱ 为每把锤子找出一个它失效的真实案例（§12 的表格是起点）
   关键：能说出“什么时候不该用”，才算真正掌握
```

### 13.3 文献

#### 合一与约束（§A）

1. **Robinson, J. A.** *A Machine-Oriented Logic Based on the Resolution Principle.* JACM 12(1), 1965.
2. **Damas & Milner.** *Principal Type-Schemes for Functional Programs.* POPL 1982.
3. **Pottier & Rémy.** *The Essence of ML Type Inference.* In *Advanced Topics in Types and Programming Languages*, 2005.
4. **Vytiniotis, Peyton Jones, Schrijvers, Sulzmann.** *OutsideIn(X): Modular Type Inference with Local Assumptions.* JFP 21, 2011.
5. **Dunfield & Krishnaswami.** *Bidirectional Typing.* ACM CSUR 54(5), 2021.（双向定型的权威综述）
6. **Steensgaard, B.** *Points-to Analysis in Almost Linear Time.* POPL 1996.
7. **Andersen, L. O.** *Program Analysis and Specialization for the C Programming Language.* PhD Thesis, DIKU, 1994.
8. **Hardekopf & Lin.** *The Ant and the Grasshopper: Fast and Accurate Pointer Analysis for Millions of Lines of Code.* PLDI 2007.（在线环折叠）
9. **Pearce, Kelly, Hankin.** *Online Cycle Detection and Difference Propagation for Pointer Analysis.* SCAM 2003.

#### 控制流即数据（§B）

10. **Reynolds, J.** *Definitional Interpreters for Higher-Order Programming Languages.* 1972.（**去函数化**的出处）
11. **Appel, A.** *Compiling with Continuations.* Cambridge, 1992.
12. **Appel, A.** *SSA is Functional Programming.* SIGPLAN Notices 33(4), 1998.
13. **Kelsey, R.** *A Correspondence between Continuation Passing Style and Static Single Assignment Form.* IR Workshop 1995.
14. **Danvy & Nielsen.** *Defunctionalization at Work.* PPDP 2001.
15. **Flanagan et al.** *The Essence of Compiling with Continuations.* PLDI 1993.（ANF）
16. **Leijen, D.** *Structured Asynchrony with Algebraic Effects.* TyDe 2017.
17. **Prokopec et al.** *Making Coroutines Cheap*；以及 Kotlin 编译器文档中关于挂起函数的 CPS + 状态机降级说明。

#### 偏求值与分阶段（§C）

18. **Futamura, Y.** *Partial Evaluation of Computation Process — An Approach to a Compiler-Compiler.* 1971.
19. **Jones, Gomard, Sestoft.** *Partial Evaluation and Automatic Program Generation.* Prentice Hall, 1993.（**可免费在线获取；偏求值领域的经典著作**）
20. **Taha & Sheard.** *MetaML and Multi-stage Programming with Explicit Annotations.* TCS 2000.
21. **Rompf & Odersky.** *Lightweight Modular Staging.* GPCE 2010.（LMS）
22. **Würthinger et al.** *One VM to Rule Them All.* Onward! 2013.（**Truffle：第一投影的工业实现**）
23. **Kell, S.** *In Search of Types.* Onward! 2014.（对“编译器 = 偏求值”这一视角的批判性讨论）

#### 属性文法与折叠（§D）

24. **Knuth, D.** *Semantics of Context-Free Languages.* Math. Systems Theory 2(2), 1968.（属性文法原始论文）
25. **Jourdan, M.** *An Optimal-Time Recursive Evaluator for Attribute Grammars.* 1984.
26. **Magnusson & Hedin.** *Circular Reference Attributed Grammars — Their Evaluation and Applications.* SCP 68(1), 2007.（**循环属性 = 不动点**）
27. **Meijer, Fokkinga, Paterson.** *Functional Programming with Bananas, Lenses, Envelopes and Barbed Wire.* FPCA 1991.（recursion schemes）
28. **Van Wyk et al.** *Silver: An Extensible Attribute Grammar System.* SCP 75(1), 2010.

#### Hash-consing 与记忆化（§E）

29. **Ershov, A. P.** *On Programming of Arithmetic Operations.* CACM 1(8), 1958.（最早的公共子表达式识别，hash-consing 的雏形）
30. **Goto, E.** *Monocopy and Associative Algorithms in an Extended Lisp.* 1974.（hash-consing 的命名来源）
31. **Filliâtre & Conchon.** *Type-Safe Modular Hash-Consing.* ML Workshop 2006.
32. **Bryant, R.** *Graph-Based Algorithms for Boolean Function Manipulation.* IEEE TC 35(8), 1986.（BDD）
33. **Downey, Sethi, Tarjan.** *Variations on the Common Subexpression Problem.* JACM 27(4), 1980.

#### SCC 与迭代顺序（§F）

34. **Tarjan, R.** *Depth-First Search and Linear Graph Algorithms.* SIAM J. Comput. 1(2), 1972.
35. **Bourdoncle, F.** *Efficient Chaotic Iteration Strategies with Widenings.* FMPA 1993.（**WTO：由 SCC 引导的迭代策略**，实践中极为重要）
36. **Havlak, P.** *Nesting of Reducible and Irreducible Loops.* TOPLAS 19(4), 1997.
37. **Ramalingam, G.** *On Loops, Dominators, and Dominance Frontiers.* TOPLAS 24(5), 2002.
38. **Horwitz, Demers, Teitelbaum.** *An Efficient General Iterative Algorithm for Dataflow Analysis.* Acta Informatica 24, 1987.

#### 判定树与分派（§G）

39. **Maranget, L.** *Compiling Pattern Matching to Good Decision Trees.* ML Workshop 2008.（**必读；可与子集构造对照阅读**）
40. **Maranget, L.** *Warnings for Pattern Matching.* JFP 17(3), 2007.（穷尽性 / 冗余检查）
41. **Le Fessant & Maranget.** *Optimizing Pattern Matching.* ICFP 2001.（**回溯自动机 vs 判定树**）
42. **Augustsson, L.** *Compiling Pattern Matching.* FPCA 1985.
43. **Cohen, N.** *Type-Extension Type Tests Can Be Performed in Constant Time.* TOPLAS 13(4), 1991.（类层次编码）
44. **Alpern, Cocchi, Grove et al.** *Efficient Implementation of Java Interfaces: Invokeinterface Considered Harmless.* OOPSLA 2001.
45. **Kennedy & Syme.** *Design and Implementation of Generics for the .NET Common Language Runtime.* PLDI 2001.（泛型实现中单态化与共享代码的工业权衡）

#### 模拟关系与验证（§H）

46. **Leroy, X.** *Formal Verification of a Realistic Compiler.* CACM 52(7), 2009.（CompCert 概览）
47. **Leroy, X.** *A Formally Verified Compiler Back-end.* JAR 43, 2009.（**模拟关系的完整技术处理**）
48. **Necula, G.** *Translation Validation for an Optimizing Compiler.* PLDI 2000.
49. **Lopes et al.** *Alive2: Bounded Translation Validation for LLVM.* PLDI 2021.
50. **Lee et al.** *Taming Undefined Behavior in LLVM.* PLDI 2017.（**为什么必须用细化而非等价**）
51. **Yang et al.** *Finding and Understanding Bugs in C Compilers.* PLDI 2011.（Csmith）
52. **Le, Afshari, Su.** *Compiler Validation via Equivalence Modulo Inputs.* PLDI 2014.（EMI）
53. **Kumar et al.** *CakeML: A Verified Implementation of ML.* POPL 2014.
54. **Cousot, P.** *Types as Abstract Interpretations.* POPL 1997.（**§K.3 的原始论文**）
55. **Sangiorgi, D.** *Introduction to Bisimulation and Coinduction.* Cambridge, 2011.

#### 查询式与增量（§I）

56. **Acar, Blelloch, Harper.** *Adaptive Functional Programming.* POPL 2002.（自调整计算）
57. **Hammer et al.** *Adapton: Composable, Demand-Driven Incremental Computation.* PLDI 2014.
58. **Matsakis, N.** *Responsive Compilers*；以及 rustc dev guide 中的 *Queries: demand-driven compilation*（rustc 查询架构，含红绿算法）。
59. **Brunsfeld, M.** *Tree-sitter: An Incremental Parsing System.* 2018.（含增量词法状态的处理）
60. **Erdweg, Bracevac, Kuci et al.** *A Co-contextual Formulation of Type Rules and Its Application to Incremental Type Checking.* OOPSLA 2015.
61. **Szabó, Erdweg, Voelter.** *IncA: A DSL for the Definition of Incremental Program Analyses.* ASE 2016.

#### 归约与分层（§J）

62. **Sarkar, Waddell, Dybvig.** *A Nanopass Infrastructure for Compiler Education.* ICFP 2004.
63. **Keep & Dybvig.** *A Nanopass Framework for Commercial Compiler Development.* ICFP 2013.
64. **Lattner et al.** *MLIR: Scaling Compiler Infrastructure for Domain Specific Computation.* CGO 2021.
65. **Matsakis, N.** *Introducing MIR.* Rust Blog, 2016.（为什么借用检查必须在 MIR 而非 LLVM IR 上做）
66. **Groff & Lattner.** *Swift's High-Level IR: A Case Study of Complementing LLVM IR with Language-Specific Optimization (SIL).* LLVM Developers' Meeting 2015.

#### 位并行（§K.1）

67. **Baeza-Yates & Gonnet.** *A New Approach to Text Searching.* CACM 35(10), 1992.（Shift-Or）
68. **Myers, G.** *A Fast Bit-Vector Algorithm for Approximate String Matching Based on Dynamic Programming.* JACM 46(3), 1999.
69. **Navarro & Raffinot.** *Flexible Pattern Matching in Strings.* Cambridge, 2002.（位并行自动机的系统处理）
70. **Wang et al.** *Hyperscan: A Fast Multi-pattern Regex Matcher for Modern CPUs.* NSDI 2019.
71. **Langdale & Lemire.** *Parsing Gigabytes of JSON per Second.* VLDB J. 28, 2019.（simdjson）

#### 区域与所有权（§K.2）

72. **Tofte & Talpin.** *Region-Based Memory Management.* Information and Computation 132(2), 1997.
73. **Grossman et al.** *Region-Based Memory Management in Cyclone.* PLDI 2002.
74. **Matsakis, N.** *Non-Lexical Lifetimes (NLL)*, RFC 2094；以及 *Polonius* 设计笔记。（**从折叠升级到不动点 / Datalog 的真实案例**）

---

## 收束

**纵观本系列，编译原理中被反复使用的东西其实只有以下五类：**

**① 在归纳结构上做计算。** 结构无环就折叠一遍；结构有环就迭代到不动点；用 SCC 把环隔离出来，让大部分计算退化为折叠。子集构造、LR 项目集、数据流分析、`FIRST`/`FOLLOW`、支配关系、类型推导、e-graph rebuild，做的都是这一件事，区别只在于格和图不同。

**② 管理等价性。** 判定等价（合一、划分精化、同余闭包）、表示等价（hash-consing、规范化、E-graph）、证明等价（模拟关系、SMT、差分测试）。前两者决定编译器算得快不快，后者决定它算得对不对。

**③ 换表示。** DFA、LR 自动机、SSA、CPS、状态机、判定树、多面体、弦图、E-graph、多层 dialect，每一次都是“用一次不可逆的信息重组，换掉一整类分析”。最漂亮的两条结构定理（活前缀构成正则语言、SSA 干扰图是弦图）都属于这一类。

**④ 特化并摊销。** 偏求值是它的完整理论（编译本身就是对解释器的偏求值）。常量折叠、内联、单态化、宏、JIT、PIC、lazy DFA、查询式架构、构建系统缓存，都是它在不同粒度上的实例。它永恒的难题是终止性（泛化 = 加宽 = 限制 k），以及猜错时的退路。

**⑤ 归约到已解决的问题，并分层。** 每一代编译器的“归约目标”都是那一代最强的通用求解技术。归约的代价永远是信息丢失，而现代编译器的主要演进方向就是**推迟丢失**。

**贯穿全部的是三条元原则：**

**迭代到不动点。**
**换一个使问题变简单的表示。**
**决定何时承诺、何时丢弃信息，并为承诺出错准备一条可检测的退路。**

最后一条最难，也最重要。它解释了为什么 `SLR → LALR → LR(1)`、`SLL → LL`、`CHA → PIC`、`Tier-1 → Tier-N JIT`、`合一 → 包含约束`、`折叠 → 不动点`、`AOT → JIT + deopt` 这些看起来毫不相干的阶梯，其实是同一条阶梯。它也解释了为什么 **PEG 的有序选择**（Ordered Choice）、**贪心窥孔优化**（Greedy Peephole Optimization）、**上下文不敏感的指向分析**这三样东西的共同缺陷并不是“不够精确”，而是：**它们失败的时候，你无从知晓。**