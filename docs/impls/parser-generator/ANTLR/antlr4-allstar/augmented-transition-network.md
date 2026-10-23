
# Augmented transition network

wikipedia [Augmented transition network](https://en.wikipedia.org/wiki/Augmented_transition_network)
An **Augmented Transition Network** (Augmented transition network) is ==a graph-based computational model used in natural language processing (NLP) and artificial intelligence to parse and analyze the grammatical structure of sentences==.


## ATN 是什么

**ATN = Augmented Transition Network（增强转移网络）**，是 ANTLR4 内部用来表示文法的数据结构，也是它的 **ALL(\*) 预测算法**的运行基础。

### 1. 直观理解

可以把 ATN 看作 **"会调用子程序的 NFA"**：

- 文法中的**每条规则**对应一个小型状态机（子网络），有一个入口状态和一个出口状态。
- 状态之间的**边**有几类：
  - **终结符边**：匹配一个 token 才能通过；
  - **ε 边**：不消耗输入，可直接通过；
  - **规则调用边**：跳进另一条规则的子网络，执行完再回到调用点（类似函数调用）；
  - **谓词边 / 动作边**：带语义判断或动作。

普通 NFA 只能识别正则语言。ATN 加上了"规则调用 + 返回"，相当于多了一个**调用栈**，因此能表达**上下文无关文法**(CFG)中的**递归结构**。这就是名字里 "Augmented"（增强）的含义。

## 2. 一个小例子

```antlr
e : e '*' e
  | INT
  ;
```

ANTLR4 会先把这种**直接左递归**自动改写成"循环 + 优先级谓词"的形式，大致相当于：

```antlr
e[p] : INT ( {p <= 2}? '*' e[3] )* ;
```

然后再构造 ATN：

```
e 的入口 ──INT──▶ s1 ──ε──▶ 循环判断 ──{谓词}?──▶ s2 ──'*'──▶ s3 ──调用 e──▶ s4 ──ε──▶ 回到循环
                                   └──ε──▶ e 的出口
```

## 3. 和原文后半句的关系

原文提到的几个概念都定义在 ATN 上：

| 概念 | 含义 |
|---|---|
| **配置 (p, i, γ)** | p 是当前所处的 **ATN 状态**；i 是正在尝试的**备选分支编号**；γ 是**调用栈**（记录从哪些规则调用点进来，以便返回） |
| **closure** | 从一组配置出发，沿所有 **ε 边**（包括进入、退出规则）扩展，得到不消耗输入就能到达的全部配置 |
| **move** | 让配置沿**匹配当前 token 的终结符边**前进一步 |

ALL(\*) 预测的过程是：在决策点为每个备选分支生成初始配置，然后对后续 token 反复执行 move 和 closure。当剩下的配置只属于同一个分支 i 时，就选定这个分支。

## 4. 为什么能"直接写左递归"

原文的第一个目标与此相关，原因有两点：

1. **ANTLR4 在构造 ATN 之前，会自动把直接左递归改写成循环加优先级谓词。** 因此 ATN 和生成的递归下降代码中都不存在真正的左递归，不会无限递归。
2. **ALL(\*) 在运行时基于 ATN 动态向前看任意多个 token**，而不是像 LL(1) 那样只看 1 个 token 并依赖静态预测表。所以很多存在公共前缀、LL(1) 下有冲突的文法也无需手工提取左公因子。

需要注意，ANTLR4 只支持**直接左递归**，间接左递归（如 `a : b ... ; b : a ...;`）仍然不支持。

## 5. 名字的来历

ATN 最早由 William Woods 在 1970 年提出，用于自然语言分析，原版带有寄存器和任意动作。ANTLR 借用了这个名称和基本思想，但使用的是简化版本：只保留状态、边、规则调用和谓词，用来服务于语法分析和预测。