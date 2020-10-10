# [Evaluation of Expression Tree](https://www.geeksforgeeks.org/evaluation-of-expression-tree/)





```python
# Python program to evaluate expression tree 

# Class to represent the nodes of syntax tree 
class node: 
	def __init__(self, value): 
		self.left = None
		self.data = value 
		self.right = None

# This function receives a node of the syntax tree 
# and recursively evaluate it 
def evaluateExpressionTree(root): 

	# empty tree 
	if root is None: 
		return 0

	# leaf node 
	if root.left is None and root.right is None: 
		return int(root.data) 

	# evaluate left tree 
	left_sum = evaluateExpressionTree(root.left) 

	# evaluate right tree 
	right_sum = evaluateExpressionTree(root.right) 

	# check which operation to apply 
	if root.data == '+': 
		return left_sum + right_sum 
	
	elif root.data == '-': 
		return left_sum - right_sum 
	
	elif root.data == '*': 
		return left_sum * right_sum 
	
	else: 
		return left_sum / right_sum 

# Driver function to test above problem 
if __name__=='__main__': 
	
	# creating a sample tree 
	root = node('+') 
	root.left = node('*') 
	root.left.left = node('5') 
	root.left.right = node('4') 
	root.right = node('-') 
	root.right.left = node('100') 
	root.right.right = node('20') 
	print evaluateExpressionTree(root) 

	root = None

	#creating a sample tree 
	root = node('+') 
	root.left = node('*') 
	root.left.left = node('5') 
	root.left.right = node('4') 
	root.right = node('-') 
	root.right.left = node('100') 
	root.right.right = node('/') 
	root.right.right.left = node('20') 
	root.right.right.right = node('2') 
	print evaluateExpressionTree(root) 

# This code is contributed by Harshit Sidhwa 

```

