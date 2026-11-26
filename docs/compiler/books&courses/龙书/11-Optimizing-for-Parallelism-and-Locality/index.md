# Chapter 11 Optimizing for Parallelism and Locality

This chapter shows how a compiler can enhance ***parallelism*** and ***locality*** in computationally intensive programs involving **arrays** to speed up target programs running on **multiprocessor systems**. Many scientific, engineering, and commercial applications have an insatiable need for computational cycles. Examples include weather prediction, protein‑folding for designing drugs, fluid‑dynamics for designing aeropropulsion systems, and quantum chromodynamics for studying the strong interactions in high‑energy physics.

翻译: 本章介绍编译器如何优化含数组的计算密集型程序，提升程序的并行度与数据局部性，进而运行在多处理器设备上、加快目标程序执行速度。大量科研、工程以及商业应用有着极高的算力需求，典型案例包含天气预报、药物研发的蛋白质折叠计算、航空推进系统设计所需的流体力学运算，还有用于研究高能物理强相互作用的量子色动力学计算。

One way to speed up a computation is to use **parallelism**. Unfortunately, it is not easy to develop software that can take advantage of parallel machines. Dividing the computation into units that can execute on different processors in parallel is already hard enough; yet that by itself does not guarantee a speedup. We must also minimize **interprocessor communication**, because communication overhead can easily make the parallel code run even slower than the sequential execution!

翻译: 提升运算速度的一种途径是启用并行计算。但想要开发出能够发挥并行硬件优势的软件并不简单。将计算任务拆分为多个可在不同处理器上并行执行的执行单元本身已是难题；仅仅完成任务拆分并不能确保程序提速。我们还需要尽可能缩减处理器之间的数据通信，通信开销很容易致使并行程序的运行速度反倒低于串行版本！

Minimizing communication can be thought of as a special case of improving a program’s ***data locality***. In general, we say that a program has good ***data locality*** if a processor often accesses the same data it has used recently. Surely if a processor on a parallel machine has good **locality**, it does not need to communicate with other processors frequently. Thus, **parallelism** and **data locality** need to be considered hand‑in‑hand. **Data locality**, by itself, is also important for the performance of individual processors. Modern processors have one or more level of caches in the memory hierarchy; a **memory access** can take tens of **machine cycles** whereas a cache hit would only take a few cycles. If a program does not have good **data locality** and misses in the cache often, its performance will suffer.

翻译: 减少处理器间通信，可以视作优化程序数据局部性的一类特殊情形。一般而言，如果处理器会频繁访问近期使用过的数据，我们就称该程序具备良好的数据局部性。

并行设备当中的处理器倘若拥有优秀的数据局部性，便无需频繁和其余处理器传输数据。由此可见，并行性与数据局部性需要同步考量。

单看数据局部性，它同样会影响单核处理器的运行效率。现代处理器的存储层级结构内置一级或多级高速缓存；一次内存访问需要耗费数十个机器周期，而缓存命中仅需少数周期。一旦程序的数据局部性较差、频繁发生缓存缺失，程序性能便会受损。

Another reason why parallelism and locality are treated together in this same chapter is that they share the same theory. If we know how to optimize for **data locality**, we know where the parallelism is. You will see in this chapter that the **program model** we used for **data‑flow analysis** in Chapter 9 is inadequate for **parallelization** and **locality** optimization. The reason is that work on **data‑flow analysis** assumes we don’t distinguish among the ways a given statement is reached, and in fact these Chapter 9 techniques take advantage of the fact that we don’t distinguish among different executions of the same statement, e.g., in a loop. To parallelize a code, we need to reason about the dependences among different dynamic executions of the same statement to determine if they can be executed on different processors simultaneously.

翻译: 本章将并行性和局部性放在一起探讨的另一个原因，是二者拥有同一套理论基础。只要掌握了数据局部性的优化方法，就能够找到程序当中可挖掘的并行位置。

你在本章将会了解到，第 9 章数据流分析所采用的程序模型，并不适用于并行化与局部性优化。

原因在于数据流分析默认不去区分语句抵达的路径；实际上第九章的相关技术正是利用该特性，不去区分同一条语句的多次动态执行（例如循环里的迭代）。

想要实现代码并行化，我们就必须分析同一条语句各个动态实例之间的数据依赖，以此判断它们能否分发至不同处理器同时运行。

This chapter focuses on techniques for optimizing the class of numerical applications that use arrays as data structures and access them with simple regular patterns. More specifically, we study programs that have **affine array accesses** with respect to surrounding loop indexes. For example, if $i$ and $j$ are the index variables of surrounding loops, then $Z[i][j]$ and $Z[i][i + j]$ are **affine accesses**. A function of one or more variables, $x_1,x_2,\dots,x_n$ is affine if it can be expressed as a sum of a constant, plus constant multiples of the variables, i.e., $c_0 + c_1x_1 + c_2x_2 + \dots + c_nx_n$, where $c_0,c_1,\dots,c_n$ are constants. Affine functions are usually known as linear functions, although strictly speaking, linear functions do not have the $c_0$ term.

翻译: 本章主要讲解数值类应用程序的优化技术，这类程序以数组作为数据结构，并按照规整简单的模式访问数组元素。更为具体地来说，我们研究数组下标相对于外层循环索引属于**仿射访问**的程序。举个例子，假定 $i$、$j$ 为循环索引变量，那么 $Z[i][j]$、$Z[i][i+j]$ 均属于仿射访问。对于含有一个或多个自变量 $x_1,x_2,\dots,x_n$ 的函数，倘若能够写成常数项加上各个变量常数倍之和，则该函数为仿射函数：

$$
c_0 + c_1x_1 + c_2x_2 + \dots + c_nx_n
$$

式中 $c_0,c_1,\dots,c_n$ 全部为常量。仿射函数常常被俗称为线性函数；不过严格的定义里，纯线性函数并不包含常数项 $c_0$。



Here is a simple example of a loop in this domain:

```c
for (i = 0; i < 10; i++) {
    Z[i] = 0;
}
```

Because iterations of the loop write to different locations, different processors can execute different iterations concurrently. On the other hand, if there is another statement $\text{Z}[j] = 1$ being executed, we need to worry about whether $i$ could ever be the same as $j$, and if so, in which order do we execute those instances of the two statements that share a common value of the array index.



翻译: 该循环的每一次迭代写入互不相同的内存地址，因此多个处理器能够并发执行不同循环迭代。但倘若程序还有另一条执行语句 $\boldsymbol{Z}[j] = 1$，我们就需要考虑循环变量 $i$ 是否有可能等于 $j$；一旦二者存在相等的情况，就必须规定两条语句在数组下标取值相同时，各个执行实例的先后执行顺序。

Knowing which iterations can refer to the same memory location is important. This knowledge lets us specify the **data dependences** that must be honored(遵循) when scheduling code for both uniprocessors and multiprocessors. Our objective is to find a schedule that honors all the **data dependences** such that operations that access the same location and cache lines are performed row. We may instead subdivide the array into blocks and visit all elements in a block before moving to the next. The resulting code will consist of outer loops traversing the blocks, and then inner loops to sweep the elements within each block. Linear algebra techniques are used to determine both the **best affine partitions** and the **best blocking schemes**.

翻译: 弄清楚哪些循环迭代会访问同一个内存地址十分关键。借助该信息，我们便可确定，在为单核处理器与多处理器做代码调度时所必须遵守的数据依赖。

我们的目标是寻找到一套调度方案：在满足全部数据依赖约束的前提下，使访问同一存储地址、同一缓存行的运算就近执行。

作为替代方案，我们可以将数组拆分成若干数据块，遍历完一个块的全部元素之后，再处理下一个块。经过变换后的代码包含两层循环，外层循环遍历各个分块，内层循环遍历块当中的数组元素。

最优仿射划分方案以及最优循环分块策略，均依靠线性代数相关方法求解得出。



In the following, we first start with an overview of the concepts in parallel computation and locality optimization in Section 11.1. Then, Section 11.2 is an extended concrete example — matrix multiplication — that shows how **loop transformations** that reorder the computation inside a loop can improve both **locality** and the effectiveness of **parallelization**.

翻译: 接下来，11.1 节首先概述并行计算与局部性优化的相关概念；随后 11.2 节给出详尽的实操案例 —— 矩阵乘法，以此演示通过循环变换调整循环内部计算顺序，同时优化数据局部性、提升并行化执行效率。



Sections 11.3 to Sections 11.6 present the preliminary information necessary for **loop transformations**. Section 11.3 shows how we model the individual iterations in a loop nest; Section 11.4 shows how we model array index functions that map each loop iteration to the array locations accessed by the iteration; Section 11.5 shows how to determine which iterations in a loop refer to the same array location or the same cache line using standard linear algebra algorithms; and Section 11.6 shows how to find all the data dependences among array references in a program.

翻译: 11.3‑11.6 节介绍循环变换所需的前置基础知识。

- 11.3 节讲解如何对循环嵌套里的单次迭代建立模型；
- 11.4 节讲解数组下标函数建模，该函数可以把每一轮循环迭代映射至它所访问的数组存储位置；
- 11.5 节介绍借助标准线性代数算法，判断循环中哪些迭代访问同一个数组单元或是同一条缓存行；
- 11.6 节说明如何找出程序内所有数组引用之间存在的数据依赖。



The rest of the chapter applies these preliminaries in coming up with the optimizations. Section 11.7 first looks at the simpler problem of finding parallelism that requires no synchronization. To find the best affine partitioning, we simply find the solution to the constraint that operations that share a data dependence must be assigned to the same processor.



Well, not too many programs can be parallelized without requiring any synchronization. Thus, in Sections 11.8 through 11.9.9, we consider the general case of finding parallelism that requires synchronization. We introduce the concept of pipelining, show how to find the affine partitioning that maximizes the degree of pipelining allowed by a program. We show how to optimize for locality in Section 11.10. Finally, we discuss how affine transforms are useful for optimizing for other forms of parallelism.
