# Reaching definition



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


