# Polish prefix notation

"infix notation" 即 "中缀表达式"，"polish notation" 即 "波兰式"。

## build && evaluate

一、evaluate

在 infogalactic [Polish notation](https://infogalactic.com/info/Polish_notation) 中，给出的是自底向上地evaluate的方式

二、build

在 geeksforgeeks [Building Expression tree from Prefix Expression](https://www.geeksforgeeks.org/building-expression-tree-from-prefix-expression/) 给出了递归、自顶向下地构建expression tree 过程

## infogalactic [Polish notation](https://infogalactic.com/info/Polish_notation)

**Polish notation** (**PN**), also known as **normal Polish notation** (**NPN**),[[1\]](https://infogalactic.com/info/Polish_notation#cite_note-Jorke_1989-1) **Łukasiewicz notation**, **Warsaw notation**, **Polish prefix notation** or simply **prefix notation**, is a form of notation for [logic](https://infogalactic.com/info/Logic), [arithmetic](https://infogalactic.com/info/Arithmetic), and [algebra](https://infogalactic.com/info/Algebra). Its distinguishing feature is that it places [operators](https://infogalactic.com/info/Operator_(mathematics)) to the left of their [operands](https://infogalactic.com/info/Operand). If the [arity](https://infogalactic.com/info/Arity) of the operators is fixed, the result is a syntax lacking parentheses or other brackets that can still be parsed without ambiguity. The [Polish](https://infogalactic.com/info/Poland) logician [Jan Łukasiewicz](https://infogalactic.com/info/Jan_Łukasiewicz) invented this notation in 1924 in order to simplify [sentential logic](https://infogalactic.com/info/Propositional_calculus).

> NOTE: 
>
> 是由波兰人  [Jan Łukasiewicz](https://infogalactic.com/info/Jan_Łukasiewicz) 发明的
>
> 

When Polish notation is used as a syntax for mathematical expressions by [programming language](https://infogalactic.com/info/Programming_language) [interpreters](https://infogalactic.com/info/Interpreter_(computing)), it is readily parsed into [abstract syntax trees](https://infogalactic.com/info/Abstract_syntax_tree) and can, in fact, define a [one-to-one representation](https://infogalactic.com/info/Bijection) for the same. Because of this, [Lisp](https://infogalactic.com/info/Lisp_(programming_language)) ([see below](https://infogalactic.com/info/Polish_notation#Computer_programming)) and related programming languages define their entire syntax in terms of prefix notation (and others use postfix notation).

### Order of operations

An example shows the ease with which a complex statement in prefix notation can be deciphered through order of operations:

```c++
− × ÷ 15 − 7 + 1 1 3 + 2 + 1 1 =
− × ÷ 15 − 7 2     3 + 2 + 1 1 =
− × ÷ 15 5         3 + 2 + 1 1 =
− × 3              3 + 2 + 1 1 =
− 9                  + 2 + 1 1 =
− 9                  + 2 2     =
− 9                  4         =
5
```

> NOTE: 
>
> 自后向前进行evaluation

Here is an implementation (in pseudocode) of prefix evaluation using a stack. Note that under this implementation the input string is scanned from right to left. This differs from the algorithm described above in which the string is processed from left to right. Both algorithms compute the same value for all valid strings.

```pseudocode
Scan the given prefix expression from right to left
for each symbol
 {
  if operand then
    push onto stack
  if operator then
   {
    operand1=pop stack
    operand2=pop stack
    compute operand1 operator operand2
    push result onto stack
   }
 }
return top of stack as result
```

Applying this algorithm to the example above yields the following:

```c++
− × ÷ 15 − 7 + 1 1 3 + 2 + 1 1 =
− × ÷ 15 − 7 + 1 1 3 + 2 2     =
− × ÷ 15 − 7 + 1 1 3 4         =
− × ÷ 15 − 7 2     3 4         =
− × ÷ 15 5         3 4         =
− × 3              3 4         =
− 9                  4         =
5
```

### Example

This uses the same expression as before and the algorithm above.

```C++
− × ÷ 15 − 7 + 1 1 3 + 2 + 1 1
```



| Token |  Action  |  Stack   |                            Notes                             |
| :---: | :------: | :------: | :----------------------------------------------------------: |
|   1   | Operand  |    1     |                       Push onto stack.                       |
|   1   | Operand  |   1 1    |                       Push onto stack.                       |
|   +   | Operator |    2     | Pop the two operands (1, 1), calculate (1 + 1 = 2) and push onto stack. |
|   2   | Operand  |   2 2    |                       Push onto stack.                       |
|   +   | Operator |    4     | Pop the two operands (2, 2), calculate (2 + 2 = 4) and push onto stack. |
|   3   | Operand  |   3 4    |                       Push onto stack.                       |
|   1   | Operand  |  1 3 4   |                       Push onto stack.                       |
|   1   | Operand  | 1 1 3 4  |                       Push onto stack.                       |
|   +   | Operator |  2 3 4   | Pop the two operands (1, 1), calculate (1 + 1 = 2) and push onto stack. |
|   7   | Operand  | 7 2 3 4  |                       Push onto stack.                       |
|   −   | Operator |  5 3 4   | Pop the two operands (7, 2), calculate (7 − 2 = 5) and push onto stack. |
|  15   | Operand  | 15 5 3 4 |                       Push onto stack.                       |
|   ÷   | Operator |  3 3 4   | Pop the two operands (15, 5), calculate (15 ÷ 5 = 3) and push onto stack. |
|   ×   | Operator |   9 4    | Pop the two operands (3, 3), calculate (3 × 3 = 9) and push onto stack. |
|   −   | Operator |    5     | Pop the two operands (9, 4), calculate (9 − 4 = 5) and push onto stack. |

The result is at the top of the stack.