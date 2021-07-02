# Binary expression tree

## wikipedia [Binary expression tree](https://en.wikipedia.org/wiki/Binary_expression_tree)

A **binary expression tree** is a specific kind of a [binary tree](https://en.wikipedia.org/wiki/Binary_tree) used to represent expressions. Two common types of expressions that a binary expression tree can represent are [algebraic](https://en.wikipedia.org/wiki/Algebra)[[1\]](https://en.wikipedia.org/wiki/Binary_expression_tree#cite_note-brpreiss-1) and [boolean](https://en.wikipedia.org/wiki/Boolean_algebra). These trees can represent expressions that contain both [unary](https://en.wikipedia.org/wiki/Unary_operation) and [binary](https://en.wikipedia.org/wiki/Binary_function) operators.[[1\]](https://en.wikipedia.org/wiki/Binary_expression_tree#cite_note-brpreiss-1)

Each node of a **binary tree**, and hence of a **binary expression tree**, has zero, one, or two children. This restricted structure simplifies the processing of **expression trees**.

> NOTE: : 二叉树能够满足 [unary](https://en.wikipedia.org/wiki/Unary_operation) and [binary](https://en.wikipedia.org/wiki/Binary_function) operators有一个或两个operands的需求；

### Overview

The leaves of a binary expression tree are **operands**, such as constants or variable names, and the other nodes contain **operators**. These particular trees happen to be binary, because all of the operations are binary, and although this is the simplest case, it is possible for nodes to have more than two children. It is also possible for a node to have only one child, as is the case with the unary minus operator. An expression tree, *T*, can be evaluated by applying the **operator** at the root to the values obtained by recursively evaluating the left and right subtrees.[[2\]](https://en.wikipedia.org/wiki/Binary_expression_tree#cite_note-Gopal2010-2) 

> NOTE: : 关于Evaluation of Expression Tree参见：

-  [Evaluation of Expression Tree](https://www.geeksforgeeks.org/evaluation-of-expression-tree/ )
- [Evaluating expression trees](https://stackoverflow.com/questions/10769174/evaluating-expression-trees)
- [Expression Evaluation](https://www.geeksforgeeks.org/expression-evaluation/)
- [Stack | Set 4 (Evaluation of Postfix Expression)](https://www.geeksforgeeks.org/stack-set-4-evaluation-postfix-expression/)
- [Expression Tree Construction and Evaluation](https://www.codechef.com/problems/UCS616A1) 
- [Binary Tree Expression Solver](https://www.codeproject.com/articles/10316/binary-tree-expression-solver)



[![img](https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Exp-tree-ex-11.svg/250px-Exp-tree-ex-11.svg.png)](https://en.wikipedia.org/wiki/File:Exp-tree-ex-11.svg)

 Expression tree 

> NOTE: : 

- how to evaluate expression tree？
- how to construct an expression tree of an expression？
- how to construct an expression of an expression tree？
- operator precedence and construction of expression tree
- [Operator associativity](https://en.wikipedia.org/wiki/Operator_associativity) and construction of expression tree



### Traversal

> NOTE: : 对binary expression tree进行traverse从而获得对应的algebraic expression。

An algebraic expression can be produced from a **binary expression tree** by recursively producing a **parenthesized left expression**, then printing out the operator at the **root**, and finally recursively producing a **parenthesized right expression**. This general strategy (left, node, right) is known as an [in-order traversal](https://en.wikipedia.org/wiki/Tree_traversal). An alternate traversal strategy is to recursively print out the left subtree, the right subtree, and then the operator. This traversal strategy is generally known as [post-order traversal](https://en.wikipedia.org/wiki/Tree_traversal). A third strategy is to print out the operator first and then recursively print out the left and right subtree known as pre-order traversal.[[2\]](https://en.wikipedia.org/wiki/Binary_expression_tree#cite_note-Gopal2010-2)



These three standard depth-first traversals are representations of the three different **expression formats**: infix, postfix, and prefix. An **infix expression** is produced by the **inorder traversal**, a **postfix expression is produced** by the **post-order traversal**, and a **prefix expression** is produced by the **pre-order traversal**.[[3\]](https://en.wikipedia.org/wiki/Binary_expression_tree#cite_note-Gilberg-3)



#### Infix traversal

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



### Construction of an expression tree

 The evaluation of the tree takes place by reading the postfix expression one symbol at a time. If the symbol is an operand, a one-node tree is created and its pointer is pushed onto a [stack](https://en.wikipedia.org/wiki/Stack_(abstract_data_type)). If the symbol is an operator, the pointers to two trees *T1* and *T2* are popped from the stack and a new tree whose root is the operator and whose left and right children point to *T2* and *T1* respectively is formed . A pointer to this new tree is then pushed to the Stack.[[4\]](https://en.wikipedia.org/wiki/Binary_expression_tree#cite_note-4) 