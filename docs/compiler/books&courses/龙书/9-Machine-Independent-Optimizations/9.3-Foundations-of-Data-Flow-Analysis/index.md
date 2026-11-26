# 9.3 Foundations of Data-Flow Analysis

Having shown several useful examples of the data-flow abstraction, we now study the family of data-flow schemas as a whole, abstractly. We shall answer several basic questions about data-flow algorithms formally:

1. Under what circumstances is the iterative algorithm used in data-flow analysis correct?
2. How precise is the solution obtained by the iterative algorithm?
3. Will the iterative algorithm converge?
4. What is the meaning of the solution to the equations?

> 在展示了若干数据流抽象的实用示例之后，我们现在从抽象层面整体研究一类数据流模式。我们将以形式化方式回答关于数据流算法的几个基础问题：
> 
> 1. 在何种条件下，数据流分析所用的迭代算法是正确的？
> 2. 迭代算法求得的解精度如何？
> 3. 迭代算法是否会收敛？
> 4. 方程组的解具有什么含义？

In Section 9.2, we addressed each of the questions above informally when describing the reaching-definitions problem. Instead of answering the same questions for each subsequent problem from scratch, we relied on analogies with the problems we had already discussed to explain the new problems. Here we present a general approach that answers all these questions, once and for all, rigorously, and for a large family of data-flow problems. We first identify the properties desired of data-flow schemas and prove the implications of these properties on the correctness, precision, and convergence of the data-flow algorithm, as well as the meaning of the solution. Thus, to understand old algorithms or formulate new ones, we simply show that the proposed data-flow problem definitions have certain properties, and the answers to all the above difficult questions are available immediately.

> 在9.2节介绍到达-定值问题时，我们已经非形式化地讨论了上述全部问题。对于后续每一个问题，我们不再从头重复回答相同问题，而是借助已讨论过问题的类比来解释新问题。本节给出一套通用方法，可以一劳永逸、严格地对一大类数据流问题回答全部这些问题。我们首先确定数据流模式需要具备的性质，并证明这些性质对数据流算法的正确性、精度、收敛性以及解的含义带来的推论。因此，想要理解已有算法或者构造新算法，我们只需证明待研究的数据流问题定义满足某些性质，上面所有这些难题的答案就可以直接得到。

The concept of having a common theoretical framework for a class of schemas also has practical implications. The framework helps us identify the reusable components of the algorithm in our software design. Not only is coding effort reduced, but programming errors are reduced by not having to recode similar details several times.

> 为一类分析模式建立统一理论框架，这个思想同样具备工程价值。该框架帮助我们在软件设计中识别算法里可复用的组件。不仅减少编码工作量，同时避免多次重复编写相似细节，从而降低代码出错概率。

A data-flow analysis framework $(D, V, \land, F)$ consists of

1. A direction of the data flow $D$, which is either FORWARDS or BACKWARDS.
2. A semilattice (see Section 9.3.1 for the definition), which includes a domain of values $V$ and a meet operator $\land$.
3. A family $F$ of transfer functions from $V$ to $V$. This family must include functions suitable for the boundary conditions, which are constant transfer functions for the special nodes ENTRY and EXIT in any flow graph.

> 一个数据流分析框架 $(D, V, \land, F)$ 由以下部分组成：
> 
> 1. 数据流方向 $D$：前向（FORWARDS）或者后向（BACKWARDS）。
> 2. 半格（定义见9.3.1节）：包含值域 $V$ 和交算子 $\land$。
> 3. 从 $V$ 映射到 $V$ 的传递函数族 $F$。该函数族必须包含满足边界条件的函数，也就是控制流图中特殊节点ENTRY（入口）、EXIT（出口）对应的常数传递函数。

## 9.3.1 Semilattices

A semilattice is a set $V$ and a binary meet operator $\land$ such that for all $x$, $y$, and $z$ in $V$:







半格由集合 $V$ 和二元交算子 $\land$ 构成，满足：对 $V$ 中任意 $x,y,z$：
