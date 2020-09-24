# [Shunting-yard algorithm](https://en.wikipedia.org/wiki/Shunting-yard_algorithm)

调度场算法

In [computer science](https://en.wikipedia.org/wiki/Computer_science), the **shunting-yard algorithm** is a method for parsing mathematical expressions specified in [infix notation](https://en.wikipedia.org/wiki/Infix_notation). It can produce either a **postfix notation** string, also known as [Reverse Polish notation](https://en.wikipedia.org/wiki/Reverse_Polish_notation) (RPN), or an [abstract syntax tree](https://en.wikipedia.org/wiki/Abstract_syntax_tree) (AST). The [algorithm](https://en.wikipedia.org/wiki/Algorithm) was invented by [Edsger Dijkstra](https://en.wikipedia.org/wiki/Edsger_Dijkstra) and named the "shunting yard"（调车场） algorithm because its operation resembles that of a [railroad shunting yard](https://en.wikipedia.org/wiki/Classification_yard). Dijkstra first described the Shunting Yard Algorithm in the [Mathematisch Centrum](https://en.wikipedia.org/wiki/Mathematisch_Centrum) report [MR 34/61](https://repository.cwi.nl/noauth/search/fullrecord.php?publnr=9251).

Like the evaluation of RPN（ [Reverse Polish notation](https://en.wikipedia.org/wiki/Reverse_Polish_notation) ）, the shunting yard algorithm is [stack](https://en.wikipedia.org/wiki/Stack_(data_structure))-based. Infix expressions are the form of mathematical notation most people are used to, for instance "3 + 4" or "3 + 4 × (2 − 1)". For the conversion there are two text [variables](https://en.wikipedia.org/wiki/Variable_(programming)) ([strings](https://en.wikipedia.org/wiki/String_(computer_science))), the input and the output. There is also a [stack](https://en.wikipedia.org/wiki/Stack_(data_structure)) that holds operators not yet added to the **output queue**. To convert, the program reads each symbol in order and does something based on that symbol. The result for the above examples would be (in [Reverse Polish notation](https://en.wikipedia.org/wiki/Reverse_Polish_notation)) "3 4 +" and "3 4 2 1 − × +", respectively.

The shunting-yard algorithm was later generalized（泛化） into [operator-precedence parsing](https://en.wikipedia.org/wiki/Operator-precedence_parser).

## A simple conversion

1. Input: 3 + 4

2. Push 3 to the output [queue](https://en.wikipedia.org/wiki/Queue_(data_structure)) (whenever a number is read it is pushed to the output)

3. [Push](https://en.wikipedia.org/wiki/Stack_(data_structure)#Basic_architecture_of_a_stack) + (or its ID) onto the operator [stack](https://en.wikipedia.org/wiki/Stack_(data_structure))

4. Push 4 to the **output queue**

5. After reading the expression, [pop](https://en.wikipedia.org/wiki/Stack_(data_structure)#Basic_architecture_of_a_stack) the operators off the stack and add them to the **output**. In this case there is only one, "+". 

6. Output: 3 4 +

   

This already shows a couple of rules:

- All numbers are pushed to the output when they are read.
- At the end of reading the expression, pop all operators off the stack and onto the output.

***SUMMARY*** : 无论哪种表达式，它们的operand的顺序是相同的，各种表达式的区别就在于它们的operator的位置不同，其实该算法所做的是决定何时将operator添加到output中，它所采用的方式是基于operator的precedence进行比较，operator stack有precedence的比较，同时也考虑了associative；由于它需要转换为postfix，所以operator看到是放到operand的后面的，当优先级更高的时候，就需要出栈，添加到output中；还需要考虑括号的情况，其实可以这样来看待括号，括号其实是一种隔离，将括号内的operator的stack和括号外的operator的stack隔离开来了；

## Graphical illustration

 [![Shunting yard.svg](https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Shunting_yard.svg/400px-Shunting_yard.svg.png)](https://en.wikipedia.org/wiki/File:Shunting_yard.svg) 

 

Graphical illustration of algorithm, using a [three-way railroad junction](https://en.wikipedia.org/wiki/Wye_junction)（三方铁路枢纽）. The input is processed one symbol at a time: if a variable or number is found, it is copied directly to the **output** a), c), e), h). If the symbol is an **operator**, it is pushed onto the **operator stack** b), d), f). If the operator's precedence is less than that of the **operators** at the top of the stack or the precedences are equal and the operator is **left associative**, then that operator is popped off the stack and added to the output g). Finally, any remaining operators are popped off the stack and added to the output i). 

***SUMMARY*** : 如果是left associative（如除法，减法），则会

## The algorithm in detail

 Important terms: [Token](https://en.wikipedia.org/wiki/Token_(parser)), [Function](https://en.wikipedia.org/wiki/Function_(mathematics)), [Operator associativity](https://en.wikipedia.org/wiki/Operator_associativity), [Precedence](https://en.wikipedia.org/wiki/Order_of_operations) 

```pseudocode
/* This implementation does not implement composite functions,functions with variable number of arguments, and unary operators. */

while there are tokens to be read do:
    read a token.
    if the token is a number, then:
        push it to the output queue.
    if the token is a function then:
        push it onto the operator stack 
    if the token is an operator, then:
        while ((there is a function at the top of the operator stack)
               or (there is an operator at the top of the operator stack with greater precedence)
               or (the operator at the top of the operator stack has equal precedence and is left associative))
              and (the operator at the top of the operator stack is not a left parenthesis):
            pop operators from the operator stack onto the output queue.
        push it onto the operator stack.
    if the token is a left paren (i.e. "("), then:
        push it onto the operator stack.
    if the token is a right paren (i.e. ")"), then:
        while the operator at the top of the operator stack is not a left paren:
            pop the operator from the operator stack onto the output queue.
        /* if the stack runs out without finding a left paren, then there are mismatched parentheses. */
        if there is a left paren at the top of the operator stack, then:
            pop the operator from the operator stack and discard it
after while loop, if operator stack not null, pop everything to output queue
if there are no more tokens to read then:
    while there are still operator tokens on the stack:
        /* if the operator token on the top of the stack is a paren, then there are mismatched parentheses. */
        pop the operator from the operator stack onto the output queue.
exit.
```

To analyze the running time complexity of this algorithm, one has only to note that each token will be read once, each number, function, or operator will be printed once, and each function, operator, or parenthesis will be pushed onto the stack and popped off the stack once—therefore, there are at most a constant number of operations executed per token, and the running time is thus O(*n*)—linear in the size of the input.

The shunting yard algorithm can also be applied to produce prefix notation (also known as [Polish notation](https://en.wikipedia.org/wiki/Polish_notation)). To do this one would simply start from the end of a string of tokens to be parsed and work backwards, reverse the output queue (therefore making the output queue an output stack), and flip the left and right parenthesis behavior (remembering that the now-left parenthesis behavior should pop until it finds a now-right parenthesis). And changing the associativity condition to right.

