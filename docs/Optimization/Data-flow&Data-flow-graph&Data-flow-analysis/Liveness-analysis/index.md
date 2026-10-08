# Live-variable analysis

## wikipedia [Live-variable analysis](https://en.wikipedia.org/wiki/Live-variable_analysis)

In [compilers](https://en.wikipedia.org/wiki/Compilers "Compilers"), **live variable analysis** (or simply **liveness analysis**) is a classic [data-flow analysis](https://en.wikipedia.org/wiki/Data-flow_analysis "Data-flow analysis") to calculate the [variables](https://en.wikipedia.org/wiki/Variable_\(programming\) "Variable (programming)") that are *live* at each point in the program. A variable is *live* at some point if it holds a value that may be needed in the future, or equivalently if its value may be read before the next time the variable is written to.

> 翻译: 如果一个变量在某程序点上保存的值未来可能会被使用，或者等价地说，在该变量下一次被写入之前，它的值有可能被读取，那么称这个变量在该点是**活跃（live）**的。

### Example

Consider the following program:

```c
b = 3
c = 5
a = f(b * c)
```

The set of live variables between lines 2 and 3 is {`b`, `c`} because both are used in the multiplication on line 3. But the set of live variables after line 1 is only {`b`}, since variable `c` is updated later, on line 2. The value of variable `a` is not used in this code.

Note that the assignment to `a` may be eliminated as `a` is not used later, but there is insufficient information to justify removing all of line 3 as `f` may have [side effects](https://en.wikipedia.org/wiki/Side_effect_\(computer_science\) "Side effect (computer science)") (printing `b * c`, perhaps).

### Expression in terms of dataflow equations

**Liveness analysis** is a "backwards may" analysis. The analysis is done in a [backwards](https://en.wikipedia.org/wiki/Data-flow_analysis#Backward_Analysis "Data-flow analysis") order, and the dataflow [confluence operator](https://en.wikipedia.org/wiki/Confluence_operator?action=edit&redlink=1 "Confluence operator (page does not exist)") is [set union](https://en.wikipedia.org/wiki/Set_union "Set union"). In other words, if applying **liveness analysis** to a function with a particular number of logical branches within it, the analysis is performed starting from the end of the function working towards the beginning (hence "backwards"), and a variable is considered live if any of the branches moving forward within the function might potentially (hence "may") need the variable's current value. This is in contrast to a "backwards must" analysis which would instead enforce this condition on all branches moving forward.

> 翻译: 活跃性分析是一种 "反向 may（可能）" 分析。该分析按[反向](https://en.wikipedia.org/wiki/Data-flow_analysis#Backward_Analysis)顺序进行，其数据流[汇合算子](https://en.wikipedia.org/wiki/Confluence_operator?action=edit&redlink=1)为[集合并集](https://en.wikipedia.org/wiki/Set_union)。换言之，若对一个内部包含若干逻辑分支的函数应用**活跃性分析**，则分析从函数末尾开始、向函数开头方向推进（故称 "反向"）；而一个变量被视为活跃的条件是：在函数内向前推进的**任意**分支都有可能（故称 "may / 可能"）用到该变量的当前值。这与 "反向 must（必须）" 分析形成对比 —— 后者要求该条件在向前推进的**所有**分支上都成立。

The **dataflow equations** used for a given basic block $s$ and exiting block $final$ in **live variable analysis** are the following:

$\text{GEN}[s]$: The set of variables that are used in $s$ before any assignment in the same basic block.

$\text{KILL}[s]$: The set of variables that are assigned a value in $s$ (in many books that discuss compiler design, $\text{KILL}(s)$ is also defined as the set of variables assigned a value in $s$ before any use, but this does not change the solution of the dataflow equation):

$$
\begin{align*}
\text{LIVE}_\text{in}[s] &= \text{GEN}[s] \cup (\text{LIVE}_\text{out}[s] - \text{KILL}[s]) \\
\text{LIVE}_\text{out}[final] &= \emptyset \\
\text{LIVE}_\text{out}[s] &= \bigcup_{p\in\text{succ}[s]} \text{LIVE}_\text{in}[p] \\
\text{GEN}[d:y \leftarrow f(x_1,\cdots,x_n)] &= \{x_1,\dots,x_n\} \\
\text{KILL}[d:y \leftarrow f(x_1,\cdots,x_n)] &= \{y\}
\end{align*}
$$

The in–state of a block is the set of variables that are live at the start of the block. Its out–state is the set of variables that are live at the end of it. The out–state is the union of the in–states of the block's successors. The transfer function of a statement is applied by making the variables that are written dead, then making the variables that are read live.


