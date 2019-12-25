[TOC]



# [Basic block](https://en.wikipedia.org/wiki/Basic_bloc)

In [compiler construction](https://en.wikipedia.org/wiki/Compiler), a **basic block** is a straight-line code sequence with no branches in except to the entry and no branches out except at the exit.[[1\]](https://en.wikipedia.org/wiki/Basic_block#cite_note-1)[[2\]](https://en.wikipedia.org/wiki/Basic_block#cite_note-2) This restricted form makes a basic block highly amenable to analysis.[[3\]](https://en.wikipedia.org/wiki/Basic_block#cite_note-3) [Compilers](https://en.wikipedia.org/wiki/Compiler) usually decompose programs into their basic blocks as a first step in the analysis process. Basic blocks form the vertices or nodes in a [control flow graph](https://en.wikipedia.org/wiki/Control_flow_graph).

## Definition

The code in a basic block has:

- One [entry point](https://en.wikipedia.org/wiki/Entry_point), meaning no code within it is the destination of a [jump instruction](https://en.wikipedia.org/wiki/Jump_instruction) anywhere in the program.
- One exit point, meaning only the last instruction can cause the program to begin executing code in a different basic block.

Under these circumstances, whenever the first instruction in a basic block is executed, the rest of the instructions are necessarily executed exactly once, in order.[[4\]](https://en.wikipedia.org/wiki/Basic_block#cite_note-4)[[5\]](https://en.wikipedia.org/wiki/Basic_block#cite_note-5)

The code may be [source code](https://en.wikipedia.org/wiki/Source_code), [assembly code](https://en.wikipedia.org/wiki/Assembly_code) or some other sequence of instructions.

More formally, a sequence of instructions forms a basic block if:

- The instruction in each position [dominates](https://en.wikipedia.org/wiki/Dominator_(graph_theory)), or always executes before, all those in later positions.
- No other instruction executes between two instructions in the sequence.

This definition is more general than the intuitive one in some ways. For example, it allows unconditional jumps to labels not targeted by other jumps. This definition embodies the properties that make basic blocks easy to work with when constructing an algorithm.

The blocks to which control may transfer after reaching the end of a block are called that block's *successors*, while the blocks from which control may have come when entering a block are called that block's *predecessors*. The start of a basic block may be jumped to from more than one location.







# [Basic Blocks and Flow Graphs | Examples](https://www.gatevidyalay.com/basic-blocks-and-flow-graphs/)

## Basic Blocks

Basic block is a set of statements that always executes in a sequence one after the other.

The characteristics of basic blocks are

- They do not contain any kind of `jump` statements in them.
- There is no possibility of branching or getting halt in the middle.
- All the statements execute in the same order they appear.
- They do not lose lose the flow control of the program.

> NOTE: 有点原子的含义

### Example Of Basic Block

Three Address Code for the expression `a = b + c + d` is-

 

![Example Of Basic Block](https://www.gatevidyalay.com/wp-content/uploads/2018/03/Example-Of-Basic-Block.png)

Here,

- All the statements execute in a sequence one after the other.
- Thus, they form a basic block.



### Example Of Not A Basic Block

Three Address Code for the expression `If A<B then 1 else 0` is-

 

![Example Of Not A Basic Block](https://www.gatevidyalay.com/wp-content/uploads/2018/03/Example-Of-Not-A-Basic-Block-1.png)

 

Here,

- The statements do not execute in a sequence one after the other.
- Thus, they do not form a basic block.

## Partitioning Intermediate Code Into Basic Blocks

Any given code can be partitioned into basic blocks using the following rules

### Rule-01: Determining Leaders

 Following statements of the code are called as **Leaders**

- First statement of the code.
- Statement that is a **target** of the conditional or unconditional `goto` statement.
- Statement that appears immediately after a `goto` statement.

 

### Rule-02: Determining Basic Blocks

 

- All the statements that follow the **leader** (including the **leader**) till the **next leader** appears form one basic block.
- The first statement of the code is called as the **first leader**.
- The block containing the **first leader** is called as **Initial block**.



## Flow Graphs

A flow graph is a directed graph with flow control information added to the basic blocks.

- The **basic blocks** serve as **nodes** of the flow graph.
- There is a directed edge from block `B1` to block `B2` if `B2` appears immediately after `B1` in the code.



## PRACTICE PROBLEMS BASED ON BASIC BLOCKS & FLOW GRAPHS

## Problem-01:

Compute the basic blocks for the given three address statements

```
(1) PROD = 0

(2) I = 1

(3) T2 = addr(A) – 4

(4) T4 = addr(B) – 4

(5) T1 = 4 x I

(6) T3 = T2[T1]

(7) T5 = T4[T1]

(8) T6 = T3 x T5

(9) PROD = PROD + T6

(10) I = I + 1

(11) IF I <=20 GOTO (5)
```



### Solution

We have-

- `PROD = 0` is a leader since first statement of the code is a leader.
- `T1 = 4 x I` is a leader since target of the conditional goto statement is a leader.

Now, the given code can be partitioned into two basic blocks as-

 

![Basic Blocks and Flow Graphs | Problem-01 | Basic Blocks](https://www.gatevidyalay.com/wp-content/uploads/2018/03/Basic-Blocks-and-Flow-Graphs-Problem-01-Basic-Blocks.png)

## Problem-02:

Draw a flow graph for the three address statements given in problem-01.



## Solution

- Firstly, we compute the basic blocks (already done above).
- Secondly, we assign the flow control information.



The required **flow graph** is-

 

![Basic Blocks and Flow Graphs | Problem-02 | Flow Graphs](https://www.gatevidyalay.com/wp-content/uploads/2018/03/Basic-Blocks-and-Flow-Graphs-Problem-02-Flow-Graphs.png)