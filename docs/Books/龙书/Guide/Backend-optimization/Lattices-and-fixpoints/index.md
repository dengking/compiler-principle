# Lattices and fixpoints in compiler

[Static Program AnalysisPart 3 – lattices and fixpoints](https://matthewbdwyer.github.io/6620/slides/3-lattices-and-fixpoints.pdf) 

[南大软分课程笔记｜06 数据流分析理论 ](https://blog.wohin.me/posts/nju-program-analysis-06/) 

## Lattices and fixpoints in compiler

https://share.google/aimode/5y8Cxtw1Q5zunqAN0

In compiler design, lattices and fixpoints are the mathematical foundation used to guarantee that data-flow analyses terminate and yield correct results. They are primarily used in optimization passes like constant propagation, liveness analysis, and available expressions. [1, 2]

------------------------------

## 1. What is a Lattice in a Compiler?

A lattice is a partially ordered set of values where any two elements have a unique highest common lower bound (called the meet or $\sqcap$) and a unique lowest common upper bound (called the join or $\sqcup$). [3, 4] 
In a compiler, a lattice represents the states of knowledge the compiler can have about a program's variables or expressions at any given point. [1] 

## Example: The Constant Propagation Lattice

Consider how a compiler tracks whether a variable x is a constant: [5] 

* 

* $\top$ (Top): "Undetermined / No information." The compiler hasn't analyzed this yet or it's uninitialized.

* Constants (1, 2, 3...): "The variable definitely holds this specific value".

* $\bot$ (Bottom): "Not a Constant (NAC)." The variable could hold multiple different values depending on the execution path. [6] 

* [ ⊤ (Top: Undefined) ]
  
      /          |           \
  
  ...  -2   -1   0   1   2  ...  (Constants)
  
      \          |           /
  
     [ ⊥ (Bottom: Not a Constant) ]

When two code execution paths merge (like after an if-else statement), the compiler uses the meet operator ($\sqcap$) to combine its knowledge:

* 
* $\text{Constant } 5 \sqcap \text{Constant } 5 = 5$ (Still a constant!)
* $\text{Constant } 5 \sqcap \text{Constant } 3 = \bot$ (It changed, so it is no longer a safe constant)
* $\top \sqcap \text{Constant } 5 = 5$ (Information overrides no information) [6] 
* 

------------------------------

## 2. What is a Fixpoint in a Compiler?

A compiler analyzes code loops by iteratively applying transfer functions ($f$). A transfer function takes the current lattice state at the input of a code block and computes the output state (e.g., "If x=2 and the line is x = x + 1, the output state is x=3"). [6, 7] 
Because loops cause information to cycle, the compiler must repeat this analysis over and over. It stops when it reaches a fixpoint. [2, 7] 
A fixpoint of a function $f$ is a value $x$ such that:
$$f(x) = x$$ 
When the compiler runs a pass over a loop and the values in the lattice stop changing, it has found a fixpoint. This means the compiler has successfully computed the absolute truth about that loop's behavior under the chosen abstract domain. [2, 7] 

------------------------------

## 3. How They Work Together: The Kleene Fixpoint Theorem

Compilers rely on Kleene's Fixed-Point Theorem (or the Knaster-Tarski Theorem) to ensure they don't get stuck in infinite analysis loops. The theorem states that a fixpoint is guaranteed to be reached if: [2] 

1. The lattice has a finite height (there are a finite number of steps from $\top$ to $\bot$).
2. The transfer functions are monotonic (order-preserving). Monotonic means that as the compiler learns more information, values only move down (or up, depending on convention) the lattice; they never bounce back and forth.

## The Iterative Fixpoint Algorithm

To solve a data-flow problem, the compiler uses an iterative algorithm to solve the equations: [7] 

1. Initialize all program states to $\top$ (or $\bot$, depending on whether it's a "must" or "may" analysis).
2. Apply transfer functions across the Control Flow Graph (CFG).
3. Combine merging paths using the lattice operator ($\sqcap$ or $\sqcup$).
4. Repeat steps 2 and 3 until $\text{State}_{\text{new}} = \text{State}_{\text{old}}$ for all blocks. [6, 7] 

Because the lattice is finite and the functions move predictably in one direction, the compiler is guaranteed to terminate quickly and find the Least Fixed Point (LFP) or Greatest Fixed Point (GFP). [8]

------------------------------

## Summary Comparison of Applications

| Compiler Analysis                                                                                  | Lattice Element Represents         | Top ($\top$) Meaning          | Bottom ($\bot$) Meaning       | Direction / Goal |
| -------------------------------------------------------------------------------------------------- | ---------------------------------- | ----------------------------- | ----------------------------- | ---------------- |
| [Constant Propagation](https://www.geeksforgeeks.org/compiler-design/data-flow-analysis-compiler/) | Specific value of a variable       | Unassigned / Any value        | Multi-valued / Variable       | Top → Bottom     |
| [Liveness Analysis](https://en.wikipedia.org/wiki/Live-variable_analysis)                          | Set of variables alive at a point  | Empty set ∅ (No vars live)    | Universal set (All vars live) | Bottom → Top     |
| [Available Expressions](https://clang.llvm.org/docs/DataFlowAnalysisIntro.html)                    | Set of expressions safely computed | Universal set (All available) | Empty set ∅ (None available)  | Top → Bottom     |

If you're interested, I can:

* Show a step-by-step example of a worklist fixpoint algorithm on a loop CFG
* Explain the mathematical difference between Least Fixed Point (LFP) and Greatest Fixed Point (GFP)
* Provide a Python simulation of a constant propagation lattice analysis

[1] [https://stackoverflow.com](https://stackoverflow.com/questions/2625261/how-is-a-lattice-used-by-a-compiler)
[2] [https://www.reddit.com](https://www.reddit.com/r/computerscience/comments/1ek4ojo/how_are_lattices_used_in_computer_science/)
[3] [https://arxiv.org](https://arxiv.org/html/2507.21439v1)
[4] [https://www.geeksforgeeks.org](https://www.geeksforgeeks.org/engineering-mathematics/lattices/)
[5] [https://pages.cs.wisc.edu](https://pages.cs.wisc.edu/~horwitz/CS704-NOTES/2.DATAFLOW.html)
[6] [https://www.cse.iitm.ac.in](https://www.cse.iitm.ac.in/~rupesh/teaching/pa/jan17/scribes/0-cp.pdf)
[7] [https://www.youtube.com](https://www.youtube.com/watch?v=eeXk_ec1n6g&t=733)
[8] [https://www.researchgate.net](https://www.researchgate.net/publication/220997507_Abstract_Interpretation_A_Unified_Lattice_Model_for_Static_Analysis_of_Programs_by_Construction_or_Approximation_of_Fixpoints)





## [The Worklist Algorithm: Principles, Applications, and Theoretical Foundations](https://www.bohrium.com/en/sciencepedia/feynman/keyword/worklist_algorithm)


