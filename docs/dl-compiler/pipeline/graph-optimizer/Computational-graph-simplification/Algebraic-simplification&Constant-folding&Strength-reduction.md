# Algebraic Simplification, Constant Folding & Strength Reduction

> **定位**：计算图化简中面向"数学等价变换"的三个经典技术。它们各自独立、但常常互相触发，是编译器 canonicalization pass 中最基础也最有用的一组重写规则。

## 一、常量折叠（Constant Folding）

编译期就把**只依赖常量**的计算算出来。

```
优化前：                    优化后：
    a = 2 * 3               a = 6         （编译期算好）
    y = x + a               y = x + 6
```

在深度学习中，可折叠的常量子图非常多：

| 场景 | 说明 |
| --- | --- |
| **权重预处理** | 训练完成后，权重是常量 |
| **BN 参数** | 推理时 $\gamma / \beta / \mu / \sigma$ 都是常量，可折叠进 Conv |
| **Shape 计算** | `x.shape[0] * 2 * y.shape[1]` 常常在编译期能算 |
| **Reshape 参数** | reshape 的目标 shape 若来自常量 |
| **量化 scale 传播** | 常量 scale × 常量 scale = 新常量 |

### 常量折叠的实现要点

```
def fold(node):
    if all(input.is_constant() for input in node.inputs):
        result = execute_on_cpu(node)   ← 编译期直接执行一次
        replace_node_with_constant(node, result)
```

**注意事项**：

- 折叠代价过大的算子应跳过（如折叠一个大 conv）
- 折叠可能触发新的常量出现 → 需迭代到不动点
- 数值稳定性：某些浮点运算折叠会引入舍入差异

## 二、代数恒等式化简（Algebraic Simplification）

利用数学恒等式删除无意义运算：

### 2.1 逐元素算子的恒等式

```
x + 0        → x
x * 1        → x
x * 0        → 0
x - x        → 0
x / 1        → x
x - 0        → x
0 - x        → -x
x * -1       → -x
(-x) * (-y)  → x * y
min(x, x)    → x
max(x, x)    → x
```

### 2.2 张量算子的恒等式

```
transpose(transpose(x, p1), p2)     → transpose(x, p2∘p1)
    若 p2∘p1 = identity              → x
reshape(reshape(x, s1), s2)         → reshape(x, s2)
reshape(x, x.shape)                 → x
concat(split(x))                    → x
split(concat(a, b))                 → (a, b)
slice(concat(a, b), ...)            → a 或 b（若切片落在其中一段）
broadcast(broadcast(x, s1), s2)     → broadcast(x, s2)
cast(cast(x, T1), T2)               → cast(x, T2)  （若无精度损失）
```

### 2.3 归约算子的恒等式

```
sum(x, axis=[])                     → x
sum([x], axis=0)                    → x     （1 元素归约）
mean(x, axis=k) 且 x.shape[k]=1     → squeeze(x, k)
```

## 三、强度削减（Strength Reduction）

用**低成本运算**替换高成本运算：

```
x / 常量  → x * (1/常量)      （除法 → 乘法，除法在 GPU 上慢一个量级）
x ^ 2     → x * x             （幂 → 乘法）
x ^ 0.5   → sqrt(x)           （幂 → 专用指令）
x * 2     → x << 1            （乘 → 移位，整数场景）
x % 2^k   → x & (2^k - 1)     （取模 → 位与，整数场景）
```

**深度学习特有的强度削减**：

```
div(x, sqrt(var + eps))    → x * rsqrt(var + eps)
    · rsqrt 是硬件专用指令，比 sqrt + div 快得多
    · LayerNorm / RMSNorm 里最常见

exp(-x) / (1 + exp(-x))    → sigmoid(x)
    · sigmoid 有稳定实现和硬件专用近似

log(softmax(x))            → log_softmax(x)
    · 数值稳定 + 少算一次 log
```

## 四、三者的组合触发

在实际编译过程中，这三种变换**紧密耦合、互相触发**：

```
初始：  y = (x + 0) * 1

step1 (代数化简)：  x + 0 → x    得到  y = x * 1
step2 (代数化简)：  x * 1 → x    得到  y = x

初始：  y = x + (2 * 3)

step1 (常量折叠)：  2 * 3 → 6    得到  y = x + 6

初始：  y = x / (2 * 2)

step1 (常量折叠)：  2 * 2 → 4        得到  y = x / 4
step2 (强度削减)：  x / 4 → x * 0.25 得到  y = x * 0.25
```

因此这三个 Pass 通常**放在同一个 canonicalization pass 中反复迭代到不动点**。

## 五、常见陷阱

### 5.1 浮点非结合性

```
数学上：(a + b) + c = a + (b + c)
浮点上：不一定成立（舍入误差）

因此 (x + 0.1) - 0.1 → x  这种化简需要"允许 fast-math"开关
```

### 5.2 特殊值

```
x * 0 → 0  ？
    · x 为 NaN 时不成立（NaN * 0 = NaN）
    · 需在"允许假设无 NaN"下才能应用
```

### 5.3 广播 shape

```
x + 0    → x
    仅当 0 的 shape 广播后不改变 x 的 shape 时才成立
    否则 x + zeros(bigger_shape) 会广播 x！
```

## 六、在各编译器中的实现

| 编译器 | 实现位置 |
| --- | --- |
| **XLA** | HLO `AlgebraicSimplifier` Pass |
| **TVM** | `FoldConstant`、`SimplifyExpr` Pass |
| **MLIR** | 各 Dialect 的 `canonicalize` / `fold` 方法 + `Canonicalizer` Pass |
| **PyTorch Inductor** | `torch._inductor.fx_passes.pre_grad` 中的一系列 pattern |
| **TensorRT** | 内部 Constant Folding + Elimination |

## 七、面试高频

| 问题 | 要点 |
| --- | --- |
| 常量折叠什么时候不能做？ | 代价过大、可能改变数值语义（浮点非结合、NaN） |
| `x / const` → `x * (1/const)` 需要注意？ | 精度损失（除数是 0.1 之类不能精确表示的浮点） |
| `transpose(transpose(x))` 怎么消？ | 计算复合置换，若为恒等则删除，否则合并为一次 |
| 为什么这三个 pass 常合在一起？ | 互相触发，需迭代到不动点 |
