# Chapter 4 Syntax Analysis

> NOTE: This chapter is mainly about algorithms of parsing or syntax analysis, I extend it to include algorithms  relevant to parsing in wikipedia which is listed in section **Wikipedia Parsing algorithms** 

This chapter is devoted to parsing methods that are typically used in compilers. We first present the basic concepts, then techniques suitable for **hand implementation**, and finally **algorithms that have been used in automated tools**. Since programs may contain syntactic errors, we discuss extensions of the parsing methods for **recovery from common errors**.

> NOTE:
> 
> 一、"Since programs may contain syntactic errors, we discuss extensions of the parsing methods for recovery from common errors."
> 
> topic: parser error handling "error recovery"
> 
> 二、hand implementation、algorithm in automated tools

By design, every programming language has precise rules that prescribe the syntactic structure of well-formed programs. In C, for example, a program is made up of functions, a function out of declarations and statements, a statement out of expressions, and so on. The syntax of programming language constructs can be specied by **context-free grammars** or **BNF (Backus-Naur Form)** notation, introduced in Section 2.2. Grammars offer signicant benefits for both **language designers** and **compiler writers**.

1、A grammar gives a precise, yet easy-to-understand, syntactic specification of a programming language. 

2、From certain classes of grammars, we can construct automatically an efficient parser that determines the syntactic structure of a source program. As a side benefit, the parser-construction process can reveal **syntactic ambiguities** and trouble spots that might have slipped through the initial design phase of a language. 

> 翻译: 对于某些类型的文法，我们可以自动构造出高效的语法分析器，以此确定源程序的语法结构。附带的好处是，语法分析器的构造过程能够暴露出**语法二义性**以及一些隐患问题，而这些问题很可能在语言最初的设计阶段被遗漏。
> 
> NOTE: 特定类型的grammar才能够自动化的构建parser，而    不是所有的grammar

3、The structure imparted(给予、赋予) to a language by a properly designed grammar is useful for translating source programs into correct **object code** and for detecting errors. 

> 翻译: 经过精心设计的文法为程序语言所赋予的结构，有助于将源程序翻译为正确的**目标代码**，同时也便于错误检测。

4、A grammar allows a language to be evolved or developed iteratively, by adding new constructs to perform new tasks. These new constructs can be integrated more easily into an implementation that follows the grammatical structure of the language.

> 翻译: 借助文法，可以通过不断添加新构造以完成新任务，对一门语言进行迭代式演化与开发。如果语言的实现遵循其文法结构，那么这些新增构造就能够更加便捷地集成进来。


