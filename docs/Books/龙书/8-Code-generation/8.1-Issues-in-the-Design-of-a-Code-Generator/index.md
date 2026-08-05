# 8.1 Issues in the Design of a Code Generator

While the details are dependent on the specifics of the **intermediate representation**, the target language, and the run‑time system, tasks such as **instruction selection**, **register allocation** and **assignment**, and **instruction ordering** are encountered in the design of almost all code generators.

翻译: 尽管实现细节取决于中间表示、目标语言以及运行时系统的具体特性，但几乎所有代码生成器的设计过程中，都会碰到指令选择、寄存器分配与指派、指令排序这类工作。

The most important criterion for a **code generator** is that it produce correct code. Correctness takes on special significance because of the number of special cases that a code generator might face. Given the premium on correctness, designing a **code generator** so it can be easily implemented, tested, and maintained is an important design goal.

翻译: 代码生成器最为核心的评判标准，就是产出正确的目标代码。由于代码生成器需要处理海量特殊场景，因此正确性有着格外关键的地位。鉴于正确性拥有极高优先级，将代码生成器设计成便于开发实现、测试以及后期维护，是一项重要的设计目标。

## 8.1.1 Input to the Code Generator

The input to the code generator is the **intermediate representation** of the source program produced by the **front end**, along with information in the **symbol table** that is used to determine the run‑time addresses of the data objects denoted by the names in the IR.

The many choices for the IR include three‑address representations such as quadruples, triples, indirect triples; virtual machine representations such as bytecodes and stack‑machine code; linear representations such as postfix notation; and graphical representations such as syntax trees and DAG's. Many of the algorithms in this chapter are couched in terms of the representations considered in Chapter 6: three‑address code, trees, and DAG's. The techniques we discuss can be applied, however, to the other intermediate representations as well.
In this chapter, we assume that the front end has scanned, parsed, and translated the source program into a relatively low‑level IR, so that the values of the names appearing in the IR can be represented by quantities that the target machine can directly manipulate, such as integers and floating‑point numbers. We also assume that all syntactic and static semantic errors have been detected, that the necessary type checking has taken place, and that type‑conversion operators have been inserted wherever necessary. The code generator can therefore proceed on the assumption that its input is free of these kinds of errors.

## 8.1.2 The Target Program

The instruction‑set architecture of the target machine has a significant impact on the difficulty of constructing a good code generator that produces high‑quality machine code. The most common target‑machine architectures are RISC (reduced instruction set computer), CISC (complex instruction set computer), and stack based.
A RISC machine typically has many registers, three‑address instructions, simple addressing modes, and a relatively simple instruction‑set architecture. In contrast, a CISC machine typically has few registers, two‑address instructions, a variety of addressing modes, several register classes, variable‑length instructions, and instructions with side effects.
In a stack‑based machine, operations are done by pushing operands onto a stack and then performing the operations on the operands at the top of the stack. To achieve high performance the top of the stack is typically kept in registers. Stack‑based machines almost disappeared because it was felt that the stack organization was too limiting and required too many swap and copy operations.
However, stack‑based architectures were revived with the introduction of the Java Virtual Machine (JVM). The JVM is a software interpreter for Java bytecodes, an intermediate language produced by Java compilers. The inter‑
