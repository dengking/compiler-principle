parse tree和syntax tree在本书中多次出现，有必要对它们进行对比一下。

介绍parse tree的主要章节有：

- 2.2.3 Parse Trees
- 2.4 Parsing
- 2.9 Summary of Chapter 2
- Chapter 4 Syntax Analysis
- Chapter 5 Syntax-Directed Translation



本书中区分parse tree和syntax tree的章节有：

- 2.5.1 Abstract and Concrete Syntax

  > Abstract syntax trees, or simply *syntax trees*, resemble parse trees to an extent. However, in the **syntax tree**, **interior nodes** represent **programming constructs** while in the **parse tree**, the **interior nodes** represent **nonterminals**. Many nonterminals of a grammar represent programming constructs, but others are "helpers" of one sort of another, such as those representing terms, factors, or other variations of expressions. In the syntax tree, these helpers typically are not needed and are hence dropped. To emphasize the contrast, a **parse tree** is
  > sometimes called a *concrete syntax tree*, and the underlying grammar is called a concrete syntax for the language.



介绍syntax tree的章节有：

- 2.1 Introduction
- 2.8.2 Construction of Syntax Trees
- 2.8.4 Three-Address Code

- 5.3.1 Construction of Syntax Trees
- 6.1 Variants of Syntax Trees

