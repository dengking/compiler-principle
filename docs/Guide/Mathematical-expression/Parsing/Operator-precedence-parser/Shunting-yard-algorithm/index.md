# Shunting-yard algorithm

一、中文意思: "调度场算法"

二、application

1、expression evaluation

它可以采用syntax-directed-translation的思想实现evaluate expression

2、map infix notation to postfix notation

## wikipedia [Shunting-yard algorithm](https://en.wikipedia.org/wiki/Shunting-yard_algorithm)

In [computer science](https://en.wikipedia.org/wiki/Computer_science), the **shunting-yard algorithm** is a method for parsing mathematical expressions specified in [infix notation](https://en.wikipedia.org/wiki/Infix_notation). It can produce either a **postfix notation** string, also known as [Reverse Polish notation](https://en.wikipedia.org/wiki/Reverse_Polish_notation) (RPN), or an [abstract syntax tree](https://en.wikipedia.org/wiki/Abstract_syntax_tree) (AST). The [algorithm](https://en.wikipedia.org/wiki/Algorithm) was invented by [Edsger Dijkstra](https://en.wikipedia.org/wiki/Edsger_Dijkstra) and named the "shunting yard"（调车场） algorithm because its operation resembles that of a [railroad shunting yard](https://en.wikipedia.org/wiki/Classification_yard). Dijkstra first described the Shunting Yard Algorithm in the [Mathematisch Centrum](https://en.wikipedia.org/wiki/Mathematisch_Centrum) report [MR 34/61](https://repository.cwi.nl/noauth/search/fullrecord.php?publnr=9251).

Like the evaluation of RPN（ [Reverse Polish notation](https://en.wikipedia.org/wiki/Reverse_Polish_notation) ）, the shunting yard algorithm is [stack](https://en.wikipedia.org/wiki/Stack_(data_structure))-based. Infix expressions are the form of mathematical notation most people are used to, for instance "3 + 4" or "3 + 4 × (2 − 1)". For the conversion there are two text [variables](https://en.wikipedia.org/wiki/Variable_(programming)) ([strings](https://en.wikipedia.org/wiki/String_(computer_science))), the input and the output. There is also a [stack](https://en.wikipedia.org/wiki/Stack_(data_structure)) that holds operators not yet added to the **output queue**. To convert, the program reads each symbol in order and does something based on that symbol. The result for the above examples would be (in [Reverse Polish notation](https://en.wikipedia.org/wiki/Reverse_Polish_notation)) "3 4 +" and "3 4 2 1 − × +", respectively.

The shunting yard algorithm will correctly parse all valid infix expressions, but does not reject all **invalid expressions**. For example, "1 2 +" is not a valid **infix expression**, but would be parsed as "1 + 2". The algorithm can however reject expressions with **mismatched parentheses**.

The **shunting-yard algorithm** was later generalized(泛化) into [operator-precedence parsing](https://en.wikipedia.org/wiki/Operator-precedence_parser).

### A simple conversion

1、Input: 3 + 4

2、Push 3 to the output [queue](https://en.wikipedia.org/wiki/Queue_(data_structure)) (whenever a number is read it is pushed to the output)

3、[Push](https://en.wikipedia.org/wiki/Stack_(data_structure)#Basic_architecture_of_a_stack) + (or its ID) onto the operator [stack](https://en.wikipedia.org/wiki/Stack_(data_structure)) 

4、Push 4 to the **output queue**

5、After reading the expression, [pop](https://en.wikipedia.org/wiki/Stack_(data_structure)#Basic_architecture_of_a_stack) the operators off the stack and add them to the **output**. In this case there is only one, "+". 

6、Output: 3 4 +



This already shows a couple of rules:

1、All numbers are pushed to the output when they are read.

2、At the end of reading the expression, pop all operators off the stack and onto the output.



### Graphical illustration

 [![Shunting yard.svg](https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Shunting_yard.svg/400px-Shunting_yard.svg.png)](https://en.wikipedia.org/wiki/File:Shunting_yard.svg) 

 

Graphical illustration of algorithm, using a [three-way railroad junction](https://en.wikipedia.org/wiki/Wye_junction)（三方铁路枢纽）. The input is processed one symbol at a time: if a variable or number is found, it is copied directly to the **output** a), c), e), h). If the symbol is an **operator**, it is pushed onto the **operator stack** b), d), f). If the operator's precedence is less than that of the **operators** at the top of the stack or the precedences are equal and the operator is **left associative**, then that operator is popped off the stack and added to the output g). Finally, any remaining operators are popped off the stack and added to the output i). 

> NOTE: 
>
> left associative（如除法，减法）

### The algorithm in detail

 Important terms: [Token](https://en.wikipedia.org/wiki/Token_(parser)), [Function](https://en.wikipedia.org/wiki/Function_(mathematics)), [Operator associativity](https://en.wikipedia.org/wiki/Operator_associativity), [Precedence](https://en.wikipedia.org/wiki/Order_of_operations) 

```pseudocode
/* The functions referred to in this algorithm are simple single argument functions such as sine, inverse or factorial. */
/* This implementation does not implement composite functions, functions with a variable number of arguments, or unary operators. */

while there are tokens to be read:
    read a token
    if the token is:
    - a number:
        put it into the output queue
    - a function:
        push it onto the operator stack 
    - an operator o1:
        while (
            there is an operator o2 at the top of the operator stack which is not a left parenthesis, 
            and (o2 has greater precedence than o1 or (o1 and o2 have the same precedence and o1 is left-associative))
        ):
            pop o2 from the operator stack into the output queue
        push o1 onto the operator stack
    - a left parenthesis (i.e. "("):
        push it onto the operator stack
    - a right parenthesis (i.e. ")"):
        while the operator at the top of the operator stack is not a left parenthesis:
            {assert the operator stack is not empty}
            /* If the stack runs out without finding a left parenthesis, then there are mismatched parentheses. */
            pop the operator from the operator stack into the output queue
        {assert there is a left parenthesis at the top of the operator stack}
        pop the left parenthesis from the operator stack and discard it
        if there is a function token at the top of the operator stack, then:
            pop the function from the operator stack into the output queue
/* After the while loop, pop the remaining items from the operator stack into the output queue. */
while there are tokens on the operator stack:
    /* If the operator token on the top of the stack is a parenthesis, then there are mismatched parentheses. */
    {assert the operator on top of the stack is not a (left) parenthesis}
    pop the operator from the operator stack onto the output queue
```

> NOTE: 
>
> 一、无论哪种表达式(infix、postfix)，它们的operand的顺序是相同的(显然shunting-yard-algorithm能够保证这一点)，各种表达式的区别就在于它们的operator的位置不同，其实该算法所做的是决定何时将**operator**添加到**output**中。
>
> 二、parentheses、operator precedence、operator associativity决定了expression的计算顺序，那shunting yard algorithm是如何实现这些内容的呢？
>
> shunting yard algorithm的只能处理binary operator，不能处理conditional (ternary) operator，这在一定程度上简化了处理，这样我们就能够只要看到一个operator知道它只能够和两个operand相结合。
>
> 1、operator precedence: 用monotonic stack来实现
>
> a、当看到lower precedence operator的时候，就需要将stack中的已有的superior precedence operator pop到input queue中让它和其中的operands结合，这样做是因为superior precedence operator比lower precedence operator拥有更高的优先级来和operand结合。下面是另外一种思考方式:
>
> 是否要pop operator(结合、reduce)，要看它后面是否有比它优先级更高的operator，那如何判断是否有呢？这就可以通过monotonic stack来实现，当碰到优先级更低的，则就触发它进行flush、reduce
>
> 
>
> 2、parentheses: supreme precedence
>
> a、可以认为括号的优先级最高: 可以看到algorithm中，一旦遇到close-parenthesis，则立马将pop operator到input queue中
>
> b、其实可以这样来看待括号，括号其实是一种隔离，将括号内的operator的stack和括号外的operator的stack隔离开来了；
>
> 3、associativity
>
> associativity决定了equal precedence operator的计算顺序(加括号方式):
>
> a、both left-associative: 比如下面情形:
>
> ```
> 3+4-5
> ```
>
> 显然operator stack中的operator是`+`，第二个是`-`，由于`+`是left-associative，所以此时需要将它pop到input queue中
>
> b、left-associative、right-associative
>
> c、both right-associative
>
> ```
> 2^3^4
> ```
>
> 这种其实是比较简单的，直接stack reverse即可
>
> 三、shunting yard algorithm有shift reduce parsing: 
>
> operator被pop出**operator stack**到input queue中，这相当于reduce
>
> 四、stack machine
>
> 

To analyze the running time complexity of this algorithm, one has only to note that each token will be read once, each number, function, or operator will be printed once, and each function, operator, or parenthesis will be pushed onto the stack and popped off the stack once—therefore, there are at most a constant number of operations executed per token, and the running time is thus O(*n*)—linear in the size of the input.

The **shunting yard algorithm** can also be applied to produce **prefix notation** (also known as [Polish notation](https://en.wikipedia.org/wiki/Polish_notation)). To do this one would simply start from the end of a string of tokens to be parsed and work backwards, reverse the output queue (therefore making the output queue an output stack), and flip the left and right parenthesis behavior (remembering that the now-left parenthesis behavior should pop until it finds a now-right parenthesis). And changing the associativity condition to right.

> NOTE:
>
> 一、two direction dual





## TODO

stackoverflow [Algorithm for converting expression to binary tree [closed]](https://stackoverflow.com/questions/42441416/algorithm-for-converting-expression-to-binary-tree)

codeproject [Binary Tree Expression Solver](https://www.codeproject.com/Articles/10316/Binary-Tree-Expression-Solver)

cnblogs [shunting-yard 调度场算法、中缀表达式转逆波兰表达式](https://www.cnblogs.com/magisk/p/8620303.html)

geeksforgeeks [Program to convert Infix notation to Expression Tree](https://www.geeksforgeeks.org/program-to-convert-infix-notation-to-expression-tree/?ref=rp)



https://news.ycombinator.com/item?id=19190208



### oilshell [Code for the Shunting Yard Algorithm, and More](http://www.oilshell.org/blog/2017/04/22.html)

> NOTE:
>
> 在这篇文章中，其实并没有详细说明shunting yard algorithm的细节，它正如它的标题所言提供了shunting yard algorithm的code
>
> > Jean-Marc Bourguet [answered my questions](https://www.reddit.com/r/oilshell/comments/5l70p7/pratt_parsing_and_precedence_climbing_are_the/) with example code:
> >
> > - [C89 expressions parsed with the shunting yard algorithm in Python](https://github.com/bourguet/operator_precedence_parsing/blob/master/shunting_yard.md)
> > - [shunting_yard.py](https://github.com/bourguet/operator_precedence_parsing/blob/master/shunting_yard.py) (~270 lines)
> >
> > And the repo has comparisons with more algorithms:
> >
> > - [bourguet/operator_precedence_parsing on Github](https://github.com/bourguet/operator_precedence_parsing) (标记不错，提供了多种parser的实现)

### codereview.stackexchange [Infix-to-postfix parser using Dijkstra's shunting yard algorithm](https://codereview.stackexchange.com/questions/46136/infix-to-postfix-parser-using-dijkstras-shunting-yard-algorithm)





