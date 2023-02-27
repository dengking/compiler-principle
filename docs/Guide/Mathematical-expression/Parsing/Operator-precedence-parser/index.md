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



## Experts

### [Eli Bendersky](https://eli.thegreenplace.net/) 

https://eli.thegreenplace.net/tag/compilation

https://eli.thegreenplace.net/tag/recursive-descent-parsing





## Algorithms



### Shunting yard algorithm

参见`Guide\Expression-tree\Shunting-yard-algorithm`。





### 比较



#### ycombinator [Shunting-yard algorithm](https://news.ycombinator.com/item?id=19190208) 



## Implementation



[bourguet](https://github.com/bourguet)/**[operator_precedence_parsing](https://github.com/bourguet/operator_precedence_parsing)**

这是在 ycombinator [Shunting-yard algorithm](https://en.wikipedia.org/wiki/Shunting-yard_algorithm) 中发现的

