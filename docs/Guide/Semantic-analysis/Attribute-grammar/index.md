# Attribute grammar



## wikipedia [Attribute grammar](https://en.wikipedia.org/wiki/Attribute_grammar)

An **attribute grammar** is a formal way to supplement a [formal grammar](https://en.wikipedia.org/wiki/Formal_grammar) with **semantic information** processing. **Semantic information** is stored in [attributes](https://en.wikipedia.org/wiki/Attribute_(computing)) associated with [terminal and nonterminal symbols](https://en.wikipedia.org/wiki/Terminal_and_nonterminal_symbols) of the grammar. The values of attributes are result of attribute evaluation rules associated with productions of the grammar. Attributes allow to transfer information from anywhere in the [abstract syntax tree](https://en.wikipedia.org/wiki/Abstract_syntax_tree) to anywhere else, in a controlled and formal way.



一、Synthesized attributes

二、Inherited attributes

三、Special types of attribute grammars

 

1、[L-attributed grammar](https://en.wikipedia.org/wiki/L-attributed_grammar): *inherited attributes* can be evaluated in one left-to-right traversal of the abstract syntax tree

2、[LR-attributed grammar](https://en.wikipedia.org/wiki/LR-attributed_grammar): an L-attributed grammar whose *inherited attributes* can also be evaluated in [bottom-up parsing](https://en.wikipedia.org/wiki/Bottom-up_parsing).

3、[ECLR-attributed grammar](https://en.wikipedia.org/wiki/ECLR-attributed_grammar): a subset of LR-attributed grammars where equivalence classes can be used to optimize the evaluation of inherited attributes.

4、[S-attributed grammar](https://en.wikipedia.org/wiki/S-attributed_grammar): a simple type of attribute grammar, using only *synthesized attributes*, but no *inherited attributes*



## wikipedia [S-attributed grammar](https://en.wikipedia.org/wiki/S-attributed_grammar)



## see also

cs.csub.edu [Ch 3.4 Attribute Grammars](https://www.cs.csub.edu/~melissa/cs350-f15/notes/notes04.html#:~:text=Static%20Semantics%20refers%20to%20the,sensitive%20meaning%20of%20a%20program.)

cs.fsu.edu [**5. Semantics**](https://www.cs.fsu.edu/~engelen/courses/COP402003/notes4.html)

cs.fsu.edu [Semantic Analysis](https://www.cs.fsu.edu/~engelen/courses/COP402001/notes4_4.pdf)

zhihu [读书笔记 | 编译原理 ——一个简单的语法制导翻译器（上）](https://zhuanlan.zhihu.com/p/428054996)