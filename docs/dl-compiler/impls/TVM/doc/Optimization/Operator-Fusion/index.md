# [Operator Fusion](https://tvm.apache.org/docs/arch/fusion.html)

**Operator fusion** is one of the most impactful optimizations in TVM. Instead of launching one **kernel** per **operator** (e.g., conv2d, bias_add, relu), fusion merges multiple operators into a single kernel, eliminating intermediate memory allocations and kernel launch overhead.

TVM provides two complementary fusion mechanisms:

- **Automatic fusion** (`FuseOps` + `FuseTIR`): groups operators based on their computational patterns using a **post-dominator analysis algorithm**.

- **Pattern-based fusion** (`FuseOpsByPattern`): groups operators that match user-defined dataflow patterns, typically for offloading to external backends (cuBLAS, CUTLASS, DNNL, etc.).
  
  - 翻译: 将匹配用户自定义数据流模式的算子进行归组，通常用于将对应计算任务卸载到外部后端（如 cuBLAS、CUTLASS、DNNL 等）执行。

Both produce the same output: Relax functions marked with `Primitive=True` that are later lowered to fused **TIR kernels** or dispatched to external libraries.

翻译: 两种方式的最终产出一致：都会生成标记了 `Primitive=True` 的 Relax 函数，这类函数后续会被降级为融合 TIR 算子内核，或调度至外部加速库执行。

## Overview

Fusion involves three passes:

```python
IRModule (after LegalizeOps)
     │
     ▼  AnnotateTIROpPattern        ← label each op (elementwise, reduce, etc.)
IRModule (annotated)
     │
     ▼  FuseOps                     ← group ops into fused Relax functions
IRModule (with fused functions marked Primitive=True)
     │
     ▼  FuseTIR                     ← merge TIR PrimFuncs inside each group
IRModule (fused TIR kernels)
```

In the compilation pipeline, these passes appear in the backend-specific `legalize_passes` phase. For example, the **CUDA pipeline** (`python/tvm/relax/backend/cuda/pipeline.py`) runs:

```python
LegalizeOps()          # lower Relax ops to call_tir
AnnotateTIROpPattern() # annotate pattern kinds
FoldConstant()
FuseOps()              # group ops
FuseTIR()              # merge TIR functions
```

## Operator Pattern Classification

Before fusion, `AnnotateTIROpPattern` analyzes each **TIR function** in the module and assigns an `OpPatternKind`. The fusion algorithm uses these pattern kinds to decide which operators can be fused together.

| Pattern Kind       | Value | Description                                                                                                                                                                       |
| ------------------ | ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `kElemWise`        | 0     | Elementwise: one-to-one input/output mapping (e.g., `add`, `relu`, `exp`).                                                                                                        |
| `kBroadcast`       | 1     | Broadcasting: output axes map to input axes in order, but some input axes may be broadcast (e.g., `bias_add`). Note: `transpose` is **not** broadcast because axes are reordered. |
| `kInjective`       | 2     | Injective: each output element depends on a single input element, but the mapping may be non-trivial (e.g., `reshape`, `concatenate`, `transpose`).                               |
| `kCommReduce`      | 3     | Communicative reduction: output elements aggregate over input elements (e.g., `sum`, `max`, `mean`).                                                                              |
| `kOutEWiseFusable` | 4     | Complex operation whose output can accept elementwise followers, but cannot chain with another complex op (e.g., `conv2d`, `matmul`, `dense`).                                    |
| `kTuple`           | 7     | Tuple node. Can fuse into subsequent injective ops but is treated specially.                                                                                                      |
| `kOpaque`          | 8     | Opaque: cannot be fused (e.g., external function c                                                                                                                                |

These kinds form an ordering: lower values are “simpler” and more fusable. The fusion algorithm uses `CombinePattern(lhs, rhs) = max(lhs, rhs)` when merging patterns along a path.

## FuseOps: Automatic Fusion

`FuseOps` (`src/relax/transform/fuse_ops.cc`) groups bindings in a dataflow block into new Relax functions. It operates only within `DataflowBlock`s — if your module doesn’t have any, run `ConvertToDataflow` first.

### Algorithm

The fusion algorithm addresses diamond-shaped dataflow branches, where a single producer (e.g., conv2d) has multiple consumers that eventually reconverge:

```
   conv2d
   /  |  \
  /   |   \
op    op   op
 \    |    /
  \   |   /
 elemwise add
```

At the point of `conv2d`, we don’t know if all future paths will merge. The algorithm uses **post-dominator analysis** to resolve this:

1. **Build forward graph**: construct an `IndexedForwardGraph` from the dataflow block. Each node has an `OpPatternKind` and a list of forward edges.

2. **Build post-dominator tree**: compute the **immediate post-dominator** of each node using [Least Common Ancestor (LCA)](https://en.wikipedia.org/wiki/Lowest_common_ancestor) on the DAG. The post-dominator of a node is the closest downstream node where **all** future paths converge.

3. **Fuse groups**: for each node in **topological order**, check if it can be fused with its **immediate post-dominator**:
   
   - **CheckPath**: verify that all paths from the node to its post-dominator satisfy the fusion conditions (pattern compatibility, depth limits, argument limits).
   
   - **CommitFuse**: mark all intermediate nodes as belonging to the same group using a **Union-Find data structure**.

4. **Create grouped functions**: extract each group into a new `relax.Function` with the attribute `Primitive=True`. Replace the original bindings with a call to the grouped function.
   
   1. 翻译: **FuseOps（源码路径：src/relax/transform/fuse_ops.cc）** 将数据流块内的绑定语句分组，构建为新的 Relax 函数。该 Pass 仅在数据流块（`DataflowBlock`）内部生效；如果你的 IRModule 中不存在数据流块，需要先执行 `ConvertToDataflow` 变换。


