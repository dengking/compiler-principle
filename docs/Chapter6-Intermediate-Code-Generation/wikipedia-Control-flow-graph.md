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

[outdegree](https://en.wikipedia.org/wiki/Outdegree)(A) > 1 or indegree(B) > 1 (or both).

The CFG can thus be obtained, at least conceptually, by starting from the program's (full) flow graph—i.e. the graph in which every node represents an individual instruction—and performing an [edge contraction](https://en.wikipedia.org/wiki/Edge_contraction) for every edge that falsifies the predicate above, i.e. contracting every edge whose source has a single exit and whose destination has a single entry. This contraction-based algorithm is of no practical importance, except as a visualization aid for understanding the CFG construction, because the CFG can be more efficiently constructed directly from the program by [scanning it for basic blocks](https://en.wikipedia.org/wiki/Basic_block#Creation_algorithm).



## Reachability

Main article: [Reachability](https://en.wikipedia.org/wiki/Reachability)

[Reachability](https://en.wikipedia.org/wiki/Reachability) is a graph property useful in optimization.

If a subgraph is not connected from the subgraph containing the entry block, that subgraph is unreachable during any execution, and so is [unreachable code](https://en.wikipedia.org/wiki/Unreachable_code); under normal conditions it can be safely removed.

If the exit block is unreachable from the entry block, an [infinite loop](https://en.wikipedia.org/wiki/Infinite_loop) may exist. Not all infinite loops are detectable, see [Halting problem](https://en.wikipedia.org/wiki/Halting_problem). A halting order may also exist there.

Unreachable code and infinite loops are possible even if the programmer does not explicitly code them: optimizations like [constant propagation](https://en.wikipedia.org/wiki/Constant_propagation) and [constant folding](https://en.wikipedia.org/wiki/Constant_folding) followed by [jump threading](https://en.wikipedia.org/wiki/Jump_threading) can collapse multiple basic blocks into one, cause edges to be removed from a CFG, etc., thus possibly disconnecting parts of the graph.

## Domination relationship

*Main article:* [Dominator (graph theory)](https://en.wikipedia.org/wiki/Dominator_(graph_theory))

A block M *[dominates](https://en.wikipedia.org/wiki/Dominator_(graph_theory))* a block N if every path from the entry that reaches block N has to pass through block M. The entry block dominates all blocks.

In the reverse direction, block M *postdominates* block N if every path from N to the exit has to pass through block M. The exit block postdominates all blocks.

It is said that a block M *immediately dominates* block N if M dominates N, and there is no intervening block P such that M dominates P and P dominates N. In other words, M is the last dominator on all paths from entry to N. Each block has a unique immediate dominator.

Similarly, there is a notion of *immediate postdominator*, analogous to *immediate dominator*.

The [*dominator tree*](https://en.wikipedia.org/wiki/Dominator_(graph_theory)) is an ancillary data structure depicting the dominator relationships. There is an arc from Block M to Block N if M is an immediate dominator of N. This graph is a tree, since each block has a unique immediate dominator. This tree is rooted at the entry block. The dominator tree can be calculated efficiently using [Lengauer–Tarjan's algorithm](https://en.wikipedia.org/wiki/Lengauer–Tarjan's_algorithm).

A *postdominator tree* is analogous to the *dominator tree*. This tree is rooted at the exit block.





## Special edges

A *back edge* is an edge that points to a block that has already been met during a depth-first ([DFS](https://en.wikipedia.org/wiki/Depth-first_search)) traversal of the graph. Back edges are typical of loops.

A *critical edge* is an edge which is neither the only edge leaving its source block, nor the only edge entering its destination block. These edges must be *split*: a new block must be created in the middle of the edge, in order to insert computations on the edge without affecting any other edges.

An *abnormal edge* is an edge whose destination is unknown. [Exception handling](https://en.wikipedia.org/wiki/Exception_handling) constructs can produce them. These edges tend to inhibit optimization.

An *impossible edge* (also known as a *fake edge*) is an edge which has been added to the graph solely to preserve the property that the exit block postdominates all blocks. It cannot ever be traversed.



## Loop management

A *loop header* (sometimes called the *entry point* of the loop) is a dominator that is the target of a loop-forming back edge. The loop header dominates all blocks in the loop body. A block may be a loop header for more than one loop. A loop may have multiple entry points, in which case it has no "loop header".

Suppose block M is a dominator with several incoming edges, some of them being back edges (so M is a loop header). It is advantageous to several optimization passes to break M up into two blocks Mpre and Mloop. The contents of M and back edges are moved to Mloop, the rest of the edges are moved to point into Mpre, and a new edge from Mpre to Mloop is inserted (so that Mpre is the immediate dominator of Mloop). In the beginning, Mpre would be empty, but passes like [loop-invariant code motion](https://en.wikipedia.org/wiki/Loop-invariant_code_motion) could populate it. Mpre is called the *loop pre-header*, and Mloop would be the loop header.



## Reducibility

A reducible CFG is one with edges that can be partitioned into two disjoint sets: forward edges, and back edges, such that:[[5\]](https://en.wikipedia.org/wiki/Control-flow_graph#cite_note-5)

- Forward edges form a [directed acyclic graph](https://en.wikipedia.org/wiki/Directed_acyclic_graph) with all nodes reachable from the entry node.
- For all back edges (A, B), node B [dominates](https://en.wikipedia.org/wiki/Dominator_(graph_theory)) node A.

[Structured programming](https://en.wikipedia.org/wiki/Structured_programming) languages are often designed such that all CFGs they produce are reducible, and common structured programming statements such as IF, FOR, WHILE, BREAK, and CONTINUE produce reducible graphs. To produce irreducible graphs, statements such as [GOTO](https://en.wikipedia.org/wiki/GOTO) are needed. Irreducible graphs may also be produced by some compiler optimizations.





## Loop connectedness

The loop connectedness of a CFG is defined with respect to a given [depth-first search](https://en.wikipedia.org/wiki/Depth-first_search) tree (DFST) of the CFG. This DFST should be rooted at the start node and cover every node of the CFG.

Edges in the CFG which run from a node to one of its DFST ancestors (including itself) are called back edges.

The loop connectedness is the largest number of back edges found in any cycle-free path of the CFG. In a reducible CFG, the loop connectedness is independent of the DFST chosen.[[6\]](https://en.wikipedia.org/wiki/Control-flow_graph#cite_note-:0-6)[[7\]](https://en.wikipedia.org/wiki/Control-flow_graph#cite_note-7)

Loop connectedness has been used to reason about the time complexity of [data-flow analysis](https://en.wikipedia.org/wiki/Data-flow_analysis).[[6\]](https://en.wikipedia.org/wiki/Control-flow_graph#cite_note-:0-6)