# CHAPTER 1 Introduction

This book is about the static single assignment form (SSA), which is a naming convention for storage **locations (variables)** in low-level representations of computer programs.

> NOTE: locations = variables

The term ***static*** indicates that SSA relates to properties and analysis of program text (code). 

The term ***single*** refers to the uniqueness property of **variable names** that SSA imposes. As illustrated above, this enables a greater degree of precision. 

> NOTE: 优势

The term ***assignment*** means variable definitions.

> NOTE: assignment = definition

$$
x = y + 1;
$$

the variable $x$ is being assigned the value of expression $(y + 1)$. This is a **definition**, or **assignment statement**, for $x$. A compiler engineer would interpret the above assignment statement to mean that the lvalue of $x$ (i.e., the memory location labeled as $x$) should be modified to store the value $(y + 1)$.

## 1.1 Definition of SSA

The simplest, least constrained, definition of SSA can be given using the following informal prose:

> “A program is defined to be in SSA form if each variable is a target of exactly one assignment statement in the program text.”

However there are various, more specialized, varieties of SSA, which impose further **constraints** on programs. Such constraints may relate to graph-theoretic properties of variable definitions and uses, or the encapsulation of specific **control-flow** or **data-flow** information. Each distinct SSA variety has specific characteristics. Basic varieties of SSA are discussed in Chapter 2. Part III of this book presents more complex extensions.

> 翻译: 当然还存在多种更专门化的SSA变体，它们会对程序施加更多约束。这类约束可能和变量定义与使用的图论性质相关，或是用于封装特定的控制流、数据流信息。每种不同的SSA变体都具备独有的特征。本书第2章讨论基础的SSA变体；第三部分介绍更复杂的扩展形式。

One important property that holds for all varieties of SSA, including the simplest definition above, is ***referential transparency***: i.e., since there is only a single definition for each variable in the program text, a variable's value is independent of its position in the program. We may refine our knowledge about a particular variable based on branching conditions, e.g. we know the value of $x$ in the conditionally executed block following an `if` statement that begins with

$$
\text{if } (x == 0)
$$

however the underlying value of $x$ does not change at this `if` statement. 



Programs written in pure functional languages are referentially transparent. Such referentially transparent programs are more amenable to formal methods and mathematical reasoning, since the meaning of an expression depends only on the meaning of its subexpressions and not on the order of evaluation or side effects of other expressions. For a referentially opaque program, consider the following code fragment.

```c
x = 1;
y = x + 1;
x = 2;
z = x + 1;
```

A naive (and incorrect) analysis may assume that the values of $y$ and $z$ are equal, since they have identical definitions of $(x + 1)$. However the value of variable $x$ depends on whether the current code position is before or after the second definition of $x$, i.e., variable values depend on their context. When a compiler transforms this program fragment to SSA code, it becomes **referentially transparent**. The translation process involves renaming to eliminate multiple assignment statements for the same variable. Now it is apparent that $y$ and $z$ are equal if and only if $x_1$ and $x_2$ are equal.

> NOTE: 普通命令式代码里，同一个名字`x`可以多次赋值，`x`的值取决于读到它的**位置**（上下文），引用不透明。
> SSA会把多次赋值重命名为`x₁, x₂, x₃`，每个名字只定义一次。
> 一旦进入SSA形式，`x₁`的值固定不变，**不管在哪一行读取`x₁`，取值永远一样**，这就是这里所说的引用透明。
> 这里的引用透明，**是针对SSA名字（$x_1,x_2$这类SSA变量）**，不是指整个程序消除内存副作用。SSA依然可以有store内存操作，只是SSA虚拟变量本身只读。
