# CHAPTER 2 Properties and Flavors

Recall from the previous chapter that a procedure is in SSA form if every variable is defined only once, and every use of a variable refers to exactly one definition. Many variations, or flavors, of SSA form that satisfy these criteria can be defined, each offering its own considerations. For example, different flavors vary in terms of the number of $\phi$-functions, which affects the size of the **intermediate representation**; some variations are more difficult to construct, maintain, and destruct compared to others. This chapter explores these SSA flavors and provides insight regarding their relative merits(相对优缺点) in certain contexts.

---

## 2.1 Def-use and use-def chains

Under SSA form, each variable is defined once. **Def-use chains**<sup>*</sup> are data structures that provide, for the single definition of a variable, the set of all its uses. In turn, a **use-def chain**<sup>*</sup>, which under SSA consists of a single name, uniquely specifies the definition that reaches the use. As we will illustrate further in the book **def-use chains** are useful for **forward data-flow analysis** as they provide direct connections that shorten the **propagation distance** between nodes that generate and use data-flow information.

> NOTE: 一般需要先定义后使用

Because of its single definition per variable property, SSA form simplifies **def-use** and **use-def chains** in several ways. First, SSA form simplifies **def-use chains** as it combines the information as early as possible. This is illustrated by Figure 2.1 where the **def-use chain** in the non-SSA program requires as many merges as there are uses of $x$, whereas the corresponding SSA form allows early and more efficient combination.

Second, as it is easy to associate each variable with its single defining operation, **use-def chains** can be represented and maintained almost for free. As this constitutes the skeleton of the so-called **SSA graph** (see Chapter 12), when considering a program under SSA form, use-def chains are implicitly considered as a given. The explicit representation of **use-def chains** simplifies **backward propagation**, which favors algorithms such as **dead-code elimination**.

> 翻译: 其次，由于可以轻松将每个变量关联到其唯一的定义操作，**使用 - 定义链（use-def chains）**几乎可以零开销地完成表示与维护。这构成了所谓**SSA 图**的骨架（参见第 12 章）；当程序采用 SSA 形式时，使用 - 定义链是默认隐含存在的。**使用 - 定义链**的显式表示简化了**反向传播**，这对于**死代码消除**这类算法十分有利。

For forward propagation, since **def-use chains** are precisely the reverse of **use-def chains**, computing them is also easy; maintaining them requires minimal effort. However, even without **def-use chains**, some lightweight **forward propagation** algorithms such as copy folding<sup>*</sup> are possible: using a single pass that processes operations along a topological order traversal of a forward CFG,<sup>1</sup> most definitions are processed prior to their uses. When processing an operation, the use-def chain provides immediate access to the prior computed value of an argument. Conservative merging is performed when, at some loop headers, a $\phi$-function encounters an unprocessed argument. Such a lightweight propagation engine proves to be fairly efficient.



> NOTE:
> 
> use-def chain: backward propagation 
> 
> def-use chain: forward propagation
