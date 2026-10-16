# 8 Code Generation

- [8.1 Issues in the Design of a Code Generator](8.1-Issues-in-the-Design-of-a-Code-Generator.md)
- [8.10 Optimal Code Generation for Expressions](8.10-Optimal-Code-Generation-for-Expressions.md)
- [8.11 Dynamic Programming Code-Generation](8.11-Dynamic-Programming-Code-Generation.md)
- [8.12 Summary of Chapter 8](8.12-Summary-of-Chapter-8.md)
- [8.13 References for Chapter 8](8.13-References-for-Chapter-8.md)
- [8.2 The Target Language](8.2-The-Target-Language.md)
- [8.3 Addresses in the Target Code](8.3-Addresses-in-the-Target-Code.md)
- [8.4 Basic Blocks and Flow Graphs](8.4-Basic-Blocks-and-Flow-Graphs.md)
- [8.5 Optimization of Basic Blocks](8.5-Optimization-of-Basic-Blocks.md)
- [8.6 A Simple Code Generator](8.6-A-Simple-Code-Generator.md)
- [8.7 Peephole Optimization](8.7-Peephole-Optimization.md)
- [8.8 Register Allocation and Assignment](8.8-Register-Allocation-and-Assignment.md)
- [8.9 Instruction Selection by Tree Rewriting](8.9-Instruction-Selection-by-Tree-Rewriting.md)

## 章首内容

Code Generation
The final phase in our compiler model is the code generator. It takes as input the intermediate representation (IR) produced by the front end of the compiler, along with relevant symbol table information, and produces as output a semantically equivalent target program, as shown in Fig. 8.1.
The requirements imposed on a code generator are severe. The target program must preserve the semantic meaning of the source program and be of high quality; that is, it must make effective use of the available resources of the target machine. Moreover, the code generator itself must run efficiently.
The challenge is that, mathematically, the problem of generating an optimal target program for a given source program is undecidable; many of the subproblems encountered in code generation such as register allocation are computationally intractable. In practice, we must be content with heuristic techniques that generate good, but not necessarily optimal, code. Fortunately, heuristics have matured enough that a carefully designed code generator can produce code that is several times faster than code produced by a naive one.
Compilers that need to produce efficient target programs, include an optimization phase prior to code generation. The optimizer maps the IR into
IR from which more efficient code can be generated. In general, the codeoptimization and code-generation phases of a compiler, often referred to as the back end, may make multiple passes over the IR before generating the target program. Code optimization is discussed in detail in Chapter 9. The techniques presented in this chapter can be used whether or not an optimization phase occurs before code generation.
A code generator has three primary tasks: instruction selection, register source Front intermediate Code intermediate Code target program End code Optimizer code Generator program
Figure 8.1: Position of code generator allocation and assignment, and instruction ordering. The importance of these tasks is outlined in Section 8.1. Instruction selection involves choosing appropriate target-machine instructions to implement the IR statements. Register allocation and assignment involves deciding what values to keep in which registers. Instruction ordering involves deciding in what order to schedule the execution of instructions.
This chapter presents algorithms that code generators can use to translate the IR into a sequence of target language instructions for simple register machines. The algorithms will be illustrated by using the machine model in Section 8.2. Chapter 10 covers the problem of code generation for complex modern machines that support a great deal of parallelism within a single instruction.
After discussing the broad issues in the design of a code generator, we show what kind of target code a compiler needs to generate to support the abstractions embodied in a typical source language. In Section 8.3, we outline implementations of static and stack allocation of data areas, and show how names in the IR can be converted into addresses in the target code.
Many code generators partition IR instructions into \basic blocks," which consist of sequences of instructions that are always executed together. The partitioning of the IR into basic blocks is the subject of Section 8.4. The following section presents simple local transformations that can be used to transform basic blocks into modified basic blocks from which more efficient code can be generated. These transformations are a rudimentary form of code optimization, although the deeper theory of code optimization will not be taken up until Chapter 9. An example of a useful, local transformation is the discovery of common subexpressions at the level of intermediate code and the resultant replacement of arithmetic operations by simpler copy operations.
Section 8.6 presents a simple code-generation algorithm that generates code for each statement in turn, keeping operands in registers as long as possible.
The output of this kind of code generator can be readily improved by peephole optimization techniques such as those discussed in the following Section 8.7.
The remaining sections explore instruction selection and register allocation.
