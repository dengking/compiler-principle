# gramar: 语言的结构
grammar即文法
## 它管什么

**Grammar(语法)规定哪些字符串构成合法的程序文本。** 形式化地说,语言是字母表 $\Sigma$ 上字符串的集合 $L \subseteq \Sigma^*$,语法层要回答的就是一个成员判定问题:

$$w \in L\ ?$$

它只关心符号的**形状与排列**,不关心含义:

```c
int x = ;          // 不属于 L:= 后缺表达式,CFG 直接拒绝
int x = "hello";   // 属于 L:形状完全合法(类型错误是静态语义的事)
```

在三层里,grammar 是最廉价、最"机械"的一层:可判定、近乎线性、错误位置精确。但下文会看到,它并不像看上去那么"纯形式"。

主流文法:

| grammar                                                                    |     |
| -------------------------------------------------------------------------- | --- |
| [[front-end/context-free-grammar/index\|context free grammar]]             | 生成式 |
| [[front-end/parsing-expression-grammar/index\|parsing expression grammar]] | 识别式 |

## Recursive grammar

递归是文法能描述无限语言和任意深度嵌套结构的根本原因，主流文法都支持递归。

## wikipedia [Recursive grammar](https://en.wikipedia.org/wiki/Recursive_grammar)

In [computer science](https://en.wikipedia.org/wiki/Computer_science "Computer science"), a [grammar](https://en.wikipedia.org/wiki/Formal_grammar "Formal grammar") is informally called a **recursive grammar** if it contains [production rules](https://en.wikipedia.org/wiki/Formal_grammar#The_syntax_of_grammars "Formal grammar") that are [recursive](https://en.wikipedia.org/wiki/Recursion_\(computer_science\) "Recursion (computer science)"), meaning that expanding a non-terminal according to these rules can eventually lead to a string that includes the same non-terminal again. Otherwise it is called a **non-recursive grammar**.[[1]](https://en.wikipedia.org/wiki/Recursive_grammar#cite_note-ns02-1)
> NOTE: 包含直接递归和间接递归

For example, a grammar for a [context-free language](https://en.wikipedia.org/wiki/Context-free_language "Context-free language") is [left recursive](https://en.wikipedia.org/wiki/Left_recursion "Left recursion") if there exists a non-terminal symbol *A* that can be put through the production rules to produce a string with *A* (as the leftmost symbol).[[2]](https://en.wikipedia.org/wiki/Recursive_grammar#cite_note-2)[[3]](https://en.wikipedia.org/wiki/Recursive_grammar#cite_note-3) All types of grammars in the [Chomsky hierarchy](https://en.wikipedia.org/wiki/Chomsky_hierarchy "Chomsky hierarchy") can be recursive and it is recursion that allows the production of infinite sets of words.

## 直接和间接

[[books&courses/龙书/4-Syntax-Analysis/4.2-Context-Free-Grammars/index|direct-recursion&indirect-recursion]]


### 素材

1、gatevidyalay [Left Recursion | Left Recursion Elimination](https://www.gatevidyalay.com/left-recursion-left-recursion-elimination/) 
