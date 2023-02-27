# Precedence-climbing-method

1、SDT vs ODT

2、决定何时使用operator和operand(lhs、rhs)相结合



## wikipedia [Operator-precedence parser](https://en.wikipedia.org/wiki/Operator-precedence_parser) # Precedence climbing method

An infix-notation expression grammar in [EBNF](https://en.wikipedia.org/wiki/EBNF) format will usually look like this:

```c++
expression ::= equality-expression
equality-expression ::= additive-expression ( ( '==' | '!=' ) additive-expression ) *
additive-expression ::= multiplicative-expression ( ( '+' | '-' ) multiplicative-expression ) *
multiplicative-expression ::= primary ( ( '*' | '/' ) primary ) *
primary ::= '(' expression ')' | NUMBER | VARIABLE | '-' primary
```

> NOTE:
>
> 一、上述grammar不是left-recursive的，因此它能够使用recursive method来实现
>
> 二、`primary ::= '-' primary` 这是负数

With many levels of precedence, implementing this grammar with a predictive recursive-descent parser can become inefficient. Parsing a number, for example, can require five function calls: one for each non-terminal in the grammar until reaching *primary*.

> NOTE:
>
> 一、primary可以看作是base case

An **operator-precedence parser** can do the same more efficiently.[[1\]](https://en.wikipedia.org/wiki/Operator-precedence_parser#cite_note-Harwell2008-1) The idea is that we can left associate the arithmetic operations as long as we find operators with the same precedence, but we have to save a temporary result to evaluate higher precedence operators. The algorithm that is presented here does not need an **explicit stack**; instead, it uses recursive calls to implement the stack.

> NOTE:
>
> 一、上面这段话要如何来进行理解呢？
>
> 核心思想是从syntax-directed-translation切换到operator-directed-translation

The algorithm is not a pure **operator-precedence parser** like the Dijkstra **shunting yard algorithm**. It assumes that the *primary* nonterminal is parsed in a separate subroutine, like in a **recursive descent parser**.

#### Pseudocode

The pseudocode for the algorithm is as follows. The parser starts at function *parse_expression*. Precedence levels are greater than or equal to 0.



```python
parse_expression()
    return parse_expression_1(parse_primary(), 0)

parse_expression_1(lhs, min_precedence)
    lookahead := peek next token
    while lookahead is a binary operator whose precedence is >= min_precedence
        op := lookahead
        advance to next token
        rhs := parse_primary ()
        lookahead := peek next token
        while lookahead is a binary operator whose precedence is greater
                 than op's, or a right-associative operator
                 whose precedence is equal to op's
            rhs := parse_expression_1 (rhs, precedence of op + (1 if lookahead precedence is greater, else 0))
            lookahead := peek next token
        lhs := the result of applying op with operands lhs and rhs
    return lhs
```





## eli.thegreenplace [Parsing expressions by precedence climbing](https://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing)

