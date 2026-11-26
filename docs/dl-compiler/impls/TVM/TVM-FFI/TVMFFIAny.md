# [struct TVMFFIAny](https://github.com/apache/tvm-ffi/blob/main/include/tvm/ffi/c_api.h)

TVMFFIAny 深度剖析：16 字节如何撑起一个跨语言、跨平台的稳定 C ABI

## 1. 引言

在 Apache TVM FFI 中，所有跨语言传递的值——无论是整数、浮点、指针、张量，还是堆上的引用计数对象——最终都要装进同一个容器：`TVMFFIAny`。它是整个 FFI 系统的"通用货币"：Python 调用 C++ 注册的函数时参数是它，编译器 codegen 生成 LLVM IR 时操作的也是它。

官方文档对它的定位非常精炼：

> `TVMFFIAny` 是一个 **16 字节的 tagged union**，可以持有 FFI 系统识别的任意值，实现跨语言边界的类型擦除值传递。

这 16 个字节看似简单，实则每一处设计都在回答三个难题：

1. **内存布局如何紧凑高效？**

2. **ABI 如何在编译器演进中保持稳定？**

3. **布局如何在 32/64 位、不同编译器间完全一致（cross platform compatibility）？** 

本文以 `include/tvm/ffi/c_api.h` 中的源码为准，逐一拆解。

## 2. 内存布局：三段式 16 字节

`TVMFFIAny` 的完整定义如下：

```c
typedef struct {
  /*!
   * \brief type index of the object.
   * \note The type index of Object and Any are shared in FFI.
   */
  int32_t type_index;
  union {  // 4 bytes
    /*! \brief padding, must set to zero for values other than small string. */
    uint32_t zero_padding;
    /*!
     * \brief Length of small string, with a max value of 7.
     *
     * We keep small str to start at next 4 bytes to ensure alignment
     * when accessing the small str content.
     */
    uint32_t small_str_len;
  };
  union {  // 8 bytes
    /*! \brief integers */
    int64_t v_int64;
    /*! \brief floating-point numbers */
    double v_float64;
    /*! \brief typeless pointers */
    void* v_ptr;
    /*! \brief raw C-string */
    const char* v_c_str;
    /*! \brief ref counted objects */
    TVMFFIObject* v_obj;
    /*! \brief data type */
    DLDataType v_dtype;
    /*! \brief device */
    DLDevice v_device;
    /*! \brief small string */
    char v_bytes[8];
    /*! \brief uint64 repr mainly used for hashing */
    uint64_t v_uint64;
  };
} TVMFFIAny;
```

其内存布局可以画成：

```text
offset 0 ┌─────────────────────────────┐
         │ int32_t type_index          │  4 字节：类型标签
offset 4 ├─────────────────────────────┤
         │ union {                     │  4 字节：辅助字段
         │   uint32_t zero_padding     │   ├─ 普通值：必须为 0
         │   uint32_t small_str_len    │   └─ 小字符串：长度（≤7）
         │ }                           │
offset 8 ├─────────────────────────────┤
         │ union {                     │  8 字节：值负载（payload）
         │   int64_t      v_int64      │
         │   double       v_float64    │
         │   void*        v_ptr        │
         │   const char*  v_c_str      │
         │   TVMFFIObject* v_obj       │
         │   DLDataType   v_dtype      │
         │   DLDevice     v_device     │
         │   char         v_bytes[8]   │
         │   uint64_t     v_uint64     │
         │ }                           │
         └─────────────────────────────┘
sizeof(TVMFFIAny) = 16，alignof = 8
```

即：

$$
\text{sizeof}(\texttt{TVMFFIAny}) = \underbrace{4}_{\text{type\_index}} + \underbrace{4}_{\text{aux union}} + \underbrace{8}_{\text{value union}} = 16 \text{ bytes}
$$

### 2.1 第一字段：type_index——不依赖 RTTI 的运行时类型系统

`type_index` 是整个 ABI 的判别标签（tag），取值来自 `TVMFFITypeIndex` 枚举，设计上分为三段区间：

- **$[0, 64)$：栈上 POD 类型**。如 `kTVMFFIInt = 1`、`kTVMFFIFloat = 3`、`kTVMFFISmallStr = 11`、`kTVMFFISmallBytes = 12`。值直接内联在 payload union 中，无堆分配、无引用计数。
- **$[64, 128)$：静态对象类型**。`kTVMFFIStaticObjectBegin = 64` 起，预留给框架内置对象（String、Bytes、Error、Function、Shape、Tensor、Array、Map、Module……）。
- **$[128, +\infty)$：动态类型**。`kTVMFFIDynObjectBegin = 128` 起的类型索引在运行时通过 `TVMFFITypeGetOrAllocIndex` 分配，支撑用户自定义类型的单继承体系。

一个关键设计原则是：**这套类型系统完全不依赖 C++ RTTI**。`type_index` 同时出现在 `TVMFFIAny` 和 `TVMFFIObject` 头部且语义共享（"The type index of Object and Any are shared in FFI"），使得"Any 里的指针指向的对象"与"Any 本身"可以用同一套编号体系校验，跨编译单元的类型检查退化为一次整数比较。

### 2.2 中间的 4 字节 union：被"变废为宝"的填充字节

这是整个布局中最精妙的一处。注意到 8 字节的值 union 含 `int64_t`、`double`、指针等成员，**必须 8 字节对齐**，因此它只能位于 offset 8。而 `type_index` 只有 4 字节——中间这 4 字节无论如何都会被对齐规则"吃掉"。

设计的第一个决策是：**不把这 4 字节交给编译器隐式填充，而是显式声明为一个 union**，一举四得：

**（a）跨平台布局确定性。** 如果依赖隐式填充，布局的正确性就押注在"所有编译器都按同样规则填充"上。显式声明后，任何平台上 offset 都是写死的，这正是 ABI 稳定性的基本要求。

**（b）小字符串优化（SSO）。** 这 4 字节不是死空间，它承载 `small_str_len`——长度不超过 7 的短字符串/短字节串直接把内容存进下一个 union 的 `v_bytes[8]`，完全免去堆分配。源码注释点明了为什么内容必须从 offset 8 开始：

```c
     * \brief Length of small string, with a max value of 7.
     *
     * We keep small str to start at next 4 bytes to ensure alignment
     * when accessing the small str content.
```

7 字节内容 + 结尾 `\0` 恰好 8 字节，对齐到 8 字节边界后可以按**单个机器字**整体读写。文档还补充了一个反向的取舍说明："To favor 8-byte alignment (v_bytes) and keep things simple, we did not further pack characters into the `small_len` field"——宁愿不把字符进一步压缩进长度字段，也要保住 8 字节对齐和布局的简单性。

**（c）单次机器字比较与哈希。** ABI 规定一条强不变式：**除小字符串外，`zero_padding` 必须置 0**。有了它，`(type_index, zero_padding)` 恰好拼成一个 8 字节字，`v_uint64` 是另一个 8 字节字——两个 Any 的相等性判断就是两次 64 位整数比较。C++ 侧的 `same_as` 正是如此实现：

```c
  TVM_FFI_INLINE bool same_as(const Any& other) const noexcept {
    return data_.type_index == other.data_.type_index &&
           data_.zero_padding == other.data_.zero_padding && data_.v_int64 == other.data_.v_int64;
  }
```

**（d）为什么不能做成 8 字节？** 那样结构会变成 $4 + 4(\text{pad}) + 8 + 8 = 24$ 字节，既浪费栈空间，又破坏了 16 字节的紧凑性——16 字节在 64 位平台上恰好可用两个寄存器完成传参和返回，这对高频的 FFI 调用开销至关重要。

### 2.3 8 字节值 union：一切负载的归宿

值 union 的成员覆盖了 FFI 需要传递的全部值形态：

| 成员                     | 用途                              | 典型 type_index                           |
| ---------------------- | ------------------------------- | --------------------------------------- |
| `v_int64`              | 整数（含 bool）                      | `kTVMFFIInt` / `kTVMFFIBool`            |
| `v_float64`            | 浮点                              | `kTVMFFIFloat`                          |
| `v_ptr` / `v_c_str`    | 不透明指针 / 原始 C 字符串                | `kTVMFFIOpaquePtr` / `kTVMFFIRawStr`    |
| `v_obj`                | 堆上引用计数对象                        | $\geq$ `kTVMFFIStaticObjectBegin`       |
| `v_dtype` / `v_device` | DLPack 数据类型 / 设备（均 $\leq$ 8 字节） | `kTVMFFIDataType` / `kTVMFFIDevice`     |
| `v_bytes[8]`           | 小字符串/小字节串内容                     | `kTVMFFISmallStr` / `kTVMFFISmallBytes` |
| `v_uint64`             | 哈希/比较用的统一 64 位视图                | ——                                      |

`v_uint64` 的存在尤为值得注意：它让哈希实现可以把任意 Any 的值部分统一按 `uint64_t` 读取，配合前述 zero-padding 不变式，哈希与相等性判断都无需关心实际存储的是指针还是数值。

## 3. 稳定的 C ABI：靠"约定"而非"编译器"

TVM FFI 的 ABI 设计原则中明确写着：**"The ABI remains stable across compiler versions and is independent of host languages or frameworks."** `TVMFFIAny` 从四个方面兑现了这条承诺。

### 3.1 纯 C、纯 POD、显式定宽类型

整个结构只含固定宽度整数（`int32_t`、`uint32_t`、`int64_t`、`uint64_t`）、`double`、指针和 C union——没有任何 C++ 特有构造（无类成员函数、无模板、无 `std::string`/`std::vector` 这类布局不受 ABI 约束的标准库类型）。文档特意强调 "C code is used for clarity, precision and friendliness to compiler builders"，因为这样的定义可以直接翻译成 LLVM IR builder 等代码生成器的操作。

### 3.2 不透明句柄隔离堆对象

堆对象在 C API 视角下只是 `typedef void* TVMFFIObjectHandle`，生命周期通过 `TVMFFIObjectIncRef` / `TVMFFIObjectDecRef` 显式管理，销毁通过对象头里的 `deleter` 函数指针完成。这意味着：**对象的实际类型、构造函数、析构逻辑全部隐藏在 ABI 边界之后**，两侧可以用不同编译器、不同版本编译，只要遵守同一套 C 约定即可互操作。

### 3.3 统一的函数调用约定

所有跨边界函数遵循同一个签名：

```c
typedef int (*TVMFFISafeCallType)(void* handle, const TVMFFIAny* args, int32_t num_args,
                                  TVMFFIAny* result);
```

参数是 `TVMFFIAny` 数组（借用语义，即 AnyView），返回值通过 `result` 输出（拥有语义，即 Any），错误经返回码 + TLS 传播。由于 `TVMFFIAny` 布局恒定，这条调用约定对任何宿主语言都可绑定。

### 3.4 同一布局，两种所有权语义

一个颇有匠心的设计：C++ 侧的 `Any`（拥有，管理引用计数）与 `AnyView`（借用，不拥有）**共享完全相同的 `TVMFFIAny` 内存布局**，区别只在语义。借用转拥有有专门的 C API `TVMFFIAnyViewToOwnedAny`。布局与语义解耦，让 ABI 边界上只传布局、不传语义，两侧的 RAII 包装各管各的生命周期。

## 4. Cross Platform Compatibility：每一字节都写死在布局里

`TVMFFIObject` 头部有一处耐人寻味的成员，其注释直接点题：

```c
    /*!
     * \brief auxilary field to TVMFFIObject is always 8 bytes aligned.
     * \note This helps us to ensure cross platform compatibility.
     */
    int64_t __ensure_align;
```

"Ensure cross platform compatibility" 在这套 ABI 中不是一句口号，而是一组具体的布局技术：

**（1）用显式字段取代隐式填充。** `TVMFFIAny` 的 `zero_padding`、`TVMFFIObject` 的 `uint32_t __padding` 与 `int64_t __ensure_align`，都是同一手法：凡是可能因对齐产生填充的位置，都用有名字的定宽字段显式占住。这样结构体的 offset 表在所有平台、所有编译器下逐字节一致，不存在"这个编译器多填了 4 字节"的灰色地带。`__ensure_align` 还顺带保证了对象头之后紧跟的 payload 永远 8 字节对齐。

**（2）杜绝平台相关宽度类型。** ABI 结构中不出现 `long`、`size_t` 这类随平台变宽的 PaxHeader 类型（`TVMFFIByteArray` 是少数例外，且其注释明确说明 32/64 位布局不同、刻意遵循指针大小以与 `std::string` 惯例保持一致）。定宽类型让 `sizeof` 和 `offsetof` 成为跨平台常量。

**（3）union 尺寸由定宽成员锚定。** 值 union 中 `v_bytes[8]` 与 `v_uint64` 的存在，把 union 大小锚定在 8 字节——即使在 32 位平台上指针只有 4 字节，union 也不会缩水，`TVMFFIAny` 仍然是 16 字节。

**（4）32 位指针的残位清零。** 值 union 里存 4 字节指针时，高 4 字节在 32 位平台上是不确定的，这会破坏前述"按机器字比较/哈希"的不变式。为此 C++ 侧提供了专用宏：

```c
/*!
 * \brief Clear the padding parts so we can safely use v_int64 for hash
 *        and equality check even when the value stored is a pointer.
 *
 * This macro is used to clear the padding parts for hash and equality check
 * in 32bit platform.
 */
#define TVM_FFI_CLEAR_PTR_PADDING_IN_FFI_ANY(result) \
  if constexpr (sizeof(void*) != sizeof(int64_t)) {  \
    (result)->v_int64 = 0;                           \
  }
```

所有写入指针的路径（如 `CopyToAnyView`、`MoveToAnyImpl`）都会调用它，保证 32 位平台上的哈希/比较语义与 64 位完全一致。

**（5）字节序也写进契约。** `TVMFFIObject` 的 `combined_ref_count`（强/弱引用计数打包进一个 `uint64_t`）注释中明确指出其位布局等价于小端下的 `{ strong, weak }`，并说明这样设计是为了让强引用计数的原子操作退化为 `+1/-1`、删除时只需一次 u64 原子读——**连位级布局都成了 ABI 文档的一部分**，这正是"稳定 ABI"与"实现细节"的根本区别。

## 5. 结语

`TVMFFIAny` 的 16 字节可以被看作一份"跨语言值的宪法"：

- **布局上**，三段式结构（4 + 4 + 8）把对齐必然产生的填充字节变成了小字符串长度字段，用两条不变式（zero-padding、8 字节对齐的 SSO 内容）换来了单机器字的比较与哈希；
- **ABI 稳定性上**，纯 C + POD + 定宽类型 + 不透明句柄 + 统一调用约定，让不同编译器、不同版本、不同语言编译出的二进制可以安全互操作，且不依赖 C++ RTTI；
- **跨平台兼容性上**，每一个可能因平台而异的字节——填充、对齐、指针残位、union 尺寸——都被显式字段或宏钉死，"layout-stable" 成为可验证的属性而非经验之谈。

对任何需要设计跨语言 FFI 的项目而言，这个 16 字节的结构都是一个值得反复研读的范本：**ABI 的稳定性，归根结底是把所有"编译器可能自由发挥"的地方全部变成显式约定。**
