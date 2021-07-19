# Evaluation

geeksforgeeks [Evaluation of Expression Tree](https://www.geeksforgeeks.org/evaluation-of-expression-tree/ )

stackoverflow [Evaluating expression trees](https://stackoverflow.com/questions/10769174/evaluating-expression-trees)

geeksforgeeks [Expression Evaluation](https://www.geeksforgeeks.org/expression-evaluation/)

geeksforgeeks [Stack | Set 4 (Evaluation of Postfix Expression)](https://www.geeksforgeeks.org/stack-set-4-evaluation-postfix-expression/)

codechef [Expression Tree Construction and Evaluation](https://www.codechef.com/problems/UCS616A1) 

codeproject [Binary Tree Expression Solver](https://www.codeproject.com/articles/10316/binary-tree-expression-solver)



## Post-order traversal、dependency、stack

表达式树也是树，既然是树，那么它的结构就具备递归性

**表达式树**的evaluation一定是**深度优先**的，不可以是**广度优先**；因为只有子树的结果都计算出来了，才能够计算得到这些子树的父节点的值；如果从遍历的角度来看的话，它所对应的是深度优先遍历的后序遍历。
