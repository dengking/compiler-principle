# Instruction Optimization（指令优化 / 后端代码生成优化）

> **定位**：AI 编译器**后端最底层**的优化，直接面向硬件指令。前面的图级、算子级优化决定了"要发什么指令"，这一层决定"这些指令如何在硬件上排布、调度、执行"。它是把**理论 FLOPS 变成实际 FLOPS** 的最后一公里。

## 一、为什么后端指令优化至关重要

即使算子级把 tile / 向量化都做完了，如果指令排布不当，仍可能只跑出理论峰值的 30~50%。原因：

```
现代 GPU 是深度流水线 + 多发射架构：
  · 访存指令延迟：数百 cycle（HBM）、几十 cycle（L2）、几 cycle（共享内存）
  · 计算指令：Tensor Core 一条指令算 4096 次乘加
  · 若指令依赖链紧密 → 流水线气泡 → 硬件闲置
```

## 二、核心技术

### 2.1 硬件原语映射（Hardware Intrinsic Mapping）

直接映射到硬件的**专用指令**，绕过通用路径。

```
矩阵乘 → Tensor Core 指令：
  · NVIDIA: mma.sync / wmma / wgmma（Hopper）
  · AMD:    v_mfma_*（MI 系列 Matrix Core）
  · Intel:  AMX (Advanced Matrix Extensions)

访存 →
  · ldmatrix.sync（协作加载 Tensor Core 输入）
  · cp.async（异步拷贝，重叠计算与访存，Ampere+）
  · TMA（Tensor Memory Accelerator，Hopper+）

Softmax / 归约 →
  · warp shuffle 指令做 warp 内归约
  · redux.sync（Ampere+ 硬件归约）
```

### 2.2 指令调度（Instruction Scheduling）

在保证语义正确的前提下**重排指令顺序**，最大化流水线利用率、隐藏访存延迟。

```
朴素顺序（每步等待前一步）：
  LOAD A0   [等 400 cycle]
  COMPUTE 0
  LOAD A1   [等 400 cycle]
  COMPUTE 1
  ...

调度后（软件流水线）：
  LOAD A0
  LOAD A1
  LOAD A2         ← 提前发出后续 load
  COMPUTE 0       ← 此时 A0 已经就绪
  LOAD A3, COMPUTE 1
  LOAD A4, COMPUTE 2
  ...             ← 计算与访存重叠
```

**软件流水线（Software Pipelining）** 是这一层最经典的优化，广泛用于 GEMM、Conv 等计算密集型算子。

### 2.3 寄存器分配（Register Allocation）

寄存器是 GPU 上最快的存储，但每个线程数量有限（通常 255 个 32-bit 寄存器）。

```
关键权衡：
  · 寄存器多 → 单线程能保存更多中间变量 → 减少访存
  · 寄存器多 → 每 SM 能容纳的线程少 → 占用率下降

编译器策略：
  · 图着色寄存器分配
  · 溢出（spill）到 local memory 时的启发式选择
  · 结合占用率反馈调整
```

### 2.4 多 SM 负载均衡（Workload Balancing）

将 grid 中的 block 均匀分发到 GPU 所有 SM，避免核心闲置。

```
问题场景：
  · Batch 太小 → block 数 < SM 数 → 部分 SM 闲置
  · Block 之间工作量不均 → 快的 SM 等慢的

解决：
  · Persistent kernel：每个 SM 常驻一个 block，动态取任务
  · Grid stride loop：一个 block 处理多个 tile
  · Split-K：对 GEMM 的 K 维切分，制造更多 block
```

### 2.5 分支消除与谓词化（Predication）

GPU 是 SIMT 架构，warp 内分支分歧（divergence）代价高。编译器策略：

```
if (cond)  a = x + y;      →   pred = cond;
else       a = x - y;           a = pred ? (x+y) : (x-y);
    分支                             谓词执行，无分歧
```

### 2.6 循环展开与常量传播

```
for i in range(4):        →    a[0] = ...
    a[i] = ...                  a[1] = ...
                                a[2] = ...
                                a[3] = ...
   循环 + 索引计算              纯计算指令，编译器可进一步优化
```

## 三、主流后端

| 后端 | 覆盖硬件 | 特点 |
| --- | --- | --- |
| **LLVM NVPTX** | NVIDIA GPU | MLIR/XLA 常用，生成 PTX |
| **CUDA C → NVCC → PTX/SASS** | NVIDIA GPU | 手工/生成的 CUDA C 路径 |
| **ROCm LLVM** | AMD GPU | MI 系列 GPU |
| **Triton MLIR** | GPU 通用 | 高层 Python DSL，自动做大量指令调度 |
| **TVM CodeGen** | 多后端（CUDA/LLVM/OpenCL/…) | 基于调度原语生成 |

## 四、与其他层的关系

```
图级优化 ──→ 算子级优化 ──→ 指令优化 (本层)
  "要算什么"    "怎么算"       "指令怎么排"

本层的收益上限，被前两层的决策严格约束：
  · 前面 tile 尺寸没选对，这里做再多流水线也无用
  · 前面选了错的数据类型，这里根本用不上 Tensor Core
```

## 五、实践清单

- 使用 Nsight Compute 观察 **SM occupancy、warp stall reason、指令发射率**
- 关注 **memory pipeline stall**（访存延迟未隐藏） vs **execution pipeline stall**（计算单元等待）
- Triton 用户：多试 `num_stages`（软件流水线深度）、`num_warps`
- CUDA 用户：关注 PTX `ld.global.ca` vs `ld.global.cs` 缓存标志
