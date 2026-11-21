# 侧表（Side Table）：编译器如何在树之外存放属性

---

## 引子：属性到底放在哪里

前几篇反复提到一个结论：语法制导翻译（Syntax-Directed Translation, SDT）的本质，是在语法树上计算**属性**（attribute）。类型、符号、常量值、生成的代码，都是属性。

理论只说“属性属于节点”，没有说**属性存在哪里**。工程上有两种基本做法：

```java
// 做法一：把属性写成节点的字段
class BinaryExpr extends Expr {
    Expr lhs, rhs;
    Type type;          // 类型检查之后才有值
    Symbol resolved;    // 名字解析之后才有值
}

// 做法二：节点只保存语法，属性放在节点之外的表里
class BinaryExpr extends Expr { Expr lhs, rhs; }

Map<Expr, Type>     types   = new IdentityHashMap<>();
Map<Expr, Symbol>   symbols = new IdentityHashMap<>();
```

第二种做法里，那张“以节点为键、以属性为值”的表，就叫**侧表**（side table），也常被称为旁表、辅助表（auxiliary table）、属性映射（attribute map）或外部属性存储（external attribute storage）。

这个设计看上去只是换了个存放位置，实际上牵涉到多遍编译（multi-pass compilation）、不可变数据结构（immutable data structure）、增量编译（incremental compilation）和内存布局等一系列问题。Go 的 `go/types`、rustc 的 `TypeckResults`、TypeScript 的类型检查器、ANTLR 的 `ParseTreeProperty`、LLVM 的元数据存储，都是侧表的实例。

本文从定义讲起，经过理论来源、动机、实现细节和真实案例，最后给出一套选型判据。

---

## 一、定义与理论来源

### 1.1 定义

> **侧表**是一种映射（mapping），把程序表示中的某个实体（通常是语法树节点，也可以是符号、IR 指令、基本块）映射到附加在它上面的信息，而这些信息**不存储在实体本身的数据结构中**。

与之相对的做法叫**侵入式存储**（intrusive storage）：属性直接作为节点的成员字段（member field）。

### 1.2 理论来源：带注释的语法树

龙书在讲 SDT 时引入了**带注释的语法树**（annotated parse tree），也叫装饰语法树（decorated syntax tree）：在每个节点上挂一组属性值，翻译过程就是按依赖关系给这棵树“填值”。

关键在于：理论中的“挂”是**逻辑上的**关联，并不要求物理上存进节点。从数学角度看，一个属性 `type` 就是一个函数：

$$
\text{type} : \text{Node} \rightarrow \text{Type}
$$

侵入式字段与侧表，是这个函数的两种实现：

| 实现方式 | 函数的物理形态 |
|---|---|
| 侵入式字段 | 函数值分散存放在每个定义域元素（节点）内部 |
| 侧表 | 函数作为一个整体，以查找表（lookup table）的形式独立存放 |

Knuth 在 1968 年提出属性文法（attribute grammar）时，也把属性看作附着在语法树上的值的集合。后来的属性文法系统（如 Kiama）干脆把属性实现为**带缓存的函数**（memoized function），缓存本身就是一张侧表。

所以侧表不是工程上的权宜之计，而是“属性即函数”这一理论观点最直接的实现。

### 1.3 与表达式问题的关系

编程语言理论里有一个著名的**表达式问题**（expression problem）：在不修改已有代码的前提下，如何同时扩展数据类型的种类和作用于其上的操作。

侧表从一个侧面回答了这个问题的一半：**新增一种属性时，不需要修改节点类型的定义**。每增加一个分析遍，只需新建一张表，AST 的类定义保持不变。

---

## 二、为什么需要侧表：侵入式字段的五个问题

侵入式字段简单、直接、访问快，Clang 的 `Expr` 就直接保存了 `QualType`。但随着编译器变复杂，它会遇到下面这些问题。

### 2.1 节点膨胀（node bloat）

每增加一种分析，节点就多一个字段。一个成熟编译器可能有几十种属性：类型、解析结果、常量值、是否被捕获（captured）、是否可变借用、源位置映射、诊断标记……

大部分属性只对少数节点有意义。比如“常量值”只对常量表达式有效，“闭包捕获列表”只对 lambda 有效。把它们全部写成字段，意味着**绝大多数节点为用不到的字段付出内存**。

侧表天然是**稀疏的**（sparse）：只有真正拥有该属性的节点才占用表项。

### 2.2 部分初始化（partial initialization）

在多遍编译中，字段在不同的时刻才变得有效：

```
解析完成后：  type == null, resolved == null
名字解析后：  type == null, resolved != null
类型检查后：  type != null, resolved != null
```

节点在生命周期的大部分时间里处于“半初始化”状态。某个遍误读了尚未填充的字段，得到的是 `null` 或默认值，错误往往在很远的地方才暴露。

侧表把这种状态显式化：**一张表存在，说明对应的遍已经运行过**。如果代码签名要求传入 `TypeTable`，那么在类型检查之前调用它，在编译期就会失败，而不是运行时读到空值。这实际上是把**遍的执行顺序**（phase ordering）编码进了类型系统。

### 2.3 不可变的树（immutable tree）

现代编译器和语言服务越来越倾向于让语法树**不可变**：

- 不可变的树可以在多个线程之间安全共享；
- 可以在编辑器中复用未修改的子树（结构共享，structural sharing）；
- 可以被缓存、哈希、序列化。

Roslyn（C# 编译器）的红绿树（red-green tree）和 rust-analyzer 的语法树都是不可变的。在不可变的树上，**根本无法写入字段**，语义信息只能放在树之外。Roslyn 因此把语义信息放在单独的 `SemanticModel` 中，语法树（`SyntaxTree`）只负责语法。

### 2.4 树不归你所有（foreign tree）

很多时候，节点类型是别人定义的：

- ANTLR 生成的 `XxxContext` 类每次重新生成都会被覆盖；
- 使用标准库的 AST（如 Go 的 `go/ast`、Python 的 `ast` 模块）时，无法修改节点定义；
- 多个工具（编译器、格式化器、linter）共享同一套 AST，各自需要不同的属性。

这时侧表是**唯一可行的方案**。

### 2.5 多个工具、多份结果

同一棵树可能被分析多次，每次的结果不同：在不同的编译配置下做类型检查，或者对同一段代码尝试多种推断策略（speculative type checking，推测性类型检查）。侵入式字段只能存一份结果；侧表可以同时存在多张，互不干扰，失败的那张直接丢弃即可。

---

## 三、侧表的核心设计：选什么作为键

侧表的所有工程难点，几乎都集中在一个问题上：**用什么来标识一个节点？**

### 3.1 对象标识（object identity）

最直接的做法是用节点对象本身（即它的内存地址或引用）作为键。

**必须使用标识相等（identity equality），而不是结构相等（structural equality）。** 考虑下面的代码：

```c
x = x + 1;
```

两个 `x` 在结构上完全一样（都是“名为 x 的标识符”），但它们是两个不同的节点：一个是赋值目标，一个是读取操作数，属性完全不同。如果侧表按结构相等比较，两个 `x` 会冲突成同一个表项。

各语言中的正确做法：

| 语言 | 正确的容器 / 做法 |
|---|---|
| Java | `IdentityHashMap`（按 `==` 比较，不调用 `equals`） |
| C++ | `std::unordered_map<const Node*, T>`、LLVM `DenseMap<const Node*, T>` |
| Go | `map[*ast.Ident]T`（指针作为键，天然是标识相等） |
| Python | 节点对象的默认 `__hash__` 基于标识；注意下面的陷阱 |
| Rust | 一般不用指针作键，改用稠密 ID（见 3.2） |

**Python 的一个陷阱**：用 `@dataclass` 定义 AST 节点时，默认 `eq=True` 会让类变成不可哈希（unhashable）；如果加上 `frozen=True`，哈希又变成按字段计算的结构哈希，两个 `Name("x")` 会撞成同一个键。用作侧表键的节点类，应声明 `@dataclass(eq=False)`，保留基于标识的哈希。另外不要用 `id(node)` 作键：对象被回收后，地址可能被新对象复用。

### 3.2 稠密整数 ID（dense integer ID）

另一种做法是给每个节点分配一个连续的整数编号，侧表就变成一个**按编号索引的数组**：

```rust
// 类型安全的索引：不同实体的 ID 不能混用
#[derive(Copy, Clone, PartialEq, Eq, Hash)]
struct ExprId(u32);

struct TypeTable {
    types: Vec<Option<Type>>,   // 下标就是 ExprId
}

impl TypeTable {
    fn get(&self, id: ExprId) -> Option<&Type> {
        self.types[id.0 as usize].as_ref()
    }
}
```

优点非常明显：

- **访问快**：数组下标访问，没有哈希计算；
- **缓存友好**（cache-friendly）：属性在内存中连续存放，按顺序遍历时局部性（locality）很好；
- **内存紧凑**：不需要存储键本身；
- **可序列化**：整数可以写进磁盘缓存，指针不行。

这种做法通常和**竞技场分配**（arena allocation）配合使用：所有节点存放在一个大向量里，节点之间用索引而不是指针相互引用。rustc 的 `IndexVec<I, T>` 就是这种“以新类型索引（newtype index）为下标的向量”。

缺点是：稀疏属性会浪费空间，此时可改用 `HashMap<ExprId, T>`。

### 3.3 分层 ID（hierarchical ID）

大型编译器还会使用分层的 ID，典型代表是 rustc 的 `HirId`：

```rust
pub struct HirId {
    pub owner: OwnerId,          // 所属的顶层条目（函数、结构体等）
    pub local_id: ItemLocalId,   // 在该条目内部的局部编号
}
```

把 ID 拆成“所有者 + 局部编号”有两个好处：

1. **侧表可以按所有者分片**（sharding）：每个函数一张小表，用 `ItemLocalId` 做稠密索引；
2. **增量编译时 ID 稳定**：修改函数 A 的函数体，不会导致函数 B 内部节点的编号变化，B 的缓存结果依然有效。

如果使用全局连续编号，在文件开头插入一个节点，后面所有编号都会偏移，整个缓存失效。

### 3.4 三种键的比较

| 键的类型 | 访问速度 | 内存 | 可序列化 | 稳定性 | 典型使用者 |
|---|---|---|---|---|---|
| 对象指针 / 引用 | 中（哈希） | 中 | 否 | 节点存活期间稳定 | Go `types.Info`、ANTLR、Java 工具 |
| 全局稠密 ID | 快（数组） | 低 | 是 | 结构变化时失效 | TypeScript 检查器 |
| 分层 ID | 快 | 低 | 是 | **增量编译友好** | rustc `HirId` |

---

## 四、真实编译器中的侧表

### 4.1 Go：`types.Info`，教科书式的侧表

Go 标准库的 `go/types` 是最适合学习侧表的样本，因为它把这个设计直接暴露成了公开 API：

```go
info := &types.Info{
    Types: make(map[ast.Expr]types.TypeAndValue), // 表达式 → 类型与常量值
    Defs:  make(map[*ast.Ident]types.Object),     // 定义处的标识符 → 对象
    Uses:  make(map[*ast.Ident]types.Object),     // 使用处的标识符 → 对象
    Scopes: make(map[ast.Node]*types.Scope),      // 节点 → 作用域
}

conf := types.Config{Importer: importer.Default()}
pkg, err := conf.Check("example", fset, files, info)

// 检查完成后，通过侧表查询任意表达式的类型
tv := info.Types[someExpr]
fmt.Println(tv.Type, tv.Value)
```

几个值得注意的设计：

- **AST 完全不变**：`go/ast` 的节点只描述语法，类型检查器不修改它们；
- **按需提供**：调用者只初始化自己需要的表，传入 `nil` 的表不会被填充，省去不必要的开销；
- **定义与使用分开**：`Defs` 和 `Uses` 是两张表，对应名字解析中“声明点”和“引用点”这两类不同的节点。

gopls、staticcheck 等工具都基于这套侧表工作，同一份 AST 可以被不同工具各自分析。

### 4.2 rustc：`TypeckResults`

rustc 对每个函数体做类型检查后，产生一个 `TypeckResults` 结构，内部是一组以 `ItemLocalId` 为键的侧表（简化）：

```rust
pub struct TypeckResults<'tcx> {
    pub hir_owner: OwnerId,
    node_types:          ItemLocalMap<Ty<'tcx>>,                 // 节点 → 类型
    type_dependent_defs: ItemLocalMap<Result<(DefKind, DefId), ErrorGuaranteed>>, // 方法调用解析到哪个定义
    adjustments:         ItemLocalMap<Vec<Adjustment<'tcx>>>,    // 自动解引用、自动借用等隐式调整
    pat_binding_modes:   ItemLocalMap<BindingMode>,              // 模式绑定是按值还是按引用
    // ……
}
```

HIR（High-level IR）本身是不可变的，类型信息全部存放在这里。`adjustments` 这张表很能说明侧表的价值：Rust 的自动解引用（auto-deref）和自动借用（auto-ref）不会改写 HIR 树，而是作为“附加在节点上的隐式操作”记录在侧表中，后续生成 MIR 时再读取并展开。

`TypeckResults` 本身又是查询系统（query system）`typeck(def_id)` 的返回值，会被缓存和增量复用（见第六节）。

### 4.3 TypeScript：`NodeLinks`

TypeScript 编译器的类型检查器使用懒分配 ID 的数组侧表（简化）：

```ts
const nodeLinks: NodeLinks[] = [];

function getNodeLinks(node: Node): NodeLinks {
    const nodeId = getNodeId(node);   // 首次访问时为节点分配一个整数 ID
    return nodeLinks[nodeId] || (nodeLinks[nodeId] = new NodeLinks());
}
```

`NodeLinks` 中保存解析出的类型、解析出的符号、各种检查标志等。符号也有类似的 `SymbolLinks`。

这里有两个细节：ID 是**懒分配**（lazy allocation）的，只有被检查器访问过的节点才有编号；`NodeLinks` 对象也是按需创建的，所以未被检查的代码几乎不占用额外内存。

### 4.4 ANTLR：`ParseTreeProperty`

ANTLR 4 直接提供了侧表工具类 `ParseTreeProperty<V>`，内部就是 `IdentityHashMap`。前面讨论过，Listener 的方法没有返回值，属性只能放在别处，这个类就是为此设计的：

```java
public class EvalListener extends ExprBaseListener {
    private final ParseTreeProperty<Integer> values = new ParseTreeProperty<>();

    @Override public void exitInt(ExprParser.IntContext ctx) {
        values.put(ctx, Integer.valueOf(ctx.INT().getText()));
    }

    @Override public void exitAddSub(ExprParser.AddSubContext ctx) {
        int l = values.get(ctx.expr(0));   // 直接按节点读取，不依赖栈顺序
        int r = values.get(ctx.expr(1));
        values.put(ctx, ctx.op.getType() == ExprParser.ADD ? l + r : l - r);
    }

    @Override public void exitParens(ExprParser.ParensContext ctx) {
        values.put(ctx, values.get(ctx.expr()));   // 括号：属性透传
    }
}
```

和“值栈”方案相比，侧表的好处在于**不依赖压栈和出栈的顺序**：要哪个子节点的属性，就按节点去取，不存在左右操作数取反的问题。代价是多了哈希开销，并且属性在遍历结束后仍然存在（需要时可用 `removeFrom` 释放）。

### 4.5 Clang 与 LLVM：侵入式为主，侧表为辅

Clang 是“以侵入式为主”的代表：`Expr` 直接保存类型，`DeclRefExpr` 直接保存指向的声明。这是出于性能考虑：类型几乎每个表达式都要用，存进节点访问最快。

但即便如此，Clang 和 LLVM 在很多地方仍然使用侧表：

- **Clang 的属性（attribute）**：声明上的 `__attribute__((...))` 列表存放在 `ASTContext` 中一张以 `Decl*` 为键的映射里，`Decl` 本身只保留一个“是否有属性”的标志位；
- **Clang 的记录布局缓存**：`ASTContext::getASTRecordLayout()` 计算结构体布局后，按 `RecordDecl*` 缓存在一张 `DenseMap` 中；
- **Clang 的父节点映射**：AST 节点不存父指针，需要时由 `ParentMapContext` 一次性构建一张“子节点 → 父节点”的侧表；
- **LLVM 的指令元数据**：除调试位置外，指令上附加的元数据（metadata）存放在 `LLVMContext` 内部一张以值为键的映射里，`Value` 对象只保留一个标志位表示“我有元数据”；
- **LLVM 的分析结果**：支配树（`DominatorTree`）、循环信息（`LoopInfo`）不存储在 IR 中，而是由分析管理器（analysis manager）按函数缓存。从概念上说，这是以“函数”为键的侧表。

这里体现了一个常见的混合策略：**高频、几乎每个节点都有的属性用字段；低频、稀疏、可选的属性用侧表，节点上只留一个标志位作为快速判断。**

---

## 五、侧表的生命周期问题

侧表与它所描述的对象是分开存放的，这带来了侵入式字段不会遇到的问题：**两者的生命周期可能不一致**。

### 5.1 悬垂键（dangling key）

如果节点被删除，而侧表中还保留着以它为键的表项，就形成了悬垂引用（dangling reference）。在 C++ 中，更危险的情况是：

1. 节点 A 被删除，其地址被释放；
2. 新节点 B 恰好分配在同一地址；
3. 侧表查询 B 时，读到的是 A 的旧属性。

这类问题被称为地址复用（address reuse），类似并发编程中的 ABA 问题，不会崩溃，只会悄悄地算错。

### 5.2 LLVM 的解决方案：值句柄

LLVM 的 IR 经常被优化遍改写：指令被删除、被替换（Replace All Uses With, RAUW）。为此 LLVM 提供了**值句柄**（value handle）机制：

| 工具 | 行为 |
|---|---|
| `WeakVH` / `WeakTrackingVH` | 值被删除时，句柄自动置空；后者在 RAUW 时还会跟随新值 |
| `AssertingVH` | 值被删除时，如果句柄仍然存在就触发断言，用于发现悬垂引用 |
| `ValueMap<K, V>` | 以值句柄为键的映射；值被删除或替换时，通过回调自动更新表项 |

这相当于让被引用的对象在销毁时“通知”所有引用它的侧表。

### 5.3 其他语言的做法

- **Java**：`WeakHashMap` 让键在不再被其他地方引用时自动移除（注意它按 `equals` 比较，用作节点侧表时要确认节点类没有重写 `equals`）；
- **稠密 ID 方案**：节点不会真的被释放（竞技场中只增不减），或者通过**代际计数**（generation counter）检测失效：ID 由“下标 + 代际号”组成，下标被复用时代际号递增，旧 ID 自然失效；
- **最简单的方案**：让侧表和树的生命周期严格绑定。树被重写之后，丢弃旧侧表、重新计算。这是大多数前端的实际做法，因为前端的树在分析期间通常不会被修改。

### 5.4 树变换之后怎么办

如果一个遍把 AST 改写成了新的树（比如去语法糖，desugaring），旧侧表中的键全部指向旧节点。常见的处理方式有三种：

1. **在变换之前把所需信息“下沉”到新树中**，变换后丢弃旧侧表；
2. **维护一张“新节点 → 旧节点”的溯源表**（provenance map），需要时回查，诊断信息常用这种方式定位源代码；
3. **改用新的中间表示**，在新 IR 上重新建立侧表。rustc 在 AST → HIR → THIR → MIR 的每一步都这样做。

---

## 六、从侧表到查询系统

把侧表再推进一步，就得到了现代编译器中越来越常见的**查询系统**（query system），也叫按需求值（demand-driven evaluation）架构。

### 6.1 侧表是一种缓存

回到第一节的观点：属性是一个函数 `type: Node → Type`。侧表是这个函数的**缓存**。

如果这个函数不是由某个“遍”一次性批量算完，而是**在第一次被查询时才计算，然后缓存结果**，那么侧表就变成了**记忆化**（memoization）的缓存：

```rust
fn type_of(db: &Database, id: ExprId) -> Type {
    if let Some(t) = db.type_cache.get(&id) {   // 命中侧表
        return t.clone();
    }
    let t = compute_type(db, id);               // 计算时可能递归查询其他节点
    db.type_cache.insert(id, t.clone());        // 写入侧表
    t
}
```

这就是 Kiama 等属性文法库实现属性的方式，也是**引用属性文法**（reference attribute grammar）系统 JastAdd 中缓存属性（cached attribute）的思想。

### 6.2 依赖追踪与增量编译

再加上一项能力：**记录每个查询读取了哪些输入**，就能在输入改变时只重新计算受影响的部分。这正是：

- rustc 的查询系统（`tcx.typeck(def_id)`、`tcx.type_of(def_id)` 等）；
- rust-analyzer 使用的 Salsa 框架；
- Roslyn 按需计算并缓存语义信息的方式。

在这些系统中，“遍”的概念被淡化了：没有“先跑名字解析、再跑类型检查”的固定顺序，只有一组相互调用的查询，以及它们背后一张张带依赖信息的侧表。

从理论上看，这也解决了前文多次提到的问题：**属性的求值顺序不再由遍历顺序决定，而是由依赖关系自动决定**。只要依赖关系无环，按需求值就能算出结果，这恰好对应属性文法理论中最一般的求值策略。

### 6.3 演进路线

```
侵入式字段  →  批量填充的侧表  →  懒计算的侧表  →  带依赖追踪的查询系统
（单遍、可变树）  （多遍、不可变树）   （按需求值）       （增量编译、IDE）
```

每往右一步，属性与树的耦合就更松一些，系统的灵活性就更高一些，实现的复杂度也更高一些。

---

## 七、常见陷阱

| 陷阱 | 原因 | 对策 |
|---|---|---|
| 两个同名标识符共享了属性 | 侧表按结构相等比较键 | 使用 `IdentityHashMap`、指针键或唯一 ID |
| Python 节点无法放入字典，或互相冲突 | `@dataclass` 改变了默认哈希行为 | 节点类声明 `eq=False` |
| 查询到不属于自己的属性 | 节点释放后地址被复用 | 让侧表与树同生命周期；或使用值句柄、代际 ID |
| 某个遍读到空值 | 在填充侧表的遍运行之前就读取了 | 把侧表作为显式参数传递，用类型系统约束遍的顺序 |
| 内存持续增长 | 树已丢弃，侧表仍持有节点引用 | 侧表随编译单元一起释放；或使用弱引用 |
| 树变换后属性全部丢失 | 侧表的键仍指向旧节点 | 变换前下沉信息、维护溯源表，或在新 IR 上重建 |
| 性能低于预期 | 高频属性每次访问都要哈希 | 高频属性改为字段，或改用稠密 ID 数组 |
| 并发访问出错 | 多个线程同时写入同一张表 | 每个遍、每个函数使用独立的表，合并时再加锁 |

---

## 八、选型判据

面对一个具体属性，可以按下面的问题逐一判断：

| 问题 | 倾向字段 | 倾向侧表 |
|---|---|---|
| 是否几乎每个节点都有这个属性？ | 是 | 否（稀疏） |
| 访问是否极其频繁、对性能敏感？ | 是 | 否 |
| 树是否可变、是否归你所有？ | 可变且自有 | 不可变，或由工具生成 |
| 属性是否只在某一遍之后才有效？ | 否 | 是（用表的存在表示遍已运行） |
| 是否需要多份结果（推测性检查、多配置）？ | 否 | 是 |
| 是否需要增量编译、磁盘缓存？ | 否 | 是（配合稳定 ID） |
| 是否有多个工具共享同一棵树？ | 否 | 是 |

再给出几条实践建议：

1. **语法归语法，语义归语义。** AST 只存放解析得到的信息，分析结果尽量放在侧表或独立结构中。这样 AST 可以被格式化器、linter、编译器共同使用。
2. **高频属性可以例外。** 如果每个表达式都有类型，且类型几乎在每一步都要读取，像 Clang 一样直接存进节点是合理的工程取舍。
3. **从一开始就设计稳定 ID。** 如果预期将来要做 IDE 支持或增量编译，用指针作键会在日后带来很大的迁移成本。
4. **把侧表当作遍的输出。** 让每个遍返回一个结果对象（如 `TypeckResults`、`types.Info`），而不是修改全局状态。遍之间的依赖关系因此变得清楚可见。
5. **低频属性配合标志位。** 节点上保留一个比特位表示“侧表中有我的条目”，避免对大量没有该属性的节点做无效查找。

---

## 结语

侧表解决的问题，归根到底只有一个：**把“某个节点有什么属性”与“这个节点是什么”分开存放。**

这种分离在理论上源于属性文法“属性即函数”的观点，在龙书中表现为“带注释的语法树”这一逻辑概念。在工程上，它支撑了多遍编译、不可变语法树、多工具共享和增量编译。

从 ANTLR 的 `ParseTreeProperty`，到 Go 的 `types.Info`、TypeScript 的 `NodeLinks`、rustc 的 `TypeckResults`，再到 Salsa 和 rustc 的查询系统，可以看到一条清晰的演进路线：属性先从节点中被分离出来，再变成按需计算的缓存，最后变成带依赖追踪的查询结果。

理解了侧表，也就理解了现代编译器前端的一个基本组织原则：**树描述程序的结构，侧表记录对结构的分析结果。**