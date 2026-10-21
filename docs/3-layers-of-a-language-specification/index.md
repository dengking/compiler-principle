# 语言规范的三层:Syntax、Static Semantics、Dynamic Semantics

language-specification=语言规范

> 本文是总纲:先概述三层,再做横向对比与总结。每一层的详细介绍见:
>
> - Syntax → [[front-end/grammar/index|grammar]]
> - Static Semantics → [[front-end/static-semantic-analysis/index|static-semantic-analysis]]
> - Dynamic Semantics → [[3-layers-of-a-language-specification/dynamic-semantic/index|dynamic-semantic]]

---

## 一、先消歧:哪一个"三层"

"三层"在不同语境下指不同的东西:

| 说法 | 三层是什么 | 常见场合 |
|---|---|---|
| **语言规范的三层** | syntax / static semantics / dynamic semantics | 语言设计、编译器前端 |
| **Chomsky 式的三层** | lexical / syntactic / semantic | 教科书讲前端流水线 |
| **实现的三层** | frontend / middle-end / backend | 编译器架构 |
| **抽象的三层** | 源语言 / IR / 目标机 | 编译流水线 |

本文讲**第一种**——它是**语言定义本身的三个部分**,由标准委员会决定,所有实现都必须遵守同一份,也是唯一一个"不随实现改变"的划分。另外三种是实现结构,换个编译器就可能重新切分。

---

## 二、总览:三个问题、三道关

### 2.1 三个层层递进的问题

给定一段代码,可以问三个层次的问题:

```c
int x = ;              // ① 这是程序吗?           → 语法错误:= 后缺表达式,CFG 直接拒绝
int x = "hello";       // ② 这是合法程序吗?       → 语法合法,类型错误(静态语义)
int x = y;             // ②' 同上                → 语法合法,名字未声明(静态语义:名字解析)
int a[5]; a[10] = 1;   // ③ 这个合法程序做什么?   → 三关全过,动态语义说:UB
```

- ① 问**形状**:字符串是否符合语言的文法。这是 **syntax(语法)**。
- ② 问**良构性**:形状合法的程序是否满足语言的其他静态规则。这是 **static semantics(静态语义)**。
- ③ 问**含义**:良构的程序执行起来意味着什么。这是 **dynamic semantics(动态语义)**。

一段代码必须**依次通过**三道关。这几行揭示了一个关键事实:**"编译通过"只覆盖到 ②。** ③ 落在静态语义的能力边界之外——它需要的是动态语义层面的保证,而 C 选择把它定义成 UB,也就是"不保证"。

### 2.2 一句话概括

$$
\underbrace{\text{Syntax}}_{\text{形状是否合法(parser)}} \;\longrightarrow\;
\underbrace{\text{Static Semantics}}_{\text{编译期可判定的良构性(Sema/类型检查)}} \;\longrightarrow\;
\underbrace{\text{Dynamic Semantics}}_{\text{程序运行时做什么(语言规范定义,编译器据此优化)}}
$$

- **Syntax 管"长什么样",Semantics 管"是什么意思"。**
- 通常说的"语义"涵盖后两者;但把语义切成静态、动态两半,结构才清楚。
- 用 Chomsky 层级的话说:syntax 基本是 **context-free** 的,static semantics 处理的是 CFG 表达不了的 **context-sensitive** 约束(因此语义分析也叫 context-sensitive analysis),dynamic semantics 则已经不是"文法"能回答的问题。

### 2.3 三层各自的定位

**Syntax:形状的守门人。** 定义哪些字符串构成合法的程序文本。形式工具是正则表达式(词法)+ 上下文无关文法(句法),判定几乎是线性的,产物是 parse tree / AST,错误位置精确到 token。值得注意的是,文法的结构本身已经编码了一部分语义意图(优先级、结合性)。
→ 详见 [[front-end/grammar/index|grammar]]

**Static Semantics:良构性的守门人。** 在形状合法的程序里,筛掉"没有意义"的那些:名字解析、类型检查与推导、重载决议、访问控制、常量求值、definite assignment、借用检查……它在编译期回答一个布尔问题——**接受还是拒绝**,同时产出一棵被充实过的 annotated AST。
→ 详见 [[front-end/static-semantic-analysis/index|static-semantic-analysis]]

**Dynamic Semantics:行为的承诺书。** 给每个被接受的程序分配一组**可观察行为**:

$$\lbrack\!\lbrack \cdot \rbrack\!\rbrack : \text{Program} \longrightarrow \mathcal{P}(\text{Behavior})$$

注意是**集合**:集合越小承诺越强,UB 就是集合等于全集。它不拒绝任何程序,只**描述**;它通过抽象机与 as-if 规则定义,是一切优化的合法性判据。
→ 详见 [[3-layers-of-a-language-specification/dynamic-semantic/index|dynamic-semantic]]

一句话区分后两层:

> **静态语义是守门人,动态语义是承诺书。编译器执行静态语义,但只能遵守动态语义。**

类型检查器是静态语义的**实现**;而优化器不是动态语义的实现,它是动态语义的**受约束方**。

---

## 三、横向对比

### 3.1 总表

| 维度 | Syntax | Static Semantics | Dynamic Semantics |
|---|---|---|---|
| **问什么** | 形状对吗 | 良构吗 | 跑起来干什么 |
| **输出** | parse tree / AST | 接受/拒绝 + annotated AST | 可观察行为的**集合** |
| **规范写法** | 正则 + CFG(BNF/EBNF) | 类型规则、属性文法、推导规则 | 操作 / 指称 / 公理语义 |
| **核心数据结构** | token 流、AST | 符号表 + 类型表 | IR + 行为集合 |
| **可判定性** | 是,完备 | 是(C++ 模板除外) | **否**(一般不可判定) |
| **判定成本** | $O(n)$ 左右 | 多项式(C++ 模板除外) | — |
| **失败表现** | syntax error,位置精确 | type/name error,位置可能很远 | UB / panic / 异常 / 静默错误 |
| **谁负责** | lexer + parser | Sema / 类型检查器 | 语言规范 + 运行时,贯穿全流程 |
| **编译器角色** | 执行者 | **执行者**(它来检查) | **遵守者**(它被约束) |
| **"相等"怎么判** | 树比较 | 指针比较(uniquing) | **SMT 求解** |
| **优化器是否依赖** | 否 | 部分(类型驱动) | **完全依赖** |
| **谁定义** | 语言标准 | 语言标准 | 语言标准 |
| **演化趋势** | 稳定 | **持续膨胀** | **持续收缩(UB 减少)** |

### 3.2 本质分界:可判定性

三者真正的分界不是时间(编译期/运行期),而是**可判定性**:前两层廉价且(基本)完备,第三层不可判定。

| 层 | 问题 | 可判定性 | 代价 |
|---|---|---|---|
| Syntax | 是否属于这个文法 | 可判定,**完备** | 线性 |
| Static Semantics | 是否良构 | 可判定(C++ 除外) | 多项式 |
| Dynamic Semantics | 程序做什么 | **不可判定**(Rice 定理) | — |

C++ 是例外:模板实例化图灵完备,"这个 C++ 程序是否良构"一般情况下不可判定——本该廉价的静态判定直接撞上停机问题。

正是**动态语义不可判定**,催生了所有的应对手段:

```
动态语义不可判定
    ├─ 类型系统         → 用可判定的近似拦住一部分(代价:拒绝某些正确程序)
    ├─ UB               → 直接不承诺,把责任推给程序员(代价:踩坑)
    ├─ 运行时检查       → 推到运行期(代价:性能)
    ├─ 抽象解释         → 过近似(代价:假警报)
    ├─ 动态 sanitizer   → 采样路径(代价:不完备)
    └─ SMT / 定理证明   → 对具体性质做证明(代价:人力、超时)
```

**类型系统的本质就是"动态语义的可判定近似"。** 它必然要么拒绝一些实际正确的程序(不完备),要么漏掉一些错误(不可靠)。主流语言选前者:

```rust
// 当前借用检查器(NLL)会拒绝这段,尽管它实际上是内存安全的
fn get_or_insert(map: &mut HashMap<u32, String>) -> &String {
    match map.get(&22) {
        Some(v) => v,                          // 返回的借用被认为贯穿整个 match
        None => {
            map.insert(22, String::from("hi")); // 拒绝:与上面的不可变借用冲突
            &map[&22]
        }
    }
}
```

NLL(非词法生命周期)和 Polonius 这些工作,做的就是**让近似更精确**——在保持可判定的前提下,减少误拒。上面这段正是 NLL 仍误拒、而 Polonius 能接受的经典案例。

### 3.3 三层与编译器阶段的关系

```
              frontend    middle-end    backend    runtime
syntax          ■            ·             ·          ·
static sem.     ■            ·             ·          ·
dynamic sem.    ■            ■             ■          ■     ← 贯穿
```

**前两层几乎只落在 frontend**,是**阶段性的工作**:做完就结束,结论是接受或拒绝。到达 IR 之后,源语言的静态语义信息大量丢失,只能经由 name mangling、debug metadata 等通道"再编码"往下传。

**第三层横贯所有阶段**,不是工作而是**契约**:每一级 IR 都有自己的一份动态语义,编译的每一步都是相邻两份之间的**精化(refinement)**:

$$\text{源码} \;\sqsupseteq\; \text{AST} \;\sqsupseteq\; \text{LLVM IR} \;\sqsupseteq\; \text{MIR} \;\sqsupseteq\; \text{机器码}$$

所以"动态语义属于 backend 吗"是个范畴错误:前端/中端/后端是**阶段划分**(谁在什么时候做什么),三层是**规范划分**(程序是什么意思)。backend 只是**负责其中一段精化**(IR 语义 → ISA 语义),并因此独占一批义务:内存模型降级、浮点模式、ABI、异常表、`volatile`。

### 3.4 每层在工具链里的物化

| 层 | 核心数据结构 | 代表工具 | 检查者 |
|---|---|---|---|
| Syntax | token 流、parse tree、AST | yacc/bison、ANTLR、tree-sitter | parser |
| Static Semantics | **符号表** + 类型表 + CFG | Clang Sema、rustc HIR/类型检查 | type checker |
| Dynamic Semantics | IR + 语义规范 | LangRef、Alive2、Miri、sanitizer | verifier + 人 |

想检查的性质落在哪一层,直接决定技术选型:

| 性质 | 工具 |
|---|---|
| 形状合法性 | CFG + parser generator(LL/LR/PEG) |
| 类型、作用域 | 属性文法、类型系统、符号表 |
| 定值-引用、活跃性、支配 | 数据流分析、不动点迭代 |
| 变换是否保语义 | **SAT / SMT**(Alive2、LEC) |
| 任意程序性质 | 不可判定(Rice 定理) |

### 3.5 三种"相等"

**三层的"相等"是三种不同的东西:**

| 层 | 什么叫相等 | 怎么判 |
|---|---|---|
| Syntax | 两棵 AST 结构相同 | 树遍历,平凡 |
| Static Semantics | 两个类型相同 | **uniquing 后变成指针比较** |
| Dynamic Semantics | 两个程序行为等价 | **SMT 求解器**(Alive2、LEC) |

Alive2 证明的从来不是"改写前后 IR 文本相同",而是"在所有输入下可观察行为相同"。从"遍历树"到"指针比较"到"调 SAT 求解器",难度跨了三个数量级。这也是为什么编译器能廉价地验证 SSA 的语法不变量(φ 在块首、终结指令在块尾),却只能在专门工具里验证支配关系和语义等价。

### 3.6 三种"完备性"

| 层 | 完备性指什么 |
|---|---|
| Syntax | 文法恰好生成意图中的语言,无歧义 |
| Static Semantics | **Soundness**:类型检查通过 ⇒ 不会发生某类错误<br>**Completeness**:不发生该类错误 ⇒ 能通过检查 |
| Dynamic Semantics | 规范本身无矛盾、覆盖所有情形 |

第三层自己也可能不完备:C++ `relaxed` 原子的 OOTA 问题、C 的指针 provenance 直到近年才被正式提案,都是动态语义规范本身有洞的实例。

### 3.7 三种"坏值":错误恢复的同构

三层都要面对同一个工程问题——**某个东西已经没有意义了,如何继续往下工作**——并且给出了同形的解法:引入一个**吸收性的坏值**。

| | Syntax | Static Semantics | Dynamic Semantics(LLVM IR) |
|---|---|---|---|
| 坏值 | `error` 终结符 / 错误节点 | `ErrorType` / poisoned symbol | `poison` / `undef` |
| 产生时机 | 遇到无法匹配的 token | 名字查找失败、类型检查失败 | `add nsw` 溢出、读未初始化内存 |
| 传播规则 | 跳过 token 直到同步点(panic mode) | 涉及它的检查静默通过 | 大多数指令对 poison 操作数产生 poison |
| 目的 | 一次报多个语法错误 | 避免级联错误噪音 | 允许优化器假定 UB 不发生,又避免立即 UB |
| 如何"洗掉" | 到同步点重新开始 | 不洗,到此为止 | `freeze`:poison → 任意确定值 |

这不是巧合——这些系统都是"在结构/格上传播信息",都需要一个顶/底元素来表示"无信息"。

### 3.8 跨语言:同一问题落在不同层

同一个"数组越界"问题,不同语言把它放在三层的不同位置:

| 语言 | 越界检查落在哪层 | 代价 |
|---|---|---|
| C / C++ | **动态语义(UB)** | 零开销,零保证 |
| Java / Go | **动态语义(有定义:抛异常/panic)** | 运行时检查开销 |
| Rust | 动态语义(panic),但**索引以外的别名错误在静态层排除** | 部分开销 + 类型系统复杂度 |
| 依赖类型语言(Idris、F*) | **静态语义**——必须在编译期证明 $i < n$ | 程序员要写证明 |
| ATS / Dafny | 静态语义 + SMT 自动证明 | 需要不变式标注 |

再从"静态语义强度 × 动态语义 UB 量"两个维度看:

| 语言 | 静态语义强度 | 动态语义 UB 量 | 策略 |
|---|---|---|---|
| **C** | 弱(类型可随意转换) | 极多(200+ 条) | 把负担全交给程序员,换优化空间 |
| **C++** | 中(RAII、模板、concepts) | 极多 | 同上,但用抽象降低出错率 |
| **Java** | 中强 | 极少(越界抛异常,溢出回绕) | 动态检查兜底,牺牲部分性能 |
| **Rust** | **强**(所有权+借用+生命周期) | safe 代码为零,`unsafe` 内有 | **用静态语义消灭 UB** |
| **Haskell/ML** | 强(HM 类型推导) | 极少 | 纯函数式 + 强类型 |
| **WebAssembly** | 强(形式化类型系统) | **零** | 规范级保证 |

这揭示了语言设计的核心权衡:

$$
\text{往上搬(静态化)} \;\Rightarrow\; \text{保证更强,表达更累}
\qquad
\text{往下放(动态化)} \;\Rightarrow\; \text{写得自由,保证更弱}
$$

C 选择"静态弱 + 动态松",换取最大优化自由;Rust 选择"静态强 + 动态严",换取安全;两者在同一光谱的两端。

---

## 四、层与层之间:桥、裂缝与交汇点

### 4.1 唯一严谨的桥:type soundness

一个良好的类型系统保证:**类型正确的程序不会出现某一类动态语义错误**。这就是 **type soundness**,口号是 "**well-typed programs don't go wrong**",它的表述方式恰好把两层语义串起来:

$$
\underbrace{\text{通过静态语义检查}}_{\text{第二层}} \;\Longrightarrow\; \underbrace{\text{动态语义中不出现 stuck state}}_{\text{第三层}}
$$

标准证法是 **progress + preservation**:

- **Progress**:良类型的项要么是值,要么能继续走一步(不会卡死在无规则可用的状态);
- **Preservation**(subject reduction):走一步之后类型不变。

两者都需要先有**操作语义**才能表述——所以**第二层的正确性定理,必须用第三层的语言来写**。这就是为什么严肃的语言设计必须三层一起做,不能只写语法和类型规则;也是为什么 WebAssembly 的规范同时给了小步语义和机器检查的类型安全证明。

### 4.2 分界在哪里崩塌

理论上三层顺序通过,实践中根本做不到干净分离。

**(1) C 的 lexer hack:syntax 反向依赖 static semantics**

```c
A * B;
```

这是**声明**(`B` 是 `A*`)还是**表达式语句**(`A` 乘 `B`)?取决于 `A` 是不是 typedef 名——而这是**符号表里的信息**。于是 C 的 parser 必须在解析途中查符号表,把 `IDENTIFIER` 动态重分类为 `TYPEDEF_NAME`:**第一层调用了第二层的数据。**

Clang 的做法稍干净些:lexer 保持纯净,由 parser 调 `Sema::ClassifyName` 把 token 原地标注成 `annot_typename`,耦合上移到 parser↔Sema 之间。但分层仍然被打穿了。

**(2) C++ 的 most vexing parse**

```cpp
Widget w(Thing());   // 变量定义?还是函数声明?
```

C++ 规定:**只要能解释成声明,就解释成声明**。于是这行声明了一个返回 `Widget`、接受"一个返回 `Thing` 的无参函数指针"的函数。消歧规则本身就是语法与语义混合的产物。

**(3) Chomsky 层级上的错位**

真实语言是**上下文相关**甚至更强的,但没人用上下文相关文法写 parser——它没有高效算法。工程妥协是:

$$\text{用 CFG 近似} \;+\; \text{把剩下的约束塞进"语义分析"}$$

"标识符先声明后使用"就是典型:它无法用 EBNF 描述,于是被推给静态语义。

**结论:"什么算语法错误、什么算语义错误"在相当程度上是实现决策,不是本质划分。** Rust 的借用检查本可以看作某种类型规则(语法性的),实际被实现成独立的 MIR 阶段分析(语义性的)。

### 4.3 交汇点:语法制导翻译

syntax 与 semantics 正式握手的地方是 **syntax-directed translation(语法制导翻译)**——把语义动作挂在文法产生式上:

```
expr → expr₁ '+' expr₂   { $$.type = unify($1.type, $2.type);
                           $$.code = emit(ADD, $1.place, $2.place); }
```

这就是**属性文法**:综合属性(自下而上)与继承属性(自上而下)在 AST 上流动,把语义信息沿着语法结构传播。yacc/bison 的 `{ ... }` 动作块、ANTLR 的 listener/visitor,都是这个思路的实现。

**它既不是纯语法也不是纯语义,而是"用语法结构组织语义计算"。** 现代编译器虽然很少在 parse 时直接生成代码(改为先建 AST 再多遍遍历),但这个"结构驱动语义"的模式贯穿始终——MLIR 的 pattern rewrite 本质上也是它的一个变体。其理论根基是**组合性原则**,详见 [[front-end/grammar/index|grammar]] 中"结构即语义"一节。

### 4.4 UB:三层合力定义出的"洞"

有了三层,UB 可以被精确定义:

> **UB = 语法合法、静态语义合法,但动态语义明确声明"不作保证"的程序。**

用行为集合的语言说:**UB 就是 $\lbrack\!\lbrack P \rbrack\!\rbrack$ 等于全集**。它不是 bug,是规范在语义层**主动留下的洞**,目的是换取优化空间——`add nsw` 溢出产生 poison、C 里有符号溢出是 UB,都是这个设计。这也是为什么"编译通过"从来不等于"程序正确"。

---

## 五、几个跨层的常见误解

**1. "静态/动态语义 = 静态/动态类型"**

两套完全正交的术语。"静态/动态语义"说的是**规范的哪一半**,"静态/动态类型"说的是**类型检查在什么时候**。

| | 静态类型 | 动态类型 |
|---|---|---|
| **动态语义复杂** | C、C++、Rust | Python、JavaScript |
| **动态语义较简单** | Java(相对) | Lua |

C 是彻底的静态类型语言,却有一份出了名复杂的动态语义。

**2. "编译通过 = 程序正确"**

编译通过只覆盖到静态语义。**静态语义能保证的性质有上限,这个上限由 Rice 定理决定**:任何非平凡的程序语义性质都不可判定。

**3. "动态语义只在运行期起作用"**

恰恰相反,它**在编译期被大量消耗**——常量折叠、循环删除、UB 推理、别名分析全发生在编译期,编译器读的就是动态语义。**动态语义是编译期的输入,运行时行为是它的输出。**

**4. "动态语义属于后端"**

范畴错误,见 3.3。动态语义不是某阶段执行的工作,而是所有阶段必须遵守的契约。

**5. "语法和语义可以干净分层"**

见 4.2。分层是规范层面的理想,实现层面处处被打穿。

---

## 六、演化趋势:责任在三层之间迁移

整个语言演化史可以概括为**责任在三层之间的迁移**——更具体地说,是**不断把责任从第三层往第二层搬**:

```
1970s  C:         几乎什么都往动态层扔(UB 约 200 条)
1990s  Java:      把内存错误搬到运行时检查(UB → 异常)
2010s  Rust:      把内存错误搬到静态层(运行时检查 → 编译错误)
2020s  Wasm:      动态层零 UB(但抽象层次低)
 ?     依赖类型:  把功能正确性也搬到静态层
```

与之对应,静态语义的内容在**大幅膨胀**:

```
C (1972)      类型 + 作用域
Java (1995)   + definite assignment + 异常检查 + 泛型
Rust (2015)   + 所有权 + 生命周期 + Send/Sync
依赖类型语言   + 任意命题的证明
```

趋势很清楚:**把原本属于动态语义的"坏行为"搬到静态语义层静态排除**。Rust 的借用检查就是把 use-after-free(原本是 UB)变成编译错误。每往上搬一层,保证更强,写起来也更累。

而第一层 syntax 相对稳定:新语言的语法创新大多是"糖",真正的设计重心早已转移到语义层。

---

## 七、总结

把整篇收成几句话:

1. **三层是语言规范本身的划分**,不随实现改变:syntax 管形状,static semantics 管良构,dynamic semantics 管行为。
2. **前两层是守门人,第三层是承诺书。** 编译器执行前两层,但只能遵守第三层;前两层做完就结束,第三层贯穿从源码到机器码的整条精化链。
3. **真正的分界是可判定性。** 前两层廉价且可判定,第三层不可判定——类型系统、UB、运行时检查、sanitizer、抽象解释、SMT,都是对这一事实的不同妥协。
4. **分层是理想,不是现实。** lexer hack、most vexing parse、C++ 模板都在打穿边界;"语法错误还是语义错误"相当程度上是实现决策。
5. **两层语义之间唯一严谨的桥是 type soundness**,而它必须用动态语义来表述——所以三层必须一起设计。
6. **语言设计的历史,就是把责任从动态层往静态层搬的历史。**

各层细节:

- Syntax → [[front-end/grammar/index|grammar]]
- Static Semantics → [[front-end/static-semantic-analysis/index|static-semantic-analysis]]
- Dynamic Semantics → [[3-layers-of-a-language-specification/dynamic-semantic/index|dynamic-semantic]]
