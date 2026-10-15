# 8.1 Issues in the Design of a Code Generator

While the details are dependent on the specifics of the **intermediate representation**, the target language, and the run‑time system, tasks such as **instruction selection**, **register allocation** and **assignment**, and **instruction ordering** are encountered in the design of almost all code generators.

翻译: 尽管实现细节取决于中间表示、目标语言以及运行时系统的具体特性，但几乎所有代码生成器的设计过程中，都会碰到指令选择、寄存器分配与指派、指令排序这类工作。

The most important criterion for a **code generator** is that it produce correct code. Correctness takes on special significance because of the number of special cases that a **code generator** might face. Given the premium on correctness, designing a **code generator** so it can be easily implemented, tested, and maintained is an important design goal.

翻译: 代码生成器最为核心的评判标准，就是产出正确的目标代码。由于代码生成器需要处理海量特殊场景，因此正确性有着格外关键的地位。鉴于正确性拥有极高优先级，将代码生成器设计成便于开发实现、测试以及后期维护，是一项重要的设计目标。

## 8.1.1 Input to the Code Generator

The input to the code generator is the **intermediate representation** of the source program produced by the **front end**, along with information in the **symbol table** that is used to determine the run‑time addresses of the data objects denoted by the names in the IR.

The many choices for the IR include:

- three‑address representations such as quadruples, triples, indirect triples; 

- virtual machine representations such as bytecodes and stack‑machine code; 

- linear representations such as postfix notation; 

- graphical representations such as syntax trees and DAG's;

Many of the algorithms in this chapter are couched in terms of(以…… 作为表达方式、基于…… 来阐述) the representations considered in Chapter 6: three‑address code, trees, and DAG's. The techniques we discuss can be applied, however, to the other **intermediate representations** as well.

In this chapter, we assume that the **front end** has scanned, parsed, and translated the source program into a relatively low‑level IR, so that the values of the names appearing in the IR can be represented by quantities(数据) that the target machine can directly manipulate, such as integers and floating‑point numbers. We also assume that all syntactic and **static semantic errors** have been detected, that the necessary type checking has taken place, and that **type‑conversion operators** have been inserted wherever necessary. The **code generator** can therefore proceed on the assumption that its input is free of these kinds of errors.

翻译: 在本章中，我们假定编译器**前端**已经完成源代码的词法扫描、语法分析与翻译工作，将源程序转换为偏底层的中间表示；因此中间表示内出现的变量取值，都能够由目标机器可直接操作的数据承载，例如整型、浮点数。同时我们默认所有语法错误、**静态语义错误**均已排查完毕，完成了全部必需的类型检查，并且在需要的位置插入好了**类型转换运算符**。故而**代码生成器**可以直接开展工作，无需再处理上述各类错误。

## 8.1.2 The Target Program

The **instruction‑set architecture** of the target machine has a significant impact on the difficulty of constructing a good **code generator** that produces high‑quality machine code. The most common target‑machine architectures are RISC (reduced instruction set computer), CISC (complex instruction set computer), and stack based.

A RISC machine typically has many registers, **three‑address instructions**, simple addressing modes, and a relatively simple **instruction‑set architecture**. In contrast, a CISC machine typically has few registers, two‑address instructions, a variety of addressing modes, several register classes, variable‑length instructions, and instructions with side effects.

In a **stack‑based machine**, operations are done by pushing operands onto a stack and then performing the operations on the operands at the top of the stack. To achieve high performance the top of the stack is typically kept in registers. **Stack‑based machines** almost disappeared because it was felt that the stack organization was too limiting and required too many swap and copy operations.

However, stack‑based architectures were revived(再度兴起) with the introduction of the Java Virtual Machine (JVM). The JVM is a software interpreter for Java bytecodes, an intermediate language produced by Java compilers. The interpreter provides software compatibility across multiple platforms, a major factor in the success of Java.

翻译: 不过，随着 Java 虚拟机（JVM）问世，基于栈的架构再度兴起。JVM 是用于解析 Java 字节码的软件解释器，而 Java 字节码即为 Java 编译器输出的一种中间语言。

To overcome the high performance penalty of interpretation, which can be on the order of a factor of 10, **just‑in‑time (JIT)** Java compilers have been created. These JIT compilers translate bytecodes during run time to the native hardware instruction set of the target machine. Another approach to improving Java performance is to build a compiler that compiles directly into the machine instructions of the target machine, bypassing the Java bytecodes entirely.

翻译: 为解决解释执行高达十倍左右的严重性能损耗，人们研发出 Java 即时（JIT）编译器。这类即时编译器会在程序运行期间，将字节码翻译为目标机器原生硬件指令集。还有一种提升 Java 运行性能的方案：构造编译器直接输出目标机机器指令，彻底跳过 Java 字节码这一层。

Producing an **absolute machine‑language program** as output has the advantage that it can be placed in a fixed location in memory and immediately executed. Programs can be compiled and executed quickly.

翻译: 输出**绝对地址机器语言程序**的优点十分突出：程序能够存放于内存固定地址，加载之后便可立刻运行，实现快速编译‑执行。

Producing a **relocatable machine‑language program** (often called an **object module**) as output allows subprograms to be compiled separately. A set of **relocatable object modules** can be linked together and loaded for execution by a **linking loader**. Although we must pay the added expense of linking and loading if we produce **relocatable object modules**, we gain a great deal of flexibility in being able to compile subroutines separately and to call other previously compiled programs from an object module. If the **target machine** does not handle relocation automatically, the compiler must provide explicit **relocation information** to the loader to link the separately compiled program modules.

翻译: 输出**可重定位机器语言程序**（常称作**目标模块**）支持子程序分开独立编译。一组可重定位目标模块可经由链接加载器完成链接、载入内存并运行。尽管生成可重定位目标模块需要承担链接与加载带来的额外开销，但它带来极高的灵活性：子程序能够单独编译，目标模块也可以调用其它提前编译完毕的程序。倘若目标硬件无法自动完成地址重定位，编译器就必须向加载器提供明确的重定位信息，用来拼接多个独立编译的程序模块。

Producing an **assembly‑language program** as output makes the process of code generation somewhat easier. We can generate **symbolic instructions** and use the macro facilities of the assembler to help generate code. The price paid is the assembly step after code generation.

翻译: 输出汇编语言程序能够简化代码生成阶段的工作。编译器只需要生成符号化指令，还可以借助汇编器的宏功能辅助代码构建；代价是代码生成结束后，还需要额外执行一次汇编步骤。

In this chapter, we shall use a very simple RISC‑like computer as our target machine. We add to it some CISC‑like addressing modes so that we can also discuss code‑generation techniques for CISC machines. For readability, we use assembly code as the target language. As long as addresses can be calculated from offsets and other information stored in the symbol table, the code generator can produce relocatable or absolute addresses for names just as easily as symbolic addresses.

翻译: 本章将采用一台简易的类‑RISC 计算机作为目标机器；我们为它增添部分 CISC 风格寻址方式，由此也能够讲解适用于复杂指令集机器的代码生成技术。出于可读性考量，下文使用汇编代码充当目标语言。只要依靠偏移量、符号表内存储的其余信息即可计算地址，代码生成器生成符号地址、可重定位地址或者绝对地址的难易程度都是一致的。

## 8.1.3 Instruction Selection

The **code generator** must map the IR program into a code sequence that can be
executed by the target machine. The complexity of performing this mapping is
determined by factors such as

- the level of the IR
- the nature of the **instruction‑set architecture**
- the desired quality of the generated code.

If the IR is **high level**, the **code generator** may translate each IR statement into a sequence of **machine instructions** using **code templates**. Such **statement‑by‑statement code generation**, however, often produces poor code that needs further optimization. If the IR reflects some of the **low‑level** details of the underlying machine, then the **code generator** can use this information to generate more efficient code sequences.

The nature of the instruction set of the target machine has a strong effect on the difficulty of instruction selection. For example, the uniformity and completeness of the instruction set are important factors. If the target machine does not support each data type in a uniform manner, then each exception to the general rule requires special handling. On some machines, for example, floating‑point operations are done using separate registers.

Instruction speeds and machine idioms are other important factors. If we do not care about the efficiency of the target program, instruction selection is straightforward. For each type of three‑address statement, we can design a code skeleton that defines the target code to be generated for that construct. For example, every three‑address statement of the form x = y + z, where x, y, and z are statically allocated, can be translated into the code sequence

This strategy often pro duces redundant loads and stores. For example, the sequence of three-address statements

## 8.1.4 Register Allocation

A key problem in **code generation** is deciding what values to hold in what registers. Registers are the fastest computational unit on the target machine, but we usually do not have enough of them to hold all values. Values not held in registers need to reside in memory. Instructions involving register operands are invariably shorter and faster than those involving operands in memory, so efficient utilization of registers is particularly important.

The use of registers is often subdivided into two subproblems:

1. *Register allocation*, during which we select the set of variables that will reside in registers at each point in the program.
2. *Register assignment*, during which we pick the specific register that a variable will reside in.

Finding an optimal assignment of registers to variables is difficult, even with single‑register machines. Mathematically, the problem is **NP‑complete**. The problem is further complicated because the hardware and/or the operating system of the target machine may require that certain register‑usage conventions be observed.

### Example 8.1

**Example 8.1**: Certain machines require ***register‑pairs*** (an even and next odd‑numbered register) for some operands and results. For example, on some machines, integer multiplication and integer division involve **register pairs**. The multiplication instruction is of the form

翻译: 编号为偶数的寄存器 + 紧随其后的奇数编号寄存器

NOTE: **register‑pairs 寄存器对**：老式计算机 ALU 为支持 64 位乘法，使用相邻一偶一奇两个 32‑bit 寄存器拼接成宽位存储

```
M x, y
```

where $x$, the multiplicand, is the odd register of an even/odd register pair and $y$, the multiplier, can be anywhere. The product occupies the entire even/odd register pair. 

翻译: 其中被乘数 `x` 需要存放在一组奇偶寄存器对内的奇数寄存器；乘数 `y` 的存放位置不受限制。乘法运算结束之后，完整的乘积会占用整组奇偶寄存器对。

The division instruction is of the form

```
D x, y
```

where the dividend occupies an even/odd register pair whose even register is x;
the divisor is y. After division, the even register holds the remainder and the
odd register the quotient.

翻译: 被除数预先存放在一组奇偶寄存器对内，该组的偶数寄存器编号为`x`；`y`代表除数。除法运算完成后：偶数寄存器存储余数，奇数寄存器存放商。

Now, consider the two three‑address code sequences in [Fig. 8.2] in which the
only difference in (a) and (b) is the operator in the second statement. The
shortest assembly‑code sequences for (a) and (b) are given in [Fig. 8.3].

![](Figure-8.3-Optimal-machine-code-sequences.png)

$Ri$ stands for register i. SRDA stands for Shift‑Right‑Double‑Arithmetic and
SRDA R0,32 shifts the dividend into R1 and clears R0 so all bits equal its sign
bit. L, ST, and A stand for load, store, and add, respectively. Note that the
optimal choice for the register into which a is to be loaded depends on what
will ultimately happen to t. $\square$

Strategies for register **allocation** and **assignment** are discussed in [Section 8.8].
[Section 8.10] shows that for certain classes of machines we can construct code
sequences that evaluate expressions using as few registers as possible.

## 8.1.5 Evaluation Order

The order in which computations are performed can affect the efficiency of the target code. As we shall see, some **computation orders** require fewer registers to hold intermediate results than others. However, picking a best order in the general case is a difficult [NP‑complete](https://en.wikipedia.org/wiki/NP-completeness) problem. Initially, we shall avoid the problem by generating code for the three‑address statements in the order in which they have been produced by the **intermediate code generator**. In [Chapter 10], we shall study **code scheduling** for **pipelined machines** that can execute several operations in a single **clock cycle**.
