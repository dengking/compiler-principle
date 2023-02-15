# 2.3 Syntax-Directed Translation





## 2.3.4 Tree Traversals 



### Preorder and Postorder Traversals 

> NOTE:
>
> 明确提出了action的概念

Preorder and postorder traversals are two important special cases of depth- rst traversals in which we visit the children of each node from left to right. Often, we traverse a tree to perform some particular action at each node. If the action is done when we rst visit a node, then we may refer to the traversal as a preorder traversal. Similarly, if the action is done just before we leave a node for the last time, then we say it is a postorder traversal of the tree. The procedure visit(N) in Fig. 2.11 is an example of a postorder traversal. Preorder and postorder traversals dene corresponding orderings on nodes, based on when the action at a node would be performed. The preorder of a (sub)tree rooted at node N consists of N, followed by the preorders of the subtrees of each of its children, if any, from the left. The postorder of a (sub)tree rooted at N consists of the postorders of each of the sub



## 2.3.5 Translation Schemes 



A **syntax-directed translation scheme** is a notation for specifying a translation by attaching program fragments to productions in a grammar. A translation scheme is like a **syntax-directed denition**, except that the order of evaluation of the semantic rules is explicitly specied.

```
rest -> + term {print('+')} rest1
```

