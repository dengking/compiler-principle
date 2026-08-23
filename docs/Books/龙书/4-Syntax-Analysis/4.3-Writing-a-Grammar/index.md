# 4.3 Writing a Grammar

Grammars are capable of describing most, but not all, of the syntax of programming languages. For instance, the requirement that identifiers be declared before they are used, cannot be described by a **context-free grammar**. Therefore, the sequences of tokens accepted by a parser form a superset of the programming language; subsequent phases of the **compiler** must analyze the output of the parser to ensure compliance with rules that are not checked by the parser.

This section begins with a discussion of how to divide work between a **lexical analyzer** and a **parser**. We then consider several transformations that could be applied to get a grammar more suitable for parsing. One technique can **eliminate ambiguity** in the grammar, and other techniques - **left-recursion elimination** and **left factoring** - are useful for rewriting grammars so they become suitable for **top-down parsing**. We conclude this section by considering some programming language constructs that cannot be described by any grammar.

## 4.3.1 Lexical Versus Syntactic Analysis

As we observed in Section 4.2.7, everything that can be described by a regular expression can also be described by a grammar. We may therefore reasonably ask: "Why use regular expressions to define the lexical syntax of a language?" There are several reasons.

1. Separating the **syntactic structure** of a language into **lexical** and **non‑lexical** parts provides a convenient way of modularizing the **front end** of a compiler into two manageable‑sized components.
   
   1. 翻译: 将语言的语法结构拆分为词法部分与非词法部分，可以很方便地把编译器前端模块化，划分为两个规模可控的组件。

2. The lexical rules of a language are frequently quite simple, and to describe them we do not need a notation as powerful as grammars.
   
   1. 翻译: 一门语言的词法规则通常十分简单，描述词法并不需要文法那样表达能力很强的记法。

3. **Regular expressions** generally provide a more concise and easier‑to‑understand notation for tokens than grammars.
   
   1. 翻译: 针对记号（token），正则表达式通常比文法更加简洁、更容易理解。

4. More efficient **lexical analyzers** can be constructed automatically from regular expressions than from arbitrary grammars.
   
   1. 翻译: 相比于任意文法，从正则表达式可以自动生成效率更高的词法分析器。

There are no firm guidelines as to what to put into the lexical rules, as opposed to the syntactic rules. Regular expressions are most useful for describing the structure of constructs such as identifiers, constants, keywords, and white space. Grammars, on the other hand, are most useful for describing nested structures such as balanced parentheses, matching begin‑end's, corresponding if‑then‑else's, and so on. These nested structures cannot be described by regular expressions.