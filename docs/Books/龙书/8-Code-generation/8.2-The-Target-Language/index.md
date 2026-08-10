# 8.2 The Target Language

Familiarity with the target machine and its **instruction set** is a prerequisite for designing a good **code generator**. Unfortunately, in a general discussion of code generation it is not possible to describe any **target machine** in sufficient detail to generate good code for a complete language on that machine. In this chapter, we shall use as a **target language assembly code** for a simple computer that is representative of many register machines. However, the code‑generation techniques presented in this chapter can be used on many other classes of machines as well.

翻译: 熟悉目标机器及其指令集，是设计出优秀代码生成器的先决条件。遗憾的是，在对代码生成进行通用性讲解时，我们无法详尽描述某一台目标机器的全部细节，从而为整套编程语言在该设备上产出优质目标代码。本章选用一台简易寄存器型计算机的汇编语言作为目标语言，该机型可以代表绝大多数寄存器架构机器。与此同时，本章介绍的各类代码生成技术同样适用于其余多种硬件机型。

## 8.2.1 A Simple Target Machine Model

Our target computer models a **three‑address machine** with load and store operations, **computation operations**, **jump operations**, and **conditional jumps**. The underlying computer is a byte‑addressable machine with $n$ general‑purpose registers, R0, R1, … , Rn − 1. 



A full‑fledged assembly language would have scores of instructions. To avoid hiding the concepts in a myriad of details, we shall use a very limited set of instructions and assume that all operands are integers. Most instructions consists of an operator, followed by a target, followed by a list of source operands. A label may precede an instruction. We assume the following kinds of instructions are available:

### Load operations

**Load operations**: The instruction `LD dst, addr` loads the value in location `addr` into location `dst`. This instruction denotes the assignment `dst = addr`. The most common form of this instruction is `LD r, x` which loads the value in location $x$ into register $r$. An instruction of the form `LD r1, r2` is a register‑to‑register copy in which the contents of register $r_2$ are copied into register $r_1$.

### Store operations

**Store operations**: The instruction `ST x, r` stores the value in register $r$ into the location $x$. This instruction denotes the assignment $x = r$.

### Computation operations

**Computation operations** of the form `OP dst, src₁, src₂`, where $OP$ is an operator like ADD or SUB, and dst, $src_1$, and $src_2$ are locations, not necessarily distinct. The effect of this machine instruction is to apply the operation represented by $OP$ to the values in locations $src_1$ and $src_2$, and place the result of this operation in location dst. For example, `SUB r1, r2, r3` computes $r_1 = r_2 - r_3$. Any value formerly stored in $r_1$ is lost, but if $r_1$ is $r_2$ or $r_3$, the old value is read first. Unary operators that take only one operand do not have a $src_2$.
