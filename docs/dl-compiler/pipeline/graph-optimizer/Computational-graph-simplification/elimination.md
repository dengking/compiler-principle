# Redundancy Elimination（冗余消除）

> **定位**：计算图化简中"删代码"的一组技术。它不改变任何有效计算，只是**删除重复的、无用的、恒等的节点**，让图更干净、后续 pass 更省力。

## 一、公共子表达式消除（Common Subexpression Elimination, CSE）

复用重复计算的子图。

```
优化前：                     优化后：
    t1 = a + b                t1 = a + b
    t2 = a + b        →       t2 = t1     （复用）
```

在计算图中，若两个节点**算子相同 + 输入相同 + 属性相同**，则可合并为一个。

### 1.1 CSE 的实现思路

```python
def cse(graph):
    hash_table = {}
    for node in graph.topological_order():
        key = (node.op_type, tuple(node.inputs), tuple(node.attrs))
        if key in hash_table:
            # 已经算过，直接复用
            replace_all_uses(node, hash_table[key])
            remove(node)
        else:
            hash_table[key] = node
```

### 1.2 深度学习中的常见触发点

```
· 模型中多次调用同一段共享子网络（如 Siamese Network 的双塔）
· 常量子表达式的重复计算（编译期未折叠彻底时）
· 分布式训练中反向图的重复梯度计算
· 图变换过程中意外产生的重复节点
```

### 1.3 与"可用表达式分析"的关系

传统编译器理论中，CSE 依赖**可用表达式分析（Available Expression Analysis）**——数据流分析的经典应用。在 DAG 结构的计算图上，简化为**基于哈希的等价类合并**。

## 二、死代码消除（Dead Code Elimination, DCE）

删除**结果未被使用**的节点。

```
    x ──▶ [OpA] ──▶ y  （y 被输出使用，保留）
    x ──▶ [OpB] ──▶ z  （z 无人使用 → 删除整个 OpB）
```

### 2.1 DCE 的实现思路

```python
def dce(graph):
    # 从输出节点反向可达性分析
    reachable = set(graph.outputs)
    stack = list(graph.outputs)
    while stack:
        node = stack.pop()
        for input in node.inputs:
            if input not in reachable:
                reachable.add(input)
                stack.append(input.producer)

    # 删除不可达的所有节点
    for node in graph.all_nodes():
        if node not in reachable and not has_side_effect(node):
            remove(node)
```

### 2.2 深度学习中的常见触发点

```
· 训练/推理切换：推理时 loss、优化器相关子图整体死掉
· Dropout 在推理时的分支
· 未使用的模型输出（导出 ONNX 时常见）
· 图变换过程中残留的临时节点
· 融合后原算子失去用户，成为死节点
```

### 2.3 副作用节点的处理

带副作用的节点（如 `Print`、随机数种子更新、跨设备通信）**不能仅因输出未用就删除**。DCE 必须尊重"副作用标记"。

## 三、恒等算子消除（Identity Elimination）

删除**不改变数据**的算子：

```
可消除的恒等操作：
- Identity              → 直接删除
- Dropout(推理时)       → 训练时保留、推理时删除
- 无效的 Cast           → cast(x, dtype=x.dtype)
- reshape 到相同 shape  → reshape(x, x.shape)
- transpose(x, identity_perm)  → 恒等置换
- Squeeze(dim, size=1)  → 若 size 本就为 1 才有效，否则错误
- scale=1 的缩放        → x * 1
- pad=0 的填充          → 全 0 填充
- concat(single_input)  → 仅一个输入的 concat
- split(x, [full_size]) → 未真正切分
```

### 3.1 恒等 Cast 的一个坑

```
cast(x, dtype=x.dtype)  → x    ？

看似恒等，但如果原本 cast 是"精度稳定化"的显式标记，删除可能改变数值行为。
需结合上下文判断。
```

## 四、三者的关系

```
CSE  ── "重复的" 就合并
DCE  ── "没人用的" 就删除
Identity Elimination ── "不改变数据的" 就删除

共同点：语义等价、纯粹在删/合并节点、不修改剩余节点的逻辑
```

在实际编译流程中，这三个 pass 通常**先融合 → 再消除**：融合会产生大量新的中间节点/临时结构，接着 CSE + DCE + Identity Elimination 把残余清理干净。

## 五、迭代到不动点

消除也存在互相触发：

```
初始：
    a = x + 0
    b = x + 0
    c = a * 1
    d = c

step1 (代数化简)：a = x, b = x
step2 (CSE)：      b = a  (即 b = x)，两者合并
step3 (代数化简)：c = a
step4 (Identity)： c = a 直接短接
step5 (DCE)：      若 b, c 未被外部使用，删除

→ 最终： d = x
```

## 六、面试高频

| 问题 | 要点 |
| --- | --- |
| CSE 的判等依据？ | 算子类型 + 输入序列 + 属性（不含 shape 也可比对） |
| DCE 何时能删？ | 输出不可达、无副作用 |
| Dropout 推理时如何处理？ | 视为 Identity 删除（编译期已知 training=false） |
| 三者需要按什么顺序执行？ | 通常放在一个 canonicalizer 里迭代到不动点 |
| 怎么保证 DCE 的正确性？ | 尊重副作用标记；从输出/side-effect 节点做反向可达 |
