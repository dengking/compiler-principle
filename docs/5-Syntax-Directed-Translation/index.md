# Chapter 5 Syntax-Directed Translation



## What is syntax-directed translation



二、zhihu [语法制导翻译是干什么的？](https://www.zhihu.com/question/27594539/answer/43441044) 

三、zhihu [C++代码与AST compiler](https://zhuanlan.zhihu.com/p/599569303)

四、zhihu [读书笔记 | 编译原理 ——一个简单的语法制导翻译器（上） - Ouyz的文章 - 知乎](https://zhuanlan.zhihu.com/p/428054996) 



### wikipedia [Syntax-directed translation](https://en.wikipedia.org/wiki/Syntax-directed_translation)

**Syntax-directed translation** refers to a method of [compiler](https://en.wikipedia.org/wiki/Compiler) implementation where the source language translation is completely driven by the [parser](https://en.wikipedia.org/wiki/Parser).

A common method of syntax-directed translation is translating a string into a sequence of actions by attaching one such action to each rule of a [grammar](https://en.wikipedia.org/wiki/Grammar).[[1\]](https://en.wikipedia.org/wiki/Syntax-directed_translation#cite_note-Gurari-1) Thus, parsing a string of the grammar produces a sequence of rule applications. SDT provides a simple way to attach [semantics](https://en.wikipedia.org/wiki/Semantics) to any such [syntax](https://en.wikipedia.org/wiki/Syntax).

> NOTE:
>
> semantic action

#### Overview

Syntax-directed translation fundamentally works by adding actions to the productions in a [context-free grammar](https://en.wikipedia.org/wiki/Context-free_grammar), resulting in a Syntax-Directed Definition (SDD).[[2\]](https://en.wikipedia.org/wiki/Syntax-directed_translation#cite_note-Alfred-2) Actions are steps or procedures that will be carried out when that production is used in a derivation. A grammar specification embedded with actions to be performed is called a *syntax-directed translation scheme*[[1\]](https://en.wikipedia.org/wiki/Syntax-directed_translation#cite_note-Gurari-1) (sometimes simply called a 'translation scheme'.)

> NOTE:
>
> 一、关于SDD，在`5.1-Syntax-Directed-Definitions`中进行了介绍

Each symbol in the grammar can have an *attribute*, which is a value that is to be associated with the symbol. Common attributes could include a variable type, the value of an expression, etc. Given a symbol *X*, with an attribute *t*, that attribute is referred to as *X*.*t*

Thus, given actions and attributes, the grammar can be used for translating strings from its language by applying the actions and carrying information through each symbol's attribute.



## 正文

This chapter develops the theme of Section 2.3: the translation of languages guided by **context-free grammars**. The translation techniques in this chapter will be applied in Chapter 6 to **type checking** and **intermediate-code generation**. The techniques are also useful for implementing little languages for specialized tasks; this chapter includes an example from typesetting.

We associate information with a language construct by attaching **attributes** to the grammar symbol(s) representing the construct, as discussed in Section 2.3.2. A **syntax-directed definition** specifies the values of **attributes** by associating **semantic rules** with the grammar productions. For example, an infix-to-postfix translator might have a production and rule

![](./5.1.jpg)

From Section 2.3.5, a syntax-directed translation scheme embeds program fragments called **semantic actions** within production bodies, as in

![](./5.2.jpg)

By convention, semantic actions are enclosed within curly braces.

Between the two notations, syntax-directed definitions can be more readable, and hence more useful for specifications. However, translation schemes can be more efficient, and hence more useful for implementations.

|                                    |      |                 |
| ---------------------------------- | ---- | --------------- |
| syntax-directed definition         | SDD  | semantic rule   |
| syntax-directed translation scheme | SDT  | semantic action |

The most general approach to **syntax-directed translation** is to construct a **parse tree** or a **syntax tree**, and then to compute the values of attributes at the nodes of the tree by visiting the nodes of the tree. In many cases, translation can be done during parsing, without building an explicit tree. We shall therefore
study a class of syntax-directed translations called "L-attributed translations" (L for left-to-right), which encompass virtually all translations that can be performed during parsing. We also study a smaller class, called "S-attributed translations" (S for synthesized), which can be performed easily in connection with a bottom-up parse.



## Application



### Semantic analysis

wikipedia的[Syntax-directed translation](https://en.wikipedia.org/wiki/Syntax-directed_translation)非常直接简明的描述了Syntax-directed translation的功能:

> **Syntax-directed translation** refers to a method of [compiler](https://en.wikipedia.org/wiki/Compiler) implementation where the source language translation is completely driven by the [parser](https://en.wikipedia.org/wiki/Parser).
>
> A common method of syntax-directed translation is translating a string into a sequence of actions by attaching one such action to each rule of a [grammar](https://en.wikipedia.org/wiki/Grammar). Thus, parsing a string of the grammar produces a sequence of rule applications. SDT provides a simple way to attach [semantics](https://en.wikipedia.org/wiki/Semantics) to any such [syntax](https://en.wikipedia.org/wiki/Syntax).

上面这段话已经将SDT和[semantics](https://en.wikipedia.org/wiki/Semantics)关联到一起了，其实SDT是[Semantic analysis](https://en.wikipedia.org/wiki/Semantic_analysis_(compilers))的一种实现方式，正如wikipedia的[compiler](https://en.wikipedia.org/wiki/Compiler)中所描述的：

> A compiler is likely to perform many or all of the following operations: [preprocessing](https://en.wikipedia.org/wiki/Preprocessor), [lexical analysis](https://en.wikipedia.org/wiki/Lexical_analysis), [parsing](https://en.wikipedia.org/wiki/Parsing), [semantic analysis](https://en.wikipedia.org/wiki/Semantic_analysis_(compilers)) ([syntax-directed translation](https://en.wikipedia.org/wiki/Syntax-directed_translation)), conversion of input programs to an [intermediate representation](https://en.wikipedia.org/wiki/Intermediate_representation), [code optimization](https://en.wikipedia.org/wiki/Code_optimization) and [code generation](https://en.wikipedia.org/wiki/Code_generation_(compiler)). 

