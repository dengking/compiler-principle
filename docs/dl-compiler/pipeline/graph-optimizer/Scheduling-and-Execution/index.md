# Scheduling and Execution（调度与执行）

> **定位**：图级优化中面向**时间维度**的一类变换。它不改变要执行的算子集合，而是通过**调整算子的执行顺序、并发度、数据搬运时机**来榨取性能。

## 一、算子调度重排（Operator Scheduling）

在满足依赖的前提下**调整算子执行顺序**，优化目标：

```
- 降低峰值内存（让占内存的张量生命周期不重叠）
- 提高并行度（让可并行算子靠拢，制造更大的并发窗口）
- 隐藏延迟（计算与数据加载重叠）
```

### 1.1 面向峰值内存的重排

```
朴素顺序：
  [A] 产生 t1 (100MB, 长生命周期)
  [B] 产生 t2 (100MB, 长生命周期)
  [C] 消费 t1
  [D] 消费 t2
      → 峰值同时活着 t1 和 t2 = 200MB

调度后：
  [A] → [C]（尽快消费 t1，让 t1 早死）→ [B] → [D]
      → 峰值 = 100MB
```

这是**Sethi-Ullman 算法**在深度学习图上的推广。

### 1.2 面向并行的重排

将可并行算子靠拢，形成较大的并行窗口，便于多流调度器一次性发射多个 kernel。

## 二、异步执行与流水线（Asynchronous Execution & Pipelining）

```
计算与数据传输重叠：
    时刻1: [传输 batch1]
    时刻2: [传输 batch2] [计算 batch1]   ← 重叠
    时刻3: [传输 batch3] [计算 batch2]
    → 隐藏数据传输延迟
```

### 2.1 CPU-GPU 流水线

```
Data Loader (CPU) ──▶ H2D 拷贝 ──▶ GPU 计算 ──▶ D2H 拷贝

  三个阶段并行 →  吞吐量 ≈ max(阶段耗时)
```

### 2.2 GPU 内多 Stream 流水线

在 GPU 上用不同 CUDA Stream 让计算和拷贝并行：

```
Stream 0：compute kernel A → compute kernel B → ...
Stream 1：cp.async 预取下一批数据      → ...
Stream 2：D2D copy 到下一个消费者        → ...
```

### 2.3 流水线并行（Pipeline Parallelism）

大模型训练场景，把网络按层切成若干 stage，micro-batch 沿 stage 流水：

```
时间→
Stage 0: [F1][F2][F3][F4][B4][B3][B2][B1]
Stage 1:     [F1][F2][F3][F4][B4][B3][B2][B1]
Stage 2:         [F1][F2][F3][F4][B4][B3][B2][B1]
Stage 3:             [F1][F2][F3][F4][B4][B3][B2][B1]
```

调度算法：1F1B、Interleaved 1F1B、Zero Bubble 等。

## 三、预取（Prefetch）

提前把下一步需要的数据搬到高速存储，隐藏访存延迟。

```
标准：           t=0: 计算需要 A → load A（等 400 cycle）→ 计算
预取：           t=-1: 提前发出 load A → t=0: 立即计算

硬件支持：
  · Ampere+：cp.async（异步全局→共享内存）
  · Hopper+：TMA（Tensor Memory Accelerator）
```

**软件流水线 = 预取 + 双缓冲 + 计算/访存交替**，是 GEMM 类内核的标准写法。

## 四、算子调度的搜索空间

对每个可并行位置，编译器可能面临的决策：

- 放到哪个 stream？
- 是否插入 event 同步？
- 是否需要 prefetch？
- 是否合并成 CUDA Graph（捕获后一次性提交，消除逐 kernel 启动开销）？

主流做法：**代价模型 + 启发式搜索**，部分工作用强化学习探索调度空间。

## 五、与其他优化的关系

- 依赖 **[并行与设备放置](docs/AI-compiler/pipeline/graph-optimizer/Parallel-and-Device-Placement/index.md)** 的结果——先决定放哪，再决定何时执行
- 与 **[内存优化](docs/AI-compiler/pipeline/Memory-Optimization/index.md)** 强耦合——调度重排是降低峰值内存的主要手段
- 与 **[分布式/通信](docs/AI-compiler/pipeline/graph-optimizer/Distributed-and-Communication/index.md)** 结合 —— 通信-计算重叠是本层的重要模式

## 六、面试高频

| 问题 | 要点 |
| --- | --- |
| 峰值内存怎么优化调度？ | 让张量早生早死，避免生命周期堆叠（区间调度） |
| CUDA Graph 优化了什么？ | 消除逐 kernel 启动开销，适合小 kernel 密集场景 |
| 流水线并行的 bubble 怎么减少？ | 1F1B、Interleaved、Zero-Bubble 调度 |
| 预取的关键约束？ | 必须有足够多的 in-flight 内存事务、共享内存双缓冲够用 |
