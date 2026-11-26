# Operator Transformation（算子级变换）

> **定位**：图级优化中对**单个算子进行等价变换**的一类，目的是为后续的融合/替换/硬件适配"铺路"。与结构化简不同，这里的变换往往并不直接减少计算量，而是**重构算子形态**以打开新的优化空间。

## 一、算子分解（Operator Decomposition）

把**复杂算子拆解**为一组基础算子，便于后续融合与优化。

```
LayerNorm → (mean, sub, var, div, scale, shift) 一组基础算子
Softmax   → (max, sub, exp, sum, div)
GELU      → (x, x³, tanh, add, mul) 展开近似式
```

**收益**：

- 拆解后可与相邻算子重新融合（`LayerNorm + Linear` 融合为 pre/post LN 融合内核）
- 暴露标量操作，方便向量化 / Tensor Core 映射
- 便于精度分析（哪一步敏感、哪一步可以低精度）

**风险**：

- 拆得太碎，反而增加 kernel launch 数（若后续没做好融合）
- 数值稳定性可能变差（如 exp 溢出、方差计算的数值稳定形式）

## 二、算子合并（Operator Merging）

与分解相反，把多个小算子**合并成一个等价的复合算子**（如已有高效实现的 `FusedLayerNorm` / `FusedGELU`）。

```
matched pattern: mean → sub → var → div → scale → shift
                         ↓
              rewrite as: FusedLayerNorm

好处：
  · 直接调用手工优化的库实现（cuDNN / oneDNN / Triton）
  · 一次性完成，避免中间张量往返 HBM
  · 便于替换为 tensor core 优化实现
```

## 三、算子替换（Operator Substitution）

将某算子替换为**等价但更高效**的实现，可分为三类：

### 3.1 硬件特化替换

用硬件有**专用指令**的算子实现：

```
GEMM         → cuBLAS / CUTLASS
Conv         → cuDNN / oneDNN Winograd
Attention    → FlashAttention / cuDNN Attention
LayerNorm    → cuDNN / Apex FusedLayerNorm
```

### 3.2 库调用替换

替换为库中已高度优化的算子（`aten::conv2d` → `mkldnn::conv2d`）。

### 3.3 数值稳定性替换

替换为**数值更稳定的等价算子**：

```
Softmax naive:      exp(x) / sum(exp(x))         → 大 x 易溢出
Softmax stable:     exp(x - max(x)) / sum(...)   → 保持数值稳定

LogSumExp naive:    log(sum(exp(x)))
LogSumExp stable:   max(x) + log(sum(exp(x - max(x))))
```

## 四、分解-融合的组合拳

在实际编译流水线中，**分解和融合往往组合使用**：

```
1. 分解阶段（Decompose）
     LayerNorm → (mean, sub, var, div, scale, shift)
     Softmax → (max, sub, exp, sum, div)
     → 得到"基础算子图"

2. 融合阶段（Fuse）
     基础算子图 + 相邻算子 → 重新融合为大 kernel
     例如: LayerNorm 的 mean/var 与前一个 GEMM 的输出融合
     例如: Attention 的 Softmax 与 QK/V 融合（FlashAttention）

3. 替换阶段（Substitute）
     若识别出经典模式，替换为库中高效实现
```

这就是 **XLA、MLIR、TVM Relax** 等编译器背后的通用套路。

## 五、与结构化简的区别

| 维度 | [结构化简](docs/AI-compiler/pipeline/graph-optimizer/Computational-graph-simplification/index.md) | 算子级变换（本节） |
| --- | --- | --- |
| 目标 | 减少计算量 / 中间张量 | 重构算子形态，为后续优化铺路 |
| 是否等价 | 严格数学等价 | 严格数学等价 |
| 典型操作 | 融合、代数化简、CSE、DCE | 分解、合并、替换 |
| 收益 | 直接可见 | 常常需与其它优化组合才可见 |

## 六、面试高频

| 问题 | 要点 |
| --- | --- |
| 为什么先分解再融合？ | 分解暴露基础算子，让重新融合能跨越原算子边界 |
| Softmax 为何要做"减 max"？ | 数值稳定性（防 exp 溢出），是"数值稳定替换" |
| 如何决定何时替换成库调用？ | 输入形状 / 硬件特性 / 是否有更优融合方案的综合决策 |
