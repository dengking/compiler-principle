# Build && evaluate

build 和 evaluate本质上是相同的，都与AST相关。

两个方向:

1、自底向上

2、自顶向下

## build、construct

如何根据expression构建expression tree？



参考文章:

一、wikipedia [Binary expression tree](https://en.wikipedia.org/wiki/Binary_expression_tree)

二、geeksforgeeks [Expression Tree](https://www.geeksforgeeks.org/expression-tree/)

给出了根据reverse polish postfix notation expression构建expression tree的示例代码，其中使用的stack。

## evaluate

