# 练习编译器后端优化：工具与项目

## 零、先给结论

你的情况很具体：**已经有一个能跑的通用 `lfp` 求解器，缺的是真实 IR 和真实 benchmark**。所以优先级不是"学一个大系统"，而是**尽快把你的求解器接到真 IR 上，看它在真实代码上的表现**。

| 阶段        | 用什么                              | 为什么                                     |
| --------- | -------------------------------- | --------------------------------------- |
| **立刻**    | **Bril**（Cornell CS 6120）        | JSON 格式的 SSA IR，Python 几行读进来，你的求解器今天就能跑 |
| **两周后**   | **LLVM out-of-tree pass**        | 真实 IR、真实 benchmark、工业级验证基础设施            |
| **按兴趣分叉** | Cranelift / Crab / Soufflé / isl | 分别对应寄存器分配、抽象解释、Datalog、多面体              |

---

## 一、⭐ 最推荐的起点：Bril

**Bril**（Big Red Intermediate Language）是 Adrian Sampson 为 Cornell CS 6120 *Advanced Compilers* 设计的教学 IR。

| 特点            | 说明                                              |
| ------------- | ----------------------------------------------- |
| **IR 是 JSON** | `json.load()` 就拿到了 CFG，无需学 API                  |
| 极小的指令集        | 整数、布尔、`br`/`jmp`、`call`、SSA 扩展（`phi`）           |
| 工具链齐全         | `bril2json`/`bril2txt`、参考解释器 `brili`、Turnt 测试框架 |
| 多语言 SDK       | Python (`briltxt`)、TypeScript、Rust              |
| **课程完全公开**    | 讲义、视频、作业、往届学生的实现报告全部在线，可自学                      |

**为什么对你特别合适**：CS 6120 的作业序列几乎就是你笔记的顺序——local DCE → 数据流框架 → 支配树 → SSA 构造/销毁 → LVN/GVN → 循环不变量外提 → 别名分析。**你的 `solve()` 可以直接当第 2 个作业的答案**，然后一路往上搭。

```bash
git clone https://github.com/sampsyo/bril
# 作业列表与讲义：https://www.cs.cornell.edu/courses/cs6120/2023fa/
```

第一个练习建议：把 Bril 的函数转成 `succ: Dict[str, List[str]]`，喂给你的 `reverse_postorder` 和 `solve`，跑活跃变量 + DCE，用 Turnt 验证输出程序行为不变。

> ⚠️ Bril 的局限要清楚：**没有真实机器后端**，所以寄存器分配、指令调度、指令选择这三块练不了。那部分必须去 LLVM 或 Cranelift。

---

## 二、工业级：LLVM

### 入门方式：out-of-tree pass

不要 fork LLVM，用**独立项目 + `opt -load-pass-plugin`**：

```bash
# 骨架模板（社区维护，CMake 配好）
git clone https://github.com/banach-space/llvm-tutor
```

`llvm-tutor` 是目前最好的 out-of-tree pass 教程集，每个 pass 都有配套讲解和 lit 测试。

### 该读哪些目录

| 路径                                         | 内容                   | 对应你的知识点                                           |
| ------------------------------------------ | -------------------- | ------------------------------------------------- |
| `llvm/lib/Analysis/SparsePropagation.h`    | 稀疏数据流框架              | 你的 `solve_forward`（push 式）                        |
| `llvm/lib/Transforms/Scalar/SCCP.cpp`      | ⭐ Wegman–Zadeck SCCP | 常量传播 + 不可达边，`Product(Env(Flat), Powerset(edges))` |
| `llvm/lib/Transforms/Scalar/NewGVN.cpp`    | 值编号                  | Cooper–Simpson 那条线                                |
| `llvm/lib/Analysis/DependenceAnalysis.cpp` | ⭐ 依赖测试               | **Goff–Kennedy–Tseng 的分级 ZIV/SIV/MIV 实现**         |
| `llvm/lib/CodeGen/RegAllocGreedy.cpp`      | 寄存器分配                | 不是图着色，是优先级 + split                                |
| `llvm/lib/Target/*/\*ISelLowering.cpp`     | 指令选择                 | SelectionDAG / GlobalISel                         |
| `llvm/lib/Analysis/ScalarEvolution.cpp`    | SCEV                 | 归纳变量的符号表示，循环优化的前提                                 |

⭐ **`DependenceAnalysis.cpp` 值得专门读**：它是 Rice 学派那套分级依赖测试的工业实现，你能在代码里直接看到 `testZIV` / `testSIV` / `testMIV` / `gcdMIVtest` / `banerjeeMIVtest` 的函数名。

### 必备的辅助工具

| 工具                                          | 用途                  |
| ------------------------------------------- | ------------------- |
| `opt -passes=... -print-after-all`          | 看每个 pass 改了什么       |
| `opt -debug-only=<pass-name>`               | pass 内部的决策日志        |
| **`llvm-mca`**                              | 静态估算一段汇编的吞吐/延迟/端口压力 |
| **Compiler Explorer**（godbolt.org）          | 改一行看汇编变化，支持本地部署     |
| **`llvm-reduce` / `cvise`**                 | 把触发 bug 的大文件自动缩到十几行 |
| `-fsave-optimization-record` + `opt-viewer` | 看编译器在哪里**没有**优化、为什么 |

最后那个常被忽略但极有用：**优化失败的原因日志**比成功日志信息量大得多。

### ⭐ Alive2：验证你的变换是否正确

```
https://alive2.llvm.org/ce/
```

你写一个 peephole 变换，Alive2 用 SMT 自动检查它在所有输入（含 `undef`/`poison`）下是否等价，不等价就给反例。**它在 LLVM 里真实发现了几百个 bug**。

**练这个会彻底改变你对"优化正确性"的理解**——你会发现自己想当然的变换，有一半在 `poison` 语义下是错的。

---

## 三、按子领域挑项目

### 寄存器分配 / 指令选择 → **Cranelift**

|                 |                                                                                           |
| --------------- | ----------------------------------------------------------------------------------------- |
| 位置              | Bytecode Alliance / Wasmtime，Rust                                                         |
| 规模              | 比 LLVM 小一到两个数量级，可通读                                                                       |
| **`regalloc2`** | ⭐ 独立 crate 的回溯式寄存器分配器（Chris Fallin），**接口干净、有 fuzzer、文档写了设计决策**。想动手改寄存器分配，这是比 LLVM 友好得多的入口 |
| **ISLE**        | 用 DSL 写指令选择规则（term rewriting），还有形式化验证的配套研究                                                |

> **这是我对"想练寄存器分配"的首选推荐**。LLVM 的 `RegAllocGreedy` 耦合太深，`regalloc2` 可以单独 benchmark、单独 fuzz。

### 小而完整的后端（适合通读）

| 项目                                    | 语言  | 规模     | 特点                                                             |
| ------------------------------------- | --- | ------ | -------------------------------------------------------------- |
| **QBE**                               | C   | ~10k 行 | SSA、x64/arm64 后端、代码极简洁。**一周能读完全部**                             |
| **libFirm**                           | C   | 中等     | 图结构 SSA（Firm IR），KIT 出品，配 `cparser` 前端                         |
| **MIR**                               | C   | 小      | Vladimir Makarov 的轻量 JIT，有 C→MIR 前端                            |
| **Go 编译器** `cmd/compile/internal/ssa` | Go  | 中等     | ⭐ **`.rules` 文件用声明式规则写重写优化**，可读性极高；pass 列表在 `compile.go` 里一目了然 |

⭐ **Go 的 SSA 后端是被低估的学习材料**：`generic.rules` 里一行 `(Add64 (Const64 [c]) (Const64 [d])) => (Const64 [c+d])` 就是一条优化，几千条规则构成了整个标量优化。看完你会明白为什么 Click–Cooper 说"把分析合并"重要。

### 抽象解释 / 数据流（你当前兴趣的直接延伸）

| 工具                  | 说明                                                                                |
| ------------------- | --------------------------------------------------------------------------------- |
| **Apron**           | 经典数值抽象域库：区间、octagon、polyhedra、congruence。INRIA 出品，OCaml 带 C 绑定                    |
| **ELINA**           | ETH Zurich，比 Apron 快的多面体实现                                                        |
| **Crab / Clam**     | ⭐ Crab 是抽象解释框架，**Clam = Crab for LLVM**。想把你的 `lfp` 求解器思路用到真 LLVM IR 上，这是最接近的参照    |
| **IKOS**            | NASA 的抽象解释器，C/C++ 验证                                                              |
| **Frama-C**（EVA 插件） | C 代码的工业级抽象解释，插件架构清晰                                                               |
| **Infer**           | Meta，基于 separation logic + abstract interpretation，有通用的 `AbstractDomain` 接口可以照抄设计 |
| **SVF**             | LLVM 上的指针分析/值流分析，稀疏分析的实现参考                                                        |

⭐ **把你的 `Interval` + `widen/narrow` 和 Apron 的实现对照看**，你会看到真实实现里的 widening 策略比教科书复杂得多（阈值、延迟加宽、loop-local 加宽点）。

### Datalog 路线 → **Soufflé**

```
https://souffle-lang.github.io/
```

⭐ **这是对你最有"顿悟感"的一个工具**：Soufflé 是高性能 Datalog 引擎，它的求值策略就是 **semi-naive evaluation**——**和你 `solve()` 里"只唤醒受影响的变量"字面上是同一个算法**。

```prolog
// 到达定值，三行
reaches(D, N) :- gen(D, N).
reaches(D, N) :- reaches(D, M), edge(M, N), !kill(D, N).
```

看看 Soufflé 为这三行生成的 C++（`souffle -g`），你会看到：索引选择、SCC 分层、增量求值——**全是你手写 worklist 时手动做的决策，被编译器自动化了**。

配套项目：**Doop**（Java 指针分析，用 Datalog 写的，上下文敏感），**cclyzer++**（LLVM 上的 Datalog 分析）。

### 循环优化 / 多面体（接上一轮 Rice 的讨论）

| 工具              | 说明                                                                                           |
| --------------- | -------------------------------------------------------------------------------------------- |
| **isl**         | ⭐ Sven Verdoolaege 的整数集库。**这就是我们说过的"两种 lattice 共存"的地方**：仿射多面体 ∩ $\mathbb Z$-格，Hermite 标准形在里面 |
| **Pluto**       | Bondhugula 的自动并行化器，仿射调度 ILP 求解                                                               |
| **Polly**       | LLVM 里的多面体框架（`-mllvm -polly`）                                                                |
| **PPCG**        | 自动生成 CUDA                                                                                    |
| **CLooG**       | 从多面体生成循环代码                                                                                   |
| **Polybench/C** | ⭐ 标准 benchmark，30 个科学计算核心，所有多面体论文都用它                                                         |

**Halide / TVM / Exo**：调度语言路线。⭐ 建议至少读一遍 **Halide 的 tutorial**——它把 "algorithm 与 schedule 分离"这个 HPF 教训的产物讲得极清楚，`tile/vectorize/parallel/reorder` 这些 scheduling primitive 的名字直接来自 Rice/Illinois 的循环变换目录。

**Exo**（MIT）比较新，强调"用户可扩展的调度 + 变换的正确性检查"，适合想研究"变换合法性如何被形式化"的方向。

### 验证 / 超优化

| 工具            | 说明                                                        |
| ------------- | --------------------------------------------------------- |
| **Alive2**    | ⭐ 见上，translation validation                               |
| **Souper**    | 用 SMT 自动**发现 LLVM 漏掉的优化**。跑一遍你会得到一堆"LLVM 本该优化但没优化"的报告     |
| **CompCert**  | Coq 验证的 C 编译器。后端优化不多，但**每个变换都有机器检查的正确性证明**，想理解"优化为什么正确"必看 |
| **Vellvm**    | LLVM IR 的 Coq 形式化                                         |
| **Z3 / CVC5** | 自己写变换验证器时的 SMT 后端                                         |

### 测试与 fuzzing

| 工具                                  | 说明                                         |
| ----------------------------------- | ------------------------------------------ |
| **Csmith**                          | Regehr 的随机 C 程序生成器，历史上在 GCC/LLVM 找出几百个 bug |
| **YARPGen**                         | Intel 出品，专门针对标量优化与 UB                      |
| **C-Reduce / cvise**                | 测试用例自动缩小                                   |
| **EMI / Equivalence Modulo Inputs** | 变异式 fuzzing 思路                             |

⭐ **想真正理解某个优化，最快的方法是 fuzz 它**：写一个变换，用 Csmith 生成一万个程序，对比变换前后行为。你会在第一天就发现自己的实现有 bug。

---

## 四、Benchmark

| 名字                       | 规模  | 用途                          |
| ------------------------ | --- | --------------------------- |
| **LLVM test-suite**      | 大   | 正确性 + 性能，LLVM 官方            |
| **Polybench/C**          | 小   | ⭐ 循环优化/多面体的事实标准             |
| **embench-iot**          | 小   | 嵌入式，代码体积与性能                 |
| **CoreMark / Dhrystone** | 极小  | 快速 sanity check（但容易被编译器钻空子） |
| **DaCapo / Renaissance** | 大   | JVM，GC 与 JIT 研究             |
| **SPEC CPU 2017**        | 大   | 工业标准，**需付费**（学术机构常有授权）      |

⚠️ **别用 CoreMark 这类微基准评价优化效果**——它太容易被整体内联 + 常量折叠掉。做标量优化用 LLVM test-suite，做循环优化用 Polybench。

---

## 五、课程（有作业和参考答案）

| 课程                                                       | 特点                                           |
| -------------------------------------------------------- | -------------------------------------------- |
| **Cornell CS 6120** *Advanced Compilers*（Adrian Sampson） | ⭐ 最适合自学：Bril、全部讲义视频公开、往届学生项目报告可读             |
| **CMU 15-745** *Optimizing Compilers*                    | 经典 lab 序列，slides 质量高                         |
| **Stanford CS 243** *Program Analysis and Optimization*  | ⭐ **Monica Lam 本人的课**，龙书第 11 章那条线的原始出处       |
| **Rice COMP 412 / 512**                                  | Keith Cooper 的课，*Engineering a Compiler* 的配套 |
| **MIT 6.172** *Performance Engineering*                  | 不是编译器课，但教"如何测量和推理性能"，是做优化的前提                 |
| **Nand2Tetris / 自制编译器类**                                 | 后端优化部分可跳过                                    |

---

## 六、具体项目建议（按难度）

### 热身（1–2 周，用 Bril）

1. 把你的 `solve()` 接到 Bril，实现活跃变量 + DCE，用 Turnt 验证。
2. 支配树（用 Cooper–Harvey–Kennedy 迭代算法）→ SSA 构造 → SSA 销毁。⭐ **SSA 销毁是真正的难点**（lost-copy / swap 问题），别跳过。
3. LVN（局部值编号）→ GVN。

### 核心（1–2 月）

4. **SCCP**：格用 `Product(Env(Flat), Powerset(edges))`，同时做常量传播和不可达边消除。⭐ **跑完后对比"先跑常量传播再跑 CFG 简化、反复两轮"的结果**——你会亲眼看到 Click–Cooper 说的那部分精度差。
5. **Lazy Code Motion**（Knoop–Rüthing–Steffen）：四个数据流分析串联（anticipated / available / earliest / latest）。⭐ 这是把你的框架用到极致的练习：**四个分析里有前向有后向、有 may 有 must**，`Dual` 包装会在这里体现价值。
6. **线性扫描寄存器分配**（Poletto–Sarkar）→ 升级到 **SSA 上的线性扫描**（Wimmer–Franz）。
7. **图着色寄存器分配**：Chaitin → 加 Briggs 乐观着色 → 加 rematerialization。对比 spill 数量。

### 进阶

8. 在 **`regalloc2`** 里实现一个新的 spill 启发式，用它的 fuzzer + benchmark 验证。
9. 用 **Soufflé** 重写你的数据流分析，对比 LOC 和性能。
10. 写一个 LLVM pass，用 **Souper** 找 LLVM 漏掉的优化，挑一个实现出来，用 **Alive2** 验证正确性，提 patch。⭐ **这是一条完整的"从发现到贡献"的路径。**
11. 在 **Polybench** 上实现 tiling + 置换选择，用 McKinley–Carr–Tseng 的 cache 代价模型，对比 Polly 的结果。
12. 把你的 `Interval` 域换成 **octagon**（或直接接 Apron），在真实 C 代码上跑数组越界检查，看 widening 策略对误报率的影响。

---

## 七、给你的具体建议

基于你已有的积累，我会这样排：

**第 1 步（本周）**：Bril + 你的求解器。目标是**一天内看到自己的 lfp 在真 IR 上跑出活跃变量**。这一步的价值是把"抽象框架"和"真实 CFG 的脏细节"（多入口、不可达块、关键边）对上。

**第 2 步**：在 Bril 上做 SSA 构造与销毁。⭐ **这是现代后端的分水岭**，不做这一步，后面所有工业代码都读不懂。

**第 3 步（分叉点）**：

- 偏**理论/分析** → Crab + Apron，或 Soufflé。你的格论背景在这边能直接变现。
- 偏**代码生成** → `regalloc2` 或 QBE/Go SSA。这是你目前最缺的部分（上一轮书单里我也指出龙书这块最弱）。
- 偏**循环/并行** → isl + Polybench + Pluto，接着上一轮 Rice 的讨论往下走。

**贯穿全程**：从一开始就把 **Alive2** 和 **Csmith/cvise** 用起来。**"我的优化是对的"这个信念，在你第一次被 fuzzer 打脸之后才真正开始有意义。**