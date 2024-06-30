# Parsing algorithm



## wikipedia [Parsing](https://en.wikipedia.org/wiki/Parsing)

**Parsing**, **syntax analysis**, or **syntactic analysis** is the process of analysing a [string](https://en.wikipedia.org/wiki/String_(computer_science)) of [symbols](https://en.wikipedia.org/wiki/Symbol_(formal)), either in [natural language](https://en.wikipedia.org/wiki/Natural_language), [computer languages](https://en.wikipedia.org/wiki/Computer_languages) or [data structures](https://en.wikipedia.org/wiki/Data_structure), conforming to the rules of a [formal grammar](https://en.wikipedia.org/wiki/Formal_grammar). The term *parsing* comes from Latin *pars* (*orationis*), meaning [part (of speech)](https://en.wikipedia.org/wiki/Part_of_speech).

> NOTE: 
>
> 一、**syntax analysis**更加能够说明[Parsing](https://en.wikipedia.org/wiki/Parsing)的含义；

The term has slightly different meanings in different branches of [linguistics](https://en.wikipedia.org/wiki/Linguistics) and [computer science](https://en.wikipedia.org/wiki/Computer_science). Traditional [sentence](https://en.wikipedia.org/wiki/Sentence_(linguistics)) parsing is often performed as a method of understanding the exact meaning of a sentence or word, sometimes with the aid of devices such as [sentence diagrams](https://en.wikipedia.org/wiki/Sentence_diagram). It usually emphasizes the importance of grammatical divisions such as [subject](https://en.wikipedia.org/wiki/Subject_(grammar)) and [predicate](https://en.wikipedia.org/wiki/Predicate_(grammar)).

Within [computational linguistics](https://en.wikipedia.org/wiki/Computational_linguistics) the term is used to refer to the formal analysis by a computer of a sentence or other string of words into its constituents, resulting in a [parse tree](https://en.wikipedia.org/wiki/Parse_tree) showing their syntactic relation to each other, which may also contain [semantic](https://en.wikipedia.org/wiki/Semantics) and other information. Some parsing algorithms may generate a *parse forest* or list of parse trees for a [syntactically ambiguous](https://en.wikipedia.org/wiki/Syntactically_ambiguous) input.

> NOTE:  
>
> Compiler principle can also be classified into  [computational linguistics](https://en.wikipedia.org/wiki/Computational_linguistics) .


The term is also used in [psycholinguistics](https://en.wikipedia.org/wiki/Psycholinguistics) when describing language comprehension. In this context, parsing refers to the way that human beings analyze a sentence or phrase (in spoken language or text) "in terms of grammatical constituents, identifying the parts of speech, syntactic relations, etc."[[1\]](https://en.wikipedia.org/wiki/Parsing#cite_note-dictionary.com-1) This term is especially common when discussing what linguistic cues help speakers to interpret [garden-path sentences](https://en.wikipedia.org/wiki/Garden_path_sentence).

Within computer science, the term is used in the analysis of [computer languages](https://en.wikipedia.org/wiki/Computer_languages), referring to the syntactic analysis of the input code into its component parts in order to facilitate the writing of [compilers](https://en.wikipedia.org/wiki/Compilers) and [interpreters](https://en.wikipedia.org/wiki/Interpreter_(computing)). The term may also be used to describe a split or separation.

### Computer languages

#### Parser

A **parser** is a software component that takes input data (frequently text) and builds a [data structure](https://en.wikipedia.org/wiki/Data_structure) – often some kind of [parse tree](https://en.wikipedia.org/wiki/Parse_tree), [abstract syntax tree](https://en.wikipedia.org/wiki/Abstract_syntax_tree) or other hierarchical structure, giving a structural representation of the input while checking for correct syntax. 

#### Overview of process

...

The next stage is parsing or syntactic analysis, which is checking that the tokens form an allowable expression. This is usually done with reference to a [context-free grammar](https://en.wikipedia.org/wiki/Context-free_grammar) which recursively defines components that can make up an expression and the order in which they must appear. However, not all rules defining programming languages can be expressed by context-free grammars alone, for example **type validity** and **proper declaration of identifiers**. These rules can be formally expressed with [attribute grammars](https://en.wikipedia.org/wiki/Attribute_grammar).

The final phase is [semantic parsing](https://en.wikipedia.org/wiki/Semantic_analysis_(computer_science)) or analysis, which is working out the implications of the expression just validated and taking the appropriate action.[[10\]](https://en.wikipedia.org/wiki/Parsing#cite_note-10) In the case of a calculator or interpreter, the action is to evaluate the expression or program; a compiler, on the other hand, would generate some kind of code. **Attribute grammars** can also be used to define these **actions**.



### Types of parsers

The *task* of the parser is essentially to determine if and how the input can be derived from the start symbol of the grammar. This can be done in essentially two ways:

1、[Top-down parsing](https://en.wikipedia.org/wiki/Top-down_parsing) - Top-down parsing can be viewed as an attempt to find left-most derivations of an input-stream by searching for [parse trees](https://en.wikipedia.org/wiki/Parse_tree) using a top-down expansion of the given [formal grammar](https://en.wikipedia.org/wiki/Formal_grammar) rules. Tokens are consumed from left to right. Inclusive choice is used to accommodate [ambiguity](https://en.wikipedia.org/wiki/Ambiguity) by expanding all alternative right-hand-sides of grammar rules.

2、[Bottom-up parsing](https://en.wikipedia.org/wiki/Bottom-up_parsing) - A parser can start with the input and attempt to rewrite it to the start symbol. Intuitively, the parser attempts to locate the most basic elements, then the elements containing these, and so on. [LR parsers](https://en.wikipedia.org/wiki/LR_parser) are examples of bottom-up parsers. Another term used for this type of parser is [Shift-Reduce](https://en.wikipedia.org/wiki/Shift-reduce_parser) parsing.



[LL parsers](https://en.wikipedia.org/wiki/LL_parser) and [recursive-descent parser](https://en.wikipedia.org/wiki/Recursive-descent_parser) are examples of top-down parsers which cannot accommodate [left recursive](https://en.wikipedia.org/wiki/Left_recursion) [production rules](https://en.wikipedia.org/wiki/Formal_grammar#The_syntax_of_grammars). Although it has been believed that simple implementations of top-down parsing cannot accommodate direct and indirect left-recursion and may require exponential time and space complexity while parsing ambiguous [context-free grammars](https://en.wikipedia.org/wiki/Context-free_grammar), more sophisticated algorithms for top-down parsing have been created by Frost, Hafiz, and Callaghan[[11\]](https://en.wikipedia.org/wiki/Parsing#cite_note-FrostHafizCallaghan_2007-11)[[12\]](https://en.wikipedia.org/wiki/Parsing#cite_note-FrostHafizCallaghan_2008-12) which accommodate [ambiguity](https://en.wikipedia.org/wiki/Ambiguity) and [left recursion](https://en.wikipedia.org/wiki/Left_recursion) in polynomial time and which generate polynomial-size representations of the potentially exponential number of parse trees. Their algorithm is able to produce both left-most and right-most derivations of an input with regard to a given [context-free grammar](https://en.wikipedia.org/wiki/Context-free_grammar).

An important distinction with regard to parsers is whether a parser generates a *leftmost derivation* or a *rightmost derivation* (see [context-free grammar](https://en.wikipedia.org/wiki/Context-free_grammar)). LL parsers will generate a leftmost [derivation](https://en.wikipedia.org/wiki/Parse_tree) and LR parsers will generate a rightmost derivation (although usually in reverse).

Some *graphical parsing* algorithms have been designed for [visual programming languages](https://en.wikipedia.org/wiki/Visual_programming_languages).[[13\]](https://en.wikipedia.org/wiki/Parsing#cite_note-13)[[14\]](https://en.wikipedia.org/wiki/Parsing#cite_note-14) Parsers for visual languages are sometimes based on [graph grammars](https://en.wikipedia.org/wiki/Graph_grammar).

### Lookahead

Lookahead establishes the maximum incoming tokens that a parser can use to decide which rule it should use. Lookahead is especially relevant to [LL](https://en.wikipedia.org/wiki/LL_parser), [LR](https://en.wikipedia.org/wiki/LR_parser), and [LALR parsers](https://en.wikipedia.org/wiki/LALR_parser), where it is often explicitly indicated by affixing the lookahead to the algorithm name in parentheses, such as LALR(1).

Most [programming languages](https://en.wikipedia.org/wiki/Programming_language), the primary target of parsers, are carefully defined in such a way that a parser with limited lookahead, typically one, can parse them, because parsers with limited lookahead are often more efficient. One important change to this trend came in 1990 when [Terence Parr](https://en.wikipedia.org/wiki/Terence_Parr) created [ANTLR](https://en.wikipedia.org/wiki/ANTLR) for his Ph.D. thesis, a [parser generator](https://en.wikipedia.org/wiki/Parser_generator) for efficient LL(*k*) parsers, where *k* is any fixed value.



## 分类

- [Top-down parsing](https://en.wikipedia.org/wiki/Top-down_parsing)
  - [LL parsers](https://en.wikipedia.org/wiki/LL_parser) 
  - [Recursive-descent parser](https://en.wikipedia.org/wiki/Recursive-descent_parser) 
- [Bottom-up parsing](https://en.wikipedia.org/wiki/Bottom-up_parsing)
  - [LR parsers](https://en.wikipedia.org/wiki/LR_parser) 



### Table-driven parser



#### gpt-4-vision

**Table-driven parsing** is a method of parsing text (such as programming language code, data files, etc.) where the parsing decisions are controlled by a data structure (often a table) rather than by hard-coded logic. This approach is commonly used in the implementation of parsers for compilers and interpreters.

Two common types of table-driven parsers are:

1. **LL(1) Parsers (Top-Down Parsers):** These parsers use a **predictive parsing table** to decide which **production rule** to apply based on **the current input token** and **the top of the stack**. The "LL" stands for **Left-to-right scanning of the input** and **Leftmost derivation of the parse tree**, and the "1" indicates that the parser uses one lookahead token at a time.

2. **LR Parsers (Bottom-Up Parsers):** These parsers use a **state machine** where the transitions between states are determined by a **parsing table**. The "LR" stands for **Left-to-right scanning of the input** and **Rightmost derivation in reverse of the parse tree**. LR parsers can handle a larger class of grammars than LL parsers. Variants of LR parsers include SLR, LALR, and CLR/GLR.

Here's a simplified example of how a table-driven parser might work:

```python
# This is a highly simplified example of a table-driven parser for illustrative purposes.

# Define the parsing table
# This table would be generated based on the grammar of the language being parsed.
# The keys are states, and the values are actions based on the next input token.
parse_table = {
    ('S', 'a'): ('shift', 'A'),
    ('S', 'b'): ('shift', 'B'),
    ('A', 'c'): ('reduce', 'S -> a'),
    ('B', 'd'): ('reduce', 'S -> b'),
    # ... more rules ...
}

# Define the input to parse
input_tokens = ['a', 'c', 'b', 'd']
stack = ['S']  # Start state

# Parsing loop
while input_tokens:
    current_state = stack[-1]
    next_token = input_tokens[0]
    action, value = parse_table.get((current_state, next_token), ('error',))

    if action == 'shift':
        stack.append(value)
        input_tokens.pop(0)  # Consume the token
    elif action == 'reduce':
        # Apply the production rule (value) to reduce the stack
        # This is a placeholder for the actual reduction logic
        stack.pop()
        stack.append(value[-1])  # Push the result of the reduction
    elif action == 'error':
        print("Parsing error!")
        break

# Output the result
print("Parsed stack:", stack)
```

In a real-world scenario, the parsing table would be much more complex and would be generated by a parser generator tool (like yacc, bison, or ANTLR) based on the formal grammar of the language. The parser would also need to handle more actions, such as accepting the input or handling errors more gracefully.

### LL VS LR VS Recursive descend VS Recursive ascend

[Recursive descent parser](https://en.wikipedia.org/wiki/Recursive_descent_parser) use [backtracking](https://en.wikipedia.org/wiki/Backtracking) to match.

LL parsers are table-based parsers, they use parsing table. Parsing table is constructed from the grammar and acts as a transformation function. Using parsing table and *k* [tokens](https://en.wikipedia.org/wiki/Token_(parser)) of [lookahead](https://en.wikipedia.org/wiki/Parsing#Lookahead), a LL parser can become *predictive parser* and  avoid  [backtracking](https://en.wikipedia.org/wiki/Backtracking). 



#### stackoverflow [What is the difference between LL and LR parsing?](https://stackoverflow.com/questions/5975741/what-is-the-difference-between-ll-and-lr-parsing)



[A](https://stackoverflow.com/a/6824545)

At a high level, the difference between LL parsing and LR parsing is that LL parsers begin at the start symbol and try to apply productions to arrive at the **target string**, whereas LR parsers begin at the target string and try to arrive back at the **start symbol**.

An LL parse is a left-to-right, leftmost derivation. That is, we consider the input symbols from the left to the right and attempt to construct a leftmost derivation. This is done by beginning at the start symbol and repeatedly expanding out the **leftmost nonterminal** until we arrive at the **target string**. 

An LR parse is a left-to-right, rightmost derivation, meaning that we scan from the left to right and attempt to construct a rightmost derivation. The parser continuously picks a substring of the input and attempts to reverse it back to a nonterminal.

During an LL parse, the parser continuously chooses between two actions:

1、**Predict**: Based on the leftmost nonterminal and some number of lookahead tokens, choose which production ought to be applied to get closer to the input string.

2、**Match**: Match the leftmost guessed terminal symbol with the leftmost unconsumed symbol of input.

As an example, given this grammar:

- S → E
- E → T + E
- E → T
- T → `int`

Then given the string `int + int + int`, an LL(2) parser (which uses two tokens of lookahead) would parse the string as follows:

```
Production       Input              Action
---------------------------------------------------------
S                int + int + int    Predict S -> E
E                int + int + int    Predict E -> T + E
T + E            int + int + int    Predict T -> int
int + E          int + int + int    Match int
+ E              + int + int        Match +
E                int + int          Predict E -> T + E
T + E            int + int          Predict T -> int
int + E          int + int          Match int
+ E              + int              Match +
E                int                Predict E -> T
T                int                Predict T -> int
int              int                Match int
                                    Accept
```

Notice that in each step we look at the leftmost symbol in our production. If it's a terminal, we match it, and if it's a nonterminal, we predict what it's going to be by choosing one of the rules.

In an LR parser, there are two actions:

1、**Shift**: Add the next token of input to a buffer for consideration.

2、**Reduce**: Reduce a collection of terminals and nonterminals in this buffer back to some nonterminal by reversing a production.

As an example, an LR(1) parser (with one token of lookahead) might parse that same string as follows:

```
Workspace        Input              Action
---------------------------------------------------------
                 int + int + int    Shift
int              + int + int        Reduce T -> int
T                + int + int        Shift
T +              int + int          Shift
T + int          + int              Reduce T -> int
T + T            + int              Shift
T + T +          int                Shift
T + T + int                         Reduce T -> int
T + T + T                           Reduce E -> T
T + T + E                           Reduce E -> T + E
T + E                               Reduce E -> T + E
E                                   Reduce S -> E
S                                   Accept
```

The two parsing algorithms you mentioned (LL and LR) are known to have different characteristics. LL parsers tend to be easier to write by hand, but they are less powerful than LR parsers and accept a much smaller set of grammars than LR parsers do. LR parsers come in many flavors (LR(0), SLR(1), LALR(1), LR(1), IELR(1), GLR(0), etc.) and are far more powerful. They also tend to have much more complex and are almost always generated by tools like `yacc` or `bison`. LL parsers also come in many flavors (including LL(*), which is used by the [`ANTLR`](http://www.antlr.org/) tool), though in practice LL(1) is the most-widely used.

As a shameless plug, if you'd like to learn more about LL and LR parsing, I just finished teaching a compilers course and have [some handouts and lecture slides on parsing](http://www.stanford.edu/class/archive/cs/cs143/cs143.1128/) on the course website. I'd be glad to elaborate on any of them if you think it would be useful.



[A](https://stackoverflow.com/a/18239653)

Josh Haberman in his article [LL and LR Parsing Demystified](http://blog.reverberate.org/2013/07/ll-and-lr-parsing-demystified.html) claims that LL parsing directly corresponds with the [Polish Notation](http://en.wikipedia.org/wiki/Polish_notation), whereas LR corresponds to [Reverse Polish Notation](http://en.wikipedia.org/wiki/Reverse_Polish_notation). The difference between PN and RPN is the order of traversing the binary tree of the equation:

![binary tree of an equation](https://i.stack.imgur.com/QLYBe.png)

```
+ 1 * 2 3  // Polish (prefix) expression; pre-order traversal.
1 2 3 * +  // Reverse Polish (postfix) expression; post-order traversal.
```

According to Haberman, this illustrates the main difference between LL and LR parsers:

> The primary difference between how LL and LR parsers operate is that an LL parser outputs a pre-order traversal of the parse tree and an LR parser outputs a post-order traversal.

For the in-depth explanation, examples and conclusions check out Haberman's [article](http://blog.reverberate.org/2013/07/ll-and-lr-parsing-demystified.html).



#### 预测分析表 VS LR语法分析表

LL和LR都是表驱动的，这两个表就是分别驱动两者的表。

语法分析的过程是不断根据产生式进行转换的过程。



两者的构造都是基于对grammar的分析，两者的构造过程都是沿着产生式进行derive，所不同的是，预测分析表一直derive到了terminal；而LR语法分析表则是将所有的可能的转换全部包含了：

预测分析表的构造使用是non-terminal symbol的FIRST和FOLLOW，FIRST和FOLLOW所包含的都是terminal，其实它的目的是知道当遇到某个terminal的时候，使用哪个production可以得到这个terminal。即它侧重的是对于一个non-terminal的production，它能够推导出什么，这样它就能够据此来决定是否使用这个production。



LR语法分析表正如其名称所揭示地，它其实是对语法的分析，对语法中所有的可能的转换进行分析，构造出来它的转换所对应的automaton。显然，因为它的转换都是基于grammar所构造出来的，因此，它的所有的转换都是有效的转换，因此只要待分析的串不符合这个automaton的转换，那么它就是无效的了。因此我们的待分析的串一定是对应了automaton中的一条路径。使用我们的文法，按照某种推导方式是一定能够derive这个串的。在待分析的串中，仅仅包含的是terminal，而grammar中，是两者都包含的，所以在进行分析的时候，一定要将terminal规约为non-terminal，这样才能够使分析继续下去。LR语法分析是推导的逆过程，显然我们是要沿着推导方向逆流而上，因为推导的过程的中间过程肯定是会存在non-terminal的，而我们是逆向进行推导，所以肯定需要将一些terminal规约为non-terminal。



为什么LR是right-most derivation？

预测分析表其实也是一个转换函数，要使用哪个产生式进行derivate

LR是一个automaton，状态，转换



语法分析表由两个部分组成：

- action
- goto



#### 从LR(0)自动机到LR语法分析表

LR语法分析表的构造是基于LR(0)自动机的

本质还是转换，无论是在terminal上的转换还是在non-terminal上的转换

action主要定义的是在terminal上的转换，而goto则定义的是在non-terminal上的转换。

SLR语法分析表的构造过程主要让我感到困惑的是它将action定义成了 状态和terminal的函数？

SLR语法分析表的ACTION的构造过程中有这样的规则：



TODO: LR语法分析器的格局configuration VS LR(0)自动机的状态



## 素材

素材: [zhihu-为什么所有的教科书中都不赞成手写自底向上的语法分析器？ - 冯东的回答 - 知乎](https://www.zhihu.com/question/21475266/answer/18346898) 

因为 [bottom-up parser](https://www.zhihu.com/search?q=bottom-up parser&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"18346898"}) 的可读性极差，根本无法手写。

实际上 **bottom-up parser** 是一个不该在实际工程中应用的纯学术的东西。最初被提出的时候，人们认为它的优点主要是 **recognition strength** 比较强。LR(1) parser 的 recognition strength 就可以超过 k 为任意值的 LL(k) parser[[1\]](#ref_1)。而且 LL(k) parser generator 的运算复杂度是 O(|T| ^ k)，所以当时人们认为其[自动化生成](https://www.zhihu.com/search?q=自动化生成&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"18346898"})算法不可能被工程应用。一度公认 LL(k) 只能手写实现，而且 k 只能实际为一。

不过后来 Terence Parr，ANTLR 的作者，开发了 LL'(k) parser，把复杂度降低到 O(|T| x k)。LL'(k) 的 strength 小于 LL(k) 但大于 LL(k-1)。这就抵消了 LR 算法的两个重要优势：自动生成和 recognition strength。如此一来，LL 一族虽然不能从理论上完全取代 LR，但是考虑到其代码可读性，已经完全消除了 LR 的工程必要性。

接下来还有几个实际问题也抵消了 bottom-up parser 的必要性：

- 目前流行的 LR parser generator 是 LALR，其 parsing strength 弱于 LR(1)。所以还不能和任意 LL(k) 相比。
- 把 LL(k) 语法改写为 LR(1) 是非常反直观的做法。
- Bottom-up parser 的优势建立在严格的[数学基础](https://www.zhihu.com/search?q=数学基础&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"18346898"})上，要求语言必须是 [context-free](https://www.zhihu.com/search?q=context-free&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"18346898"}) 语法。实际中严格的 context-free 语法很少。可读性极好的 LL parser 可以任意加入 [ad-hoc trick](https://www.zhihu.com/search?q=ad-hoc trick&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"18346898"}) 来分析 context-sensitive 语法，乃至于使用回溯来分析 undetermined 语法。而 bottom-up parser 就无能为力了。
- 实际中[设计语言](https://www.zhihu.com/search?q=设计语言&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"18346898"})可以尽量向 LL(1) 靠拢。注意这一条并不和上一条矛盾。一个语言可以是 99% 的  LL(1) 语法加上几个 undetermined 语法的特例。这时用 bottom-up parser 是最尴尬的，[parsing strength](https://www.zhihu.com/search?q=parsing strength&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"18346898"}) 在 99% 的情况下白白浪费（之所以说是浪费是因为这种 strength 是以 [readability](https://www.zhihu.com/search?q=readability&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"18346898"}) 为代价的），在 1% 的特例中还非常难于处理。



[@vczh](http://www.zhihu.com/people/0970f947b898ecc0ec035f9126dd4e08)

 的看法可能来自一些误解。我的观点不是 LL 多么牛逼。而是：



- LL'(k) 的发明说明 LL 没有人们原本想像的那么弱。
- LL 经常用 recursive-descend 实现。而这种实现是最容易加入 ad-hoc trick 的方式。



[@vczh](http://www.zhihu.com/people/0970f947b898ecc0ec035f9126dd4e08)

 举的例子基本上都是 LL 在纯理论方面比 LR 弱的例子。这恰恰是我已经说明过的问题。比如 [@vczh](http://www.zhihu.com/people/0970f947b898ecc0ec035f9126dd4e08) 说道：「再说了，语言设计成 LL(1) 的话，整个语法憋手蹩脚，你会发现根本没有一个流行的语言是这么做的」。我不能同意。写一个纯粹的 LL(1) 语法当然很反直观，但是 99% 的 LL(1) 语法加上个别特例是非常常见的。Lua 语言就是几乎 LL(1) 语法。



**参考**

1. [^](#ref_1_0)Knuth, D. E. (July 1965). "On the translation of languages from left to right" (PDF). Information and Control. 8 (6): 607–639. doi:10.1016/S0019-9958(65)90426-2. Archived from the original (PDF) on 15 March 2012. Retrieved 29 May 2011.

[现在的编译前端技术还是用NFA和递归下降实现lexer和parser吗？ - RednaxelaFX的回答 - 知乎](https://www.zhihu.com/question/34968369/answer/60588787)  

然后当然也还有一些前端是用lex/yacc系的做法，例如Ruby的[parser](https://www.zhihu.com/search?q=parser&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"60588787"})；或者是用ANTLR那样的`LL(*)`的做法，例如Groovy的parser。

（注意ANTLR的LL(*)不是给定k的LL(k)而比后者更强，因为其lookahead允许无限多，本质上跟PEG类似）

如果改为：

> 最新的理论编译技术的前端还是使用Lex/yacc里面的实现原理吗？

那答案会是：当然不是，早就不是了。

就像 

[@vczh](http://www.zhihu.com/people/0970f947b898ecc0ec035f9126dd4e08)

 的回答说的，[语法分析](https://www.zhihu.com/search?q=语法分析&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"60588787"})上，自底向上方面其实GLR系的算法早就有了，实现上也越来越好，早就比yacc/bison用的LALR(1)好。

而自顶向下方面在2000后也有 PEG、`LL(*)` （ANTLRv3）和 `ALL(*)` （ANTLRv4）的发展，颇有抢回地盘的趋势。



素材: [shift reduce，预测分析，递归下降分析（这是解析方法）和LL(K) LR(K) SLR以LALR的关系？ - 彭飞的回答 - 知乎](https://www.zhihu.com/question/29636774/answer/45070915) 

Parsing 算法大致分为两派，top-down 和bottom-up。其中[top-down parsing](https://www.zhihu.com/search?q=top-down parsing&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"45070915"}) 也就是你说的递归下降分析，一般实现[top-down parser](https://www.zhihu.com/search?q=top-down parser&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"45070915"}) 都要求parsing 是线性运行时间，所以大多数top-down parser 也就是predict parser 即[预测分析器](https://www.zhihu.com/search?q=预测分析器&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"45070915"})，因为这种parser 在运行时每次都要至少向前看一个符号（然后去查每个[产生式](https://www.zhihu.com/search?q=产生式&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"45070915"})的**predictive set**）才能决定用哪个产生式，即predict parser 是由“向前看”（预测）来驱动的。这点建议你看看《Language Implementation Patterns》中给出的LL(1) parser 的模板代码，马上就理解了。同时因为它总是把左边先看到的符合产生式的一串符号构建成一个[语法树](https://www.zhihu.com/search?q=语法树&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"45070915"})，所以也叫LL(k) parsing，其中第二个L就是最左推导的意思，而k 是指最多向前看几个符号（我刚刚说了，至少一个，有时需要多个），且k 为常数（可以用环形缓冲区实现）。当加入[回溯策略](https://www.zhihu.com/search?q=回溯策略&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"45070915"})时，这个k 就可以是无穷大了。

LL(1)、LL(2) 和更大的k 之间有什么区别对于新手来说确实不好判断，所以我建议你可以从top-down parser 开始自己给一门语言写个parser，开始只选择几个特性来写，然后逐步添加grammar。比如你想给JavaScript写个parser，那么参考Lambda Calculus 你可以先实现：1）单参数[匿名函数](https://www.zhihu.com/search?q=匿名函数&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"45070915"})的定义；2）[函数调用](https://www.zhihu.com/search?q=函数调用&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"45070915"})。这个你只需要LL(1) 就可以了。然后逐步加入其他grammar，当你遇到`function f (x) {...}` 的时候你就发现它和你之前写的`function (x) {...}` 冲突了（因为前者规约为一个语句，后者规约为一个表达式），这时候你就需要上LL(2).

相对照来说，bottom-up parser 就对应LR(k) parser 了。它和LL(k) 不一样的地方在于：1）自右向左、自底向上构建语法树；2）不由“向前看符号”（预测）来驱动。你说的shift、reduce 就是这种算法中的两个动作：shift（吞入下一个符号），reduce（将已近吞入的、最右侧的、符合某个产生式的一串符号构建成一个语法树）。但是有时候你会发现在某一步parser 不知道应该shift 还是reduce，这时候SLR 就发挥作用了，它通过向前看一个符号来解决这个冲突。所以说：**LL通过预测驱动，而LR通过预测来解决冲突**。至于SLR 和LALR 有什么区别，请移步  

[SLR与LALR之间的区别？ - vczh 的回答](https://link.zhihu.com/?target=http%3A//zhi.hu/fEhl)

  推荐你跟着SLR 算法，对着一段需要被parse 的程序走一遍，就马上明白了。

最后再说一下，这张图应该是想告诉你**理论上**每种grammar class（以及对应的parsing algirithm）之间描述能力（[解析能力](https://www.zhihu.com/search?q=解析能力&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"45070915"})）的差别。而且这张图讨论的应该是grammar class 而不是language class。

纯理论地来看，它们之间解析能力的差异是很难看出来的，所以给几个例子，如图：

![img](https://pic2.zhimg.com/80/2f30858394111ea25c6d08f5f2b891a9_1440w.webp)

你可以看出其实这些特殊的grammar 都是很诡异的，一般不会出现在[编程语言](https://www.zhihu.com/search?q=编程语言&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"45070915"})中。所以还是像我上面说的那样，自己挑一门语言实现个parser （不能用[parser generator](https://www.zhihu.com/search?q=parser generator&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"45070915"})），大多数parsing algorithm 的能力区别你就都明白了。

当然，如果你不满足这种“工程方法”的话，想看一个grammar 可不可以被LL(k) 解析，就手动为每个产生式构建predictive set，看看set 之间有没有冲突。而LALR（SLR）的话有个更简单的方法，用Bison 的--report=all 选项生成table，所有的信息都在里面。

素材: LR

zhihu [SLR与LALR之间的区别？](https://www.zhihu.com/question/27922607)

zhihu [编译原理-几种LR算法的演化1——LR(0)](https://zhuanlan.zhihu.com/p/92249157)



素材: LEMON语法分析生成器

[zhihu-有哪些优秀的1万行以下的源码？ - codedump的回答 - 知乎](https://www.zhihu.com/question/21737583/answer/25571103) 

推荐两个,Lua源码,比1W行略多,但是对于一门完备的工业级别[脚本语言](https://www.zhihu.com/search?q=脚本语言&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"25571103"}),这个性价比挺高了;另一个是Lemon,一个LALR(1)的[语法分析器](https://www.zhihu.com/search?q=语法分析器&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"25571103"}),不到5K行吧,读完它词法/语法分析那部分能领悟很多.

啊,我还忘记了最近在看的Leveldb代码,不算[测试用例](https://www.zhihu.com/search?q=测试用例&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"25571103"})的话也是这个量级,[大师作品](https://www.zhihu.com/search?q=大师作品&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A"25571103"}),不多说了.



