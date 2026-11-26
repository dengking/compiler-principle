# TensorRT

**TensorRT 是 NVIDIA 推出的专属深度学习推理优化引擎与运行时框架**，专门针对 NVIDIA 全系 GPU 做硬件级深度优化，是当前 NVIDIA 平台上推理性能的工业级天花板方案。

承接上一个关于 ONNX 的问题：ONNX 是跨框架的通用中间格式，而 TensorRT 是把通用模型“压榨”到硬件极限的最终优化执行引擎，二者常组成 `PyTorch/TensorFlow → ONNX → TensorRT` 的经典部署链路。

## 一、核心优化原理：为什么它比原生框架快数倍

TensorRT 的性能提升不是单一技巧，而是多层优化叠加的结果，核心手段包括：

### 1. 计算图重构与算子融合

这是最基础也收益最高的优化：

- 剔除训练冗余节点：自动移除 Dropout、恒等映射、无用分支等仅训练阶段需要的结构
- 纵向算子融合：把连续的多个小算子合并成一个 CUDA 内核，比如经典的 `Conv + BN + ReLU` 三合一，避免多次内核启动开销和反复的显存读写
- 横向算子融合：把输入相同、结构一致的多个并行算子合并执行
- 在 Transformer 结构中，会进一步融合 QKV 投影、Attention 计算、FeedForward 等多层算子

### 2. 低精度量化 + 硬件加速

- 支持 FP32/FP16/BF16/INT8/FP8/FP4 多级精度，可根据业务精度要求灵活选择
- 直接调用 GPU 的 **Tensor Core** 硬件加速矩阵运算：比如 Hopper 架构 H100 的 FP8 Tensor Core、Blackwell 架构 B200 的 FP4 加速，算力密度比单精度高数倍
- 提供内置校准工具，无需重新训练即可完成 INT8 量化，通常能在精度损失极小的前提下，把显存占用降低一半以上、吞吐提升 2~4 倍

### 3. 内核自动调优（Auto-Tuning）

同一个算子存在多种 CUDA 实现（不同分块策略、访存模式），TensorRT 构建引擎时会针对**当前具体的 GPU 型号、输入尺寸**，实际运行测试所有实现，选出耗时最短的版本，确保每一款 GPU 都能得到专属最优解，而非通用兼容实现。

### 4. 内存与调度优化

- 显存池化与复用：中间张量共享显存空间，避免频繁申请释放，大幅降低峰值显存占用
- 多流异步执行：重叠数据传输与计算过程，减少 GPU 空闲等待
- 动态内存规划：根据输入尺寸自动分配最优显存布局

## 二、大模型时代的 TensorRT-LLM

针对大语言模型的特殊结构，NVIDIA 推出了独立的 **TensorRT-LLM** 分支，专门优化 Transformer 推理，是目前工业级大模型服务的主流方案之一：

- 核心大模型优化：分页 KV 缓存（Paged KV Cache）、飞行批处理（In-flight Batching）、分块预填充（Chunked Prefill），大幅提升高并发场景的吞吐与显存利用率
- 全模型覆盖：原生支持 Llama、Qwen、DeepSeek、Gemma、Mixtral 等几乎所有主流开源大模型与 MoE 结构
- 高级生产特性：投机解码、动态 LoRA 加载、多卡张量并行/流水线并行、专家并行、OpenAI 兼容接口
- 性能表现：在 Blackwell B200 显卡上，70B 参数模型 FP4 量化后，单卡峰值吞吐可达上万 token/s

## 三、主流使用方式

### 1. 传统通用模型（CV/语音/小模型 NLP）

最经典的 ONNX 转换路径：

1. 将训练好的模型导出为 ONNX 格式
2. 使用 TensorRT 自带的 `trtexec` 命令行工具，把 ONNX 编译为专属优化引擎（`.engine` 文件）
3. 调用 TensorRT Runtime 的 Python/C++ API 加载引擎执行推理
   通用性最强，支持几乎所有主流训练框架产出的模型。

### 2. PyTorch 原生适配：Torch-TensorRT

无需手动导出 ONNX，直接对接 PyTorch 模型，一行代码开启 TensorRT 优化，兼容 `torch.compile` 生态，适配更灵活的动态计算图。

### 3. HuggingFace 生态一键加速：Optimum TensorRT

基于 HuggingFace Transformers 模型，通过 Optimum 库一键完成转换与推理，不用手动处理算子兼容、精度配置等细节，是快速落地的首选。

### 4. 大模型专属：TensorRT-LLM

提供完整的模型转换脚本、推理服务、Python/C++ API，专门面向 LLM 生产级部署，是目前 NVIDIA 平台大模型推理的性能标杆。

## 四、优势与局限性

### 优势

- **性能天花板**：同硬件下，通常比 PyTorch 原生推理快 2~10 倍，显存占用降低 30%~70%
- **生产级稳定**：NVIDIA 官方维护，广泛应用于自动驾驶、云服务、工业视觉等严苛场景
- **全硬件覆盖**：从数据中心 A100/H100/B200，到消费级 RTX 显卡，再到边缘 Jetson 设备全兼容

### 局限性

- **硬件强绑定**：仅支持 NVIDIA GPU，苹果 M 系列（MPS）、AMD 显卡、纯 CPU 都无法使用
- **构建成本高**：生成优化引擎需要几分钟到几十分钟，输入尺寸变化较大时需要重新构建或配置 profile
- **自定义算子门槛高**：模型包含冷门自定义算子时，需要手动开发 TensorRT 插件，开发成本较高
- **调试难度大**：优化后的计算图为黑盒，出现精度问题时排查成本远高于原生框架

## 五、常见部署方案选型对比

| 方案             | 核心适用场景             | 性能上限 | 硬件通用性            | 开发成本 |
| -------------- | ------------------ | ---- | ---------------- | ---- |
| PyTorch 原生     | 模型调试、小流量验证服务       | 低    | 中                | 最低   |
| ONNX Runtime   | 跨平台、多硬件通用部署        | 中    | 高                | 低    |
| TensorRT       | NVIDIA GPU 高性能生产部署 | 最高   | 低（仅 NVIDIA）      | 中高   |
| TensorRT-LLM   | NVIDIA 平台大模型生产部署   | 最高   | 极低（仅 LLM+NVIDIA） | 高    |
| llama.cpp/GGUF | 本地 CPU/苹果芯片跑大模型    | 中    | 中                | 低    |

简单总结：如果你的目标是在 NVIDIA GPU 上把模型跑到最快、用最低硬件成本扛最高并发，TensorRT 是首选；如果需要跨硬件兼容、快速验证，ONNX 体系更合适；而苹果芯片设备上，只能依赖 MPS 或 llama.cpp 这类方案。

需要我补充一份 ONNX 转 TensorRT 的实操步骤，或者大模型 TensorRT-LLM 的部署流程吗？





## wikipedia [TensorRT](https://en.wikipedia.org/wiki/TensorRT)


