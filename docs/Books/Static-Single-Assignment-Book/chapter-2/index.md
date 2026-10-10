# CHAPTER 2 Properties and Flavors

Recall from the previous chapter that a procedure is in SSA form if every variable is defined only once, and every use of a variable refers to exactly one definition. Many variations, or flavors, of SSA form that satisfy these criteria can be defined, each offering its own considerations. For example, different flavors vary in terms of the number of $\phi$-functions, which affects the size of the **intermediate representation**; some variations are more difficult to construct, maintain, and destruct compared to others. This chapter explores these SSA flavors and provides insight regarding their relative merits(相对优缺点) in certain contexts.

---

## 2.1 Def-use and use-def chains

Under SSA form, each variable is defined once. **Def-use chains**<sup>*</sup> are data structures that provide, for the single definition of a variable, the set of all its uses. In turn, a **use-def chain**<sup>*</sup>, which under SSA consists of a single name, uniquely specifies the definition that reaches the use. As we will illustrate further in the book **def-use chains** are useful for **forward data-flow analysis** as they provide direct connections that shorten the **propagation distance** between nodes that generate and use data-flow information.

> NOTE: 一般需要先定义后使用

Because of its single definition per variable property, SSA form simplifies **def-use** and **use-def chains** in several ways. First, SSA form simplifies **def-use chains** as it combines the information as early as possible. This is illustrated by Figure 2.1 where the **def-use chain** in the non-SSA program requires as many merges as there are uses of $x$, whereas the corresponding SSA form allows early and more efficient combination.

Second, as it is easy to associate each variable with its single defining operation, **use-def chains** can be represented and maintained almost for free. As this constitutes the skeleton of the so-called **SSA graph** (see Chapter 12), when considering a program under SSA form, use-def chains are implicitly considered as a given. The explicit representation of **use-def chains** simplifies **backward propagation**, which favors algorithms such as **dead-code elimination**.

> 翻译: 其次，由于可以轻松将每个变量关联到其唯一的定义操作，**使用 - 定义链（use-def chains）**几乎可以零开销地完成表示与维护。这构成了所谓**SSA 图**的骨架（参见第 12 章）；当程序采用 SSA 形式时，使用 - 定义链是默认隐含存在的。**使用 - 定义链**的显式表示简化了**反向传播**，这对于**死代码消除**这类算法十分有利。

For forward propagation, since **def-use chains** are precisely the reverse of **use-def chains**, computing them is also easy; maintaining them requires minimal effort. However, even without **def-use chains**, some lightweight **forward propagation** algorithms such as copy folding<sup>*</sup> are possible: using a single pass that processes operations along a topological order traversal of a **forward CFG**,<sup>1</sup> most definitions are processed prior to their uses. When processing an operation, the use-def chain provides immediate access to the prior computed value of an argument. Conservative merging is performed when, at some loop headers, a $\phi$-function encounters an unprocessed argument. Such a lightweight propagation engine proves to be fairly efficient.

> NOTE:
> 
> use-def chain: backward propagation 
> 
> def-use chain: forward propagation

---

¹ A forward control-flow graph is an acyclic reduction of the CFG obtained by removing back-edges.

---

## 2.2 Minimality(极小性)

SSA construction is a two-phase process: placement of $\phi$-functions, followed by renaming. The goal of the first phase is to generate code that fulfills the **single reaching-definition property**, as already outlined. **Minimality** is an additional property relating to code that has $\phi$-functions inserted, but prior to renaming; Chapter 3 describes the classical **SSA construction algorithm** in detail, while this section focuses primarily on describing the **minimality property**.

> 翻译: 静态单赋值（SSA）构造分为两个阶段：$\phi$函数插入，随后进行重命名。第一阶段的目标是生成满足**单一定义到达**性质的代码，前文已经简述过该性质。**极小性**是针对已经插入$\phi$函数、但尚未执行重命名的代码的另一项性质；第3章会详细介绍经典SSA构造算法，本节重点阐述极小性这一性质。

A definition $D$ of variable $v$ reaches a point $p$ in the CFG if there exists a path from $D$ to $p$ that does not pass through another definition of $v$. We say that a code has the **single reaching-definition property** iff no **program point** can be reached by two definitions of the same variable. Under the assumption that the **single reaching-definition property** is fulfilled, the **minimality property** states the minimality of the number of inserted $\phi$-functions.

> 翻译: 变量$v$的定义$D$能够到达控制流图（CFG）上的某点$p$，当且仅当存在一条从$D$到$p$的路径，且该路径不会经过变量$v$的其他定义。若任意程序位置都不会同时被同一个变量的两处定义到达，则称该代码满足**单一定义到达**性质。在满足单一定义到达性质的前提下，极小性描述的是：**所插入$\phi$函数的数量达到最小**。

This property can be characterized using the following notion of **join sets**. Let $n_1$ and $n_2$ be distinct **basic blocks** in a CFG. A basic block $n_3$, which may or may not be distinct from $n_1$ or $n_2$, is a **join node** of $n_1$ and $n_2$ if there exist at least two non-empty paths, i.e., paths containing at least one CFG edge, from $n_1$ to $n_3$ and from $n_2$ to $n_3$, respectively, such that $n_3$ is the only **basic block** that occurs on both of the paths. In other words, the two paths **converge**(汇合) at $n_3$ and no other CFG node. Given a set $S$ of basic blocks, $n_3$ is a **join node** of $S$ if it is the join node of at least two **basic blocks** in $S$. The set of **join nodes** of set $S$ is denoted $\mathscr{J}(S)$.

> 翻译: 该性质可以借助**汇合集（join sets）**这一概念来描述。设$n_1$、$n_2$是控制流图中两个不同的基本块。基本块$n_3$（可以与$n_1$或$n_2$相同）称为$n_1$与$n_2$的**汇合节点**，当且仅当至少存在两条非空路径（路径至少包含一条CFG边）：一条从$n_1$到$n_3$，一条从$n_2$到$n_3$；并且$n_3$是同时出现在两条路径上的唯一基本块。换句话说，两条路径仅在$n_3$处汇合，不在其他CFG节点交汇。给定基本块集合$S$，若$n_3$是$S$中至少两个基本块的汇合节点，则$n_3$是集合$S$的汇合节点。集合$S$的全部**汇合节点**构成的集合记作$\mathscr{J}(S)$。

Intuitively, a **join set** corresponds to the placement of $\phi$-functions. In other words, if $n_1$ and $n_2$ are **basic blocks** that both contain a definition of variable $v$, then we ought to instantiate $\phi$-functions for $v$ at every **basic block** in $\mathscr{J}(\{n_1,n_2\})$. Generalizing this statement, if $D_v$ is the set of **basic blocks** containing definitions of $v$, then $\phi$-functions should be instantiated in every **basic block** in $\mathscr{J}(D_v)$. As inserted $\phi$-functions are themselves **definition points**, some new $\phi$-functions should be inserted at $\mathscr{J}(D_v \cup \mathscr{J}(D_v))$. Actually it turns out that $\mathscr{J}(S\cup \mathscr{J}(S))=\mathscr{J}(S)$, so the **join set** of the set of **definition points** of a variable in the original program characterizes exactly the minimum set of program points where $\phi$-functions should be inserted.

> 翻译: 直观上，汇合集对应$\phi$函数的插入位置。也就是说：如果基本块$n_1$和$n_2$都包含变量$v$的定义，那么我们应当在$\mathscr{J}(\{n_1,n_2\})$内的每一个基本块中，为变量$v$创建$\phi$函数。推广这个结论：若$D_v$是包含变量$v$定义的所有基本块构成的集合，则应当在$\mathscr{J}(D_v)$内的每个基本块插入$v$的$\phi$函数。由于插入的$\phi$函数本身也属于定义点，看上去还需要在$\mathscr{J}(D_v \cup \mathscr{J}(D_v))$中新增一部分$\phi$函数。但实际上可以证明$\mathscr{J}(S\cup \mathscr{J}(S))=\mathscr{J}(S)$，因此，原程序中变量所有定义点构成集合的汇合集，恰好刻画了**需要插入$\phi$函数的最少程序位置**。

We are not aware of any optimizations that require a strict enforcement of **minimality property**. However, placing $\phi$-functions only at the **join sets** can be done easily using a simple **topological traversal** of the CFG as described in Chapter 4, Section 4.4. Classical techniques place $\phi$-functions of a variable $v$ at $\mathscr{J}(D_v \cup \{r\})$, with $r$ the entry node of the CFG. There are good reasons for that as we will explain further. Finally, as explained in Chapter 3, Section 3.3 for reducible flow graphs, some copy-propagation engines can easily turn a non-minimal SSA code into a minimal one.

> 翻译: 目前尚没有任何优化算法要求必须严格满足极小性。不过，仅在汇合集位置插入$\phi$函数，可以通过对CFG做简单的拓扑序遍历轻松实现，详见第4章4.4节。经典算法会在$\mathscr{J}(D_v \cup \{r\})$处放置变量$v$的$\phi$函数，其中$r$是控制流图的入口节点，后续会解释这么做的原因。最后，正如第3章3.3节针对可归约流图所介绍的：部分拷贝传播引擎可以很方便地把**非极小SSA代码**转换为极小SSA代码。
