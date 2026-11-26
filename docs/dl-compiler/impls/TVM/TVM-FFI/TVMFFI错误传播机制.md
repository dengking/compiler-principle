# TVM FFI 错误传播机制：基于 TLS 的跨语言异常通道设计

## 1. 引言

跨语言 FFI 调用中，错误处理是最棘手的问题之一：C++ 有异常、Python 有 traceback、C 只有返回码，而 ABI 边界上**不允许抛出 C++ 异常**（不同编译器/运行时的异常机制互不兼容，越界抛出即未定义行为）。TVM FFI 给出的方案是：**统一的整型返回码 + 线程局部存储（TLS）中的错误对象**。本文解读这套机制的设计动机、协议细节与实现方式。

## 2. TLS 是什么

**TLS（Thread-Local Storage，线程局部存储）** 是一种让每个线程各自持有独立变量副本的存储机制：

- C++11：`thread_local` 关键字
- C11：`_Thread_local` 关键字
- 底层由操作系统与运行时协同实现（如 ELF 平台的 `__tls_get_addr`、Windows 的 `TlsAlloc` 家族）

对同一变量名，线程 A 写入的值对线程 B 不可见，且无需任何加锁。这一性质使它成为"每线程上下文"的天然载体——errno 就是最经典的先例。

## 3. 错误传播协议：返回码 + TLS 旁路

### 3.1 统一约定

TVM FFI 中所有可能失败的 C API 遵循同一个返回码约定：

```485:487:include/tvm/ffi/c_api.h
 *  Possible return error of the API functions:
 *  * 0: success
 *  * -1: error happens, can be retrieved by TVMFFIErrorMoveFromRaised
```

问题在于：$-1$ 只表达了"出错了"，错误的种类、消息、回溯（backtrace）这些信息放哪？答案是**当前线程的 TLS 槽位**——错误不走参数也不走返回值，而是走一条"旁路通道"（side channel）。

### 3.2 三个核心 API

```749:768:include/tvm/ffi/c_api.h
/*!
 * \brief Move the last error from the environment to the result.
 * \param result The result error.
 * \note This function clears the error stored in the TLS.
 */
TVM_FFI_DLL void TVMFFIErrorMoveFromRaised(TVMFFIObjectHandle* result);

/*!
 * \brief Set a raised error in TLS, which can be fetched by TVMFFIErrorMoveFromRaised.
 * \param error The error object handle
 */
TVM_FFI_DLL void TVMFFIErrorSetRaised(TVMFFIObjectHandle error);

/*!
 * \brief Set a raised error in TLS, which can be fetched by TVMFFIErrorMoveFromRaised.
 * \param kind The kind of the error.
 * \param message The error message.
 * \note This is a convenient method for the C API side to set an error directly from a string.
 */
TVM_FFI_DLL int TVMFFIErrorSetRaisedFromCStr(const char* kind, const char* message);
```

三个 API 构成完整的写/读闭环：

| API                            | 方向  | 语义                                                        |
| ------------------------------ | --- | --------------------------------------------------------- |
| `TVMFFIErrorSetRaised`         | 写   | 把已构造好的 Error 对象放入 TLS                                     |
| `TVMFFIErrorSetRaisedFromCStr` | 写   | 便捷入口：直接用 C 字符串构造 Error 放入 TLS（另有多段拼接版 `...FromCStrParts`） |
| `TVMFFIErrorMoveFromRaised`    | 读   | 把 TLS 中的错误**移动**给调用方，同时清空 TLS 槽位                          |

注意 `MoveFromRaised` 的两个细节：所有权随调用转移给调用方（用完需 `TVMFFIObjectDecRef`）；读取即清空，保证"一个错误只被消费一次"，避免陈旧错误污染后续调用。

### 3.3 完整工作流程

```text
被调方（callee）                    调用方（caller）
─────────────────                  ─────────────────
出错
  ↓
TVMFFIErrorSetRaisedFromCStr(
    "ValueError", "...")
  ↓ 写入本线程 TLS
return -1               ──────►   收到 ret == -1
                                    ↓
                                  TVMFFIErrorMoveFromRaised(&err)
                                    ↓ 从本线程 TLS 取出并清空
                                  读取 kind/message/backtrace
                                    ↓
                                  TVMFFIObjectDecRef(err)
```

错误对象本身是一个标准的 TVM FFI 对象（`kTVMFFIError = 67`），其 payload 为 `TVMFFIErrorCell`，包含 kind、message、backtrace、原因链（cause chain）与额外上下文：

```430:465:include/tvm/ffi/c_api.h
typedef struct {
  /*! \brief The kind of the error. */
  TVMFFIByteArray kind;
  /*! \brief The message of the error. */
  TVMFFIByteArray message;
  ...
  TVMFFIObjectHandle cause_chain;
  /*! \brief Optional extra context ... */
  TVMFFIObjectHandle extra_context;
} TVMFFIErrorCell;
```

这意味着**所有语言的错误（C++ 异常、Python 异常）都会被翻译成同一种 Error 对象**——TLS 通道上流通的是统一格式，调用方可以用一套代码处理来自任何语言的失败。

## 4. 实现：`SafeCallContext` 与 `thread_local`

TLS 槽位的实现位于 `src/ffi/error.cc`，核心是一个每线程单例：

```67:70:src/ffi/error.cc
  static SafeCallContext* ThreadLocal() {
    static thread_local SafeCallContext ctx;
    return &ctx;
  }
```

`SafeCallContext` 内部以 `ObjectPtr<ErrorObj>` 持有最近一个错误，三个 C API 都是对它的薄封装：

```92:98:src/ffi/error.cc
void TVMFFIErrorSetRaised(TVMFFIObjectHandle error) {
  tvm::ffi::SafeCallContext::ThreadLocal()->SetRaised(error);
}

void TVMFFIErrorMoveFromRaised(TVMFFIObjectHandle* result) {
  tvm::ffi::SafeCallContext::ThreadLocal()->MoveFromRaised(result);
}
```

C++ 侧的宏 `TVM_FFI_SAFE_CALL_BEGIN/END` 在 ABI 边界自动完成"catch 所有 C++ 异常 → 构造 Error → SetRaised → return -1"的转换，这就是 `TVMFFISafeCallType` 中 "Safe call explicitly catches exception on function boundary" 的含义。同样的 TLS 手法也用于 backtrace 字符串缓冲（`backtrace.cc`）与环境上下文（`EnvContext`），是贯穿整个运行时的惯用法。

## 5. 设计权衡：为什么是 TLS

`c_api.h` 的注释坦率地记录了这项决策的收益与代价：

```489:494:include/tvm/ffi/c_api.h
 * \note We decided to leverage TVMFFIErrorMoveFromRaised and TVMFFIErrorSetRaised
 *  for C function error propagation. This design choice, while
 *  introducing a dependency for TLS runtime, simplifies error
 *  propgation in chains of calls in compiler codegen.
 *  As we do not need to propagate error through argument but simply
 *  set them in the runtime environment.
```

**收益一：线程安全且无锁。** 这是必须 TLS 而非全局变量的根本原因。FFI 调用在多线程下并发发生，若错误存全局变量，两个线程的错误会互相覆盖，加锁又会引入竞争与死锁风险。TLS 让"每线程一个错误槽"的语义天然成立，零同步开销。

**收益二：极大简化 codegen 的错误传播。** TVM FFI 的重要使用方是编译器——生成的代码中 FFI 调用层层嵌套。若错误通过出参传播，每层调用都要增加一个错误参数、逐层检查并转发，生成的 IR 会显著膨胀。TLS 方案下，被调方"往环境里一扔"，返回码 $-1$ 沿调用链自然向上冒泡，最外层统一取一次即可。

**收益三：调用约定保持干净。** `TVMFFISafeCallType` 的签名得以固定为 $(\texttt{handle}, \texttt{args}, \texttt{num\_args}, \texttt{result})$ 四参数，错误通道完全正交于参数/返回值通道，任何宿主语言都易于绑定。

**代价：依赖 TLS 运行时。** 使用方必须处于支持 TLS 的环境——对 Linux/macOS/Windows 等主流平台这不是问题，但对某些极端嵌入式或 freestanding 环境，这是一个需要显式考量的依赖。这也是注释中 "introducing a dependency for TLS runtime" 一句的由来。

## 6. 与 ABI 其他部分的呼应

TLS 错误通道并非孤立设计，它与前述 ABI 构件环环相扣：

- **错误即对象**：Error 以 `TVMFFIObject` 为头、引用计数管理，跨语言传递复用同一套所有权协议；
- **读取即清空**：`MoveFromRaised` 的 move 语义与 `Any` 的拥有/借用二分一致——TLS 槽位相当于一个持有所有权的 `Any`；
- **返回码约定统一**：`TVMFFIObjectIncRef/DecRef`、`TVMFFIFunctionCall` 等所有 API 共享 $0/-1$ 约定，调用方只需一套检查逻辑；
- **`TVMFFIErrorCreate` 的例外**：作为错误处理循环自身使用的 API，它刻意**不**在失败时写 TLS（注释见 `c_api.h:804-807`），否则"处理错误时出错"会递归污染错误通道——这是协议设计者对边界情形的自觉。

## 7. 结语

TLS 在 TVM FFI 中扮演的角色可以概括为一句话：**把"异常"这种控制流信息，编码为"每线程环境"中的数据，从而安全穿越不允许异常存在的 ABI 边界**。它用极小的机制（一个 `thread_local` 槽位 + 三个 C 函数）同时满足了四个约束：跨语言可用、多线程安全、对 codegen 友好、不污染调用签名——是稳定 ABI 设计中"以约定代替机制"的又一范例。
