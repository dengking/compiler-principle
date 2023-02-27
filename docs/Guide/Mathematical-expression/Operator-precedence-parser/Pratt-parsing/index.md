# Pratt parsing

oilshell [Pratt Parsing Index and Updates](https://www.oilshell.org/blog/2017/03/31.html)

github [andychu](https://github.com/andychu)/**[pratt-parsing-demo](https://github.com/andychu/pratt-parsing-demo)**



oilshell [Pratt Parsing and Precedence Climbing Are the Same Algorithm](https://www.oilshell.org/blog/2016/11/01.html)

> I used Eli Bendersky's 2012 [article on precedence climbing](http://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing) to write it. I cited his article in the patch, as well as Keith Clarke's 1986 paper [The Top-Down Parsing of Expressions](https://scholar.google.com/scholar?cluster=17307359715187030691), which I found in a relevant [Wikipedia article](https://en.wikipedia.org/wiki/Operator-precedence_parser).
>
> (For contrast, GNU `expr` uses a plain recursive descent parser, which works fine, but is more verbose and in theory less efficient.)
>
> The `expr` command only supports binary operators, so we just need a single recursive function `eval_expr()` to handle all operators, as in Bendersky's article.
>
> But shell arithmetic is borrowed from C and also has these constructs:
>
> - prefix operators: `-3` and `+x`
> - the ternary operator: `x > 2 ? y : 0`
> - right associative operators: `2 ** 3 ** 4` is `2 ** (3 ** 4)`
> - array indexing: `a[0]`





matklad.github [Simple but Powerful Pratt Parsing](https://matklad.github.io/2020/04/13/simple-but-powerful-pratt-parsing.html#Simple-but-Powerful-Pratt-Parsing) 

