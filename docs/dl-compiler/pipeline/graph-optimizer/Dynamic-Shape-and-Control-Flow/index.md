# Dynamic Shape and Control Flow（动态 Shape 与控制流优化）

> **定位**：图级优化在**非静态图**场景下的扩展。传统图优化假设 shape 已知、无控制流，但真实模型（Batch 变化、序列变长、条件分支、循环）远比这复杂。这一方向是编译器"能不能落地生产环境"的关键。

## 一、Shape 推断与传播（Shape Inference）

编译期尽可能推断每个张量的 shape：

```
静态 shape：所有维度都是常量
    → 可做最激进的优化（tiling 尺寸、内存规划、Tensor Core 匹配）

动态 shape：部分维度未知（如 batch、seq_len）
    → 需要额外机制：shape 特化、分桶、符号推理
```

### 1.1 符号 Shape（Symbolic Shape）

用**符号变量**表示未知维度，在图上做代数推理：

```
输入：  x: [N, C, H, W]     ← N, H, W 是符号
Conv → [N, C', H', W']    ← 编译器推出 H' = (H + 2p - k) / s + 1
Pool → [N, C', H'', W'']
...
    → 后续 pass 可基于 H'/W' 的代数表达式做变换
```

### 1.2 约束求解

某些优化需要判断 `dim1 == dim2` 或 `dim > 0`。图优化器往往内置一个轻量约束求解器（如 XLA 的 `IsKnownEq` / MLIR 的 `presburger`）。

## 二、动态 Shape 特化（Shape Specialization）

**为常见 shape 生成专用高效 kernel**，其余 shape 走通用路径。这是"性能与灵活性"的经典折衷。

### 2.1 分桶（Bucketing）

```
观察：推理请求的 batch_size 集中在 [1, 4, 8, 16, 32]
策略：为每个桶预编译一个 kernel，运行时选桶
```

**代价**：编译时间与二进制大小随桶数量线性增长。

### 2.2 Padding to Bucket

将实际 shape padding 到最近的桶尺寸：

```
实际 seq_len = 137 → padding 到 seq_len = 256 的 kernel
    · 优点：只需一个 kernel
    · 缺点：算了很多无效计算，需要 attention mask 屏蔽
```

### 2.3 Ragged / Nested Tensor

对不等长序列不做 padding，直接用**变长张量**表示，配合 `flash_attn_varlen` 等专用 kernel。vLLM/SGLang 的核心技巧之一。

## 三、控制流优化（Control Flow Optimization）

针对图中的**分支/循环**（`if / while / for`）：

### 3.1 循环不变量外提（LICM，Loop-Invariant Code Motion）

```
for i in range(N):
    a = f(x)          ← 与 i 无关，可提到循环外
    y[i] = a + i

→
a = f(x)
for i in range(N):
    y[i] = a + i
```

### 3.2 分支化简与死分支消除

```
if constant_true:      →   直接保留 then 分支
    do_A()                 do_A()
else:
    do_B()

if x > 0 and x < 0:    →   死分支，整体删除
    do_C()
```

### 3.3 循环展开（Loop Unrolling）

```
for i in range(4):     →    y[0] = f(x[0])
    y[i] = f(x[i])          y[1] = f(x[1])
                            y[2] = f(x[2])
                            y[3] = f(x[3])
```

**收益**：暴露更多并行、便于向量化；**代价**：代码膨胀、指令缓存压力。

### 3.4 循环融合（Loop Fusion）

```
for i in range(N):
    y[i] = f(x[i])
for i in range(N):        →    for i in range(N):
    z[i] = g(y[i])                y[i] = f(x[i])
                                  z[i] = g(y[i])
```

这与算子融合本质相同，只是发生在控制流层面。

### 3.5 尾递归转循环 / 循环转向量化

编译器高层的经典变换，同样适用于计算图中的循环控制。

## 四、Trace vs Symbolic vs Guarded

现代深度学习编译器（`torch.compile`、`JAX`、`XLA`）处理动态图有三种主流模式：

| 模式 | 代表 | 特点 |
| --- | --- | --- |
| **Trace-based** | `torch.jit.trace`、`jax.jit` | 一次执行捕获图，shape 固定 → 换 shape 需重编译 |
| **Symbolic** | Torch Dynamo + Symbolic Shapes | shape 用符号变量，一次编译支持多 shape |
| **Guarded** | Dynamo Guards | 编译时插入 guard（如 `assert N==8`），失败则重编译 |

## 五、与其他优化的关系

- Shape 推断是**几乎所有下游优化的基础** —— tiling、内存规划、算法替换都依赖 shape
- 动态 shape 通常削弱 [结构化简](docs/AI-compiler/pipeline/graph-optimizer/Computational-graph-simplification/index.md) 的效果（无法折叠 shape 计算）
- 与 [调度与执行](docs/AI-compiler/pipeline/graph-optimizer/Scheduling-and-Execution/index.md) 结合：变长 batch 的动态调度是 vLLM/SGLang 的关键

## 六、面试高频

| 问题 | 要点 |
| --- | --- |
| 动态 shape 为什么难优化？ | 阻碍 tile 尺寸决策、静态内存规划、算法替换 |
| torch.compile 怎么处理动态 shape？ | Dynamo + Symbolic Shape + Guard，失败则 recompile |
| Padding 与 Ragged 各自的取舍？ | Padding 通用但浪费；Ragged 高效但需专用 kernel |
| LICM 为什么重要？ | 把常量子图/不变计算移出循环，直接减少运行时开销 |
