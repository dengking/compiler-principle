[TOC]



# [Control-flow graph](https://en.wikipedia.org/wiki/Control-flow_graph)

In [computer science](https://en.wikipedia.org/wiki/Computer_science), a **control-flow graph** (**CFG**) is a [representation](https://en.wikipedia.org/wiki/Depiction), using [graph](https://en.wikipedia.org/wiki/Graph_(discrete_mathematics)) notation, of all paths that might be traversed through a [program](https://en.wikipedia.org/wiki/Computer_program) during its [execution](https://en.wikipedia.org/wiki/Execution_(computing)). The control-flow graph is due to [Frances E. Allen](https://en.wikipedia.org/wiki/Frances_E._Allen),[[1\]](https://en.wikipedia.org/wiki/Control-flow_graph#cite_note-1) who notes that [Reese T. Prosser](https://en.wikipedia.org/wiki/Reese_Prosser) used [boolean connectivity matrices](https://en.wikipedia.org/wiki/Adjacency_matrix) for flow analysis before.[[2\]](https://en.wikipedia.org/wiki/Control-flow_graph#cite_note-2)

The CFG is essential to many [compiler optimizations](https://en.wikipedia.org/wiki/Compiler_optimization#Data-flow_optimizations) and [static-analysis](https://en.wikipedia.org/wiki/Static_code_analysis) tools.

## Definition

In a **control-flow graph** each [node](https://en.wikipedia.org/wiki/Vertex_(graph_theory)) in the [graph](https://en.wikipedia.org/wiki/Graph_(discrete_mathematics)) represents a [basic block](https://en.wikipedia.org/wiki/Basic_block), i.e. a straight-line piece of code without any jumps or [jump targets](https://en.wikipedia.org/wiki/Jump_target_(computing)); jump targets start a block, and jumps end a block. Directed [edges](https://en.wikipedia.org/wiki/Edge_(graph_theory)) are used to represent **jumps** in the [control flow](https://en.wikipedia.org/wiki/Control_flow). There are, in most presentations, two specially designated blocks: the *entry block*, through which control enters into the flow graph, and the *exit block*, through which all control flow leaves.[[3\]](https://en.wikipedia.org/wiki/Control-flow_graph#cite_note-3)

> NOTE: 表示jump的关键字：
>
> - `break`
> - `goto`
>
> 

Because of its construction procedure, in a CFG, every edge A→B has the property that:



The CFG can thus be obtained, at least conceptually, by starting from the program's (full) flow graph—i.e. the graph in which every node represents an individual instruction—and performing an [edge contraction](https://en.wikipedia.org/wiki/Edge_contraction) for every edge that falsifies the predicate above, i.e. contracting every edge whose source has a single exit and whose destination has a single entry. This contraction-based algorithm is of no practical importance, except as a visualization aid for understanding the CFG construction, because the CFG can be more efficiently constructed directly from the program by [scanning it for basic blocks](https://en.wikipedia.org/wiki/Basic_block#Creation_algorithm).