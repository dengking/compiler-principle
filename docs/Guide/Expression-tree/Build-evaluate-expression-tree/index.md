# Build && evaluate

build 和 evaluate本质上是非常类似的:

一、都与AST相关

"evaluate"的过程其实是对AST的traversal

二、两个方向:

1、自底向上

2、自顶向下

## build、construct

如何根据expression构建expression tree？参考文章:

一、wikipedia [Binary expression tree](https://en.wikipedia.org/wiki/Binary_expression_tree)

二、geeksforgeeks [Expression Tree](https://www.geeksforgeeks.org/expression-tree/)

reverse polish postfix notation expression、自底向上(使用stack)构建expression tree的示例代码。

三、geeksforgeeks [Building Expression tree from Prefix Expression](https://www.geeksforgeeks.org/building-expression-tree-from-prefix-expression/) 

polish prefix notation expression、递归、自顶向下

## evaluate

一、geeksforgeeks [Expression Tree](https://www.geeksforgeeks.org/expression-tree/)

递归、自顶向下、binary tree-DFS-post order后序-return value

二、geeksforgeeks [Evaluation of Expression Tree](https://www.geeksforgeeks.org/evaluation-of-expression-tree/?ref=rp)

递归、自顶向下、binary tree-DFS-post order后序-return value

