## 8. 生命周期与启动时序

**刻意泄漏的单例**——与 `GlobalFunctionTable` 同一手法：

```377:384:src/ffi/object.cc
  static TypeTable* Global() {
    // deliberately create a new instance via raw new
    // to ensure table lives longer in case unloading
    // still need the table info
    // memory will be recycled by the OS at program exit
    static TypeTable* inst = new TypeTable();
    return inst;
  }
```

共享库卸载顺序不确定，卸载后的代码可能仍需查表，因此干脆让表活到进程结束，由 OS 回收。

**构造即预注册**：`TypeTable` 构造函数先把 $[0, 128)$ 全部置空，再注册根类型 `Object`（index $64$、depth $0$），随后经 `ReserveBuiltinTypeIndex` / `ReserveDepthOneObjectTypeIndex` 为全部内置静态类型占位（`object.cc:387-440`）。C++ 侧的用户注册则通常放在 `TVM_FFI_STATIC_INIT_BLOCK()` 中，随共享库加载自动完成（`object.cc` 底部的内置反射注册块即为例证）。

## 9. 诊断工具：Dump

`Dump(min_children_count)` 自底向上统计每个类型的实际子孙数与期望槽位数，打印 `index / type_key / parent / num_child_slots / num_children / expected_child_slots` 对照表（`object.cc:342-375`）。它为 `_type_child_slots` 的调优提供数据支撑——让快路径（区间判断）命中率最大化，是性能调优的实用入口。

## 10. 结语

把对象类型注册进 TVM FFI，本质上是**用 `type_key` 向 `TypeTable` 交换一个全局唯一的 `type_index`，并挂上单继承祖先链与反射元数据**。这套机制的设计哲学可以浓缩为三句话：

1. **布局冻结，类型开放**——24 字节对象头不变，`type_index` 空间从 128 起无限扩展；
2. **约定代替锁**——初始化期注册、运行期只读，把同步成本降为零；
3. **注册期复杂，查询期 O(1)**——祖先链压平 + 连续槽位，把类型检查压成一次数组访问或区间比较。

`TypeTable` 由此成为整个动态类型系统的单一事实来源：对上支撑 `ObjectDef`/`register_object` 的多语言注册，对下支撑 `IsInstance` 检查、反射访问与 stub 生成，是 ABI"稳定而又可扩展"承诺的最终兑现者。

-
现在我已掌握完整链路，来分析这个装饰器。

# `@tvm_ffi.register_object("ir.IRModule")` 实现分析

这一行代码做的事，本质是**把 Python 类 `IRModule` 与 C++ 类 `IRModuleNode` 通过 `type_index` 绑定起来**，并把 C++ 反射信息"注入"到 Python 类上。它是一个**纯 Python 侧的绑定操作**——注意 `register_object` 的文档明确要求："It requires `type_key` to be registered already on the C++ side"。

## 全景：三段式链路

```text
① C++ 侧注册（tvm 项目，库加载时自动执行）
   TVM_FFI_DECLARE_OBJECT_INFO_FINAL("ir.IRModule", IRModuleNode, ffi::Object)
   TVM_FFI_STATIC_INIT_BLOCK() { IRModuleNode::RegisterReflection(); }
        ↓ 写入 TypeTable：分配 type_index、祖先链、5 个字段、TypeAttr
② Python 装饰器（tvm-ffi 项目）
   @tvm_ffi.register_object("ir.IRModule")
        ↓ 按 type_key 反查 type_index，建立双向映射，注入属性
③ 运行期
   C++ 返回 IRModule 对象 → make_ret_object 按 type_index 查表 → 实例化 Python IRModule
```

## ① C++ 侧：类型早已在 TypeTable 中

TVM 的 `IRModuleNode` 用宏声明类型信息（不可再派生）：

```245:245:/Users/dengkai/Documents/GitHub/tvm/include/tvm/ir/module.h
  TVM_FFI_DECLARE_OBJECT_INFO_FINAL("ir.IRModule", IRModuleNode, ffi::Object);
```

并在静态初始化块中注册反射字段与结构相等/哈希方法：

```134:146:/Users/dengkai/Documents/GitHub/tvm/include/tvm/ir/module.h
  static void RegisterReflection() {
    namespace refl = tvm::ffi::reflection;
    refl::ObjectDef<IRModuleNode>()
        .def_ro("functions", &IRModuleNode::functions)
        .def_ro("global_var_map_", &IRModuleNode::global_var_map_)
        .def_ro("source_map", &IRModuleNode::source_map)
        .def_ro("attrs", &IRModuleNode::attrs)
        .def_ro("global_infos", &IRModuleNode::global_infos);
    // register custom structural equal and hash.
    refl::TypeAttrDef<IRModuleNode>()
        .def("__s_equal__", &IRModuleNode::SEqual)
        .def("__s_hash__", &IRModuleNode::SHash);
  }
```

```42:42:/Users/dengkai/Documents/GitHub/tvm/src/ir/module.cc
TVM_FFI_STATIC_INIT_BLOCK() { IRModuleNode::RegisterReflection(); }
```

即：`libtvm.so` 被加载时，`TypeTable` 里已存在 key 为 `"ir.IRModule"` 的 `Entry`，含 `type_index`（$\geq 128$ 的动态索引）、祖先链、5 个 `TVMFFIFieldInfo`、以及 `__s_equal__` / `__s_hash__` 属性列。

## ② Python 装饰器：`_register` 的四步

装饰器主体只有 13 行（`tvm-ffi/python/tvm_ffi/registry.py:79-91`）：

```79:91:/Users/dengkai/Documents/GitHub/tvm-ffi/python/tvm_ffi/registry.py
    def _register(cls: _T, object_name: str) -> _T:
        """Register the object type with the FFI core."""
        type_index = core._object_type_key_to_index(object_name)
        if type_index is None:
            if _SKIP_UNKNOWN_OBJECTS:
                return cls
            raise ValueError(f"Cannot find object type index for {object_name}")
        info = core._register_object_by_index(type_index, cls)
        _add_class_attrs(type_cls=cls, type_info=info)
        setattr(cls, "__tvm_ffi_type_info__", info)
        if init:
            _install_init(cls, info)
        return cls
```

### 第 1 步：type_key → type_index

`_object_type_key_to_index` 是 Cython 薄封装，直接调 C ABI 的 `TVMFFITypeKeyToIndex`：

```419:425:/Users/dengkai/Documents/GitHub/tvm-ffi/python/tvm_ffi/cython/object.pxi
def _object_type_key_to_index(str type_key):
    """get the type index of object class"""
    cdef int32_t tidx
    type_key_arg = ByteArrayArg(c_str(type_key))
    if TVMFFITypeKeyToIndex(type_key_arg.cptr(), &tidx) == 0:
        return tidx
    return None
```

若 C++ 侧没注册（比如 `libtvm.so` 未加载或拼错 key），返回 `None`，装饰器抛 `ValueError: Cannot find object type index for ir.IRModule`——这是最常见的报错来源。

### 第 2 步：建立四张映射表

# TVM FFI 动态类型系统：对象类型注册与 TypeTable 全解析

## 1. 引言

TVM FFI 的 ABI 承诺"稳定而又可扩展"：`TVMFFIObject` 的 24 字节头部永远冻结，但类型体系必须允许用户在运行时不断加入新类型。连接这对矛盾的枢纽，就是**对象类型注册机制**——它把每个 C++ 类映射为一个全局唯一的 `type_index`，记录其单继承关系与反射元数据，使 Python/Rust/编译器生成代码都能识别、校验和操作这些类型。

这套机制有两张面孔：面向用户的**注册流程**（C ABI + C++ 宏/反射 API），以及承载一切的运行时设施 **`TypeTable`**。本文将两者合并，给出一幅完整的图景。

## 2. 总体架构：TypeTable 作为单一事实来源

所有类型注册最终汇聚到 `src/ffi/object.cc` 中的进程级私有单例 `TypeTable`。它的类注释开宗明义地给出了并发约定：

```49:59:src/ffi/object.cc
/*!
 * \brief Global registry that manages
 *
 * \note We do not use mutex to guard updating of TypeTable
 *
 * The assumption is that updating of TypeTable will be done
 * in the main thread during initialization or loading, or
 * explicitly locked from the caller.
 *
 * Then the followup code will leverage the information
 */
```

**设计约定：初始化期注册（不加锁），运行期只读（零开销）。** 这一约定贯穿整个 tvm-ffi 的全局表设计。

### 2.1 双视图存储

```text
type_table_     : vector<unique_ptr<Entry>>   ← type_index 即下标，O(1) 查表
type_key2index_ : Map<String, int64_t>        ← type_key → type_index，幂等注册
```

`type_index` 直接作为 `type_table_` 的数组下标，这是 `TVMFFIGetTypeInfo` 能做到 O(1) 且标注 `TVM_FFI_ATTRIBUTE_PURE` 的根本原因。

### 2.2 Entry：ABI 视图与拥有型存储的叠加

每个类型条目 `Entry` 继承 ABI 结构 `TVMFFITypeInfo`，把"对外暴露的裸指针视图"叠在"内部真正拥有数据的容器"之上（`object.cc:63-116`）：

| Entry 自有字段（拥有数据）                                             | TypeInfo 基类字段（ABI 视图）       |
| ------------------------------------------------------------ | --------------------------- |
| `String type_key_data`                                       | `type_key`（指向前者的 data/size） |
| `vector<const TVMFFITypeInfo*> type_ancestors_data`          | `type_ancestors`            |
| `vector<TVMFFIFieldInfo> type_fields_data`                   | `fields`, `num_fields`      |
| `vector<TVMFFIMethodInfo> type_methods_data`                 | `methods`, `num_methods`    |
| `TVMFFITypeMetadata metadata_data`                           | `metadata`（未注册时为 `nullptr`） |
| `num_slots` / `allocated_slots` / `child_slots_can_overflow` | ——（槽位分配状态）                  |

这种配对带来一个必须小心的后果：vector 扩容会使基类指针失效，因此**每次 push_back 后都要刷新视图指针**（`entry->fields = entry->type_fields_data.data()`，`object.cc:264`）。

## 3. 注册的两层 API

### 3.1 C ABI 层：一切注册的最终落点

索引分配与查询：

```1487:1498:include/tvm/ffi/c_api.h
TVM_FFI_DLL int32_t TVMFFITypeGetOrAllocIndex(const TVMFFIByteArray* type_key,
                                              int32_t static_type_index, int32_t type_depth,
                                              int32_t num_child_slots,
                                              int32_t child_slots_can_overflow,
                                              int32_t parent_type_index);

TVM_FFI_DLL TVM_FFI_ATTRIBUTE_PURE const TVMFFITypeInfo* TVMFFIGetTypeInfo(int32_t type_index);
```

反射元数据注册（`c_api.h:1404-1434`）：

| API                          | 注册内容                                |
| ---------------------------- | ----------------------------------- |
| `TVMFFITypeRegisterField`    | 字段（名称、偏移、getter/setter、默认值）         |
| `TVMFFITypeRegisterMethod`   | 方法（含静态标记等 flags）                    |
| `TVMFFITypeRegisterMetadata` | 元数据（`total_size`、结构相等/哈希策略、creator） |
| `TVMFFITypeRegisterAttr`     | 开放属性列（按 type index 索引的任意附加信息）       |

这些 C 函数都是薄封装，直接转发到 `TypeTable::Global()`（如 `object.cc:588-597`）。

### 3.2 C++ 层：用户实际书写的代码

分**声明**与**注册**两步：

- **声明**：在类中写 `TVM_FFI_DECLARE_OBJECT_INFO("ffi.MyType", MyTypeObj, ParentObj)`，为类注入 `_type_key`、`_type_depth`、`RuntimeTypeIndex()` 等静态成员（`object.h:1109`）；不可被继承的类用 `TVM_FFI_DECLARE_OBJECT_INFO_FINAL`（额外固定 `_type_child_slots = 0`）。
- **注册**：在某个 `.cc` 文件中调用一次 `tvm::ffi::reflection::ObjectDef<MyTypeObj>()`，并可链式追加 `.def_ro(...)` / `.def(...)` 等字段方法定义。宏文档明确了这个约定：

```1097:1102:include/tvm/ffi/object.h
/*!
 * \brief Helper macro to declare object information with dynamic type index.
 *
 * For each custom object, you need to call tvm::ffi::reflection::ObjectDef<TypeName>()
 * once in your cc file to register the type index with the runtime.
```
