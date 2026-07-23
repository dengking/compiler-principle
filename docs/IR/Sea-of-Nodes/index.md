# Sea of nodes(节点海洋，简称SoN)

**Sea of Nodes** 是一种**JIT即时编译器专用的中间表示IR**，由 Cliff Click 在1995年为HotSpot服务端编译器（C2）发明，现在广泛用于：

- JVM HotSpot C2 编译器
- GraalVM Graal 编译器
- V8引擎 TurboFan（JavaScript）
- 各类高性能语言JIT（Rust、Lua等自研JIT）

核心思想：**把控制流图CFG + 数据流DFG合并成一张统一无区块限制的节点图**，抛弃传统基本块（Basic Block）结构。

## 传统IR vs Sea of Nodes

### 传统编译器两段分离模型

1. **控制流图CFG**：代码切分成多个基本块，分支/跳转连接块，强制指令绑定在块内固定顺序；
2. **数据流DFG（SSA）**：每个值用唯一变量表示，依附在对应基本块；
   缺陷：无副作用运算会被块边界限制，跨块优化、重排、常量传播难度大。

### Sea of Nodes 统一图模型

所有运算、值、分支、内存操作全部抽象为**Node节点**，边分两类：

- **数据边（Value Edge）**：表示输入依赖（a+b中a、b是加法节点的数据输入）；

- **控制边（Control Edge）**：仅带副作用操作才有（存储store、函数调用call、分支if、循环跳转），标记执行时序约束。
     

关键特性：

- **无副作用节点自由漂浮**：算术、常量、纯函数节点不受基本块束缚，只要输入就绪就能任意重排、合并、消除；
- **图改写式优化**：优化器直接对节点图做局部匹配替换（常量折叠、公共子表达式消除CSE、循环不变量外提、逃逸分析），不用跨块分析；
- **调度后置**：全部优化完成后，调度器Scheduler才把节点打包分配到基本块、生成机器码。

## 核心优势

1. **优化粒度更细、收益更高**
   纯计算节点不受块边界阻隔，全局值编号GVN、常量传播、死代码删除几乎无额外开销；循环优化、向量化、内联效果远优于**块式IR**。
2. **分支/循环优化天然友好**
   if、loop仅靠控制边约束，容易做分支预测、循环展开、循环剥离、条件常量传播。
3. **内存别名分析简化**
   读写内存节点带控制依赖，可快速区分“只读无冲突”运算，大幅提升内存优化效率。
4. **适配动态语言JIT**
   JS、Java动态类型、多态调用频繁，SoN图结构方便做类型特化、去虚调用、投机优化。

## 典型执行流程（SoN编译流水线）

1. 前端AST/字节码 → 生成原始Sea of Nodes图；

2. 迭代图优化循环：GVN、常量折叠、死节点消除、内联、循环优化、逃逸分析；

3. 插入屏障、内存模型约束节点；

4. **调度（Schedule）**：将漂浮节点按控制约束分组为基本块、排定指令顺序；

5. 寄存器分配、生成机器码。

## 易混淆概念区分

### 1. Sea of Nodes ≠ Node.js SEA

   Node.js SEA = Single Executable Application，是Node单文件可执行打包工具，和编译器IR无关，只是缩写撞名。

### 2. Sea of Nodes ≠ SSA

SSA是值的命名规则（每个赋值唯一变量）；Sea of Nodes是**图组织结构**，SoN内部普遍使用SSA形式，但二者不是同一层级概念。

## 简单示例直观理解

   代码：

```java
int f(int x) {
int a = x + 2;
int b = a * 3;
if (b > 10) return b;
return a;
}
```

- 传统IR：拆成2个基本块（if真/if假），a、b被绑定在入口块；
- SoN：
  - `x`、`2`、`3`、`+`、`*`、`10`、`>` 都是纯数据节点，无控制边，自由漂浮；
  - `if分支节点`、`return`节点带控制边，限定时序；
  - 优化器可直接识别 `x*3+6` 合并计算，不受if块边界阻挡。

## 用与不适用场景

### 适合

- 高性能服务端JIT、动态语言虚拟机、需要重度全局优化的编译器；

### 不适合

- 快速AOT编译器、资源受限嵌入式轻量编译器（图结构内存开销更大、实现复杂）。
  

## wikipedia [Sea of nodes](https://en.wikipedia.org/wiki/Sea_of_nodes)

A **sea of nodes** is a [graph](https://en.wikipedia.org/wiki/Graph_\(abstract_data_type\) "Graph (abstract data type)") representation of [single-static assignment (SSA)](https://en.wikipedia.org/wiki/Static_single-assignment_form "Static single-assignment form") representation of a program that combines [data flow](https://en.wikipedia.org/wiki/Data-flow_analysis "Data-flow analysis") and [control flow](https://en.wikipedia.org/wiki/Control-flow_graph "Control-flow graph"), and relaxes the [control flow](https://en.wikipedia.org/wiki/Control_flow "Control flow") from a [total order](https://en.wikipedia.org/wiki/Total_order "Total order") to a [partial order](https://en.wikipedia.org/wiki/Partially_ordered_set "Partially ordered set"), keeping only the orderings required by [data flow](https://en.wikipedia.org/wiki/Dataflow "Dataflow").


