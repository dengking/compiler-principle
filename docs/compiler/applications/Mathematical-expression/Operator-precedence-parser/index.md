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

> NOTE:
>
> 一、参见 `Precedence-climbing-method` 章节



### Pratt parsing

> NOTE:





## Experts

### [Eli Bendersky](https://eli.thegreenplace.net/) 

https://eli.thegreenplace.net/tag/compilation

https://eli.thegreenplace.net/tag/recursive-descent-parsing



### Andy Chu

oilshell [Pratt Parsing Index and Updates](https://www.oilshell.org/blog/2017/03/31.html) 



## Algorithms

一、three-common-thing in expression: 

1、precedence

2、associativity

3、parentheses

二、parentheses=sub-expression ( eli.thegreenplace [Parsing expressions by precedence climbing](https://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing) )

explicit parentheses

implicit parentheses: 算法根据operator的precedence、associativity来加上implicit parentheses

三、lookahead 1 symbol: 

1、根据next symbol来决定是否构造sub-expression，可以肯定的是每个atom后面都跟着一个operator

2、eli.thegreenplace [Parsing expressions by precedence climbing](https://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing) 

> The algorithm is *operator-guided*. Its fundamental step is to consume the next atom and look at the operator following it. If the operator has precedence lower than the lowest acceptable for the current step, the algorithm returns. Otherwise, it calls itself in a loop to handle the sub-expression.

因为是binary operator，因此每个atom后面肯定有一个operator，因此是可以根据此来进行判定的。

四、operator-directed-translation: eli.thegreenplace [Parsing expressions by precedence climbing](https://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing) 

五、

1、shunting yard algorithm是使用monotonic stack来构建由具备相同precedence、associativity的operator连接的operand构成一个sub-expression

2、precedence climbing algorithm使用变量minimal precedence作为recursive function的入参实现的

六、决定何时使用operator和operand(lhs、rhs)相结合

### Shunting yard algorithm

参见`Guide\Expression-tree\Shunting-yard-algorithm`。



### 比较

一、ycombinator [Shuntxing-yard algorithm](https://news.ycombinator.com/item?id=19190208) 

二、eli.thegreenplace [Parsing expressions by precedence climbing](https://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing)

> ***Update (2016-11-02):** Andy Chu [notes](http://www.oilshell.org/blog/2016/11/01.html) that precedence climbing and [TDOP](https://eli.thegreenplace.net/2010/01/02/top-down-operator-precedence-parsing) are pretty much the same algorithm, formulated a bit differently. I tend to agree, and also note that [Shunting Yard](https://eli.thegreenplace.net/2009/03/20/a-recursive-descent-parser-with-an-infix-expression-evaluator) is again the same algorithm, except that the explicit recursion is replaced by a stack.*



## Implementation



[bourguet](https://github.com/bourguet)/**[operator_precedence_parsing](https://github.com/bourguet/operator_precedence_parsing)**

这是在 ycombinator [Shunting-yard algorithm](https://en.wikipedia.org/wiki/Shunting-yard_algorithm) 中发现的



## TODO



stackoverflow [Equation (expression) parser with precedence?](https://stackoverflow.com/questions/28256/equation-expression-parser-with-precedence)

codeproject [Simple Guide to Mathematical Expression Parsing](https://www.codeproject.com/articles/88435/simple-guide-to-mathematical-expression-parsing)

