# Static single assignment form

采用 SSA 的:

一、根据 wikipedia [valgrind](https://en.wikipedia.org/wiki/Valgrind) 中的介绍，valgrind 的 IR 采用的就是 [SSA](https://en.wikipedia.org/wiki/Static_single_assignment_form)-based form。

二、LLVM IR:

1、[Single-Static Assignment Form and PHI](https://mapping-high-level-constructs-to-llvm-ir.readthedocs.io/en/latest/control-structures/ssa-phi.html)

 2、zhihu [如何评价只有 LLVM 10% 代码的 QBE？](https://www.zhihu.com/question/43956056/answer/97238727)



## wikipedia [Static single assignment form](https://en.wikipedia.org/wiki/Static_single_assignment_form)

In [compiler](https://en.wikipedia.org/wiki/Compiler) design, **static single assignment form** (often abbreviated as **SSA form** or simply **SSA**) is a property of an [intermediate representation](https://en.wikipedia.org/wiki/Intermediate_representation) (IR), which requires that each variable be [assigned](https://en.wikipedia.org/wiki/Assignment_(computer_science)) exactly once, and every variable be defined before it is used. Existing variables in the original IR are split into *versions*, new variables typically indicated by the original name with a subscript in textbooks, so that every definition gets its own version. In SSA form, [use-def chains](https://en.wikipedia.org/wiki/Use-define_chain) are explicit and each contains a single element.



