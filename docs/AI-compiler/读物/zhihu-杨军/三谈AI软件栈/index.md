# zhihu [三谈AI软件栈](https://zhuanlan.zhihu.com/p/408783175)



目前MLIR的工作中，真正复用程度高的，确实是以core developer开发的模块为主。比如

- 图优化pass。一些具体的示例：

- [别名分析](https://link.zhihu.com/?target=https%3A//github.com/llvm/llvm-project/blob/main/mlir/lib/Analysis/AliasAnalysis.cpp)/[Liveness Analysis](https://link.zhihu.com/?target=https%3A//github.com/llvm/llvm-project/blob/main/mlir/lib/Analysis/Liveness.cpp)/[Inliner](https://link.zhihu.com/?target=https%3A//github.com/llvm/llvm-project/blob/main/mlir/lib/Transforms/InlinerPass.cpp)/[LICM](https://link.zhihu.com/?target=https%3A//github.com/llvm/llvm-project/blob/main/mlir/lib/Transforms/LoopInvariantCodeMotion.cpp)/[SCCP](https://link.zhihu.com/?target=https%3A//github.com/llvm/llvm-project/blob/main/mlir/lib/Transforms/SCCP.cpp)/[DCE](https://link.zhihu.com/?target=https%3A//github.com/llvm/llvm-project/blob/main/mlir/lib/Transforms/SymbolDCE.cpp)/[CSE](https://link.zhihu.com/?target=https%3A//github.com/llvm/llvm-project/blob/main/mlir/lib/Transforms/CSE.cpp)/[Dominance Analysis](https://link.zhihu.com/?target=https%3A//github.com/llvm/llvm-project/blob/main/mlir/lib/IR/Dominance.cpp)

- 基础工具

- [Lexer](https://link.zhihu.com/?target=https%3A//github.com/llvm/llvm-project/blob/main/mlir/lib/Parser/Lexer.cpp)/[Parser](https://link.zhihu.com/?target=https%3A//github.com/llvm/llvm-project/blob/main/mlir/lib/Parser/Parser.cpp)/[FileCheck](https://link.zhihu.com/?target=https%3A//github.com/llvm-mirror/llvm/blob/master/utils/FileCheck/FileCheck.cpp)/[TableGen](https://link.zhihu.com/?target=https%3A//github.com/llvm/llvm-project/tree/main/mlir/lib/TableGen)/Error Location Tracker

- Core dialects

- [Standard](https://link.zhihu.com/?target=https%3A//github.com/llvm/llvm-project/tree/main/mlir/include/mlir/Dialect/StandardOps)/[Tensor](https://link.zhihu.com/?target=https%3A//github.com/llvm/llvm-project/tree/main/mlir/include/mlir/Dialect/Tensor)/[Shape](https://link.zhihu.com/?target=https%3A//github.com/llvm/llvm-project/tree/main/mlir/include/mlir/Dialect/Shape)/[MemRef](https://link.zhihu.com/?target=https%3A//github.com/llvm/llvm-project/tree/main/mlir/include/mlir/Dialect/MemRef)


