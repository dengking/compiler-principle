# 初始代数与初始代数语义：从范畴论概念到程序语义方法

**Initial Algebras and Initial Algebra Semantics: From a Categorical Concept to a Semantic Methodology**

---

## 摘要（Abstract）

**初始代数（Initial Algebra）**是范畴论中的一个基本概念，指某个代数范畴中的**初始对象（Initial Object）**。**初始代数语义（Initial Algebra Semantics）**是在这一概念上建立的**语义方法论（Semantic Methodology）**：把语言的**抽象语法（Abstract Syntax）**视为初始代数，把语义视为另一个代数，把**意义函数（Meaning Function）**定义为二者之间唯一的**同态（Homomorphism）**。本文先从**泛代数（Universal Algebra）**与范畴论两个角度介绍初始代数，讨论它的基本性质与存在条件，再说明如何以它为基础构建初始代数语义，包括**等式规约（Equational Specification）**、**连续代数（Continuous Algebra）**与递归程序的语义，以及它的对偶理论**终余代数（Final Coalgebra）**。最后介绍它在**函数式编程（Functional Programming）**、**类型论（Type Theory）**和**代数规约（Algebraic Specification）**中的应用与现代发展。

**关键词（Keywords）**：初始代数（Initial Algebra）；F-代数（F-Algebra）；初始代数语义（Initial Algebra Semantics）；下态射（Catamorphism）；组合性（Compositionality）；结构归纳（Structural Induction）；终余代数（Final Coalgebra）

---

## 1. 引言（Introduction）

程序语言语义学需要回答两个问题：

1. 如何精确描述**归纳定义的数据类型（Inductively Defined Data Types）**，例如自然数、列表和语法树？
2. 如何为程序和表达式赋予意义，并保证这种意义是良定义的、可组合的、便于推理的？

1970 年代，**ADJ 小组（ADJ Group：J. A. Goguen、J. W. Thatcher、E. G. Wagner、J. B. Wright）**发现这两个问题可以用同一个数学结构回答，这个结构就是初始代数。

- 作为**概念**，初始代数刻画了"由构造子自由生成、不含多余元素、也没有多余等同"的数据结构。
- 作为**方法**，初始代数语义利用初始性给出的唯一同态来定义语义，从而自动得到良定义性、**组合性（Compositionality）**和**结构归纳原理（Structural Induction Principle）**。

二者的关系类似于**不动点（Fixed Point）**与**不动点语义（Fixed-Point Semantics）**的关系：前者是数学工具，后者是使用这一工具的语义框架。本文按照"概念、性质、方法、应用"的顺序把两部分内容整合起来。

---

## 2. 泛代数视角：签名与项代数（The Universal-Algebraic View: Signatures and Term Algebras）

### 2.1 签名与 Σ-代数（Signatures and Σ-Algebras）

一个**签名（Signature）** $\Sigma$ 是一组**运算符（Operators）**，每个运算符 $\sigma$ 带有一个**元数（Arity）** $\mathrm{ar}(\sigma)\in\mathbb{N}$。元数为 0 的运算符称为**常量（Constant）**。

一个 **Σ-代数（Σ-Algebra）** $A$ 由以下两部分组成：

- **载体集（Carrier Set）** $|A|$；
- 对每个 $\sigma\in\Sigma$ 的**解释（Interpretation）** $\sigma_A : |A|^{\mathrm{ar}(\sigma)}\to|A|$。

从 $A$ 到 $B$ 的 **Σ-同态（Σ-Homomorphism）**是一个保持所有运算的函数 $h:|A|\to|B|$：

$$
h(\sigma_A(a_1,\dots,a_n)) = \sigma_B(h(a_1),\dots,h(a_n))
$$

所有 Σ-代数及其同态构成范畴 $\mathbf{Alg}_\Sigma$。

### 2.2 项代数（Term Algebra）

由 $\Sigma$ 中运算符构造的全体**有限项（Finite Terms）**组成集合 $T_\Sigma$。令每个运算符按语法方式作用：

$$
\sigma_{T_\Sigma}(t_1,\dots,t_n) = \sigma(t_1,\dots,t_n)
$$

这样得到的 Σ-代数称为**项代数（Term Algebra）**。

> **定理 2.1（项代数的初始性）**：$T_\Sigma$ 是 $\mathbf{Alg}_\Sigma$ 的初始对象。也就是说，对任意 Σ-代数 $A$，存在唯一的 Σ-同态 $h_A: T_\Sigma\to A$。

**证明要点**：同态条件迫使 $h_A(\sigma(t_1,\dots,t_n)) = \sigma_A(h_A(t_1),\dots,h_A(t_n))$。对项的结构递归，这个等式既给出了 $h_A$ 的定义（存在性），也说明不可能有其他定义（唯一性）。∎

**例**：签名 $\Sigma=\{\mathtt{zero}:0,\ \mathtt{succ}:1\}$ 的项代数为 $\{\mathtt{zero},\ \mathtt{succ}(\mathtt{zero}),\ \mathtt{succ}(\mathtt{succ}(\mathtt{zero})),\dots\}$，同构于自然数 $\mathbb{N}$。

在 ADT 理论中通常还需要**多类签名（Many-Sorted Signature）**，即每个运算符带有输入类和输出类，如 `push : Stack × Elem → Stack`。上述结果可以直接推广到这种情形。

---

## 3. 范畴论视角：F-代数与初始代数（The Categorical View: F-Algebras and Initial Algebras）

### 3.1 F-代数（F-Algebra）

设 $\mathcal{C}$ 是一个**范畴（Category）**，$F:\mathcal{C}\to\mathcal{C}$ 是一个**自函子（Endofunctor）**。一个 **F-代数**是一个二元组 $(A,\alpha)$，其中

$$
\alpha : FA\to A
$$

$A$ 称为**载体（Carrier）**，$\alpha$ 称为**结构映射（Structure Map）**。

### 3.2 F-代数同态（F-Algebra Homomorphism）

从 $(A,\alpha)$ 到 $(B,\beta)$ 的同态是一个**态射（Morphism）** $h:A\to B$，使下图**交换（Commute）**：

$$
\begin{array}{ccc}
FA & \xrightarrow{\ \alpha\ } & A \\
\downarrow{\scriptstyle Fh} & & \downarrow{\scriptstyle h} \\
FB & \xrightarrow{\ \beta\ } & B
\end{array}
\qquad\text{即}\qquad h\circ\alpha=\beta\circ Fh
$$

F-代数及其同态构成范畴 $\mathbf{Alg}(F)$。

### 3.3 初始代数（Initial Algebra）

若 $(\mu F,\ \mathrm{in})$ 是 $\mathbf{Alg}(F)$ 的初始对象，则称它为 $F$ 的**初始代数**。此时对任意 F-代数 $(A,\alpha)$，存在唯一同态

$$
(\!|\alpha|\!):\mu F\to A
$$

这个同态称为**下态射（Catamorphism）**，在编程中也称为**折叠（Fold）**。记号 $(\!|\cdot|\!)$ 因形状被俗称为"香蕉括号（Banana Brackets）"。

### 3.4 两种表述的统一（Unifying the Two Formulations）

每个签名 $\Sigma$ 都诱导一个**多项式函子（Polynomial Functor）**：

$$
F_\Sigma(X)=\coprod_{\sigma\in\Sigma}X^{\mathrm{ar}(\sigma)}
$$

这时有范畴同构 $\mathbf{Alg}_\Sigma\cong\mathbf{Alg}(F_\Sigma)$，因此

$$
T_\Sigma\cong\mu F_\Sigma
$$

一个 $F_\Sigma$-代数 $\alpha:\coprod_\sigma A^{\mathrm{ar}(\sigma)}\to A$ 由**余积（Coproduct）**的泛性质分解为一组映射 $[\sigma_A]_{\sigma\in\Sigma}$，正好对应每个运算符的解释。

> **例**：$\Sigma=\{\mathtt{zero}:0,\ \mathtt{succ}:1,\ \mathtt{plus}:2\}$ 对应 $F_\Sigma(X)=1+X+X\times X$。

范畴论表述更为一般。它不依赖"集合加运算"的具体形式，可以用于任意范畴，例如**完全偏序（Complete Partial Order, CPO）**范畴或**预层范畴（Presheaf Category）**，从而能处理递归、变量绑定等更复杂的结构（见第 11 节）。

---

## 4. 初始代数的基本性质（Fundamental Properties）

### 4.1 Lambek 引理（Lambek's Lemma）

> **定理 4.1**：若 $(\mu F,\mathrm{in})$ 是初始代数，则 $\mathrm{in}:F(\mu F)\to\mu F$ 是**同构（Isomorphism）**。

**证明**：$(F(\mu F),\ F\,\mathrm{in})$ 也是一个 F-代数。由初始性，存在唯一同态 $g=(\!|F\,\mathrm{in}|\!):\mu F\to F(\mu F)$。容易验证 $\mathrm{in}$ 本身是从 $(F(\mu F),F\,\mathrm{in})$ 到 $(\mu F,\mathrm{in})$ 的同态，因此 $\mathrm{in}\circ g$ 是从 $\mu F$ 到自身的同态。由唯一性得 $\mathrm{in}\circ g=\mathrm{id}$。进一步有

$$
g\circ\mathrm{in}=F\,\mathrm{in}\circ Fg=F(\mathrm{in}\circ g)=\mathrm{id}
$$

∎

因此 $\mu F\cong F(\mu F)$，即 $\mu F$ 是方程 $X\cong FX$ 的解，而且是**最小不动点（Least Fixed Point）**。这正是记号 $\mu$ 的由来。

### 4.2 泛性质（Universal Property）

初始性可以等价地写成：

$$
h=(\!|\alpha|\!)\iff h\circ\mathrm{in}=\alpha\circ Fh
$$

由此可以推出以下**计算律（Calculational Laws）**：

| 名称 | 规律 | 含义 |
|---|---|---|
| 消去律（Cancellation Law） | $(\!|\alpha|\!)\circ\mathrm{in}=\alpha\circ F(\!|\alpha|\!)$ | fold 的计算规则 |
| 反射律（Reflection Law） | $(\!|\mathrm{in}|\!)=\mathrm{id}$ | 用构造子折叠等于恒等 |
| 融合律（Fusion Law） | 若 $h\circ\alpha=\beta\circ Fh$，则 $h\circ(\!|\alpha|\!)=(\!|\beta|\!)$ | 将后处理并入 fold |

融合律是**程序变换（Program Transformation）**和**消除中间数据结构（Deforestation）**的理论依据。

### 4.3 结构归纳原理（Structural Induction Principle）

初始性的**唯一性（Uniqueness）**部分等价于结构归纳法。要证明两个态射 $f,g:\mu F\to A$ 相等，只需证明它们都是同一个代数 $(A,\alpha)$ 的同态。

在 $\mathbf{Set}$ 中这还可以表述为谓词形式：若子集 $P\subseteq\mu F$ 对构造子封闭，即 $\mathrm{in}(F P)\subseteq P$，则 $P=\mu F$。这一点可以从"$\mu F$ 没有真子代数"直接推出。

### 4.4 存在性与唯一性的分工（Roles of Existence and Uniqueness）

| 初始性的组成 | 数学作用 | 编程/语义中的作用 |
|---|---|---|
| 存在性（Existence） | 存在一个同态 | 递归定义良定义，无需另证合法性 |
| 唯一性（Uniqueness） | 同态只有一个 | 支持归纳证明，规定唯一的语义 |
| 同态条件（Homomorphism Condition） | 交换图成立 | 组合性：整体意义由部分意义决定 |

后文的初始代数语义正是建立在这三点之上。

---

## 5. 初始代数的存在性（Existence of Initial Algebras）

### 5.1 反例（Counterexample）

并非每个函子都有初始代数。$\mathbf{Set}$ 上的**幂集函子（Powerset Functor）** $\mathcal{P}$ 没有初始代数：如果有，由 Lambek 引理会得到 $\mathcal{P}X\cong X$，这与 **Cantor 定理（Cantor's Theorem）**矛盾。

### 5.2 Adámek 定理（Adámek's Theorem）

> **定理 5.1**：设 $\mathcal{C}$ 有初始对象 $0$ 和 **ω-链（ω-Chain）**的**余极限（Colimit）**，且 $F$ 保持 ω-链的余极限（即 $F$ 是 **ω-余连续的（ω-Cocontinuous）**），则
> $$
> \mu F=\mathrm{colim}\big(0\xrightarrow{!}F0\xrightarrow{F!}F^20\xrightarrow{F^2!}\cdots\big)
> $$

这一构造与 **Kleene 不动点定理（Kleene Fixed-Point Theorem）** $\mathrm{lfp}(f)=\bigsqcup_n f^n(\bot)$ 形式一致。直观上，$F^n0$ 是"深度不超过 $n$ 的项"，取余极限就得到所有有限项。

由**常量函子（Constant Functor）**、**恒等函子（Identity Functor）**、有限**积（Product）**和**余积（Coproduct）**构成的有限元数多项式函子都是 ω-余连续的，因此都有初始代数。更一般地，**可达函子（Accessible Functor）**也都有初始代数，只是构造需要超限迭代（Transfinite Iteration）。

---

## 6. 典型例子（Canonical Examples）

| 数据类型 | 函子 $F X$ | 结构映射 $\mathrm{in}$ | 下态射 |
|---|---|---|---|
| 自然数（Natural Numbers） | $1+X$ | $[\mathrm{zero},\mathrm{succ}]$ | 迭代（Iteration） |
| 列表（Lists） | $1+E\times X$ | $[\mathrm{nil},\mathrm{cons}]$ | 右折叠（`foldr`） |
| 二叉树（Binary Trees） | $E+X\times X$ | $[\mathrm{leaf},\mathrm{node}]$ | 树折叠（Tree Fold） |
| 算术表达式（Arithmetic Expressions） | $\mathbb{Z}+X\times X+X\times X$ | $[\mathrm{lit},\mathrm{add},\mathrm{mul}]$ | 求值、打印等 |

**自然数**：代数 $[z,s]:1+A\to A$ 由零元 $z\in A$ 和后继 $s:A\to A$ 给出，唯一同态 $h:\mathbb{N}\to A$ 满足

$$
h(0)=z,\qquad h(n+1)=s(h(n))
$$

**列表**：下态射就是

```haskell
foldr :: (e -> a -> a) -> a -> [e] -> a
foldr f z []     = z
foldr f z (x:xs) = f x (foldr f z xs)
```

例如 `sum = foldr (+) 0`，`length = foldr (\_ n -> n + 1) 0`。

---

## 7. 初始代数语义（Initial Algebra Semantics）

### 7.1 基本思想（Basic Idea）

初始代数语义把"为语言定义语义"归结为三个步骤：

| 步骤 | 内容 | 数学对应 |
|---|---|---|
| ① 语法即初始代数（Syntax as Initial Algebra） | 用签名描述抽象语法 | $T_\Sigma\cong\mu F_\Sigma$ |
| ② 语义即代数（Semantics as an Algebra） | 选定**语义域（Semantic Domain）** $D$，为每个运算符给出解释 | $(D,\{\sigma_D\})$ |
| ③ 意义函数即唯一同态（Meaning Function as Unique Homomorphism） | 由初始性自动得到 | $\llbracket-\rrbracket:T_\Sigma\to D$ |

同态条件就是**组合性原则（Principle of Compositionality）**：

$$
\llbracket\sigma(t_1,\dots,t_n)\rrbracket=\sigma_D(\llbracket t_1\rrbracket,\dots,\llbracket t_n\rrbracket)
$$

也就是说，**表达式（Expression）**的意义只取决于其**子表达式（Subexpressions）**的意义和组合它们的运算符。这一原则通常追溯到 Frege，初始代数语义为它给出了精确的数学表述。

### 7.2 示例：一种语法，多种语义（One Syntax, Many Semantics）

```haskell
-- ① 语法：基函子（Base Functor），其初始代数即表达式语法树
data ExprF r = Lit Int | Add r r | Mul r r deriving Functor
type Expr = Fix ExprF

-- ② 语义：同一签名上的不同代数
evalAlg :: ExprF Int -> Int              -- 语义域：整数
evalAlg (Lit n)   = n
evalAlg (Add a b) = a + b
evalAlg (Mul a b) = a * b

showAlg :: ExprF String -> String        -- 语义域：字符串
showAlg (Lit n)   = show n
showAlg (Add a b) = "(" ++ a ++ " + " ++ b ++ ")"
showAlg (Mul a b) = a ++ " * " ++ b

depthAlg :: ExprF Int -> Int             -- 语义域：语法树深度
depthAlg (Lit _)   = 1
depthAlg (Add a b) = 1 + max a b
depthAlg (Mul a b) = 1 + max a b

-- ③ 意义函数：由初始性唯一确定
eval   = cata evalAlg
pretty = cata showAlg
depth  = cata depthAlg
```

求值、打印、计算深度、类型检查、编译到目标代码等，都只是同一初始代数到不同目标代数的唯一同态。

### 7.3 编译正确性：一个经典应用（Compiler Correctness）

Burstall–Landin（1969）和 Morris（1973）提出了用代数方法证明编译器正确性，ADJ 小组后来对此做了系统化。核心是下面的交换图：

$$
\begin{array}{ccc}
\text{源语言语法 } T_\Sigma & \xrightarrow{\ \text{compile}\ } & \text{目标语言 } T \\
\downarrow{\scriptstyle\llbracket-\rrbracket_S} & & \downarrow{\scriptstyle\llbracket-\rrbracket_T} \\
\text{源语义 } M & \xrightarrow{\ \text{encode}\ } & \text{目标语义 } U
\end{array}
$$

如果 compile、两个语义函数和 encode 都是 Σ-同态，那么两条路径都是从初始代数 $T_\Sigma$ 出发的同态，由唯一性立刻得到图交换，也就是编译正确。这是"唯一性即证明原理"的典型用法。

---

## 8. 带方程的初始代数与代数规约（Initial Algebras with Equations and Algebraic Specification）

### 8.1 等式规约（Equational Specification）

**抽象数据类型（Abstract Data Type, ADT）**的规约通常由签名和**方程（Equations）**组成，记为 $(\Sigma,E)$。满足 $E$ 的 Σ-代数构成一个**簇（Variety）** $\mathbf{Alg}_{(\Sigma,E)}$，其初始对象是**商项代数（Quotient Term Algebra）**：

$$
T_{\Sigma,E}=T_\Sigma/{\equiv_E}
$$

其中 $\equiv_E$ 是由 $E$ 生成的最小**同余关系（Congruence Relation）**。由泛代数中**自由代数（Free Algebra）**的存在性（Birkhoff）可知，等式规约的初始代数总是存在。

**示例**：

```
spec NAT =
  sorts  Nat
  ops    zero : → Nat
         succ : Nat → Nat
         plus : Nat × Nat → Nat
  eqns   plus(n, zero)    = n
         plus(n, succ(m)) = succ(plus(n, m))
```

其初始模型同构于 $\mathbb{N}$。项 `plus(succ(zero), succ(zero))` 与 `succ(succ(zero))` 属于同一等价类。

### 8.2 "无冗余，无混淆"（No Junk, No Confusion）

Burstall 与 Goguen 用这一口号刻画初始模型。设 $h:T_\Sigma\to A$ 是唯一同态：

| 口号 | 含义 | 数学条件 |
|---|---|---|
| 无冗余（No Junk） | 每个元素都能由某个项表示 | $h$ 是**满射（Surjective）**，即 $A$ 是**可达的（Reachable）** |
| 无混淆（No Confusion） | 只有能由 $E$ 推出相等的项才相等 | $\ker h={\equiv_E}$ |

$A$ 同构于初始模型，当且仅当这两条同时成立。

### 8.3 初始语义与其他规约语义（Initial Semantics vs. Other Specification Semantics）

在代数规约理论中，"初始代数语义"常简称为**初始语义（Initial Semantics）**，以区别于另外两种选择模型的方式：

| 语义 | 选取的模型 | 等式的判定原则 | 典型用途 |
|---|---|---|---|
| 初始语义（Initial Semantics） | 初始模型 $T_\Sigma/{\equiv_E}$ | 尽可能少地等同：不能证明相等就不相等 | 构造性数据类型；对应归纳法 |
| 终语义（Final / Terminal Semantics） | 终模型（通常在可达模型中取） | 尽可能多地等同：不能通过观察区分就相等 | 行为与状态系统；对应余归纳与互模拟 |
| 松散语义（Loose Semantics） | 所有满足规约的模型 | 不选定唯一模型 | 不完全规约与**逐步求精（Stepwise Refinement）** |

**示例**：在规约 `SET` 中若只给出 `insert(x, insert(x, s)) = insert(x, s)`，而没有给出交换律 `insert(x, insert(y, s)) = insert(y, insert(x, s))`，那么初始模型会把插入顺序不同的集合视为不同元素。也就是说，初始语义要求规约者把所有期望成立的等式**显式写出**。这既是它的严格之处，也是它的局限。

### 8.4 层次规约与充分完全性（Hierarchical Specifications and Sufficient Completeness）

实际规约通常是分层的：在已有规约（如 `BOOL`、`NAT`）之上扩展新的类和运算。为了保证扩展不破坏原有类型，人们引入两个条件：

- **充分完全性（Sufficient Completeness）**（Guttag, 1975）：新运算作用于旧类型时，其结果都能化归为旧类型的项。这保证扩展不引入新的冗余元素，即"No Junk"。
- **一致性（Consistency）/ 保守性（Conservativity）**：扩展不会使旧类型中原本不同的项变得相等，即"No Confusion"。

两者同时满足时，扩展称为**持久的（Persistent）**。这一框架在 OBJ、CafeOBJ、Maude、CASL 等语言中得到实现，其中 Maude 还借助**重写逻辑（Rewriting Logic）**把方程作为**项重写规则（Term Rewriting Rules）**来执行，从而使初始模型可以计算。

---

## 9. 连续代数与递归程序的语义（Continuous Algebras and the Semantics of Recursive Programs）

### 9.1 动机（Motivation）

项代数 $T_\Sigma$ 只含有限项，无法直接表达**递归定义（Recursive Definitions）**、**无限计算（Infinite Computations）**与**非终止（Non-Termination）**。ADJ 小组 1977 年论文标题中的 "Continuous Algebras" 正是为此而引入的。

### 9.2 连续代数（Continuous Algebra）

一个**连续 Σ-代数（Continuous Σ-Algebra）**满足：

- 载体是带最小元 $\bot$ 的**ω-完全偏序（ω-Complete Partial Order, ω-CPO）**；
- 每个运算 $\sigma_A$ 都是**单调的（Monotone）**和**连续的（Continuous）**，即保持 ω-链的上确界。

同态要求**严格（Strict）**且连续。在这个范畴中，初始对象是由**有限、部分与无限 Σ-树（Finite, Partial and Infinite Σ-Trees）**组成的代数 $CT_\Sigma$，偏序为"用更多结点替换 $\bot$"所得的**近似序（Approximation Order）**。

### 9.3 递归程序模式的语义（Semantics of Recursive Program Schemes）

一个**递归程序模式（Recursive Program Scheme）**是一组方程，例如

$$
\varphi(x)=\mathtt{if}\ p(x)\ \mathtt{then}\ x\ \mathtt{else}\ \varphi(f(x))
$$

初始代数语义按两步给出其意义：

1. **语法层面**：在 $CT_\Sigma$ 中把方程视为连续算子，取其最小不动点 $\bigsqcup_n \Phi^n(\bot)$，得到一棵可能无限的树，即程序的**语法展开（Syntactic Unfolding）**；
2. **语义层面**：对任意连续 Σ-代数 $D$（即对 $p$、$f$ 等基本运算的任意解释），由初始性得到唯一的连续同态 $CT_\Sigma\to D$，把这棵树映射为程序在 $D$ 中的意义。

这种方法的优点在于**语法与解释分离**：递归的不动点只需在语法层面计算一次，对所有解释都适用。这一结果被称为**Mezei–Wright 定理（Mezei–Wright Theorem）**的连续版本。

### 9.4 与指称语义的联系（Connection with Denotational Semantics）

连续代数把初始代数语义与 **Scott–Strachey 指称语义（Scott–Strachey Denotational Semantics）**连接起来：

- 指称语义中的**语义域（Semantic Domains）**正是 CPO；
- 语义方程的组合性对应同态条件；
- 递归定义通过 Kleene 不动点定理求解，对应第 5 节 Adámek 定理中的 ω-链余极限。

---

## 10. 对偶理论：终余代数与终语义（Duality: Final Coalgebras and Final Semantics）

### 10.1 F-余代数（F-Coalgebra）

将 F-代数中的箭头反转，得到 **F-余代数** $(A,\gamma)$，其中 $\gamma:A\to FA$。余代数同态 $h:A\to B$ 满足 $\delta\circ h=Fh\circ\gamma$。若 $(\nu F,\mathrm{out})$ 是余代数范畴的**终对象（Terminal Object）**，则称它为**终余代数（Final Coalgebra）**。对任意余代数 $(A,\gamma)$ 存在唯一同态

$$
[\!(\gamma)\!]:A\to\nu F
$$

称为**上态射（Anamorphism）**，即**展开（Unfold）**。

### 10.2 对偶性质（Dual Properties）

| 初始代数（Initial Algebra） | 终余代数（Final Coalgebra） |
|---|---|
| 归纳类型（Inductive Types），有限数据 | 余归纳类型（Coinductive Types），可能无限的数据，如**流（Streams）** |
| 构造子（Constructors） | 析构子（Destructors）/ 观察（Observations） |
| 下态射（Catamorphism, fold） | 上态射（Anamorphism, unfold） |
| Lambek 引理：$\mathrm{in}$ 是同构 | 对偶 Lambek 引理：$\mathrm{out}$ 是同构 |
| 最小不动点 $\mu F$ | 最大不动点 $\nu F$ |
| 唯一性 ⇒ 归纳法（Induction） | 唯一性 ⇒ 余归纳法（Coinduction） |
| 同余关系（Congruence） | 互模拟（Bisimulation） |
| Adámek：$0\to F0\to F^20\to\cdots$ 的余极限 | Barr / Worrell：$1\leftarrow F1\leftarrow F^21\leftarrow\cdots$ 的极限（可能需超限延续） |
| 初始语义 | 终语义 |

**例**：对 $FX=E\times X$，$\nu F$ 是 $E$ 上的无限流 $E^\omega$，$\mathrm{out}=\langle\mathrm{head},\mathrm{tail}\rangle$。

### 10.3 余归纳证明原理（Coinduction Proof Principle）

在 $\mathbf{Set}$ 中，若关系 $R\subseteq\nu F\times\nu F$ 是一个互模拟，则 $R\subseteq\Delta$（对角线），即互模拟的元素必然相等。这是终余代数唯一性的直接推论，也是**进程演算（Process Calculi）**中**行为等价（Behavioural Equivalence）**理论的基础（Aczel 的**非良基集合（Non-Well-Founded Sets）**，Rutten 的**泛余代数（Universal Coalgebra）**）。

### 10.4 代数紧致性（Algebraic Compactness）

在一些范畴中，$\mu F$ 与 $\nu F$ 重合。典型情形是以严格连续函数为态射的 CPO 范畴 $\mathbf{CPO}_\bot$：对**局部连续函子（Locally Continuous Functor）**，初始代数与终余代数的载体同构（Smyth–Plotkin, 1982）。Freyd 把这一性质称为**代数紧致性（Algebraic Compactness）**。

Haskell 等**惰性语言（Lazy Languages）**的语义正属于这种情形：同一个 `data` 声明既可以容纳有限列表，也可以容纳无限列表，fold 和 unfold 作用于同一个类型。这也是**复合态射（Hylomorphism）** $(\!|\alpha|\!)\circ[\!(\gamma)\!]$ 可以在这类语言中直接定义的原因。代价是失去了一部分归纳推理能力，因为类型中包含部分值和无限值。

---

## 11. 推广与现代发展（Generalisations and Modern Developments）

初始代数语义的范畴论表述可以推广到多种更丰富的结构。

### 11.1 变量绑定的抽象语法（Abstract Syntax with Variable Binding）

普通签名无法表达 λ-抽象这类**绑定构造（Binding Constructs）**。两种主要解决方案：

- **预层方法（Presheaf Approach）**（Fiore, Plotkin, Turi, 1999）：在预层范畴 $\mathbf{Set}^{\mathbb{F}}$（$\mathbb{F}$ 为有限集与函数构成的范畴）中，λ-演算的项是函子
  $$
  F(X)=V+X\times X+\delta X
  $$
  的初始代数，其中 $V$ 是变量预层，$\delta X(n)=X(n+1)$ 表示"多绑定一个变量"。替换（Substitution）由额外的**幺半群结构（Monoid Structure）**刻画。
- **名义集方法（Nominal Sets Approach）**（Gabbay, Pitts, 1999）：在名义集范畴中把 α-等价直接内建于载体，从而可以对模 α-等价的项做结构递归与归纳。

### 11.2 嵌套数据类型与 GADT（Nested Data Types and GADTs）

形如 `data Nest a = Nil | Cons a (Nest (a, a))` 的**嵌套数据类型（Nested Data Types）**中，递归调用的类型参数发生变化，不能用 $\mathbf{Set}$ 上的初始代数描述。解决方法是将其视为**函子范畴（Functor Category）** $[\mathbf{Set},\mathbf{Set}]$ 上的**高阶函子（Higher-Order Functor）**的初始代数（Bird & Meertens, 1998；Bird & Paterson, 1999）。Johann 与 Ghani（2008）进一步证明，**广义代数数据类型（Generalised Algebraic Data Types, GADTs）**也可以纳入初始代数语义框架。

### 11.3 归纳族与依赖类型（Inductive Families and Dependent Types）

在**依赖类型论（Dependent Type Theory）**中：

- **W-类型（W-Types）**是**多项式函子 / 容器（Containers）**的初始代数（Moerdijk & Palmgren, 2000；Abbott, Altenkirch, Ghani, 2005）；
- **归纳族（Inductive Families）**（Dybjer, 1994），如长度索引的向量 `Vec A n`，是**索引容器（Indexed Containers）**在切片范畴（Slice Category）$\mathbf{Set}/I$ 中的初始代数；
- **归纳-递归（Induction-Recursion）**与**归纳-归纳（Induction-Induction）**定义也都有对应的初始代数刻画。

### 11.4 同伦类型论中的高阶归纳类型（Higher Inductive Types in Homotopy Type Theory）

在**同伦类型论（Homotopy Type Theory, HoTT）**中，"初始"需要换成**同伦初始（Homotopy-Initial）**：从该代数出发的同态空间是**可缩的（Contractible）**。Awodey、Gambino 和 Sojakova（2012）证明：

$$
\text{W-类型满足依赖消去规则} \iff \text{它是同伦初始代数}
$$

这在类型论内部严格确立了"初始性 ⇔ 归纳原理"的对应。**高阶归纳类型（Higher Inductive Types, HITs）**与**商归纳类型（Quotient Inductive Types, QITs）**（Altenkirch & Kaposi, 2016）可以看作第 8 节"带方程的初始代数"在类型论中的对应物：构造子不仅生成元素，还生成等式。

### 11.5 自由单子与代数效应（Free Monads and Algebraic Effects）

对函子 $F$ 和对象 $A$，

$$
F^*A=\mu X.\ A+FX
$$

是 $F$ 生成的**自由单子（Free Monad）**。在**代数效应（Algebraic Effects）**理论（Plotkin & Power, 2001–2003）中，带效应的计算被视为某个效应签名上的项，**效应处理器（Effect Handlers）**（Plotkin & Pretnar, 2009）则是从自由模型出发的唯一同态，也就是一种 fold。这可以看作初始代数语义在计算效应上的直接延伸。

### 11.6 广义折叠（Generalised Folds）

普通 fold 并不能直接表达所有结构递归。人们由此提出多种推广：

- **Mendler 风格迭代（Mendler-Style Iteration）**：不需要 $F$ 是函子，适用于更广泛的类型；
- **伴随折叠（Adjoint Folds）**（Hinze, 2013）：利用伴随函子把 mutual recursion、带累积参数的递归等统一为 fold；
- **共变/反变混合的数据类型**的语义需借助**混合变异函子（Mixed-Variance Functors）**与**二元化（Dinaturality）**技术处理。

---

## 12. 在函数式编程中的应用（Applications in Functional Programming）

### 12.1 不动点类型与下态射（Fixed-Point Types and Catamorphisms）

```haskell
{-# LANGUAGE DeriveFunctor #-}

newtype Fix f = In { out :: f (Fix f) }     -- 不动点类型（Fixed-Point Type）

cata :: Functor f => (f a -> a) -> Fix f -> a        -- 下态射（Catamorphism）
cata alg = alg . fmap (cata alg) . out

ana :: Functor f => (a -> f a) -> a -> Fix f          -- 上态射（Anamorphism）
ana coalg = In . fmap (ana coalg) . coalg

hylo :: Functor f => (f b -> b) -> (a -> f a) -> a -> b   -- 复合态射（Hylomorphism）
hylo alg coalg = alg . fmap (hylo alg coalg) . coalg
```

`cata` 的定义正是消去律 $(\!|\alpha|\!)\circ\mathrm{in}=\alpha\circ F(\!|\alpha|\!)$ 的直接转写。

### 12.2 递归模式（Recursion Schemes）

| 递归模式 | 英文 | 提出者 | 特点 |
|---|---|---|---|
| 下态射 | Catamorphism | Meijer 等（1991） | 基本结构递归 |
| 旁态射 | Paramorphism | Meertens（1992） | 递归时可访问原始子结构，对应原始递归 |
| 历史态射 | Histomorphism | Uustalu & Vene（1999） | 可访问所有先前计算结果，对应**值过程递归（Course-of-Values Recursion）** |
| 复合态射 | Hylomorphism | Meijer 等（1991） | 先展开再折叠，中间结构可被消除 |
| 上态射 | Anamorphism | Meijer 等（1991） | 由种子生成结构 |
| 拟态射 | Apomorphism | Vene & Uustalu（1998） | 旁态射的对偶，可提前终止展开 |
| 未来态射 | Futumorphism | Uustalu & Vene（1999） | 历史态射的对偶 |

Hinze、Wu 与 Gibbons（2013）在论文 *Unifying Structured Recursion Schemes* 中利用**共轭链（Conjugate Hylomorphisms）**和伴随函子把这些模式统一起来。

### 12.3 程序融合（Program Fusion）

融合律直接给出了程序优化规则。以 GHC 的**短路融合（Shortcut Fusion）**（Gill, Launchbury, Peyton Jones, 1993）为例：

```haskell
build :: (forall b. (a -> b -> b) -> b -> b) -> [a]
build g = g (:) []

-- foldr/build 规则：
--   foldr k z (build g) = g k z
```

这条规则可以从初始代数的泛性质与**参数性（Parametricity）**推出。它消除了中间列表的分配，例如 `sum (map f (filter p xs))` 会被编译为一个不分配中间列表的循环。

### 12.4 数据类型通用编程（Datatype-Generic Programming）

由于所有代数数据类型都是某个多项式函子的初始代数，许多函数（相等判断、序列化、映射、遍历）可以对函子结构一次性定义，然后自动适用于所有数据类型。这是 PolyP、Generic Haskell 以及 GHC `GHC.Generics` 等**通用编程（Generic Programming）**工具的理论基础。

---

## 13. 应用领域总览（Overview of Application Areas）

| 领域 | 初始代数的角色 | 代表工作或系统 |
|---|---|---|
| 抽象数据类型规约（ADT Specification） | 规约的标准模型 | OBJ, CafeOBJ, Maude, CASL |
| 指称语义（Denotational Semantics） | 组合性语义 = 唯一同态 | ADJ（1977）；连续代数 |
| 编译器正确性（Compiler Correctness） | 唯一性给出交换图 | Burstall–Landin（1969）；Morris（1973）；Thatcher–Wagner–Wright（1980） |
| 类型论与证明助手（Type Theory and Proof Assistants） | 归纳类型及其**消去规则（Elimination Rules）** | Coq / Rocq, Agda, Lean, Idris |
| 函数式编程（Functional Programming） | fold 与递归模式 | Haskell, OCaml, Scala 的 recursion-schemes 库 |
| 程序推导与优化（Program Derivation and Optimisation） | 融合律 | Bird–Meertens 形式化（Squiggol）；GHC 重写规则 |
| 编译器构造（Compiler Construction） | 语法树遍历、**属性文法（Attribute Grammars）** | 属性文法的 catamorphism 解读（Fokkinga 等） |
| 代数效应（Algebraic Effects） | 自由模型与处理器 | Eff, Koka, OCaml 5 效应处理器 |
| 形式化元理论（Formalised Metatheory） | 带绑定的抽象语法 | 预层语义；名义逻辑（Nominal Isabelle） |

---

## 14. 结论（Conclusion）

初始代数与初始代数语义的关系可以概括为一句话：**初始代数提供了"唯一同态"这一数学事实，初始代数语义则把这一事实用作定义语义与进行推理的方法。**

$$
\underbrace{(\mu F,\ \mathrm{in})}_{\text{初始代数：概念}}
\ \xrightarrow{\ \text{初始性：对任意 }(A,\alpha)\text{ 存在唯一同态}\ }\
\underbrace{\llbracket-\rrbracket=(\!|\alpha|\!)}_{\text{初始代数语义：方法}}
$$

初始性的三个组成部分分别对应语义学中的三项基本要求：

| 初始性 | 语义学要求 |
|---|---|
| 存在性（Existence） | 语义定义是良定义的（Well-Definedness） |
| 唯一性（Uniqueness） | 语义可以由结构归纳推理（Induction） |
| 同态条件（Homomorphism Condition） | 语义满足组合性（Compositionality） |

从 Birkhoff 的泛代数、Lambek 的不动点引理，到 ADJ 小组的系统化理论，再到函数式编程中的递归模式、依赖类型论中的归纳族和同伦类型论中的高阶归纳类型，初始代数始终是描述"由构造生成的事物"的核心工具。它的对偶，终余代数，则为"由观察刻画的事物"提供了同样精确的框架。两者共同构成了现代程序语义学的代数与余代数基础。

---

## 参考文献（References）

**奠基性文献（Foundational Works）**

1. Birkhoff, G. *On the Structure of Abstract Algebras*. Proceedings of the Cambridge Philosophical Society, 31, 1935.
2. Lambek, J. *A Fixpoint Theorem for Complete Categories*. Mathematische Zeitschrift, 103, 1968.
3. Burstall, R. M., Landin, P. J. *Programs and Their Proofs: An Algebraic Approach*. Machine Intelligence 4, 1969.
4. Adámek, J. *Free Algebras and Automata Realizations in the Language of Categories*. Commentationes Mathematicae Universitatis Carolinae, 15, 1974.
5. Goguen, J. A., Thatcher, J. W., Wagner, E. G., Wright, J. B. *Initial Algebra Semantics and Continuous Algebras*. Journal of the ACM, 24(1), 1977.
6. Goguen, J. A., Thatcher, J. W., Wagner, E. G. *An Initial Algebra Approach to the Specification, Correctness, and Implementation of Abstract Data Types*. In Current Trends in Programming Methodology IV, 1978.

**代数规约（Algebraic Specification）**

7. Guttag, J. V., Horning, J. J. *The Algebraic Specification of Abstract Data Types*. Acta Informatica, 10, 1978.
8. Ehrig, H., Mahr, B. *Fundamentals of Algebraic Specification 1: Equations and Initial Semantics*. Springer, 1985.
9. Goguen, J. A., Malcolm, G. (eds.) *Software Engineering with OBJ: Algebraic Specification in Action*. Kluwer, 2000.

**程序计算与递归模式（Program Calculation and Recursion Schemes）**

10. Meijer, E., Fokkinga, M., Paterson, R. *Functional Programming with Bananas, Lenses, Envelopes and Barbed Wire*. FPCA, 1991.
11. Gill, A., Launchbury, J., Peyton Jones, S. *A Short Cut to Deforestation*. FPCA, 1993.
12. Bird, R., de Moor, O. *Algebra of Programming*. Prentice Hall, 1997.
13. Hinze, R. *Adjoint Folds and Unfolds: An Extended Study*. Science of Computer Programming, 78(11), 2013.
14. Hinze, R., Wu, N., Gibbons, J. *Unifying Structured Recursion Schemes*. ICFP, 2013.
15. Meertens, L. *Paramorphisms*. Formal Aspects of Computing, 4(5), 1992.
16. Uustalu, T., Vene, V. *Primitive (Co)Recursion and Course-of-Value (Co)Iteration, Categorically*. Informatica, 10(1), 1999.
17. Vene, V., Uustalu, T. *Functional Programming with Apomorphisms (Corecursion)*. Proceedings of the Estonian Academy of Sciences: Physics, Mathematics, 47(3), 1998.

**语义、编译正确性与递归程序（Semantics, Compiler Correctness and Recursive Programs）**

18. Mezei, J., Wright, J. B. *Algebraic Automata and Context-Free Sets*. Information and Control, 11, 1967.
19. Morris, F. L. *Advice on Structuring Compilers and Proving Them Correct*. POPL, 1973.
20. Thatcher, J. W., Wagner, E. G., Wright, J. B. *More on Advice on Structuring Compilers and Proving Them Correct*. Theoretical Computer Science, 15(3), 1981.
21. Burstall, R. M., Goguen, J. A. *Algebras, Theories and Freeness: An Introduction for Computer Scientists*. In Theoretical Foundations of Programming Methodology, Reidel, 1982.
22. Guttag, J. V. *The Specification and Application to Programming of Abstract Data Types*. PhD Thesis, University of Toronto, 1975.
23. Meseguer, J. *Conditional Rewriting Logic as a Unified Model of Concurrency*. Theoretical Computer Science, 96(1), 1992.

**论域理论与余代数（Domain Theory and Coalgebra）**

24. Smyth, M. B., Plotkin, G. D. *The Category-Theoretic Solution of Recursive Domain Equations*. SIAM Journal on Computing, 11(4), 1982.
25. Freyd, P. *Algebraically Complete Categories*. In Category Theory (Como 1990), LNM 1488, Springer, 1991.
26. Aczel, P. *Non-Well-Founded Sets*. CSLI Lecture Notes 14, 1988.
27. Barr, M. *Terminal Coalgebras in Well-Founded Set Theory*. Theoretical Computer Science, 114(2), 1993.
28. Worrell, J. *On the Final Sequence of a Finitary Set Functor*. Theoretical Computer Science, 338, 2005.
29. Jacobs, B., Rutten, J. *A Tutorial on (Co)Algebras and (Co)Induction*. Bulletin of the EATCS, 62, 1997.
30. Rutten, J. *Universal Coalgebra: A Theory of Systems*. Theoretical Computer Science, 249(1), 2000.

**推广与现代发展（Generalisations and Modern Developments）**

31. Fiore, M., Plotkin, G., Turi, D. *Abstract Syntax and Variable Binding*. LICS, 1999.
32. Gabbay, M. J., Pitts, A. M. *A New Approach to Abstract Syntax Involving Binders*. LICS, 1999.
33. Bird, R., Meertens, L. *Nested Datatypes*. MPC, LNCS 1422, 1998.
34. Bird, R., Paterson, R. *Generalised Folds for Nested Datatypes*. Formal Aspects of Computing, 11(2), 1999.
35. Johann, P., Ghani, N. *Foundations for Structured Programming with GADTs*. POPL, 2008.
36. Dybjer, P. *Inductive Families*. Formal Aspects of Computing, 6(4), 1994.
37. Moerdijk, I., Palmgren, E. *Wellfounded Trees in Categories*. Annals of Pure and Applied Logic, 104, 2000.
38. Abbott, M., Altenkirch, T., Ghani, N. *Containers: Constructing Strictly Positive Types*. Theoretical Computer Science, 342(1), 2005.
39. Awodey, S., Gambino, N., Sojakova, K. *Inductive Types in Homotopy Type Theory*. LICS, 2012.
40. Altenkirch, T., Kaposi, A. *Type Theory in Type Theory Using Quotient Inductive Types*. POPL, 2016.
41. Plotkin, G., Power, J. *Algebraic Operations and Generic Effects*. Applied Categorical Structures, 11(1), 2003.
42. Plotkin, G., Pretnar, M. *Handlers of Algebraic Effects*. ESOP, LNCS 5502, 2009.

---

## 附录 A：符号表（Notation）

| 符号 | 含义 | English |
|---|---|---|
| $\mathcal{C}$ | 范畴 | Category |
| $F:\mathcal{C}\to\mathcal{C}$ | 自函子 | Endofunctor |
| $(A,\alpha)$，$\alpha:FA\to A$ | F-代数 | F-Algebra |
| $(A,\gamma)$，$\gamma:A\to FA$ | F-余代数 | F-Coalgebra |
| $\mathbf{Alg}(F)$ | F-代数范畴 | Category of F-Algebras |
| $\mathbf{Alg}_\Sigma$ | Σ-代数范畴 | Category of Σ-Algebras |
| $(\mu F,\mathrm{in})$ | 初始代数 | Initial Algebra |
| $(\nu F,\mathrm{out})$ | 终余代数 | Final Coalgebra |
| $(\!\vert\alpha\vert\!)$ | 下态射（香蕉括号） | Catamorphism (Banana Brackets) |
| $[\!(\gamma)\!]$ | 上态射（透镜括号） | Anamorphism (Lens Brackets) |
| $T_\Sigma$ | 项代数 | Term Algebra |
| $T_\Sigma/{\equiv_E}$ | 商项代数 | Quotient Term Algebra |
| $CT_\Sigma$ | 初始连续代数（有限、部分与无限树） | Initial Continuous Algebra |
| $F_\Sigma$ | 签名诱导的多项式函子 | Polynomial Functor Induced by a Signature |
| $\llbracket-\rrbracket$ | 意义函数 | Meaning Function |
| $\bot$ | 最小元（未定义） | Bottom (Undefined) |
| $F^*A$ | 自由单子 | Free Monad |

---

## 附录 B：术语对照表（Glossary）

### B.1 范畴论基础（Category-Theoretic Foundations）

| 中文 | English | 中文 | English |
|---|---|---|---|
| 范畴论 | Category Theory | 范畴 | Category |
| 函子 | Functor | 自函子 | Endofunctor |
| 态射 | Morphism | 同构 | Isomorphism |
| 初始对象 | Initial Object | 终对象 | Terminal Object |
| 交换图 | Commutative Diagram | 泛性质 | Universal Property |
| 积 | Product | 余积 / 和 | Coproduct / Sum |
| 极限 | Limit | 余极限 | Colimit |
| ω-链 | ω-Chain | ω-余连续 | ω-Cocontinuous |
| 多项式函子 | Polynomial Functor | 可达函子 | Accessible Functor |
| 幂集函子 | Powerset Functor | 函子范畴 | Functor Category |
| 预层范畴 | Presheaf Category | 切片范畴 | Slice Category |
| 伴随函子 | Adjoint Functors | 超限迭代 | Transfinite Iteration |

### B.2 代数与余代数（Algebras and Coalgebras）

| 中文 | English | 中文 | English |
|---|---|---|---|
| 初始代数 | Initial Algebra | 终余代数 | Final / Terminal Coalgebra |
| F-代数 | F-Algebra | F-余代数 | F-Coalgebra |
| 载体 / 载体集 | Carrier / Carrier Set | 结构映射 | Structure Map |
| 同态 | Homomorphism | 初始性 | Initiality |
| 泛代数 | Universal Algebra | Σ-代数 | Σ-Algebra |
| 签名 | Signature | 多类签名 | Many-Sorted Signature |
| 运算符 | Operator | 元数 | Arity |
| 项代数 | Term Algebra | 商项代数 | Quotient Term Algebra |
| 自由代数 | Free Algebra | 簇 | Variety |
| 同余关系 | Congruence Relation | 互模拟 | Bisimulation |
| Lambek 引理 | Lambek's Lemma | Adámek 定理 | Adámek's Theorem |
| 最小不动点 | Least Fixed Point | 最大不动点 | Greatest Fixed Point |
| 代数紧致性 | Algebraic Compactness | 局部连续函子 | Locally Continuous Functor |

### B.3 语义与规约（Semantics and Specification）

| 中文 | English | 中文 | English |
|---|---|---|---|
| 初始代数语义 | Initial Algebra Semantics | 语义方法论 | Semantic Methodology |
| 初始语义 | Initial Semantics | 终语义 | Final / Terminal Semantics |
| 松散语义 | Loose Semantics | 指称语义 | Denotational Semantics |
| 抽象语法 | Abstract Syntax | 语义域 | Semantic Domain |
| 意义函数 | Meaning Function | 组合性 | Compositionality |
| 良定义 | Well-Defined | 解释 | Interpretation |
| 抽象数据类型 | Abstract Data Type (ADT) | 等式规约 | Equational Specification |
| 代数规约 | Algebraic Specification | 逐步求精 | Stepwise Refinement |
| 无冗余 / 无混淆 | No Junk / No Confusion | 可达的 | Reachable |
| 充分完全性 | Sufficient Completeness | 持久的 | Persistent |
| 保守性 | Conservativity | 重写逻辑 | Rewriting Logic |
| 项重写 | Term Rewriting | 编译器正确性 | Compiler Correctness |
| 连续代数 | Continuous Algebra | 完全偏序 | Complete Partial Order (CPO) |
| 近似序 | Approximation Order | 严格函数 | Strict Function |
| 递归程序模式 | Recursive Program Scheme | 语法展开 | Syntactic Unfolding |
| 非终止 | Non-Termination | 行为等价 | Behavioural Equivalence |
| 进程演算 | Process Calculus | 非良基集合 | Non-Well-Founded Sets |

### B.4 递归、归纳与编程（Recursion, Induction and Programming）

| 中文 | English | 中文 | English |
|---|---|---|---|
| 归纳类型 | Inductive Type | 余归纳类型 | Coinductive Type |
| 构造子 | Constructor | 析构子 | Destructor |
| 结构递归 | Structural Recursion | 原始递归 | Primitive Recursion |
| 结构归纳法 | Structural Induction | 余归纳法 | Coinduction |
| 值过程递归 | Course-of-Values Recursion | 递归模式 | Recursion Schemes |
| 下态射 / 折叠 | Catamorphism / Fold | 上态射 / 展开 | Anamorphism / Unfold |
| 旁态射 | Paramorphism | 拟态射 | Apomorphism |
| 历史态射 | Histomorphism | 未来态射 | Futumorphism |
| 复合态射 | Hylomorphism | 伴随折叠 | Adjoint Fold |
| Mendler 风格迭代 | Mendler-Style Iteration | 基函子 | Base Functor |
| 消去律 | Cancellation Law | 反射律 | Reflection Law |
| 融合律 | Fusion Law | 短路融合 | Shortcut Fusion |
| 消除中间数据结构 | Deforestation | 程序变换 | Program Transformation |
| 参数性 | Parametricity | 通用编程 | (Datatype-)Generic Programming |
| 惰性语言 | Lazy Language | 流 | Stream |
| 自由单子 | Free Monad | 代数效应 | Algebraic Effects |
| 效应处理器 | Effect Handler | 属性文法 | Attribute Grammar |

### B.5 类型论（Type Theory）

| 中文 | English | 中文 | English |
|---|---|---|---|
| 依赖类型论 | Dependent Type Theory | 证明助手 | Proof Assistant |
| 消去规则 | Elimination Rule | W-类型 | W-Type |
| 容器 | Container | 索引容器 | Indexed Container |
| 归纳族 | Inductive Family | 嵌套数据类型 | Nested Data Type |
| 广义代数数据类型 | Generalised Algebraic Data Type (GADT) | 归纳-递归 | Induction-Recursion |
| 归纳-归纳 | Induction-Induction | 同伦类型论 | Homotopy Type Theory (HoTT) |
| 同伦初始 | Homotopy-Initial | 可缩的 | Contractible |
| 高阶归纳类型 | Higher Inductive Type (HIT) | 商归纳类型 | Quotient Inductive Type (QIT) |
| 变量绑定 | Variable Binding | 名义集 | Nominal Sets |
| α-等价 | α-Equivalence | 替换 | Substitution |

---

## 附录 C：勘误（Errata）

正文中有两处术语翻译需要更正：

1. **第 11.6 节**："二元化（Dinaturality）"应为"**双自然性（Dinaturality）**"。该术语指混合变异函子之间的双自然变换（Dinatural Transformation）。
2. **第 12.2 节**："共轭链（Conjugate Hylomorphisms）"应为"**共轭复合态射（Conjugate Hylomorphisms）**"。Hinze、Wu 与 Gibbons 的统一框架以伴随函子和共轭复合态射（hylomorphism）为核心，并不涉及"链"。

另外，第 7.3 节中 Thatcher–Wagner–Wright 关于编译正确性的工作，在第 13 节表格中标为 1980 年。该工作最初以会议论文形式发表于 ICALP 1979，期刊版本见参考文献 [20]（TCS, 1981）。