[TOC]



# [Top-down parsing](https://en.wikipedia.org/wiki/Top-down_parsing)

In [computer science](https://en.wikipedia.org/wiki/Computer_science), **top-down parsing** is a [parsing](https://en.wikipedia.org/wiki/Parsing) strategy where one first looks at the highest level of the [parse tree](https://en.wikipedia.org/wiki/Parse_tree) and works down the parse tree by using the rewriting rules of a [formal grammar](https://en.wikipedia.org/wiki/Formal_grammar).[[1\]](https://en.wikipedia.org/wiki/Top-down_parsing#cite_note-GruneJacobs2007-1) [LL parsers](https://en.wikipedia.org/wiki/LL_parser) are a type of parser that uses a top-down parsing strategy.

> NOTE: [Rewriting](https://en.wikipedia.org/wiki/Rewriting) rules means expanding, substituting an  [nonterminal symbol](https://en.wikipedia.org/wiki/Nonterminal_symbol) with [production body](https://en.wikipedia.org/wiki/Production_(computer_science)).

Top-down parsing is a strategy of analyzing unknown data relationships by hypothesizing general [parse tree](https://en.wikipedia.org/wiki/Parse_tree) structures and then considering whether the known fundamental structures are compatible with the hypothesis. It occurs in the analysis of both natural [languages](https://en.wikipedia.org/wiki/Language) and [computer languages](https://en.wikipedia.org/wiki/Computer_language).

Top-down parsing can be viewed as an attempt to find [left-most derivations](https://en.wikipedia.org/wiki/Context-free_grammar#Derivations_and_syntax_trees) of an input-stream by searching for [parse-trees](https://en.wikipedia.org/wiki/Parse_tree) using a top-down expansion of the given [formal grammar](https://en.wikipedia.org/wiki/Formal_grammar) rules. Inclusive choice is used to accommodate [ambiguity](https://en.wikipedia.org/wiki/Syntactic_ambiguity) by expanding all alternative right-hand-sides of grammar rules.[[2\]](https://en.wikipedia.org/wiki/Top-down_parsing#cite_note-AhoSethiUllman_1986-2)

Simple implementations of top-down parsing do not terminate for [left-recursive](https://en.wikipedia.org/wiki/Left_recursion) grammars, and top-down parsing with backtracking may have [exponential](https://en.wikipedia.org/wiki/Exponential_time) time complexity with respect to the length of the input for ambiguous [CFGs](https://en.wikipedia.org/wiki/Context-free_grammar).[[3\]](https://en.wikipedia.org/wiki/Top-down_parsing#cite_note-AhoUllman_1972-3) However, more sophisticated top-down parsers have been created by Frost, Hafiz, and Callaghan [[4\]](https://en.wikipedia.org/wiki/Top-down_parsing#cite_note-FrostHafizCallaghan_2007-4)[[5\]](https://en.wikipedia.org/wiki/Top-down_parsing#cite_note-FrostHafizCallaghan_2008-5) which do [accommodate ambiguity and left recursion](https://en.wikipedia.org/wiki/Top-down_parsing#Accommodating_left_recursion_in_top-down_parsing) in [polynomial time](https://en.wikipedia.org/wiki/Time_complexity#Polynomial_time) and which generate polynomial-sized representations of the potentially exponential number of parse trees.

