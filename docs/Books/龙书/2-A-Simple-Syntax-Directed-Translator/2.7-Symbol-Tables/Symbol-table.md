# Symbol table

Symbol table即符号表，在`Chapter-1-Introduction\1.2-The-Structure-of-a-Compiler.md`中提及了它，本章对它进行专门总结。

## 龙书中涉及symbol table的章节

符号表也是一门科学，需要对它仔细研究，本书中涉及符号表的章节有：

- 1.2.1 Lexical Analysis

- 1.2.7 Symbol-Table Management
- 2.7 Symbol Tables



## What is symbol？

结合具体语言来说：

- [C++ `std` Symbol Index](http://en.cppreference.com/w/cpp/symbol_index) 



## symbol table的重要价值

symbol table以结构化的方式存储着关于source code的信息。

compile阶段：在compile的各个阶段都需要它。

debug阶段：在debug的时候，只有读取了symbol table了，才能够灵活地设置。



## wikipedia [Symbol table](https://en.wikipedia.org/wiki/Symbol_table)

In [computer science](https://en.wikipedia.org/wiki/Computer_science), a **symbol table** is a [data structure](https://en.wikipedia.org/wiki/Data_structure) used by a language [translator](https://en.wikipedia.org/wiki/Translator) such as a [compiler](https://en.wikipedia.org/wiki/Compiler) or [interpreter](https://en.wikipedia.org/wiki/Interpreter_(computing)), where each [identifier](https://en.wikipedia.org/wiki/Identifier) (a.k.a. [symbol](https://en.wikipedia.org/wiki/Symbol_(programming))) in a program's [source code](https://en.wikipedia.org/wiki/Source_code) is associated with information relating to its declaration or appearance in the source. In other words, the entries of a symbol table store the information related to the entry's corresponding symbol.



## Implementation

可以参考下面两种实现：

### CPython symbol table

参见工程programming-language的`Python\Language\Developer's-guide\25-Design-of-CPython's-Compiler\04-cpython-symbol-table`章节。

### Clang symbol table

参见工程programming-language的`C-family-language\C-and-C++\From-source-code-to-exec\Compile\Implementation\LLVM\Clang`。