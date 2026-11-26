# MLIR
- https://mlir.llvm.org/
- zhihu [MLIR中国社区](https://www.zhihu.com/people/mlir-70)


## Progressive lowering pipeline
常见 dialect 按抽象层次从高到低大致为：

```
TOSA / StableHLO / torch     （ML 图级别）
        ↓
linalg / tensor              （结构化张量计算）
        ↓
affine / scf / vector / memref（循环、向量、缓冲区）
        ↓
arith / func / cf / gpu
        ↓
llvm / spirv                 （目标相关）
```
TOSA=Tensor Operator Set Architecture

## MLIR 与 LLVM IR 的区别，以及为什么要引入 MLIR

- **LLVM IR**：LLVM 编译器的核心中间表示。它是**一种具体的 IR**，有固定的指令集和类型系统，抽象层次接近机器（"可移植的汇编"）。
- **MLIR（Multi-Level Intermediate Representation）**：由 Chris Lattner 等人 2018 年在 Google 发起，2019 年底并入 LLVM 项目。它**不是另一种 IR**，而是**用来构建 IR 的框架/基础设施**。在 **MLIR** 里，**LLVM IR** 本身也只是其中一个 dialect（`llvm` dialect）。

因此 MLIR 并没有取代 LLVM IR。典型流程是：在 MLIR 中逐级下降，最后转成 LLVM IR，再交给 LLVM 后端生成机器码。

### 主要区别

#### 1. 单层固定 vs. 多层可扩展（Dialect 机制）

| | LLVM IR | MLIR |
|---|---|---|
| 指令集 | 固定（add、load、store、br、call…） | 无固定指令集，由 **Dialect** 定义 Operation |
| 类型系统 | 固定（iN、float、ptr、vector、struct…） | 类型与属性均可自定义（tensor、memref、量化类型…） |
| 扩展方式 | intrinsic、metadata，或修改 LLVM 核心代码 | 新建 dialect 即可，无需改核心 |
| 抽象层次 | 只有一层，接近硬件 | 同一模块中可以混合多个层次的 dialect |


#### 2. 统一而通用的 Operation 结构

MLIR 中"一切皆 Operation"，包括函数和模块本身。每个 Op 统一由以下部分组成：

- 名称（`dialect.opname`）
- 操作数（operands）和结果（results）
- 属性（attributes，编译期常量信息）
- **区域（regions）**：可以嵌套其他 block
- 后继块（successors）
- 源码位置（location，强制携带）

因为结构统一，通用的 pass（如 CSE、DCE、规范化、内联）不需要理解具体 Op 的语义也能工作，Op 的特性通过 **Traits / Interfaces** 声明。

#### 3. Region：保留结构化信息

LLVM IR 只有"函数 → 基本块 → 指令"的扁平 CFG，循环在生成 IR 时就被拆成跳转，之后要靠 LoopInfo 等分析把它们重新识别出来。

MLIR 的 Region 支持嵌套，可以直接表达结构化控制流：

```mlir
// MLIR：循环结构显式保留
scf.for %i = %c0 to %n step %c1 {
  %v = memref.load %A[%i] : memref<?xf32>
  ...
}
```

```llvm
; LLVM IR：循环已变成基本块和跳转
loop:
  %i = phi i64 [0, %entry], [%i.next, %loop]
  ...
  br i1 %cond, label %loop, label %exit
```

`affine` dialect 还能直接表达仿射循环和访存，适合做多面体优化（tiling、fusion、interchange）。

#### 4. Block Argument 取代 Phi 节点

MLIR 用**基本块参数**代替 LLVM 的 `phi` 指令：

```mlir
^bb1(%x: i32):   // 前驱块跳转时传入值
  ...
  cf.br ^bb1(%y : i32)
```

这样写更规整，不需要 phi 必须位于块首之类的特殊规则，变换代码也更好写。

#### 5. 配套基础设施更完善

- **ODS（Operation Definition Specification）**：用 TableGen 声明式定义 Op，自动生成 C++ 类、校验器（verifier）、解析器和打印器（自定义汇编格式）。
- **Pattern Rewriting**：包括 DRR、PDL/PDLL 和贪心模式重写驱动。
- **Dialect Conversion 框架**：支持部分或全部 lowering、类型转换，以及合法性目标（ConversionTarget）。
- **Pass Manager**：Pass 可以锚定在任意 Op 上（如 `func.func`、`gpu.module`），天然支持多线程并行。
- **Location 追踪**：所有 Op 必须带位置信息，方便调试和报错溯源。
- **Symbol Table**、嵌套模块等机制，便于表达异构程序（如 host 端加 device 端代码）。

#### 6. 总结对比

| 维度 | LLVM IR | MLIR |
|---|---|---|
| 定位 | 一种具体 IR | 构建 IR 的框架 |
| 抽象层次 | 低层，单层 | 多层，可混合 |
| 可扩展性 | 弱 | 强（dialect） |
| 控制流 | 扁平 CFG | Region 嵌套加 CFG |
| SSA 合并 | phi 节点 | block 参数 |
| 主要领域 | CPU/GPU 通用代码生成 | ML、HPC、硬件设计、语言前端等 |
| 优化方式 | 下降到低层后再优化 | 在合适的抽象层做合适的优化，逐级下降 |

---

### 为什么需要 MLIR

### 1. 高层语义在下降过程中过早丢失

LLVM IR 太低层。张量形状、循环嵌套结构、并行性、数据布局、算子语义等信息，一旦降到 LLVM IR 就丢失或很难恢复。

例如，矩阵乘在 linalg 层是一个 `linalg.matmul`，做分块、融合、映射到硬件指令都很直接。但在 LLVM IR 层它只是三重循环里的 load/store/fmul，再想做这些优化就困难得多。

MLIR 的核心思想是**渐进式下降（Progressive Lowering）**：在每个抽象层做最适合该层的优化，再逐步往下走。

### 2. 各家重复造轮子，IR 严重碎片化

MLIR 出现之前，许多语言和框架都在 LLVM IR 之上自建了高层 IR：

- Swift 的 SIL、Rust 的 MIR、Julia IR、Flang 的 FIR
- TensorFlow 生态中的 Graph、XLA HLO、TF Lite、TPU IR 等

每个项目都要重新实现 IR 定义、解析与打印、校验、Pass 管理、模式重写、调试工具等。这些工作重复、质量参差，相互之间也无法复用。MLIR 提供了通用基础设施，让"定义一个新 IR"的成本大幅降低。

### 3. 异构硬件与领域专用加速器爆发

摩尔定律放缓之后，GPU、TPU、NPU、DSP、FPGA 等专用硬件大量涌现。LLVM IR 的设计以传统 CPU 为中心，难以表达：

- 张量和高维向量运算
- 多级存储层次、片上内存
- 主机与设备协同的异构程序

MLIR 可以针对新硬件定义专门的 dialect，并与已有 dialect 复用和组合。

### 4. 深度学习编译器的需求

TensorFlow、PyTorch 等框架需要把计算图编译到各种后端，过程涉及图优化、算子融合、循环优化、代码生成等多个层次。这正是 MLIR "多层 IR 加可组合 dialect"所擅长的场景，也是 MLIR 最初在 Google 诞生的直接动因。

### 5. 让编译器研究和工程更模块化

多面体优化、自动并行化、量化等技术可以作为独立的 dialect 或 pass 存在，被不同项目复用，不必绑定在某一个编译器里。

---

## 四、MLIR 的典型应用

- **AI 编译器**：IREE、OpenXLA（StableHLO）、Torch-MLIR、OpenAI Triton、ONNX-MLIR
- **编程语言**：Mojo、Flang（Fortran 前端）、ClangIR（为 C/C++ 引入高层 IR）
- **硬件设计**：CIRCT（用 MLIR 做电路设计和 HLS）
- **量子计算**：多个量子编译器项目基于 MLIR

---

## 一句话总结

LLVM IR 解决的是"如何把多种语言高效编译到多种 CPU"的问题，它是一种低层的通用 IR。MLIR 解决的是"如何低成本地构建多层次、可扩展、面向领域和异构硬件的编译器"的问题。它通过 Dialect、Region 和渐进式下降，在合适的抽象层保留并利用高层语义，最后再交给 LLVM IR 完成代码生成。