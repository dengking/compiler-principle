# Computational Graph Simplification（计算图化简）

> **定位**：图级优化中的**传统核心**方向，围绕"结构化简"这一主题，通过一系列**语义等价的重写规则**让计算图更小、更快、更省内存。它是 AI 编译器岗位面试与工程实战中出现频率最高的一组技术。

## 一、五大方向

```
┌────────────────────────────────────────────┐
│ 1. 算子融合 (Operator Fusion)     ★最重要   │
│    · 垂直融合、水平融合                     │
├────────────────────────────────────────────┤
│ 2. 代数化简 (Algebraic Simplification)      │
│    · 常量折叠、代数恒等式、强度削减         │
├────────────────────────────────────────────┤
│ 3. 冗余消除 (Redundancy Elimination)        │
│    · CSE、死代码消除、恒等算子消除          │
├────────────────────────────────────────────┤
│ 4. 布局优化 (Layout Optimization)           │
│    · NCHW↔NHWC、消除冗余 transpose/reshape  │
├────────────────────────────────────────────┤
│ 5. 算子替换/规范化 (Canonicalization)       │
│    · 用高效算子替换、算子分解与合并         │
└────────────────────────────────────────────┘
```

| 方向 | 详见 |
| --- | --- |
| **算子融合** | [Operator-fusion](Operator-fusion.md) |
| **代数化简 / 常量折叠 / 强度削减** | [Algebraic-simplification & Constant-folding & Strength-reduction](Algebraic-simplification&Constant-folding&Strength-reduction.md) |
| **冗余消除（CSE / DCE / Identity）** | [elimination](elimination.md) |
| **布局优化** | 见本页第五节 |
| **算子替换 / 规范化** | 详见 [../Operator-Transformation](docs/AI-compiler/pipeline/graph-optimizer/Operator-Transformation/index.md) |

## 二、化简的共同性质

- **语义等价**：所有重写必须严格保留数学含义
- **收敛性**：反复应用直到不动点（fixed-point）
- **组合触发**：常量折叠可能产生新常量 → 又触发新的化简

## 三、布局与数据流优化

### 3.1 布局转换与传播（Layout Transformation）

不同硬件偏好不同数据布局：

```
CPU 常偏好 NCHW，GPU/TensorCore 常偏好 NHWC
    → 编译器插入 transpose 适配
    → 但要通过"布局传播"消除连续冗余的 transpose
```

### 3.2 冗余 Transpose / Reshape 消除

```
优化前：                              优化后：
    x → transpose → transpose → y  →   x → y
    （两次转置互相抵消）
```

这是深度学习图化简中**极其常见**的优化——框架导出的模型往往含大量冗余的 reshape/transpose。

**常见规则**：

```
transpose(transpose(x, p1), p2) → transpose(x, p1∘p2)
    若 p1∘p2 = identity → 直接删除
reshape(reshape(x, s1), s2)     → reshape(x, s2)
reshape(x, x.shape)             → x  (恒等 reshape)
```

## 四、实现机制：Pattern Rewrite

现代 AI 编译器（尤其是 MLIR）用**模式重写（Pattern Rewrite）**统一实现这些化简。

```
定义一系列 "匹配模式 → 替换模式" 的规则：

    match:    A → B → C  (某个子图模式)
    rewrite:  fused_ABC   (替换为化简后的形式)

编译器反复扫描图，匹配到就替换，直到无法再化简（收敛）
```

### MLIR 中的实现

```
- Canonicalization Pass：规范化 + 基础代数化简
- DRR (Declarative Rewrite Rules)：声明式重写规则
- PDL (Pattern Descriptor Language)：模式描述语言
- 各 Dialect 自带 canonicalize / fold 方法
```

**示例（概念性）**：

```cpp
// 匹配 add(x, 0) 并化简为 x
struct SimplifyAddZero : public OpRewritePattern<AddOp> {
  LogicalResult matchAndRewrite(AddOp op, PatternRewriter &rewriter) const {
    if (isZero(op.getRhs())) {
      rewriter.replaceOp(op, op.getLhs());  // add(x,0) → x
      return success();
    }
    return failure();
  }
};
```

### 关键：迭代直到不动点

```
化简规则之间会互相触发：
  常量折叠 → 产生新常量 → 又触发新的代数化简 → …

因此需要迭代应用，直到图不再变化（Fixed-Point）
```

## 五、各 AI 编译器中的对应实现

| 编译器 | 图化简实现 |
| --- | --- |
| **TVM** | Relay/Relax 的 Pass（FuseOps、FoldConstant、EliminateCommonSubexpr…） |
| **MLIR** | Canonicalization、CSE Pass、各 Dialect 的 fold |
| **XLA** | HLO 层的 Algebraic Simplifier、Fusion |
| **TensorRT** | Layer Fusion（垂直/水平融合，闭源但文档丰富） |
| **PyTorch** | torch.fx 图变换、Inductor 的融合 |

## 六、面试高频问题

| 问题 | 要点 |
| --- | --- |
| **算子融合为什么能提速？** | 减少中间结果的内存往返（访存瓶颈）+ 减少 kernel 启动开销 |
| **垂直融合 vs 水平融合？** | 垂直=生产者消费者链；水平=共享输入的并行算子 |
| **Conv+BN 折叠原理？** | BN 推理时参数为常量，可数学合并进 Conv 权重/偏置 |
| **什么算子难融合？** | reduce 类、改变数据依赖的算子、资源超限时 |
| **图化简如何保证正确性？** | 每条重写规则必须是"语义等价"变换 |
| **为什么要迭代到不动点？** | 化简规则互相触发，需反复应用直到收敛 |
| **在 MLIR 里怎么实现？** | Pattern Rewrite（DRR/PDL）、Canonicalization、CSE Pass |

## 七、总结

```
计算图化简 = 在 DAG 层面做"语义等价"的结构精简

五大武器：
  ① 算子融合    ── 减少访存与启动开销（最重要）
  ② 代数化简    ── 常量折叠、恒等式、强度削减
  ③ 冗余消除    ── CSE、DCE、恒等算子消除
  ④ 布局优化    ── 消除冗余 transpose/reshape
  ⑤ 规范化      ── 算子替换与合并

实现机制：Pattern Rewrite，迭代至不动点

核心价值：深度学习瓶颈在访存，图化简（尤其融合）
         通过减少内存往返，直接命中性能要害
```

> 📌 **一句话总结**：计算图化简是 AI 编译器高层优化的**主战场**，其中**算子融合**是皇冠上的明珠——它抓住了"深度学习是访存密集型"这个本质，通过减少中间结果的内存读写来大幅提速。理解它，是理解 AI 编译器"为什么快"的关键。
