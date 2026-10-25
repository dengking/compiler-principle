# 上下文无关文法中的直接递归与间接递归

## 摘要

递归是上下文无关文法（CFG）能描述无限语言和任意深度嵌套结构的根本原因，也给语法分析器的构造带来了问题。本文从形式定义出发，区分**直接递归**与**间接递归**，并按递归位置将其细分为**左递归**、**右递归**和**自嵌套递归**。随后讨论递归的**图论检测方法**、左递归的消除算法（包括间接左递归的系统化消除），以及各类递归对 LL、LR、PEG 等分析技术的影响。最后从形式语言理论的角度说明自嵌套递归与语言表达能力的关系。

---

## 1. 基本定义

### 1.1 文法与推导

设上下文无关文法 $G = (N, \Sigma, P, S)$，其中 $N$ 为非终结符集合，$\Sigma$ 为终结符集合，$P$ 为产生式集合，$S$ 为开始符号。记：

- $\Rightarrow$：一步推导；
- $\Rightarrow^+$：一步或多步推导；
- $\Rightarrow^*$：零步或多步推导。

下文默认文法是**化简的**（reduced），即每个非终结符都可达（从 $S$ 出发能推导出含它的句型），且有用（能推导出终结符串）。

### 1.2 递归非终结符

**定义 1（递归）** 非终结符 $A$ 是递归的，当且仅当存在推导

$$A \Rightarrow^+ \alpha A \beta,\quad \alpha, \beta \in (N \cup \Sigma)^*$$

一个文法是递归文法，当且仅当它至少含有一个**递归非终结符**。对于化简文法，$L(G)$ 是**无限语言**当且仅当 $G$ 是递归的（忽略只产生 $A \Rightarrow^+ A$ 这类环的平凡情形）。

### 1.3 直接递归与间接递归

**定义 2（直接递归）** 若 $P$ 中存在产生式 $A \to \alpha A \beta$，则称 $A$ 是**直接递归**（immediate / direct recursion）的。

**定义 3（间接递归）** 若存在推导

$$A \Rightarrow \gamma_1 B_1 \delta_1 \Rightarrow^* \cdots \Rightarrow^* \alpha A \beta$$

其中递归路径经过至少一个不同于 $A$ 的非终结符 $B_1, \dots, B_k$，则称 $A$ 是**间接递归**（indirect recursion）的。若参与循环的多个非终结符彼此可达，也称它们**相互递归**（mutual recursion）。

两者并不互斥：同一个非终结符可以既有直接递归产生式，又处在间接递归的环路上。

### 1.4 按递归位置分类

根据 $A$ 在递归句型中的位置，可做如下正交分类：

| 类型    | 形式                                                                     | 说明           |
| ----- | ---------------------------------------------------------------------- | ------------ |
| 左递归   | $A \Rightarrow^+ A\beta$                                               | $A$ 出现在句型最左端 |
| 右递归   | $A \Rightarrow^+ \alpha A$                                             | $A$ 出现在句型最右端 |
| 自嵌套递归 | $A \Rightarrow^+ \alpha A \beta$，$\alpha, \beta \Rightarrow^* $ 非空终结符串 | $A$ 两侧均有实际内容 |

将"直接/间接"与"左/右/自嵌套"组合，得到六种情形。以经典表达式文法（ETF 文法）为例：

```
E → E + T | T
T → T * F | F
F → ( E ) | id
```

| 非终结符 | 递归形式 | 类别 |
|---|---|---|
| E | $E \to E + T$ | 直接左递归 |
| T | $T \to T * F$ | 直接左递归 |
| F | $F \Rightarrow (E) \Rightarrow (T) \Rightarrow (F)$ | 间接自嵌套递归 |
| E | $E \Rightarrow T \Rightarrow F \Rightarrow (E)$ | 间接自嵌套递归 |

可见 E 同时具有**直接左递归**和**间接自嵌套递归**。

### 1.5 两种需要特别注意的情形

**隐藏左递归（hidden left recursion）**：

```
A → B A c | d
B → b | ε
```

产生式 $A \to BAc$ 字面上不以 $A$ 开头，但由于 $B \Rightarrow^* \varepsilon$，有 $A \Rightarrow BAc \Rightarrow Ac$，所以 $A$ 是左递归的。这类递归不易察觉，判断时必须考虑可空（nullable）符号。

**环（cycle）**：若 $A \Rightarrow^+ A$，称文法含环。环是左递归和右递归的退化形式，它使文法具有无穷多义性：同一句子有无穷多棵分析树。实际文法中应通过消除单产生式和 ε 产生式来避免环。

---

## 2. 递归的检测

### 2.1 依赖图

构造有向图 $G_{dep} = (N, E_{dep})$：若存在产生式 $A \to \alpha B \beta$，则添加边 $A \to B$。

- $A$ 是递归的 ⇔ $A$ 位于 $G_{dep}$ 的某个环上；
- $A$ 是直接递归的 ⇔ $G_{dep}$ 中存在自环 $A \to A$；
- 同一强连通分量（SCC）中的非终结符相互递归。若 SCC 中含有不少于两个节点，则其中每个节点都是间接递归的。

### 2.2 左角图

为检测左递归，构造**左角图**（left-corner graph）$G_{lc}$：若存在产生式 $A \to \alpha B \beta$ 且 $\alpha \Rightarrow^* \varepsilon$，则添加边 $A \to B$。

$A$ 是左递归的，当且仅当 $A$ 位于 $G_{lc}$ 的环上。这个定义自然覆盖了隐藏左递归。

### 2.3 算法

```python
def nullable_set(grammar):
    nullable = set()
    changed = True
    while changed:
        changed = False
        for A, rhs in grammar.productions:
            if A not in nullable and all(X in nullable for X in rhs):
                nullable.add(A)
                changed = True
    return nullable

def left_corner_graph(grammar):
    nullable = nullable_set(grammar)
    edges = {A: set() for A in grammar.nonterminals}
    for A, rhs in grammar.productions:
        for X in rhs:
            if X in grammar.nonterminals:
                edges[A].add(X)
            if X not in nullable:     # 终结符或不可空符号，停止
                break
    return edges

def left_recursive_nonterminals(grammar):
    g = left_corner_graph(grammar)
    result = set()
    for scc in tarjan_scc(g):
        if len(scc) > 1 or any(A in g[A] for A in scc):
            result |= scc
    return result
```

可空集合的计算是标准不动点迭代，Tarjan 算法求 SCC 的时间复杂度为 $O(|N| + |E|)$。整体复杂度与文法规模 $|G|$ 近似线性。

---

## 3. 左递归的消除

左递归是自顶向下分析（LL、递归下降）的主要障碍，因此需要系统化的消除方法。

### 3.1 直接左递归的消除

对产生式组

$$A \to A\alpha_1 \mid \cdots \mid A\alpha_m \mid \beta_1 \mid \cdots \mid \beta_n$$

其中 $\beta_i$ 不以 $A$ 开头，引入新非终结符 $A'$，改写为：

$$
\begin{aligned}
A &\to \beta_1 A' \mid \cdots \mid \beta_n A' \\
A' &\to \alpha_1 A' \mid \cdots \mid \alpha_m A' \mid \varepsilon
\end{aligned}
$$

本质上，$A$ 生成的语言是 $(\beta_1|\cdots|\beta_n)(\alpha_1|\cdots|\alpha_m)^*$，改写把左递归转换成了等价的右递归。

ETF 文法改写结果：

```
E  → T E'
E' → + T E' | ε
T  → F T'
T' → * F T' | ε
F  → ( E ) | id
```

### 3.2 间接左递归的消除

直接左递归的消除方法只作用于单个非终结符的产生式，无法处理跨非终结符的间接左递归。标准方法是**代入法**（Paull 算法，即龙书第 2 版算法 4.19）。

**前提**：文法无环、无 ε 产生式。

**算法**：

```
将非终结符排序为 A1, A2, ..., An
for i = 1 to n:
    for j = 1 to i-1:
        将每个形如 Ai → Aj γ 的产生式替换为
            Ai → δ1 γ | δ2 γ | ... | δk γ
        其中 Aj → δ1 | δ2 | ... | δk 是 Aj 当前的全部产生式
    消除 Ai 的直接左递归
```

**不变式**：第 $i$ 轮结束后，对所有 $k \le i$，$A_k$ 的任意产生式 $A_k \to A_l\gamma$ 都满足 $l > k$。因此左角图中只存在从低序号指向高序号的边，不可能形成环。

**例**（龙书例 4.20）：

```
S → A a | b
A → A c | S d | ε
```

其中 $S \Rightarrow Aa \Rightarrow Sda$，构成间接左递归。

1. 排序 $A_1 = S, A_2 = A$。
2. $i = 1$：S 无直接左递归，不变。
3. $i = 2$：将 $A \to Sd$ 代入 S 的产生式，得 $A \to Aad \mid bd$。此时
   $$A \to Ac \mid Aad \mid bd \mid \varepsilon$$
4. 消除 A 的直接左递归：

```
S  → A a | b
A  → b d A' | A'
A' → c A' | a d A' | ε
```

此例含 ε 产生式 $A \to \varepsilon$，严格来说不满足前提，但由于该 ε 产生式不会引出新的左递归路径，算法仍然得到正确结果。一般情况下应先消除 ε 产生式。

### 3.3 算法的局限与改进

- **规模膨胀**：代入可能导致产生式数量指数级增长，且结果依赖于非终结符的排序。
- **改进算法**：Moore（2000）在实验中比较了多种方法，指出先做左因子提取再代入、只对真正参与左递归的非终结符代入，以及基于**左角变换**（left-corner transform）的方法，能显著减小输出规模。
- **Greibach 范式**：任何不含 ε 的 CFL 都有 Greibach 范式文法（每条产生式形如 $A \to a\alpha$），它完全不含左递归。不过这种方法主要具有理论意义，转换后文法可读性差。

### 3.4 语义层面的代价

消除左递归保持了**语言**等价，但改变了**分析树结构**。对于 `a - b - c`：

- 原文法 $E \to E - T$ 产生左结合的树：$(a - b) - c$；
- 改写后 $E' \to - T E'$ 自然产生右倾的树：$a - (b - c)$。

工程上有两种常见补救方法：

1. **继承属性**：在 L 属性 SDD 中，通过 $E'$ 的继承属性向下传递左操作数，在 $\varepsilon$ 处返回结果（龙书 5.4 节）；
2. **EBNF 迭代**：将 $E \to T\,\{(+|-)\,T\}$ 实现为循环，在循环中按左结合方式累积结果：

```python
def parse_E():
    left = parse_T()
    while peek() in ('+', '-'):
        op = advance()
        right = parse_T()
        left = BinOp(op, left, right)   # 保持左结合
    return left
```

---

## 4. 各类递归对分析技术的影响

### 4.1 递归下降与 LL(k)

**左递归**（无论直接还是间接）会导致无限递归。例如对间接左递归 $S \to Aa,\ A \to Sd$，函数 `S()` 调用 `A()`，`A()` 又调用 `S()`，期间不消耗任何输入。从 LL 分析表的角度看，左递归必然导致 FIRST 集冲突，因此**左递归文法不可能是 LL(k) 文法**。

**右递归与自嵌套递归**是安全的。设 $A \Rightarrow^+ \alpha A \beta$，且 $\alpha$ 推导出非空终结符串。分析器每经过一次递归环路，至少消耗一个输入记号。由于输入有限，递归深度以输入长度为上界，算法必然终止。

以 ETF 文法中 $F \to (E)$ 为例，`F()` 先匹配 `(`，再调用 `E()`：

```python
def parse_F():
    if peek() == '(':
        expect('(')
        node = parse_E()      # 间接递归，但已消耗 '('
        expect(')')
        return node
    return Id(expect('id'))
```

**实现层面**：间接递归在递归下降中体现为相互调用的函数，它们共享同一个调用栈。对于极深的嵌套输入（如上万层括号），可能导致栈溢出。生产级实现通常会设置深度限制，或改用显式栈。

### 4.2 LR 分析

LR 分析器是自底向上的，左递归不会引起非终止，**LR 分析反而偏好左递归**：

- 左递归 $L \to L\ x \mid x$：每读入一个 $x$ 即可归约，分析栈深度为 $O(1)$；
- 右递归 $L \to x\ L \mid x$：必须将全部 $x$ 移入栈中，直到末尾才开始连续归约，栈深度为 $O(n)$。

Yacc/Bison 文档也因此建议列表结构使用左递归。间接递归对 LR 分析没有特殊影响，LR(0) 项集闭包会自然展开相互递归的非终结符。

### 4.3 PEG 与 Packrat 分析

PEG 采用有序选择和回溯，语义上类似递归下降，因此左递归同样会导致非终止。Warth、Douglass 与 Millstein（2008）提出了"种子增长"（seed growing）技术，使 Packrat 分析器支持直接左递归，并进一步扩展到间接左递归。间接情形需要追踪左递归调用链上所有涉及的规则（"involved set"），实现复杂度明显高于直接情形。后续研究（如 Medeiros 等人 2014 年基于有界左递归的语义）给出了更清晰的形式化。

### 4.4 广义分析算法

Earley、GLR、GLL 等广义算法可以处理任意 CFG，包括直接和间接左递归。其中 GLL（Scott & Johnstone, 2010）保留了递归下降的结构，同时借助图结构栈（GSS）原生支持左递归。

### 4.5 运算符优先级分析

Pratt 分析与优先级爬升（precedence climbing）绕开了 ETF 风格的分层文法。它们用一个参数化的递归函数处理所有二元运算符，用循环实现左结合，用递归实现右结合。这类方法本质上是对"左递归 + 优先级"的直接编码。

---

## 5. 形式语言视角：自嵌套递归与表达能力

### 5.1 右线性文法与正则语言

若文法的每条产生式都形如 $A \to wB$ 或 $A \to w$（$w \in \Sigma^*$），则称其为右线性文法，它生成的语言恰好是正则语言。右线性文法中只存在右递归，而且递归可以是直接的，也可以是间接的（对应有限自动机中的环）。左线性文法同理。

### 5.2 Chomsky 的自嵌套定理

**定理**（Chomsky, 1959）：若上下文无关文法 $G$ 不含自嵌套非终结符，则 $L(G)$ 是正则语言。

其逆否命题是：**一个非正则的上下文无关语言，其每一个文法都必然含有自嵌套递归。**

这说明在 CFG 的各类递归中：

- 纯左递归和纯右递归（无论直接还是间接）在表达能力上都没有超出正则语言；
- **自嵌套递归**才是 CFG 超越正则语言的根本来源。

ETF 文法中的 $F \Rightarrow^+ (F)$ 正是自嵌套递归。它使语言能够描述任意深度的括号匹配，类似 Dyck 语言的结构，而这是有限自动机无法识别的。注意它是**间接**的：自嵌套并不要求在单条产生式中出现。

### 5.3 间接递归的可消除性

间接递归总可以通过代入转化为直接递归，前提是对相关非终结符做展开：

```
F → ( E ) | id ,  E → T ,  T → F
⟹  F → ( F ) | id        （仅在 E、T 为单产生式时成立）
```

一般情形下，代入可能使产生式数量膨胀。但这说明"直接"与"间接"是**文法表示层面**的区别，而不是语言层面的区别。相反，"是否存在自嵌套"则关系到语言本身的性质，见 5.2 节。

---

## 6. 总结

| 维度 | 直接递归 | 间接递归 |
|---|---|---|
| 识别 | 单条产生式即可判断 | 需依赖图或左角图的环检测 |
| 左递归消除 | 局部改写（引入 $A'$） | 需排序 + 代入，再消除直接左递归 |
| 对 LL / 递归下降 | 左递归致非终止 | 左递归同样致非终止，且更隐蔽 |
| 对 LR | 偏好左递归 | 无特殊影响 |
| 对 PEG | 种子增长可解决 | 需追踪 involved set，更复杂 |
| 语言能力 | 与间接递归无本质区别 | 可经代入化为直接递归 |

核心结论如下：

1. **"直接/间接"描述的是递归的路径**，属于文法表示层面的性质，可以通过代入相互转化。
2. **"左/右/自嵌套"描述的是递归的位置**，它决定了分析器的行为与语言的表达能力。
3. 对自顶向下分析而言，真正有害的是**左递归**，包括直接、间接和隐藏左递归。右递归与自嵌套递归在每轮递归中都消耗输入，因此是安全的。
4. **自嵌套递归**是 CFG 超越正则语言的根本原因，不能也不应被消除。

---

## 参考文献

1. Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. *Compilers: Principles, Techniques, and Tools* (2nd ed.). Addison-Wesley, 2006. §2.4.5, §4.3.3.
2. Hopcroft, J. E., Motwani, R., & Ullman, J. D. *Introduction to Automata Theory, Languages, and Computation* (3rd ed.). Pearson, 2006. Ch. 5, 7.
3. Chomsky, N. "On Certain Formal Properties of Grammars." *Information and Control*, 2(2), 137–167, 1959.
4. Moore, R. C. "Removing Left Recursion from Context-Free Grammars." *Proc. NAACL*, 2000.
5. Warth, A., Douglass, J. R., & Millstein, T. "Packrat Parsers Can Support Left Recursion." *Proc. PEPM*, 2008.
6. Medeiros, S., Mascarenhas, F., & Ierusalimschy, R. "Left Recursion in Parsing Expression Grammars." *Science of Computer Programming*, 96, 2014.
7. Scott, E., & Johnstone, A. "GLL Parsing." *Electronic Notes in Theoretical Computer Science*, 253(7), 2010.
8. Grune, D., & Jacobs, C. J. H. *Parsing Techniques: A Practical Guide* (2nd ed.). Springer, 2008.