# Distributed and Communication Optimization（分布式与通信优化）

> **定位**：图级优化在**多卡/多机训练与推理**场景下的扩展。它把跨设备通信作为"一等公民"纳入计算图，通过**融合、重叠、并行策略变换**三条主线来隐藏通信开销。这是大模型时代不可回避的核心方向。

## 一、通信算子融合（Communication Fusion）

把多个小的通信操作（AllReduce/AllGather）合并成大的，减少通信次数。

```
多个梯度 AllReduce → 打包成一个大 AllReduce
  · 减少通信启动开销（每次 AllReduce 都有固定 latency）
  · 提高带宽利用率（大消息才能打满 NVLink/IB）
```

**典型实现**：

- **PyTorch DDP Bucketing**：反向传播时把梯度按 25MB 一桶打包，桶满即发起 AllReduce
- **Horovod Tensor Fusion**：同上思路，通用实现
- **DeepSpeed / FSDP**：结合 ZeRO 分片做通信融合

**权衡**：

- 桶太小 → 通信次数多，启动开销高
- 桶太大 → 反向计算与通信重叠机会变小

## 二、计算-通信重叠（Compute-Communication Overlap）

让通信（如梯度同步）与计算并行进行，隐藏通信延迟。

```
反向传播 layer N 的同时 → AllReduce layer N+1 的梯度
    → 通信被计算"掩盖"
```

**关键条件**：

- 通信在独立的 stream/线程上执行
- 通信内核不阻塞主 stream 的计算
- 有足够多的独立通信任务可调度

**硬件基础**：

- NVLink / IB 上的 GPU-Direct RDMA
- SM 上独立的 copy engine
- NCCL 的多 channel 并发

## 三、并行策略相关图变换

大模型训练需要 **3D 并行**（DP + TP + PP），每种并行策略都对应特定的图变换：

### 3.1 数据并行（DP）

```
图变换：
  · 图复制到每张卡
  · 在反向图末尾插入 AllReduce（梯度同步）
  · 结合 ZeRO：状态/梯度/参数分片，插入 AllGather/ReduceScatter
```

### 3.2 张量并行（TP，Tensor Parallelism）

沿算子内部维度切分，通信算子插入到关键位置：

```
Column-Parallel Linear:
  输入 x → 每卡持有部分列的 W_i → 每卡输出部分列 y_i
  最后 AllGather 拼接 y

Row-Parallel Linear:
  输入 x 已经沿列切分 → 每卡持有部分行的 W_i
  每卡计算 y_i → AllReduce 求和得到 y

Megatron 的典型组合：
  MLP: ColumnParallel(fc1) → GELU → RowParallel(fc2)
       → 前后各一次 AllReduce
```

### 3.3 流水线并行（PP）

```
图变换：
  · 图按层切分为 stage
  · 相邻 stage 之间插入 Send/Recv
  · 微批调度（1F1B / Interleaved / Zero Bubble）
```

详见 [Scheduling-and-Execution](docs/AI-compiler/pipeline/graph-optimizer/Scheduling-and-Execution/index.md) 中的流水线并行章节。

### 3.4 序列并行（SP）与上下文并行（CP）

大模型长上下文场景的扩展：

- **序列并行**：把序列维度切到不同卡，通信量与序列长度线性相关
- **上下文并行**（Ring Attention）：让 Q/K/V 在卡间"环形"传递

## 四、通信原语速查

| 原语 | 语义 | 常见用途 |
| --- | --- | --- |
| **AllReduce** | 每卡持有相同 sum 结果 | DP 梯度同步、TP 中 Row-Parallel 输出 |
| **AllGather** | 每卡拼接得到完整数据 | ZeRO 参数收集、TP 中 Column-Parallel 输出 |
| **ReduceScatter** | 每卡持有部分 sum 结果 | ZeRO 梯度分片 |
| **All-to-All** | 每卡向其他卡发不同数据 | MoE 路由 |
| **Send/Recv** | 点对点 | 流水线并行 stage 间 |
| **Broadcast** | 一对多 | 初始参数广播 |

## 五、编译器视角的关键 Pass

现代大模型编译器（如 **Megatron / DeepSpeed / TorchTitan / Alpa**）通常包含：

1. **并行策略搜索 / 标注**：决定每个算子的并行方式
2. **通信插入 Pass**：按并行标注插入通信算子
3. **通信融合 Pass**：合并相邻通信
4. **通信-计算重叠 Pass**：拆分算子、重排顺序，制造重叠机会
5. **通信内核选择**：NCCL / MSCCL / 自定义 kernel

## 六、面试高频

| 问题 | 要点 |
| --- | --- |
| DDP 的 bucket 是干什么的？ | 通信融合，减少 AllReduce 次数与固定开销 |
| ZeRO 的三阶段？ | Optimizer state / Gradient / Parameter 分片，通信量递增 |
| TP 中 Column vs Row parallel？ | 前者切列后 AllGather；后者切行后 AllReduce |
| 流水线并行 bubble 怎么减？ | 1F1B / Interleaved / Zero-Bubble 调度 |
| MoE 的通信瓶颈？ | All-to-All，需要与专家计算重叠 |
| 长上下文场景的通信策略？ | 序列并行 / Ring Attention，控制 O(N) 通信 |
