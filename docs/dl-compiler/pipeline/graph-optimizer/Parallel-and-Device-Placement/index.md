# Parallel and Device Placement（并行与设备放置）

> **定位**：图级优化的**并行/设备分派**方向。它决定了大图**在哪里执行、以什么并行度执行**，是多卡/异构编译器的核心能力。

## 一、图切分（Graph Partitioning）

将大图**切分成子图**，分配到不同设备或不同后端执行。

```
应用场景：
  · 多卡/多设备：子图分到不同 GPU
  · 异构后端：部分算子给 NPU，不支持的回退到 CPU
  · 编译单元划分：便于并行编译
```

**切分策略**：

- **按设备能力**：某算子在 NPU 上不支持 → 回退 CPU 子图
- **按并行策略**：数据并行/张量并行/流水线并行下的切分模式
- **按最小通信**：min-cut 找出通信量最小的切分边界

## 二、设备放置（Device Placement）

决定每个算子/子图**在哪个设备上执行**，权衡计算与数据传输成本。

```
    [OpA]@GPU0 ──传输──▶ [OpB]@GPU1
                ▲
         传输开销要纳入决策
         （放同设备省传输，但要均衡负载）
```

**核心权衡**：

- **传输开销**：跨设备张量拷贝（PCIe / NVLink / 网络）
- **负载均衡**：算力分布是否均匀，避免热点设备成为瓶颈
- **显存占用**：模型太大时必须切到多卡

**主流做法**：

- **规则式**：如 TensorFlow 的 `tf.device` / PyTorch 的 `.to(device)`
- **代价模型 + 搜索**：基于设备算力、带宽、张量大小的图搜索
- **强化学习**：Google Placer 系列，用 RL agent 学习放置策略

## 三、算子并行调度（Operator Parallel Scheduling）

识别图中**无依赖的算子**，标记为可并行执行（对应硬件的多流/多核）。

```
    ┌─▶ [OpA]  ┐
x ──┤          ├──▶ [OpD]    OpA、OpB、OpC 无依赖
    ├─▶ [OpB]  │              → 可并行
    └─▶ [OpC]  ┘
```

在 GPU 上，这通常表现为**多 CUDA Stream**：不同流上的 kernel 可并发执行。编译器需要：

- 分析数据依赖图，标记独立子图
- 分配 Stream
- 插入必要的 event / synchronize

## 四、与其他优化的关系

- 与 **[分布式/通信优化](docs/AI-compiler/pipeline/graph-optimizer/Distributed-and-Communication/index.md)** 强相关：切分后需要通信算子
- 与 **[调度与执行](docs/AI-compiler/pipeline/graph-optimizer/Scheduling-and-Execution/index.md)** 协同：并行标记 → 具体的运行时调度
- 与 **[内存优化](docs/AI-compiler/pipeline/Memory-Optimization/index.md)** 相关：设备放置直接决定显存占用
