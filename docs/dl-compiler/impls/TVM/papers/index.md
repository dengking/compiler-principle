# Apache TVM 相关论文梳理

## 说明

以下梳理 Apache TVM（深度学习编译器栈）发展过程中的核心学术论文。**请注意**：部分论文的发表年份、会议归属等细节我可能记忆有偏差，建议你在引用前通过 Google Scholar 或论文官方页面核实。我会在不确定处明确标注。

TVM 的核心目标是：**将深度学习模型从各种框架（TensorFlow、PyTorch 等）编译并优化到多样化的硬件后端（CPU、GPU、加速器）上高效执行**。围绕这一目标，论文大致可分为几个演进阶段。

---

## 1. 奠基之作：TVM 编译器栈

### 《TVM: An Automated End-to-End Optimizing Compiler for Deep Learning》

- **会议**：OSDI 2018
- **主要作者**：Tianqi Chen（陈天奇）等，华盛顿大学
- **核心贡献**：
  - 提出完整的**端到端深度学习编译栈**，打通"高层模型 → 中间表示 → 底层优化代码"的全流程。
  - 引入**张量表达式（Tensor Expression）**语言，将**计算（compute）**与**调度（schedule）**分离——这一思想借鉴自 **Halide**。
  - 支持跨平台代码生成：CPU、GPU、以及 FPGA/专用加速器。
  - 解决了将深度学习算子高效映射到多样硬件的核心难题。

**地位**：这是 TVM 的原始论文，奠定了整个项目的架构基础。

---

## 2. 自动调优：从手工调度到机器学习驱动

深度学习算子在不同硬件上的最优调度参数空间极其庞大，手工调优不现实。以下工作聚焦**自动化调度搜索**。

### 《Learning to Optimize Tensor Programs》（AutoTVM）

- **会议**：NeurIPS 2018
- **核心贡献**：
  - 提出 **AutoTVM**，用**机器学习模型**（统计代价模型）预测不同调度配置的性能，替代真实硬件上的昂贵测量。
  - 通过学习型代价模型引导搜索，大幅减少需要实际测量的配置数量。
  - 用户仍需提供**调度模板（schedule template）**，搜索在模板定义的参数空间内进行。

### 《Ansor: Generating High-Performance Tensor Programs for Deep Learning》

- **会议**：OSDI 2020
- **核心贡献**：
  - 提出 **Ansor（AutoScheduler）**，相比 AutoTVM 的重大进步在于**无需手工编写调度模板**。
  - 通过**分层搜索空间**自动生成候选程序，覆盖 AutoTVM 难以触及的优化组合。
  - 采用**演化搜索 + 学习型代价模型**，并引入任务调度器在多个子图间分配调优时间。
  - 在多种硬件上取得优于 AutoTVM 的性能。

**演进关系**：AutoTVM（模板驱动） → Ansor（自动生成，无模板）。

---

## 3. 高层中间表示：Relay

### 《Relay: A New IR for Machine Learning Frameworks》

- **会议 / 场合**：MAPL 2018（我对具体会议记忆不完全确定）
- 后续还有更完整的版本 **《Relay: A High-Level Compiler for Deep Learning》**（技术报告 / arXiv）
- **核心贡献**：
  - 提出 **Relay**，作为 TVM 的**高层函数式中间表示（IR）**，取代早期较为简单的图 IR（NNVM）。
  - 支持**控制流、递归、闭包**等高级语言特性，表达能力强于传统计算图。
  - 便于进行图级别优化（算子融合、常量折叠、布局变换等）。

**地位**：Relay 是 TVM 高层 IR 的核心，承接前端模型导入与后端算子编译。

---

## 4. 底层 IR 的现代化：TensorIR

### 《TensorIR: An Abstraction for Automatic Tensorized Program Optimization》

- **会议**：ASPLOS 2023
- **核心贡献**：
  - 提出 **TensorIR**，作为 TVM 新一代**底层张量程序 IR**。
  - 核心引入 **Block（块）** 抽象，用于表达和优化面向**张量化硬件指令**（如 GPU Tensor Core、TPU MMA）的计算。
  - 配合 **MetaSchedule**（新一代自动调度系统），支持对张量化指令的自动化优化。

**演进关系**：这代表 TVM 底层从原始张量表达式向更强大、更适配现代 AI 加速器的 IR 演进。

---

## 5. 运行时与动态性支持

### 《Nimble: Efficiently Compiling Dynamic Neural Networks for Model Inference》

- **会议 / 场合**：MLSys 2021（年份请核实）
- **核心贡献**：
  - 针对**动态形状（dynamic shape）**和**动态控制流**的模型（如 NLP 中变长序列）提供编译与运行时支持。
  - 弥补早期 TVM 主要面向静态形状的局限。

---

## 6. 演进脉络总结

```
                  TVM (OSDI 2018)
              端到端编译栈 + 计算/调度分离
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   高层 IR          自动调优          底层 IR
        │               │               │
    Relay          AutoTVM         Tensor Expr
  (MAPL 2018)    (NeurIPS 2018)         │
        │               │          TensorIR
        │            Ansor          (ASPLOS 2023)
        │          (OSDI 2020)           │
        │               │          MetaSchedule
        │          无需模板               │
        └───────────────┴───────────────┘
                        │
                  动态性支持
                Nimble (MLSys 2021)
```

---

## 7. 阅读建议

| 目标              | 推荐阅读顺序                                |
| --------------- | ------------------------------------- |
| **理解 TVM 整体架构** | 先读 TVM (OSDI 2018) 原始论文               |
| **理解自动调优演进**    | AutoTVM → Ansor，对比模板驱动 vs 自动生成        |
| **理解高层 IR 设计**  | Relay 论文                              |
| **理解最新底层优化**    | TensorIR (ASPLOS 2023) + MetaSchedule |
| **理解动态模型支持**    | Nimble                                |

---

## 免责与核实提示

- 上述论文的**发表年份、会议名称**部分依赖我的记忆，尤其是 Relay、Nimble 的具体发表场合，请务必核实。
- TVM 生态发展很快，可能还有我未涵盖的重要工作（如 **Lorien**、**Collage**、量化相关、以及新近的 **Relax / Unity** 方向）。
- 建议查阅 **TVM 官方网站（tvm.apache.org）的 Publications 页面** 和 **陈天奇（Tianqi Chen）的 Google Scholar 主页**获取权威、最新的论文列表。

如果你想让我针对**其中某一篇**（例如 TVM 原始论文或 Ansor）做**深入的技术精读与讲解**，请告诉我，我可以展开详述其技术细节、方法与创新点。😊

## TVM 核心学术论文
### 一、开山主论文（正式发表版）
**标题**：*TVM: An Automated End-to-End Optimizing Compiler for Deep Learning*
**发表会议**：第13届 USENIX Symposium on Operating Systems Design and Implementation（OSDI '18），2018年10月
**作者**：Tianqi Chen, Thierry Moreau, Ziheng Jiang, Lianmin Zheng, Eddie Yan 等（华盛顿大学、AWS、上海交大等机构）
**核心贡献**：
- 提出「计算图级优化 + 算子级调度优化」的两级编译架构
- 借鉴 Halide 的算法-调度分离思想，实现多硬件后端的性能可移植性
- 内置 AutoTVM 基于模板的自动调优机制
- 首次完整实现深度学习端到端编译栈，覆盖CPU、GPU、FPGA等多类硬件
**官方链接**：https://www.usenix.org/conference/osdi18/presentation/chen

> 更早的预印本版本（arXiv 2018.02）标题为 *TVM: End-to-End Optimization Stack for Deep Learning*，内容与正式发表版基本一致。

### 二、TVM 生态核心衍生论文
#### 1. Ansor：无模板自动调度
**标题**：*Ansor: Generating High-Performance Tensor Programs for Deep Learning*
**发表会议**：OSDI 2020
**核心定位**：AutoTVM 的升级方案，无需手写调度模板，通过分层搜索空间自动生成高性能张量程序，现已并入 TVM 主线。

#### 2. TensorIR：新一代底层张量IR
**标题**：*TensorIR: An Abstraction for Automatic Tensorized Program Optimization*
**发表会议**：ASPLOS 2023（第28届ACM架构支持编程语言和操作系统国际会议）
**核心定位**：替代原有的 TE（Tensor Expression）调度体系，支持张量原语、自动调度、跨硬件统一抽象，是 TVM 现阶段的核心底层IR。

#### 3. Relax：动态形状高阶IR
**标题**：*Relax: Composable Abstractions for End-to-End Dynamic Machine Learning*
**发表**：arXiv 2023
**核心定位**：针对大语言模型等动态形状工作负载设计的新一代高层IR，统一计算图、循环级程序与外部库调用，支持全局符号形状推导，是 TVM 面向LLM时代的核心演进。

#### 4. Relay：函数式计算图IR
TVM 经典高阶中间表示 Relay，设计体系在主论文中已有阐述，配套的Pass基础设施、类型系统是 TVM 图级优化的核心基础。

需要我补充其中某篇论文的**BibTeX引用格式**吗？
