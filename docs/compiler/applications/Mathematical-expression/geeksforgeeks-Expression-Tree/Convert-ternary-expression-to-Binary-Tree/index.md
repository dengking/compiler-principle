# Convert ternary expression to Binary Tree

将 ternary expression 转换为 Binary Tree，这是最最基本的parsing: 

1、geeksforgeeks [Convert ternary expression to Binary Tree using Stack](https://www.geeksforgeeks.org/convert-ternary-expression-to-binary-tree-using-stack/?ref=rp)

自底向上

2、geeksforgeeks [Convert Ternary Expression to a Binary Tree](https://www.geeksforgeeks.org/convert-ternary-expression-binary-tree/?ref=rp)

自顶向下

## geeksforgeeks [Convert ternary expression to Binary Tree using Stack](https://www.geeksforgeeks.org/convert-ternary-expression-to-binary-tree-using-stack/?ref=rp)

> NOTE: 
>
> 这是典型的bottom-up parsing

Given a string **str** that contains a ternary expression which may be nested. The task is to convert the given ternary expression to a binary tree and return the root.
**Examples:** 

```
Input: str = "a?b:c"
Output: a b c
  a
 / \
b   c
The preorder traversal of the above tree is a b c.

Input: str = "a?b?c:d:e"
Output: a b c d e
    a
   / \
  b   e
 / \
c   d
```

**Approach:** This is a stack-based approach to the given problem. Since the ternary operator has associativity from right-to-left, the string can be traversed from right to left. Take the letters one by one skipping the letters ‘`?`’ and ‘`:`’ as these letters are used to decide whether the current letter (alphabet [`a` to `z`]) will go into the stack or be used to pop the top 2 elements from the top of the stack to make them the children of the current letter which is then itself pushed into the stack. This forms the tree in a bottom-up manner and the last remaining element in the stack after the entire string is processed is the root of the tree.

### 完整实现

Below is the implementation of the above approach:

```c++
// C++ implementation of the approach
#include <bits/stdc++.h>
using namespace std;

// Node structure
struct Node
{
	char data;
	Node *left, *right;
};

// Function to create a new node
Node* createNewNode(int data)
{
	Node *node = new Node;
	node->data = data;
	node->left = NULL, node->right = NULL;
	return node;
}

// Function to print the preorder
// traversal of the tree
void preorder(Node *root)
{
	if (root == NULL)
		return;
	cout << root->data << " ";
	preorder(root->left);
	preorder(root->right);
}

// Function to convert the expression to a binary tree
Node* convertExpression(string str)
{
	stack<Node*> s;

	// If the letter is the last letter of
	// the string or is of the type :letter: or ?letter:
	// we push the node pointer containing
	// the letter to the stack
	for (int i = str.length() - 1; i >= 0;)
	{
		if ((i == str.length() - 1) || (i != 0 && ((str[i - 1] == ':' && str[i + 1] == ':') || (str[i - 1] == '?' && str[i + 1] == ':'))))
		{
			s.push(createNewNode(str[i]));
		}

		// If we do not push the current letter node to stack,
		// it means the top 2 nodes in the stack currently are the
		// left and the right children of the current node
		// So pop these elements and assign them as the
		// children of the current letter node and then
		// push this node into the stack
		else
		{
			Node *lnode = s.top();
			s.pop();
			Node *rnode = s.top();
			s.pop();
			Node *node = createNewNode(str[i]);
			node->left = lnode;
			node->right = rnode;
			s.push(node);
		}
		i -= 2;
	}

	// Finally, there will be only 1 element
	// in the stack which will be the
	// root of the binary tree
	return s.top();
}

// Driver code
int main()
{
	string str = "a?b?c:d:e";

	// Convert expression
	Node *root = convertExpression(str);

	// Print the preorder traversal
	preorder(root);

	return 0;
}
// g++ test.cpp --std=c++11 -pedantic -Wall -Wextra

```





## geeksforgeeks [Convert Ternary Expression to a Binary Tree](https://www.geeksforgeeks.org/convert-ternary-expression-binary-tree/?ref=rp)



### 完整实现

```C++
// C++ program to convert a ternary expression to
// a tree.
#include<bits/stdc++.h>
using namespace std;

// tree structure
struct Node
{
	char data;
	Node *left, *right;
};

// function create a new node
Node *newNode(char Data)
{
	Node *new_node = new Node;
	new_node->data = Data;
	new_node->left = new_node->right = NULL;
	return new_node;
}

// Function to convert Ternary Expression to a Binary
// Tree. It return the root of tree
//Notice that we pass index i by reference because we want to skip the characters in the subtree
Node *convertExpression(string str, int & i)
{
	// store current character of expression_string
	// [ 'a' to 'z']
	Node * root =newNode(str[i]);

	//If it was last character return
	//Base Case
	if(i==str.length()-1) return root;

	// Move ahead in str
	i++;
	//If the next character is '?'.Then there will be subtree for the current node
	if(str[i]=='?')
	{
		//skip the '?'
		i++;

		//construct the left subtree
		//Notice after the below recursive call i will point to ':' just before the right child of current node since we pass i by reference
		root->left = convertExpression(str,i);
		
		//skip the ':' character
		i++;

		//construct the right subtree
		root->right = convertExpression(str,i);
		return root;
	}
	//If the next character is not '?' no subtree just return it
	else return root;
}

// function print tree
void printTree( Node *root)
{
	if (!root)
		return ;
	cout << root->data <<" ";
	printTree(root->left);
	printTree(root->right);
}

// Driver program to test above function
int main()
{
	string expression = "a?b?c:d:e";
	int i=0;
	Node *root = convertExpression(expression, i);
	printTree(root) ;
	return 0;
}

```

