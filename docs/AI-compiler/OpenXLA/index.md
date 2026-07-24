# OpenXLA



官网: [OpenXLA](https://openxla.github.io/iree/)

[openxla](https://github.com/openxla)/**[stablehlo](https://github.com/openxla/stablehlo)** 

> We use MLIR bytecode as [serialization format](https://github.com/openxla/stablehlo/blob/main/docs/bytecode.md) and provide [backward and forward compatibility](https://github.com/openxla/stablehlo/blob/main/docs/compatibility.md) guarantees.  

[openxla](https://github.com/openxla)/**[iree](https://github.com/openxla/iree)** 

> IREE (**I**ntermediate **R**epresentation **E**xecution **E**nvironment, pronounced as "eerie") is an [MLIR](https://mlir.llvm.org/)-based end-to-end compiler and runtime that lowers Machine Learning (ML) models to a unified IR that scales up to meet the needs of the datacenter and down to satisfy the constraints and special considerations of mobile and edge deployments. 

[openxla](https://github.com/openxla)/**[xla](https://github.com/openxla/xla)** 

> XLA (Accelerated Linear Algebra) is an open-source machine learning (ML) compiler for GPUs, CPUs, and ML accelerators.



mlir 官网 [Multi-Level Intermediate Representation Overview](https://mlir.llvm.org/) 



## Posts

cloud.google [**Open source collaborations and key partnerships to help accelerate AI innovation**](https://cloud.google.com/blog/products/ai-machine-learning/googles-open-source-momentum-openxla-new-partnerships) 

ycombinator [OpenXLA Is Available Now | Hacker News](https://news.ycombinator.com/item?id=35078410)

opensource.googleblog [OpenXLA is available now to accelerate and simplify machine learning](https://opensource.googleblog.com/2023/03/openxla-is-ready-to-accelerate-and-simplify-ml-development.html)

> Today, we’re taking a significant step towards eliminating these barriers by making the [OpenXLA Project](https://github.com/openxla), including the [XLA](https://github.com/openxla/xla), [StableHLO](https://github.com/openxla/stablehlo), and [IREE](https://github.com/openxla/iree) repositories, available for use and contribution.

zhihu [如何看待OpenXLA这个开源项目？](https://www.zhihu.com/question/561079030) 



### 为解决机器学习碎片化问题，阿里、苹果、谷歌等 12 家巨头推出 OpenXLA

> NOTE: 
>
> 一、通过csdn公众号发现的OpenXLA

3 月 12 日消息，阿里巴巴、亚马逊 AWS、AMD、苹果、Arm、Cerebras、谷歌、Graphcore、Hugging Face、英特尔、Meta 和英伟达 12 家科技巨头宣布，联合推出 OpenXLA 项目（包括 XLA、StableHLO 和 IREE 存储库），使开发者能够编译和优化来自所有领先 ML 框架的模型，以便在各种硬件上进行高效培训和服务。这一通用的编译器可以将不同的硬件设备桥接到当今使用的多个框架（例如 TensorFlow、PyTorch），通过 OpenXLA 来帮助加速 AI 的开发和交付来实现 AI 的实际潜力。