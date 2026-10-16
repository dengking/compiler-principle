# 12 Interprocedural Analysis

- [12.1 Basic Concepts](12.1-Basic-Concepts.md)
- [12.2 Why Interprocedural Analysis?](12.2-Why-Interprocedural-Analysis.md)
- [12.3 A Logical Representation of Data Flow](12.3-A-Logical-Representation-of-Data-Flow.md)
- [12.4 A Simple Pointer-Analysis Algorithm](12.4-A-Simple-Pointer-Analysis-Algorithm.md)
- [12.5 Context-Insensitive Interprocedural Analysis](12.5-Context-Insensitive-Interprocedural-Analysis.md)
- [12.6 Context-Sensitive Pointer Analysis](12.6-Context-Sensitive-Pointer-Analysis.md)
- [12.7 Datalog Implementation by BDD's](12.7-Datalog-Implementation-by-BDD's.md)
- [12.8 Summary of Chapter 12](12.8-Summary-of-Chapter-12.md)
- [12.9 References for Chapter 12](12.9-References-for-Chapter-12.md)

## 章首内容

Interprocedural Analysis
In this chapter, we motivate the importance of interprocedural analysis by discussing a number of important optimization problems that cannot be solved with intraprocedural analysis. We begin by describing the common forms of interprocedural analysis and explaining the difficulties in their implementation.
We then describe applications for interprocedural analysis. For widely used programming languages like C and Java, pointer alias analysis is key to any interprocedural analysis. Thus, for much of the chapter, we discuss techniques needed to compute pointer aliases. To start, we present Datalog, a notation that greatly hides the complexity of an efficient pointer analysis. We then describe an algorithm for pointer analysis, and show how we use the abstraction of binary decision diagrams (BDD's) to implement the algorithm efficiently.
Most compiler optimizations, including those described in Chapters 9, 10, and 11, are performed on procedures one at a time. We refer to such analyses as intraprocedural. These analyses conservatively assume that procedures invoked may alter the state of all the variables visible to the procedures and that they may create all possible side effects, such as modifying any of the variables visible to the procedure or generating exceptions that cause the unwinding of the call stack. Intraprocedural analysis is thus relatively simple, albeit imprecise.
Some optimizations do not need interprocedural analysis, while others may yield almost no useful information without it.
An interprocedural analysis operates across an entire program, flowing information from the caller to its callees and vice versa. One relatively simple but useful technique is to inline procedures, that is, to replace a procedure invocation by the body of the procedure itself with suitable modifications to account for parameter passing and the return value. This method is applicable only if we know the target of the procedure call.
If procedures are invoked indirectly through a pointer or via the methoddispatch mechanism prevalent in object-oriented programming, analysis of the program's pointers or references can in some cases determine the targets of the indirect invocations. If there is a unique target, inlining can be applied.
Even if a unique target is determined for each procedure invocation, inlining must be applied judiciously. In general, it is not possible to inline recursive procedures directly, and even without recursion, inlining can expand the code size exponentially.
