# Dynamic semantic

**动态语义**定义的是"这段程序执行起来意味着什么"。程序设计语言形式语义学的**形式化方法**有三套经典路线/范式:

| 方法                                | 做法                          | 典型用处                        |
| --------------------------------- | --------------------------- | --------------------------- |
| **操作语义** (operational semantics)  | 定义**状态转移规则**(小步 / 大步)       | 解释器、WebAssembly 规范、Rust MIR |
| **指称语义** (denotational semantics) | 把程序映射成数学对象(函数)              | 理论研究、抽象解释的基础                |
| **公理语义** (axiomatic semantics)    | Hoare 三元组 $\{P\}\,C\,\{Q\}$ | 程序验证、CompCert、契约式设计         |

**优化器真正吃的是动态语义。** 这点很重要:一个 pass 合不合法,判据不是"改完后语法还对吗",而是"改完后的**可观察行为**和改之前一致吗"。所以语义规范写得越精确,优化器能做的就越激进——这正是 LangRef 把大半篇幅花在 poison / undef / UB / `nsw` 上的原因。



## wikipedia [Semantics (programming languages)](https://en.wikipedia.org/wiki/Semantics_(programming_languages))
  
  > NOTE: 这篇文章所讲述的其实是动态语义

In [programming language theory](https://en.wikipedia.org/wiki/Programming_language_theory "Programming language theory"), **semantics** is the rigorous mathematical logic study of the meaning of [programming languages](https://en.wikipedia.org/wiki/Programming_language "Programming language").[[1]](https://en.wikipedia.org/wiki/Semantics_\(programming_languages\)#cite_note-1) Semantics assigns [computational](https://en.wikipedia.org/wiki/Computation "Computation") meaning to valid [strings](https://en.wikipedia.org/wiki/String_\(computer_science\)) in a [programming language syntax](https://en.wikipedia.org/wiki/Programming_language_syntax "Programming language syntax"). It is closely related to, and often crosses over with, the [semantics of mathematical proofs](https://en.wikipedia.org/wiki/Semantics_of_logic "Semantics of logic").

> 翻译: 在**编程语言理论**中，**语义学**是借助数理逻辑对编程语言的含义展开的严谨研究¹。语义学为符合**编程语言语法**的合法字符串赋予**计算**层面的含义，它与**逻辑语义学**联系紧密，研究领域多有交叉。

Semantics describes the processes a computer follows when [executing](https://en.wikipedia.org/wiki/Execution_\(computing\) "Execution (computing)") a program in that specific language. This can be done by describing the relationship between the input and output of a program, or giving an explanation of how the program will be executed on a certain [platform](https://en.wikipedia.org/wiki/Computer_platform "Computer platform"), thereby creating a [model of computation](https://en.wikipedia.org/wiki/Model_of_computation "Model of computation").

> 翻译: 语义学描述了计算机执行某一特定语言的程序时所遵循的过程。其研究路径分为两类：
> 一是刻画程序输入与输出之间的对应关系
> 二是阐释程序在特定**计算机平台**上的执行机制
> 上述二者都可以构建出对应的**计算模型**。

## 每一级IR都有自己的一份动态语义
每一级 IR 都有自己的一份动态语义，下面是一个例子:

```
C/C++ 源码      ← ISO 标准(散文)
   │
LLVM IR         ← LangRef(散文)          ← 本文主角
   │
MIR             ← 几乎没有正式规范
   │
机器码           ← ISA 手册(RISC-V 有 Sail 形式语义)
```

