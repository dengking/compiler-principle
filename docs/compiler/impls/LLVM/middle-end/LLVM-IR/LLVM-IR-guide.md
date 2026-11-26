
# LLVM IR guide


LangRef:LLVM IR 的"宪法"
**LangRef** = [LLVM Language Reference Manual](https://llvm.org/docs/LangRef.html),LLVM IR 的规范文档。它在 LLVM 生态里的地位,相当于 ISO C 标准之于 C。**LangRef 是 LLVM IR 那一层的动态语义规范**——只不过它是用散文写的,而不是形式化的推导规则。

---

## 一、它在三层框架里的位置

前面讲过,每一级 IR 都有自己的一份动态语义。LangRef 定义的正是中间那一层:

```
C/C++ 源码      ← ISO 标准(散文)
   │
LLVM IR         ← LangRef(散文)          ← 本文主角
   │
MIR             ← 几乎没有正式规范
   │
机器码           ← ISA 手册(RISC-V 有 Sail 形式语义)
```

而 LangRef 自己也覆盖三层:

| 层                     | LangRef 里对应的内容                     | 谁来检查                     |
| --------------------- | ---------------------------------- | ------------------------ |
| **Syntax**            | 文本 IR 的具体写法(`%x = add i32 %a, %b`) | parser(`.ll` 读取器)        |
| **Static Semantics**  | 类型规则、SSA 支配关系、φ 的位置约束              | **Verifier**             |
| **Dynamic Semantics** | poison/undef、UB 列表、内存模型、各指令的行为     | **没人检查**——只能靠人读 + Alive2 |

**第三列是重点**:前两层有机器把关,第三层没有。这是 LLVM 里 miscompilation 的主要来源。

---

## 二、文档结构

LangRef 很长(单页几万行),但骨架清晰:

| 部分 | 内容 | 重要性 |
|---|---|---|
| **Identifiers** | `%local` / `@global`,命名 vs 编号 | 基础 |
| **High Level Structure** | Module、Function、BasicBlock、linkage、visibility、COMDAT、section | 基础 |
| **Parameter / Function Attributes** | `noalias`、`nonnull`、`readonly`、`nounwind`、`willreturn`… | **极重要**,优化全靠它 |
| **Type System** | `iN`、`float`、`ptr`、`[N x T]`、`{T,...}`、`<N x T>` | 基础 |
| **Constants** | 常量表达式、`zeroinitializer`、`poison`、`undef` | **语义核心** |
| **Metadata** | `!dbg`、`!tbaa`、`!range`、`!llvm.loop`… | 优化与调试的旁路通道 |
| **Instruction Reference** | 每条指令的语法 + 语义 | **主体** |
| **Intrinsic Functions** | `llvm.memcpy`、`llvm.assume`、`llvm.lifetime.*` 等数百个 | 扩展点 |
| **Undefined / Poison Values** | 两者的区别与传播规则 | **全文最难的一节** |
| **Memory Model for Concurrent Operations** | happens-before、原子序、数据竞争 | 与 C++11 对齐 |

实用建议:**LangRef 不是用来通读的,是用来查的**。日常工作中反复回去看的通常只有三处——属性列表、poison/undef 那节、以及手上正在用的那几条指令。

---

## 三、最关键的一节:undef 与 poison

这是 LangRef 里最反直觉、也最容易出错的部分。

### 两者的定义

| | `undef` | `poison` |
|---|---|---|
| 含义 | "**任意一个**该类型的值" | "**非法值**,比 undef 更毒" |
| 每次读 | **可以不同**(非确定性) | — |
| 传播 | 大多数指令传播 undef | **传播 poison,且更激进** |
| 被使用时 | 一般仍是良定义的 | 若被"有副作用的指令"使用 → **立即 UB** |
| 精化序 | $\texttt{poison} \sqsubseteq \texttt{undef} \sqsubseteq \text{具体值}$ | |

### undef 的致命陷阱

```llvm
%x = ... undef ...
%a = add i32 %x, %x        ; 这不等于 2*%x !
```

因为 `undef` 的两次读取可以给出**不同的值**,所以 `undef + undef` 不是偶数。这条让下面这个"显然正确"的优化变成错误:

```llvm
; 错误!
%a = add i32 %x, %x   →   %a = shl i32 %x, 1
```

当 `%x` 是 `undef` 时,左边可以是任意值(含奇数),右边只能是偶数。**右边的行为集合不是左边的子集**,违反了精化条件 $⟦\text{after}⟧ \subseteq ⟦\text{before}⟧$。

这正是引入 `poison` 的动机之一:`poison` 是单一的"坏值",不会每次读出不同结果,推理起来干净得多。

### poison 从哪来

| 来源 | 条件 |
|---|---|
| `add nsw` / `nuw` | 发生有符号/无符号溢出 |
| `mul nsw` / `shl nsw` | 同上 |
| `getelementptr inbounds` | 结果越出分配对象 |
| `udiv exact` / `sdiv exact` | 除不尽 |
| `lshr exact` / `ashr exact` | 移出了非零位 |
| 带 `!range` 的 `load` | 读到范围外的值 |
| 带 `nonnull`/`align` 的指针 | 违反承诺 |

注意这些 flag 的本质:**它们不是"告诉编译器去优化",而是"程序员/前端承诺某事不会发生,若发生则结果是 poison"**。前端加 `nsw` 是因为 C 的有符号溢出本就是 UB,所以把这个承诺传递给 IR 层。

### freeze:把毒性截断

```llvm
%y = freeze i32 %x
```

`freeze` 把 poison/undef **固定成某个任意但确定的具体值**。它正好把精化偏序往下压一级:

$$\texttt{poison}/\texttt{undef} \;\xrightarrow{\ \texttt{freeze}\ }\; \text{某个具体值(不确定是哪个,但固定)}$$

于是前面那个优化可以安全地做:

```llvm
%y = freeze i32 %x
%a = add i32 %y, %y    →    %a = shl i32 %y, 1     ; 现在合法
```

`freeze` 是 2020 年左右才加进 LLVM 的,正是为了解决 undef 语义导致的一系列真实 miscompilation(特别是 select / phi 的优化)。

---

## 四、属性:LangRef 里最"有钱"的部分

优化器的绝大部分威力来自函数和参数属性。这些属性本质上是**对动态语义的额外承诺**。

### 参数属性

| 属性 | 承诺 | 违反的后果 |
|---|---|---|
| `noalias` | 该指针的 provenance 与其他参数不交(≈ `restrict`) | **UB** |
| `nonnull` | 非空 | poison 或 UB |
| `dereferenceable(N)` | 至少 N 字节可读 | UB |
| `align N` | 对齐 | UB |
| `nocapture` | 函数不会保存该指针 | UB |
| `readonly` / `writeonly` | 只读 / 只写 | UB |
| `byval` / `sret` | ABI 相关的传递方式 | 调用约定错 |

### 函数属性

| 属性 | 含义 | 启用什么优化 |
|---|---|---|
| `memory(none)`(旧名 `readnone`) | 不读写任何内存 | CSE、提升、删除 |
| `memory(read)` | 只读内存 | 可跨写操作重排 |
| `nounwind` | 不抛异常 | 不需 landing pad,简化 CFG |
| `willreturn` | 必然返回(不死循环、不 `exit`) | **允许删除无用调用** |
| `norecurse` | 不递归 | 栈分析 |
| `speculatable` | 可被投机执行(无副作用、不陷入) | 提到分支外 |
| `nofree` | 不释放内存 | 指针仍有效 |
| `alwaysinline` / `noinline` | 内联决策 | — |

**`willreturn` 值得单独说**:前面提过 C++ 允许假定无副作用的循环终止、C 不允许。这个语言级差异在 IR 层就体现为 Clang 是否给函数加 `willreturn` / 给循环加 `llvm.loop.mustprogress`。**同一个后端,靠属性区分两种语言的动态语义。**

---

## 五、LangRef 的内存模型

LangRef 的并发语义**刻意与 C++11 对齐**,但措辞更底层:

| LLVM | 对应 C++ |
|---|---|
| `unordered` | (无直接对应,给 Java 的非 volatile 字段用) |
| `monotonic` | `relaxed` |
| `acquire` / `release` / `acq_rel` | 同名 |
| `seq_cst` | 同名 |
| 非原子访问 + 竞争 | 数据竞争 → **返回 `undef`** |

注意最后一行的差异:**C++ 说数据竞争是 UB,LangRef 说竞争的读返回 `undef`**。这是故意的——LLVM 要同时服务 C++(竞争=UB)和 Java(竞争有界、不破坏内存安全),所以选了一个较弱的模型,让 Java 前端也能用。

`unordered` 这一级就是专门为 Java 的非 volatile 字段设计的:保证不撕裂、不凭空出现,但不提供任何顺序保证。

---

## 六、LangRef 的根本问题:它是散文

这是整个 LLVM 生态公认的痛点。

### 问题表现

| 问题 | 具体例子 |
|---|---|
| **歧义** | `ptrtoint`/`inttoptr` 往返是否保留 provenance?LangRef 没说清 |
| **条款间不一致** | 某些 pass 的实际行为与 LangRef 字面意思冲突 |
| **缺失** | `undef` 与 `select`/`phi` 交互的精确规则长期靠口头传统 |
| **不可机器检查** | 无法自动验证一个 pass 是否符合规范 |

最著名的研究是 Lee 等人的论文 *"Taming Undefined Behavior in LLVM"*(PLDI 2017),它指出 LLVM 当时的 `undef` 语义**自相矛盾**:存在两个各自看起来正确的优化,组合起来会产生 miscompilation。`freeze` 指令就是这篇论文提出的解决方案之一,后来被真正合入。

### 实际后果

```
LangRef 是散文
    ↓
优化器作者各自理解
    ↓
pass A 假定继承 provenance,pass B 假定不继承
    ↓
A 和 B 单独都"对",组合后 miscompile
    ↓
bug 报告 → 吵架 → 修改 LangRef 措辞 → 循环
```

LLVM 的 issue tracker 里有一批长期挂着的 "IR semantics" 标签 bug,很多都属于这一类。

### 对比:WebAssembly 怎么做的

|        | LLVM IR          | WebAssembly                    |
| ------ | ---------------- | ------------------------------ |
| 规范形式   | 散文 LangRef       | **完整的小步操作语义**                  |
| UB     | 大量               | **零**                          |
| 类型安全   | Verifier 检查(无证明) | **机器检查的 soundness 证明**         |
| 多实现一致性 | 靠测试              | 靠规范 + 官方 reference interpreter |

Wasm 从第一天就带了形式语义和 Coq/Isabelle 证明,这是语言设计实践上的明显进步。代价是 Wasm 的抽象层次低得多——它不需要表达 `nsw`、provenance 这些东西。

---

## 七、围绕 LangRef 的工具生态

既然规范本身不可机器检查,就只能从外部补救:

| 工具 | 做什么 | 与 LangRef 的关系 |
|---|---|---|
| **Verifier** (`-verify`) | 检查结构性/类型性不变量 | 实现 LangRef 的**静态语义**部分 |
| **Alive2** | 用 SMT 证明一对 IR 的 refinement | 实现 LangRef 的**动态语义**(的一个形式化猜测) |
| **llvm-reduce / bugpoint** | 缩小触发 bug 的 IR | 辅助定位 |
| **csmith / yarpgen** | 随机生成 C 程序做差分测试 | 端到端找 miscompile |
| **AliveToolkit / souper** | 超优化器,自动发现优化机会 | 基于语义搜索 |

**Alive2 最值得了解**。它的工作方式是:

```
输入:两段 IR(优化前 / 优化后)
  ↓  把语义(含 poison/undef/UB/内存)编码成 SMT 公式
  ↓  求解 ∃ 输入, 使得 after ⊄ before
输出:要么"验证通过",要么给出反例
```

它的困难之处恰恰在于第一步:**把散文 LangRef 翻译成精确的 SMT 编码,本身就是在"猜 LangRef 想说什么"**。Alive2 的作者同时也是 LangRef 措辞的主要推动修订者之一——工具和规范在互相塑造。

Alive2 现在已经接进 LLVM 的 CI,对 `InstCombine` 等 pass 的测试用例做自动验证,实际抓出了不少 bug。

---

## 八、怎么读 LangRef(实操)

**查指令语义时的标准顺序**:

1. **Syntax** —— 文本形式
2. **Overview** —— 一句话干什么
3. **Arguments** —— 类型约束(这部分是静态语义,Verifier 会查)
4. **Semantics** —— **真正要细读的部分**,注意里面的 "poison"、"undefined behavior" 字样
5. **Example**

**读的时候重点盯这几个词**:

| 措辞                                 | 含义            |
| ---------------------------------- | ------------- |
| "the result is a **poison** value" | 产生 poison,可传播 |
| "the behavior is **undefined**"    | 立即 UB,全程序失效   |
| "the result is **undef**"          | 任意值,每次可不同     |
| "it is **unspecified**"            | 有限几种可能        |
| "the compiler **may assume**"      | 这是优化授权        |

**最常回查的几节**:

- `getelementptr` ——`inbounds` 的确切含义,以及地址计算的 provenance 规则
- `load` / `store` ——对齐、`volatile`、原子序、`!range` 等元数据
- `select` / `phi` ——与 poison 的交互(历史上出过最多 bug 的地方)
- Function Attributes ——写 pass 时必须知道能依赖什么
- Undefined/Poison Values ——所有疑难杂症的根源

---

## 九、总结

| | LangRef 是什么 |
|---|---|
| **定位** | LLVM IR 这一层的语言规范,覆盖 syntax / static / dynamic 三层 |
| **形式** | **散文**(这是它所有问题的根源) |
| **核心难点** | `undef` / `poison` 的精化偏序;provenance;并发模型 |
| **机器把关** | 只有静态语义有(Verifier);动态语义**无人检查** |
| **补救手段** | Alive2(SMT 验证)、csmith(差分测试)、人工 review |
| **对标** | ISO C 标准(同样散文,同样有 DR 修订流程) |
| **反面榜样** | WebAssembly(完整形式语义 + 机器检查证明) |

**一句话:LangRef 定义了"什么是合法 IR"和"合法 IR 意味着什么",前者有 Verifier 把关,后者只有人脑和 Alive2。** 前面讨论过的一切——精化关系 $\sqsubseteq$、UB 作为行为全集、provenance、SC-DRF、backend 的内存序降级——在 LLVM 的世界里,源头都是这一份文档里的某一句散文。