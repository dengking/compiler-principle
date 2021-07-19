# geeksforgeeks [Building Expression tree from Prefix Expression](https://www.geeksforgeeks.org/building-expression-tree-from-prefix-expression/)

> NOTE: 
>
> 一、需要掌握prefix expression的递归定义，然后根据recursive definition就可以写出对应的recursive function，下面的"Approach"既是如此。
>
> 它的implementation让我想到了根据preorder traversal来反序列化一棵二叉树
>
> 原文给出的实现是递归自顶向下构建二叉树；
>
> 在 infogalactic [Polish notation](https://infogalactic.com/info/Polish_notation) 中，给出了自底向上evaluate prefix expression
>
> 

**Approach:** If the character is an **operand** i.e. **X** then it’ll be the leaf node of the required tree as all the **operands** are at the leaf in an expression tree. Else if the character is an operator and of the form **OP X Y** then it’ll be an internal node with left child as the **expressionTree(X)** and right child as the **expressionTree(Y)** which can be solved using a recursive function.



## Examples

```C++
Input: a[] = “*+ab-cd”
Output: The Infix expression is:
a + b * c – d
The Postfix expression is:
a b + c d – *

Input: a[] = “+ab”
Output: The Infix expression is:
a + b
The Postfix expression is:
a b +
```

## 完整程序

> NOTE: 
>
> 下面程序是根据原文的程序稍微整理的

```C++
// C program to construct an expression tree
// from prefix expression
#include <stdio.h>
#include <stdlib.h>

// Represents a node of the required tree
typedef struct node
{
	char data;
	struct node *left, *right;
} node;

/**
 * @brief Function to recursively build the expression tree
 *
 * @param p
 * @param a 当前节点的data值
 * @return 下一个节点的data值
 */
char* add(node **p, char *a)
{
	// If its the end of the expression
	if (*a == '\0')
	{
		return '\0';
	}
	/**
	 * 第一步: 先构造节点，
	 * 第二步:
	 * 1、如果对应的节点是一个operator，则需要递归向下构造左右子树
	 * 2、如果对应的节点是一个operand，则完成了构造
	 */
	while (1)
	{
		if (*p == NULL) // 第一步: 需要创建一个新的节点
		{

			// Create a node with *a as the data and
			// both the children set to null
			node *nn = (node*) malloc(sizeof(node));
			nn->data = *a;
			nn->left = NULL;
			nn->right = NULL;
			*p = nn;
		}
		else // 第二步
		{

			// If the character is an operand
			if (*a >= 'a' && *a <= 'z') // 是一个操作数，显然不需要递归向下了
			{
				return a;
			}
			else // 是一个运算符，则需要递归的构造它的左右子树
			{
				char *q = "null";
				// Build the left sub-tree
				q = add(&(*p)->left, a + 1);

				// Build the right sub-tree
				q = add(&(*p)->right, q + 1);

				return q;
			}
		}
	}
}

// Function to print the infix expression for the tree
void inr(node *p) // recursion
{
	if (p == NULL)
	{
		return;
	}
	else
	{
		inr(p->left);
		printf("%c ", p->data);
		inr(p->right);
	}
}

// Function to print the postfix expression for the tree
void postr(node *p)
{
	if (p == NULL)
	{
		return;
	}
	else
	{
		postr(p->left);
		postr(p->right);
		printf("%c ", p->data);
	}
}

// Driver code
int main()
{
	node *s = NULL;
	char a[] = "*+ab-cd";
	add(&s, a);
	printf("The Infix expression is:\n ");
	inr(s);
	printf("\n");
	printf("The Postfix expression is:\n ");
	postr(s);
	printf("\n");
	return 0;
}

// g++ test.cpp --std=c++11 -pedantic -Wall -Wextra


```

