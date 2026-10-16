# 5 Syntax-Directed Translation

- [5.1 Syntax-Directed Definitions](5.1-Syntax-Directed-Definitions.md)
- [5.2 Evaluation Orders for SDD's](5.2-Evaluation-Orders-for-SDD's.md)
- [5.3 Applications of Syntax-Directed Translation](5.3-Applications-of-Syntax-Directed-Translation.md)
- [5.4 Syntax-Directed Translation Schemes](5.4-Syntax-Directed-Translation-Schemes.md)
- [5.5 Implementing L-Attributed SDD's](5.5-Implementing-L-Attributed-SDD's.md)
- [5.6 Summary of Chapter 5](5.6-Summary-of-Chapter-5.md)
- [5.7 References for Chapter 5](5.7-References-for-Chapter-5.md)

## 章首内容

Syntax-Directed
Translation
This chapter develops the theme of Section 2.3: the translation of languages guided by context-free grammars. The translation techniques in this chapter will be applied in Chapter 6 to type checking and intermediate-code generation.
The techniques are also useful for implementing little languages for specialized tasks; this chapter includes an example from typesetting.
We associate information with a language construct by attaching attributes to the grammar symbol(s) representing the construct, as discussed in Section 2.3.2. A syntax-directed definition specifies the values of attributes by associating semantic rules with the grammar productions. For example, an infix-to-postfix translator might have a production and rule
PRODUCTION SEMANTIC RULE
E ! E1 + T E:code = E1:code k T:code k +
This production has two nonterminals, E and T ; the subscript in E1 distinguishes the occurrence of E in the production body from the occurrence of E as the head. Both E and T have a string-valued attribute code. The semantic rule specifies that the string E:code is formed by concatenating E1:code, T:code, and the character + . While the rule makes it explicit that the translation of
E is built up from the translations of E1, T , and + , it may be inefficient to implement the translation directly by manipulating strings.
From Section 2.3.5, a syntax-directed translation scheme embeds program fragments called semantic actions within production bodies, as in
E ! E1 + T f print + g (5.2)
By convention, semantic actions are enclosed within curly braces. (If curly braces occur as grammar symbols, we enclose them within single quotes, as in f and g .) The position of a semantic action in a production body determines the order in which the action is executed. In production (5.2), the action occurs at the end, after all the grammar symbols; in general, semantic actions may occur at any position in a production body.
Between the two notations, syntax-directed definitions can be more readable, and hence more useful for specifications. However, translation schemes can be more efficient, and hence more useful for implementations.
The most general approach to syntax-directed translation is to construct a parse tree or a syntax tree, and then to compute the values of attributes at the nodes of the tree by visiting the nodes of the tree. In many cases, translation can be done during parsing, without building an explicit tree. We shall therefore study a class of syntax-directed translations called \L-attributed translations"
(L for left-to-right), which encompass virtually all translations that can be performed during parsing. We also study a smaller class, called \S-attributed translations" (S for synthesized), which can be performed easily in connection with a bottom-up parse.
