# Symbol table

Symbol table即符号表。
先消歧一个常见混淆:"符号表"在编译领域有两个完全不同的东西: 

| |编译器内部符号表|目标文件符号表|
|---|---|---|
|内容|名字 → 声明(类型、作用域、种类)|名字 → 地址/节/绑定|
|存在期|仅编译期,通常不落盘|落在 `.o` 的 `.symtab` / `.dynsym`|
|查看方式|编译器内部数据结构|`nm`、`readelf -s`、`objdump -t`|
本文讲的是**前者**。后者是链接器的事。
在 [[books&courses/龙书/1-Introduction/1.2-The-Structure-of-a-Compiler/index|龙书#The-Structure-of-a-Compiler]] 中提及了它，本章对它进行总结归纳。
## 龙书中涉及symbol table的章节

符号表也是一门科学，需要对它仔细研究，本书中涉及符号表的章节有：

- 1.2.1 Lexical Analysis

- 1.2.7 Symbol-Table Management

- [[books&courses/龙书/2-A-Simple-Syntax-Directed-Translator/2.7-Symbol-Tables/index|2.7 Symbol Tables]]

- [[books&courses/龙书/5-Syntax-Directed-Translation/5.2-Evaluation-Orders-for-SDD's/index|5.2.5 Semantic Rules with Controlled Side Effects]]

## What is symbol？

结合具体语言来说：

- [C++ `std` Symbol Index](http://en.cppreference.com/w/cpp/symbol_index) 

## Symbol table的重要价值

symbol table以结构化的方式存储着关于source code的信息。

compile阶段：在compile的各个阶段都需要它。

debug阶段：在debug的时候，只有读取了symbol table了，才能够灵活地设置。

## wikipedia [Symbol table](https://en.wikipedia.org/wiki/Symbol_table)

In [computer science](https://en.wikipedia.org/wiki/Computer_science), a **symbol table** is a [data structure](https://en.wikipedia.org/wiki/Data_structure) used by a language [translator](https://en.wikipedia.org/wiki/Translator) such as a [compiler](https://en.wikipedia.org/wiki/Compiler) or [interpreter](https://en.wikipedia.org/wiki/Interpreter_(computing)), where each [identifier](https://en.wikipedia.org/wiki/Identifier) (a.k.a. [symbol](https://en.wikipedia.org/wiki/Symbol_(programming))) in a program's [source code](https://en.wikipedia.org/wiki/Source_code) is associated with information relating to its declaration or appearance in the source. In other words, the entries of a symbol table store the information related to the entry's corresponding symbol.

## Symbol Table 与 Semantic Analysis

**static semantic analysis 是把"一串合法形状的 token"变成"一棵有意义的树"(annotated AST)的那一步,而 symbol table 是它的记忆。**
## Implementation

可以参考下面两种实现：

### CPython symbol table

参见工程programming-language的`Python\Language\Developer's-guide\25-Design-of-CPython's-Compiler\04-cpython-symbol-table`章节。

### Clang symbol table

参见工程programming-language的`C-family-language\C-and-C++\From-source-code-to-exec\Compile\Implementation\LLVM\Clang`。

符号表是一个 **名字 → 属性集** 的映射。属性集的典型内容:

```c++
Symbol { 
    name // 标识符(通常 interned,见下) 
    kind // 变量 / 函数 / 类型 / 常量 / 标签 / 模块 ... type // 指向类型表中的类型对象 
    scope // 所属作用域(或作用域深度) 
    linkage // internal / external / none storage // auto / static / register / thread_local 
    is_definition // 声明还是定义 
    source_location // 用于报错与调试信息 
    mangled_name // 后端/链接用 
    // 后端填充: 
    offset // 栈帧偏移或结构体内偏移 
    llvm_value // 对应的 alloca / GlobalVariable 
}
```

两个实现要点:

1. 名字要 **intern(驻留)**。把每个不同的标识符字符串只存一份，后续全部用指针比较。Clang 的 `IdentifierTable` 就干这个，产出 `IdentifierInfo*`。好处不只是省内存——字符串比较退化成指针比较，而这恰好和前面说的"LLVM 把类型 uniqued 之后类型相等变成指针比较"是同一个手法。

2. `llvm_value` 那一行是前后端的缝合点。前端在符号表里给每个局部变量挂一个 `alloca`，所有读写都翻成 `load / store`；后续由 `mem2reg` 把它提升成 SSA 值。符号表在这里把"命名的可变变量"交给 IR，IR 再把它变成"单赋值的值" ——这就是为什么前端完全不需要自己插 φ。

## Sema&symbol table
symbol table中的主要信息是由 [[front-end/static-semantic-analysis/index|Sema]] 维护生成的:
- [[front-end/static-semantic-analysis/index|Sema]]: Symbol Gathering功能;"核心载体:符号表与类型表"一节将symbol table归为Sema的输出
