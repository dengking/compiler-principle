以下按当前 `tvm` 工作区的编译优化实现进行归类。路径均相对于仓库根目录 `/Users/dengkai/Documents/GitHub/tvm`。

> **范围说明**：这里将“编译优化算法”定义为会改变 Relax、TIRx、S-TIR IR 或调度决策的 Pass、调度原语、规则调度、自动调优及其关键分析/简化算法。  
> 不将纯运行时、测试、构建脚本，以及 LLVM/CUDA 等下游编译器内部优化算作 TVM 自身算法。`src/target` 主要负责代码生成，低层寄存器分配、指令选择等通常由 LLVM、NVCC 等下游工具完成。

---

# 1. 总体入口与层次

| 层次           | 主要目录                            | 作用                              |
| ------------ | ------------------------------- | ------------------------------- |
| Relax 图层     | `src/relax/transform/`          | 图级重写、融合、内存规划、设备/布局/精度变换、算子降级    |
| TIRx 低层 IR   | `src/tirx/transform/`           | 循环、缓冲区、表达式、ABI 与设备代码 lowering   |
| S-TIR        | `src/s_tir/transform/`          | 面向 GPU/加速器调度结果的降级与内存、线程、异步流水线优化 |
| Schedule 原语  | `src/s_tir/schedule/primitive/` | 手动或规则驱动的程序变换操作                  |
| MetaSchedule | `src/s_tir/meta_schedule/`      | 搜索空间生成、进化搜索、测量、代价模型、数据库复用       |
| DLight       | `python/tvm/s_tir/dlight/`      | 基于模式匹配的确定性高性能调度规则               |
| 算术分析         | `src/arith/`                    | 整数范围、仿射关系、约束、化简与证明，支撑其他优化合法性判断  |
| TIR/S-TIR 分析 | `src/s_tir/analysis/`           | 内存、FLOPs、访问区域、越界、纯度等分析          |

主要公开 API 声明通常位于：

- `include/tvm/relax/transform.h`
- `include/tvm/tirx/transform.h`
- `include/tvm/s_tir/transform.h`
- `include/tvm/s_tir/schedule/primitive.h`

---

# 2. Relax 图层优化

目录：`src/relax/transform/`

## 2.1 规范化、局部简化与图清理

| 算法 / Pass                              | 源码位置                                              | 作用                                           |
| -------------------------------------- | ------------------------------------------------- | -------------------------------------------- |
| ANF 规范化与类型补全 `Normalize`               | `src/relax/transform/normalize.cc`                | 将 Relax 表达式转换为 A-normal form，并补全/规范结构信息。     |
| 全局符号规范化 `NormalizeGlobalVar`           | `src/relax/transform/normalize.cc`                | 规范 `GlobalVar`、`global_symbol` 与命名。          |
| 绑定规范化、复制传播 `CanonicalizeBindings`      | `src/relax/transform/canonicalize_bindings.cc`    | 消除冗余别名绑定、传播变量、简化 tuple 访问和部分冗余 `match_cast`。 |
| 常量折叠 `FoldConstant`                    | `src/relax/transform/fold_constant.cc`            | 编译期执行常量子图。                                   |
| 公共子表达式消除 `EliminateCommonSubexpr`      | `src/relax/transform/eliminate_common_subexpr.cc` | 识别等价表达式并复用计算结果。                              |
| 死代码消除 `DeadCodeElimination`            | `src/relax/transform/dead_code_elimination.cc`    | 删除无副作用且未被使用的绑定，以及入口不可达函数。                    |
| 拓扑排序 `TopologicalSort`                 | `src/relax/transform/topological_sort.cc`         | 按依赖关系重排绑定或函数结构。                              |
| 转换为 Dataflow Block `ConvertToDataflow` | `src/relax/transform/convert_dataflow.cc`         | 将连续纯计算组织为数据流块，为融合、CSE、常量折叠创造条件。              |
| 消除 Dataflow Block `ToNonDataflow`      | `src/relax/transform/to_non_dataflow.cc`          | 清除 dataflow 结构，进入后续 lower 阶段。                |
| 移除纯度检查标记 `RemovePurityChecking`        | `src/relax/transform/remove_purity_checking.cc`   | 清理 pure / force-pure 语义标记。                   |
| 计算原始值 `ComputePrimValue`               | `src/relax/transform/compute_prim_value.cc`       | 显式化或提前计算可处理的 `PrimExpr` / 形状相关值。             |

## 2.2 函数结构与调用图优化

| 算法 / Pass                                | 源码位置                                                           | 作用                                |
| ---------------------------------------- | -------------------------------------------------------------- | --------------------------------- |
| Lambda 提升 `LambdaLift`                   | `src/relax/transform/lambda_lift.cc`                           | 将嵌套函数提升为全局函数。                     |
| 内联私有函数 `InlinePrivateFunctions`          | `src/relax/transform/inline_functions.cc`                      | 内联私有 Relax 函数，暴露跨函数优化机会。          |
| 展开 tuple 参数 `ExpandTupleArguments`       | `src/relax/transform/expand_tuple_arguments.cc`                | 将 tuple 参数拆分为更直接的函数输入。            |
| 删除未使用参数 `RemoveUnusedParameters`         | `src/relax/transform/remove_unused_parameters.cc`              | 收缩函数 ABI 与跨函数调用参数。                |
| 删除未使用输出 `RemoveUnusedOutputs`            | `src/relax/transform/remove_unused_outputs.cc`                 | 删除调用链中未消费的输出。                     |
| 融合算子 `FuseOps`                           | `src/relax/transform/fuse_ops.cc`                              | 按 Op pattern 将连续算子组合为融合函数。        |
| 融合到 TIR `FuseTIR`                        | `src/relax/transform/fuse_tir.cc`                              | 将 Relax 融合函数生成/合并为低层 TIR 函数。      |
| 合并复合函数 `MergeCompositeFunctions`         | `src/relax/transform/merge_composite_functions.cc`             | 合并带有 composite 标记的函数，用于外部代码生成或分区。 |
| 分割 `call_tir` 模式 `SplitCallTIRByPattern` | `src/relax/transform/split_call_tir_by_pattern.cc`             | 基于模式拆分 `call_tir` 调用图。            |
| 基于调用点特化 `PrimFunc`                       | `src/relax/transform/specialize_primfunc_based_on_callsite.cc` | 根据实际调用参数对底层函数进行特化。                |
| 并行 MatMul 合并 `CombineParallelMatmul`     | `src/relax/transform/combine_parallel_matmul.cc`               | 合并可共享输入或结构的并行矩阵乘。                 |
| 调整 MatMul 顺序 `AdjustMatmulOrder`         | `src/relax/transform/adjust_matmul_order.cc`                   | 重写矩阵乘关联/执行顺序以改善性能或降低开销。           |
| 展开 MatMul 的求和形式 `ExpandMatmulOfSum`      | `src/relax/transform/expand_matmul_of_sum.cc`                  | 对特定矩阵乘加法模式进行代数重写。                 |
| `take` 与 MatMul 重排序                      | `src/relax/transform/reorder_take_after_matmul.cc`             | 将可交换的索引操作移到 MatMul 后。             |
| `permute_dims` 与 `concat` 重排序            | `src/relax/transform/reorder_permute_dims_after_concat.cc`     | 减少重复转置或改善拼接布局。                    |

## 2.3 算子降级、布局与精度优化

| 算法 / Pass                 | 源码位置                                                     | 作用                                           |
| ------------------------- | -------------------------------------------------------- | -------------------------------------------- |
| 算子合法化 `LegalizeOps`       | `src/relax/transform/legalize_ops.cc`                    | 将高层 Relax 算子转换为 lower 后可执行的调用或 TIR 实现。       |
| 算子实现替换 `AlterOpImpl`      | `src/relax/transform/alter_op_impl.cc`                   | 按目标或属性选择更合适的算子实现。                            |
| 算子分解 `DecomposeOps`       | `src/relax/transform/decompose_ops.cc`                   | 将复杂算子拆为更基础的算子组合。                             |
| 布局转换 `ConvertLayout`      | `src/relax/transform/convert_layout.cc`                  | 推导并插入布局转换，适配目标算子布局。                          |
| 布局自由缓冲区标注                 | `src/relax/transform/attach_attr_layout_free_buffers.cc` | 标识可进行布局变换的缓冲区。                               |
| 布局重写预处理拆分                 | `src/relax/transform/split_layout_rewrite_preproc.cc`    | 将布局重写预处理从主计算路径分离。                            |
| 混合精度转换 `ToMixedPrecision` | `src/relax/transform/to_mixed_precision.cc`              | 按规则将计算改写为较低精度或混合精度。                          |
| 数据流 reshape 重写            | `src/relax/transform/rewrite_dataflow_reshape.cc`        | 将可零拷贝处理的 reshape 类计算重写为 view 语义。             |
| `call_tir` 重写             | `src/relax/transform/call_tir_rewrite.cc`                | 为 `call_tir` / `call_dps_packed` 显式插入输出张量分配。 |
| TIR Op Pattern 标注         | `src/relax/transform/annotate_tir_op_pattern.cc`         | 识别和标注 TIR 函数模式，为融合等变换提供信息。                   |

## 2.4 内存、设备与部署优化

| 算法 / Pass                        | 源码位置                                              | 作用                              |
| -------------------------------- | ------------------------------------------------- | ------------------------------- |
| 原地调用选择 `DataflowUseInplaceCalls` | `src/relax/transform/dataflow_inplace.cc`         | 将安全的计算改为原地调用，减少中间张量分配。          |
| 最后使用点释放 `KillAfterLastUse`       | `src/relax/transform/kill_after_last_use.cc`      | 标记对象最后使用位置，帮助内存回收。              |
| 静态块内存规划 `StaticPlanBlockMemory`  | `src/relax/transform/static_plan_block_memory.cc` | 分析对象生命周期并复用内存块。                 |
| 分配工作空间 `AllocateWorkspace`       | `src/relax/transform/allocate_workspace.cc`       | 为模块/函数规划工作空间。                   |
| 降级 `alloc_tensor`                | `src/relax/transform/lower_alloc_tensor.cc`       | 将高层张量分配转换为较低层内存操作。              |
| 虚拟设备实现 `RealizeVDevice`          | `src/relax/transform/realize_vdevice.cc`          | 将虚拟设备规划落地为具体设备与复制操作。            |
| 更新虚拟设备信息 `UpdateVDevice`         | `src/relax/transform/update_vdevice.cc`           | 更新或传播设备放置信息。                    |
| CUDA Graph 重写 `RewriteCUDAGraph` | `src/relax/transform/rewrite_cuda_graph.cc`       | 将可捕获的执行序列改写为 CUDA Graph 友好形式。   |
| 绑定参数 `BindParams`                | `src/relax/transform/bind_params.cc`              | 固化模型权重或常量参数。                    |
| 绑定符号变量 `BindSymbolicVars`        | `src/relax/transform/bind_symbolic_vars.cc`       | 固化符号形状变量，减少动态形状开销。              |
| 更新参数类型 `UpdateParamType`         | `src/relax/transform/update_param_type.cc`        | 按参数变换同步类型信息。                    |
| 打包模型参数 `BundleModelParams`       | `src/relax/transform/bundle_model_params.cc`      | 将模型参数组织为适用于部署的结构。               |
| 参数变换延迟执行                         | `src/relax/transform/lazy_transform_params.cc`    | 延迟参数预处理，减少初始化和传输开销。             |
| 提升参数变换 `LiftTransformParams`     | `src/relax/transform/lift_transform_params.cc`    | 将参数变换提升为可复用/可提前执行的函数。           |
| 绑定全局符号 `AttachGlobalSymbol`      | `src/relax/transform/attach_global_symbol.cc`     | 给可编译入口附加稳定符号名。                  |
| 运行代码生成 `RunCodegen`              | `src/relax/transform/run_codegen.cc`              | 分派外部代码生成器；属于部署 lowering，不是狭义优化。 |

此外，`gradient.cc`、`gradient_simplifier.cc` 实现自动微分及梯度简化，属于编译变换能力，但通常不计入推理编译优化主流水线。

---

# 3. TIRx 低层 IR 优化与 Lowering

目录：`src/tirx/transform/`

## 3.1 表达式、控制流与循环优化

| 算法 / Pass                       | 源码位置                                             | 作用                      |
| ------------------------------- | ------------------------------------------------ | ----------------------- |
| 公共子表达式消除 `CommonSubexprElimTIR` | `src/tirx/transform/common_subexpr_elim.cc`      | 复用重复标量或地址计算。            |
| 语句化简 `StmtSimplify`             | `src/tirx/transform/stmt_simplify.cc`            | 基于算术分析化简条件、索引和语句结构。     |
| 删除空操作 `RemoveNoOp`              | `src/tirx/transform/remove_no_op.cc`             | 删除无效 evaluate、空循环、空分支等。 |
| 删除 `assume`                     | `src/tirx/transform/remove_assume.cc`            | 在约束已消费后清理冗余 assume。     |
| 省略断言 `SkipAssert`               | `src/tirx/transform/skip_assert.cc`              | 移除运行时断言以降低开销。           |
| 循环展开 `UnrollLoop`               | `src/tirx/transform/unroll_loop.cc`              | 静态或受限循环展开。              |
| 循环向量化 `VectorizeLoop`           | `src/tirx/transform/vectorize_loop.cc`           | 将可向量化循环转换为 SIMD 风格操作。   |
| 私有函数内联                          | `src/tirx/transform/inline_private_functions.cc` | 内联模块私有 `PrimFunc`。      |
| 线程轴重映射                          | `src/tirx/transform/remap_thread_axis.cc`        | 变换线程轴绑定以适配目标执行模型。       |
| 替换选中表达式                         | `src/tirx/transform/replace_selected_expr.cc`    | 提供受控表达式替换基础能力。          |

## 3.2 缓冲区、存储与地址优化

| 算法 / Pass                   | 源码位置                                                 | 作用                     |
| --------------------------- | ---------------------------------------------------- | ---------------------- |
| 缓冲区扁平化 `FlattenBuffer`      | `src/tirx/transform/flatten_buffer.cc`               | 将多维 buffer 访问降为线性地址访问。 |
| 存储重写 `StorageRewrite`       | `src/tirx/transform/storage_rewrite.cc`              | 基于生命周期复用/重写临时存储。       |
| Warp 内存降级 `LowerWarpMemory` | `src/tirx/transform/lower_warp_memory.cc`            | 将 warp 级内存抽象转换为底层实现。   |
| 更新指针存储域                     | `src/tirx/transform/update_pointer_storage_scope.cc` | 推导或改写指针存储空间。           |
| 强制索引到 `int32`               | `src/tirx/transform/force_narrow_index_to_i32.cc`    | 在目标允许时压缩索引位宽。          |

## 3.3 数据类型、目标与 ABI Lowering

| 算法 / Pass                     | 源码位置                                               | 作用                           |
| ----------------------------- | -------------------------------------------------- | ---------------------------- |
| 数据类型窄化 `NarrowDataType`       | `src/tirx/transform/narrow_datatype.cc`            | 根据值域或目标要求缩窄整数类型。             |
| 数据类型转换                        | `src/tirx/transform/dtype_conversion.cc`           | 实施特定 dtype 转换规则。             |
| 不支持 dtype 合法化                 | `src/tirx/transform/unsupported_dtype_legalize.cc` | 将目标不支持的数据类型转换为等价可支持形式。       |
| 降级 intrinsic `LowerIntrin`    | `src/tirx/transform/lower_intrin.cc`               | 将高层 intrinsic 替换为目标实现。       |
| 降级 TVM builtin                | `src/tirx/transform/lower_tvm_builtin.cc`          | 将 TVM 运行时 builtin 调用转为低层实现。  |
| 绑定目标 `BindTarget`             | `src/tirx/transform/bind_target.cc`                | 把目标信息绑定到函数/模块。               |
| 主 TIRx lowering               | `src/tirx/transform/lower_tirx.cc`                 | 组织 TIRx 到后端前 IR 的主要降级。       |
| 清理 TIRx Lowering 产物           | `src/tirx/transform/lower_tirx_cleanup.cc`         | 清除 lowering 后的冗余结构。          |
| Opaque TIRx lowering          | `src/tirx/transform/lower_tirx_opaque.cc`          | 处理不透明/特殊 TIRx 结构。            |
| TensorMap 去重 lowering         | `src/tirx/transform/lower_tirx_dedup_tensormap.cc` | 去除或复用重复 TensorMap 描述。        |
| 主机/设备代码分离 `SplitHostDevice`   | `src/tirx/transform/split_host_device.cc`          | 将 host 与 kernel 代码拆分。        |
| 生成 Packed API `MakePackedAPI` | `src/tirx/transform/make_packed_api.cc`            | 生成运行时 ABI 入口。                |
| TVM FFI 参数绑定                  | `src/tirx/transform/tvm_ffi_binder.cc`             | 将函数接口绑定到 FFI 调用约定。           |
| Tile Primitive 分派             | `src/tirx/transform/tile_primitive_dispatch.cc`    | 针对 tile primitive 选择或生成相应实现。 |

---

# 4. S-TIR：面向 GPU/加速器的调度后优化

目录：`src/s_tir/transform/`

## 4.1 循环、线程与并行执行

| 算法 / Pass                       | 源码位置                                                     |
| ------------------------------- | -------------------------------------------------------- |
| 循环规范化 `CanonicalizeLoop`        | `src/s_tir/transform/canonicalize_loop.cc`               |
| 不规则循环标注 `AnnotateIrregularLoop` | `src/s_tir/transform/annotate_irregular_loop.cc`         |
| 循环分区 `LoopPartition`            | `src/s_tir/transform/loop_partition.cc`                  |
| 提升线程绑定 `LiftThreadBinding`      | `src/s_tir/transform/lift_thread_binding.cc`             |
| 统一线程绑定 `UnifyThreadBinding`     | `src/s_tir/transform/unify_thread_binding.cc`            |
| 注入虚拟线程 `InjectVirtualThread`    | `src/s_tir/transform/inject_virtual_thread.cc`           |
| 线程存储同步 `ThreadStorageSync`      | `src/s_tir/transform/thread_storage_sync.cc`             |
| 跨线程归约 lowering                  | `src/s_tir/transform/lower_cross_thread_reduction.cc`    |
| 线程全归约 lowering                  | `src/s_tir/transform/lower_thread_allreduce.cc`          |
| 默认 GPU 调度                       | `src/s_tir/transform/default_gpu_schedule.cc`            |
| GPU 代码边界检查                      | `src/s_tir/transform/bound_checker.cc`                   |
| 使用 assume 减少分支                  | `src/s_tir/transform/using_assume_to_reduce_branches.cc` |
| 不安全 select 重写                   | `src/s_tir/transform/rewrite_unsafe_select.cc`           |

## 4.2 内存、缓冲区与数据搬运

| 算法 / Pass                                      | 源码位置                                                            |
| ---------------------------------------------- | --------------------------------------------------------------- |
| 双缓冲注入 `InjectDoubleBuffer`                     | `src/s_tir/transform/inject_double_buffer.cc`                   |
| 分配位置规划 `PlanAndUpdateBufferAllocationLocation` | `src/s_tir/transform/plan_update_buffer_allocation_location.cc` |
| 共享内存分配合并                                       | `src/s_tir/transform/merge_shared_memory_allocations.cc`        |
| 生成 shared/local stage                          | `src/s_tir/transform/manifest_shared_memory_local_stage.cc`     |
| 紧凑缓冲区区域 `CompactBufferRegion`                  | `src/s_tir/transform/compact_buffer_region.cc`                  |
| 降级 `match_buffer`                              | `src/s_tir/transform/lower_match_buffer.cc`                     |
| 降级 VTCM 分配                                     | `src/s_tir/transform/lower_vtcm_alloc.cc`                       |
| PTX 异步拷贝注入                                     | `src/s_tir/transform/inject_ptx_async_copy.cc`                  |
| PTX `ldg32` 注入                                 | `src/s_tir/transform/inject_ptx_ldg32.cc`                       |
| 异步 DMA lowering                                | `src/s_tir/transform/lower_async_dma.cc`                        |
| Permuted Layout 注入                             | `src/s_tir/transform/inject_permuted_layout.cc`                 |
| 移除未定义值存储                                       | `src/s_tir/transform/remove_store_undef.cc`                     |
| 移除权重布局重写块                                      | `src/s_tir/transform/remove_weight_layout_rewrite_block.cc`     |

## 4.3 软件流水线、Tensor Core 与专用重写

| 算法 / Pass                        | 源码位置                                                  |
| -------------------------------- | ----------------------------------------------------- |
| 软件流水线注入 `InjectSoftwarePipeline` | `src/s_tir/transform/inject_software_pipeline.cc`     |
| 表达式提升 `HoistExpression`          | `src/s_tir/transform/hoist_expression.cc`             |
| 推导 Tensor Core fragment          | `src/s_tir/transform/tensorcore_infer_fragment.cc`    |
| 变换 MMA buffer layout             | `src/s_tir/transform/transform_mma_buffer_layout.cc`  |
| MemHammer 合并访存                   | `src/s_tir/transform/memhammer_coalesce.cc`           |
| MemHammer 中间 stage               | `src/s_tir/transform/memhammer_intermediate_stage.cc` |
| MemHammer 自动拷贝 lowering          | `src/s_tir/transform/memhammer_lower_auto_copy.cc`    |
| MemHammer Tensor Core 重写         | `src/s_tir/transform/memhammer_tensorcore_rewrite.cc` |
| 分裂模式再规范化                         | `src/s_tir/transform/renormalize_split_pattern.cc`    |
| 定义续接/更新                          | `src/s_tir/transform/renew_defs.cc`                   |

## 4.4 结构 Lowering、运行时与辅助变换

| 算法 / Pass         | 源码位置                                              |
| ----------------- | ------------------------------------------------- |
| 将 block 转为 opaque | `src/s_tir/transform/convert_blocks_to_opaque.cc` |
| 降级 opaque block   | `src/s_tir/transform/lower_opaque_block.cc`       |
| 降级初始化 block       | `src/s_tir/transform/lower_init_block.cc`         |
| 设备域标注             | `src/s_tir/transform/decorate_device_scope.cc`    |
| Profile 插桩        | `src/s_tir/transform/profile_instrumentation.cc`  |

---

# 5. S-TIR Schedule 原语

目录：`src/s_tir/schedule/primitive/`

这些是显式程序变换的“积木”，可由手写 `Schedule`、DLight 和 MetaSchedule 调用。

| 原语类别                 | 源码位置                                      | 代表操作                                                            |
| -------------------- | ----------------------------------------- | --------------------------------------------------------------- |
| Cache 与数据局部性         | `cache_read_write.cc`                     | `cache_read`、`cache_write`                                      |
| Cache index          | `cache_index.cc`、`cache_index_helpers.cc` | 索引缓存与辅助变换                                                       |
| 计算位置变换               | `compute_at.cc`                           | `compute_at`、`reverse_compute_at`                               |
| 内联                   | `compute_inline.cc`                       | `compute_inline`、`reverse_compute_inline`                       |
| 循环变换                 | `loop_transformation.cc`                  | `split`、`fuse`、`reorder`、`parallel`、`vectorize`、`unroll`、`bind` |
| 归约变换                 | `reduction.cc`                            | `decompose_reduction`、`rfactor`                                 |
| Blockize 与 Tensorize | `blockize_tensorize.cc`                   | `blockize`、`tensorize`                                          |
| 布局变换                 | `layout_transformation.cc`                | `transform_layout` 等                                            |
| Buffer 访问标注          | `annotate_buffer_access.cc`               | buffer access annotation                                        |
| 通用标注                 | `annotate.cc`、`block_annotate.cc`         | loop/block annotation                                           |
| 读写位置重写               | `read_write_at.cc`                        | `cache_read_at`、`cache_write_at`                                |
| 滚动缓冲区                | `rolling_buffer.cc`                       | `rolling_buffer`                                                |
| Einsum padding       | `pad_einsum.cc`                           | `pad_einsum`                                                    |
| Padding 分解           | `decompose_padding.cc`                    | `decompose_padding`                                             |
| Block 迭代变量重排         | `reorder_block_iter_var.cc`               | block iter var reorder                                          |
| 隐藏 buffer access     | `hide_buffer_access.cc`                   | 隐藏访问关系                                                          |
| 获取 block/loop        | `get_block_loop.cc`                       | 调度对象定位                                                          |
| 循环类型修改               | `for_kind.cc`                             | 设置并行、向量化、展开等 loop kind                                          |
| 采样                   | `sampling.cc`                             | `sample_perfect_tile`、`sample_categorical` 等搜索空间采样              |

调度状态、指令记录与可回放 trace 的核心实现位于：

- `src/s_tir/schedule/schedule.cc`
- `src/s_tir/schedule/state.cc`
- `src/s_tir/schedule/instruction.cc`
- `src/s_tir/schedule/trace.cc`
- `src/s_tir/schedule/traced_schedule.cc`

---

# 6. MetaSchedule 自动调优

目录：`src/s_tir/meta_schedule/`  
Python 层接口与默认实现：`python/tvm/s_tir/meta_schedule/`

## 6.1 搜索空间生成与搜索策略

| 算法                          | C++ 源码位置                                                           | Python 接口/实现                                                              |
| --------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| 后序规则应用空间生成 `PostOrderApply` | `src/s_tir/meta_schedule/space_generator/post_order_apply.cc`      | `python/tvm/s_tir/meta_schedule/space_generator/post_order_apply.py`      |
| 自定义调度函数空间生成                 | `src/s_tir/meta_schedule/space_generator/schedule_fn.cc`           | `python/tvm/s_tir/meta_schedule/space_generator/schedule_fn.py`           |
| 空间生成器并集                     | `src/s_tir/meta_schedule/space_generator/space_generator_union.cc` | `python/tvm/s_tir/meta_schedule/space_generator/space_generator_union.py` |
| 进化搜索 `EvolutionarySearch`   | `src/s_tir/meta_schedule/search_strategy/evolutionary_search.cc`   | `python/tvm/s_tir/meta_schedule/search_strategy/evolutionary_search.py`   |
| 函数回放搜索 `ReplayFunc`         | `src/s_tir/meta_schedule/search_strategy/replay_func.cc`           | `python/tvm/s_tir/meta_schedule/search_strategy/replay_func.py`           |
| Trace 回放搜索 `ReplayTrace`    | `src/s_tir/meta_schedule/search_strategy/replay_trace.cc`          | `python/tvm/s_tir/meta_schedule/search_strategy/replay_trace.py`          |

## 6.2 Schedule Rules

目录：`src/s_tir/meta_schedule/schedule_rule/`

| 规则                      | 源码位置                                | 作用                                          |
| ----------------------- | ----------------------------------- | ------------------------------------------- |
| 多级分块 `MultiLevelTiling` | `multi_level_tiling.cc`             | 生成 tile / reorder / compute location 等候选调度。 |
| Tensor Core 多级分块        | `multi_level_tiling_tensor_core.cc` | 生成 Tensor Core 候选。                          |
| 宽向量多级分块                 | `multi_level_tiling_wide_vector.cc` | 面向 SIMD/宽向量目标。                              |
| Intrinsic 多级分块          | `multi_level_tiling_with_intrin.cc` | 面向指定硬件 intrinsic。                           |
| 自动线程绑定 `AutoBind`       | `auto_bind.cc`                      | 自动绑定 block/thread 轴。                        |
| 自动内联 `AutoInline`       | `auto_inline.cc`                    | 按规则内联 producer/consumer。                    |
| 跨线程归约                   | `cross_thread_reduction.cc`         | 构造 GPU cross-thread reduction。              |
| 添加 rfactor              | `add_rfactor.cc`                    | 将归约拆分为可并行归约阶段。                              |
| 并行/向量化/展开               | `parallel_vectorize_unroll.cc`      | 调整 CPU/GPU loop kind。                       |
| 随机计算位置                  | `random_compute_location.cc`        | 生成不同 `compute_at` 决策。                       |
| 自定义规则                   | `apply_custom_rule.cc`              | 调用用户定义调度规则。                                 |

Python 对应目录：`python/tvm/s_tir/meta_schedule/schedule_rule/`。

## 6.3 候选变异、后处理、测量与反馈

| 类别       | 算法 / 组件                        | 源码位置                                                                                                   |
| -------- | ------------------------------ | ------------------------------------------------------------------------------------------------------ |
| Mutator  | 改变计算位置                         | `src/s_tir/meta_schedule/mutator/mutate_compute_location.cc`                                           |
| Mutator  | 改变并行度                          | `src/s_tir/meta_schedule/mutator/mutate_parallel.cc`                                                   |
| Mutator  | 改变线程绑定                         | `src/s_tir/meta_schedule/mutator/mutate_thread_binding.cc`                                             |
| Mutator  | 改变 tile size                   | `src/s_tir/meta_schedule/mutator/mutate_tile_size.cc`                                                  |
| Mutator  | 改变 unroll 因子                   | `src/s_tir/meta_schedule/mutator/mutate_unroll.cc`                                                     |
| Postproc | Cooperative fetch 重写           | `src/s_tir/meta_schedule/postproc/rewrite_cooperative_fetch.cc`                                        |
| Postproc | Layout 重写                      | `src/s_tir/meta_schedule/postproc/rewrite_layout.cc`                                                   |
| Postproc | 并行/向量化/展开重写                    | `src/s_tir/meta_schedule/postproc/rewrite_parallel_vectorize_unroll.cc`                                |
| Postproc | Reduction block 重写             | `src/s_tir/meta_schedule/postproc/rewrite_reduction_block.cc`                                          |
| Postproc | Tensorize 重写                   | `src/s_tir/meta_schedule/postproc/rewrite_tensorize.cc`                                                |
| Postproc | 未绑定 block 重写                   | `src/s_tir/meta_schedule/postproc/rewrite_unbound_block.cc`                                            |
| Postproc | 禁止动态循环                         | `src/s_tir/meta_schedule/postproc/disallow_dynamic_loop.cc`                                            |
| Postproc | 禁止异步 stride copy               | `src/s_tir/meta_schedule/postproc/disallow_async_strided_mem_copy.cc`                                  |
| Postproc | 验证 GPU 代码                      | `src/s_tir/meta_schedule/postproc/verify_gpu_code.cc`                                                  |
| Postproc | 验证 VTCM 容量                     | `src/s_tir/meta_schedule/postproc/verify_vtcm_limit.cc`                                                |
| 特征提取     | Per-store 特征                   | `src/s_tir/meta_schedule/feature_extractor/per_store_feature.cc`                                       |
| 代价模型接口   | Cost model                     | `src/s_tir/meta_schedule/cost_model/cost_model.cc`                                                     |
| 代价模型     | MLP / XGBoost / Random         | `python/tvm/s_tir/meta_schedule/cost_model/mlp_model.py`、`xgb_model.py`、`random_model.py`              |
| 任务调度     | 梯度式调度                          | `src/s_tir/meta_schedule/task_scheduler/gradient_based.cc`                                             |
| 任务调度     | Round-robin                    | `src/s_tir/meta_schedule/task_scheduler/round_robin.cc`                                                |
| 构建       | 本地 Builder                     | `src/s_tir/meta_schedule/builder/builder.cc`、`python/tvm/s_tir/meta_schedule/builder/local_builder.py` |
| 测量       | Local/RPC Runner               | `python/tvm/s_tir/meta_schedule/runner/local_runner.py`、`rpc_runner.py`                                |
| 结果持久化    | Memory / JSON / Union Database | `src/s_tir/meta_schedule/database/`                                                                    |
| 调优结果复用   | Trace Apply                    | `src/s_tir/meta_schedule/trace_apply.cc`、`python/tvm/s_tir/meta_schedule/trace_apply.py`               |

---

# 7. DLight 确定性规则调度

目录：`python/tvm/s_tir/dlight/`

DLight 不通过大规模搜索选择调度，而是按算子/模式匹配确定性地应用规则。

| 目标类别                    | 规则实现位置                                                                                         |
| ----------------------- | ---------------------------------------------------------------------------------------------- |
| GPU MatMul              | `python/tvm/s_tir/dlight/gpu/matmul.py`                                                        |
| GPU GEMV                | `python/tvm/s_tir/dlight/gpu/gemv.py`                                                          |
| GPU 小 batch GEMV        | `python/tvm/s_tir/dlight/gpu/low_batch_gemv.py`                                                |
| GPU 归约                  | `python/tvm/s_tir/dlight/gpu/reduction.py`                                                     |
| GPU 一般归约                | `python/tvm/s_tir/dlight/gpu/general_reduction.py`                                             |
| GPU RMSNorm             | `python/tvm/s_tir/dlight/gpu/rmsnorm.py`                                                       |
| GPU 转置                  | `python/tvm/s_tir/dlight/gpu/transpose.py`                                                     |
| GPU 回退规则                | `python/tvm/s_tir/dlight/gpu/fallback.py`                                                      |
| CPU GEMV                | `python/tvm/s_tir/dlight/cpu/gemv.py`                                                          |
| CPU 归约                  | `python/tvm/s_tir/dlight/cpu/reduction.py`                                                     |
| Adreno 卷积               | `python/tvm/s_tir/dlight/adreno/convolution.py`                                                |
| Adreno Pooling          | `python/tvm/s_tir/dlight/adreno/pool.py`                                                       |
| Adreno Layout Transform | `python/tvm/s_tir/dlight/adreno/layout_transform.py`                                           |
| Adreno 回退规则             | `python/tvm/s_tir/dlight/adreno/fallback.py`                                                   |
| 通用规则接口与调度框架             | `python/tvm/s_tir/dlight/base/schedule_rule.py`、`base/common_schedules.py`、`base/transform.py` |
| GEMV / block 分析         | `python/tvm/s_tir/dlight/analysis/common_analysis.py`、`analysis/gemv.py`                       |

---

# 8. 算术分析、表达式化简与约束求解

目录：`src/arith/`

这些实现多数不是独立 Pass，而是为循环变换、边界消除、索引化简、向量化、内存规划等提供证明和重写能力。

| 算法类别                             | 源码位置                                                                  |
| -------------------------------- | --------------------------------------------------------------------- |
| 算术分析器 `Analyzer`                 | `src/arith/analyzer.cc`                                               |
| 规范化代数化简                          | `src/arith/canonical_simplify.cc`                                     |
| 重写规则化简                           | `src/arith/rewrite_simplify.cc`、`rewrite_simplify.h`                  |
| 常量折叠                             | `src/arith/const_fold.h`                                              |
| 整数常量范围分析                         | `src/arith/const_int_bound.cc`                                        |
| 区间 / 整数集合推导                      | `src/arith/int_set.cc`、`interval_set.h`                               |
| 模集合分析                            | `src/arith/modular_set.cc`                                            |
| 变量范围与边界推导                        | `src/arith/bound_deducer.cc`                                          |
| 约束提取                             | `src/arith/constraint_extract.cc`                                     |
| 整数约束系统                           | `src/arith/int_constraints.cc`                                        |
| 线性方程检测                           | `src/arith/detect_linear_equation.cc`                                 |
| 线性方程求解                           | `src/arith/solve_linear_equation.cc`                                  |
| 线性不等式求解                          | `src/arith/solve_linear_inequality.cc`                                |
| Presburger 集合                    | `src/arith/presburger_set.cc`                                         |
| 仿射迭代映射分析                         | `src/arith/iter_affine_map.cc`                                        |
| 合取范式转换                           | `src/arith/conjunctive_normal_form.cc`                                |
| 传递比较分析                           | `src/arith/transitive_comparison_analyzer.cc`                         |
| 向量表达式拆解                          | `src/arith/unwrap_vector_expr.cc`                                     |
| 访问域分析                            | `src/arith/domain_touched.cc`                                         |
| Z3 证明器集成                         | `src/arith/z3_prover.cc`                                              |
| 携带 Analyzer 的 IR Visitor/Mutator | `src/arith/ir_visitor_with_analyzer.cc`、`ir_mutator_with_analyzer.cc` |

---

# 9. S-TIR 分析算法

目录：`src/s_tir/analysis/`

| 分析                   | 源码位置                                   |
| -------------------- | -------------------------------------- |
| 已分配内存计算              | `calculate_allocated_memory.cc`        |
| FLOPs 估计             | `estimate_flops.cc`                    |
| Anchor SBlock 查找     | `find_anchor_sblock.cc`                |
| 内存复制识别               | `identify_memcpy.cc`                   |
| 纯函数判断                | `is_pure_function.cc`                  |
| 越界检查                 | `oob_checker.cc`                       |
| SBlock 访问区域检测        | `sblock_access_region_detector.cc`     |
| Buffer access LCA 检测 | `sblock_buffer_access_lca_detector.cc` |
| GPU 代码合法性验证          | `verify_gpu_code.cc`                   |

---

# 10. TE 到 TIRx 的构建与图分析

目录：`src/te/operation/`

这部分主要负责从 Tensor Expression 构造低层 IR，而不是调优器本身，但它是后续优化的入口。

| 组件                    | 源码位置                                  |
| --------------------- | ------------------------------------- |
| Compute Operation     | `src/te/operation/compute_op.cc`      |
| 创建 PrimFunc           | `src/te/operation/create_primfunc.cc` |
| Extern Operation      | `src/te/operation/extern_op.cc`       |
| 图分析                   | `src/te/operation/graph.cc`           |
| Placeholder Operation | `src/te/operation/placeholder_op.cc`  |
| Scan Operation        | `src/te/operation/scan_op.cc`         |

---

## 推荐阅读顺序

1. `src/relax/transform/fuse_ops.cc`
2. `src/relax/transform/fuse_tir.cc`
3. `src/relax/transform/static_plan_block_memory.cc`
4. `src/tirx/transform/storage_rewrite.cc`
5. `src/tirx/transform/vectorize_loop.cc`
6. `src/s_tir/schedule/primitive/loop_transformation.cc`
7. `src/s_tir/meta_schedule/schedule_rule/multi_level_tiling.cc`
8. `src/s_tir/meta_schedule/search_strategy/evolutionary_search.cc`
9. `python/tvm/s_tir/dlight/gpu/matmul.py`
10. `src/arith/analyzer.cc` 与 `src/arith/rewrite_simplify.cc`

这个清单覆盖了当前项目中主要的确定性编译优化、调度变换、自动搜索优化和其关键分析基础。
