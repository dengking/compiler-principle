# 9.2 Introduction to Data-Flow Analysis

All the optimizations introduced in Section 9.1 depend on **data-flow analysis**. "Data-ow analysis" refers to a body of techniques that derive(获取) information about the flow of data along program execution paths. For example, one way to implement **global common subexpression elimination** requires us to determine whether two textually identical expressions evaluate to the same value along any possible execution path of the program. As another example, if the result of an assignment is not used along any subsequent execution path, then we can eliminate the assignment as **dead code**. These and many other important questions can be answered by **data-ow analysis**.

> 翻译: 9.1 节介绍的全部优化手段都依赖**数据流分析**。**数据流分析**是一类技术的统称，这类技术用于推导数据沿着程序执行路径流动的相关信息。例如，实现**全局公共子表达式消除**的一种方案，需要我们判断：两个文本形式完全相同的表达式，在程序**所有可能的执行路径**上是否都算出同一个值。再举一例：如果一条赋值语句的结果，在后续任意一条执行路径中都不会被使用，那么我们就可以把这条赋值语句当作**死代码**删除。上述问题以及众多其他关键问题，都可以依靠**数据流分析**求解。

## 9.2.1 The Data-Flow Abstraction

Following Section 1.6.2, the execution of a program can be viewed as a series of transformations of the **program state**, which consists of the **values of all the variables** in the program, including those associated with **stack frames** below the top of the run-time stack. Each execution of an **intermediate-code statement** transforms an **input state** to a **new output state**. The **input state** is associated with the **program point** before the statement and the **output state** is associated with the **program point** after the statement.

> 翻译: 回顾 1.6.2 节，程序的执行可以看作**程序状态**的一系列变换。程序状态由程序中所有变量的值构成，包括运行时栈栈顶之下各栈帧关联的变量。每执行一条中间代码语句，都会将一个输入状态变换为新的输出状态。输入状态对应**语句之前的程序点**，输出状态对应**语句之后的程序点**。

When we analyze the behavior of a program, we must consider all the possible sequences of **program points** ("**paths**") through a **flow graph** that the program execution can take. We then extract, from the possible **program states** at each point, the information we need for the particular **data-flow analysis** problem we want to solve. In more complex analyses, we must consider **paths** that jump among the **flow graphs** for various procedures, as calls and returns are executed. However, to begin our study, we shall concentrate on the **paths** through a single **flow graph** for a single procedure.

> 翻译: 分析程序行为时，我们必须考虑程序执行在流图上所有可能的程序点序列（称为**路径**）。随后，从每个程序点的全部可能程序状态中，提取我们要解决的特定数据流分析问题所需信息。在更复杂的分析中，随着函数调用与返回的执行，我们还要考虑在多个过程的流图之间跳转的路径。但作为入门学习，我们只聚焦**单个过程的单一流图**内的路径。

Let us see what the **flow graph** tells us about the possible execution paths.

- Within one basic block, the program point after a statement is the same as the program point before the next statement.
- If there is an edge from block $B_1$ to block $B_2$, then the program point after the last statement of $B_1$ may be followed immediately by the program point before the first statement of $B_2$.

Thus, we may define an *execution path* (or just *path*) from point $p_1$ to point $p_n$ to be a sequence of points $p_1,p_2,\dots,p_n$ such that for each $i = 1,2,\dots,n-1$, either

1. $p_i$ is the point immediately preceding a statement and $p_{i+1}$ is the point immediately following that same statement, or
2. $p_i$ is the end of some block and $p_{i+1}$ is the beginning of a successor block.

In general, there is an infinite number of possible execution paths through a program, and there is no finite upper bound on the length of an execution path. Program analyses summarize all the possible program states that can occur at a point in the program with a finite set of facts. Different analyses may choose to abstract out different information, and in general, no analysis is necessarily a perfect representation of the state.

> 翻译: 一般来说，一个程序拥有无穷多条可能的执行路径，并且执行路径的长度不存在有限上界。程序分析会用**有限的一组事实**，来概括在程序某一点上所有可能出现的程序状态。不同的分析可以选择提取不同的信息；总体而言，不存在一种分析能够完美地表示程序状态。

## Example 9.8

**Example 9.8**: Even the simple program in Fig. 9.12 describes an unbounded number of execution paths. Not entering the loop at all, the shortest complete execution path consists of the program points $ (1,2,3,4,9) $. The next shortest path executes one iteration of the loop and consists of the points $(1,2,3,4,5,6,7,8,3,4,9)$. We know that, for example, the first time program point $(5)$ is executed, the value of $a$ is $1$ due to definition $d_1$. We say that $d_1$ *reaches* point $(5)$ in the first iteration. In subsequent iterations, $d_3$ reaches point $(5)$ and the value of $a$ is $243$.

> 翻译: **例9.8**：即使是图9.12中的这个简单程序，也存在**无穷多条执行路径**。完全不进入循环时，最短的完整执行路径由程序点 $(1,2,3,4,9)$ 构成。次短的路径会执行一次循环迭代，对应的程序点序列为 $(1,2,3,4,5,6,7,8,3,4,9)$。例如我们知道，**第一次执行程序点(5)**时，由于定值 $d_1$，变量 $a$ 的值为1。我们称：在第一次迭代中，$d_1$ **到达**程序点(5)。在后续迭代里，定值 $d_3$ 到达程序点(5)，此时 $a$ 的值是243。