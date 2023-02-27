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

a、equality-expression、additive-expression、multiplicative-expression 运算符优先级降低、不断的增加层次；

b、括号的处理

```
primary ::= '(' expression ')' 
```

括号中是 `expression`，这说明遇到括号我们需要recursion
