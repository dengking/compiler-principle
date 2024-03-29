# 1.5 Applications of Compiler Technology

Compiler design is not only about compilers, and many people use the technology learned by studying compilers in school, yet have never, strictly speaking, written (even part of ) a compiler for a major programming language. Compiler technology has other important uses as well. Additionally, compiler design impacts several other areas of computer science. In this section, we review the most important interactions and applications of the technology.

## 1.5.1 Implementation of High-Level Programming Languages

A high-level programming language defines a programming abstraction: the programmer expresses an algorithm using the language, and the compiler must translate that program to the target language.

## 1.5.2 Optimizations for Computer Architectures

The rapid evolution of computer architectures has also led to an insatiable demand for new compiler technology. Almost all high-performance systems take advantage of the same two basic techniques: *parallelism* and *memory hierarchies*. 

**Parallelism** can be found at several levels: at the instruction level, where multiple operations are executed simultaneously and at the processor level, where different threads of the same application are run on different processors. 

**Memory hierarchies** are a response to the basic limitation that we can build very fast storage or very large storage, but not storage that is both fast and large.

## 1.5.3 Design of New Computer Architectures

In the early days of computer architecture design, compilers were developed after the machines were built. That has changed. Since programming in high-level languages is the norm, the performance of a computer system is determined not by its raw speed but also by how well compilers can exploit its features. Thus, in modern computer architecture development, compilers are developed in the processor-design stage, and compiled code, running on simulators, is used to evaluate the proposed architectural features.

## 1.5.4 Program Translations

While we normally think of compiling as a translation from a high-level language to the machine level, the same technology can be applied to translate between different kinds of languages. The following are some of the important applications of program-translation techniques.



## 1.5.5 Software Productivity Tools

Programs are arguably the most complicated engineering artifacts ever produced; they consist of many many details, every one of which must be correct before the program will work completely. As a result, errors are rampant in programs; errors may crash a system, produce wrong results, render a system
vulnerable to security attacks, or even lead to catastrophic failures in critical systems. Testing is the primary technique for locating errors in programs.

An interesting and promising complementary approach is to use [data-flow analysis](https://en.wikipedia.org/wiki/Data-flow_analysis) to locate errors statically (that is, before the program is run). Data-flow analysis can find errors along all the possible execution paths, and not just those exercised by the input data sets, as in the case of program testing.
Many of the data-flow-analysis techniques, originally developed for **compiler optimizations**, can be used to create tools that assist programmers in their software engineering tasks.

The problem of finding all program errors is undecidable. A data-flow analysis may be designed to warn the programmers of all possible statements with a particular category of errors. But if most of these warnings are false alarms, users will not use the tool. Thus, practical error detectors are often neither sound nor complete. That is, they may not find all the errors in the program, and not all errors reported are guaranteed to be real errors. Nonetheless, various static analyses have been developed and shown to be effective in finding errors, such as dereferencing null or freed pointers, in real programs. The fact that error detectors may be unsound makes them significantly different from compiler optimizations. Optimizers must be conservative and cannot alter the semantics of the program under any circumstances.

In the balance of this section, we shall mention several ways in which program analysis, building up on techniques originally develop ed to optimize code in compilers, have improved software productivity. Of special importance are techniques that detect statically when a program might have a security vulnerability.

### Type Checking



### Bounds Checking



### Memory-Management Tools

Garbage collection is another excellent example of the tradeoff between efficiency and a combination of ease of programming and software reliability. Automatic memory management obliterates all memory-management errors (e.g., "memory leaks"), which are a major source of problems in C and `C++` programs. Various tools have been developed to help programmers find memory management errors. For example, [Purify](https://en.wikipedia.org/wiki/PurifyPlus) is a widely used tool that dynamically catches memory management errors as they occur. Tools that help identify some of these problems statically have also been developed.



> NOTE: 现代IDE一般都会集成很多software productivity tools，比如在[pycharm](https://www.jetbrains.com/pycharm/)中。
>
> See also：
>
> - [List of tools for static code analysis](https://en.wikipedia.org/wiki/List_of_tools_for_static_code_analysis)
> - [Source Code Analysis Tools](https://owasp.org/www-community/Source_Code_Analysis_Tools)
> - code inspection tools
>
> 在学习了本书中的内容后，其实读者可以大致推测这些工具的原理了。
>
> 显然这些都是帮助[Software quality assurance](https://en.wikipedia.org/wiki/Software_quality_assurance)的有效工具。