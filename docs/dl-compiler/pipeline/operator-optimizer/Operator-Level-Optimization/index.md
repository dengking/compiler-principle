# Operator-Level Optimization（算子级优化）

> **定位**：AI 编译器**中端底层**的优化，针对**单个算子内核**做细粒度调度优化，最大化单 SM（Streaming Multiprocessor）硬件利用率。图级优化把图"化简干净"后，就轮到这一层把每个算子的实现"压榨到极限"。

## 一、为什么需要算子级优化

图级优化关心的是**"要算什么"**（计算图结构），算子级优化关心的是**"怎么算得快"**（单算子实现）。同一个 MatMul 算子，在不同的分块策略、向量化方式下，性能可能相差**十倍以上**。

```
关键事实：
  · 现代 GPU 有几千个 CUDA Core / 上百个 Tensor Core
  · 一个"朴素"算子内核往往只能用到 <10% 的算力
  · 通过 tiling / 向量化 / Tensor Core 映射，可提升 5~10x
```

## 二、核心技术

### 2.1 循环分块（Tiling / Loop Blocking，[循环分块](docs/AI-compiler/pipeline/operator-optimizer/tag-loop-tiling=循环分块.txt)）

将大张量切分为**适配共享内存/寄存器容量**的小块，最大化数据复用，减少全局访存。

```
朴素矩阵乘（每次读整行整列）：
  for i, j, k:  C[i,j] += A[i,k] * B[k,j]
      → A、B 反复被读入 → 严重访存瓶颈

Tiling 后（把 A、B 的一个 tile 载入共享内存）：
  for i0, j0, k0:                       ← 外层遍历 tile
    load A_tile, B_tile 到共享内存
    for i1, j1, k1:                     ← 内层复用 tile 中的数据
      C[..] += A_tile[..] * B_tile[..]
      → 每个数据元素被读 O(tile_size) 次全部命中共享内存
```

**多级 tiling**：Block Tile（共享内存） → Warp Tile（寄存器分片） → Thread Tile（单线程寄存器），层层适配 GPU 的存储金字塔。

### 2.2 循环重排（Loop Reordering / Loop Permutation）

调整循环嵌套顺序，改善**空间局部性**与**并行度**。

```
访问 A[i][j]（行主序）：
  外层 i，内层 j → 顺序访问 → 缓存友好 ✅
  外层 j，内层 i → 跨行跳跃 → 频繁 cache miss ❌
```

### 2.3 向量化（Vectorization）

将标量操作合并为 SIMD/SIMT 向量指令，一次完成多元素运算。

```
标量：   for i: y[i] = a*x[i] + b        (1 element / cycle)
向量化： for i step 4:                    (4 elements / cycle)
           y[i:i+4] = a*x[i:i+4] + b     ← 用 vec4/float4 加载
```

在 GPU 上通常表现为使用 `float4`、`half2`、`ldmatrix.sync` 等向量化访存指令。

### 2.4 并行化（Parallelization）

将循环维度映射到 GPU 的**线程层级**：Grid（多 SM） / Block（单 SM 内多 warp） / Warp（32 线程 SIMT） / Thread。

```
for i in range(N):
    y[i] = f(x[i])

→ 映射为：
    Block idx.x  = i / block_size
    Thread idx.x = i % block_size
    每个线程处理 y[i]
```

关键权衡：**并行度 vs 单线程负载**。线程太少 → 占用率低；线程太多 → 寄存器溢出、共享内存不够。

### 2.5 Tensor Core / WMMA 映射

现代 GPU 有专用矩阵计算单元。算子级优化需要**把小块矩阵乘映射到 Tensor Core 的固定尺寸指令**（如 `mma.m16n8k16`）。

```
需要精确匹配的：
  · 数据类型（FP16/BF16/TF32/FP8/INT8）
  · 矩阵形状（16x16、8x8 等固定 tile）
  · 数据在共享内存中的排布（swizzle 模式）
```

### 2.6 自动调优（Auto-Tuning）

一个算子的"最优实现"依赖于**输入形状 + 硬件型号**，参数空间巨大（tile 尺寸、循环顺序、向量化因子、unroll 因子……）无法手工穷举。

主流自动调优框架：

| 框架 | 特点 |
| --- | --- |
| **AutoTVM** | 基于模板 + 机器学习代价模型搜索 |
| **Ansor / MetaSchedule** | 无模板，自动生成调度空间 |
| **Triton Autotune** | 编译期常量 + 装饰器语法，工程易用 |
| **CUTLASS Profiler** | NVIDIA 官方，针对 GEMM/Conv 等 |

## 三、与图级优化的关系

```
图级优化（决定要算什么）
      ↓ Lowering
算子级优化（决定每个算子怎么算）   ← 本层
      ↓ Lowering
指令优化（决定生成什么机器指令）
```

图级优化后的图越"干净"（融合充分、冗余消除彻底），算子级优化的空间越大——一个含大量小算子的脏图，根本没法做有效 tiling。

## 四、实践清单

- 判断算子是**计算密集型（Compute-Bound）** 还是 **访存密集型（Memory-Bound）**（用 roofline 模型）
- 计算密集型 → 重点做 Tensor Core 映射、寄存器分块
- 访存密集型 → 重点做 tiling、共享内存复用、[向量化](docs/AI-compiler/pipeline/graph-optimizer/tag-vectorization=向量化.txt)访存
- 用 Nsight Compute / rocprof 等工具验证优化效果
