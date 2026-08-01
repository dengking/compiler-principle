# Chapter 6 Intermediate-Code Generation

> NOTE:
> 
> 一、本章主要介绍的是将SDT用于type checking、intermediate-code generation: 
> 
> Chapter 5:
> 
> "The translation techniques in this chapter will be applied in Chapter 6 to **type checking** and **intermediate-code generation**."
> 
> Chapter 6:
> 
> "We shall use the syntax-directed formalisms of Chapters 2 and 5 to specify checking and translation"

In the **analysis-synthesis model** of a compiler, the **front end** analyzes a source program and creates an intermediate representation, from which the **back end** generates target code. Ideally, details of the source language are confined(限制于) to the **front end**, and details of the target machine to the **back end**. With a suitably defined intermediate representation, a compiler for language i and machine j can then be built by combining the **front end** for language i with the **back end** for machine j. This approach to creating suite of compilers can save a considerable amount of effort: `m * n` compilers can be built by writing just `m` front ends and `n` back ends.

This chapter deals with **intermediate representations**, **static type checking**, and **intermediate code generation**. For simplicity, we assume that a **compiler front end** is organized as in Fig. 6.1, where **parsing**, **static checking**, and **intermediate-code generation** are done sequentially; sometimes they can be combined and folded into **parsing**. We shall use the syntax-directed formalisms(形式化方法) of Chapters 2 and 5 to specify checking and translation. Many of the **translation schemes** can be implemented during either bottom-up or top-down parsing, using the techniques of Chapter 5. All schemes can be implemented by creatinga **syntax tree** and then walking the tree.

![](Figure-6.1-Logical-structure-of-a-compiler-front-end.png)

## Static checking

**Static checking** includes type checking, which ensures that operators are applied to compatible operands. It also includes any **syntactic checks** that remain after parsing. For example, **static checking** assures that a break-statement in C is enclosed within a while-, for-, or switch-statement; an error is reported if such an enclosing statement does not exist.

The approach in this chapter can be used for a wide range of intermediate representations, including **syntax trees** and **three-address code**, both of which were introduced in Section 2.8. The term "three-address code" comes from instructions of the general form $x = y\ op\ z$ with three addresses: two for the operands $y$ and $z$ and one for the result $x$.

## MLIR

In the process of translating a program in a given source language into code for a given target machine, a compiler may construct a sequence of **intermediate representations**, as in Fig. 6.2. **High-level representations** are close to the source language and **low-level representations** are close to the target machine. **Syntax trees** are high level; they depict(描述) the natural **hierarchical structure** of the source program and are well suited to tasks like **static type checking**.

![](Figure-6.2-A-compiler-might-use-a-sequence-of-intermediate-representations.png)

A **low-level representation** is suitable for **machine-dependent tasks** like **register allocation** and **instruction selection**. **Three-address code** can range from high- to low-level, depending on the choice of operators. For expressions, the differences between **syntax trees** and **three-address code** are superficial, as we shall see in Section 6.2.3. For looping statements, for example, a syntax tree represents the components of a statement, whereas three-address code contains labels and jump instructions to represent the flow of control, as in machine language.

翻译: 低层中间表示适用于依赖目标机器的任务，例如寄存器分配与指令选择。三地址码的层级可高可低，取决于所选用的操作符。对于表达式而言，语法树与三地址码之间的差异只是表面上的，我们将在 6.2.3 节中看到这一点。以循环语句为例：语法树只描述语句的组成部分，而三地址码会引入标号与跳转指令，像机器语言一样刻画控制流。


The choice or design of an intermediate representation varies from compiler to compiler. An intermediate representation may either be an actual language or it may consist of internal data structures that are shared by phases of the compiler. C is a programming language, yet it is often used as an intermediate form because it is flexible, it compiles into efficient machine code, and its compilers are widely available. The original C++ compiler consisted of a front end that generated C, treating a C compiler as a back end.

# 6.1 Variants of Syntax Trees

Nodes in a syntax tree represent constructs in the source program; the children of a node represent the meaningful components of a construct. A directed acyclic graph (hereafter called a DAG) for an expression identifies the common subexpressions (subexpressions that occur more than once) of the expression. As we shall see in this section, DAG's can be constructed by using the same techniques that construct syntax trees.