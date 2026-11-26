# TVM

apache [Apache TVM](https://tvm.apache.org/)

## How to practice

没有物理 GPU **并不会**阻挡你学习 TVM 和 GPU 编程的绝大部分内容。原因有二：

- **TVM 的核心思想（调度、优化、编译流程）大部分是设备无关的**——你在 CPU 上就能练习绝大多数概念；
- **GPU 编程的"真机"可以用云服务、模拟器、免费在线平台补齐**——现在获取一块临时 GPU 的门槛极低。

下面分成"能在 CPU 上学的部分"和"需要 GPU 时怎么办"两条线来讲。

---

### 2. 大量 TVM 内容可以纯 CPU 练习

TVM 学习的重点其实是**思维方式**，而这些在 CPU 后端上完全能练：

- **张量表达式（Tensor Expression, TE）与 TensorIR**：定义计算、写调度（schedule）。`split`、`reorder`、`fuse`、`vectorize`、`parallel`、`tile` 这些调度原语，在 CPU 后端（`target="llvm"`）上都能跑、能测性能。
- **理解 compute 与 schedule 分离**：这是 TVM 最核心的哲学，与是否有 GPU 无关。
- **AutoTVM / MetaSchedule 自动调优**：在 CPU 上照样能体验"自动搜索最优调度"的完整流程。
- **Relax / Relay 前端到后端的编译流程**：导入模型、做图级优化、lower 到底层 IR，整个 pipeline 在 CPU 上都能走通。

**建议做法**：安装 CPU 版 TVM（`pip` 装或从源码编译，`target` 用 `llvm`），先把 TVM 官方的 [Tutorials 和 How-To Guides](https://tvm.apache.org/docs/) 从头到尾跑一遍。这一步不需要任何 GPU。

---

### 3. GPU 编程概念也能先在 CPU / 模拟环境理解

GPU 编程的很多核心概念是可以脱离真机先建立直觉的：

- **线程层次模型**（grid / block / thread，或 TVM 里的 `blockIdx` / `threadIdx`）；
- **内存层次**（global / shared / register，即 TVM 里的 `shared`、`local` scope）；
- **并行归约、bank conflict、coalesced access（合并访存）** 等优化概念。

即使代码暂时跑不到真 GPU 上，你也可以：**用 TVM 写出 GPU 调度（绑定 `blockIdx`、`threadIdx`，用 `cache_read` 到 shared memory），然后用 `mod.script()` 打印生成的 CUDA 代码来"读"**——阅读生成的 kernel 本身就是极好的学习。

---

### 4. 需要真 GPU 时——免费/低成本的获取途径

到了要**实际运行、测性能、调优**的阶段，可以用以下方式借到 GPU：

**① Google Colab（最推荐的入门选择）**

- 免费版就提供 NVIDIA GPU（通常是 T4）。
- 可以在 Colab 里 `pip` 安装或编译 TVM，直接写 CUDA、跑 GPU 调度。
- 也可以直接在 Colab 里写 CUDA C（用 `nvcc`）练习原生 GPU 编程。

**② Kaggle Notebooks**

- 每周有固定额度的免费 GPU（如 T4、P100），适合跑稍长的调优任务。

**③ 云服务商的按需实例**

- AWS、阿里云、腾讯云、AutoDL（国内，性价比高、按小时计费）等都提供 GPU 云主机。
- 用于练习，选最便宜的卡按小时租即可，练完就关，花费很低。

**④ 学校/公司资源**

- 如果是学生，很多学校有 GPU 集群或实验室资源，值得问一下。

---

### 5. 关于原生 CUDA / GPU 编程的练习

如果你想练的是**通用 GPU 编程**（不仅是 TVM），几条路：

- **CUDA C/C++**：在 Colab 上用 `%%writefile` 写 `.cu` 文件，`!nvcc` 编译运行。经典教材是《Programming Massively Parallel Processors》(PMPP)，配套练习都能在 Colab 完成。
- **Triton**：OpenAI 的 GPU 编程语言，用 Python 写 GPU kernel，语法友好，同样可在 Colab 跑，与 TVM 的思路有相通之处。
- **无 GPU 时的替代**：可以用 CPU 上的 OpenMP / SIMD 先建立"并行"的直觉，但真正的 GPU 特性（如 warp、shared memory）还是要在真机上体会。

---

### 6. 一条推荐的循序渐进路线

```
阶段一（纯 CPU，本地）
  装 CPU 版 TVM → 跑通 TE/TensorIR 教程 → 练 CPU 调度原语
        ↓
阶段二（纯 CPU，本地）
  写 GPU 调度但只【打印】生成的 CUDA 代码来阅读理解
        ↓
阶段三（借用 Colab 免费 GPU）
  把阶段二的 GPU 调度真正跑起来，测性能，对比不同调度
        ↓
阶段四（Colab / 云 GPU）
  练原生 CUDA / Triton，跑 MetaSchedule 自动调优，做端到端模型部署
```

---

### 7. 小结

- **绝大部分 TVM 学习（compute/schedule 分离、调度原语、编译流程、自动调优）在纯 CPU 上就能完成**，这是你现在立刻就能开始的部分。
- **GPU 概念**可以先通过"写 GPU 调度 + 阅读生成的 CUDA 代码"建立直觉，无需真机。
- **真正需要运行 GPU 代码时**，Google Colab（免费）是最省事的起点，Kaggle 和按小时租的云 GPU（如 AutoDL）是进阶选择。

一句话：**没有 GPU 完全不影响你现在就开始学 TVM——先在 CPU 上把核心思想吃透，等到需要跑 GPU 时，一块免费的 Colab GPU 就够你练很久了。**
