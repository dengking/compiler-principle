# Graph IR

AI 编译器最顶层是各种 AI 训练框架编写的神经网络模型，一般由 Python 编写，常见框架有 PyTorch、MindSpore、PaddlePaddle 等。

- StableHLO: Google 主导的 OpenXLA 项目，基于 MLIR 编译器基础设施构建
- Torch: Meta 开发的主流深度学习建模与训练框架，以动态图（Eager 模式）为核心，是 AI 应用的**前端输入源**
- TOSA: Tensor Operator Set Architecture
## 从框架模型到 Graph IR

导入 AI 编译器时，需要用对应框架的 `converter` 功能，将模型转换为 AI 编译器统一的 **Graph IR**（计算图级别 IR）。

- 输入：各框架编写的网络模型。
- 转换：由各框架对应的 `converter` 完成。
- 输出：统一的 Graph IR，供 [Graph Optimizer](docs/AI-compiler/pipeline/graph-optimizer/index.md) 在计算图级别进行优化。

## 在流水线中的位置

```text
框架模型 ──converter──► Graph IR ──► Graph Optimizer ──► Tensor IR
```

Graph IR 关注计算图整体的拓扑结构，不关心算子的具体实现；算子的内部实现由后续的 [Tensor IR](docs/AI-compiler/pipeline/tensor-IR/index.md) 描述。
