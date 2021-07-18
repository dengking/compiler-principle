# Abstract syntax tree

## wikipedia [Abstract syntax tree](https://en.wikipedia.org/wiki/Abstract_syntax_tree)

In [computer science](https://en.wikipedia.org/wiki/Computer_science), an **abstract syntax tree** (**AST**), or just **syntax tree**, is a [tree](https://en.wikipedia.org/wiki/Directed_tree) representation of the [abstract syntactic](https://en.wikipedia.org/wiki/Abstract_syntax) structure of [source code](https://en.wikipedia.org/wiki/Source_code) written in a [programming language](https://en.wikipedia.org/wiki/Programming_language). Each node of the tree denotes a construct occurring in the source code.

> NOTE : 表示源代码的抽象语法结构，树中的每个节点都表示源代码中的一个construct。

The syntax is "abstract" in the sense that it does not represent every **detail** appearing in the real **syntax**, but rather just the **structural or content-related details**. For instance, grouping [parentheses](https://en.wikipedia.org/wiki/Bracket#Parentheses) are implicit in the **tree structure**, so these do not have to be represented as separate nodes. Likewise, a syntactic construct like an if-condition-then expression may be denoted by means of a single node with three branches.

This distinguishes **abstract syntax trees** from **concrete syntax trees**, traditionally designated [parse trees](https://en.wikipedia.org/wiki/Parse_tree). Parse trees are typically **built** by a [parser](https://en.wikipedia.org/wiki/Parser) during the source code translation and [compiling](https://en.wikipedia.org/wiki/Compiler) process. Once built, additional information is added to the AST by means of subsequent processing, e.g., [contextual analysis](https://en.wikipedia.org/wiki/Semantic_analysis_(compilers)).

> NOTE: 
>
> parse tree和abstract syntax tree的构建

Abstract syntax trees are also used in [program analysis](https://en.wikipedia.org/wiki/Program_analysis) and [program transformation](https://en.wikipedia.org/wiki/Program_transformation) systems.

[![img](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Abstract_syntax_tree_for_Euclidean_algorithm.svg/400px-Abstract_syntax_tree_for_Euclidean_algorithm.svg.png)](https://en.wikipedia.org/wiki/File:Abstract_syntax_tree_for_Euclidean_algorithm.svg)

An abstract syntax tree for the following code for the [Euclidean algorithm](https://en.wikipedia.org/wiki/Euclidean_algorithm)

```pseudocode
while b ≠ 0
  if a > b
    a := a − b
  else
    b := b − a
return a
```



### Application in compilers

**Abstract syntax trees** are [data structures](https://en.wikipedia.org/wiki/Data_structures) widely used in [compilers](https://en.wikipedia.org/wiki/Compilers) to represent the structure of program code. An AST is usually the result of the [syntax analysis](https://en.wikipedia.org/wiki/Syntax_analysis) phase of a compiler. It often serves as an intermediate representation of the program through several stages that the compiler requires, and has a strong impact on the final output of the compiler. 

### Motivation

An AST has several properties that aid the further steps of the compilation process:

- An AST can be edited and enhanced with information such as properties and annotations for every element it contains. Such editing and annotation is impossible with the source code of a program, since it would imply changing it.
- Compared to the [source code](https://en.wikipedia.org/wiki/Source_code), an AST does not include inessential punctuation and delimiters (braces, semicolons, parentheses, etc.).
- An AST usually contains extra information about the program, due to the consecutive stages of analysis by the compiler. For example, it may store the position of each element in the source code, allowing the compiler to print useful **error messages**.

ASTs are needed because of the inherent nature of programming languages and their documentation. Languages are often ambiguous by nature. In order to avoid this ambiguity, programming languages are often specified as a [context-free grammar](https://en.wikipedia.org/wiki/Context-free_grammar) (CFG). However, there are often aspects of programming languages that a CFG can't express, but are part of the language and are documented in its specification. These are details that require a context to determine their validity and behaviour. For example, if a language allows new types to be declared, a CFG cannot predict the names of such types nor the way in which they should be used. Even if a language has a predefined set of types, enforcing proper usage usually requires some context. Another example is [duck typing](https://en.wikipedia.org/wiki/Duck_typing), where the type of an element can change depending on context. [Operator overloading](https://en.wikipedia.org/wiki/Operator_overloading) is yet another case where correct usage and final function are determined based on the context. Java provides an excellent example, where the '+' operator is both numerical addition and concatenation of strings.

Although there are other [data structures](https://en.wikipedia.org/wiki/Data_structure) involved in the inner workings of a compiler, the AST performs a unique function. During the first stage, the [syntax analysis](https://en.wikipedia.org/wiki/Syntax_analysis) stage, a compiler produces a parse tree. This parse tree can be used to perform almost all functions of a compiler by means of s**yntax-directed translation**. Although this method can lead to a more efficient compiler, it goes against the software engineering principles of writing and maintaining programs[*[citation needed](https://en.wikipedia.org/wiki/Wikipedia:Citation_needed)*]. Another advantage that the AST has over a parse tree is the size, particularly the smaller height of the AST and the smaller number of elements.

### Design

The design of an AST is often closely linked with the design of a compiler and its expected features.

Core requirements include the following:

- Variable types must be preserved, as well as the location of each declaration in source code.
- The order of executable statements must be explicitly represented and well defined.
- Left and right components of binary operations must be stored and correctly identified.
- Identifiers and their assigned values must be stored for assignment statements.

These requirements can be used to design the data structure for the AST.

Some operations will always require two elements, such as the two terms for addition. However, some language constructs require an arbitrarily large number of children, such as argument lists passed to programs from the [command shell](https://en.wikipedia.org/wiki/Command_shell). As a result, an AST used to represent code written in such a language has to also be flexible enough to allow for quick addition of an unknown quantity of children.

To support compiler verification it should be possible to unparse an AST into source code form. The source code produced should be sufficiently similar to the original in appearance and identical in execution, upon recompilation.

### Design patterns

Due to the complexity of the requirements for an AST and the overall complexity of a compiler, it is beneficial to apply sound software development principles. One of these is to use proven design patterns to enhance modularity and ease of development.

Different operations don't necessarily have different types, so it is important to have a sound node class hierarchy. This is crucial in the creation and the modification of the AST as the compiler progresses.

Because the compiler traverses the tree several times to determine syntactic correctness, it is important to make traversing the tree a simple operation. The compiler executes a specific set of operations, depending on the type of each node, upon reaching it, so it often makes sense to use the [visitor pattern](https://en.wikipedia.org/wiki/Visitor_pattern).

### Usage

The AST is used intensively during [semantic analysis](https://en.wikipedia.org/wiki/Semantic_analysis_(compilers)), where the compiler checks for correct usage of the elements of the program and the language. The compiler also generates [symbol tables](https://en.wikipedia.org/wiki/Symbol_table) based on the AST during semantic analysis. A complete traversal of the tree allows verification of the correctness of the program.

After verifying correctness, the AST serves as the base for code generation. The AST is often used to generate an intermediate representation (IR), sometimes called an [intermediate language](https://en.wikipedia.org/wiki/Intermediate_language), for the code generation.

