# Use-define chain&Definition-use chain

Use-define=use's define，需要知道自己被哪些使用

Definition-use=definition's use，需要知道使用的variable是源自哪里

wikipedia [Use-define chain](https://en.wikipedia.org/wiki/Use-define_chain) 

Within [computer science](https://en.wikipedia.org/wiki/Computer_science "Computer science"), a **use-definition chain** (or **UD chain**) is a [data structure](https://en.wikipedia.org/wiki/Data_structure "Data structure") that consists of a use *U*, of a [variable](https://en.wikipedia.org/wiki/Variable_\(programming\) "Variable (programming)"), and all the definitions *D* of that variable that can reach that use without any other intervening definitions.[[1]](https://en.wikipedia.org/wiki/Use-define_chain#cite_note-kennedy-1)[[2]](https://en.wikipedia.org/wiki/Use-define_chain#cite_note-duct-2) A UD Chain generally means the [assignment](https://en.wikipedia.org/wiki/Assignment_\(computer_science\) "Assignment (computer science)") of some value to a variable.

A counterpart of a *UD Chain* is a **definition-use chain** (or **DU chain**), which consists of a definition *D* of a variable and all the uses *U* reachable from that definition without any other intervening definitions.[[3]](https://en.wikipedia.org/wiki/Use-define_chain#cite_note-leiss-3)

Both UD and DU chains are created by using a form of [static code analysis](https://en.wikipedia.org/wiki/Static_code_analysis "Static code analysis") known as [data flow analysis](https://en.wikipedia.org/wiki/Data_flow_analysis "Data flow analysis"). Knowing the use-def and def-use chains for a program or subprogram is a prerequisite for many [compiler optimizations](https://en.wikipedia.org/wiki/Compiler_optimization "Compiler optimization"), including [constant propagation](https://en.wikipedia.org/wiki/Constant_propagation "Constant propagation") and [common subexpression elimination](https://en.wikipedia.org/wiki/Common_subexpression_elimination "Common subexpression elimination").

## wikipedia [Reaching definition](https://en.wikipedia.org/wiki/Reaching_definition)

In [compiler theory](https://en.wikipedia.org/wiki/Compiler_theory "Compiler theory"), a **reaching definition** for a given instruction is an earlier instruction whose target variable can reach (be assigned to) the given one without an intervening assignment. For example, in the following code:

```
d1 : y := 3
d2 : x := y
```

`d1` is a reaching definition for `d2`. In the following, example, however:

```
d1 : y := 3
d2 : y := 4
d3 : x := y
```

`d1` is no longer a reaching definition for `d3`, because `d2` kills its reach: the value defined in `d1` is no longer available and cannot reach `d3`.

### As analysis

The similarly named **reaching definitions** is a [data-flow analysis](https://en.wikipedia.org/wiki/Data-flow_analysis "Data-flow analysis") which statically determines which definitions may reach a given point in the code. Because of its simplicity, it is often used as the canonical example of a data-flow analysis in textbooks. The data-flow confluence operator used is set union, and the analysis is forward flow. Reaching definitions are used to compute [use-def chains](https://en.wikipedia.org/wiki/Use-def_chain "Use-def chain").

## Combination

它们是一种combination:

> Because of its single definition per variable property, SSA form simplifies **def-use** and **use-def chains** in several ways. First, SSA form simplifies **def-use chains** as it combines the information as early as possible. This is illustrated by Figure 2.1 where the **def-use chain** in the non-SSA program requires as many merges as there are uses of $x$, whereas the corresponding SSA form allows early and more efficient combination.
