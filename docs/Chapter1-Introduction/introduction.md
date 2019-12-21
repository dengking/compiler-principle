[TOC]

# Introduction

How long have you been programming? Have you ever wondered what a programming language is? 

There are many ways to answer this question, here I will try to answer this question from some different perspectives.

## From  [formal language](https://en.wikipedia.org/wiki/Formal_language)

A **programming language** is a [formal language](https://en.wikipedia.org/wiki/Formal_language),  so it is equipped with

- [alphabet](https://en.wikipedia.org/wiki/Alphabet_(computer_science)) 
- [words](https://en.wikipedia.org/wiki/String_(computer_science)) and [lexical grammar](https://en.wikipedia.org/wiki/Lexical_grammar) to defining the [syntax](https://en.wikipedia.org/wiki/Syntax_(programming_languages)) of [tokens](https://en.wikipedia.org/wiki/Token_(parser)). 

- [Syntax](https://en.wikipedia.org/wiki/Syntax) and [formal grammar](https://en.wikipedia.org/wiki/Formal_grammar) to describe its [syntax](https://en.wikipedia.org/wiki/Syntax)
- [semantics](https://en.wikipedia.org/wiki/Semantics#Computer_science)



## From the perspectives of a compiler front end



|                                                              |                                                              |                                                              |                                                              |                                                              |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| [alphabet](https://en.wikipedia.org/wiki/Alphabet_(computer_science)) |                                                              |                                                              |                                                              |                                                              |
| [Lexical grammar](https://en.wikipedia.org/wiki/Lexical_grammar) | [Lexical analysis](https://en.wikipedia.org/wiki/Lexical_analysis) | [regular expressions](https://en.wikipedia.org/wiki/Regular_expression) | [Finite-state machine](https://en.wikipedia.org/wiki/Finite-state_machine) | Scanner generators, for example [Lex (software)](https://en.wikipedia.org/wiki/Lex_(software)) |
| [Syntax (programming languages)](https://en.wikipedia.org/wiki/Syntax_(programming_languages)) | [syntax analysis](https://en.wikipedia.org/wiki/Parsing)     | [Context-free grammar](https://en.wikipedia.org/wiki/Context-free_grammar) | [parse tree](https://en.wikipedia.org/wiki/Parse_tree), [abstract syntax tree](https://en.wikipedia.org/wiki/Abstract_syntax_tree) | Parser generators, for example [Yacc](https://en.wikipedia.org/wiki/Yacc) |
| [Semantics (computer science)](https://en.wikipedia.org/wiki/Semantics_(computer_science)) | [Semantic analysis (compilers)](https://en.wikipedia.org/wiki/Semantic_analysis_(compilers)) |                                                              |                                                              |                                                              |



[Lexical grammar](https://en.wikipedia.org/wiki/Lexical_grammar), [syntax ](https://en.wikipedia.org/wiki/Syntax_(programming_languages)) and [semantics ](https://en.wikipedia.org/wiki/Semantics_(computer_science)) define a programming language,.Only when specifying [lexical grammar](https://en.wikipedia.org/wiki/Lexical_grammar), [syntax ](https://en.wikipedia.org/wiki/Syntax_(programming_languages)) and [semantics ](https://en.wikipedia.org/wiki/Semantics_(computer_science)) can the **compiler** understand what programmer have written and translate the language correctly. 







This book is about how to design and implement compilers. We shall discover that a few basic ideas can be used to construct translators for a wide variety of languages and machines. Besides compilers, the **principles** and **techniques** for compiler design are applicable to so many other domains that they
are likely to b e reused many times in the career of a computer scientist. The study of compiler writing touches up on programming languages, machine architecture, language theory, algorithms, and software engineering.

> NOTE: 在我的编程生涯中，曾多次收到作者在本书中所描述的principle和technique的启发而解决了实际问题。

