# 2.1 Introduction

The analysis phase of a compiler breaks up a source program into constituent pieces and produces an internal representation for it, called intermediate code. 

The synthesis phase translates the intermediate code into the target program.

## What "syntax" of programming language can do

Analysis is organized around the "**syntax**" of the language to be compiled. The syntax of a programming language describes the proper form of its programs, while the **semantics** of the language defines what its programs mean; that is, what each program does when it executes. For specifying syntax, we present a widely used notation, called [**context-free grammars**](https://en.wikipedia.org/wiki/Context-free_grammar) or **BNF (for Backus-Naur Form)** in Section 2.2. With the notations currently available, the **semantics** of a language is much more difficult to describe than the **syntax**. For specifying semantics, we shall therefore use informal descriptions and suggestive examples. 

Besides specifying the **syntax** of a language, a **context-free grammar** can be used to help guide the translation of programs. In Section 2.3, we introduce a grammar-oriented compiling technique known as **syntax-directed translation**. Parsing or syntax analysis is introduced in Section 2.4.

> NOTE:
>
> 一、For compiler, what can **syntax** do?
>
> 1、Specify syntax as described in Section 2.2
>
> 2、Help guide the translation of programs, a grammar-oriented compiling technique known as [*syntax-directed translation*](https://en.wikipedia.org/wiki/Syntax-directed_translation) introduced  in Section 2.4



## The model of a compiler front end 

The rest of this chapter is a quick tour through the model of a compiler front end in Fig. 2.3.

We begin with the parser. For simplicity, we consider the **syntax-directed translation** of **infix** expressions to **postfix** form, a notation in which operators appear after their operands. For example, the postx form of the expression `9 - 5 + 2` is `95 - 2+`. Translation into postfix form is rich enough to illustrate **syntax analysis**, yet simple enough that the translator is shown in full in Section 2.5. The simple translator handles expressions like `9 - 5 + 2`, consisting of digits separated by plus and minus signs. One reason for starting with such simple expressions is that the syntax analyzer can work directly with the individual characters for operators and nd operands.

...

Next, we consider **intermediate-code generation**. Two forms of intermediate code are illustrated in Fig. 2.4. One form, called **abstract syntax trees** or simply **syntax trees**, represents the hierarchical syntactic structure of the source program. In the model in Fig. 2.3, the parser produces a **syntax tree**, that is further translated into **three-address code**. Some compilers combine parsing and **intermediate-code generation** into one component.

