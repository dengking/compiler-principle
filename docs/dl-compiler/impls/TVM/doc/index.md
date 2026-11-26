# documents

- https://discuss.tvm.apache.org/

- **源码 `tests` 目录**：所有 Pass、调度原语、IR 接口的用法，在单元测试里都有最标准的写法，是查 API 的最佳去处

- **官方 RFC 文档**：Relax、TensorIR、TVM Unity 等所有核心架构设计，都有对应的 RFC 提案，是理解设计思路、底层原理的最佳资料，可在 GitHub 仓库的 `rfcs` 目录或社区论坛找到

- 陈天奇《机器学习编译》(MLC) 课程
  
  - https://mlc.ai/summer22-zh/
  
  - https://github.com/Relph1119/mlc-learning

## Overview

Apache TVM is a machine learning compilation framework, following the principle of **Python-first development** and **universal deployment**. It takes in **pre-trained machine learning models**, compiles and generates deployable modules that can be embedded and run everywhere. Apache TVM also enables customizing optimization processes to introduce new optimizations, libraries, **codegen** and more.

### Key Principle

### Key Flow

Here is a typical flow of using TVM to deploy a machine learning model. For a runnable example, please refer to [Quick Start](https://tvm.apache.org/docs/get_started/tutorials/quick_start.html#quick-start)

(1) **Import/construct an ML model**

(2) **Perform composable optimization** transformations via `pipelines`

The pipeline encapsulates a collection of transformations to achieve two goals:

- **Graph Optimizations**: such as operator fusion, and layout rewrites.

- **Tensor Program Optimization**: Map the operators to low-level implementations (both library or codegen)

> The two are goals but not the stages of the pipeline. The two optimizations are performed **at the same level**, or separately in two stages.

(3) **Build and universal deploy**


