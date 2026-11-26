可从以下三个位置查看，推荐优先使用第 1 种。

## 1. Python API 总览：`tvm.relax.op`

```python
from tvm import relax

dir(relax.op)
```

该模块的聚合入口是：

```text
python/tvm/relax/op/__init__.py
```

它按类别导出了核心算子，例如：

- 基础与调用：`base.py`
- 一元算子：`unary.py`
- 二元算子：`binary.py`
- 三元算子：`ternary.py`
- 张量创建：`create.py`
- 索引：`index.py`
- 线W性代数：`linear_algebra.py`
- 张量变形与布局：`manipulate.py`
- 统计与归约：`statistical.py`
- 排序与选择：`sorting.py`、`search.py`、`set.py`
- 量化：`qdq.py`
- 神经网络：`nn/`
- 图像与视觉：`image/`、`vision/`
- 内存视图：`memory/`
- 集体通信与分布式：`ccl/`、`distributed/`
- VM 与内建调用：`vm/`、`builtin/`

例如，`python/tvm/relax/op/__init__.py` 已集中列出 `add`、`matmul`、`reshape`、`concat`、`sum`、`softmax` 等 Python 可用算子。

## 2. 运行时完整列表：注册表查询

若要查看**当前已加载构建实际支持的全部 Relax 算子**，使用 TVM 的 Op 注册表：

```python
from tvm.ir import Op

relax_ops = sorted(
    op_name
    for op_name in Op.list_op_names()
    if op_name.startswith("relax.")
)

print("\n".join(relax_ops))
print(f"共 {len(relax_ops)} 个 Relax Op")
```

`Op.list_op_names()` 定义于：

```text
python/tvm/ir/op.py
```

它会调用 C++ Op Registry，因此能包含：

- `relax.*` 核心算子；
- `relax.nn.*` 神经网络算子；
- `relax.image.*`、`relax.vision.*`；
- `relax.ccl.*` 与 `relax.distributed.*`；
- 已编译、已加载的可选扩展提供的算子。

这比单纯查看 Python 文件更可靠，因为某些算子是 C++ 注册、Python 仅提供封装；也可能因构建选项不同而增减。

## 3. C++ 注册实现：权威源码位置

所有 Relax Op 最终都通过如下形式注册：

```cpp
TVM_REGISTER_OP("relax.xxx")
```

核心目录：

```text
src/relax/op/
```

主要分类如下：

| 算子类别                                | C++ 实现位置                                                  |
| ----------------------------------- | --------------------------------------------------------- |
| 基础调用、`call_tir`、`call_packed`、设备提示等 | `src/relax/op/op.cc`                                      |
| 一元算子                                | `src/relax/op/tensor/unary.cc`                            |
| 二元算子                                | `src/relax/op/tensor/binary.cc`                           |
| 三元算子                                | `src/relax/op/tensor/ternary.cc`                          |
| 张量创建                                | `src/relax/op/tensor/create.cc`                           |
| 索引与切片                               | `src/relax/op/tensor/index.cc`                            |
| 张量变形、布局、拼接、gather/scatter           | `src/relax/op/tensor/manipulate.cc`                       |
| 线性代数                                | `src/relax/op/tensor/linear_algebra.cc`                   |
| 统计、归约                               | `src/relax/op/tensor/statistical.cc`                      |
| 排序与 TopK                            | `src/relax/op/tensor/sorting.cc`                          |
| 搜索、`where`、`argmax`、`argmin`        | `src/relax/op/tensor/search.cc`                           |
| 集合类算子                               | `src/relax/op/tensor/set.cc`                              |
| 数据类型转换                              | `src/relax/op/tensor/datatype.cc`                         |
| 量化 / 反量化                            | `src/relax/op/tensor/qdq.cc`                              |
| 随机采样                                | `src/relax/op/tensor/sampling.cc`                         |
| 梯度相关算子                              | `src/relax/op/tensor/grad.cc`                             |
| 张量属性检查                              | `src/relax/op/tensor/inspect.cc`                          |
| 神经网络通用算子                            | `src/relax/op/nn/nn.cc`                                   |
| 卷积                                  | `src/relax/op/nn/convolution.cc`                          |
| 注意力                                 | `src/relax/op/nn/attention.cc`                            |
| 池化                                  | `src/relax/op/nn/pooling.cc`                              |
| 图像 resize                           | `src/relax/op/image/resize.cc`                            |
| ROI Align / ROI Pool / NMS          | `src/relax/op/vision/roi_align.cc`、`roi_pool.cc`、`nms.cc` |
| CCL 通信                              | `src/relax/op/ccl/ccl.cc`                                 |
| 分布式算子                               | `src/relax/op/distributed/`                               |
| 内存 view 算子                          | `src/relax/op/memory/view.cc`                             |

## Python 封装与 C++ 注册的关系

以 `relax.add` 为例：

```text
Python 调用接口：
python/tvm/relax/op/binary.py

        ↓ FFI 调用

C++ Op 注册与类型/形状推导：
src/relax/op/tensor/binary.cc
TVM_REGISTER_OP("relax.add")
```

因此：

- **想看如何调用、参数含义、Python 类型标注**：看 `python/tvm/relax/op/`；
- **想看算子真正的注册、类型推导、结构信息推导、纯度等属性**：看 `src/relax/op/`；
- **想获取当前环境完整、准确的列表**：运行 `Op.list_op_names()` 后筛选 `relax.` 前缀。
