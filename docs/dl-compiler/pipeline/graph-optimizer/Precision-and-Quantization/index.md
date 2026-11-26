# Precision and Quantization（精度与量化）

> **定位**：图级优化中面向**数值表示**的一类变换，通过降低精度或替换算法，在保证效果的前提下大幅提升算力利用率与显存效率。

## 一、混合精度（Mixed Precision）

在图中自动插入精度转换，让适合的算子用低精度（FP16/BF16/FP8），敏感算子保留高精度（FP32）。

```
    Conv/MatMul  → FP16/BF16/FP8（计算密集，低精度加速明显）
    LayerNorm/Softmax → FP32（数值敏感，保精度）

编译器自动：
  · 插入 cast 算子
  · 决策精度分配（按算子敏感度）
  · 消除冗余 cast（cast(cast(x)) 化简、fp16↔fp32 抵消）
  · 处理 loss scaling（防止 FP16 下溢）
```

**精度选择表**：

| 类型 | 位宽 | 典型用途 |
| --- | --- | --- |
| FP32 | 32 | 归约、损失函数、优化器主副本 |
| FP16 | 16 | 训练/推理主计算，需 loss scaling |
| BF16 | 16 | 训练主计算，动态范围与 FP32 相同，无需 loss scaling |
| TF32 | 19 | Ampere+ 自动使用，无需代码改动 |
| FP8 (E4M3/E5M2) | 8 | Hopper+ 推理与训练前向 |

## 二、量化（Quantization）

将 FP32 权重/激活转为 **INT8 / INT4 / INT2** 等整数类型，图级需要一整套变换：

```
1. 插入量化/反量化算子（Quantize / Dequantize）
2. 量化算子融合（QDQ 融合进计算算子内部）
3. 消除冗余的 quant-dequant 对
4. 量化参数（scale / zero-point）传播
5. INT 计算的溢出保护（累加用更宽的类型）
```

### 2.1 量化模式

| 模式 | 说明 |
| --- | --- |
| **PTQ（Post-Training Quantization）** | 训练后校准 scale/zero-point，不改权重 |
| **QAT（Quantization-Aware Training）** | 训练时插入伪量化，模型学习适应量化误差 |
| **权重量化（W-only）** | 只量化权重，激活保持 FP16（W4A16 / W8A16） |
| **全量化（W+A）** | 权重和激活都量化（W8A8） |
| **动态量化** | 运行时统计激活分布 |
| **静态量化** | 编译期确定所有 scale |

### 2.2 QDQ 融合示例

```
朴素形式：
    Q(x) ──▶ Dequant ──▶ MatMul ──▶ Q(y) ──▶ Dequant ──▶ ReLU ──▶ Q ...

融合后：
    Q(x) ──▶ IntMatMul(int8 → int32 累加) ──▶ Requantize ──▶ IntReLU ...
    → 中间保持整数，只有必要时才 dequant
```

## 三、算法级算子替换

用**数学等价但更高效**的算法替换算子。图级优化器根据输入形状/硬件特性自动做等价替换：

| 替换 | 适用场景 |
| --- | --- |
| **普通卷积 → Winograd 卷积** | 3×3 卷积，减少乘法次数（约 2.25×） |
| **普通卷积 → FFT 卷积** | 大 kernel（如 7×7+） |
| **普通卷积 → im2col + GEMM** | 通用后端，映射到 BLAS 库 |
| **普通卷积 → Implicit GEMM** | GPU cuDNN 主流实现 |
| **MatMul → 针对特定 shape 的 GEMM 库调用** | Tall-and-skinny、Batched GEMM |
| **Softmax → Online Softmax** | 与后续算子融合时（如 Attention） |

## 四、与其他层的协同

```
图级（本层）    ── 决策精度分配、插入/消除 cast、算法替换
   ↓
算子级          ── 生成对应低精度的 kernel（FP8 GEMM / INT8 GEMM）
   ↓
指令级          ── 映射到 Tensor Core 的低精度指令（mma.m16n8k16.f16 等）
```

低精度收益的完整释放，需要三层协同：图级选对精度 → 算子级生成正确 kernel → 指令级用上专用硬件。

## 五、面试高频

| 问题 | 要点 |
| --- | --- |
| 为什么 BF16 比 FP16 更适合训练？ | 动态范围与 FP32 相同，无需 loss scaling |
| INT8 量化误差来源？ | 截断误差 + 量化步长舍入 + scale 选择偏差 |
| QAT 和 PTQ 差异？ | QAT 训练时感知量化误差；PTQ 只在训练后校准 |
| 为什么 W4A16 流行？ | 大模型激活小、权重大，量化权重直接减显存与带宽 |
| 反量化融合的关键？ | 权重存 INT4，就地在计算前解量化，不写回 HBM |
