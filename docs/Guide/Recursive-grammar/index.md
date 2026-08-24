# Recursive grammar

素材:

1、gatevidyalay [Left Recursion | Left Recursion Elimination](https://www.gatevidyalay.com/left-recursion-left-recursion-elimination/) 

## wikipedia [Recursive grammar](https://en.wikipedia.org/wiki/Recursive_grammar)

In [computer science](https://en.wikipedia.org/wiki/Computer_science "Computer science"), a [grammar](https://en.wikipedia.org/wiki/Formal_grammar "Formal grammar") is informally called a **recursive grammar** if it contains [production rules](https://en.wikipedia.org/wiki/Formal_grammar#The_syntax_of_grammars "Formal grammar") that are [recursive](https://en.wikipedia.org/wiki/Recursion_\(computer_science\) "Recursion (computer science)"), meaning that expanding a non-terminal according to these rules can eventually lead to a string that includes the same non-terminal again. Otherwise it is called a **non-recursive grammar**.[[1]](https://en.wikipedia.org/wiki/Recursive_grammar#cite_note-ns02-1)

For example, a grammar for a [context-free language](https://en.wikipedia.org/wiki/Context-free_language "Context-free language") is [left recursive](https://en.wikipedia.org/wiki/Left_recursion "Left recursion") if there exists a non-terminal symbol *A* that can be put through the production rules to produce a string with *A* (as the leftmost symbol).[[2]](https://en.wikipedia.org/wiki/Recursive_grammar#cite_note-2)[[3]](https://en.wikipedia.org/wiki/Recursive_grammar#cite_note-3) All types of grammars in the [Chomsky hierarchy](https://en.wikipedia.org/wiki/Chomsky_hierarchy "Chomsky hierarchy") can be recursive and it is recursion that allows the production of infinite sets of words.