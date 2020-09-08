# 2.7 Symbol Tables

**Symbol tables** are data structures that are used by **compilers** to hold information about source-program constructs. The information is collected incrementally by the **analysis phases** of a **compiler** and used by the **synthesis phases** to generate the **target code**. Entries in the symbol table contain information about an identifier such as its character string (or lexeme), its type, its position in storage,and any other relevant information. Symbol tables typically need to support multiple declarations of the same identifier within a program.

From Section 1.6.1, the **scope** of a **declaration** is the portion of a program to which the **declaration** applies. We shall implement **scopes** by setting up a separate **symbol table** for each **scope**. A program block with declarations will have its own **symbol table** with an entry for each declaration in the block. This approach also works for other constructs that set up scopes; for example, a **class** would have its own table, with an entry for each **field** and **method**.

This section contains a symbol-table module suitable for use with the Java translator fragments in this chapter. The module will be used as is when we put together the translator in Appendix A. Meanwhile, for simplicity, the main example of this section is a stripped-down(被简化的) language with just the key constructs that touch symbol tables; namely, blocks, declarations, and factors. All of the other **statement** and **expression** constructs are omitted so we can focus on the symbol-table operations. A program consists of blocks with optional declarations and statements consisting of single identifiers. Each such statement represents a use of the identifier. Here is a sample program in this language



---

>Who Creates Symbol-Table Entries?
>
>Symbol-table entries are created and used during the analysis phase by the lexical analyzer, the parser, and the semantic analyzer. In this chapter,we have the parser create entries. With its knowledge of the syntactic structure of a program, a parser is often in a better position than the lexical analyzer to distinguish among different declarations of an identifier.In some cases, a lexical analyzer can create a symbol-table entry as so on as it sees the characters that make up a lexeme. More often, the lexical analyzer can only return to the parser a token, say id, along with a pointer to the lexeme. Only the parser, however, can decide whether to use a previously created symbol-table entry or create a new one for the identifier.

---

