# Operator Optimizer

`Operator Optimizer`（OpsOptimizer）对 [Tensor IR](docs/AI-compiler/pipeline/tensor-IR/index.md) 进行算子级优化，也叫**后端优化**。

## 后端优化概述

- 针对单个算子的内部具体实现优化，使算子性能达到最优。
- 主要流程为对算子节点的输入、输出、内存循环方式和计算逻辑进行编排与转换。
- 优化是硬件相关的，主要包括循环优化、算子融合、tiling、张量化。
- 只关注单个算子节点，与前端优化的局部或全局视野不同。

![后端优化](https://developer.qcloudimg.com/http-save/11307734/68e2035b2adf594a5c04cc8db249cebf.png)

在这一阶段，需要针对不同的硬件架构/微架构，选择不同的算法实现方式，目的是找到算子的最优实现，达到最优性能。同一算子的不同形态（如 Conv1x1、Conv3x3、Conv7x7）会有不同的循环优化方法。实现方式多种多样，可以人工凭经验手写算子实现，也可以通过自动调优搜索高性能实现。

算子级优化结束后，进入 [Codegen](docs/AI-compiler/pipeline/codegen/index.md) 阶段。

## 算子优化的挑战

算子根据计算形式的特点可分为访存密集型与计算密集型。

### 访存密集（Memory-Bound）型

执行过程中主要涉及大量内存读写。这类算子频繁从内存读取数据，执行简单计算，再将结果写回内存，性能受限于内存带宽和访问延迟，而不太受计算能力限制。

例如 RNN 训练任务，其网络结构计算密度很低，瓶颈转移到 host 端的 Op Launch 上，算子的计算 kernel 之间出现大量空白。

### 计算密集（Compute-Bound）型

执行过程中主要涉及大量计算，对内存访问相对较少。这类算子主要依赖 CPU 或 GPU 的计算能力，对内存带宽和访问延迟的需求不是特别高。矩阵乘法、卷积运算、复杂数学函数计算等数值计算密集型的算法通常属于这一类。

### 主要挑战

由于算子种类多样，没有一个一网打尽的优化手段能解决所有算子的高性能执行问题，算子优化存在以下挑战：

- **优化手段多样**：针对不同种类算子、相同算子的不同参数，需要在不同情况下权衡优化手段及其参数，即使对优化专家也相当耗费精力。
- **通用性与移植性**：不同硬件架构差异大，优化方法需考虑硬件可用指令集、内存带宽、算力以及存储层次等因素。
- **不同优化间相互影响**：各种优化之间可能相互制约、相互影响，找到最优的优化组合与序列是困难的组合优化问题，甚至是 NP 问题。

## 算子优化方法

算子的不同实现，性能差距千差万别，最好与最差相比甚至可达上百倍的时间开销。业界有多种做法获得高性能算子。

### 算子库

最常见的方式是将预置的算子实现封装成**计算库**。算子库是一组高度优化的计算核心函数，用于加速特定类型的计算任务，例如矩阵乘法、卷积、循环神经网络等，通常由硬件厂商或第三方开发者编写，旨在充分利用硬件平台的计算能力，并提供易用高效的接口。

- **cuDNN**：英伟达开发的深度学习加速库，针对常见深度学习算法高度优化。算子函数基于 CUDA 实现，利用 GPU 的并行性和向量化特性，并通过半精度浮点数运算、算法重排等技术进一步加速。
- **Eigen**：C++ 编写的线性代数库，实现矩阵乘法、矩阵求解、特征值分解等。算子函数使用 SIMD 指令集实现，可在不同 CPU 架构上自动优化。

这种方法存在三个问题：

- **算子迭代更新快**：AI 领域算法和模型经常迭代，算子库需要及时跟进，开发者要不断更新和优化现有实现。
- **多平台移植的一致性**：算子库通常针对特定硬件平台（GPU、CPU）优化设计，移植到不同平台时，硬件架构和指令集的差异需要特定优化和调整，才能保证计算结果一致。
- **算子组合爆炸**：复杂模型结构或多阶段数据处理流程中算子组合繁多，参数多样、融合大算子等使算子之间的参数与组合方式变得多样而复杂。

### 自动生成

为解决上述问题，可通过自动化生成高性能 kernel 来减小算子开发开销。目前有两种主流方法：

- **Auto Tuning**：通过自动搜索和优化参数组合来生成高效 kernel 代码。通常基于启发式算法或机器学习技术，自动探索不同参数组合以找到最佳性能配置，并可根据具体硬件平台和任务特性自动选择合适的优化策略。
- **Polyhedral**：基于数学多面体理论的编译优化方法，用于描述循环嵌套的迭代空间和数据依赖关系，并生成高效的循环 kernel 代码。通过对循环迭代空间进行变换和重组，可实现循环并行化、内存局部性优化等，从而提升性能。

## 子章节

| 章节 | 内容 |
| --- | --- |
| [Operator-Level-Optimization](docs/AI-compiler/pipeline/operator-optimizer/Operator-Level-Optimization/index.md) | 算子级优化：循环分块、循环重排、向量化、并行化、自动调优 |
| [Polyhedral-compilation](docs/AI-compiler/pipeline/operator-optimizer/Polyhedral-compilation/index.md) | 多面体编译：Pluto、polyhedral 等资料 |
| [Polyhedral Model 之后：Auto-Tiling 与 Auto-Tensorize](docs/AI-compiler/pipeline/operator-optimizer/Polyhedral-Model之后-Auto-Tiling-与-Auto-Tensorize的技术演进/index.md) | 多面体模型的局限，以及 auto-tiling / auto-tensorize 的技术演进 |

相关横切主题：[Memory-Optimization](docs/AI-compiler/pipeline/Memory-Optimization/index.md)、[LLM-Specific-Optimization](docs/AI-compiler/pipeline/LLM-Specific-Optimization/index.md)。
