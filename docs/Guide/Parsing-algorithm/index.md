# Parsing algorithm



## wikipedia [Parsing](https://en.wikipedia.org/wiki/Parsing)

**Parsing**, **syntax analysis**, or **syntactic analysis** is the process of analysing a [string](https://en.wikipedia.org/wiki/String_(computer_science)) of [symbols](https://en.wikipedia.org/wiki/Symbol_(formal)), either in [natural language](https://en.wikipedia.org/wiki/Natural_language), [computer languages](https://en.wikipedia.org/wiki/Computer_languages) or [data structures](https://en.wikipedia.org/wiki/Data_structure), conforming to the rules of a [formal grammar](https://en.wikipedia.org/wiki/Formal_grammar). The term *parsing* comes from Latin *pars* (*orationis*), meaning [part (of speech)](https://en.wikipedia.org/wiki/Part_of_speech).[[1\]](https://en.wikipedia.org/wiki/Parsing#cite_note-dictionary.com-1)

> NOTE: **syntax analysis**更加能够说明[Parsing](https://en.wikipedia.org/wiki/Parsing)的含义；

The term has slightly different meanings in different branches of [linguistics](https://en.wikipedia.org/wiki/Linguistics) and [computer science](https://en.wikipedia.org/wiki/Computer_science). Traditional [sentence](https://en.wikipedia.org/wiki/Sentence_(linguistics)) parsing is often performed as a method of understanding the exact meaning of a sentence or word, sometimes with the aid of devices such as [sentence diagrams](https://en.wikipedia.org/wiki/Sentence_diagram). It usually emphasizes the importance of grammatical divisions such as [subject](https://en.wikipedia.org/wiki/Subject_(grammar)) and [predicate](https://en.wikipedia.org/wiki/Predicate_(grammar)).

Within [computational linguistics](https://en.wikipedia.org/wiki/Computational_linguistics) the term is used to refer to the formal analysis by a computer of a sentence or other string of words into its constituents, resulting in a [parse tree](https://en.wikipedia.org/wiki/Parse_tree) showing their syntactic relation to each other, which may also contain [semantic](https://en.wikipedia.org/wiki/Semantics) and other information. Some parsing algorithms may generate a *parse forest* or list of parse trees for a [syntactically ambiguous](https://en.wikipedia.org/wiki/Syntactically_ambiguous) input.

> NOTE:  
>
> Compiler principle can also be classified into  [computational linguistics](https://en.wikipedia.org/wiki/Computational_linguistics) .


The term is also used in [psycholinguistics](https://en.wikipedia.org/wiki/Psycholinguistics) when describing language comprehension. In this context, parsing refers to the way that human beings analyze a sentence or phrase (in spoken language or text) "in terms of grammatical constituents, identifying the parts of speech, syntactic relations, etc."[[1\]](https://en.wikipedia.org/wiki/Parsing#cite_note-dictionary.com-1) This term is especially common when discussing what linguistic cues help speakers to interpret [garden-path sentences](https://en.wikipedia.org/wiki/Garden_path_sentence).

Within computer science, the term is used in the analysis of [computer languages](https://en.wikipedia.org/wiki/Computer_languages), referring to the syntactic analysis of the input code into its component parts in order to facilitate the writing of [compilers](https://en.wikipedia.org/wiki/Compilers) and [interpreters](https://en.wikipedia.org/wiki/Interpreter_(computing)). The term may also be used to describe a split or separation.



### Types of parsers

The *task* of the parser is essentially to determine if and how the input can be derived from the start symbol of the grammar. This can be done in essentially two ways:

1、[Top-down parsing](https://en.wikipedia.org/wiki/Top-down_parsing) - Top-down parsing can be viewed as an attempt to find left-most derivations of an input-stream by searching for [parse trees](https://en.wikipedia.org/wiki/Parse_tree) using a top-down expansion of the given [formal grammar](https://en.wikipedia.org/wiki/Formal_grammar) rules. Tokens are consumed from left to right. Inclusive choice is used to accommodate [ambiguity](https://en.wikipedia.org/wiki/Ambiguity) by expanding all alternative right-hand-sides of grammar rules.

2、[Bottom-up parsing](https://en.wikipedia.org/wiki/Bottom-up_parsing) - A parser can start with the input and attempt to rewrite it to the start symbol. Intuitively, the parser attempts to locate the most basic elements, then the elements containing these, and so on. [LR parsers](https://en.wikipedia.org/wiki/LR_parser) are examples of bottom-up parsers. Another term used for this type of parser is [Shift-Reduce](https://en.wikipedia.org/wiki/Shift-reduce_parser) parsing.



> NOTE: 
>
> Top-down:
>
> |                            parser                            | doc  | code |
> | :----------------------------------------------------------: | :--: | :--: |
> |    [LL parsers](https://en.wikipedia.org/wiki/LL_parser)     |      |      |
> | [Recursive-descent parser](https://en.wikipedia.org/wiki/Recursive-descent_parser) |      |      |
> |                                                              |      |      |
>
> Bottom-up:
>
>  [LR parsers](https://en.wikipedia.org/wiki/LR_parser) 、[Shift-Reduce](https://en.wikipedia.org/wiki/Shift-reduce_parser) 

[LL parsers](https://en.wikipedia.org/wiki/LL_parser) and [recursive-descent parser](https://en.wikipedia.org/wiki/Recursive-descent_parser) are examples of top-down parsers which cannot accommodate [left recursive](https://en.wikipedia.org/wiki/Left_recursion) [production rules](https://en.wikipedia.org/wiki/Formal_grammar#The_syntax_of_grammars). Although it has been believed that simple implementations of top-down parsing cannot accommodate direct and indirect left-recursion and may require exponential time and space complexity while parsing ambiguous [context-free grammars](https://en.wikipedia.org/wiki/Context-free_grammar), more sophisticated algorithms for top-down parsing have been created by Frost, Hafiz, and Callaghan[[11\]](https://en.wikipedia.org/wiki/Parsing#cite_note-FrostHafizCallaghan_2007-11)[[12\]](https://en.wikipedia.org/wiki/Parsing#cite_note-FrostHafizCallaghan_2008-12) which accommodate [ambiguity](https://en.wikipedia.org/wiki/Ambiguity) and [left recursion](https://en.wikipedia.org/wiki/Left_recursion) in polynomial time and which generate polynomial-size representations of the potentially exponential number of parse trees. Their algorithm is able to produce both left-most and right-most derivations of an input with regard to a given [context-free grammar](https://en.wikipedia.org/wiki/Context-free_grammar).

An important distinction with regard to parsers is whether a parser generates a *leftmost derivation* or a *rightmost derivation* (see [context-free grammar](https://en.wikipedia.org/wiki/Context-free_grammar)). LL parsers will generate a leftmost [derivation](https://en.wikipedia.org/wiki/Parse_tree) and LR parsers will generate a rightmost derivation (although usually in reverse).

Some *graphical parsing* algorithms have been designed for [visual programming languages](https://en.wikipedia.org/wiki/Visual_programming_languages).[[13\]](https://en.wikipedia.org/wiki/Parsing#cite_note-13)[[14\]](https://en.wikipedia.org/wiki/Parsing#cite_note-14) Parsers for visual languages are sometimes based on [graph grammars](https://en.wikipedia.org/wiki/Graph_grammar).
