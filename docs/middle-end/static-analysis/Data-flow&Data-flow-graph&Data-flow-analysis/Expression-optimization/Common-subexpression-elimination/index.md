# Common subexpression elimination

stackoverflow [Implementing common subexpression elimination](https://stackoverflow.com/questions/11326346/implementing-common-subexpression-elimination) 

51cto [[hash 表达式树]UVa12219 - Common Subexpression Elimination](https://blog.51cto.com/u_12911014/5548109)

wiki.algo [Perfect hashing](https://wiki.algo.is/Perfect%20hashing) # [Common Subexpression Elimination](https://archive.algo.is/icpc/nwerc/2009/nwerc09.pdf)[1](https://wiki.algo.is/Perfect hashing#fn-1) 

## wikipedia [Common subexpression elimination](https://en.wikipedia.org/wiki/Common_subexpression_elimination)

In [compiler theory](https://en.wikipedia.org/wiki/Compiler_theory "Compiler theory"), **common subexpression elimination** (**CSE**) is a [compiler optimization](https://en.wikipedia.org/wiki/Compiler_optimization "Compiler optimization") that searches for instances of identical [expressions](https://en.wikipedia.org/wiki/Expression_\(computer_science\) "Expression (computer science)") (i.e., they all evaluate to the same value), and analyzes whether it is worthwhile replacing them with a single variable holding the computed value.[[1]](https://en.wikipedia.org/wiki/Common_subexpression_elimination#cite_note-MuchnickAssociates1997-1)

### Example

In the following code:

```
a = b * c + g;
d = b * c * e;
```

it may be worth transforming the code to:

```
tmp = b * c;
a = tmp + g;
d = tmp * e;
```

if the cost of storing and retrieving `tmp` is less than the cost of calculating `b * c` an extra time.

### Principle

The possibility to perform CSE is based on [available expression](https://en.wikipedia.org/wiki/Available_expression "Available expression") analysis (a [data flow analysis](https://en.wikipedia.org/wiki/Data_flow_analysis "Data flow analysis")). An expression `b*c` is available at a point *p* in a program if:

- every path from the initial node to p evaluates `b*c` before reaching *p*,
- and there are no assignments to `b` or `c` after the evaluation but before *p*.

The cost/benefit analysis performed by an optimizer will calculate whether the cost of the store to `tmp` is less than the cost of the multiplication; in practice other factors such as which values are held in which registers are also significant.

Compiler writers distinguish two kinds of CSE:

- **local common subexpression elimination** works within a single [basic block](https://en.wikipedia.org/wiki/Basic_block "Basic block")
- **global common subexpression elimination** works on an entire procedure,

Both kinds rely on [data flow analysis](https://en.wikipedia.org/wiki/Data_flow_analysis "Data flow analysis") of which expressions are available at which points in a program.