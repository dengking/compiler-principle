# Global value numbering(GVN)

## GVN = Global Value Numbering(全局值编号)

GVN是编译器核心冗余消除优化算法，LLVM、MLIR、TVM、HotSpot C2（Sea of Nodes）全部标配Pass。

## 核心定义

给程序里**所有表达式/计算节点分配唯一编号（Value Number）**：

- 只要两个节点**语义等价、计算结果永远相同**，就分配同一个VN；
- 重复计算直接复用已有节点，删掉冗余运算；
- 跨整个控制流图CFG全局生效，不受单个基本块限制。

底层依赖**SSA**；Sea of Nodes图IR天然适配GVN，是SoN最核心优化循环。

## 二、核心工作原理

1. **标准化（Canonicalize）**
   交换律统一顺序：`a+b`、`b+a` 归一为同一种哈希形式；
   代数化简：`x*1`、`x+0` 直接归约为x。
2. **全局哈希注册表**
   键 = (操作符, 左操作数VN, 右操作数VN)
   查表：存在就复用旧节点；不存在新建并记录VN。
3. **等价替换**
   重复表达式全部替换为第一次计算的结果，消除重复指令。

### 最简示例

```c
int t1 = x + y;
int t2 = x + y;
```

GVN分配 `Add(VN(x), VN(y)) = #5`
`t2` 直接替换成 `t1`，删除第二条加法。

### 跨分支优势（普通局部CSE做不到）

```c
int a = 2;
if (cond) a = 2;
int res = a + 3;
```

GVN识别两条路径a恒等于2，`a+3` 直接折叠为常量5。

## 三、GVN 同时自带两大配套优化（你前面问过）

1. **Constant Propagation 常量传播**
   GVN注册表记录常量值，自动把常量沿数据流替换到所有使用点。
2. **Constant Folding 常量折叠**
   若算子所有输入VN都是常量，编译期直接算出常数，替换常量节点。

> 三者层级关系：
> GVN是顶层框架 → 内部包含常量传播 + 常量折叠；
> 传播负责“替换变量为常量”，折叠负责“常量表达式求值”。

## 四、GVN vs CSE（公共子表达式消除）

|         | GVN 全局值编号       | 传统CSE           |
| ------- | --------------- | --------------- |
| 匹配依据    | **语义等价**（值相等即可） | 文本完全相同          |
| 跨分支/Phi | 支持，SSA下全局分析     | 仅支配路径，弱         |
| 代数化简    | 内置交换律、单位元化简     | 无标准化，匹配能力差      |
| 常量处理    | 天然融合传播+折叠       | 仅处理重复表达式，不做常量推导 |

一句话：**GVN是更强、更通用的升级版CSE**。

## 五、GVN 在你关心的技术栈里的作用

### 1. HotSpot C2 Sea of Nodes

SoN没有基本块分割，整张节点图跑GVN循环（PhaseGVN）：

- 自动合并重复算术、消除冗余load；
- 常量传播+折叠、代数化简全在GVN阶段完成；
- 是SoN最核心、迭代次数最多的优化Pass。

### 2. LLVM / MLIR

LLVM独立`-gvn` Pass；MLIR各类Dialect（Linalg、Vector、RVV）都内置GVN：

- 消除重复张量计算、重复向量load/store；
- 向量化前化简冗余循环内表达式。

### 3. TVM Relay / TIR

Relay图优化、TIR循环优化均集成GVN：

- 消除重复卷积、重复广播、重复访存；
- 配合常量折叠简化量化、激活算子。

## 六、Local Value Numbering（LVN 局部值编号）补充

仅在**单个基本块**内做值编号，范围小、能力弱；GVN是LVN的全局扩展，工业编译器一律优先GVN。

## 一句话总结

GVN（全局值编号）是基于SSA/图IR的全局冗余消除算法，通过给等价表达式分配统一编号复用计算，同时内置常量传播、常量折叠，是Sea of Nodes、MLIR、TVM等现代AI/JIT编译器的基础优化。

## wikipedia [Value numbering](https://en.wikipedia.org/wiki/Value_numbering)

**Value numbering** is a technique of determining when two [computations](https://en.wikipedia.org/wiki/Computations "Computations") in a program are equivalent and eliminating one of them with a semantics-preserving [optimization](https://en.wikipedia.org/wiki/Compiler_optimization "Compiler optimization").
