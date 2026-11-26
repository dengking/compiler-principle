# Codegen

代码生成是后端优化流程的最后一步：根据硬件，将优化后的低级 IR 转化为机器指令执行。


Graph IR → Tensor IR → (算子优化后的更低级 IR) → 【Codegen】→ SPIR-V / LLVM IR / PTX → GPU 驱动 / 后端编译器 → 机器指令


## 常见做法

现阶段最广泛的做法是借助成熟的编译工具来实现：把低级 IR 转化成 LLVM、NVCC 等编译工具的输入形式，再调用其生成机器指令。

代码生成不是 AI 编译器的核心内容。

## 目标 IR

Codegen 的输出通常不是直接的机器码，而是某个成熟后端能接收的**目标 IR**，再由对应的后端编译器 / 驱动生成最终机器指令。

| 目标 IR | 面向硬件 / API | 后续编译者 |
| --- | --- | --- |
| LLVM IR | CPU、AMDGPU 等 | LLVM 后端 |
| PTX | NVIDIA GPU | NVCC / 驱动 JIT（`ptxas`） |
| SPIR-V | Vulkan、OpenCL 的 GPU / 加速器 | GPU 驱动 JIT |

### SPIR-V

SPIR-V 是 Khronos 定义的二进制中间语言，用于 Vulkan、OpenCL 的 shader 和 compute kernel。

- **层级**：属于 Codegen 的目标 IR，与 LLVM IR、PTX 同级。
- **形式**：SSA 形式的低层 IR，已接近硬件，不再保留循环嵌套、tiling、张量化等张量语义。
- **与 Tensor IR 的区别**：[Tensor IR](docs/AI-compiler/pipeline/tensor-IR/index.md) 是 AI 编译器自己的低层 IR，用于表达循环与张量计算并做算子优化；SPIR-V 是优化完成后的输出产物。
- **可移植性**：SPIR-V 是可移植的中间产物，最终由各厂商 GPU 驱动 JIT 编译为具体机器码。
- **典型使用**：TVM 的 Vulkan / SPIR-V codegen、MLIR 的 SPIR-V dialect、IREE 的 GPU 后端。

## 在后端优化流程中的位置

1. 生成低级 IR：见 [Tensor IR](docs/AI-compiler/pipeline/tensor-IR/index.md)。
2. 后端优化：见 [Operator Optimizer](docs/AI-compiler/pipeline/operator-optimizer/index.md)。
3. 代码生成：本章。

## 子章节

- [Instruction-Optimization](docs/AI-compiler/pipeline/codegen/Instruction-Optimization/index.md)：指令优化（硬件原语映射、指令调度与流水线、多 SM 负载均衡）
