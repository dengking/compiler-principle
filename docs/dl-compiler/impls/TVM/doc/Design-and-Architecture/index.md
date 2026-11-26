# [Design and Architecture](https://tvm.apache.org/docs/arch/index.html)

> NOTE: 这篇文字的问题:
> 
> 1. **tirx::PrimFunc**、TensorIR、TIR 混用

This guide provides a few complementary views of the architecture. First, we review a single **end-to-end compilation flow** and discuss the key data structures and the transformations. This runtime-based view focuses on the interactions of each components when running the compiler. Then we will review the logical modules of the codebase and their relationship. This part provides a static overarching view of the design.

翻译: 本指南从多个互补视角介绍整体架构。首先，我们梳理一条完整的端到端编译流程，讲解核心数据结构与程序变换操作。该基于运行时的视角，着重剖析编译器运行时各个组件之间的交互关系。随后介绍代码库内的各个逻辑模块以及模块间的关联；此板块提供一份静态、宏观的架构设计概述。

## Overall Flow

In this guide, we will study an example **compilation flow** in the compiler. The figure below shows the flow. At a high-level, it contains several steps:

- **Model Creation**: Create the IRModule to be optimized and compiled, which contains a collection of functions that internally represent the model. Users can manually construct IRModule via `NNModule`, **TVMScript**, or import a **pre-trained model** from **Relax frontend**.

- **Transformation**: The compiler transforms an IRModule to another functionally equivalent or approximately equivalent(e.g. in the case of **quantization(量化)**) IRModule. Many of the transformations are **target (backend) independent**. We also allow target to affect the configuration of the transformation pipeline.

- **Target Translation**: The compiler translates(**codegen**) the IRModule to an executable format specified by the target. The target translation result is encapsulated as a **runtime.Module** that can be exported, loaded, and executed on the **target runtime environment**.

- **Runtime Execution**: the user loads back a **runtime.Module** and runs the compiled functions in the supported runtime environment.
  
  - 翻译: 用户加载回运行时模块，并在兼容的运行环境当中执行已经编译完成的函数

### Key data structures

One of the best ways to design and understand a complex system is to identify the **key data structures** and APIs that manipulate (transform) these **data structures**. Once we identified the **key data structures**, we can then breakdown a system into logical components that either define a collection of key data structures or transformations among the data structures.

**IRModule** is the primary data structure used across the entire stack. An IRModule (intermediate representation module) contains a collection of **functions**. Currently, we support two primary variants of functions.

- **relax::Function** is a high-level functional program representation. A **relax.Function** represents high-level graph structure, usually corresponds to an end-to-end model or a sub-graph of the overall model. You can view a **relax.Function** as a computational graph with additional support for control-flow, and complex data structures.

- **tirx::PrimFunc** is a low-level program representation that contains elements including loop-nest choices, multi-dimensional load/store, threading, and vector/tensor instructions. It is usually used to represent an **operator program** that executes a (possibly-fused(融合) layer in a model.

During the **compilation** and **transformation**, all **relax operators** are lowered to `tirx::PrimFunc` or `TVM PackedFunc`, which can be executed directly on the target device, while the calls to **relax operators** are lowered to calls to low-level functions (e.g. `R.call_tir` or `R.call_dps_packed`).

翻译: 在编译变换过程中，所有 Relax 算子都会被降级为可在目标设备上直接执行的 `tirx::PrimFunc` 或 TVM PackedFunc；而对 Relax 算子的调用指令，则会被降级为对底层函数的调用（例如 `R.call_tir` 或 `R.call_dps_packed`）。



### Transformations

Now that we have covered the **key data structures**, let us talk about the transformations. Each transformation could serve one of the following purposes:

- optimization: transform a program to an equivalent, possibly more optimized version.

- lowering: transform a program to a lower-level representation that is closer to the target.

#### relax transformations

relax transformations contain a collection of passes that apply to relax functions. The optimizations include common graph-level optimizations such as constant folding and dead-code elimination for operators, and backend-specific optimizations such as library dispatch.

#### TensorIR transformations

- **TensorIR schedule**: **TensorIR schedules** are designed to optimize the **TensorIR functions** for a specific target, with user-guided instructions and control how the target code is generated. For CPU targets, a **TensorIR PrimFunc** can generate valid code and execute on the target device without schedule but with very-low performance. However, for GPU targets, the schedule is essential for generating valid code with thread bindings. For more details, please refer to the [TensorIR Transformation](https://tvm.apache.org/docs/deep_dive/tensor_ir/tutorials/tir_transformation.html#tirx-transform) section. Additionally, we provides `MetaSchedule` to automate the search of **TensorIR schedule**.
  
  - 翻译: **TensorIR 调度**：TensorIR 调度用于针对特定目标硬件优化 TensorIR 函数，通过用户引导指令控制目标代码的生成逻辑。
    
    对于 CPU 目标平台，即使不做任何调度，TensorIR PrimFunc 也能生成可运行的合法代码并在目标设备上执行，但性能极差。而对于 GPU 目标平台，调度是生成带线程绑定的合法代码的必要前提。更多细节可参考「TensorIR 变换」章节。此外，TVM 还提供了元调度（MetaSchedule）能力，可自动化搜索最优的 TensorIR 调度方案。

- **Lowering Passes**: These passes usually perform after the schedule is applied, transforming a TensorIR PrimFunc into another functionally equivalent PrimFunc, but closer to the target-specific representation. For example, there are passes to flatten multi-dimensional access to one-dimensional pointer access, to expand the intrinsics into target-specific ones, and to decorate the function entry to meet the runtime calling convention.
  
  - 翻译: **降级 Pass**：这类 Pass 通常在调度执行后运行，将 TensorIR 原语函数转换为**功能等价**、但更贴近目标硬件专属表示的原语函数。例如部分 Pass 负责将多维内存访问展平为一维指针访问，部分将通用内置原语展开为目标硬件专属原语，还有的会修饰函数入口，使其符合运行时调用约定。

Many **low-level optimizations** can be handled in the target phase by the LLVM, CUDA C, and other target compilers. As a result, we leave **low-level optimizations** such as **register allocation** to the downstream compilers and only focus on optimizations that are not covered by them.

翻译: 大量底层优化可在目标代码生成阶段交由 LLVM、CUDA C 及其他目标后端编译器完成。因此，我们将寄存器分配这类底层优化交由下游编译器处理，仅聚焦于这些编译器无法覆盖的优化工作。

#### cross-level transformations

Apache TVM enables **cross-level optimization** of end-to-end models. As the **IRModule** includes both Relax and TensorIR functions, the **cross-level transformations** are designed to mutate the IRModule by applying different transformations to these two types of functions.

翻译: Apache TVM 可实现端到端模型的跨层级优化。由于 IRModule 同时包含 Relax 与 TensorIR 两类函数，跨层级变换的作用机制是对这两类函数分别执行不同的变换逻辑，以此完成对 IRModule 的整体改写。

For example, `relax.LegalizeOps` pass mutates the IRModule by lowering relax operators, adding corresponding TensorIR PrimFunc into the IRModule, and replacing the relax operators with calls to the lowered TensorIR PrimFunc. Another example is the operator fusion pipeline (`relax.FuseOps` + `relax.FuseTIR`), which fuses multiple consecutive tensor operations into a single kernel. See [Operator Fusion](https://tvm.apache.org/docs/arch/fusion.html#fusion-arch) for a detailed explanation of the fusion algorithm, operator pattern classification, and pattern-based fusion for external backends.



### Target Translation

The target translation phase transforms an IRModule to the corresponding target executable format. For backends such as x86 and ARM, we use the **LLVM IRBuilder** to build in-memory **LLVM IR**. We can also generate source-level languages such as CUDA C and OpenCL. Finally, we support direct translations of a **Relax function** (sub-graph) to specific targets via external code generators. See [Code Generation](https://tvm.apache.org/docs/arch/codegen.html#codegen-arch) for how **TIR functions** are compiled to native code through the LLVM and Source codegen families. See [External Library Dispatch (BYOC)](https://tvm.apache.org/docs/arch/external_library_dispatch.html#external-library-dispatch) for the full BYOC (Bring Your Own Codegen) pipeline that offloads operator subgraphs to vendor libraries like cuBLAS, CUTLASS, and cuDNN. It is important that the final code generation phase is as lightweight as possible. Vast majority of transformations and lowering should be performed before the target translation phase.

翻译: **目标翻译阶段**会将 IRModule 转换为对应目标平台的可执行格式。针对 x86、ARM 等后端，我们通过 LLVM IRBuilder 在内存中构建 LLVM 中间表示；也可以生成 CUDA C、OpenCL 这类源码级语言代码。此外，TVM 还支持通过外部代码生成器，将 Relax 函数（计算子图）直接翻译为特定目标平台的代码。

关于 TIR 函数如何通过 LLVM 代码生成与源码代码生成两大体系编译为原生机器码，可参见「代码生成」章节。关于将算子子图卸载到 cuBLAS、CUTLASS、cuDNN 等厂商加速库的完整 BYOC（自带代码生成）流水线，可参见「外部库调度（BYOC）」章节。

核心原则是：最终的代码生成阶段应尽可能轻量化，绝大多数的 IR 变换与降级工作都应在目标翻译阶段之前完成。

- [Code Generation](https://tvm.apache.org/docs/arch/codegen.html)
- [External Library Dispatch (BYOC)](https://tvm.apache.org/docs/arch/external_library_dispatch.html)

We also provide a Target structure to specify the compilation target. The **transformations** before the target translation phase can also be affected by the target — for example, a target’s vector length would change the **vectorization** behavior.



### Runtime Execution
