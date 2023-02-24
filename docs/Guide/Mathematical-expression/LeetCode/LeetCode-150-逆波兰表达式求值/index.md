# leetcode [150. 逆波兰表达式求值](https://leetcode-cn.com/problems/evaluate-reverse-polish-notation/)



## 我的解题



```C++

class Solution
{
public:
	int evalRPN(vector<string> &tokens)
	{
		stack<int> st;
		for (auto &&token : tokens)
		{
			if (isOperator(token))
			{
				int operand2 = st.top();
				st.pop();
				int operand1 = st.top();
				st.pop();
				st.push(cal(operand1, operand2, token));
			}
			else
			{
				st.push(stoi(token));
			}
		}
		return st.top();
	}
	bool isOperator(string &s)
	{
		return s == "+" || s == "-" || s == "*" || s == "/";
	}
	int cal(int operand1, int operand2, string &Operator)
	{
		if (Operator == "+")
		{
			return operand1 + operand2;
		}
		else if (Operator == "-")
		{
			return operand1 - operand2;
		}
		else if (Operator == "*")
		{
			return operand1 * operand2;
		}
		else if (Operator == "/")
		{
			return operand1 / operand2;
		}
		else
		{
			return 0;
		}
	}
};
```

