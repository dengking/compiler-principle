# Expression 

关于 expression tree，需要思考如下问题: 

1、how to evaluate expression tree？

2、how to construct an expression tree of an expression？

3、how to construct an expression of an expression tree？

4、operator precedence、[operator associativity](https://en.wikipedia.org/wiki/Operator_associativity) 



## Expression grammar

一、operator precedence

1、wikipedia [Operator-precedence parser](https://en.wikipedia.org/wiki/Operator-precedence_parser)

> An infix-notation expression grammar in [EBNF](https://en.wikipedia.org/wiki/EBNF) format will usually look like this:
>
> ```
> expression ::= equality-expression
> equality-expression ::= additive-expression ( ( '==' | '!=' ) additive-expression ) *
> additive-expression ::= multiplicative-expression ( ( '+' | '-' ) multiplicative-expression ) *
> multiplicative-expression ::= primary ( ( '*' | '/' ) primary ) *
> primary ::= '(' expression ')' | NUMBER | VARIABLE | '-' primary
> ```



如何理解`primary`？在如下文章中，它被称为atom，我觉得这个名字时更好的:

eli.thegreenplace [Parsing expressions by precedence climbing](https://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing)

龙书

其实更应该使用expression tree的思想来看待。

a、equality-expression、additive-expression、multiplicative-expression 运算符优先级降低、不断的增加层次；

equality-expression由additive-expression构成

additive-expression由multiplicative-expression构成

b、括号的处理

```
primary ::= '(' expression ')' 
```

括号中是 `expression`，这说明遇到括号我们需要recursion

c、上述grammar需要结合具体的例子来进行理解:

```c++
2 + 3 * 4 * 5 - 6
```

