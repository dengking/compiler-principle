# Syntax:语言的形状

> 本文是 [[3-layers-of-a-language-specification/index|语言规范的三层]] 中的第一层。三层的总览与横向对比见总纲;后两层见 [[front-end/static-semantic-analysis/index|static-semantic-analysis]] 与 [[3-layers-of-a-language-specification/dynamic-semantic/index|dynamic-semantic]]。

---

## 一、它管什么

**Syntax(语法)规定哪些字符串构成合法的程序文本。** 形式化地说,语言是字母表 $\Sigma$ 上字符串的集合 $L \subseteq \Sigma^*$,语法层要回答的就是一个成员判定问题:

$$w \in L\ ?$$

它只关心符号的**形状与排列**,不关心含义:

```c
int x = ;          // 不属于 L:= 后缺表达式,CFG 直接拒绝
int x = "hello";   // 属于 L:形状完全合法(类型错误是静态语义的事)
```

在三层里,syntax 是最廉价、最"机械"的一层:可判定、近乎线性、错误位置精确。但下文会看到,它并不像看上去那么"纯形式"。

---

## 二、两级结构:词法与句法

工程上语法层被再切成两级:

| | 词法(lexical) | 句法(syntactic) |
|---|---|---|
| 单位 | 字符 → token | token → 树 |
| 形式工具 | 正则表达式 | 上下文无关文法(CFG) |
| 识别器 | 有限自动机(DFA) | 下推自动机(LL / LR / PEG parser) |
| Chomsky 层级 | 3 型(正则) | 2 型(上下文无关) |
| 代表工具 | lex/flex、re2c | yacc/bison、ANTLR、tree-sitter |

切成两级不是理论必须(正则语言本就是上下文无关语言的子集),而是工程收益:词法用 DFA 一遍扫完,把空白、注释、关键字识别这些"琐事"挡在 parser 之外,让文法规模小一个量级。

---

## 三、形式工具:BNF / EBNF

句法用 CFG 描述,书写形式是 BNF / EBNF。经典的表达式文法(E-T-F):

```
expr   → expr '+' term   | term
term   → term '*' factor | factor
factor → NUMBER | '(' expr ')' | IDENT
```

几点值得注意:

- **递归**让有限条规则生成无限多的句子,见 [[front-end/grammar/recursive-grammar/index|recursive grammar]];
- `expr → expr '+' term` 是**左递归**,对 LR parser 友好,对 LL / 递归下降 parser 则必须先消除;
- 同一个语言可以有多份文法,它们**生成同样的字符串集合,却给出不同形状的树**——这一点正是下一节的主题。

---

## 四、产物:parse tree 与 AST

| | Parse tree(具体语法树) | AST(抽象语法树) |
|---|---|---|
| 内容 | 文法推导的完整记录 | 只保留对语义有用的结构 |
| 括号、分号 | 保留 | 吸收进树形,不再出现 |
| 用途 | 理论分析、格式化工具 | 后续所有阶段的输入 |

从代数角度看,AST 是由一组构造子(签名 $\Sigma$)自由生成的**项代数** $T_\Sigma$——具体语法(括号、优先级、空格)已经在解析阶段被吸收掉。这一视角是"结构即语义"的数学起点,详见 [[front-end/grammar/structure-is-semantics/index|结构即语义]]。

---

## 五、文法结构编码了语义意图

一个常被忽略的点:**语法规则编码了结合性与优先级,而那已经带有语义意图了。**

`a + b * c` 解析成 `a + (b * c)` 而不是 `(a + b) * c`,不是 parser 里写了一段 `if/else` 判断,而是文法的形状决定的——`term` 的产生式里根本没有 `+`,另一种分组**在语法上无法推导出来**。但选择这个形状的理由来自**算术语义**。所以第一层也不是纯形式的。

这背后有两种强度不同的命题:

| | 命题 | 例子 |
|---|---|---|
| **弱形式(描述性)** | 复合结构的含义由结构与成分含义唯一决定(组合性原则) | 语法制导翻译、沿 AST 递归的求值器 |
| **强形式(构造性)** | 精心设计结构,使非法语义在结构上不可表示 | E-T-F 文法让错误分组无法推导 |

展开阅读:

- [[front-end/grammar/structure-is-semantics/index|结构即语义:从表达式文法到类型系统的一条主线]]
- [[front-end/grammar/structure-is-semantics/expression-grammar-associativity-and-precedence|表达式文法如何编码结合性与优先级]]
- [[front-end/grammar/structure-is-semantics/if-then-else-grammar|if-then-else 文法与 dangling else]]
- [[front-end/grammar/structure-is-semantics/left-recursion-recursion|左递归与递归]]

---

## 六、二义性与消歧

一份文法若能为同一个句子给出两棵不同的树,就是**二义的(ambiguous)**。二义性本身不是语法错误,而是"同一形状有多种含义"——这又一次说明语法与语义的纠缠。

消除二义有两条路:

1. **改写文法**:像 E-T-F 那样分层,让多余的树无法推导;
2. **外挂消歧规则(disambiguating rules)**:文法保持二义,另加规则选择其中一棵。yacc 的 `%left` / `%right` / `%prec`、dangling else 的"就近匹配"(else 与最近的未匹配 if 结合)都属此类。

C++ 的 **most vexing parse** 是消歧规则的极端例子:

```cpp
Widget w(Thing());   // 变量定义?还是函数声明?
```

规则是"只要能解释成声明,就解释成声明"——消歧规则本身就是语法与语义混合的产物。

---

## 七、判定成本与失败表现

**判定成本**:通用 CFG 解析(CYK、Earley、GLR)最坏 $O(n^3)$;但实际语言的文法都被设计成 LL(k) / LR(k) / PEG 可解析,成本是**线性**的。

**失败表现**:syntax error,**位置精确**——就在那个 token。这与静态语义形成鲜明对比:后者的"案发现场"可能离"犯罪现场"很远(C++ 模板错误报在模板体内,真正的问题在调用点)。

**错误恢复**:parser 不能遇到第一个错误就停。常见手法:

| 手法 | 做法 |
|---|---|
| panic mode | 丢弃 token 直到同步点(`;`、`}`),再继续解析 |
| error production | 在文法中显式加入"错误产生式",如 yacc 的 `error` 终结符 |
| phrase-level | 局部插入/删除/替换 token,修补成合法输入 |
| 错误节点 | 在 AST 中插入 error node,让后续阶段继续工作(tree-sitter、Roslyn) |

"插入一个吸收性的坏值让流程继续"这一手法,在静态语义(`ErrorType`)和动态语义(`poison`)里会以同构的形式再出现两次,见总纲 3.7 节。

---

## 八、能力边界:CFG 只是近似

真实编程语言在 Chomsky 层级上是**上下文相关**甚至更强的。最典型的反例就是"**标识符先声明后使用**"——这类约束无法用 EBNF 描述,因此在解析阶段不易检测(维基百科对 semantic analysis 的定义正是以此为例)。

但没人用上下文相关文法写 parser——它没有高效算法。工程妥协是:

$$\text{用 CFG 近似} \;+\; \text{把剩下的约束塞进"语义分析"}$$

而这个近似并不总能守住边界。C 的 **lexer hack** 就是 syntax 反向依赖 static semantics 的例子:

```c
A * B;   // 声明(B 是 A*)还是乘法表达式?取决于 A 是否 typedef 名
```

parser 必须在解析途中查符号表,把 `IDENTIFIER` 重分类为 `TYPEDEF_NAME`——第一层调用了第二层的数据。所以**"什么算语法错误、什么算语义错误"在相当程度上是实现决策,不是本质划分**。更多案例见总纲 4.2 节。

---

## 九、同一语义,多套语法:以 LLVM IR 为例

syntax / semantics 的区分在 IR 层同样适用:

> **内存表示、文本 `.ll`、bitcode `.bc` 是同一份语义的三种语法编码。**

| | Syntax | Semantics |
|---|---|---|
| 内存表示 | C++ 类层次、use list、uniqued 类型 | ← 同一份 |
| 文本 `.ll` | LangRef 定义的文本文法 | ← 同一份 |
| Bitcode `.bc` | 位流容器、abbreviation、VBR 编码 | ← 同一份 |

它们能**无损往返**,正是因为语义同构、只有语法不同。而 LangRef 恰好覆盖两件事:

- **Syntax 部分**:`define i32 @f(i32 %a) { ... }` 怎么写、标识符规则、类型怎么拼;
- **Semantics 部分**:`add nsw` 溢出产生 **poison** 而不是回绕,`sdiv` 除零是 **UB**,`freeze` 把 poison 变成任意确定值……

篇幅上**语义压倒性占多数**。原因很直白:语法错了,parser 会报错;语义没定义清楚,优化器会悄悄生成错误代码。

SSA 的不变量也分属两边:

| 约束 | 性质 | 怎么查 |
|---|---|---|
| φ 必须在基本块头部且连续 | **语法性** | 扫一遍指令列表 |
| 终结指令必须且只能在块末尾 | **语法性** | 局部检查 |
| 类型必须精确匹配 | **语法性**(uniqued 后是指针比较) | 局部检查 |
| **use 必须被 def 支配** | **语义性** | 需要构造支配树 |
| φ 的每个前驱恰好一个条目 | **语义性** | 需要 CFG 结构 |

`Verifier` 两类都查,但代价差了一个数量级——这就是为什么支配关系检查只在 `-verify-each` 或 debug build 里全量跑。

---

## 十、小结

| 维度 | Syntax |
|---|---|
| 问什么 | 形状对吗($w \in L$?) |
| 形式工具 | 正则(词法)+ CFG / BNF / EBNF(句法) |
| 产物 | token 流、parse tree、AST |
| 可判定性 | 可判定,完备 |
| 成本 | 实践中线性 |
| 失败表现 | syntax error,位置精确 |
| 什么叫相等 | 两棵 AST 结构相同(树遍历) |
| 什么叫完备 | 文法恰好生成意图中的语言,无歧义 |
| 演化趋势 | 稳定 |

三句话收束:

1. 语法层判定"形状",廉价、可判定、错误精确,是三层中最"工程化"的一层;
2. 但它**并不纯形式**:文法结构编码了优先级、结合性等语义意图,二义性的消歧规则也掺杂语义;
3. CFG 只是真实语言的近似,超出部分被推给静态语义——这条边界由实现决定,并且会被 lexer hack 这类技巧打穿。
