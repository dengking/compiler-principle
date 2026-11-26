AI编译器领域迭代极快，专门的系统专著不多，核心知识分散在编译原理、GPU高性能计算、AI系统三大领域。下面按「打底→核心→专项→进阶补充」整理权威书单]。

## 基础打底：编译原理核心（必补根基）

AI编译器是领域专用编译器的分支，所有优化技术都根植于经典编译原理，优先建立完整知识框架。

1. **《编译原理》（龙书）Compilers: Principles, Techniques, and Tools** 编译领域圣经，系统讲解词法/语法分析、中间表示、数据流分析、指令调度、寄存器分配等核心概念。AI编译器中的图优化、算子调度、内存分配，本质都是经典编译技术在深度学习领域的延伸。
2. **《Engineering a Compiler》（工程编译器）** 比龙书更偏向现代编译器工程实现，对中间表示设计、代码生成、优化流水线的讲解更贴合工业界实践，适合想动手做编译器开发的读者。

## 核心对口：AI编译器专属专著

1. **《Deep Learning Systems: Algorithms, Compilers, and Processors for Large-Scale AI》** 目前AI系统与编译器领域最权威的英文专著，全链路覆盖计算图优化、算子分块调度、内存层次优化、Tensor Core硬件映射、自动调优等核心技术，同时串联GPU硬件架构与大模型算力需求，和你关注的SM、Blackwell/Rubin架构适配度极高。
2. **《深度学习编译器入门与实战：基于TVM框架》** 国内少有的实战向AI编译器书籍，以TVM为载体，从计算图IR、算子融合、循环分块到AutoTVM自动调优，配套完整代码案例，适合从零上手实操。
3. **《机器学习系统：设计与实现》** 对应CMU经典课程15-442，其中编译优化是核心章节，深度对比了XLA、TVM、TensorRT等主流框架的设计思路，兼顾训练与推理场景。

## 后端根基：GPU高性能计算（读懂底层优化）

AI编译器的最终性能取决于对GPU硬件的利用效率，不懂GPU架构就做不好深度优化。

1. **《大规模并行处理器编程实战》（Programming Massively Parallel Processors）** CUDA领域“红宝书”，讲透SIMT架构、SM执行模型、内存层次、分块复用、流水线延迟隐藏等底层逻辑，是理解算子级优化、FlashAttention显存优化的必备基础。
2. **《CUDA C编程权威指南》** 国内更易读的CUDA进阶教材，配套大量可运行的内核案例，能帮你直观理解AI编译器最终生成的GPU指令形态。

## 前沿专项：大模型编译与推理优化

传统AI编译器书籍对Transformer、MoE、长上下文等新场景覆盖有限，优先看这两本贴合当前工业界的新作：

1. **《大模型系统：原理与工程实践》** 国内最新的大模型系统专著，专门章节讲解大模型专属编译优化，包括FlashAttention融合、PagedAttention内存调度、KV缓存压缩、MoE路由与通信流水化等你之前关注的技术点。
2. **《Large Language Models: Foundations, Systems, and Applications》** 英文权威著作，系统梳理大模型推理系统的编译优化、显存管理、并发调度，对长上下文、Agent推理等场景的编译优化有深度拆解。

## 进阶补充：最新技术必读（书籍天然滞后）

AI编译器迭代速度远超出版周期，FlashAttention、FP8量化、MoE稀疏编译等前沿技术均以论文和开源文档形式发布，是进阶必看：

- 核心论文：TVM原理论文、FlashAttention系列论文、MLIR架构论文、PagedAttention论文
- 官方文档：TVM官方文档、MLIR官方文档、TensorRT-LLM开发者指南、Triton官方教程
- 开源课程：CMU 15-442 机器学习系统、Stanford CS231n 系统模块

## 阅读路径建议

- 入门：编译原理基础 → TVM实战书 → CUDA红宝书
- 进阶：《Deep Learning Systems》 → 大模型系统专项 → 啃论文+读源码

