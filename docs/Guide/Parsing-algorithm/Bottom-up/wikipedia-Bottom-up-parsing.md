[TOC]



# [Bottom-up parsing](https://en.wikipedia.org/wiki/Bottom-up_parsing)

In [computer science](https://en.wikipedia.org/wiki/Computer_science), [parsing](https://en.wikipedia.org/wiki/Parsing) reveals the grammatical structure of linear input text, as a first step in working out its meaning. **Bottom-up parsing** recognizes the text's lowest-level small details first, before its mid-level structures, and leaving the highest-level overall structure to last.

## Bottom-up Versus Top-down

The bottom-up name comes from the concept of a [parse tree](https://en.wikipedia.org/wiki/Parse_tree), in which the most detailed parts are at the **bottom** of the (upside-down) tree, and larger structures composed from them are in successively higher layers, until at the top or "root" of the tree a single unit describes the entire input stream. A bottom-up parse discovers and processes that tree starting from the **bottom left end**, and incrementally works its way upwards and rightwards.[[2\]](https://en.wikipedia.org/wiki/Bottom-up_parsing#cite_note-2) A parser may act on the structure hierarchy's low, mid, and highest levels without ever creating an actual data tree; the tree is then merely implicit in the parser's actions. Bottom-up parsing patiently waits until it has scanned and parsed all parts of some construct before committing to what the combined construct is.



The opposite of this is **[top-down parsing](https://en.wikipedia.org/wiki/Top-down_parsing)**, in which the input's overall structure is decided (or guessed at) first, before dealing with mid-level parts, leaving completion of all lowest-level details to last. A top-down parser discovers and processes the hierarchical tree starting from the top, and incrementally works its way first downwards and then rightwards. Top-down parsing eagerly decides what a construct is much earlier, when it has only scanned the leftmost symbol of that construct and has not yet parsed any of its parts. **[Left corner](https://en.wikipedia.org/wiki/Left_corner) parsing** is a hybrid method which works bottom-up along the left edges of each subtree, and top-down on the rest of the parse tree.



If a language grammar has multiple rules that may start with the same leftmost symbols but have different endings, then that grammar can be efficiently handled by a [deterministic](https://en.wikipedia.org/wiki/Deterministic) bottom-up parse but cannot be handled top-down without guesswork and [backtracking](https://en.wikipedia.org/wiki/Backtracking). So bottom-up parsers handle a somewhat larger range of computer language grammars than do deterministic top-down parsers.



Bottom-up parsing is sometimes done by [backtracking](https://en.wikipedia.org/wiki/Backtracking). But much more commonly, bottom-up parsing is done by a **[shift-reduce parser](https://en.wikipedia.org/wiki/Shift-reduce_parser)** such as a [LALR parser](https://en.wikipedia.org/wiki/LALR_parser).





## Examples

Some of the parsers that use bottom-up parsing include:

- Precedence parser
  - [Simple precedence parser](https://en.wikipedia.org/wiki/Simple_precedence_parser)
  - [Operator-precedence parser](https://en.wikipedia.org/wiki/Operator-precedence_parser)
- Bounded-context parser (BC)
- [LR parser](https://en.wikipedia.org/wiki/LR_parser) (**L**eft-to-right, **R**ightmost derivation in reverse)
  - [Simple LR parser](https://en.wikipedia.org/wiki/Simple_LR_parser) (SLR)
  - [LALR parser](https://en.wikipedia.org/wiki/LALR_parser) (Look-Ahead)
  - [Canonical LR parser](https://en.wikipedia.org/wiki/Canonical_LR_parser) (LR(1))
  - [GLR parser](https://en.wikipedia.org/wiki/GLR_parser) (Generalized)[[3\]](https://en.wikipedia.org/wiki/Bottom-up_parsing#cite_note-GruneJacobs2007-3)
- [CYK parser](https://en.wikipedia.org/wiki/CYK_algorithm) (Cocke–Younger–Kasami)
- Recursive ascent parser
  - [Packrat parser](https://en.wikipedia.org/wiki/Packrat_parser)
- [Shift-reduce parser](https://en.wikipedia.org/wiki/Shift-reduce_parser)