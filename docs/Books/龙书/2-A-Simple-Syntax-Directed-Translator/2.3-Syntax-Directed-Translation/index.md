# 2.3 Syntax-Directed Translation





## 2.3.5 Translation Schemes 



A **syntax-directed translation scheme** is a notation for specifying a translation by attaching program fragments to productions in a grammar. A translation scheme is like a syntax-directed denition, except that the order of evaluation of the semantic rules is explicitly specied.

```
rest -> + term {print('+')} rest1
```

