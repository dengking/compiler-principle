[TOC]



# [LL parser](https://en.wikipedia.org/wiki/LL_parser)

In [computer science](https://en.wikipedia.org/wiki/Computer_science), an **LL parser** (Left-to-right, Leftmost derivation) is a [top-down parser](https://en.wikipedia.org/wiki/Top-down_parsing) for a subset of [context-free languages](https://en.wikipedia.org/wiki/Context-free_languages). It parses the input from **L**eft to right, performing [**L**eftmost derivation](https://en.wikipedia.org/wiki/Context-free_grammar#Derivations_and_syntax_trees) of the sentence.

An LL parser is called an LL(*k*) parser if it uses *k* [tokens](https://en.wikipedia.org/wiki/Token_(parser)) of [lookahead](https://en.wikipedia.org/wiki/Parsing#Lookahead) when parsing a sentence. A grammar is called an [LL(*k*) grammar](https://en.wikipedia.org/wiki/LL_grammar) if an LL(*k*) parser can be constructed from it. A formal language is called an LL(*k*) language if it has an LL(*k*) grammar. The set of LL(*k*) languages is properly contained in that of LL(*k*+1) languages, for each *k* ≥ 0. A corollary of this is that not all context-free languages can be recognized by an LL(*k*) parser. An LL parser is called an LL(`*`), or LL-regular, parser if it is not restricted to a finite number *k* of tokens of lookahead, but can make parsing decisions by recognizing whether the following tokens belong to a [regular language](https://en.wikipedia.org/wiki/Regular_language) (for example by means of a [deterministic finite automaton](https://en.wikipedia.org/wiki/Deterministic_finite_automaton)).

LL grammars, particularly LL(1) grammars, are of great practical interest, as parsers for these grammars are easy to construct, and many [computer languages](https://en.wikipedia.org/wiki/Computer_language) are designed to be LL(1) for this reason.[[3\]](https://en.wikipedia.org/wiki/LL_parser#cite_note-3) LL parsers are table-based parsers, similar to [LR parsers](https://en.wikipedia.org/wiki/LR_parser). LL grammars can also be parsed by [recursive descent parsers](https://en.wikipedia.org/wiki/Recursive_descent_parser). According to Waite and Goos (1984),  LL(*k*) grammars were introduced by Stearns and Lewis (1969). 



## Overview

For a given [context-free grammar](https://en.wikipedia.org/wiki/Context-free_grammar), the parser attempts to find the [leftmost derivation](https://en.wikipedia.org/wiki/Context-free_grammar#Derivations_and_syntax_trees). Given an example grammar $ G $:

1. $ S\to E $
2. $ E\to (E+E) $
3. $ E\to i $

the leftmost derivation for $ w=((i+i)+i) $ is:

$ S\ {\overset {(1)}{\Rightarrow }}\ E\ {\overset {(2)}{\Rightarrow }}\ (E+E)\ {\overset {(2)}{\Rightarrow }}\ ((E+E)+E)\ {\overset {(3)}{\Rightarrow }}\ ((i+E)+E)\ {\overset {(3)}{\Rightarrow }}\ ((i+i)+E)\ {\overset {(3)}{\Rightarrow }}\ ((i+i)+i) $

Generally, there are multiple possibilities when selecting a rule to expand the leftmost non-terminal. In step 2 of the previous example, the parser must choose whether to apply rule 2 or rule 3:

$ S\ {\overset {(1)}{\Rightarrow }}\ E\ {\overset {(?)}{\Rightarrow }}\ ? $

To be efficient, the parser must be able to make this choice deterministically when possible, without [backtracking](https://en.wikipedia.org/wiki/Backtracking). For some grammars, it can do this by peeking on the unread input (without reading). In our example, if the parser knows that the next unread symbol is $ ( $ , the only correct rule that can be used is 2.

Generally, an $ LL(k) $ parser can look ahead at $ k $ symbols. However, given a grammar, the problem of determining if there exists a $ LL(k) $ parser for some $ k $ that recognizes it is undecidable. For each $ k $, there is a language that cannot be recognized by an $ LL(k) $ parser, but can be by an $ LL(k+1) $.

We can use the above analysis to give the following formal definition:

Let $ G $ be a context-free grammar and $ k\geq 1 $. We say that $ G $ is $ LL(k) $, if and only if for any two leftmost derivations:

1. $ S\ \Rightarrow \ \dots \ \Rightarrow \ wA\alpha \ \Rightarrow \ \dots \ \Rightarrow \ w\beta \alpha \ \Rightarrow \ \dots \ \Rightarrow \ wu $
2. $ S\ \Rightarrow \ \dots \ \Rightarrow \ wA\alpha \ \Rightarrow \ \dots \ \Rightarrow \ w\gamma \alpha \ \Rightarrow \ \dots \ \Rightarrow \ wv $

the following condition holds: the prefix of the string $ u $ of length $ k $ equals the prefix of the string $ v $ of length $ k $ implies $ \beta \ =\ \gamma $.

> Do not understand.



## Parser

The $ LL(k) $ parser is a [deterministic pushdown automaton](https://en.wikipedia.org/wiki/Deterministic_pushdown_automaton) with the ability to peek on the next $ k $ input symbols without reading. This peek capability can be emulated by storing the lookahead buffer contents in the **finite state space**, since both buffer and input alphabet are finite in size. As a result, this does not make the automaton more powerful, but is a convenient abstraction.

The stack alphabet is $ \Gamma =N\cup \Sigma $, where:

- $ N $ is the set of non-terminals;
- $ \Sigma $ the set of terminal (input) symbols with a special end-of-input (EOI) symbol $ \$ $.



The **parser stack** initially contains the **starting symbol** above the EOI: $ [\ S\ \$\ ] $. During operation, the parser repeatedly replaces the symbol $ X $ on top of the stack:

- with some $ \alpha $, if $ X\in N $ and there is a rule $ X\to \alpha $;
- with $ \epsilon $ (in some notations $ \lambda $), i.e. $ X $ is popped off the stack, if $ X\in \Sigma $. In this case, an input symbol $ x $ is read and if $ x\neq X $, the parser rejects the input.