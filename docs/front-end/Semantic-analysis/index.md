# Semantic analysis
Sema=Semantic analysis=语义分析
## What is semantic

- [[books&courses/龙书/2-A-Simple-Syntax-Directed-Translator/2.1-Introduction/index|dragon-book#2.1 Introduction]]:  the **semantics** of the language defines what its programs mean; that is, what each program does when it executes.
- [[front-end/syntax-VS-semantic/index]] 

## What Sema Does
While the parser builds a syntactically valid [Abstract Syntax Tree (AST)](https://axion-resources.vercel.app/semantic-analysis/orchestrator), it doesn't know if variables exist(variable declared before use), if types match, or if operations are legal. Sema performs key **checks** and **transformations**: [[1](https://stackoverflow.com/questions/11510792/is-the-semantic-analysis-step-in-clang-an-essential-part-of-the-compiler)]
- **Symbol Gathering**: Scans declarations (`let`, `fn`, `class`), maintains and update symbol tables(不同的编译器实现不同)
- **Name Resolution:** Maps every variable or function usage to its actual **declaration**, and catches undefined references. [[1](https://axion-resources.vercel.app/semantic-analysis/orchestrator)]
- **Type Checking:** Verifies that expressions, function signatures, assignments, and returns match expected types. [[1](https://axion-resources.vercel.app/semantic-analysis/orchestrator)]
- **Scope & Access Control:** Checks visibility rules (e.g., public vs. private in C++ or Rust) and ensures variables aren't used out of scope. [[1](https://clang.llvm.org/doxygen/classclang_1_1Sema.html), [2](https://axion-resources.vercel.app/semantic-analysis/orchestrator)]
- **Intermediate Representation (IR) Lowering / Evaluation:** In modern compilers like [Zig](https://mitchellh.com/zig/sema), Sema also handles language-specific compile-time evaluation (such as Zig's `comptime` or generics) and converts untyped AST/ZIR representations into typed intermediate representations like AIR. [[1](https://mitchellh.com/zig/sema), [2](https://ziggit.dev/t/build-without-semantic-analysis/8010)]

| 任务                     | 做什么                                   | 是否依赖符号表      |
| ---------------------- | ------------------------------------- | ------------ |
| 名字解析 (name resolution) | 把每个标识符引用绑定到它的声明                       | 核心           |
| 类型检查                   | 验证操作数类型相容                             | 是(查声明的类型)    |
| 类型推导                   | `auto` / `var` / Hindley–Milner       | 是(写回符号表)     |
| 隐式转换插入                 | 整型提升、`int → double`、派生类到基类            | 是            |
| 重载决议                   | 从候选集里选最佳匹配                            | 核心           |
| 常量求值                   | `constexpr`、数组维度、`case` 标签            | 是            |
| 控制流检查                  | 不可达代码、`return` 缺失、definite assignment | 否(靠 CFG)     |
| 访问控制                   | `private` / `pub` / 模块可见性             | 是            |
| 借用检查 (Rust)            | 生命周期与别名                               | 否(靠 MIR 数据流) |
注意最后两类:**控制流类检查**不依赖符号表,而依赖 CFG。Java 的 definite assignment(JLS §16,"变量使用前必须在所有路径上被赋值")本质就是一个数据流分析——它和前面讨论的"单一定义到达"是同一个家族的问题,只是跑在 AST/CFG 上而不是 SSA 上。

---

Examples in Real Compilers

- **Clang (C/C++):** Houses its **semantic analysis engine** in classes and files prefixed with `Sema` (e.g., `Sema.h`, `SemaDecl.cpp`, `SemaChecking.cpp`), which build and validate the AST simultaneously or via **multi-pass checks**. [[1](https://stackoverflow.com/questions/11510792/is-the-semantic-analysis-step-in-clang-an-essential-part-of-the-compiler), [2](https://clang.llvm.org/doxygen/classclang_1_1Sema.html)]
- **Zig:** Features `src/Sema.zig`, a central stage that interprets untyped ZIR (Zig Intermediate Representation) to evaluate `comptime` code and emit typed AIR. [[1](https://mitchellh.com/zig/sema), [2](https://ziggit.dev/t/build-without-semantic-analysis/8010)]
- **Custom/Monolithic Compilers:** Often structured as a multi-pass orchestrator that walks the AST to resolve symbols first, type-check second, and perform flow/borrow checks third. [[1](https://axion-resources.vercel.app/semantic-analysis/orchestrator)]


## wikipedia [Semantic analysis (compilers)](https://en.wikipedia.org/wiki/Semantic_analysis_(compilers))

**Semantic analysis** or **context sensitive analysis** is a process in [compiler](https://en.wikipedia.org/wiki/Compiler) construction, usually after [parsing](https://en.wikipedia.org/wiki/Parsing), to gather necessary semantic information from the [source code](https://en.wikipedia.org/wiki/Source_code).[[1\]](https://en.wikipedia.org/wiki/Semantic_analysis_(compilers)#cite_note-WilhelmSeidl2013-1) It usually includes [type checking](https://en.wikipedia.org/wiki/Type_checking), or makes sure a variable is declared before use which is impossible to describe in the [extended Backus–Naur form](https://en.wikipedia.org/wiki/Extended_Backus–Naur_form) and thus not easily detected during parsing.
