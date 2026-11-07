# 3 Lexical Analysis

- [3.1 The Role of the Lexical Analyzer](books&courses/龙书/compilers-principles/3-Lexical-Analysis/3.1-The-Role-of-the-Lexical-Analyzer.md)
- [3.10 Summary of Chapter 3](books&courses/龙书/compilers-principles/3-Lexical-Analysis/3.10-Summary-of-Chapter-3.md)
- [3.11 References for Chapter 3](books&courses/龙书/compilers-principles/3-Lexical-Analysis/3.11-References-for-Chapter-3.md)
- [3.2 Input Buffering](books&courses/龙书/compilers-principles/3-Lexical-Analysis/3.2-Input-Buffering.md)
- [3.3 Specification of Tokens](books&courses/龙书/compilers-principles/3-Lexical-Analysis/3.3-Specification-of-Tokens.md)
- [3.4 Recognition of Tokens](books&courses/龙书/compilers-principles/3-Lexical-Analysis/3.4-Recognition-of-Tokens.md)
- [3.5 The Lexical-Analyzer Generator Lex](books&courses/龙书/compilers-principles/3-Lexical-Analysis/3.5-The-Lexical-Analyzer-Generator-Lex.md)
- [3.6 Finite Automata](books&courses/龙书/compilers-principles/3-Lexical-Analysis/3.6-Finite-Automata.md)
- [3.7 From Regular Expressions to Automata](books&courses/龙书/compilers-principles/3-Lexical-Analysis/3.7-From-Regular-Expressions-to-Automata.md)
- [3.8 Design of a Lexical-Analyzer Generator](books&courses/龙书/compilers-principles/3-Lexical-Analysis/3.8-Design-of-a-Lexical-Analyzer-Generator.md)
- [3.9 Optimization of DFA-Based Pattern Matchers](books&courses/龙书/compilers-principles/3-Lexical-Analysis/3.9-Optimization-of-DFA-Based-Pattern-Matchers.md)

## 章首内容

Lexical Analysis
In this chapter we show how to construct a lexical analyzer. To implement a lexical analyzer by hand, it helps to start with a diagram or other description for the lexemes of each token. We can then write code to identify each occurrence of each lexeme on the input and to return information about the token identified.
We can also produce a lexical analyzer automatically by specifying the lexeme patterns to a lexical-analyzer generator and compiling those patterns into code that functions as a lexical analyzer. This approach makes it easier to modify a lexical analyzer, since we have only to rewrite the affected patterns, not the entire program. It also speeds up the process of implementing the lexical analyzer, since the programmer specifies the software at the very high level of patterns and relies on the generator to produce the detailed code. We shall introduce in Section 3.5 a lexical-analyzer generator called Lex (or Flex in a more recent embodiment).
We begin the study of lexical-analyzer generators by introducing regular expressions, a convenient notation for specifying lexeme patterns. We show how this notation can be transformed, first into nondeterministic automata and then into deterministic automata. The latter two notations can be used as input to a “driver,” that is, code which simulates these automata and uses them as a guide to determining the next token. This driver and the specification of the automaton form the nucleus of the lexical analyzer.
