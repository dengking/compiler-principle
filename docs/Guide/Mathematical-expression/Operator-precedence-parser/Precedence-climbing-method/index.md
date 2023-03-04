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
    result = compute operator(result, rhs) # 这里是evaluate expression，根据 lhs opertor rhs 计算出结果

  return result
```

> NOTE:
>
> 一、先读取一个operand，然后读取operator，它本质上和  [Shunting-yard algorithm](https://en.wikipedia.org/wiki/Shunting-yard_algorithm) 是一样的: 当当前operator的precedence比之前的operator的precedence要低的时候就让之前的evaluate，对应上述code就是不进入while loop，而是直接 `return result`。
>
> 二、为什么right-associativity不进行precedence-climbing？
>
> 三、`result`

Each recursive call here handles a sequence of operator-connected atoms sharing the same **minimal precedence**.



#### An example

To get a feel for how the algorithm works, let's start with an example:

```c++
2 + 3 ^ 2 * 3 + 4
```

It's recommended to follow the execution of the algorithm through this expression with, on paper. The computation is **kicked off**(启动) by calling `compute_expr(1)`, because 1 is the **minimal operator precedence** among all operators we've defined. Here is the "call tree" the algorithm produces for this expression:

```
* compute_expr(1)                # Initial call on the whole expression
  * compute_atom() --> 2
  * compute_expr(2)              # Loop entered, operator '+'
    * compute_atom() --> 3
    * compute_expr(3)
      * compute_atom() --> 2
      * result --> 2             # Loop not entered for '*' (prec < '^')
    * result = 3 ^ 2 --> 9
    * compute_expr(3)
      * compute_atom() --> 3
      * result --> 3             # Loop not entered for '+' (prec < '*')
    * result = 9 * 3 --> 27
  * result = 2 + 27 --> 29
  * compute_expr(2)              # Loop entered, operator '+'
    * compute_atom() --> 4
    * result --> 4               # Loop not entered - end of expression
  * result = 29 + 4 --> 33
```

#### Handling precedence

Note that the algorithm makes one **recursive call** per **binary operator**. Some of these calls are short lived - they will only consume an atom and return it because the `while` loop is not entered (this happens on the second 2, as well as on the second 3 in the example expression above). Some are longer lived. The initial call to `compute_expr` will compute the whole expression.

The `while` loop is the essential ingredient here. It's the thing that makes sure that the current `compute_expr` call handles all consecutive operators with the given **minimal precedence** before exiting.

#### Handling associativity

In my opinion, one of the coolest aspects of this algorithm is the simple and elegant way it handles associativity. It's all in that condition that either sets the minimal precedence for the next call to the current one, or current one plus one.

Here's how this works. Assume we have this sub-expression somewhere:

```c++
8 * 9 * 10

  ^
  |
```

The arrow marks where the `compute_expr` call is, having entered the `while` loop. `prec` is 2. Since the associativity of `*` is left, `next_min_prec` is set to 3. The recursive call to `compute_expr(3)`, after consuming an atom, sees the next `*` token:

```
8 * 9 * 10

      ^
      |
```

Since the precedence of `*` is 2, while `min_prec` is 3, the `while` loop never runs and the call returns. So the original `compute_expr` will get to handle the second multiplication, not the internal call. Essentially, this means that the expression is grouped as follows:

```
(8 * 9) * 10
```

Which is exactly what we want from left associativity.

In contrast, for this expression:

```c++
8 ^ 9 ^ 10
```

The precedence of `^` is 3, and since it's right associative, the `min_prec` for the recursive call stays 3. This will mean that the recursive call *will* consume the next `^` operator before returning to the original `compute_expr`, grouping the expression as follows:

```c++
8 ^ (9 ^ 10)
```

#### Handling sub-expressions

The algorithm pseudo-code presented above doesn't explain how parenthesized sub-expressions are handled. Consider this expression:

```
2000 * (4 - 3) / 100
```

It's not clear how the `while` loop can handle this. The answer is `compute_atom`. When it sees a left paren, it knows that a sub-expression will follow, so it calls `compute_expr` on the sub expression (which lasts until the matching right paren), and returns its result as the result of the atom. So `compute_expr` is oblivious(不知) to the existence of sub-expressions.

Finally, in order to stay short the pseudo-code leaves some interesting details out. What follows is a full implementation of the algorithm that fills all the gaps.

### A Python implementation

