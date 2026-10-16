# A: A Complete Front End

- [A.1 The Source Language](A.1-The-Source-Language.md)
- [A.2 Main](A.2-Main.md)
- [A.3 Lexical Analyzer](A.3-Lexical-Analyzer.md)
- [A.4 Symbol Tables and Types](A.4-Symbol-Tables-and-Types.md)
- [A.5 Intermediate Code for Expressions](A.5-Intermediate-Code-for-Expressions.md)
- [A.6 Jumping Code for Boolean Expressions](A.6-Jumping-Code-for-Boolean-Expressions.md)
- [A.7 Intermediate Code for Statements](A.7-Intermediate-Code-for-Statements.md)
- [A.8 Parser](A.8-Parser.md)
- [A.9 Creating the Front End](A.9-Creating-the-Front-End.md)

## 章首内容

A Complete Front End
The complete compiler front end in this appendix is based on the informally described simple compiler of Sections 2.5-2.8. The main difference from Chapter 2 is that the front end generates jumping code for boolean expressions, as in Section 6.6. We begin with the syntax of the source language, described by a grammar that needs to be adapted for top-down parsing.
The Java code for the translator consists of five packages: main, lexer, symbols, parser, and inter. Package inter contains classes for the language constructs in the abstract syntax. Since the code for the parser interacts with the rest of the packages, it will be discussed last. Each package is stored as a separate directory with a file per class.
Going into the parser, the source program consists of a stream of tokens, so object-orientation has little to do with the code for the parser. Coming out of the parser, the source program consists of a syntax tree, with constructs or nodes implemented as objects. These objects deal with all of the following: construct a syntax-tree node, check types, and generate three-address intermediate code
(see package inter).
