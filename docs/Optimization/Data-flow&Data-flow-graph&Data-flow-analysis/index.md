# Data-flow&Data-flow-graph&Data-flow-analysis



## wikipedia [Data-flow analysis](https://en.wikipedia.org/wiki/Data-flow_analysis)

**Data-flow analysis** is a technique for gathering information about the possible set of values calculated at various points in a [computer program](https://en.wikipedia.org/wiki/Computer_program "Computer program"). It forms the foundation for a wide variety of compiler optimizations and program verification techniques. A program's [control-flow graph](https://en.wikipedia.org/wiki/Control-flow_graph "Control-flow graph") (CFG) is used to determine those parts of a program to which a particular value assigned to a variable might propagate(程序的**控制流图（CFG）** 用于判定：变量被赋予的某个特定值，可能会传播到程序的哪些代码片段). The information gathered is often used by [compilers](https://en.wikipedia.org/wiki/Compiler "Compiler") when [optimizing](https://en.wikipedia.org/wiki/Optimizing_compiler "Optimizing compiler") a program. A canonical example of a data-flow analysis is [reaching definitions](https://en.wikipedia.org/wiki/Reaching_definitions "Reaching definitions"). Other commonly used **data-flow analyses** include:

- **live variable analysis**

- available expressions 

- constant propagation

- very busy expressions

each serving a distinct purpose in compiler optimization passes.

## Data-flow equation

## Data-flow confluence operator



## may&must&lattice

补充说明：在数据流分析的语境中，"may" 与 "must" 是两种经典的格（lattice）方向 ——may 分析取**上近似**（可能发生即记为发生，对应并集），must 分析取**下近似**（必然发生才记为发生，对应交集）。活跃性分析之所以是 "may"，是因为只要某条路径上变量未来会被用到，就不能在当前点将其寄存器回收。


