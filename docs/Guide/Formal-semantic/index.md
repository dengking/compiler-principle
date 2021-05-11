# Formal semantic

## draft1

我不知道本节标题的formal semantic是否准确，这是上周彭总提出的一个概念。其实对symbol expression的evaluation就是对它的语义的理解，关于此，我首先想到的是基于AST的evaluation，如果都是基于AST的话，那么operator的定义、含义的解释就非常重要了。

我的一个问题是: 是否都是基于AST的evaluation来实现semantic的理解？关于这个问题，可以阅读: 

1) `programming-language\docs\Theory\Programming-paradigm\Symbolic-programming\utexas-cs378.pdf`

2) 龙书中的描述

3) Google "tree and formal semantic"

4) [Formal Semantics and Formal Pragmatics, Lecture 1](http://people.umass.edu/partee/MGU_2009/materials/MGU091_2-up.pdf)  这篇文章不错，已经将他保存到了本地



## draft2

将sentence看做是expression，然后将expression转换为tree，然后基于tree进行翻译，将它翻译为一些列的指令，这就完成了语义的理解。最最典型的案例就是[computer algebra](https://en.wikipedia.org/wiki/Computer_algebra)。