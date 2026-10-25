# Grammar examples

本文总结梳理一些经典的文法以帮助读者掌握如何书写文法，由难到易，从对每个production进行详细分析和展开再到对文法整体进行说明。
## 经典的表达式文法(E-T-F)
[[front-end/grammar/index#三、形式工具 BNF / EBNF|经典的表达式文法(E-T-F)]]

```EBNF
expr   → expr '+' term   | term
term   → term '*' factor | factor
factor → NUMBER | '(' expr ')' | IDENT
```

`factor -> | '(' expr ')' |` 这是典型的indirect recursion，`expr` 就是**递归非终结符**。


一个产生式中能够有一个同级operator

### 产生式 `expr   → expr '+' term   | term` 的能否替换为`expr   → expr '+' term `

答案是: 不能，因为替换后文法描述的**语言变了**：表达式中最多只能出现一个顶层的 `+`。
tips: `expr   → expr '+' term` 类似于 linked list的recursive definition，后面会进行说明。
#### 1. 对比两种写法生成的语言

**原文法：**
```EBNF
expr → expr '+' term | term
```
`expr` 可以递归展开任意多次：
```EBNF
expr ⇒ expr + term
     ⇒ expr + term + term
     ⇒ term + term + term + ...
```
它等价于 `expr → term { '+' term }`(这使用的是[[EBNF]])，也就是用 `+` 连接的**任意多个** term。

>NOTE: 注意上述等价写法是**非递归**的: 其实它是使用正则语言来描述recursion/recursive definition，后面对这种EBNF的写法进行了介绍

**替换后：**
```
expr → term '+' term | term
```
右侧不再包含 `expr`，没有了递归，所以 `expr` 只能是：
- `term`，或
- `term + term`

#### 2. 反例：`1 + 2 + 3`

用原文法可以推导：
```EBNF
expr ⇒ expr + term
     ⇒ (expr + term) + term
     ⇒ (term + term) + term
     ⇒ 1 + 2 + 3   ✓
```

用替换后的文法，`expr → term + term` 只能把串切成两个 term。但 `term` 只能由 `*` 和 `factor` 构成，无法吸收一个不带括号的 `+`：
- `1 + 2` 不是合法的 term
- `2 + 3` 也不是合法的 term

所以 `1 + 2 + 3` **无法推导** ✗，只能写成 `(1 + 2) + 3` 这种带括号的形式。

#### 3. 如果想去掉左递归，正确的做法

左递归会让 LL / 递归下降分析器陷入无限递归，这可能正是你想改写它的原因。下面几种写法都能保持语言不变：

**(a) 改成右递归**
```
expr → term '+' expr | term
```
语言相同，但语法树变成**右结合**：`1+2+3` 被解析为 `1+(2+3)`。对 `+` 来说结果一样；如果以后加入 `-` 或 `/`，结果就会出错，比如 `8-3-2` 会被算成 `8-(3-2)`。

**(b) 标准的消除左递归**
```
expr  → term expr'
expr' → '+' term expr' | ε
```
这种写法适合 LL(1) 分析。如果要保持左结合，需要在语义动作中处理。

**(c) EBNF 重复形式（推荐用于递归下降）**
```
expr → term { '+' term }
```
实现时用循环即可，天然保持左结合：
```python
def expr():
    val = term()
    while peek() == '+':
        consume('+')
        val = val + term()
    return val
```

#### 结论

`expr → term '+' term` 去掉了递归，使语言从"任意多个 term 相加"缩小为"至多两个 term 相加"，因此不能替换。`term → term '*' factor` 也是同样的道理。如果目的是消除左递归，应采用上面 3(b) 或 3(c) 的写法。

