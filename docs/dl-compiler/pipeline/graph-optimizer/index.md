# Graph Optimizer

`Graph Optimizer` 在计算图级别对 Graph IR 进行优化，也叫**前端优化**。

## 特点

- 针对计算图整体拓扑结构优化，不关心算子的具体实现。
- 具有局部或全局的视野。
- 主要流程为对算子节点进行融合、消除、化简，使得计算图的计算和存储开销最小。
- 这些优化是硬件无关的通用优化。

![前端优化](https://developer.qcloudimg.com/http-save/11307734/552d408df1920329ca0999de15538264.png)

## 主要优化

- 图算融合
- 数据排布转换
- 内存优化
- 死代码消除

## 后续阶段

得到优化后的计算图后，将其转换为 [Tensor IR](docs/AI-compiler/pipeline/tensor-IR/index.md)，送入 [Operator Optimizer](docs/AI-compiler/pipeline/operator-optimizer/index.md) 进行算子级优化（后端优化）。


# Graph-Level Optimization（图级优化）

> **定位**：图级优化是 AI 编译器**高层优化**的主战场，在与硬件无关的**计算图（Computational Graph）**层面对模型做全局的等价变换。本文构建一张完整的知识地图，让读者具备系统性视野；每一大类的详细内容详见对应子目录。

## 一、什么是计算图

深度学习模型在编译器中被表示为**有向无环图（DAG）**：

```
- 节点（Node）  = 算子/操作（Conv、MatMul、Add、ReLU…）
- 边（Edge）    = 张量（Tensor），表示数据流动
```

**示例**：一个简单的 `y = ReLU(Conv(x, w) + b)`

```
    x ──┐
        ├──▶ [Conv] ──▶ [Add] ──▶ [ReLU] ──▶ y
    w ──┘            ▲
                 b ──┘
```

图级优化就是对这个 DAG 做**语义等价的变换**，使其"更小、更快、更省内存"。

## 二、为什么需要图级优化

### 深度学习的性能瓶颈：访存 > 计算

```
关键事实：
  现代硬件的算力增长 >> 内存带宽增长
  → 很多算子是"访存密集型（Memory-Bound）"
  → 瓶颈在于反复读写中间结果，而非计算本身
```

### 图级优化带来的核心收益

| 收益 | 说明 |
| --- | --- |
| **减少内存访问** | 融合算子避免中间结果写回内存（最大收益）⭐ |
| **减少 [kernel 启动](tag-kernel-launch.txt) 开销** | 每个算子=一次 kernel launch，融合后减少启动次数 |
| **减少计算量** | 常量折叠、冗余消除直接砍掉计算 |
| **降低峰值内存** | 内存复用、重计算让更大模型能跑起来 |
| **为后续优化铺路** | 简化的图更利于 tiling、[向量化](docs/AI-compiler/pipeline/graph-optimizer/tag-vectorization=向量化.txt) 等中低层优化 |

> **核心动机**：一次算子 = 一次"读输入→计算→写输出"。如果把 5 个算子融合成 1 个，就省下了 4 次中间结果的内存往返——这在访存密集场景收益巨大。

## 三、图级优化全景分类

图级优化本质是一个**多目标优化系统**，可按"优化目标"划分为九大方向：

| 分类 | 关键技术 | 详见 |
| --- | --- | --- |
| **① 结构化简（传统核心）** | 算子融合 · 代数化简 · 常量折叠 · CSE · DCE · 布局 | [Computational-graph-simplification](docs/AI-compiler/pipeline/graph-optimizer/Computational-graph-simplification/index.md) |
| **② 内存优化** | 内存复用/规划 · In-place · 内存池 · 重计算 | [../Memory-Optimization](../Memory-Optimization/index.md) |
| **③ 并行与设备** | 图切分 · 设备放置 · 并行调度 | [Parallel-and-Device-Placement](docs/AI-compiler/pipeline/graph-optimizer/Parallel-and-Device-Placement/index.md) |
| **④ 精度与量化** | 混合精度 · 量化(QDQ) · 算法替换(Winograd) | [Precision-and-Quantization](docs/AI-compiler/pipeline/graph-optimizer/Precision-and-Quantization/index.md) |
| **⑤ 调度与执行** | 算子重排 · 异步/流水线 · 预取 | [Scheduling-and-Execution](docs/AI-compiler/pipeline/graph-optimizer/Scheduling-and-Execution/index.md) |
| **⑥ 算子级变换** | 算子分解 · 合并 · 替换 | [Operator-Transformation](docs/AI-compiler/pipeline/graph-optimizer/Operator-Transformation/index.md) |
| **⑦ 大模型专用** | 重计算 · KV Cache · FlashAttention 融合 | [../LLM-Specific-Optimization](../LLM-Specific-Optimization/index.md) |
| **⑧ 分布式/通信** | 通信融合 · 计算通信重叠 · 并行策略变换 | [Distributed-and-Communication](docs/AI-compiler/pipeline/graph-optimizer/Distributed-and-Communication/index.md) |
| **⑨ 动态 Shape/控制流** | Shape 推断 · 控制流优化 · 动态特化 | [Dynamic-Shape-and-Control-Flow](docs/AI-compiler/pipeline/graph-optimizer/Dynamic-Shape-and-Control-Flow/index.md) |

> **重要认知**：很多人对图级优化的理解停留在"算子融合"这一个点。实际上它是在**时间（访存/延迟）、空间（内存）、并行度、精度**之间做全局权衡的完整体系。

## 四、实现机制：Pattern Rewrite

现代 AI 编译器（尤其是 MLIR）用**模式重写（Pattern Rewrite）**统一实现所有图优化。

```
定义一系列 "匹配模式 → 替换模式" 的规则：

    match:    A → B → C  (某个子图模式)
    rewrite:  fused_ABC   (替换为化简后的形式)

编译器反复扫描图，匹配到就替换，直到无法再化简（收敛 / Fixed-Point）
```

### 各 AI 编译器中的对应实现

| 编译器 | 图优化实现 |
| --- | --- |
| **TVM** | Relay/Relax 的 Pass（FuseOps、FoldConstant、EliminateCommonSubexpr…） |
| **MLIR** | Canonicalization、CSE Pass、各 Dialect 的 fold |
| **XLA** | HLO 层的 Algebraic Simplifier、Fusion |
| **TensorRT** | Layer Fusion（垂直/水平融合，闭源但文档丰富） |
| **PyTorch** | torch.fx 图变换、Inductor 的融合 |

## 五、面试高频问题

| 问题 | 要点 |
| --- | --- |
| 算子融合为什么能提速？ | 减少中间结果的内存往返（访存瓶颈）+ 减少 kernel 启动开销 |
| 垂直融合 vs 水平融合？ | 垂直=生产者消费者链；水平=共享输入的并行算子 |
| Conv+BN 折叠原理？ | BN 推理时参数为常量，可数学合并进 Conv 权重/偏置 |
| 什么算子难融合？ | reduce 类、改变数据依赖的算子、资源超限时 |
| 内存复用怎么做？ | 张量生命周期分析 + 图着色/区间调度 |
| 重计算的 trade-off？ | 用计算换内存，大模型训练必备 |
| FlashAttention 属于什么优化？ | 图级+kernel 级融合，核心是避免 N×N 矩阵写回 HBM |
| 混合精度谁决定精度？ | 编译器按算子敏感度分配，自动插入/消除 cast |
| 分布式通信如何优化？ | 通信融合 + 计算通信重叠 |
| 图优化如何保证正确性？ | 每条重写规则必须是"语义等价"变换 |
| 为什么要迭代到不动点？ | 优化规则互相触发，需反复应用直到收敛 |

## 六、与整体优化流程的关系

```
图级优化（高层，硬件无关）                                ← 本层
      ↓ Lowering
算子/循环优化（中层：tiling、向量化）  ← 图优化后的图更利于此层优化
      ↓ Lowering
后端代码生成（低层：寄存器分配、指令调度）
```

> **重要认知**：图优化是**"打地基"**的优化。图优化得越干净，后续中低层优化的效果越好——一个含大量冗余 transpose 的脏图，会严重拖累后续所有优化。

## 七、核心要义

```
图级优化 = 在 DAG 层面做"语义等价"的多目标全局优化

本质权衡：时间（访存/延迟） ⇄ 空间（内存）
          ⇄ 并行度 ⇄ 精度

三条主线：
  · 传统核心 —— 结构化简（算子融合是明珠）
  · 大模型新增 —— 内存优化（重计算/KV Cache）、FlashAttention 融合
  · 分布式新增 —— 通信融合、计算通信重叠

统一实现机制：Pattern Rewrite，迭代至不动点
```

> 📌 图级优化远不止"融合和化简"这一个点。它是 AI 编译器高层优化的**主战场**，是一个在**时间、空间、并行度、精度**之间做全局权衡的**多目标优化系统**。
