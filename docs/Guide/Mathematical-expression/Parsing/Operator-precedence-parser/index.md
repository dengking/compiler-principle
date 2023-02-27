# Operator-precedence parser



## wikipedia [Operator-precedence parser](https://en.wikipedia.org/wiki/Operator-precedence_parser)

In [computer science](https://en.wikipedia.org/wiki/Computer_science), an **operator precedence parser** is a [bottom-up parser](https://en.wikipedia.org/wiki/Bottom-up_parsing) that interprets an [operator-precedence grammar](https://en.wikipedia.org/wiki/Operator-precedence_grammar). For example, most [calculators](https://en.wikipedia.org/wiki/Calculator) use operator precedence parsers to convert from the human-readable [infix notation](https://en.wikipedia.org/wiki/Infix_notation) relying on [order of operations](https://en.wikipedia.org/wiki/Order_of_operations) to a format that is optimized for evaluation such as [Reverse Polish notation](https://en.wikipedia.org/wiki/Reverse_Polish_notation) (RPN).

[Edsger Dijkstra](https://en.wikipedia.org/wiki/Edsger_Dijkstra)'s [shunting yard algorithm](https://en.wikipedia.org/wiki/Shunting_yard_algorithm) is commonly used to implement operator precedence parsers. Other algorithms include the precedence climbing method and the [top down operator precedence method](https://en.wikipedia.org/wiki/Pratt_parser).



### Relationship to other parsers

[Raku](https://en.wikipedia.org/wiki/Raku_(programming_language)) sandwiches an **operator-precedence parser** between two [recursive descent parsers](https://en.wikipedia.org/wiki/Recursive_descent_parser) in order to achieve a balance of speed and dynamism. [GCC](https://en.wikipedia.org/wiki/GNU_Compiler_Collection)'s C and C++ parsers, which are hand-coded recursive descent parsers, are both sped up by an **operator-precedence parser** that can quickly examine arithmetic expressions. **Operator precedence parsers** are also embedded within [compiler-compiler](https://en.wikipedia.org/wiki/Compiler-compiler)-generated parsers to noticeably speed up the recursive descent approach to expression parsing.

> NOTE:
>
> 一、在 ycombinator [Shunting-yard algorithm](https://en.wikipedia.org/wiki/Shunting-yard_algorithm) 中有如下描述:
>
> > They're both nicer than grammar-based approaches when you have many levels of precedence, like C.



### Precedence climbing method



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







### Pratt parsing

> NOTE:





## Experts

### [Eli Bendersky](https://eli.thegreenplace.net/) 

https://eli.thegreenplace.net/tag/compilation

https://eli.thegreenplace.net/tag/recursive-descent-parsing



### Andy Chu

oilshell [Pratt Parsing Index and Updates](https://www.oilshell.org/blog/2017/03/31.html) 



## Algorithms



### Shunting yard algorithm

参见`Guide\Expression-tree\Shunting-yard-algorithm`。





### 比较



#### ycombinator [Shuntxing-yard algorithm](https://news.ycombinator.com/item?id=19190208) 



## Implementation



[bourguet](https://github.com/bourguet)/**[operator_precedence_parsing](https://github.com/bourguet/operator_precedence_parsing)**

这是在 ycombinator [Shunting-yard algorithm](https://en.wikipedia.org/wiki/Shunting-yard_algorithm) 中发现的

