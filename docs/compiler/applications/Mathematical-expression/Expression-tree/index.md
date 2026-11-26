# Expression tree

expression tree 是 AST

## wikipedia [Binary expression tree](https://en.wikipedia.org/wiki/Binary_expression_tree)

A **binary expression tree** is a specific kind of a [binary tree](https://en.wikipedia.org/wiki/Binary_tree) used to represent expressions. Two common types of expressions that a binary expression tree can represent are [algebraic](https://en.wikipedia.org/wiki/Algebra)[[1\]](https://en.wikipedia.org/wiki/Binary_expression_tree#cite_note-brpreiss-1) and [boolean](https://en.wikipedia.org/wiki/Boolean_algebra). These trees can represent expressions that contain both [unary](https://en.wikipedia.org/wiki/Unary_operation) and [binary](https://en.wikipedia.org/wiki/Binary_function) operators.[[1\]](https://en.wikipedia.org/wiki/Binary_expression_tree#cite_note-brpreiss-1)

Each node of a **binary tree**, and hence of a **binary expression tree**, has zero, one, or two children. This restricted structure simplifies the processing of **expression trees**.

> NOTE: : 
>
> 一、二叉树能够满足 [unary](https://en.wikipedia.org/wiki/Unary_operation) and [binary](https://en.wikipedia.org/wiki/Binary_function) operators有一个或两个operands的需求；

### Overview

The leaves of a binary expression tree are **operands**, such as constants or variable names, and the other nodes contain **operators**. These particular trees happen to be binary, because all of the operations are binary, and although this is the simplest case, it is possible for nodes to have more than two children. It is also possible for a node to have only one child, as is the case with the unary minus operator. An expression tree, *T*, can be evaluated by applying the **operator** at the root to the values obtained by recursively evaluating the left and right subtrees.

> NOTE: 
>
> 关于Evaluation of Expression Tree参见 `Evaluation` 章节
>



[![img](https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Exp-tree-ex-11.svg/250px-Exp-tree-ex-11.svg.png)](https://en.wikipedia.org/wiki/File:Exp-tree-ex-11.svg)



### Traversal

> NOTE: : 对binary expression tree进行traverse从而获得对应的algebraic expression。



#### Infix traversal

> NOTE: 
>
> 其实就是inorder traversal

When an **infix expression** is printed, an opening and closing parenthesis must be added at the beginning and ending of each expression. As every **subtree** represents a **subexpression**, an opening parenthesis is printed at its start and the closing parenthesis is printed after processing all of its children. 

 Pseudocode: 

```pseudocode
Algorithm infix (tree)
/*Print the infix expression for an expression tree.
 Pre : tree is a pointer to an expression tree
 Post: the infix expression has been printed*/
 if (tree not empty)
    if (tree token is operator)
       print (open parenthesis)
    end if
    infix (tree left subtree)
    print (tree token)
    infix (tree right subtree)
    if (tree token is operator)
       print (close parenthesis)
    end if
 end if
end infix
```

#### Postfix traversal

The postfix expression is formed by the basic postorder traversal of any binary tree. It does not require parentheses.

Pseudocode:

```pseudocode
Algorithm postfix (tree)
/*Print the postfix expression for an expression tree.
 Pre : tree is a pointer to an expression tree
 Post: the postfix expression has been printed*/
 if (tree not empty)
    postfix (tree left subtree)
    postfix (tree right subtree)
    print (tree token)
 end if
end postfix
```

#### Prefix traversal

The prefix expression formed by prefix traversal uses the standard pre-order tree traversal. No parentheses are necessary.

Pseudocode:

```pseudocode
Algorithm prefix (tree)
/*Print the prefix expression for an expression tree.
 Pre : tree is a pointer to an expression tree
 Post: the prefix expression has been printed*/
 if (tree not empty)
    print (tree token)
    prefix (tree left subtree)
    prefix (tree right subtree)
 end if
end prefix
```

### Construction of an expression tree

The evaluation of the tree takes place by reading the postfix expression one symbol at a time. If the symbol is an operand, a one-node tree is created and its pointer is pushed onto a [stack](https://en.wikipedia.org/wiki/Stack_(abstract_data_type)). If the symbol is an operator, the pointers to two trees *T1* and *T2* are popped from the stack and a new tree whose root is the operator and whose left and right children point to *T2* and *T1* respectively is formed . A pointer to this new tree is then pushed to the Stack.[[4\]](https://en.wikipedia.org/wiki/Binary_expression_tree#cite_note-4) 



## Build && evaluate

build 和 evaluate本质上是非常类似的:

一、都与AST相关

"evaluate"的过程其实是对AST的traversal

二、两个方向:

1、自底向上

2、自顶向下

## build、construct expression

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

