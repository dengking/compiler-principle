# [Chart parser](https://en.wikipedia.org/wiki/Chart_parser)

In [computer science](https://en.wikipedia.org/wiki/Computer_science), a **chart parser** is a type of [parser](https://en.wikipedia.org/wiki/Parsing) suitable for [ambiguous grammars](https://en.wikipedia.org/wiki/Ambiguous_grammar) (including grammars of [natural languages](https://en.wikipedia.org/wiki/Natural_language)). It uses the [dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming) approach—partial hypothesized results are stored in a structure called a **chart** and can be re-used. This eliminates [backtracking](https://en.wikipedia.org/wiki/Backtracking) and prevents a [combinatorial explosion](https://en.wikipedia.org/wiki/Combinatorial_explosion).

Chart parsing is generally credited to [Martin Kay](https://en.wikipedia.org/wiki/Martin_Kay).

## Types of chart parsers

A common approach is to use a variant of the [Viterbi algorithm](https://en.wikipedia.org/wiki/Viterbi_algorithm). The [Earley parser](https://en.wikipedia.org/wiki/Earley_parser) is a type of chart parser mainly used for parsing in [computational linguistics](https://en.wikipedia.org/wiki/Computational_linguistics), named for its inventor. Another chart parsing algorithm is the [Cocke-Younger-Kasami](https://en.wikipedia.org/wiki/Cocke-Younger-Kasami_algorithm) (CYK) algorithm.

Chart parsers can also be used for parsing computer languages. **Earley parsers** in particular have been used in [compiler compilers](https://en.wikipedia.org/wiki/Compiler_compiler) where their ability to parse using arbitrary [Context-free grammars](https://en.wikipedia.org/wiki/Context-free_grammars) eases the task of writing the grammar for a particular language. However their lower efficiency has led to people avoiding them for most compiler work.

In bidirectional chart parsing, edges of the chart are marked with a direction, either forwards or backwards, and rules are enforced on the direction in which edges must point in order to be combined into further edges.

In incremental chart parsing, the chart is constructed incrementally as the text is edited by the user, with each change to the text resulting in the minimal possible corresponding change to the chart.

Chart parsers are distinguished between [top-down](https://en.wikipedia.org/wiki/Top-down_parsing) and [bottom-up](https://en.wikipedia.org/wiki/Bottom-up_parser), as well as active and passive.