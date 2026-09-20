# Data-flow Schemas

In compiler design, **data-flow schemas** usually refer to the general framework for computing information about a program by propagating (传播) facts (事实) through its **control-flow graph (CFG)**.

They support analyses such as **reaching definitions**, live variables, available expressions, and constant propagation.

## 1. Basic Framework

For each basic block $B$, maintain:

- **IN[B]**: facts true immediately before the block.
- **OUT[B]**: facts true immediately after the block.
- **Transfer function** $f_B$: how the block changes those facts.
- **Merge operator**: how **facts** from multiple **control-flow paths** are combined.

The analysis repeatedly updates these values until reaching a **fixed point**—no value changes.

## 2. Forward Data-flow Schema

Information flows in the direction of program execution:

$$
IN[B] = \bigwedge_{P \in pred(B)} OUT[P]
$$

$$
OUT[B] = f_B(IN[B])
$$

> 非常优雅的图语言

Here, $\bigwedge$ denotes the **analysis-specific merge operator**, not necessarily **intersection**.

A common **transfer function** is:

$$
OUT[B] = GEN[B] \cup (IN[B] - KILL[B])
$$

- **GEN**: facts produced by the block that remain valid at its exit.
- **KILL**: incoming facts invalidated by the block.

### Example: Reaching Definitions

For:

```text
d1: x = 1
d2: y = x + 2
```

The block generates definitions `d1` and `d2` and kills other definitions of `x` and `y`.

At a control-flow join, use **union**: a definition reaches the join if it can arrive along **any** incoming path.

## 3. Backward Data-flow Schema

Information flows opposite to execution:

$$
OUT[B] = \bigwedge_{S \in succ(B)} IN[S]
$$

$$
IN[B] = f_B(OUT[B])
$$

### Example: Live-variable Analysis

A variable is live if its current value may be used later before being overwritten.

$$
OUT[B] = \bigcup_{S \in succ(B)} IN[S]
$$

$$
IN[B] = USE[B] \cup (OUT[B] - DEF[B])
$$

- **USE[B]**: variables read before being defined within the block.
- **DEF[B]**: variables assigned within the block.

For:

```text
x = y + 1
```

$$
USE = \{y\}, \qquad DEF = \{x\}
$$

If $OUT = \{x,z\}$, then:

$$
IN = \{y\} \cup (\{x,z\} - \{x\}) = \{y,z\}
$$

## 4. Common Schemas

| Analysis              | Direction | Merge                  | Main question                                                                              |
| --------------------- | --------- | ---------------------- | ------------------------------------------------------------------------------------------ |
| Reaching definitions  | Forward   | Union                  | Which assignments may reach this point?                                                    |
| Live variables        | Backward  | Union                  | Which values may be needed later?                                                          |
| Available expressions | Forward   | Intersection           | Which expressions have already been computed on every incoming path, without invalidation? |
| Very busy expressions | Backward  | Intersection           | Which expressions will be evaluated on every outgoing path before their operands change?   |
| Constant propagation  | Forward   | Constant-lattice merge | Does a variable have the same constant value on all incoming paths?                        |

**May analyses** typically use union; **must analyses** typically use intersection.

## 5. Fixed-point Implementation

A forward worklist solver looks like:

```text
initialize IN and OUT
set entry boundary conditions
worklist = all blocks

while worklist is not empty:
    B = remove one block

    IN[B] = merge OUT values of predecessors
            respecting entry boundary conditions

    newOUT = transfer(B, IN[B])

    if newOUT != OUT[B]:
        OUT[B] = newOUT
        add successors of B to worklist
```

For backward analysis, merge successor `IN` values, update `IN[B]`, and re-enqueue predecessors.

Initialization matters: union-based set analyses commonly start with empty sets, while intersection-based analyses commonly start with the universal set, subject to entry/exit boundary conditions. Monotone transfer functions over finite-height lattices guarantee termination with the appropriate initialization.

**In short:** a data-flow schema specifies the **facts, direction, merge operator, transfer functions, and boundary conditions** needed to compute a program property.