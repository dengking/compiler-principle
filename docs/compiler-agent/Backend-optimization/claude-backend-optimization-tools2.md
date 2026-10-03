# 如果想要练习编译器后端优化，有哪些工具或开源项目可以使用

下面按「由浅入深」的路线整理，后端优化（IR 优化 + 指令选择/调度/寄存器分配 + 目标码生成）可用的工具和项目。

## 一、入门：小而全，能读完全部代码

| 项目                           | 语言                      | 适合练什么                                                                                |
| ---------------------------- | ----------------------- | ------------------------------------------------------------------------------------ |
| **Bril** (Cornell CS6120)    | Python/TS/Rust 均可写 pass | 最推荐的入门：JSON 格式 IR，自己写 DCE/LVN/SSA 构造/支配树/数据流框架/LICM                                  |
| **QBE**                      | C，约 1 万行                | 完整的后端：SSA、RA（线性扫描+合并）、ABI、x64/arm64/riscv 代码生成                                       |
| **chibicc / 8cc / tcc**      | C                       | 从零理解"IR → 汇编"，适合先把 pipeline 跑通                                                       |
| **Cranelift** (Wasmtime 的后端) | Rust                    | 现代设计：e-graph 优化（ISLE/alias analysis）、regalloc2、VCode；文档好，issue 里有大量 good-first-issue |
| **LCC / Nanopass framework** | C / Scheme              | 教科书式的指令选择（树覆盖）、pass 拆分思想                                                             |

练手清单（在 Bril 或 QBE 上做一遍）：

1. 构造 CFG、支配树、支配边界 → SSA 构造（Cytron 算法）与析构
2. 数据流分析框架 → 活跃变量、可用表达式、常量传播（SCCP）
3. LVN/GVN、DCE、CSE、复写传播、强度削弱
4. 循环识别 → LICM、归纳变量分析、展开、unswitching
5. 线性扫描 / 图着色寄存器分配 + spill 代价模型
6. 窥孔优化、指令调度（list scheduling）

## 二、工业级：LLVM / GCC / MLIR

**LLVM** 是性价比最高的选择，社区活跃、文档全。

- **IR 层**：`llvm/lib/Transforms/` 写自己的 Pass（新 PassManager），用 `opt -passes=...` 调试
- **后端层**（真正的"后端"）：
  - 指令选择：SelectionDAG、**GlobalISel**（当前热点，很多架构在迁移）、TableGen 模式
  - MachineIR 优化、`MachineScheduler`、`RegAllocGreedy`、PEI/Prologue、`MachineCombiner`
  - 加一个自定义 target 或给 RISC-V backend 补 pattern 是很好的练手方式
- 实用工具链：
  
  ```bash
  opt -passes='loop-unroll' -S -print-after-all a.ll
  llc -march=riscv64 -debug-only=isel a.ll
  llvm-mca -mcpu=skylake a.s        # 静态流水线性能分析
  llvm-reduce / bugpoint            # 自动缩小复现用例
  ```
- 入门资料：`llvm/docs/WritingAnLLVMPass`、*LLVM Cookbook*、**Chapter 之外**：`llvm-tutor`（banach-space/llvm-tutor，一堆独立 pass 示例，强烈推荐）

**MLIR**：如果想做 AI/DSL 编译器，练 dialect 设计、pattern rewrite、bufferization、affine/linalg 变换、lowering 到 LLVM。

**GCC**：GIMPLE/RTL 两层 IR，plugin 机制可以写外部 pass（`-fplugin=`）。学习曲线陡，但 RTL 层的 combine/reload 是另一套思路，值得对比。

## 三、JIT / 运行时后端

- **V8**：Sparkplug（baseline）→ Maglev → TurboFan（Sea-of-Nodes）
- **JavaScriptCore B3/Air**：B3 是很干净的 SSA 后端，论文/文档质量高
- **HotSpot C1/C2**、**GraalVM Graal 编译器**（Java 写的，可读性好，适合看 partial escape analysis、推测优化）
- **LuaJIT**：trace JIT + 极致的 IR 设计（lj_ir / 折叠引擎），代码精炼
- **Wasmtime/Cranelift、WAMR** 的 wasm 后端

## 四、循环/张量/多面体优化

- **Halide**：schedule 与算法分离，练 tiling/fusion/vectorize 的直觉
- **TVM / TensorIR**、**Triton**、**XLA**、**IREE**：AI 编译器后端（tiling、layout、auto-tuning、codegen 到 GPU）
- **Polly / isl / PLUTO / Tiramisu**：多面体模型，循环变换的数学化处理
- **PolyBench / TSVC**：循环优化专用 benchmark，验证向量化效果

## 五、验证、搜索与"自动找优化机会"

这类工具很适合做研究型练习：

- **Alive2**：用 SMT 验证 LLVM IR 变换的正确性（找 miscompile bug）
- **Souper**：超优化器，自动从程序里挖掘可简化的表达式，常直接产出 LLVM patch
- **STOKE**：随机搜索做 x86 超优化
- **Csmith / YARPGen / EMI**：随机程序生成做 differential testing，找编译器 bug
- **C-Reduce**：用例最小化
- **CompilerGym**：把编译器优化包装成 RL 环境（pass ordering、phase ordering 研究）

## 六、测量与建模（优化必须闭环）

- **Compiler Explorer**（godbolt）：最快看到 codegen 差异，支持本地部署
- **llvm-mca / uiCA / OSACA / IACA**：指令级吞吐与端口压力分析
- **perf / VTune / nanoBench / Google Benchmark**
- **gem5**：周期级模拟，做调度/预取相关实验
- Benchmark：**LLVM test-suite**、SPEC CPU、Embench-IoT、CoreMark、Phoronix Test Suite

## 七、带评测的"比赛式"练习

- **全国大学生计算机系统能力大赛 — 编译系统设计赛**（SysY 语言 → ARM/RISC-V，有公开测试集和历年优秀作品，是中文圈最好的后端优化实战项目）
- **Cornell CS6120**（Adrian Sampson，公开课+Bril+作业，强烈推荐）
- **CMU 15-411 / Stanford CS243 / Rice COMP512** 公开材料
- 给 LLVM / Cranelift / Wasmtime 提 PR（从 `good first issue`、missed-optimization 标签入手）

## 八、必读书与资料

- *Engineering a Compiler*（Cooper & Torczon）— 后端部分最实用
- **SSA-based Compiler Design**（免费 PDF，SSA 相关的权威汇编）
- *Optimizing Compilers for Modern Architectures*（Allen & Kennedy）— 循环变换
- *Advanced Compiler Design and Implementation*（Muchnick）— 当字典用
- Agner Fog 的优化手册 + Intel/ARM 优化指南（理解"为什么这样 codegen 更快"）
- LLVM 社区：`llvm-dev` 邮件列表、LLVM Weekly、每年的 LLVM Dev Meeting 视频

## 建议路径

1. **2–4 周**：Bril 上实现 SSA + 数据流 + 若干经典 pass，建立基本功
2. **1–2 月**：读完 QBE 或 Cranelift 一个后端，自己为 RISC-V 写一个简易 codegen + 线性扫描 RA
3. **之后**：进入 LLVM，先写 IR pass（配 llvm-tutor），再进 MachineIR / GlobalISel；同时用 llvm-mca + perf 做量化验证
4. **进阶方向**：选一个——传统 CPU 后端（调度/RA/向量化）、JIT（推测优化、去优化）、AI 编译器（MLIR/TVM/Triton）、形式验证（Alive2 系）

需要的话我可以针对你的目标方向（比如"想做 RISC-V 后端"或"想做 AI 编译器"）给一份更细的两三个月学习计划。