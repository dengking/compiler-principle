# Chapter 12 Interprocedural Analysis(跨过程分析)

In this chapter, we motivate the importance of **interprocedural analysis** by discussing a number of important optimization problems that cannot be solved with **intraprocedural analysis(过程内分析)**. We begin by describing the common forms of **interprocedural analysis** and explaining the difficulties in their implementation. We then describe applications for **interprocedural analysis**. For widely used programming languages like C and Java, **pointer alias analysis** is key to any **interprocedural analysis**. Thus, for much of the chapter, we discuss techniques needed to compute **pointer aliases**. To start, we present **Datalog**, a notation that greatly hides the complexity of an efficient **pointer analysis**. We then describe an algorithm for pointer analysis, and show how we use the abstraction of binary decision diagrams (BDD’s) to implement the algorithm efficiently.

翻译: 本章将通过介绍若干关键的优化问题，阐明**跨过程分析**的重要性 —— 这类优化仅凭**过程内分析**无法完成。我们首先介绍跨过程分析的常见类型，讲解落地实现当中的各类难点；随后介绍跨过程分析的实际用途。对于 C、Java 这类主流编程语言，**指针别名分析**是所有跨过程分析的核心基础。因此本章大部分篇幅用来讲解求解**指针别名**的相关技术。开篇会介绍 Datalog 描述语言，该记号体系能够屏蔽高性能**指针分析算法**的复杂细节；之后讲解指针分析算法，并说明如何借助二叉决策图（BDD）这种抽象结构，高效实现该算法。



Most compiler optimizations, including those described in Chapters 9, 10, and 11, are performed on procedures one at a time. We refer to such analyses as **intraprocedural**. These analyses conservatively(保守地) assume that procedures invoked may alter the state of all the variables visible to the procedures and that they may create all possible side effects, such as modifying any of the variables visible to the procedure or generating exceptions that cause the unwinding of the call stack. **Intraprocedural analysis** is thus relatively simple, albeit imprecise. Some optimizations do not need **interprocedural analysis**, while others may yield almost no useful information without it.

翻译: 绝大多数编译器优化（包含第 9、10、11 章介绍的优化），一次仅针对单个函数开展分析，这类分析称作**过程内分析**。过程内分析会采取保守假设：被调用函数能够修改当前函数所有可见变量的状态，并且可以产生全部潜在副作用，例如改动任意可见变量、抛出异常进而引发调用栈回退。所以过程内分析实现简单，但是分析精度较差。一部分优化不需要跨过程分析，还有一部分优化脱离跨过程分析之后几乎得不到任何有效分析信息。




An **interprocedural analysis** operates across an entire program, flowing information from the caller to its callees and vice versa. One relatively simple but useful technique is to **inline procedures**, that is, to replace a procedure invocation by the body of the procedure itself with suitable modifications to account for parameter passing and the return value. This method is applicable only if we know the target of the procedure call. If procedures are invoked indirectly through a pointer or via the method‑dispatch mechanism prevalent in object‑oriented programming, analysis of the program’s pointers or references can in some cases determine the targets of the indirect invocations. If there is a unique target, inlining can be applied. Even if a unique target is determined for each procedure invocation, inlining must be applied judiciously. In general, it is not possible to inline recursive procedures directly, and even without recursion, inlining can expand the code size exponentially.

翻译: 跨过程分析的分析范围覆盖整个程序，能够在调用者与被调用子程序之间双向传递数据流信息。

函数内联是一种实现简单且实用性很强的优化手段：使用子程序函数体替换函数调用语句，同时做出适配改动，用来处理参数传递以及返回值相关逻辑。该优化的使用前提是能够确定函数调用的目标子程序。

倘若函数依靠函数指针发起间接调用，或是采用面向对象编程普遍使用的方法分派机制完成调用；此时通过分析程序当中的指针、引用，部分场景下可以定位出间接调用的目标函数。当调用仅有唯一目标时，便可执行函数内联。

即便已经确定每一处函数调用对应的唯一目标，内联优化依旧需要审慎使用。一般来说递归函数不能够直接进行内联；就算函数不存在递归，不加节制的内联也会令程序代码体量出现指数级膨胀。


