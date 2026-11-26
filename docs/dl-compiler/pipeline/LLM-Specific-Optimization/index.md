# LLM-Specific Optimization（大模型时代专项优化）

> **定位**：针对 **Transformer、MoE、长上下文、Agent AI** 等大模型场景的定制化编译优化。这些优化通常**跨越图级、算子级、内存、指令四个层级**，是端到端协同设计的产物，也是当前 Rubin/Blackwell 架构适配的核心方向。

## 一、为什么大模型需要专项优化

通用编译器的四大类优化对大模型仍然适用，但**收益远远不够**。原因：

```
大模型场景的独特挑战：
  1. Attention 的 O(N²) 中间矩阵    → 长序列下访存爆炸
  2. KV Cache 随序列线性增长        → 显存/带宽同时告急
  3. MoE 的稀疏 + 通信              → 通用编译器难以处理
  4. 推理 batch 内序列长度差异大    → 静态调度效率低
  5. 权重远大于激活                  → 传统"激活复用"思路失效
```

于是催生了**跨层协同**的一系列专项优化。

## 二、注意力机制专项优化

### 2.1 FlashAttention 系列融合编译

自动将 `Q·K^T`、`Softmax`、`·V` **全流程融合**，通过分块计算让中间数据全程驻留共享内存/寄存器，大幅降低 HBM 访存。

```
标准 Attention：
  Q,K,V ──▶ QK^T ──▶ [N×N 矩阵写回 HBM] ──▶ Softmax ──▶ [写回 HBM] ──▶ ·V

FlashAttention：
  分块循环：
    for each block:
      load Q_block, K_block, V_block 到 SRAM
      在 SRAM 内完成 QK^T + online softmax + ·V
      仅输出结果写回 HBM
  → 中间的 N×N 矩阵从未出现在 HBM 中
```

**这是当前大模型推理的核心性能来源。** 属于典型的 **图级融合 + 算子级 tiling + 数值算法（online softmax）** 三者协同。

### 2.2 PagedAttention 内存管理

**类虚拟内存**思想的 KV 缓存调度机制，支持非连续显存块存储 KV。

```
传统 KV Cache：
  为每个序列预分配 max_len × d 的连续显存
  → 短请求也占用完整槽位，碎片严重

PagedAttention (vLLM)：
  · KV 划分为固定大小 page（如 16 个 token）
  · 每个请求持有一张"page 表"
  · 空闲 page 全局共享
  → 显存利用率大幅提升，支持高并发批量推理
```

### 2.3 前缀缓存（Prefix / Prompt Caching）

自动识别重复的系统提示、RAG 上下文，缓存对应 KV 结果，只增量计算新 Token。

```
场景（Agent AI 极度典型）：
  系统提示（5000 tokens，每次相同）+ 用户问题（50 tokens）

无 prefix cache：每次都重算 5050 tokens 的 KV
有 prefix cache：命中 5000 tokens 缓存，只算 50 tokens
  → 长上下文推理成本降低一个数量级
```

## 三、MoE 模型专属编译优化

### 3.1 路由与通信流水化

静态分析专家路由模式，优化"路由 → 分发 → 计算 → 归并"的执行时序，将 **All-to-All 通信与专家计算重叠**，隐藏跨卡互联延迟。

```
串行流程：
  Route → All-to-All(send) → Expert compute → All-to-All(recv) → Merge
  [────── 全程串行，通信空等 ──────]

流水化：
  Route(t)  ─▶ Send(t)  ─▶ Compute(t)  ─▶ Recv(t)  ─▶ Merge(t)
              Route(t+1) ─▶ Send(t+1)  ─▶ Compute(t+1) ...
  → 相邻 micro-batch 的通信与计算重叠
```

### 3.2 稀疏计算生成

自动跳过未激活专家的计算，生成稀疏高效内核，避免无效算力开销。

```
Top-K 路由后（如 K=2，专家总数 128）：
  只有 2/128 ≈ 1.5% 的专家参与计算
  编译器需要：
    · 生成 gather/scatter 内核收发 token
    · 生成"批处理稀疏 GEMM"（grouped GEMM）
    · 避免为未激活专家启动 kernel
```

### 3.3 专家负载均衡编译

结合路由分布调整专家调度策略，解决专家负载不均导致的算力浪费。

## 四、长上下文推理优化

### 4.1 KV 缓存量化压缩

编译期自动对 KV 缓存做**低比特量化（INT4/INT2）**、稀疏化处理，线性降低长序列显存占用，支撑百万级 Token 场景。

### 4.2 分块流水线并行

将超长上下文切分为数据块，流水化完成计算与通信，平衡单卡算力与跨卡传输开销。

### 4.3 稀疏注意力编译

自动识别 **滑动窗口、块稀疏、Longformer、StreamingLLM** 等注意力模式，生成定制化高效内核，剔除无效计算。

## 五、低精度与量化编译

### 5.1 自动混合精度

自动识别算子精度敏感度，在不损失效果的前提下切换 **BF16/FP8/INT8**，充分释放 Tensor Core 算力。

```
典型策略：
  Conv/MatMul       → FP16/BF16/FP8（计算密集，低精度加速明显）
  LayerNorm/Softmax → FP32（数值敏感，保精度）
  Loss scale / Reduce sum → FP32

编译器职责：
  · 精度传播 & cast 插入
  · 冗余 cast 消除
  · 保证数值稳定性
```

### 5.2 量化计算融合

将 **反量化（Dequantize）与算子计算融合**为单内核，消除量化带来的额外访存开销。

```
朴素路径：
  权重(INT4) ──▶ Dequant ──▶ FP16 权重 ──▶ MatMul
     [多一次 HBM 写回 FP16 权重，显存 & 带宽双损失]

融合路径：
  权重(INT4) ─────────┐
                     └──▶ 单 kernel: load INT4 → 就地 dequant → mma
     [权重全程 INT4 存在显存，只在计算前一刻反量化]
  → 让 INT4/INT8 推理兼顾显存与速度（W4A16 的关键）
```

## 六、主流框架

| 框架 | 定位 | 核心优化能力 |
| --- | --- | --- |
| **vLLM** | 推理服务 | PagedAttention · Continuous Batching · Prefix Caching |
| **TensorRT-LLM** | NVIDIA 推理 | 深度融合 · FP8 · In-flight Batching |
| **SGLang** | Agent 场景 | RadixAttention（前缀树缓存）· 结构化输出 |
| **DeepSpeed-Inference** | 训练/推理 | ZeRO · MoE 优化 · 张量并行 |
| **Megatron-LM** | 大规模训练 | 3D 并行 · 序列并行 · 通信重叠 |

## 七、与四大通用方向的关系

```
大模型专项优化 = 四大通用优化的"深度组合与场景特化"

FlashAttention  = 图级融合 + 算子级 tiling + 数值重构
PagedAttention  = 内存优化的极致形态（虚拟内存化）
量化融合         = 图级融合 + 指令级 Tensor Core 特化
MoE 通信重叠     = 图级调度 + 通信/计算流水线
```

## 八、面试高频考点

| 问题 | 要点 |
| --- | --- |
| FlashAttention 为什么快？ | 中间 N×N 矩阵不写回 HBM，靠 online softmax 分块 |
| PagedAttention 解决什么问题？ | KV Cache 显存碎片 & 动态序列长度 |
| Prefix Caching 的典型场景？ | 长系统提示 / RAG / Agent 多轮 |
| MoE 编译最难在哪？ | 稀疏路由 + All-to-All 通信 + 负载不均 |
| W4A16 与 W8A8 的区别？ | W4A16 权重 INT4 激活 FP16，重反量化融合；W8A8 全 INT8，需重激活量化 |
| KV Cache 量化的注意点？ | 长序列累计误差、逐 head/逐 token scale |
