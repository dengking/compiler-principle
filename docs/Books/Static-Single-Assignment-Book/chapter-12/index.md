# Graphs and Gating Functions

Many compilers represent the input program as some form of **graph** in order to support analysis and transformation. Over time a cornucopia(层出不穷) of **program graphs** have been presented in the literature and subsequently implemented in real compilers. Many of these graphs use **SSA concepts** as the core principle of their representation, ranging from literal(字面的、直接的) translations of SSA into graph form to more abstract graphs which are implicitly in SSA form. We aim to introduce a selection of program graphs which use these SSA concepts, and examine how they may be useful to a compiler writer.

> 翻译: 许多编译器将输入程序表示为某种图结构，以此支持程序分析与变换。长久以来，文献中涌现出大量程序图，并且它们陆续在真实编译器中落地实现。这类图中有很多都以静态单赋值（SSA）思想作为表示的核心准则：既有把SSA直接转换成图形式的方案，也有隐式采用SSA形式的更抽象图结构。本章将介绍若干基于SSA思想的程序图，并探讨它们对编译器开发者的实用价值。

A well-known graph representation is the Control-Flow Graph$^\star$(CFG) which we encountered at the beginning of the book whilst being introduced to the core concept of SSA. The CFG models control flow in a program, but the graphs that we will study instead model *data flow*. This is useful as a large number of compiler optimizations are based on **data flow analysis**. In fact, all graphs that we consider in this chapter are all **data-flow graphs**.

In this chapter, we will look at a number of SSA-based graph$^\star$ representations. An introduction to each graph will be given, along with diagrams to show how sample programs look when translated into that particular graph. Additionally, we will describe the techniques that each graph was created to solve, with references to the literature for further research.

For this chapter, we assume that the reader already has familiarity with SSA (see [Chapter 1]) and the applications that it is used for.


