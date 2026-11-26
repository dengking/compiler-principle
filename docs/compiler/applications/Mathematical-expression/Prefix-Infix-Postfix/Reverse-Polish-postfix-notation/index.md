# Reverse Polish notation



## infogalactic [Reverse Polish notation](https://infogalactic.com/info/Reverse_Polish_notation)

**Reverse Polish notation** (**RPN**) is a mathematical notation in which every [operator](https://infogalactic.com/info/Operation_(mathematics)) follows all of its [operands](https://infogalactic.com/info/Operand), in contrast to [Polish notation](https://infogalactic.com/info/Polish_notation) (PN), which puts the operator in the prefix position. It is also known as **postfix notation** and is parenthesis-free as long as operator [arities](https://infogalactic.com/info/Arity) are fixed. The description "Polish" refers to the [nationality](https://infogalactic.com/info/Nationality) of [logician](https://infogalactic.com/info/Logician) [Jan Łukasiewicz](https://infogalactic.com/info/Jan_Łukasiewicz),[[1\]](https://infogalactic.com/info/Reverse_Polish_notation#cite_note-.C5.81ukasiewicz_1957-1) who invented (prefix) Polish notation in the 1920s.

### Postfix algorithm

### Converting from infix notation

Main article: [Shunting-yard algorithm](https://infogalactic.com/info/Shunting-yard_algorithm)

[Edsger Dijkstra](https://infogalactic.com/info/Edsger_Dijkstra) invented the [shunting-yard algorithm](https://infogalactic.com/info/Shunting-yard_algorithm) to convert infix expressions to postfix (RPN), so named because its operation resembles that of a [railroad shunting yard](https://infogalactic.com/info/Classification_yard).

There are other ways of producing postfix expressions from infix notation. Most [operator-precedence parsers](https://infogalactic.com/info/Operator-precedence_parser) can be modified to produce postfix expressions; in particular, once an [abstract syntax tree](https://infogalactic.com/info/Abstract_syntax_tree) has been constructed, the corresponding postfix expression is given by a simple [post-order traversal](https://infogalactic.com/info/Post-order_traversal) of that tree.

