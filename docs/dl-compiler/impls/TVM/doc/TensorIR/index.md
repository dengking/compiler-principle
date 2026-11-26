# [TensorIR](https://tvm.apache.org/docs/deep_dive/tensor_ir/index.html)

TensorIR is one of the **core abstractions** in the Apache TVM stack, used to **represent** and **optimize** ***primitive tensor functions***.

The TensorIR codebase consists of two modules (split from the former `tir`):

- **tirx** — Core IR definitions and lowering (PrimFunc, Buffer, SBlock, expressions, statements, lowering passes).

- **s_tir** (Schedulable TIR) — Schedule primitives, MetaSchedule, DLight, and tensor intrinsics.

In TVMScript, both modules are accessed via `from tvm.script import tirx as T`.

## [Tensor Program Abstraction](https://tvm.apache.org/docs/deep_dive/tensor_ir/abstraction.html)

Before we dive into the details of **TensorIR**, let’s first introduce what is a **primitive tensor function**. **Primitive tensor functions** are functions that correspond to a single “unit” of **computational operation**. For example, a **convolution operation** can be a **primitive tensor function**, and a **fused convolution + relu operation** can also be a **primitive tensor function**. Usually, a typical abstraction for **primitive tensor function** implementation contains the following elements: multi-dimensional buffers, loop nests that drive the tensor computations, and finally, the compute statements themselves.

翻译: 在深入讲解 TensorIR 的细节之前，我们先来介绍何为**张量原语函数**。**张量原语函数**对应着单个计算操作单元。例如一次卷积运算可以作为一个**张量原语函数**；卷积‑ReLU 融合后的运算同样能够成为**张量原语函数**。一般而言，一套用于实现**张量原语函数**的标准抽象包含下述组成部分：多维缓冲区、驱动张量计算的循环嵌套，以及最核心的计算语句本身。

```python
from tvm.script import tirx as T

@T.prim_func
def main(
    A: T.Buffer((128,), "float32"),
    B: T.Buffer((128,), "float32"),
    C: T.Buffer((128,), "float32"),
) -> None:
    for i in range(128):
        with T.sblock("C"):
            vi = T.axis.spatial(128, i)
            C[vi] = A[vi] + B[vi]
```

### Key Elements of Tensor Programs

The demonstrated primitive tensor function calculates the element-wise sum of two vectors. The function:

- Accepts three **multi-dimensional buffers** as parameters, and generates one **multi-dimensional buffer** as output.

- Incorporates(包含/内置) a solitary(单层/唯一) **loop nest** `i` that facilitates the computation.
  
  - 翻译: 内含唯一一组用于完成计算的循环嵌套 `i`。

- Features a singular **compute statement** that calculates the element-wise sum of the two vectors.
  
  - 翻译: 仅有一条计算语句，用于求解两个向量的逐元素相加。



### Extra Structure in TensorIR

翻译: 关键一点：我们不能够对程序执行任意变换，部分计算依赖循环的执行顺序。所幸，我们所研究的绝大多数张量原语函数都具备优良特性，例如各个循环迭代之间相互独立。

Crucially, we are unable to execute arbitrary transformations on the program, as certain computations rely on the loop’s sequence. Fortunately, the majority of **primitive tensor functions** we focus on possess favorable properties, such as independence among loop iterations. For instance, the aforementioned program includes block and iteration annotations:

- The **block annotation** `with T.sblock("C")` signifies that the block is the **fundamental computation unit** designated for scheduling. A block may encompass a single computation statement, multiple computation statements with loops, or opaque intrinsics such as **Tensor Core instructions**.
  
  - 翻译: 块注解 `with T.sblock("C")` 代表该代码块是用于调度的**基础计算单元**。一个调度块可以仅包含一条计算语句、带有循环的多条计算语句，或是张量核心指令这类不可见内置函数。

- The **iteration annotation** `T.axis.spatial`, indicating that variable `vi` is mapped to `i`, and all iterations are independent.

While this information isn’t crucial for *executing* the specific program, it proves useful when transforming the program. Consequently, we can confidently parallelize or reorder loops associated with `vi`, provided we traverse all the index elements from 0 to 128.

翻译: 该类信息对于**运行**当前程序而言并非必要，但在做程序变换时十分关键。因此只要遍历区间 0‑128 的全部索引元素，我们便可安心地对`vi`对应的循环执行并行化或是循环重排操作。

## [Understand TensorIR Abstraction](https://tvm.apache.org/docs/deep_dive/tensor_ir/learning.html)

TensorIR is the tensor program abstraction in Apache TVM, which is one of the standard machine learning compilation frameworks. The principal objective of tensor program abstraction is to depict loops and associated hardware acceleration options, including threading, the application of specialized hardware instructions, and memory access.
