# Vectorization

素材:

[How to optimize GEMM on CPU](https://daobook.github.io/tvm/docs/how_to/optimize_operators/opt_gemm.html)

https://www.doubao.com/docx/LNsHd8Ja2oi5ZExNND2cOuEQnpd 

[What is vectorization and is it a just hint?](https://discuss.tvm.apache.org/t/what-is-vectorization-and-is-it-a-just-hint/10606) 

[Enhancing TVM VTA Simulator Performance Through SIMD Vectorization](https://ieeexplore.ieee.org/document/10547748)

本文通过 SIMD（单指令多数据）向量化技术，对 TVM VTA（通用张量加速器，Versatile Tensor Accelerator）的模拟器性能进行优化提升。文章首先对 VTA 模拟器展开分析，定位出完整执行链路中的性能瓶颈；在此基础上，借助 ARM Neon、ARM SVE 两款 SIMD 指令集架构（ISA），对 VTA 模拟器的热点代码进行优化，实现路径分别采用了 SIMD 内建函数与内联汇编两种方案。

我们在搭载 SIMD 指令的通用 CPU 平台上，对所提优化方案的执行性能进行了评测。实验结果表明，针对测试基准程序集，SIMD 技术可显著提升 VTA 模拟器的执行效率，最高加速比可达 2.27 倍。


