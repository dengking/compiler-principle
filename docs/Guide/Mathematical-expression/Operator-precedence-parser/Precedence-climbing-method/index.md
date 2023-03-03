# Precedence-climbing-method

1、SDT vs ODT

ODT是在 eli.thegreenplace [Parsing expressions by precedence climbing](https://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing) 中提出的



2、决定何时使用operator和operand(lhs、rhs)相结合



3、three-common-thing: 

precedence、associativity、parenthesis

implicit parentheses(由precedence、associativity决定)、explicit parentheses



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

An **operator-precedence parser** can do the same more efficiently.[[1\]](https://en.wikipedia.org/wiki/Operator-precedence_parser#cite_note-Harwell2008-1) The idea is that we can **left associate** the arithmetic operations as long as we find operators with the same precedence, but we have to save a temporary result to evaluate higher precedence operators. The algorithm that is presented here does not need an **explicit stack**; instead, it uses recursive calls to implement the stack.

> NOTE:
>
> 一、上面这段话要如何来进行理解呢？
>
> "The idea is that we can **left associate** the arithmetic operations as long as we find operators with the same precedence" 这其实和  [shunting-yard algorithm](https://en.wikipedia.org/wiki/Shunting-yard_algorithm) 的处理方式相同 
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



### Precedence climbing - what it aims to achieve

So the basic goal of the algorithm is the following: treat an expression as a bunch of nested sub-expressions, where each sub-expression has in common the lowest precedence level of the the operators it contains.

> NOTE:
>
> 一、这个算法有一个非常重要的概念就是"minimal precedence"(在后面会提及)，也就是上面这段话中所述的"lowest precedence level"，它是通过operator precedence、operator associativity来构建sub-expression，其实所谓的sub-expression其实是加括号的结果，显然这个算法其实所实现的就是重新加上括号。

Here's a simple example:

```c++
2 + 3 * 4 * 5 - 6
```

Assuming that the precedence of `+` (and `-`) is 1 and the precedence of `*` (and `/`) is 2, we have:

```c++
2 + 3 * 4 * 5 - 6

|---------------|   : prec 1
    |-------|       : prec 2
```

The sub-expression multiplying the three numbers has a **minimal precedence** of 2. The sub-expression spanning the whole original expression has a **minimal precedence** of 1.

Here's a more complex example, adding a power operator `^` with precedence 3:

```c++
2 + 3 ^ 2 * 3 + 4

|---------------|   : prec 1
    |-------|       : prec 2
    |---|           : prec 3
```

#### Associativity

Binary operators, in addition to precedence, also have the concept of *associativity*. Simply put, *left associative* operators stick to the left stronger than to the right; *right associative* operators vice versa.

Some examples. Since addition is left associative, this:

```
2 + 3 + 4
```

Is equivalent to this:

```
(2 + 3) + 4
```

On the other hand, power (exponentiation) is right associative. This:

```
2 ^ 3 ^ 4
```

Is equivalent to this:

```
2 ^ (3 ^ 4)
```

The precedence climbing algorithm also needs to handle associativity correctly.

#### Nested parenthesized sub-expressions

Finally, we all know that parentheses can be used to explicitly group sub-expressions, beating operator precedence. So the following expression computes the addition *before* the multiplication:

```c++
2 * (3 + 5) * 7
```

As we'll see, the algorithm has a special provision(规定) to cleverly handle nested sub-expressions.

> NOTE:
>
> 一、翻译如下: "正如我们将看到的，该算法有一个特殊的规定来巧妙地处理嵌套的子表达式。"



### Precedence climbing - how it actually works

First let's define some terms. *Atoms* are either **numbers** or **parenthesized expressions**. *Expressions* consist of **atoms** connected by **binary operators** [[1\]](https://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing#id4). Note how these two terms are mutually dependent. This is normal in the land of grammars and parsers.

The algorithm is *operator-guided*. Its fundamental step is to consume the next atom and look at the operator following it. If the operator has precedence lower than the lowest acceptable for the current step, the algorithm returns. Otherwise, it calls itself in a loop to handle the sub-expression. In pseudo-code, it looks like this [[2\]](https://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing#id5):

> NOTE:
>
> 一、lookahead 1 symbol: "The algorithm is *operator-guided*. Its fundamental step is to consume the next atom and look at the operator following it."
>
> 

```pseudocode
compute_expr(min_prec):
  result = compute_atom()

  while cur token is a binary operator with precedence >= min_prec:
    prec, assoc = precedence and associativity of current token
    if assoc is left:
      next_min_prec = prec + 1 # precedence climbing
    else:
      next_min_prec = prec
    rhs = compute_expr(next_min_prec)
    result = compute operator(result, rhs)

  return result
```

Each recursive call here handles a sequence of operator-connected atoms sharing the same **minimal precedence**.



#### An example

To get a feel for how the algorithm works, let's start with an example:

```c++
2 + 3 ^ 2 * 3 + 4
```
