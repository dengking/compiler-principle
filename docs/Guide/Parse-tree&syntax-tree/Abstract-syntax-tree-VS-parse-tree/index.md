# Abstract Syntax Tree VS Concrete Syntax Tree

龙书中区分parse tree和syntax tree的章节有：

一、2.5.1 Abstract and Concrete Syntax

> Abstract syntax trees, or simply *syntax trees*, resemble(类似于) parse trees to an extent. However, in the **syntax tree**, **interior nodes** represent **programming constructs** while in the **parse tree**, the **interior nodes** represent **nonterminals**. Many nonterminals of a grammar represent programming constructs, but others are "helpers" of one sort of another, such as those representing terms, factors, or other variations of expressions. In the syntax tree, these helpers typically are not needed and are hence dropped. To emphasize the contrast, a **parse tree** is sometimes called a *concrete syntax tree*, and the underlying grammar is called a concrete syntax for the language.





## stackoverflow [What is the difference between an Abstract Syntax Tree and a Concrete Syntax Tree?](https://stackoverflow.com/questions/1888854/what-is-the-difference-between-an-abstract-syntax-tree-and-a-concrete-syntax-tre)

I've been reading a bit about how interpreters/compilers work, and one area where I'm getting confused is the difference between an AST and a CST. My understanding is that the **parser** makes a CST, hands it to the **semantic analyzer** which turns it into an **AST**. However, my understanding is that the **semantic analyzer** simply ensures that rules are followed. I don't really understand why it would actually make any changes to make it abstract rather than concrete.

Is there something that I'm missing about the **semantic analyzer**, or is the difference between an AST and CST somewhat artificial?



### [A](https://stackoverflow.com/a/1888973)

A **concrete syntax tree** represents the source text exactly in parsed form. In general, it conforms to the **context-free grammar** defining the source language.

However, the concrete grammar and tree have a lot of things that are necessary to make source text **unambiguously(无二义的) parseable**, but do not contribute to actual meaning. For example, to implement **operator precedence**, your CFG usually has several levels of expression components (term, factor, etc.), with the operators connecting them at the different levels (you add terms to get expressions, terms are composed of factors optionally multipled, etc.). To actually interpret or compile the language, however, you don't need this; you just need Expression nodes that have operators and operands. The **abstract syntax tree** is the result of simplifying the **concrete syntax tree** down to this things actually needed to represent the meaning of the program. This tree has a much simpler definition and is thus easier to process in the later stages of **execution**.

You usually don't need to actually build a **concrete syntax tree**. The action routines in your YACC (or Antlr, or Menhir, or whatever...) grammar can directly build the **abstract syntax tree**, so the **concrete syntax tree** only exists as a conceptual entity representing the parse structure of your source text.

***COMMENTS*** : 

Supplements: the Python interpreter first builds a CST and then converts to AST. – [cgsdfc](https://stackoverflow.com/users/8039762/cgsdfc) [Dec 2 '18 at 12:18](https://stackoverflow.com/questions/1888854/what-is-the-difference-between-an-abstract-syntax-tree-and-a-concrete-syntax-tree#comment94023727_1888973) 

### [A](https://stackoverflow.com/a/1916687)

A *concrete syntax tree* matches what the grammar rules say is the syntax. The purpose of the *abstract syntax tree* is have a "simple" representation of what's essential in "the syntax tree".

A real value in the AST IMHO is that it is *smaller* than the CST, and therefore takes less time to process. (You might say, who cares? But I work with a tool where we have tens of millions of nodes live at once!).

Most parser generators that have any support for building syntax trees insist that you personally specify exactly how they get built under the assumption that your tree nodes will be "simpler" than the CST (and in that, they are generally right, as programmers are pretty lazy). Arguably it means you have to code fewer tree visitor functions, and that's valuable, too, in that it minimizes engineering energy. When you have 3500 rules (e.g., for COBOL) this matters. And this "simpler"ness leads to the good property of "smallness".

But having such ASTs creates a problem that wasn't there: it doesn't match the grammar, and now you have to mentally track both of them. And when there are 1500 AST nodes for a 3500 rule grammar, this matters a lot. And if the grammar evolves (they always do!), now you have two giant sets of things to keep in synch.

Another solution is to let the parser simply build CST nodes for you and just use those. This is a huge advantage when building the grammars: there's no need to invent 1500 special AST nodes to model 3500 grammar rules. Just think about the tree being isomorphic to the grammar. From the point of view of the grammar engineer this is completely brainless, which lets him focus on getting the grammar right and hacking at it to his heart's content. Arguably you have to write more node visitor rules, but that can be managed. More on this later.

What we do with the [DMS Software Reengineering Toolkit](http://www.semanticdesigns.com/Products/DMS/DMSToolkit.html) is to automatically build a CST based on the results of a (GLR) parsing process. DMS then automatically constructs an "compressed" CST for space efficiency reasons, by eliminating non-value carrying terminals (keywords, punctation), semantically useless unary productions, and forming lists for grammar rule pairs that are list like:

```
    L = e ;
    L = L e ;
    L2 = e2 ;
    L2 = L2  ','  e2 ;
```

and a wide variety of variations of such forms. You think in terms of the grammar rules and the virtual CST; the tool operates on the compressed representation. Easy on your brain, faster/smaller at runtime.

Remarkably, the compressed CST built this way looks a lot an AST that you might have designed by hand (see link at end to examples). In particular, the compressed CST doesn't carry any nodes that are just concrete syntax. There are minor bits of awkwardness: for example while the concrete nodes for '(' and ')' classically found in expression subgrammars are not in the tree, a "parentheses node" *does* appear in the compressed CST and has to be handled. A true AST would not have this. This seems like a pretty small price to pay for the convenience of not have to specify the AST construction, ever. And the documentation for the tree is always available and correct: the grammar *is* the documentation.

How do we avoid "extra visitors"? We don't entirely, but DMS provides an AST library that walks the AST and handles the differences between the CST and the AST transparently. DMS also offers an "attribute grammar" evaluator (AGE), which is a method for passing values computed a nodes up and down the tree; the AGE handles all the tree representation issues and so the tool engineer only worries about writing computations effectively directly on the grammar rules themselves. Finally, DMS also provides "surface-syntax" patterns, which allows code fragments from the grammar to used to find specific types of subtrees, without knowing most of the node types involved.

One of the other answers observes that if you want to build tools that can regenerate source, your AST will have to match the CST. That's not really right, but it is far easier to regenerate the source if you have CST nodes. [DMS generates most of the prettyprinter automatically](https://stackoverflow.com/questions/5832412/compiling-an-ast-back-to-source-code/5834775#5834775) because it has access to both :-}

Bottom line: ASTs are good for small, both phyiscal and conceptual. Automated AST construction from the CST provides both, and lets you avoid the problem of tracking two different sets.

EDIT March 2015: [Link to examples of CST vs. "AST" built this way](https://stackoverflow.com/a/6378997/120163)





### [A](https://stackoverflow.com/a/1888898)

[This blog post](http://eli.thegreenplace.net/2009/02/16/abstract-vs-concrete-syntax-trees/) may be helpful.

It seems to me that the AST "throws away" a lot of intermediate grammatical/structural information that wouldn't contribute to semantics. For example, you don't care that 3 is an atom is a term is a factor is a.... You just care that it's `3` when you're implementing the exponentiation expression or whatever.



## stackoverflow [What's the difference between parse tree and AST?](https://stackoverflow.com/questions/5026517/whats-the-difference-between-parse-tree-and-ast)

 Are they generated by different phases of a compiling process? Or are they just different names for the same thing? 

***COMMENTS***:

1、**Parse Tree** is the result of your **grammar** with its artifacts (you can write an infinity of grammars for the same language), an **AST** reduce the **Parse Tree** the closest possible to the language. Several **grammars** for the same language will give different **parse trees** but should result to the same AST. (you can also reduce different scripts (different parse trees from the same grammar) to the same AST) – [Guillaume86](https://stackoverflow.com/users/172074/guillaume86) [Aug 29 '12 at 14:38](https://stackoverflow.com/questions/5026517/whats-the-difference-between-parse-tree-and-ast#comment16306109_5026517)  



### [A](https://stackoverflow.com/a/9864571)

This is based on the [Expression Evaluator](http://www.antlr3.org/works/help/tutorial/calculator.html) grammar by Terrence Parr.

The grammar for this example:

```
grammar Expr002;

options 
{
    output=AST;
    ASTLabelType=CommonTree; // type of $stat.tree ref etc...
}

prog    :   ( stat )+ ;

stat    :   expr NEWLINE        -> expr
        |   ID '=' expr NEWLINE -> ^('=' ID expr)
        |   NEWLINE             ->
        ;

expr    :   multExpr (( '+'^ | '-'^ ) multExpr)*
        ; 

multExpr
        :   atom ('*'^ atom)*
        ; 

atom    :   INT 
        |   ID
        |   '('! expr ')'!
        ;

ID      : ('a'..'z' | 'A'..'Z' )+ ;
INT     : '0'..'9'+ ;
NEWLINE : '\r'? '\n' ;
WS      : ( ' ' | '\t' )+ { skip(); } ;
```

Input

```
x=1
y=2
3*(x+y)
```

**Parse Tree**

The parse tree is a concrete representation of the input. The parse tree retains all of the information of the input. The empty boxes represent whitespace, i.e. end of line.

![Parse Tree](https://i.stack.imgur.com/SyonV.png)

**AST**

The AST is an abstract representation of the input. Notice that parens are not present in the AST because the associations are derivable from the tree structure.

![AST](https://i.stack.imgur.com/dhd3v.png)

For a more through explanation see [Compilers and Compiler Generators](http://www.cs.ru.ac.za/compilers/pdfvers.pdf) pg. 23
or [Abstract Syntax Trees](http://homepage.divms.uiowa.edu/~slonnegr/plf/Book/Chapter1.pdf) on pg. 21 in [Syntax and Semantics of Programming Languages](http://homepage.divms.uiowa.edu/~slonnegr/plf/Book/)



### [A](https://stackoverflow.com/a/5026608)

From what I understand, the AST focuses more on the abstract relationships between the components of source code, while the parse tree focuses on the actual implementation of the **grammar** utilized by the language, including the nitpicky details. They are definitely not the same, since another term for "parse tree" is "concrete syntax tree".

I found this [page](http://www.jguru.com/faq/view.jsp?EID=814505) which attempts to resolve this exact question.



### [A](https://stackoverflow.com/a/5026642)

The [DSL book](https://martinfowler.com/books/dsl.html) from Martin Fowler explains this nicely. The AST only contains all 'useful' elements that will be used for further processing, while the parse tree contains all the artifacts (spaces, brackets, ...) from the original document you parse 

### [A](https://stackoverflow.com/a/31811999)

Take the pascal assignment Age:= 42;

The syntax tree would look just like the source code. Below I am putting brackets around the nodes. `[Age][:=][42][;]`

An abstract tree would look like this `[=][Age][42]`

The assignment becomes a node with 2 elements, `Age` and `42`. The idea is that you can **execute** the assignment.

Also note that the pascal syntax disappears. Thus it is possible to have more than one language generate the same AST. This is useful for cross language script engines.



## TODO

stackoverflow [What would an AST (abstract syntax tree) for an object-oriented programming language look like?](https://stackoverflow.com/questions/6376662/what-would-an-ast-abstract-syntax-tree-for-an-object-oriented-programming-lang)

stackoverflow [Compiling an AST back to source code](https://stackoverflow.com/questions/5832412/compiling-an-ast-back-to-source-code)

thegreenplace [Abstract vs. Concrete Syntax Trees](https://eli.thegreenplace.net/2009/02/16/abstract-vs-concrete-syntax-trees)



## draft

在《Compilers Principles, Techniques, & Tools Second Edition》4.2.4 Parse Trees and Derivations节中有这样的描述：

> A parse tree is a graphical representation of a derivation that filters out the **order** in which productions are applied to replace nonterminals. Each interior node of a parse tree represents the application of a production. The interior node is labeled with the nonterminal `A` in the head of the production; the children of the node are labeled, from left to right, by the symbols in the body of the production by which this `A` was replaced during the derivation.

expression tree的interior node是operator。

两者之间既存在着相同点也存在着不同点。



