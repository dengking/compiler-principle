# tvm_ffi_header

这三行在 `CMakeLists.txt:36-42` 定义了一个名为 `tvm_ffi_header` 的 **INTERFACE 库（纯头文件目标）**。逐行解释：

## 逐行含义

**第 1 行：`add_library(tvm_ffi_header INTERFACE)`**

声明一个 **INTERFACE 库**——一种不产生任何构建产物（没有 `.a`/`.so`）的"虚拟目标"，它唯一的用途是**携带使用要求（usage requirements）**：头文件搜索路径、编译特性、宏定义等。注释说明了动机：

```38:40:CMakeLists.txt
# they can be used in cases where user do not want to link into the library in cases like deferred
# linking
```

即：有些用户（例如编译器 codegen 产出的 kernel 库）只需要 tvm-ffi 的**头文件**来按 ABI 约定导出 `__tvm_ffi_*` 符号，运行时才被宿主加载（延迟链接/符号在宿主侧解析），**不希望也不应该链接 `libtvm_ffi`**。这个 INTERFACE 目标就是为这种"只要头文件"的场景准备的。

**第 2 行：`add_library(tvm_ffi::header ALIAS tvm_ffi_header)`**

为目标创建**命名空间别名** `tvm_ffi::header`。两个作用：

1. **构建树与安装树用法统一**：包被 `install(EXPORT)` 导出后，下游通过 `find_package(tvm_ffi)` 拿到的名字就是 `tvm_ffi::header`。有了 ALIAS，无论是在本项目内部、以 `add_subdirectory` 引入、还是安装后使用，链接写法都是同一个 `target_link_libraries(foo PRIVATE tvm_ffi::header)`，无需区分来源。
2. **防拼写错误**：带 `::` 的名字若不是目标，CMake 会在配置期直接报错，而不是静默地当成 `-ltvm_ffi::header` 传给链接器。

**第 3 行：`target_compile_features(tvm_ffi_header INTERFACE cxx_std_17)`**

把"需要 C++17"声明为该目标的 **INTERFACE 属性**（纯传播，自身不参与编译，因为本来就没有源文件）。效果是：任何链接 `tvm_ffi_header` 的目标会自动获得"至少用 C++17 编译"的要求，CMake 会为其选择满足要求的标准（若消费者已是 C++20 则保持 C++20）。这比设置全局 `CMAKE_CXX_STANDARD` 更精确——要求跟着目标走，不污染整个工程。这与项目约定（AGENTS.md 中的 "C++17 API"）一致。

## 它在整个构建中的角色

同一个文件随后往这个目标上挂了更多 INTERFACE 属性（均以同样的方式传播给消费者）：

- 端序宏 `TVM_FFI_CMAKE_LITTLE_ENDIAN`（`CMakeLists.txt:44-50`）；
- 头文件路径 `include/` 与 `3rdparty/dlpack/include`，并用 `$<BUILD_INTERFACE:...>` / `$<INSTALL_INTERFACE:include>` 区分构建树与安装树的路径（`CMakeLists.txt:52-59`）。

然后项目内的真实产物目标通过链接它来继承这些要求：

```163:165:CMakeLists.txt
target_link_libraries(tvm_ffi_objs PUBLIC tvm_ffi_header)
target_link_libraries(tvm_ffi_shared PUBLIC tvm_ffi_header)
target_link_libraries(tvm_ffi_static PUBLIC tvm_ffi_header)
```

`PUBLIC` 意味着：这些库**自己编译时**会用上 include 路径和 C++17，同时把这些要求**继续传递给它们的下游**——于是任何 `target_link_libraries(my_lib PRIVATE tvm_ffi::shared)` 的外部项目也会自动获得正确的头文件路径与 C++ 标准，形成一条完整的传递链。

## 一句话总结

这三行创建了一个**不产出二进制、只携带"头文件路径 + C++17 要求 + 宏定义"的接口目标 `tvm_ffi::header`**：对内，它是 `tvm_ffi_objs/shared/static` 公共编译要求的单一来源；对外，它让只需头文件即可对接 ABI 的下游（如延迟链接的 kernel 库）可以零成本接入，而不必链接整个 `libtvm_ffi`。
