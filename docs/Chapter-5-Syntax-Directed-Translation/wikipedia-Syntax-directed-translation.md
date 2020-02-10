[TOC]



# [Syntax-directed translation](https://en.wikipedia.org/wiki/Syntax-directed_translation)

**Syntax-directed translation** refers to a method of [compiler](https://en.wikipedia.org/wiki/Compiler) implementation where the source language translation is completely driven by the [parser](https://en.wikipedia.org/wiki/Parser).

A common method of syntax-directed translation is translating a string into a sequence of actions by attaching one such action to each rule of a [grammar](https://en.wikipedia.org/wiki/Grammar).[[1\]](https://en.wikipedia.org/wiki/Syntax-directed_translation#cite_note-Gurari-1) Thus, parsing a string of the grammar produces a sequence of rule applications. SDT provides a simple way to attach [semantics](https://en.wikipedia.org/wiki/Semantics) to any such [syntax](https://en.wikipedia.org/wiki/Syntax).

## Overview

Syntax-directed translation fundamentally works by adding actions to the productions in a [context-free grammar](https://en.wikipedia.org/wiki/Context-free_grammar), resulting in a Syntax-Directed Definition (SDD).[[2\]](https://en.wikipedia.org/wiki/Syntax-directed_translation#cite_note-Alfred-2) Actions are steps or procedures that will be carried out when that production is used in a derivation. A grammar specification embedded with actions to be performed is called a *syntax-directed translation scheme*[[1\]](https://en.wikipedia.org/wiki/Syntax-directed_translation#cite_note-Gurari-1) (sometimes simply called a 'translation scheme'.)

Each symbol in the grammar can have an *attribute*, which is a value that is to be associated with the symbol. Common attributes could include a variable type, the value of an expression, etc. Given a symbol *X*, with an attribute *t*, that attribute is referred to as *X*.*t*

Thus, given actions and attributes, the grammar can be used for translating strings from its language by applying the actions and carrying information through each symbol's attribute.