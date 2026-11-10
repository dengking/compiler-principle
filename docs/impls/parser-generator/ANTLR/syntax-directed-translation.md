# 语法制导翻译的工程实现

## ——以 ANTLR 4 为例，论属性文法如何落到可执行的代码上

---

## 0. 问题的提出

语法制导翻译（Syntax-Directed Translation, SDT）回答的是这样一个问题：

> 给定一个输入串的语法结构，如何在其上计算出一组值？

它的标准答案是：给文法符号附加**属性**，用**语义规则**规定属性之间的依赖，把翻译过程定义为“按依赖顺序对属性求值”。这套理论自 Knuth 1968 年的属性文法起，经龙书（Aho, Lam, Sethi, Ullman）的 SDD/SDT 二分化，成为编译器前端教科书的骨架。

但理论文本与工程实现之间有一道鸿沟。理论说“按依赖顺序求值”，却不说**谁来求、何时求、值存哪**。这三件事恰恰是语言工具（parser generator）必须做出的设计取舍，而取舍的结果决定了你在它之上能表达什么、不能表达什么。

ANTLR 4 是一个值得解剖的样本，因为它的架构选择格外清晰，而且其作者 Terence Parr 对这套理论有着明确的、经过权衡的立场。本文从 SDT 的理论基线出发，逐层说明 ANTLR 4 的四种机制（内嵌动作、Listener、Visitor、侧表）各自对应属性文法的哪个概念、能求出哪一类定义、以及在何处失效。

**核心论点**：ANTLR 4 的四种机制并不是四种编程风格，而是**同一条理论谱系上的四个位置**，区别仅在于“求值序由谁决定、**属性值**存在哪里”。理解这条谱系，就能在任意工具上判断某个翻译任务“理论上做得成还是做不成”，而不是靠试错。

---

## 1. 理论基线：五组必须分清的概念

### 1.1 SDD 与 SDT

- **语法制导定义（SDD）**：只声明产生式、属性与语义规则。它描述的是**属性之间的依赖关系**，本身不含求值算法。
- **语法制导翻译方案（SDT）**：把语义动作嵌入产生式右部，从而**固定了求值顺序**。它描述的是**算法**。

这个二分是整个话题的关键。SDD 是规范（specification），SDT 是实现（implementation）。同一个 SDD 可以有多份合法的 SDT，代价不同。教科书讨论“哪种 SDT 更好”，本质上讨论的是“对哪一类 SDD，这个求值序是可行的”。

ANTLR 4 的四种机制，可以精确地写成：
- 内嵌动作是 SDT；
- Listener 与 Visitor 是由 SDT 生成的求值器；
- 侧表是把 SDD 中“属性”这一概念从语法层迁移到宿主语言层之后的产物；

### 1.2 综合属性与继承属性

设产生式 $A \to X_1 X_2 \cdots X_n$：

- **综合属性**：$A.a = f(X_1.a_1, \dots, X_n.a_n)$。信息**自下而上**。
- **继承属性**：$X_i.b = f(A.a, X_1.a_1, \dots, X_{i-1}.a_{i-1})$。信息**自上而下、自左而右**。

注意继承属性的定义里**不含右兄弟**。这不是巧合，而是刻意设计的边界，它换来了下面这个东西。

### 1.3 S 属性与 L 属性

- **S 属性定义**：只用综合属性。可自底向上求值，与 LR 分析天然契合（归约时算，栈就是属性容器）。
- **L 属性定义**：允许继承属性，但只允许依赖父节点与**左**兄弟。可在一遍自顶向下、从左至右的遍历中求值。

L 即 Left。**L 属性定义的求值序，恰好是深度优先、从左至右遍历分析树的序。** 这句话是后面一切的支点，第 3 节会给出精确陈述。

### 1.4 带注释的语法树

龙书给出的关键中间概念：在分析树的每个节点上挂一组属性值，得到**带注释的语法树（annotated parse tree）**。求值就是在这棵树上做拓扑排序。有了这个视角，“一遍翻译”与“多遍翻译”的差别被消解为：**树是隐式的（遍历中即刻消失）还是显式的（能反复访问）**。

### 1.5 一遍与多遍：L 属性的硬边界

若某个属性依赖关系**不是 L 属性**，例如需要右兄弟的信息、需要在整个编译单元上先建立全局信息再回填(backpatch)引用，那么无论实现多聪明，**一遍遍历都做不完**。这是理论约束，不是工程缺陷。

一个常见的误判：把“用一遍 Listener 硬做”当作“实现得比较 hack”，实际上那是**在错误的求值序上求值**，得到的属性值可能在你察觉不到的地方是旧的或缺失的。第 8 节会把这类失败模式逐条对应到理论疏忽上。

---

## 2. ANTLR 4 的三个架构事实

在讨论机制之前，必须先接受 ANTLR 4 的架构给定条件。它们不是可以商量的事项。

**事实一：ALL(\*) 自适应预测。** 运行时用 ATN（增广转移网络）模拟来预测分支，支持直接左递归（自动改写为循环 + 优先级爬升）。语法层面是 LL 的，但表达力被工程手段大幅拉伸。

**事实二：默认总是构建完整的分析树。** 每个规则调用产生一个 `XxxContext` 对象，树上保留**全部**子节点，包括括号、实际使用的运算符 token、多余的分隔符。这是一棵**具体语法树（CST）**，不是抽象语法树（AST）。

**事实三：ANTLR 4 删掉了 ANTLR 2/3 的树语法与 `->` 重写规则。** 从分析树到目标结构的重构，全部下移到宿主机语言的代码层（`ParseTreeListener` / `ParseTreeVisitor`），只保留 `ParseTreePattern`、`XPath` 这类弱化的树查询能力。

事实三是本文全部张力的来源：**ANTLR 4 把“翻译”从文法层驱逐到了代码层**。于是 Listener 与 Visitor 不是可选的便利设施，而是这套工具唯一的 SDT 执行机构。

分析树节点的统一形状：

```
ParseTree
├── RuleContext              一个非终结符的展开（= 属性挂载点）
│   ├── getRuleIndex()       对应哪条产生式
│   ├── getParent()          上行通道
│   ├── getChild(i)          下行通道（位置访问）
│   ├── expr(0), expr(1)     同名子规则的按序访问
│   ├── ID(), op             终端节点的按名访问
│   └── getSourceInterval()  [start, stop] token 区间
└── TerminalNode             一个 Token
```

这张表值得记住的是：**`RuleContext` 就是带注释语法树里的“节点”，它是 SDT 中“属性属于节点”这一事实唯一的物理载体。** 后面所有机制，差别只在于“属性存进 `ctx`、存进栈、还是存进返回值”。

---

## 3. 支点：遍历序 = L 属性的求值序

这一节是全文的理论核心，值得单独陈述。

> **命题**：设 $T$ 为一棵分析树，考虑对其做深度优先、从左至右的遍历，产生事件序列 $\sigma = \langle \text{enter}(v_1), \ldots, \text{exit}(v_m) \rangle$。对文法上**任意** L 属性定义，存在一个只依赖 $\sigma$ 的求值策略：每个属性在它首次可用的那个事件点求值。

**为什么成立**（对节点深度归纳）：

- 继承属性 $X.b$ 只依赖父节点属性与左兄弟属性。走到 $\text{enter}(v_X)$ 时，父节点已经 `enter` 过（必要时其继承属性已就绪），从根到 $X$ 的所有左兄弟子树已经**完整走完**（`enter` 与 `exit` 都发生过，因此其综合属性也已就绪）。故 $\text{enter}$ 时刻，$X$ 的全部继承属性可求。
- 综合属性 $X.a$ 只依赖子节点属性。走到 $\text{exit}(v_X)$ 时，$X$ 的所有子孙节点都已 `exit`。故 $\text{exit}$ 时刻，$X$ 的全部综合属性可求。

**推论一**：一个同时具备 `enter` 与 `exit` 双回调的遍历器，其求值能力**精确等于** L 属性定义类。不多也不少。

**推论二**：这个求值序由**文法与遍历算法**共同固定，用户无法干预。因此任何非 L 的依赖图，在这个序下都求不出来，无论写多少代码。

**推论三**：若允许用户自己决定访问子节点的顺序（即自定义求值序），则可以在单遍递归下降的框架内，支持任何**无环**依赖图，只要它能在一次后序遍历中拓扑排序。这需要求值器把控制权交还给用户。

推论一是 Listener 的存在理由，推论三是 Visitor 的存在理由。二者不是“功能强弱”的差别，而是**求值序可否定制**的差别。

---

## 4. 四种机制

### 4.1 内嵌动作：最纯的 SDT，只有一遍

ANTLR 4 完整保留了龙书式的属性与动作语法：

```antlr
stat[int indent] returns [int width, List<String> lines]
locals [int tmpCount]
    : ID '=' expr ';'  { $width = $expr.v; $lines = $expr.code; }
    ;

expr returns [int v, List<String> code]
    : a=expr op=('*'|'/') b=expr
        { $v = compute($a.v, $op.text, $b.v);
          $code.add(newTemp() + " = " + $a.v + $op.text + " " + $b.v); }
    | INT { $v = Integer.parseInt($INT.text); }
    ;
```

- `[args]` → 继承属性，调用方传入
- `returns [...]` → 综合属性，通过 `$ctx.v` 或 `$rule.v` 读取
- `locals [...]` → 本次规则调用私有的中间状态（比显式栈好用得多）
- 类级动作 `@header` / `@members` → 全局状态与辅助方法

从 SDT 的角度看，**这是教科书 SDT 的字面实现**：动作内嵌在产生式右部，位置即求值时刻。等价类恰好是“一遍、L 属性、无分支裁剪、无上下文切换”的翻译。

它为什么在工程上被 Parr 强烈不推荐，理由全部可以从第 3 节推出：

1. **求值序被文法锁死**。任何非 L 依赖都做不成。
2. **语法与宿主语言绑定**，无法跨 target 复用。
3. **无多遍**。而现代语言的名字解析、类型推导几乎必然要多遍。
4. **分析树不可单独保留**，因此语法无法独立测试，也无法在树上做优化。
5. 错误恢复可能在部分匹配后执行动作，副作用不可撤销。

有两个技术细节值得澄清，因为它们常被误解：

- ANTLR 4 的预测阶段跑的是 ATN 模拟，**不执行动作**（但会求值语义谓词 `{...}?`）。因此不存在 ANTLR 3 时代“回溯导致动作重复执行”的经典陷阱。
- 语义谓词是绕过 LL 表达力限制的逃生舱，但它在预测期可能被反复求值，成本高且使语法不可静态分析。**能用左公因子或词法模式 `mode` 解决的，不要用谓词。**

内嵌动作还有一个被低估的用法：配合 `-no-listener -no-visitor` 与 `parser.setBuildParseTree(false)`，它是不建树、一遍发射的**最快路径**。这是“性能压倒可维护性”场景下的正解，而不是错误。

---

### 4.2 Listener：L 属性求值器的默认实现

```java
public interface ExprListener extends ParseTreeListener {
    void enterProg(ProgContext ctx);
    void exitProg(ProgContext ctx);
    void enterAddSub(AddSubContext ctx);
    void exitAddSub(AddSubContext ctx);
    // 每个规则一对
}
```

```java
ParseTreeWalker.DEFAULT.walk(new MyListener(), tree);
```

`ParseTreeWalker` 做的正是第 3 节的 $\sigma$：深度优先、从左至右、每节点恰好 `enter` 一次、`exit` 一次。因此：

$$\text{enter} \equiv \text{继承属性的求值点}, \qquad \text{exit} \equiv \text{综合属性的求值点}$$

一个 Listener 类同时维护“下行通道”（在 `enter` 里算继承属性）与“上行通道”（在 `exit` 里算综合属性），就等价于一个完整的 L 属性求值器。这是它设计上最优雅之处：双回调不是 API 对称性的审美选择，而是**双向数据流的物理映射**。

Listener 的三个能力边界，都可以从“求值序固定”这一条推出：

| 能力 | 原因 |
|---|---|
| 不能返回值 | 返回值是“把综合属性交给调用者”，而调用者是 Walker，不是用户 |
| 不能中断 | 中断即改变求值序（跳过后续节点），Walker 不允许 |
| 不能剪枝 | 同上 |
| 不能传参给子节点 | 继承属性只能走“压栈 → 子节点 `enter` 时读栈顶”这条绕路 |

于是所有属性都必须落在**字段**上。这就引出了下一个必须讲清的问题。

---

### 4.3 值栈：为什么属性必须是一个栈

这是 ANTLR 的 Listener 模型里最容易被当作“技巧”记住、实际上有严格理由的一点。

一个 Listener 对象是**单例**，在整棵树上只有一份。而“非终结符 $X$ 的属性”在树的不同位置有**多份**。因此：

> **不能用字段直接存某个非终结符的属性，因为字段只有一份，而属性有多份。**

字段只能存放两类东西：全局状态（临时变量计数器、输出缓冲区、符号表），以及“当前活跃节点”的状态。后者必须存储在**与树节点一一对应**的位置上。

有两条路：

**路径 A：侧表。** 属性直接标注在节点上：

```java
Map<ParserRuleContext, Value> attrs = new IdentityHashMap<>();
// enter/exit 时 attrs.put(ctx, v) / attrs.get(childCtx)
```

这在语义上**就是带注释的语法树**，只是把“字段”换成了哈希表。因为 `ParserRuleContext` 是引用类型且每次解析唯一，`IdentityHashMap` 的键与树节点构成一一对应，语义等价于给节点开字段。当属性的依赖关系不在栈序上（例如需要回头取某个已完成子树的属性）时，侧表比栈清晰得多，是**优先考虑**的方案。

**路径 B：栈。**

```java
public class ThreeAddrListener extends ExprBaseListener {
    private final Deque<String> vals = new ArrayDeque<>();   // 综合属性栈
    private int tmpSeq = 0;
    private final List<String> out = new ArrayList<>();

    @Override public void exitInt(IntContext ctx) {
        vals.push(ctx.INT().getText());
    }

    @Override public void exitAddSub(AddSubContext ctx) {
        String r = vals.pop(), l = vals.pop();        // 出栈序 = 右、左
        String t = "t" + (++tmpSeq);
        out.add(t + " = " + l + " " + ctx.op.getText() + " " + r);
        vals.push(t);
    }

    @Override public void exitParens(ParensContext ctx) {
        // 括号不产生代码，属性直接透传：什么都不做，栈顶即内层值
    }
}
```

栈的不变式值得写清楚，因为它解释了全部正确性：

> **不变式**：任一时刻，栈中元素数 = “已 `enter` 未 `exit`、且已压入属性”的节点数；栈顶 = 最近一次 `exit` 的节点的综合属性。

由深度优先左至右的遍历序，子节点按从左到右压栈，故出栈自然反转。**压栈顺序 = 子节点序，出栈顺序 = 逆子节点序**，这就是 `r = pop(); l = pop();` 的来历。写反是这类代码最典型的 bug（见第 8 节）。

栈这种形状天生适合**固定元数的表达式节点**：一元、二元运算写起来非常顺。它天生不适合需要“取第 $k$ 个子树属性”或“回头引用已完成子树”的场合，因为那些依赖不在栈的 LIFO 序上。这就是路径 A 存在的理由。

---

### 4.4 Visitor：把求值序的控制权交还给用户

```java
public interface ExprVisitor<T> extends ParseTreeVisitor<T> {
    T visitAddSub(AddSubContext ctx);
    T visitInt(IntContext ctx);
}
```

`ExprBaseVisitor<T>` 的默认实现是：

```java
public T visitAddSub(AddSubContext ctx) { return visitChildren(ctx); }

public T visitChildren(RuleNode node) {
    T result = defaultResult();
    for (int i = 0; i < node.getChildCount(); i++) {
        if (!shouldVisitNextChild(node, result)) break;
        result = aggregateResult(result, node.getChild(i).accept(this));
    }
    return result;
}
```

这段默认实现有两个后果必须记住：

1. **默认 `visitChildren` 丢弃所有子结果、返回 `defaultResult()`（通常是 `null`）**。如果你重写了 `visitXxx` 却没有显式调用 `visit(ctx.expr())`，**程序不会报错，只会静默产生 `null`**。这是 ANTLR Visitor 最常见、最难定位的缺陷。工程防护：让 `defaultResult()` 返回哨兵值，或在关键处 `requireNonNull`。
2. `shouldVisitNextChild(node, result)` 是内建的**剪枝钩子**——返回 `false` 即中止当前节点的子节点遍历。重写它可以实现“找到即停”的语义。

从 SDT 角度，Visitor 的三处对应关系是：

| 属性文法概念 | Visitor 中的载体 |
|---|---|
| 综合属性 | `visitXxx` 的**返回值** $T$ |
| 继承属性 | **构造参数**，或进入子作用域时**新建一个子 Visitor** |
| 每个节点的属性存储 | 返回值（无需存储）；需要跨节点访问时退回侧表 |

继承属性走构造参数的惯用法（作用域是典型场景）：

```java
class TypeCheckVisitor extends ExprBaseVisitor<Type> {
    final Scope scope;
    TypeCheckVisitor(Scope s) { this.scope = s; }

    @Override public Type visitBlock(BlockContext ctx) {
        return new TypeCheckVisitor(new Scope(scope)).visitChildren(ctx);
    }

    @Override public Type visitVarDecl(VarDeclContext ctx) {
        Type t = visit(ctx.type());
        scope.define(ctx.ID().getText(), t);   // 副作用写回父可见的 scope
        return t;
    }
}
```

**但 Visitor 真正的理论增量不在“有返回值”，而在于它可以重排求值序。** 举一个最能说明问题的例子：

```java
@Override
public Type visitAssign(AssignContext ctx) {
    Type rhs = visit(ctx.expr());     // 先求右操作数（右兄弟）
    Type lhs = visit(ctx.lvalue());   // 后求左操作数
    ...
}
```

假如某条语义规则要求“先知道右操作数的类型，才能决定左操作数如何解释”，这在 Listener 中**做不到**（Walker 固定先左后右），在 Visitor 中写出来就成立。因此：

> **Listener 的求值能力 = L 属性定义类；Visitor 的求值能力 = 可在一次后序遍历中拓扑排序的任意无环依赖图。**

这就是为什么 Visitor 是“表达式求值与单遍翻译”的默认选择。一旦你的翻译一旦涉及“需要先看右边”，Listener 就出局，无需再讨论代码量。

它的代价是样板代码：每个分支都要手写 `visit`。对于分支众多的文法，这部分代码量不可忽略。

---

### 4.5 侧表与“属性的两种形态”

把 4.3 的路径 A 与 1.4 的带注释语法树并置，可以得到一个重要观察：

> ANTLR 4 中属性之所以能被任意标注、读取、跨节点共享，是因为 `ParseTree` 节点是**引用类型且每次解析唯一**。因此 `IdentityHashMap<ParseTree, Attr>` 在语义上与“给节点加字段”完全等价。**侧表不是权宜之计，而是带注释语法树这一理论构造的直接实现。**

侧表的实用价值在多遍分析中尤其明显：多个分析器在多遍之间共享同一份 `Map`，无需修改树、无需重解析，就是教科书里“属性被逐遍填入”的过程。这比“每个 Visitor 各自一个字段”健壮得多，因为它把属性的**存在性**与**计算它的那遍**解耦了。

由此还可以引出属性的另一种形态，它在龙书第 6 章里被反复使用，但常被忽略：

> **属性可以是值，也可以是引用。**

符号表就是一个极端的例子：把“标识符的类型”作为属性存进树，代价是每个引用点都持有一份拷贝；把“指向符号表条目的指针”作为属性，则属性值是一个引用，真正的信息在全局表中，且可以**延迟填充**。

这一招的威力在于：**它把大量非 L 依赖伪装成 L 属性。** 诸如 C 的 `typedef` 歧义、Java 的类成员互相引用、前向声明，都可以这样处理：

- 第一遍：只建立“名字 → 条目”的映射，引用点填入**未解析占位符**（这是纯 L 属性——每个引用点只需知道自己这个名字）。
- 第二遍：遍历所有引用点，从全局表解析。

两遍之所以必要，不是实现者偷懒，而是“引用 → 定义”这条依赖在**同一遍内是有环的**，无法拓扑排序。

---

## 5. 非 L 属性：什么时候必须多遍

把第 4 节收拢，可以得到一张关于“可行性”的判据表。这张表的价值在于：它能在你写第一行代码之前就告出结论。

| 你的依赖图 | 最少遍数 | 可用机制 |
|---|---|---|
| 纯综合属性（信息只向上） | 1 | 任何：Listener `exit`、Visitor 返回、内嵌动作 |
| L 属性（允许向下、向左） | 1 | Listener `enter`+`exit`、Visitor、内嵌动作 |
| 依赖右兄弟但无环 | 1 | **只能用 Visitor**（自定义求值序）或内嵌动作重排 |
| 依赖图跨多棵子树但有环/需全局信息 | ≥2 | Visitor 建 AST 或侧表，然后多遍 |
| 需要“先收集全部声明，再检查全部使用” | ≥2（通常是 3） | 建 AST / 侧表 + 多遍 |

第三行是最容易被低估的一格：它说明 Visitor 相对于 Listener 的差异**不是风格，而是表达能力**。

至于第五行，现实的编译器前端典型是：

1. 解析 → CST
2. Visitor 建 AST（丢弃括号、标点、冗余层级）
3. 遍历 AST：建符号表（声明收集）
4. 遍历 AST：名字解析 / 类型检查（使用检查）
5. 遍历 AST：发射 IR（三地址码 / SSA）

**一旦第 2 步完成，ANTLR 生成的代码就可以彻底退场。** 这是所有真实编译器的共同形态，也是 Parr 反对内嵌动作的根本理由——不是美学，是“语言语义一遍算不完”这个事实。

---

## 6. CST 与 AST：一个必须跨过的界面

第 2 节的事实二意味着 ANTLR 交给你的树**不是** SDT 理论假定的那棵树。差别有三：

1. **它保留了具体语法**。`(1+2)` 的 `ParensContext` 里有真实的括号 token；每个运算符是一个 `TerminalNode`。节点数与层级都比抽象树多。
2. **它被左递归改写污染**。`expr: expr op expr` 在内部被改成循环 + 优先级爬升，因此 `ctx.expr(0)` / `ctx.expr(1)` 的语义要按 ANTLR 的改写规则理解，**不能按你写的原文法直觉理解**。这是新手最容易踩的一处概念错位。
3. **错误恢复会造出“畸形树”**。默认 `DefaultErrorStrategy` 会插入或删除 token 后继续解析，因此 `ctx.expr()` 可能返回 `null`。**你的求值器必须容忍属性缺失**——这在 SDT 的形式模型里不存在，是工程现实。

因此，“Visitor 的第一件工作”通常就是**把 CST 折叠成 AST**：

```java
class AstBuilder extends ExprBaseVisitor<AstNode> {
    @Override public AstNode visitAddSub(AddSubContext ctx) {
        return new BinOp(ctx.op.getText(), visit(ctx.expr(0)), visit(ctx.expr(1)));
    }
    @Override public AstNode visitInt(IntContext ctx) {
        return new Num(Integer.parseInt(ctx.INT().getText()));
    }
    @Override public AstNode visitParens(ParensContext ctx) {
        return visit(ctx.expr());      // 括号在抽象树里消失
    }
}
```

这一遍的语义角色很清楚：**它是一次纯 L 属性的翻译，目标树是下一次 SDT 的输入。** 之后的类型检查、优化、代码生成，全部在你自己定义的节点类型上做，不再受 ANTLR 的树形状约束。

---

## 7. 选择：由 SDT 性质导出的决策图

```
翻译任务
│
├─ 依赖只向上（纯综合）？
│   ├─ 是，且语法无需复用、无需多遍 ──→ 内嵌动作 + 不建树（最快）
│   └─ 是，但需解耦/跨 target ───────→ Listener（exit）
│
├─ 依赖包含继承属性，且严格 L 属性？
│   ├─ 状态是“当前作用域/当前标签”之类 ─→ Visitor + 构造参数（子作用域新建）
│   ├─ 状态是局部值序列（表达式）  ─────→ Listener + 值栈
│   └─ 属性需要跨节点回头访问  ─────────→ 侧表（IdentityHashMap）
│
├─ 需要依赖右兄弟，或需剪枝/中途返回？
│   └─ 是 ─────────────────────────→ Visitor（必须）
│
├─ 依赖图有环 / 需全局信息？
│   └─ 是 ─────────────────────────→ 建 AST，多遍（≥2）
│
└─ 只需按 token 区间做文本替换（格式化、重构）？
    └─ 是 ─────────────────────────→ TokenStreamRewriter（不属于 SDT，属源码到源码）
```

工程上的配套开关：

- 默认只生成 `ParseTreeListener`；加 `-visitor` 同时生成 `ParseTreeVisitor`；**`-no-listener -visitor` 只生成 Visitor**，能省一半生成代码，写编译器时推荐后者。
- 纯发射、不要树：`parser.setBuildParseTree(false)`，配合 `parser.addParseListener(...)` 边解析边回调——这是 L 属性求值的极限形态（连树都不存在）。
- 性能：`PredictionMode.SLL` 失败回退 LL 的两段式解析通常有显著加速，属于 `parser.getInterpreter()` 的实例级设置。

---

## 8. 失败模式：每条对应一个理论疏忽

最后把实践中最常见的坑，逐条映射回它背后的属性文法概念。**每个 bug 都能在理论上被提前预言**，这是这套视角最实际的收益。

| 症状 | 理论原因 |
|---|---|
| Visitor 静默返回 `null` | 综合属性未定义：你重写了 `visitXxx` 却未调用 `visit` 子节点，依赖图中出现了“无定义的属性引用”。默认 `visitChildren` 丢弃结果，所以没有报错。 |
| 不用 `#Label` 标签，`visitXxx` 里满是 `ctx.getChild(1)` | 属性定义退化为“按位置索引”。语义规则本应绑定到产生式分支，此处被绑定到子节点下标，语法一改即崩。 |
| Listener 里“先算子节点再取右兄弟的属性”，结果拿到旧值 | 在固定求值序（L 序）上求一个非 L 的依赖。读到的不是新算的值，而是上一次 `exit` 残留的值。**这类 bug 不崩溃，只算错。** |
| 值栈取出的左右操作数装反 | 栈不变式被破坏：压栈顺序=子节点序，出栈即逆序，故必须 `r = pop(); l = pop();`。 |
| 把 CST 当 AST 用，做优化时发现节点数不对、看不清结构 | 传递函数的定义域错了。SDD 假定的是抽象树；CST 里有括号、标点、左递归改写产生的循环层。 |
| Visitor 遇到 `ctx.expr() == null` 崩溃 | 忽略了错误恢复会构造部分畸形的树。形式模型里不存在“属性缺失”，工程里必然存在，求值器必须容忍。 |
| 深左递归表达式导致栈溢出 | 递归下降求值器（Visitor）的空间开销是树高。数千项求和时，显式栈的 Listener 更稳。 |
| 内嵌动作里做了不可撤销的副作用 | 错误恢复可能在产生式**部分匹配**后执行动作。动作应视为“可能被丢弃的候选求值”。 |

---

## 9. 结语

把 ANTLR 4 的四种机制放回属性文法的坐标系里，全貌是一个很简洁的谱系：

```
                    求值序由谁决定          能求的属性类
内嵌动作            文法                    单遍 L 属性（无裁剪）
Listener            遍历器（固定 L 序）      L 属性（含 enter 下行通道）
Visitor             用户（可重排）           一次后序遍历内可拓扑排序的无环图
建 AST + 多遍       用户（任意）             任意无环依赖图
```

而这三条分界线，分别对应 SDD/SDT 二分、S 属性/L 属性二分、以及“L 属性的硬边界”。教科书把它们讲成理论；ANTLR 4 把它们讲成了 API 的形状。

所以当有人问“该用 Listener 还是 Visitor”，正确的回答方式不是比较代码量，而是先回答一个问题：**你要算的属性，依赖图是什么形状？**

依赖只向上，两者都行，选代码少的。依赖含右兄弟，只能用 Visitor。依赖有环，两遍起步，先把 CST 折成 AST。这个判断一旦做出，API 的选择就是推论，不再是偏好。