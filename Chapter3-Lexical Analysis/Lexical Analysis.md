# Lexical Analysis

In this chapter we show how to construct a [**lexical analyzer**](https://en.wikipedia.org/wiki/Lexical_analysis). To implement a **lexical analyzer** by hand, it helps to start with a diagram or other description for
the lexemes of each token. We can then write co de to identify each o ccurrence of
each lexeme on the input and to return information ab out the token identi?ed.

> NOTE: Manual implementation just to make it easier for the readers to understand how the lexical analyzer works,  what should be focused on is how does it work automatically and how to implement it.

We can also produce a lexical analyzer automatically by specifying the [lexeme](https://en.wikipedia.org/wiki/Lexeme) patterns to a lexical-analyzer generator and compiling those patterns into code that functions as a **lexical analyzer**. This approach makes it easier to modify a **lexical analyzer**, since we have only to rewrite the affected patterns, not
the entire program. It also speeds up the process of implementing the lexical analyzer, since the programmer specifies the software at the very high level of patterns and relies on the generator to produce the detailed code. We shall introduce in Section 3.5 a lexical-analyzer generator called [Lex](https://en.wikipedia.org/wiki/Lex_%28software%29) (or Flex in a more recent embodiment).

> NOTE: In fact, the essence lies in how lex works.

We begin the study of lexical-analyzer generators by introducing regular expressions, a convenient notation for specifying lexeme patterns. We show how this notation can be transformed, first into nondeterministic automata and then into deterministic automata. The latter two notations can be used as input to a "driver," that is, code which simulates these automata and uses them as a guide to determining the next token. This driver and the specification of the automaton form the nucleus of the lexical analyzer.

> NOTE: Nucleus of the lexical analyzer is what we should focus on.

