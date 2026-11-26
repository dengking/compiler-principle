# geeksforgeeks [Evaluation of Expression Tree](https://www.geeksforgeeks.org/evaluation-of-expression-tree/?ref=rp)

> NOTE: 
>
> 典型的递归、自顶向下、binary tree-DFS-post order后序-return value

As all the operators in the tree are binary hence each node will have either 0 or 2 children. As it can be inferred from the examples above , the integer values would appear at the leaf nodes , while the interior nodes represent the operators.
To evaluate the syntax tree , a recursive approach can be followed .

```c++
Algorithm :
Let t be the syntax tree
If  t is not null then
      If t.info is operand then  
         Return  t.info
      Else
         A = solve(t.left)
         B = solve(t.right)
         return A operator B
         where operator is the info contained in t
```

## 完整程序

```C++
// C++ program to evaluate an expression tree
#include <bits/stdc++.h>
using namespace std;

// Class to represent the nodes of syntax tree
class node
{
public:
	string info;
	node *left = NULL, *right = NULL;
	node(string x)
	{
		info = x;
	}
};

// Utility function to return the integer value
// of a given string
int toInt(string s)
{
	int num = 0;

	// Check if the integral value is
	// negative or not
	// If it is not negative, generate the number
	// normally
	if (s[0] != '-')
		for (int i = 0; i < s.length(); i++)
			num = num * 10 + (int(s[i]) - 48);
	// If it is negative, calculate the +ve number
	// first ignoring the sign and invert the
	// sign at the end
	else
		for (int i = 1; i < s.length(); i++)
		{
			num = num * 10 + (int(s[i]) - 48);
			num = num * -1;
		}

	return num;
}

// This function receives a node of the syntax tree
// and recursively evaluates it
int eval(node *root)
{
	// empty tree
	if (!root)
		return 0;

	// leaf node i.e, an integer
	if (!root->left && !root->right)
		return toInt(root->info);

	// Evaluate left subtree
	int l_val = eval(root->left);

	// Evaluate right subtree
	int r_val = eval(root->right);

	// Check which operator to apply
	if (root->info == "+")
		return l_val + r_val;

	if (root->info == "-")
		return l_val - r_val;

	if (root->info == "*")
		return l_val * r_val;

	return l_val / r_val;
}

//driver function to check the above program
int main()
{
	// create a syntax tree
	node *root = new node("+");
	root->left = new node("*");
	root->left->left = new node("5");
	root->left->right = new node("-4");
	root->right = new node("-");
	root->right->left = new node("100");
	root->right->right = new node("20");
	cout << eval(root) << endl;

	delete (root);

	root = new node("+");
	root->left = new node("*");
	root->left->left = new node("5");
	root->left->right = new node("4");
	root->right = new node("-");
	root->right->left = new node("100");
	root->right->right = new node("/");
	root->right->right->left = new node("20");
	root->right->right->right = new node("2");

	cout << eval(root);
	return 0;
}

// g++ test.cpp --std=c++11 -pedantic -Wall -Wextra


```

