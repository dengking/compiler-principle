# Static semantics 与语义分析(Sema)

> 本文是 [[3-layers-of-a-language-specification/index|语言规范的三层]] 中的第二层。三层的总览与横向对比见总纲;前后两层见 [[front-end/grammar/index|grammar]] 与 [[3-layers-of-a-language-specification/dynamic-semantic/index|dynamic-semantic]]。
>
> Sema = Semantic analysis = 语义分析。本文讨论的是 **static** semantic analysis。

---

## 一、什么是静态语义

先看"语义"本身:

- [[books&courses/龙书/2-A-Simple-Syntax-Directed-Translator/2.1-Introduction/index|dragon-book#2.1 Introduction]]: the **semantics** of the language defines what its programs mean; that is, what each program does when it executes.
- 另见 [[3-layers-of-a-language-specification/index|语言规范的三层]]。

龙书这句定义说的其实是**动态语义**。静态语义是夹在语法与动态语义之间的那一层:

> **静态语义 = "语法之外、运行之前"的全部规则,即编译期可判定的良构性(well-formedness)。**

它的使命是**拒绝**:在编译期回答一个布尔问题——这个程序该不该被接受?

```c
int x = "hello";   // 形状合法,类型不相容 → 拒绝
int x = y;         // 形状合法,y 未声明   → 拒绝
```

维基百科 [Semantic analysis (compilers)](https://en.wikipedia.org/wiki/Semantic_analysis_(compilers)) 给出了它在编译器构造里的定位:

> **Semantic analysis** or **context sensitive analysis** is a process in [compiler](https://en.wikipedia.org/wiki/Compiler) construction, usually after [parsing](https://en.wikipedia.org/wiki/Parsing), to gather necessary semantic information from the [source code](https://en.wikipedia.org/wiki/Source_code).[[1]](https://en.wikipedia.org/wiki/Semantic_analysis_(compilers)#cite_note-WilhelmSeidl2013-1) It usually includes [type checking](https://en.wikipedia.org/wiki/Type_checking), or makes sure a variable is declared before use which is impossible to describe in the [extended Backus–Naur form](https://en.wikipedia.org/wiki/Extended_Backus–Naur_form) and thus not easily detected during parsing.

"context sensitive analysis"这个别名点出了本质:静态语义处理的正是 CFG 表达不了的**上下文相关约束**——语法层"用 CFG 近似"之后剩下的那部分。

与动态语义的关键区别:**编译器执行静态语义,但只能遵守动态语义**。类型检查器就是静态语义的实现。

---

## 二、静态语义包含什么

| 类别 | 内容 | 依赖 | 典型语言 |
|---|---|---|---|
| **名字解析** | 每个标识符引用绑定到哪个声明;作用域、遮蔽 | **符号表(核心)** | 全部 |
| **类型检查** | 操作数类型相容、函数签名、赋值、返回值匹配 | 符号表(查声明的类型) | 全部静态类型语言 |
| **类型推导** | `auto` / `var` / Hindley–Milner | 符号表(写回) | C++、Rust、ML |
| **隐式转换插入** | 整型提升、`int → double`、派生类到基类 | 符号表 | C、C++、Java |
| **重载决议** | 从候选集选最佳匹配 | **符号表(核心)** | C++、Java、Rust |
| **访问控制** | `private` / `pub` / 模块边界 | 符号表 | C++、Java、Rust |
| **常量求值** | `constexpr`、数组维度、`case` 标签、Zig `comptime` | 符号表 | C++、Rust、Zig |
| **definite assignment** | 变量使用前在所有路径上已赋值 | **CFG** | Java、C# |
| **可达性** | 死代码、缺失 `return` | **CFG** | Java、Rust |
| **借用检查** | 生命周期与别名规则 | **MIR 数据流** | Rust |
| **effect / 线性类型** | 资源使用次数、副作用追踪 | 类型系统 | Rust(部分)、Koka、Linear Haskell |

相关专题:

- 名字解析 → [[front-end/static-semantic-analysis/name-binding/index|name binding]]
- 先声明后使用 → [[front-end/static-semantic-analysis/semantic-analysis~identifier-declared-before-used/index|identifier declared before used]]
- 符号表 → [[front-end/static-semantic-analysis/symbol-table/index|symbol table]]

---

## 三、形式工具

| 工具 | 用来描述 |
|---|---|
| **类型系统(推导规则)** | 类型检查、类型推导 |
| **属性文法** | 沿语法结构传播的语义信息,见 [[front-end/static-semantic-analysis/attribute-grammar/index|attribute grammar]] |
| **符号表** | 名字 → 声明的绑定 |
| **数据流分析** | definite assignment、借用检查等流敏感性质 |

典型的类型规则长这样:

$$
\frac{\Gamma \vdash e_1 : \texttt{int} \qquad \Gamma \vdash e_2 : \texttt{int}}{\Gamma \vdash e_1 + e_2 : \texttt{int}}
$$

读作:在类型环境 $\Gamma$ 下,若 $e_1$、$e_2$ 都是 `int`,则 $e_1 + e_2$ 也是 `int`。**$\Gamma$ 在实现里的物理载体就是符号表。**

类型规则按语法结构归纳定义——每条规则对应一种语法构造,这正是"结构即语义"在静态语义层的体现。

---

## 四、一个重要的内部分裂:流不敏感 vs 流敏感

第二节表里其实混着两类性质,实现机制完全不同。

**流不敏感(flow-insensitive)** 的检查只看声明和表达式结构,靠**符号表 + 类型规则**即可:

```c
int x = "hello";   // 看类型就知道不行,不需要知道控制流
```

**流敏感(flow-sensitive)** 的检查必须分析控制流图,靠**数据流分析 + 不动点迭代**:

```java
int x;
if (cond) x = 1;
System.out.println(x);   // 错误:x 可能未初始化
```

Java 的 definite assignment(JLS §16)、Rust 的借用检查、C# 的 nullable 流分析都属于后者。它们在形式上是**前向数据流分析**:

$$\text{OUT}[B] = f_B(\text{IN}[B]), \qquad \text{IN}[B] = \bigcap_{P \in \text{pred}(B)} \text{OUT}[P]$$

这里用的是交(must 性质:"所有路径上都已赋值")。它和中端的常量传播、活跃变量分析、"单一定义到达"是**同一套数学**——区别只在于它跑在前端的 AST/CFG 上,结论用于**拒绝程序**,而不是用于优化。

**这是一条值得记住的对应**:静态语义里最复杂的部分,其技术底座和中端优化完全相同。Rust 把借用检查放在 MIR(而非 AST)上做,正是因为需要一个像样的 CFG。

---

## 五、核心载体:符号表与类型表

静态语义的"记忆"是两张表:

```
符号表 (Symbol Table)    名字 → Symbol { kind, type, scope, linkage, ... }
类型表 (Type Table)      类型的规范表示,做 uniquing
```

类型表要做 **uniquing**(唯一化):`int*` 只构造一次,结构相同的函数类型共享同一对象。于是

$$\texttt{T1 == T2} \iff \text{两者是同一类型}$$

退化成**指针比较**。这个手法在编译器里到处出现——Clang 的 `IdentifierTable` 对标识符字符串做 interning,LLVM 的 `LLVMContext` 对 `i32` 和 `ConstantInt` 做 uniquing,动机完全一致:**把语义相等变成物理相等,把 $O(n)$ 比较变成 $O(1)$**。

这也是静态语义层"相等"的含义:语法层的相等是树比较,静态语义层是指针比较,动态语义层则需要 SMT 求解(见总纲 3.5 节)。

---

## 六、Sema 做什么:检查 + 变换

parser 产出的 AST 只保证形状合法,它并不知道变量是否存在、类型是否匹配、操作是否合法。Sema 同时做**检查(checks)**和**变换(transformations)**:[[1](https://stackoverflow.com/questions/11510792/is-the-semantic-analysis-step-in-clang-an-essential-part-of-the-compiler)]

- **Symbol Gathering**:扫描声明(`let`、`fn`、`class`),维护和更新符号表(不同编译器实现不同);
- **Name Resolution**:把每个变量/函数的使用映射到它的**声明**,捕获未定义引用;[[1](https://axion-resources.vercel.app/semantic-analysis/orchestrator)]
- **Type Checking**:验证表达式、函数签名、赋值、返回值的类型;
- **Scope & Access Control**:检查可见性规则(C++/Rust 的 public vs private),确保变量不越出作用域;[[1](https://clang.llvm.org/doxygen/classclang_1_1Sema.html)]
- **IR Lowering / 编译期求值**:在 Zig 这类现代编译器里,Sema 还负责 `comptime` 与泛型求值,并把无类型的 ZIR 转成有类型的 AIR。[[1](https://mitchellh.com/zig/sema)]

### 静态语义会改写程序

一个常被忽略的事实:Sema **不只是检查,它主动修改 AST**。

```c
int add(int, int);
double r = add(5, 2);
return r;              // 函数返回 int
```

语义分析做了什么:

1. 查 `add` → 命中声明,签名匹配;
2. `add(5,2)` 类型为 `int`,赋给 `double` → **插入 `ImplicitCastExpr: int → double`**;
3. `return r`,`r` 是 `double`,返回类型是 `int` → **再插一次 `double → int`**。

出口的树比入口的树信息多得多,这就是 **annotated AST / decorated AST**。类似地,重载决议把"一个名字"替换成"一个具体函数";`constexpr` 求值把表达式替换成字面量。

> **静态语义的产物不是"是/否",而是一棵被充实过的树(外加符号表)。**

---

## 七、判定成本与失败表现

**判定成本**:多项式居多。但有例外——**C++ 模板实例化是图灵完备的,所以"这个 C++ 程序是否良构"一般情况下不可判定**。良构性本该是编译器能回答的问题,这里它直接撞上停机问题。

**失败表现**:type error、name error。与语法错误不同,**位置可能很远**:

```cpp
template<typename T> void f(T t) { t.foo(); }
f(42);   // 错误报在模板体内,但真正的问题在调用点
```

C++ 模板的错误信息臭名昭著,根源就是语义检查推迟到实例化期才发生。**Concepts 的核心动机正是把语义约束前移,变成接近语法层的可检查契约。**

---

## 八、错误恢复:中毒符号

实际编译器不能遇到第一个错误就停,否则一次编译只能报一个错。标准手法是插入**中毒(poisoned)符号**:

```c
int x = undeclared_thing;   // ① 报 "undeclared identifier"
x + 1;                      // ② 不应再报 "x 类型未知"
```

做法:查找失败时插入 `type = ErrorType` 的占位符号,后续所有涉及 `ErrorType` 的检查**一律静默通过**;Clang 还会 `setInvalidDecl()` 并做 typo correction。

**错误类型在类型系统里的角色,和 `poison` 在 LLVM IR 动态语义里的角色高度同构**——都是一个**吸收性的坏值**,会传播但不产生新噪音。语法层的 error 节点也是同一思路,三者的对照见总纲 3.7 节。

---

## 九、在编译流水线中的落点

### 9.1 几乎全在前端

```
源码 → [lexer] → [parser] → [Sema] → annotated AST → IR
                              ↑
                        静态语义在这里
```

它的产物是**决定**(接受/拒绝)加**充实后的 AST**。到达 IR 之后,静态语义的使命基本结束。

### 9.2 IR 层的类型系统远弱于源语言

LLVM IR 的 `i32` 不知道自己原本是 `int` 还是 `unsigned`——signedness 在 IR 里属于**操作**而非**类型**,故有 `sdiv`/`udiv` 之分。源语言的大量静态语义信息(作用域、访问控制、类名)在此丢失。

需要往下传的部分只能**另辟通道**:

- 名字 → **name mangling**(C++ 用 Itanium ABI)→ `.o` 符号表;
- 类型与变量名 → **debug metadata**(`!DILocalVariable`、`!DIType`)→ DWARF。

```llvm
%x.addr = alloca i32, align 4
  #dbg_declare(ptr %x.addr, !10, !DIExpression(), !11)
!10 = !DILocalVariable(name: "x", scope: !5, line: 3, type: !8)
```

**符号表的内容在这里被"再编码"了一次**——从编译器的工作数据结构,变成随 IR 流动的元数据。调试器能告诉你 `x = 42`,全靠这条链。

### 9.3 真实编译器中的 Sema

- **Clang (C/C++)**:语义分析引擎集中在以 `Sema` 为前缀的类和文件里(`Sema.h`、`SemaDecl.cpp`、`SemaChecking.cpp`),在构建 AST 的同时或通过 **multi-pass** 检查完成验证。[[1](https://stackoverflow.com/questions/11510792/is-the-semantic-analysis-step-in-clang-an-essential-part-of-the-compiler), [2](https://clang.llvm.org/doxygen/classclang_1_1Sema.html)]
- **Zig**:`src/Sema.zig` 是中心阶段,解释无类型的 ZIR 以求值 `comptime` 代码,并产出有类型的 AIR。[[1](https://mitchellh.com/zig/sema), [2](https://ziggit.dev/t/build-without-semantic-analysis/8010)]
- **rustc**:名字解析与类型检查在 HIR 上做,借用检查在 MIR 上做——典型的"流不敏感在树上、流敏感在 CFG 上"的分工。
- **自研/单体编译器**:通常组织成多遍(multi-pass)的编排器——先解析符号,再类型检查,最后做流/借用检查。[[1](https://axion-resources.vercel.app/semantic-analysis/orchestrator)]

---

## 十、能力边界:动态语义的可判定近似

静态语义能保证的性质有上限,这个上限由 **Rice 定理**决定:任何非平凡的程序语义性质都不可判定。所以:

> **类型系统的本质是"动态语义的可判定近似"。**

它必然要么拒绝一些实际正确的程序(不完备),要么漏掉一些错误(不可靠)。衡量它的两把尺子:

| 性质 | 含义 |
|---|---|
| **Soundness** | 类型检查通过 ⇒ 不会发生某类运行时错误 |
| **Completeness** | 不发生该类错误 ⇒ 能通过检查 |

主流语言选 soundness、放弃 completeness;Rust 的 NLL、Polonius 等工作就是在保持可判定的前提下**减少误拒**。

soundness 的经典表述 "well-typed programs don't go wrong",需要借助**操作语义**用 progress + preservation 来证明——**静态语义的正确性定理,必须用动态语义的语言来写**。详见总纲 4.1 节。

---

## 十一、演化:静态语义在膨胀

```
C (1972)      类型 + 作用域
Java (1995)   + definite assignment + 异常检查 + 泛型
Rust (2015)   + 所有权 + 生命周期 + Send/Sync
依赖类型语言   + 任意命题的证明
```

趋势很清楚:**把原本属于动态语义的"坏行为"搬到静态语义层排除**。Rust 的借用检查就是把 use-after-free(原本是 UB)变成编译错误。代价是检查器越来越复杂、表达越来越受限。

---

## 十二、小结

| 维度 | Static Semantics |
|---|---|
| 问什么 | 良构吗 |
| 输出 | 接受/拒绝 + annotated AST + 符号表 |
| 形式工具 | 类型规则、属性文法、符号表、数据流分析 |
| 可判定性 | 可判定(C++ 模板除外) |
| 成本 | 多项式 |
| 失败表现 | type error、name error,位置可能远离根因 |
| 编译器角色 | **执行者** |
| 什么叫相等 | 两个类型相同(uniquing 后指针比较) |
| 演化趋势 | 持续膨胀 |

三句话收束:

1. 静态语义是**守门人**:处理 CFG 表达不了的上下文相关约束,在编译期决定接受还是拒绝;
2. 它的产物不止是"是/否",还有一棵被充实的树和一张符号表,并且其中最复杂的部分(流敏感检查)与中端优化共享同一套数据流数学;
3. 它是**动态语义的可判定近似**——语言设计的主线,就是不断把动态语义的责任搬进这一层。
