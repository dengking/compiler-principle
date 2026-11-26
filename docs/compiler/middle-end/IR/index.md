# IR

CFG IR

Sea of nodes

SSA=static-single-assignment-form

## CFG IR VS Sea of nodes

wikipedia [Sea of nodes](https://en.wikipedia.org/wiki/Sea_of_nodes)

> It is used as an [intermediate representation (IR)](https://en.wikipedia.org/wiki/Intermediate_representation "Intermediate representation") in the [HotSpot](https://en.wikipedia.org/wiki/HotSpot_\(virtual_machine\) "HotSpot (virtual machine)") JVM,[[5]](https://en.wikipedia.org/wiki/Sea_of_nodes#cite_note-Demange_2018-5): 163  [LibFirm](https://en.wikipedia.org/wiki/LibFirm?action=edit&redlink=1 "LibFirm (page does not exist)"),[[5]](https://en.wikipedia.org/wiki/Sea_of_nodes#cite_note-Demange_2018-5): 163  and [GraalVM](https://en.wikipedia.org/wiki/GraalVM "GraalVM").[[5]](https://en.wikipedia.org/wiki/Sea_of_nodes#cite_note-Demange_2018-5): 163 [[8]](https://en.wikipedia.org/wiki/Sea_of_nodes#cite_note-Webb_2021-8): 2 [[11]](https://en.wikipedia.org/wiki/Sea_of_nodes#cite_note-11) It was also used by [V8](https://en.wikipedia.org/wiki/V8_\(JavaScript_engine\) "V8 (JavaScript engine)")'s TurboFan [JIT compiler](https://en.wikipedia.org/wiki/Just-in-time_compilation "Just-in-time compilation"), but in 2022 they decided that it was poorly suited for [JavaScript](https://en.wikipedia.org/wiki/JavaScript "JavaScript")'s [dynamicity](https://en.wikipedia.org/wiki/Dynamic_programming_language "Dynamic programming language"), thereby making development and debugging too difficult, and so they decided to develop Turboshaft as a replacement, going back to using a CFG IR.





# 

## Wikipedia [Intermediate language](https://infogalactic.com/info/Intermediate_language)

In [computer science](https://infogalactic.com/info/Computer_science), an **intermediate language** is the language of an [abstract machine](https://infogalactic.com/info/Abstract_machine) designed to aid in the analysis of [computer programs](https://infogalactic.com/info/Computer_program). 

> NOTE: 面向计算的

The term comes from their use in [compilers](https://infogalactic.com/info/Compiler), where the source code of a program is translated into a form more suitable for code-improving transformations before being used to generate [object](https://infogalactic.com/info/Object_file) or [machine](https://infogalactic.com/info/Machine_language) code for a target machine. 

A popular format for intermediate languages is [three-address code](https://infogalactic.com/info/Three-address_code).

The term is also used to refer to languages used as **intermediates** by some [high-level programming languages](https://infogalactic.com/info/High-level_programming_language) which do not output object or machine code themselves, but output the **intermediate language** only. 

This is usually done to ease the process of [optimization](https://infogalactic.com/info/Optimization_(computer_science)) or to increase [portability](https://infogalactic.com/info/Porting) by using an intermediate language that has compilers for many [processors](https://infogalactic.com/info/Central_processing_unit) and [operating systems](https://infogalactic.com/info/Operating_systems), such as [C](https://infogalactic.com/info/C_(programming_language)). Languages used for this fall in complexity between high-level languages and [low-level](https://infogalactic.com/info/Low-level_programming_language) languages, such as [assembly languages](https://infogalactic.com/info/Assembly_language).

### Intermediate representation

A canonical example is found in most modern [compilers](https://infogalactic.com/info/Compilers), where the linear human-readable text representing a program is transformed into an intermediate [graph](https://infogalactic.com/info/Graph_(data_structure)) data structure that allows [flow analysis](https://infogalactic.com/info/Flow_analysis) and re-arrangements before starting to create the list of actual CPU instructions that will do the work. Use of an Intermediate representation allows compiler systems like [GNU GCC](https://infogalactic.com/info/GNU_Compiler_Collection) and [LLVM](https://infogalactic.com/info/LLVM) to be targeted by many different source languages, and support generation for many different target architectures.

## Case study

> NOTE: 源自 Wikipedia [Intermediate language](https://infogalactic.com/info/Intermediate_language) 。主要是在compiler中应用。

### [Three-address code](https://infogalactic.com/info/Three-address_code)

> NOTE: 最最流行的

### C as intermediate language

Though not explicitly designed as an intermediate language, [C](https://infogalactic.com/info/C_(programming_language))'s nature as an abstraction of assembly and its ubiquity as the de facto [system language](https://infogalactic.com/info/System_programming_language) in [Unix-like](https://infogalactic.com/info/Unix-like) and other operating systems has made it a popular intermediate language: [Eiffel](https://infogalactic.com/info/Eiffel_(programming_language)), [Sather](https://infogalactic.com/info/Sather), [Esterel](https://infogalactic.com/info/Esterel), some [dialects](https://infogalactic.com/info/Programming_language_dialect) of [Lisp](https://infogalactic.com/info/Lisp_(programming_language)) ([Lush](https://infogalactic.com/w/index.php?title=Lush_(programming_language)&action=edit&redlink=1), [Gambit](https://infogalactic.com/info/Gambit_(Scheme_implementation))), [Haskell](https://infogalactic.com/info/Haskell_(programming_language)) ([Glasgow Haskell Compiler](https://infogalactic.com/info/Glasgow_Haskell_Compiler)), [Squeak](https://infogalactic.com/info/Squeak)'s Smalltalk-subset Slang, [Cython](https://infogalactic.com/info/Cython), [Seed7](https://infogalactic.com/info/Seed7), [SystemTap](https://infogalactic.com/info/SystemTap), [Vala](https://infogalactic.com/info/Vala_(programming_language)), and others make use of C as an intermediate language. 

### Language for VM

Any language targeting a [virtual machine](https://infogalactic.com/info/Virtual_machine) can be considered an intermediate language:

- [Java bytecode](https://infogalactic.com/info/Java_bytecode)
- Microsoft's [Common Intermediate Language](https://infogalactic.com/info/Common_Intermediate_Language) is an intermediate language designed to be shared by all compilers for the [.NET Framework](https://infogalactic.com/info/.NET_Framework), before static or dynamic compilation to machine code.
- While most intermediate languages are designed to support statically typed languages, the [Parrot intermediate representation](https://infogalactic.com/info/Parrot_intermediate_representation) is designed to support dynamically typed languages—initially Perl and Python.
- [TIMI](https://infogalactic.com/info/IBM_System_i#Instruction_set) is a high level that targets the IBM System i platform.

> NOTE: 下面是一些补充
> 
> Python bytecode 
> 
> sqlite bytecode

### GCC IR

The [GNU Compiler Collection](https://infogalactic.com/info/GNU_Compiler_Collection) (GCC) uses several intermediate languages internally to simplify portability and [cross-compilation](https://infogalactic.com/info/Cross-compilation). Among these languages are

- the historical [Register Transfer Language](https://infogalactic.com/info/Register_Transfer_Language) (RTL)
- the tree language [GENERIC](https://infogalactic.com/info/GNU_Compiler_Collection#GENERIC_and_GIMPLE)
- the [SSA](https://infogalactic.com/info/Static_single_assignment_form)-based [GIMPLE](https://infogalactic.com/info/GIMPLE).
- [Standard Portable Intermediate Representation](https://infogalactic.com/info/Standard_Portable_Intermediate_Representation) SPIR/SPIR-V
- [LLVM Intermediate Representation](https://infogalactic.com/info/LLVM_Intermediate_Representation)
- [HSA Intermediate Layer](https://infogalactic.com/info/HSA_Intermediate_Layer)

### LLVM IR

The [LLVM](https://infogalactic.com/info/LLVM) compiler framework is based on the [LLVM IR](https://infogalactic.com/info/LLVM#Intermediate_Representation) intermediate language, which has been productized by Apple as "bitcode".[[1\]](https://infogalactic.com/info/Intermediate_language#cite_note-Apple.27s_bitcode-1)[[2\]](https://infogalactic.com/info/Intermediate_language#cite_note-LLVM_Bitcode-2)

### Deep learning IR

参见工程machine-learning的`Theory\Deep-learning\Guide\Compiler`章节。
