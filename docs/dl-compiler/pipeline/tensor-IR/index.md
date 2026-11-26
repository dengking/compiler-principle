# Tensor IR

Tensor IR 是 AI 编译器中的**低级 IR**，是后端优化的输入。后端优化的第一步即“生成低级 IR”：将高级或计算图级别 IR（Graph IR）转换为低级 IR（Tensor IR）。

## 生成方式

- 不同 AI 编译器内部低级 IR 的形式和定义不同，但对于同一算子，算法的原理实质相同。
- 对于每个具体的算子，需要用 AI 编译器底层的接口来定义算法，再由编译器生成内部的低级 IR。

![生成低级 IR](https://developer.qcloudimg.com/http-save/11307734/44ddb7597a76a7be032676189b6536c4.png)

## 为什么不直接复用传统编译器

传统编译器（如 GCC、LLVM）也有后端优化部分，但 AI 编译器的后端优化不直接委托给它们，主要有两个原因：

1. **数据形式不同**：深度学习中数据形式主要为张量（Tensor），而传统编译器不擅长对张量计算优化，更擅长标量计算。
2. **缺乏必要的支持**：传统编译器主要针对通用编程语言，缺乏对领域特定语言（DSL）的支持，特别是对神经网络及相关的特殊优化。

## 后续阶段

Tensor IR 送入 [Operator Optimizer](docs/AI-compiler/pipeline/operator-optimizer/index.md) 进行算子级优化，并被转换为更低级的 IR，最终进入 [Codegen](docs/AI-compiler/pipeline/codegen/index.md)。
