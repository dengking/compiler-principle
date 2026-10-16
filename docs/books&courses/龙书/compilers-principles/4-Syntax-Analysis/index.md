# 4 Syntax Analysis

- [4.1 Introduction](4.1-Introduction.md)
- [4.10 Summary of Chapter 4](4.10-Summary-of-Chapter-4.md)
- [4.11 References for Chapter 4](4.11-References-for-Chapter-4.md)
- [4.2 Context-Free Grammars](4.2-Context-Free-Grammars.md)
- [4.3 Writing a Grammar](4.3-Writing-a-Grammar.md)
- [4.4 Top-Down Parsing](4.4-Top-Down-Parsing.md)
- [4.5 Bottom-Up Parsing](4.5-Bottom-Up-Parsing.md)
- [4.6 Introduction to LR Parsing: Simple LR](4.6-Introduction-to-LR-Parsing-Simple-LR.md)
- [4.7 More Powerful LR Parsers](4.7-More-Powerful-LR-Parsers.md)
- [4.8 Using Ambiguous Grammars](4.8-Using-Ambiguous-Grammars.md)
- [4.9 Parser Generators](4.9-Parser-Generators.md)

## 章首内容

Syntax Analysis
This chapter is devoted to parsing methods that are typically used in compilers.
We first present the basic concepts, then techniques suitable for hand implementation, and finally algorithms that have been used in automated tools. Since programs may contain syntactic errors, we discuss extensions of the parsing methods for recovery from common errors.
By design, every programming language has precise rules that prescribe the syntactic structure of well-formed programs. In C, for example, a program is made up of functions, a function out of declarations and statements, a statement out of expressions, and so on. The syntax of programming language constructs can be specified by context-free grammars or BNF (Backus-Naur Form) notation, introduced in Section 2.2. Grammars offer significant benefits for both language designers and compiler writers.
A grammar gives a precise, yet easy-to-understand, syntactic specification of a programming language.
From certain classes of grammars, we can construct automatically an efficient parser that determines the syntactic structure of a source program.
As a side benefit, the parser-construction process can reveal syntactic ambiguities and trouble spots that might have slipped through the initial design phase of a language.
The structure imparted to a language by a properly designed grammar is useful for translating source programs into correct object code and for detecting errors.
A grammar allows a language to be evolved or developed iteratively, by adding new constructs to perform new tasks. These new constructs can be integrated more easily into an implementation that follows the grammatical structure of the language.
