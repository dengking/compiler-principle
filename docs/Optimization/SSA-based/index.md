# SSA-based optimization

## SSA

| 名称                           | 说明                                                 |
| ---------------------------- | -------------------------------------------------- |
| **Vanilla SSA（Maximal SSA）** | 原始完整版本：所有交汇点全部插入$\phi$，满足支配性质；$\phi$最多。教材理论默认讲的就是它 |
| Pruned SSA（剪枝SSA）            | 只在**活跃变量**处插入$\phi$，减少phi节点数量，LLVM/GCC常用           |
| Semi-pruned SSA              | 折中方案，只在块入口活跃的变量插入phi                               |
| Minimal SSA                  | 只保证满足SSA基本约束，不保证支配性质（不属于vanilla SSA）               |

### Vanilla SSA

Vanilla SSA：基础版SSA / 原生SSA（标准静态单赋值形式），vanilla 在计算机术语里 = **原味、基础、未经扩展、标准原版**，没有额外变种/增强。

Vanilla SSA（标准SSA，strict SSA），满足两条核心性质：

1. 每个变量名**仅有一处静态定义**；
2. **支配性质（dominance property）**：**任何定义都支配它所有的使用**。
   这是最经典、最基础的SSA，也就是《SSA-based Compiler Design》书中定义的vanilla flavor SSA。

> 当控制流交汇时，在基本块开头插入 $\phi$ 函数（phi-node），用来选择来自不同前驱分支的值。

#### 关键要点

1. Vanilla SSA = **Maximal SSA**，是理论研究的基准版本；用支配前沿（dominance frontier）算法构建。
2. $\phi$ 函数**只允许放在基本块的起始位置**（vanilla SSA强制要求）。
3. 现代工业编译器（LLVM）**不是vanilla SSA**，是剪枝后的SSA，减少phi开销。
