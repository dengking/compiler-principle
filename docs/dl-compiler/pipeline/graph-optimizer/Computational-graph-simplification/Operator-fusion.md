# Operator Fusion（算子融合）

> **定位**：计算图化简中**最重要**的技术，直接命中"访存瓶颈"这一深度学习性能要害。图级优化的皇冠上的明珠。

## 一、为什么算子融合能提速

一次算子的执行流程：

```
[读输入张量] → [计算] → [写输出张量]     ← 每次都要访问全局显存
```

如果两个算子是"生产者-消费者"关系，中间张量必然一读一写全局显存。融合后：

```
读输入 → 计算1 → 计算2 → ... → 写输出
         └────── 中间数据全程留在寄存器/共享内存 ──────┘
```

**收益**：

1. **减少 HBM 访存**（最大收益）——中间结果不再往返显存
2. **减少 kernel launch 次数** —— 每次 launch 都有几个 μs 的固定开销
3. **暴露更多并行**——大 kernel 可以更好地打满 SM

## 二、垂直融合（Vertical / Producer-Consumer Fusion）

沿**数据流方向**，把"生产者-消费者"链上的算子合并成一个 kernel。

```
融合前（3 个 kernel，2 次中间结果往返内存）：
    Conv ──▶ [写内存] ──▶ BatchNorm ──▶ [写内存] ──▶ ReLU

融合后（1 个 kernel，中间结果留在寄存器/片上）：
    ┌──────────────────────────┐
    │  Conv + BN + ReLU (fused) │
    └──────────────────────────┘
```

### 2.1 最经典的融合模式

```
Conv + BatchNorm + ReLU        → CBR 融合（CV 领域标配）
MatMul + BiasAdd + Activation  → 全连接层融合
Elementwise 链 (Add→Mul→ReLU)  → 逐元素算子链融合
LayerNorm + Linear             → Pre/Post-LN Transformer 融合
QKV projection + Reshape       → Attention 前奏融合
```

### 2.2 Conv + BN 折叠（BN Folding）

推理时 BN 的参数是常量，可直接**数学上合并进 Conv 的权重和偏置**，让 BN 彻底消失——这是常量折叠 + 融合的经典结合。

推理时 BN 的计算：

$$y = \gamma \cdot \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}} + \beta$$

设 $s = \frac{\gamma}{\sqrt{\sigma^2 + \epsilon}}$，则 $y = s \cdot x + (\beta - s \cdot \mu)$。

若 $x = W * z + b$（Conv 输出），代入：

$$y = s \cdot (W * z + b) + (\beta - s \cdot \mu) = (s \cdot W) * z + (s \cdot b + \beta - s \cdot \mu)$$

即：
- 新权重 $W' = s \cdot W$
- 新偏置 $b' = s \cdot b + \beta - s \cdot \mu$

**BN 彻底消失，一分钱运行时开销都没有。**

## 三、水平融合（Horizontal Fusion）

把**共享同一输入**、彼此无依赖的**并行算子**合并。

```
融合前：           融合后：
    ┌─▶ Conv1        ┌─▶ [Conv1|Conv2|Conv3
x ──┼─▶ Conv2   →  x ─┤   一次性并行计算]
    └─▶ Conv3        └─▶ 提高并行度、减少启动
```

**典型场景**：

- **Multi-Head Attention 的多个 Q/K/V 投影**：合并为一个大 GEMM，输出后再切分
- **Inception 模块的并行分支**：多个不同 kernel 大小的 Conv 合并
- **梯度计算中的多个 elementwise op**

## 四、深度融合案例：FlashAttention

FlashAttention 是**图级融合 + 算子级 tiling + 数值算法**的巅峰作品：

```
标准 Attention：
  Q,K,V → matmul → [N×N HBM] → softmax → [N×N HBM] → matmul → O

FlashAttention：
  一个 kernel 内完成：
    分块加载 Q/K/V 到 SRAM
    在 SRAM 内完成 QK^T
    online softmax（无需完整行的 max/sum，边算边更新）
    与 V 相乘累加到输出
    只写回最终 O

  → 中间 N×N 矩阵从未出现在 HBM 中
```

## 五、融合的约束条件

不是所有算子都能融合，需考虑：

```
✅ 数据依赖关系是否允许（无环、生产者-消费者顺序）
✅ 硬件资源（寄存器/共享内存）是否够用
✅ 融合后是否反而降低并行度（大 kernel 占用率下降）
✅ 算子类型是否兼容
    · elementwise ↔ elementwise：几乎总能融合
    · elementwise ↔ reduce：常可融合（下沉）
    · reduce ↔ reduce：常常不能（数据依赖复杂）
    · GEMM ↔ elementwise：epilogue 融合（CUTLASS 广泛支持）
    · GEMM ↔ GEMM：极少融合（除非做深度重构如 FlashAttention）
```

## 六、融合决策：编译器怎么选

主流策略：

### 6.1 规则式融合（Pattern-Based）

预定义融合模式（如 `Conv+BN+ReLU`），扫描图匹配后重写。TensorRT、cuDNN 走这条路。

### 6.2 分组式融合（Group-Based）

- **TVM Relay FuseOps**：基于算子类型标签（`kElemWise`、`kBroadcast`、`kInjective`、`kCommReduce`、`kOutEWiseFusable`、`kOpaque`）按可融合关系分组
- 一次遍历，将同一组内的算子融合成一个 fused function

### 6.3 代价模型驱动（Cost-Based）

XLA / Inductor 部分采用：枚举融合方案，用代价模型评估收益，选最优。

### 6.4 用户显式指定

Triton / CUTLASS：由开发者手工写融合内核，编译器只做代码生成。

## 七、面试高频

| 问题 | 要点 |
| --- | --- |
| **算子融合为什么能提速？** | 减少中间结果 HBM 往返（最大收益）+ 减少 kernel launch 开销 |
| **垂直融合 vs 水平融合？** | 垂直=生产者消费者链上下融合；水平=共享输入的多个算子并列融合 |
| **Conv+BN 折叠原理？** | BN 推理时参数为常量，可数学合并进 Conv 权重与偏置，BN 完全消失 |
| **什么算子难融合？** | reduce ↔ reduce、依赖复杂、资源超限、GEMM ↔ GEMM（除非深度重构） |
| **FlashAttention 属于什么融合？** | 图级+算子级+数值算法的深度融合，核心是不写回 N×N 矩阵 |
| **TVM 怎么做融合？** | Relay FuseOps，按算子标签分组一次遍历 |
| **MLIR 怎么做融合？** | Linalg fusion / structured ops fusion，基于 loop nest 分析 |
| **融合的正确性保证？** | 每步重写必须语义等价，通常靠形式化的 pattern 规则保证 |

---

> 📌 **一句话总结**：算子融合是深度学习性能优化的**第一性原理**——只要访存是瓶颈，就总能通过融合再挤出性能。
