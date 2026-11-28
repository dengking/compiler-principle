# Data-flow-analysis
数据流分析

## wikipedia [Data-flow analysis](https://en.wikipedia.org/wiki/Data-flow_analysis)

**Data-flow analysis** is a technique for gathering information about the possible set of values calculated at various points in a [computer program](https://en.wikipedia.org/wiki/Computer_program "Computer program"). It forms the foundation for a wide variety of compiler optimizations and program verification techniques. A program's [control-flow graph](https://en.wikipedia.org/wiki/Control-flow_graph "Control-flow graph") (CFG) is used to determine those parts of a program to which a particular value assigned to a variable might propagate(程序的**控制流图（CFG）** 用于判定：变量被赋予的某个特定值，可能会传播到程序的哪些代码片段). The information gathered is often used by [compilers](https://en.wikipedia.org/wiki/Compiler "Compiler") when [optimizing](https://en.wikipedia.org/wiki/Optimizing_compiler "Optimizing compiler") a program. A canonical example of a data-flow analysis is [reaching definitions](https://en.wikipedia.org/wiki/Reaching_definitions "Reaching definitions"). Other commonly used **data-flow analyses** include:

- **live variable analysis**

- available expressions 

- constant propagation

- very busy expressions

each serving a distinct purpose in compiler optimization passes.

## Data-flow equation

## Data-flow confluence operator


## 为什么需要data flow analysis

**数据流分析**（Data Flow Analysis）是一种静态分析技术：不运行程序，而是推断程序在**每个执行点**上数据的可能状态，例如变量取什么值、在哪里被定义、在哪里被使用。之所以要做它，主要出于以下几个目的。

### 核心目的：支持编译器优化

编译器想让代码更快、更小，但每次变换都必须**保证程序语义不变**。数据流分析提供了判断"某个优化是否安全"的依据。

| 优化技术            | 依赖的数据流分析                         | 解决的问题                   |
| --------------- | -------------------------------- | ----------------------- |
| **死代码消除**       | 活跃变量分析（Live Variable Analysis）   | 某个赋值的结果以后还会被用到吗？不会就可以删除 |
| **常量传播 / 常量折叠** | 到达定值分析、常量传播分析                    | 某变量在此处是否一定是常量？          |
| **公共子表达式消除**    | 可用表达式分析（Available Expressions）   | 这个表达式之前算过且操作数没变吗？       |
| **循环不变代码外提**    | 到达定值分析                           | 循环里的计算是否每次结果都一样？        |
| **寄存器分配**       | 活跃变量分析                           | 哪些变量同时"活着"，不能共用一个寄存器？   |
| **部分冗余消除**      | 预期表达式分析（Anticipated Expressions） | 能否把计算移到更合适的位置？          |

**例子：**
```c
x = 5;
y = x + 3;   // 常量传播 → y = 8
z = y * 2;   // 继续传播 → z = 16
x = 10;      // 若之后 x 不再被使用 → 死代码，可删除
```

---

### 发现程序错误与缺陷

数据流分析也是许多静态检查工具的基础：

- **使用未初始化的变量**：通过到达定值分析，发现变量在使用前没有被赋值
- **空指针解引用**：追踪指针可能为 `NULL` 的路径
- **资源泄漏**：文件、内存、锁在某些路径上没有释放
- **无用赋值**：赋了值却从未使用，往往是逻辑错误的信号

例如 Java 编译器要求"局部变量使用前必须明确赋值"，背后就是**数据流分析**。

---

### 保障程序安全

- **污点分析**（Taint Analysis）：追踪不可信的用户输入是否未经过滤就流向敏感操作，用于检测 SQL 注入、XSS、命令注入等漏洞
- **信息泄露检测**：判断敏感数据（如密码、隐私信息）是否流向日志或网络等不安全的出口

---

### 辅助程序理解与软件工程

- **程序切片**（Program Slicing）：找出影响某个变量值的所有语句，便于调试
- **重构支持**：IDE 判断"提取方法""内联变量"等操作是否安全
- **影响分析**：修改一处代码后，判断会影响到哪些地方

---

### 为什么必须"系统地"做分析

1. **控制流复杂**：分支和循环使一个程序点可能有无数条执行路径，人工无法逐一推理。
2. **需要保守且可靠的结论**：优化必须对**所有可能的执行**都正确。数据流分析借助格（lattice）和不动点迭代，能在有限时间内得到安全的近似结果。
3. **通用框架可复用**：不同分析都可以统一表达为"传递函数 + 交汇运算 + 迭代求解"，便于在编译器中实现和扩展。

---

### 总结

> 数据流分析回答的是 **"程序运行到这里时，数据可能是什么样子？"**

有了这个答案，编译器才能**安全地优化代码**，工具才能**提前发现错误和安全漏洞**，开发者也能**更好地理解和维护程序**。它是现代编译器（如 GCC、LLVM）和静态分析工具（如 Coverity、SonarQube、CodeQL）的基础技术之一。