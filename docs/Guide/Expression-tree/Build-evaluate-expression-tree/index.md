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

### evaluation of expression tree

一、geeksforgeeks [Expression Tree](https://www.geeksforgeeks.org/expression-tree/)

递归、自顶向下、binary tree-DFS-post order后序-return value

二、geeksforgeeks [Evaluation of Expression Tree](https://www.geeksforgeeks.org/evaluation-of-expression-tree/?ref=rp)

递归、自顶向下、binary tree-DFS-post order后序-return value

### evaluation of expression 

一、infogalactic [Polish notation](https://infogalactic.com/info/Polish_notation)

自右向左、自底向上(使用stack)

二、infogalactic [Reverse Polish notation](https://infogalactic.com/info/Reverse_Polish_notation)

自右向左、自底向上(使用stack)

三、leetcode [150. 逆波兰表达式求值](https://leetcode-cn.com/problems/evaluate-reverse-polish-notation/)



### Post-order traversal、dependency、stack

表达式树也是树，既然是树，那么它的结构就具备递归性

**表达式树**的evaluation一定是**深度优先**的，不可以是**广度优先**；因为只有子树的结果都计算出来了，才能够计算得到这些子树的父节点的值；如果从遍历的角度来看的话，它所对应的是深度优先遍历的后序遍历。

### Evaluation TODO

geeksforgeeks [Evaluation of Expression Tree](https://www.geeksforgeeks.org/evaluation-of-expression-tree/ )

stackoverflow [Evaluating expression trees](https://stackoverflow.com/questions/10769174/evaluating-expression-trees)

geeksforgeeks [Expression Evaluation](https://www.geeksforgeeks.org/expression-evaluation/)

geeksforgeeks [Stack | Set 4 (Evaluation of Postfix Expression)](https://www.geeksforgeeks.org/stack-set-4-evaluation-postfix-expression/)

codechef [Expression Tree Construction and Evaluation](https://www.codechef.com/problems/UCS616A1) 

codeproject [Binary Tree Expression Solver](https://www.codeproject.com/articles/10316/binary-tree-expression-solver)

