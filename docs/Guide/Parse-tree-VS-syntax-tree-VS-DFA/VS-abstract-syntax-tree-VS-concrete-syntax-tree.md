[TOC]





# [What is the difference between an Abstract Syntax Tree and a Concrete Syntax Tree?](https://stackoverflow.com/questions/1888854/what-is-the-difference-between-an-abstract-syntax-tree-and-a-concrete-syntax-tre)

I've been reading a bit about how interpreters/compilers work, and one area where I'm getting confused is the difference between an AST and a CST. My understanding is that the **parser** makes a CST, hands it to the **semantic analyzer** which turns it into an **AST**. However, my understanding is that the **semantic analyzer** simply ensures that rules are followed. I don't really understand why it would actually make any changes to make it abstract rather than concrete.

Is there something that I'm missing about the **semantic analyzer**, or is the difference between an AST and CST somewhat artificial?



## [A](https://stackoverflow.com/a/1888973)



A **concrete syntax tree** represents the source text exactly in parsed form. In general, it conforms to the **context-free grammar** defining the source language.

However, the concrete grammar and tree have a lot of things that are necessary to make source text **unambiguously parseable**, but do not contribute to actual meaning. For example, to implement **operator precedence**, your CFG usually has several levels of expression components (term, factor, etc.), with the operators connecting them at the different levels (you add terms to get expressions, terms are composed of factors optionally multipled, etc.). To actually interpret or compile the language, however, you don't need this; you just need Expression nodes that have operators and operands. The abstract syntax tree is the result of simplifying the concrete syntax tree down to this things actually needed to represent the meaning of the program. This tree has a much simpler definition and is thus easier to process in the later stages of **execution**.

You usually don't need to actually build a concrete syntax tree. The action routines in your YACC (or Antlr, or Menhir, or whatever...) grammar can directly build the **abstract syntax tree**, so the **concrete syntax tree** only exists as a conceptual entity representing the parse structure of your source text.

***COMMENTS*** : 

-  Supplement: the Python interpreter first builds a CST and then converts to AST. – [cgsdfc](https://stackoverflow.com/users/8039762/cgsdfc) [Dec 2 '18 at 12:18](https://stackoverflow.com/questions/1888854/what-is-the-difference-between-an-abstract-syntax-tree-and-a-concrete-syntax-tree#comment94023727_1888973) 

## [A](https://stackoverflow.com/a/1916687)

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





## [A](https://stackoverflow.com/a/1888898)

[This blog post](http://eli.thegreenplace.net/2009/02/16/abstract-vs-concrete-syntax-trees/) may be helpful.

It seems to me that the AST "throws away" a lot of intermediate grammatical/structural information that wouldn't contribute to semantics. For example, you don't care that 3 is an atom is a term is a factor is a.... You just care that it's `3` when you're implementing the exponentiation expression or whatever.

# [What's the difference between parse tree and AST?](https://stackoverflow.com/questions/5026517/whats-the-difference-between-parse-tree-and-ast)

 Are they generated by different phases of a compiling process? Or are they just different names for the same thing? 

***COMMENTS***:

- **Parse Tree** is the result of your **grammar** with its artifacts (you can write an infinity of grammars for the same language), an **AST** reduce the **Parse Tree** the closest possible to the language. Several **grammars** for the same language will give different **parse trees** but should result to the same AST. (you can also reduce different scripts (different parse trees from the same grammar) to the same AST) – [Guillaume86](https://stackoverflow.com/users/172074/guillaume86) [Aug 29 '12 at 14:38](https://stackoverflow.com/questions/5026517/whats-the-difference-between-parse-tree-and-ast#comment16306109_5026517)  
- 



## [A](https://stackoverflow.com/a/9864571)

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

***COMMENTS***

-  How do you derive the AST from the parse tree? What's the method of simplifying a parse tree into an AST? – [CMCDragonkai](https://stackoverflow.com/users/582917/cmcdragonkai) [Feb 15 '15 at 8:54](https://stackoverflow.com/questions/5026517/whats-the-difference-between-parse-tree-and-ast#comment45364941_9864571) 





## [A](https://stackoverflow.com/a/5026608)

From what I understand, the AST focuses more on the abstract relationships between the components of source code, while the parse tree focuses on the actual implementation of the **grammar** utilized by the language, including the nitpicky details. They are definitely not the same, since another term for "parse tree" is "concrete syntax tree".

I found this [page](http://www.jguru.com/faq/view.jsp?EID=814505) which attempts to resolve this exact question.



## [A](https://stackoverflow.com/a/5026642)

The [DSL book](https://martinfowler.com/books/dsl.html) from Martin Fowler explains this nicely. The AST only contains all 'useful' elements that will be used for further processing, while the parse tree contains all the artifacts (spaces, brackets, ...) from the original document you parse 

## [A](https://stackoverflow.com/a/31811999)

Take the pascal assignment Age:= 42;

The syntax tree would look just like the source code. Below I am putting brackets around the nodes. `[Age][:=][42][;]`

An abstract tree would look like this `[=][Age][42]`

The assignment becomes a node with 2 elements, `Age` and `42`. The idea is that you can **execute** the assignment.

Also note that the pascal syntax disappears. Thus it is possible to have more than one language generate the same AST. This is useful for cross language script engines.





# [What would an AST (abstract syntax tree) for an object-oriented programming language look like?](https://stackoverflow.com/questions/6376662/what-would-an-ast-abstract-syntax-tree-for-an-object-oriented-programming-lang)

I'm reading about AST (abstract syntax trees) but all the samples I see use expressions such as:

```java
a + b * c 
```

Which could be represented in a lispy like syntax as:

```java
(+ a (* b c) )
```

Which will be the equivalent to:

```java
  +
 / \
a   * 
   / \
  b   c
```

My question is How an AST for a class in a OOPL would look like?

My naive attempt is for this Java code:

```java
 class Person { 
     String name;
     int    age;
     public String toString() { 
        return "name";
     }
 }
```

Is:

```java
;Hand written
(classDeclaration Person 
     (varDeclaration String name)
     (varDeclaration int    age )
     (funcDeclaration String toString 
           (return "name")
     )
 )
```

But I'm not quite sure how close or far am I to a real AST representation.

Does it depends on the language I choose. How much detail is needed? Are those "xyzDeclaraction" needed or could be as:

```java
 (Person (String name) (int age))
```

Where can I see a "real" representation of an actual programming language to learn more.



## [A](https://stackoverflow.com/a/6376707)

AST is an abstraction of the CST ([concrete syntax tree](http://en.wikipedia.org/wiki/Parse_tree), or, parse tree). The concrete syntax tree is the tree resulting from the productions (in the grammar) used to parse the file. So your AST is basically derived from your grammar definition, but has for transformed

```java
                        Exp                    
                      /  |  \                   
                     /   |   \                       *
                 Ident BinOp Ident       into       / \
                  /      |     \                  "x" "y"
                 /       |      \
               "x"       *      "y"
```

All in all I think the example in your post looks fine. I would probably wrap the variable declarations in a `varDeclList` and the function declaration in a `methDeclList`, and the return statement in a `stmtList`. (See below.)

One more or less "real" representation of an AST is described by Apple in his book "Modern Compiler Implementation in Java". (Resources can be found [here](http://www.cambridge.org/resources/052182060X/).)

Using those classes, your program would be represented as follows:

```java
Program
    ClassDeclList
        ClassDecl
            Identifier
                id: Person
            VarDeclList
                VarDecl
                    type: String
                    id: name
                VarDecl
                    type: int
                    id: age
            MethDeclList
                MethodDecl
                    modifiers: public
                    returnType: String
                    id: toString
                    Formals
                        (empty)
                    StmtList
                        returnStmt
                            Identifier
                                id: name
```



## [A](https://stackoverflow.com/a/6378997)

OP: *Where can I see a real representation of an actual programming language to learn more?*

For your source text as a file Person.java:

```java
class Person {  
    String name;
    int    age;
    public String toString()
      { return "name";     } 
}
```

what follows are both Concrete and Abstract Syntax Tree in an S-expression-style dump of the parser tree from our [DMS Software Reengineering Toolkit](http://www.semanticdesigns.com/Products/DMS/DMSToolkit.html), using its Java1.6 parser. All the apparant complexity is pretty much caused by the real complexity of the language (e.g., of Java itself).

The CST clearly contains more stuff (139 nodes) than the AST (54 nodes). The AST drops everything that can be automatically inferred from the grammar, given the AST. This includes removing non-value-carrying leaves, unary productions, and compressing spines caused by left or right recursive grammar rules into explicit list nodes.

A left paren signals a new subtree. Following the left paren is the name of the node type; @Java~Java1_.6 might seem unnecessary until you understand DMS can handle many languages at once, including langauges nested inside one another. The #nnnnnn is the memory address of the node. ^M means "this node has M parents and is left off when M==1. Things inside [...] are the node value. A { M } means this list node has M list-children. Each node is stamped with position information.

This is the Concrete Syntax tree (see further down for AST):

```java
(compilation_unit@Java~Java1_6=1#4885d00^0 Line 1 Column 1 File C:/temp/Person.java
 (type_declarations@Java~Java1_6=15#4885cc0 Line 1 Column 1 File C:/temp/Person.java
  (type_declarations@Java~Java1_6=16#4884d80 Line 1 Column 1 File C:/temp/Person.java)type_declarations
  (type_declaration@Java~Java1_6=17#4885ca0 Line 1 Column 1 File C:/temp/Person.java
   (type_class_modifiers@Java~Java1_6=77#4884dc0 Line 1 Column 1 File C:/temp/Person.java)type_class_modifiers
   (class_header@Java~Java1_6=89#4884ec0 Line 1 Column 1 File C:/temp/Person.java
   |('class'@Java~Java1_6=459#4884c60[Keyword:0] Line 1 Column 1 File C:/temp/Person.java)'class'
   |(IDENTIFIER@Java~Java1_6=447#4884e20[`Person'] Line 1 Column 7 File C:/temp/Person.java)IDENTIFIER
   |(type_parameters@Java~Java1_6=408#4884e80 Line 1 Column 14 File C:/temp/Person.java)type_parameters
   )class_header
   (class_body@Java~Java1_6=94#4885c80 Line 1 Column 14 File C:/temp/Person.java
   |('{'@Java~Java1_6=448#4884e60[Keyword:0] Line 1 Column 14 File C:/temp/Person.java)'{'
   |(class_body_declarations@Java~Java1_6=111#4885c60 Line 2 Column 5 File C:/temp/Person.java
   | (class_body_declarations@Java~Java1_6=111#4885380 Line 2 Column 5 File C:/temp/Person.java
   |  (class_body_declarations@Java~Java1_6=110#4885400 Line 2 Column 5 File C:/temp/Person.java
   |   (class_body_declaration@Java~Java1_6=118#4885360 Line 2 Column 5 File C:/temp/Person.java
   |   |(field_declaration@Java~Java1_6=168#4885440 Line 2 Column 5 File C:/temp/Person.java
   |   | (field_modifiers@Java~Java1_6=170#4884f40 Line 2 Column 5 File C:/temp/Person.java)field_modifiers
   |   | (type@Java~Java1_6=191#48852c0 Line 2 Column 5 File C:/temp/Person.java
   |   |  (name@Java~Java1_6=406#48851e0 Line 2 Column 5 File C:/temp/Person.java
   |   |   (IDENTIFIER@Java~Java1_6=447#4884f20[`String'] Line 2 Column 5 File C:/temp/Person.java)IDENTIFIER
   |   |   (type_arguments@Java~Java1_6=407#4885160 Line 2 Column 12 File C:/temp/Person.java)type_arguments
   |   |  )name
   |   |  (brackets@Java~Java1_6=157#4885260 Line 2 Column 12 File C:/temp/Person.java)brackets
   |   | )type
   |   | (variable_declarator_list@Java~Java1_6=179#4884e00 Line 2 Column 12 File C:/temp/Person.java
   |   |  (variable_declarator@Java~Java1_6=181#4885300 Line 2 Column 12 File C:/temp/Person.java
   |   |   (variable_declarator_id@Java~Java1_6=167#4885320 Line 2 Column 12 File C:/temp/Person.java
   |   |   |(IDENTIFIER@Java~Java1_6=447#4885140[`name'] Line 2 Column 12 File C:/temp/Person.java)IDENTIFIER
   |   |   |(brackets@Java~Java1_6=157#4885040 Line 2 Column 16 File C:/temp/Person.java)brackets
   |   |   )variable_declarator_id
   |   |  )variable_declarator
   |   | )variable_declarator_list
   |   | (';'@Java~Java1_6=440#4885100[Keyword:0] Line 2 Column 16 File C:/temp/Person.java)';'
   |   |)field_declaration
   |   )class_body_declaration
   |  )class_body_declarations
   |  (class_body_declaration@Java~Java1_6=118#48852e0 Line 3 Column 5 File C:/temp/Person.java
   |   (field_declaration@Java~Java1_6=168#4885480 Line 3 Column 5 File C:/temp/Person.java
   |   |(field_modifiers@Java~Java1_6=170#4885340 Line 3 Column 5 File C:/temp/Person.java)field_modifiers
   |   |(type@Java~Java1_6=192#4885220 Line 3 Column 5 File C:/temp/Person.java
   |   | (primitive_type@Java~Java1_6=198#4885420 Line 3 Column 5 File C:/temp/Person.java
   |   |  ('int'@Java~Java1_6=479#48853e0[Keyword:0] Line 3 Column 5 File C:/temp/Person.java)'int'
   |   | )primitive_type
   |   | (brackets@Java~Java1_6=157#4885200 Line 3 Column 12 File C:/temp/Person.java)brackets
   |   |)type
   |   |(variable_declarator_list@Java~Java1_6=179#4885540 Line 3 Column 12 File C:/temp/Person.java
   |   | (variable_declarator@Java~Java1_6=181#4885520 Line 3 Column 12 File C:/temp/Person.java
   |   |  (variable_declarator_id@Java~Java1_6=167#4885500 Line 3 Column 12 File C:/temp/Person.java
   |   |   (IDENTIFIER@Java~Java1_6=447#4884fc0[`age'] Line 3 Column 12 File C:/temp/Person.java)IDENTIFIER
   |   |   (brackets@Java~Java1_6=157#48854e0 Line 3 Column 15 File C:/temp/Person.java)brackets
   |   |  )variable_declarator_id
   |   | )variable_declarator
   |   |)variable_declarator_list
   |   |(';'@Java~Java1_6=440#48854c0[Keyword:0] Line 3 Column 15 File C:/temp/Person.java)';'
   |   )field_declaration
   |  )class_body_declaration
   | )class_body_declarations
   | (class_body_declaration@Java~Java1_6=117#4885c40 Line 4 Column 5 File C:/temp/Person.java
   |  (method_declaration@Java~Java1_6=135#4885c00 Line 4 Column 5 File C:/temp/Person.java
   |   (method_modifiers@Java~Java1_6=141#4885700 Line 4 Column 5 File C:/temp/Person.java
   |   |(method_modifiers@Java~Java1_6=142#4884e40 Line 4 Column 5 File C:/temp/Person.java)method_modifiers
   |   |(method_modifier@Java~Java1_6=147#48856a0 Line 4 Column 5 File C:/temp/Person.java
   |   | ('public'@Java~Java1_6=453#48853a0[Keyword:0] Line 4 Column 5 File C:/temp/Person.java)'public'
   |   |)method_modifier
   |   )method_modifiers
   |   (type_parameters@Java~Java1_6=408#4885740 Line 4 Column 12 File C:/temp/Person.java)type_parameters
   |   (type@Java~Java1_6=191#4885900 Line 4 Column 12 File C:/temp/Person.java
   |   |(name@Java~Java1_6=406#48852a0 Line 4 Column 12 File C:/temp/Person.java
   |   | (IDENTIFIER@Java~Java1_6=447#4885660[`String'] Line 4 Column 12 File C:/temp/Person.java)IDENTIFIER
   |   | (type_arguments@Java~Java1_6=407#48851a0 Line 4 Column 19 File C:/temp/Person.java)type_arguments
   |   |)name
   |   |(brackets@Java~Java1_6=157#48858c0 Line 4 Column 19 File C:/temp/Person.java)brackets
   |   )type
   |   (IDENTIFIER@Java~Java1_6=447#48855c0[`toString'] Line 4 Column 19 File C:/temp/Person.java)IDENTIFIER
   |   (parameters@Java~Java1_6=158#48858e0 Line 4 Column 27 File C:/temp/Person.java
   |   |('('@Java~Java1_6=450#4885840[Keyword:0] Line 4 Column 27 File C:/temp/Person.java)'('
   |   |(')'@Java~Java1_6=451#4885620[Keyword:0] Line 4 Column 28 File C:/temp/Person.java)')'
   |   )parameters
   |   (brackets@Java~Java1_6=157#4885060 Line 5 Column 7 File C:/temp/Person.java)brackets
   |   (block@Java~Java1_6=217#4885be0 Line 5 Column 7 File C:/temp/Person.java
   |   |('{'@Java~Java1_6=448#48851c0[Keyword:0] Line 5 Column 7 File C:/temp/Person.java)'{'
   |   |(statement_sequence@Java~Java1_6=218#4885ba0 Line 5 Column 9 File C:/temp/Person.java
   |   | (statement_sequence_member@Java~Java1_6=223#4885b80 Line 5 Column 9 File C:/temp/Person.java
   |   |  (executable_statement@Java~Java1_6=243#4885b60 Line 5 Column 9 File C:/temp/Person.java
   |   |   ('return'@Java~Java1_6=491#4884f60[Keyword:0] Line 5 Column 9 File C:/temp/Person.java)'return'
   |   |   (expression@Java~Java1_6=332#4885ac0 Line 5 Column 16 File C:/temp/Person.java
   |   |   |(conditional_expression@Java~Java1_6=345#4885a60 Line 5 Column 16 File C:/temp/Person.java
   |   |   | (conditional_or_expression@Java~Java1_6=347#4885a20 Line 5 Column 16 File C:/temp/Person.java
   |   |   |  (conditional_and_expression@Java~Java1_6=349#48859e0 Line 5 Column 16 File C:/temp/Person.java
   |   |   |   (inclusive_or_expression@Java~Java1_6=351#48857e0 Line 5 Column 16 File C:/temp/Person.java
   |   |   |   |(exclusive_or_expression@Java~Java1_6=353#48855a0 Line 5 Column 16 File C:/temp/Person.java
   |   |   |   | (and_expression@Java~Java1_6=355#4885940 Line 5 Column 16 File C:/temp/Person.java
   |   |   |   |  (equality_expression@Java~Java1_6=357#4885880 Line 5 Column 16 File C:/temp/Person.java
   |   |   |   |   (relational_expression@Java~Java1_6=360#4885800 Line 5 Column 16 File C:/temp/Person.java
   |   |   |   |   |(shift_expression@Java~Java1_6=366#48856c0 Line 5 Column 16 File C:/temp/Person.java
   |   |   |   |   | (additive_expression@Java~Java1_6=370#4885180 Line 5 Column 16 File C:/temp/Person.java
   |   |   |   |   |  (multiplicative_expression@Java~Java1_6=373#4885780 Line 5 Column 16 File C:/temp/Person.java
   |   |   |   |   |   (unary_expression@Java~Java1_6=383#4885600 Line 5 Column 16 File C:/temp/Person.java
   |   |   |   |   |   |(unary_expression_not_plus_minus@Java~Java1_6=389#4885680 Line 5 Column 16 File C:/temp/Person.java
   |   |   |   |   |   | (literal@Java~Java1_6=390#4884f80 Line 5 Column 16 File C:/temp/Person.java
   |   |   |   |   |   |  (STRING@Java~Java1_6=536#4885120[`name'] Line 5 Column 16 File C:/temp/Person.java)STRING
   |   |   |   |   |   | )literal
   |   |   |   |   |   |)unary_expression_not_plus_minus
   |   |   |   |   |   )unary_expression
   |   |   |   |   |  )multiplicative_expression
   |   |   |   |   | )additive_expression
   |   |   |   |   |)shift_expression
   |   |   |   |   )relational_expression
   |   |   |   |  )equality_expression
   |   |   |   | )and_expression
   |   |   |   |)exclusive_or_expression
   |   |   |   )inclusive_or_expression
   |   |   |  )conditional_and_expression
   |   |   | )conditional_or_expression
   |   |   |)conditional_expression
   |   |   )expression
   |   |   (';'@Java~Java1_6=440#48856e0[Keyword:0] Line 5 Column 22 File C:/temp/Person.java)';'
   |   |  )executable_statement
   |   | )statement_sequence_member
   |   |)statement_sequence
   |   |('}'@Java~Java1_6=449#4885b40[Keyword:0] Line 5 Column 28 File C:/temp/Person.java)'}'
   |   )block
   |  )method_declaration
   | )class_body_declaration
   |)class_body_declarations
   |('}'@Java~Java1_6=449#4885bc0[Keyword:0] Line 6 Column 1 File C:/temp/Person.java)'}'
   )class_body
  )type_declaration
 )type_declarations
 (optional_CONTROL_Z@Java~Java1_6=5#4885ce0 Line 7 Column 1 File C:/temp/Person.java)optional_CONTROL_Z
)compilation_unit
```

This is the AST (automatically generated by DMS from the CST):

```java
(compilation_unit@Java~Java1_6=1#486f900^0 Line 1 Column 1 File C:/temp/Person.java
 (type_declarations@Java~Java1_6=15#486f4c0 {1} Line 1 Column 1 File C:/temp/Person.java
  (type_declaration@Java~Java1_6=17#486f5e0 Line 1 Column 1 File C:/temp/Person.java
   (type_class_modifiers@Java~Java1_6=77#486eda0 Line 1 Column 1 File C:/temp/Person.java)type_class_modifiers
   (class_header@Java~Java1_6=89#486ee60 Line 1 Column 1 File C:/temp/Person.java
   |(IDENTIFIER@Java~Java1_6=447#486ede0[`Person'] Line 1 Column 7 File C:/temp/Person.java)IDENTIFIER
   |(type_parameters@Java~Java1_6=408#486ee20 Line 1 Column 14 File C:/temp/Person.java)type_parameters
   )class_header
   (class_body@Java~Java1_6=94#486f040 Line 1 Column 14 File C:/temp/Person.java
   |(class_body_declarations@Java~Java1_6=111#486ee40 {3} Line 2 Column 5 File C:/temp/Person.java
   | (class_body_declaration@Java~Java1_6=118#486f300 Line 2 Column 5 File C:/temp/Person.java
   |  (field_declaration@Java~Java1_6=168#486f380 Line 2 Column 5 File C:/temp/Person.java
   |   (field_modifiers@Java~Java1_6=170#486eec0 Line 2 Column 5 File C:/temp/Person.java)field_modifiers
   |   (type@Java~Java1_6=191#486f240 Line 2 Column 5 File C:/temp/Person.java
   |   |(name@Java~Java1_6=406#486f180 Line 2 Column 5 File C:/temp/Person.java
   |   | (IDENTIFIER@Java~Java1_6=447#486eea0[`String'] Line 2 Column 5 File C:/temp/Person.java)IDENTIFIER
   |   | (type_arguments@Java~Java1_6=407#486f0e0 Line 2 Column 12 File C:/temp/Person.java)type_arguments
   |   |)name
   |   |(brackets@Java~Java1_6=157#486f200 Line 2 Column 12 File C:/temp/Person.java)brackets
   |   )type
   |   (variable_declarator@Java~Java1_6=181#486ef20 Line 2 Column 12 File C:/temp/Person.java
   |   |(variable_declarator_id@Java~Java1_6=167#486efe0 Line 2 Column 12 File C:/temp/Person.java
   |   | (IDENTIFIER@Java~Java1_6=447#486f0c0[`name'] Line 2 Column 12 File C:/temp/Person.java)IDENTIFIER
   |   | (brackets@Java~Java1_6=157#486f060 Line 2 Column 16 File C:/temp/Person.java)brackets
   |   |)variable_declarator_id
   |   )variable_declarator
   |  )field_declaration
   | )class_body_declaration
   | (class_body_declaration@Java~Java1_6=118#486f000 Line 3 Column 5 File C:/temp/Person.java
   |  (field_declaration@Java~Java1_6=168#486f320 Line 3 Column 5 File C:/temp/Person.java
   |   (field_modifiers@Java~Java1_6=170#486f2a0 Line 3 Column 5 File C:/temp/Person.java)field_modifiers
   |   (type@Java~Java1_6=192#486eee0 Line 3 Column 5 File C:/temp/Person.java
   |   |(primitive_type@Java~Java1_6=198#486ef60 Line 3 Column 5 File C:/temp/Person.java)primitive_type
   |   |(brackets@Java~Java1_6=157#486ee00 Line 3 Column 12 File C:/temp/Person.java)brackets
   |   )type
   |   (variable_declarator@Java~Java1_6=181#486f2c0 Line 3 Column 12 File C:/temp/Person.java
   |   |(variable_declarator_id@Java~Java1_6=167#486f3a0 Line 3 Column 12 File C:/temp/Person.java
   |   | (IDENTIFIER@Java~Java1_6=447#486f120[`age'] Line 3 Column 12 File C:/temp/Person.java)IDENTIFIER
   |   | (brackets@Java~Java1_6=157#486ef00 Line 3 Column 15 File C:/temp/Person.java)brackets
   |   |)variable_declarator_id
   |   )variable_declarator
   |  )field_declaration
   | )class_body_declaration
   | (class_body_declaration@Java~Java1_6=117#486f7a0 Line 4 Column 5 File C:/temp/Person.java
   |  (method_declaration@Java~Java1_6=135#486f480 Line 4 Column 5 File C:/temp/Person.java
   |   (method_modifiers@Java~Java1_6=141#486f460 {1} Line 4 Column 5 File C:/temp/Person.java
   |   |(method_modifier@Java~Java1_6=147#486f400 Line 4 Column 5 File C:/temp/Person.java)method_modifier
   |   )method_modifiers
   |   (type_parameters@Java~Java1_6=408#486f540 Line 4 Column 12 File C:/temp/Person.java)type_parameters
   |   (type@Java~Java1_6=191#486f740 Line 4 Column 12 File C:/temp/Person.java
   |   |(name@Java~Java1_6=406#486f620 Line 4 Column 12 File C:/temp/Person.java
   |   | (IDENTIFIER@Java~Java1_6=447#486f080[`String'] Line 4 Column 12 File C:/temp/Person.java)IDENTIFIER
   |   | (type_arguments@Java~Java1_6=407#486f640 Line 4 Column 19 File C:/temp/Person.java)type_arguments
   |   |)name
   |   |(brackets@Java~Java1_6=157#486f700 Line 4 Column 19 File C:/temp/Person.java)brackets
   |   )type
   |   (IDENTIFIER@Java~Java1_6=447#486f140[`toString'] Line 4 Column 19 File C:/temp/Person.java)IDENTIFIER
   |   (parameters@Java~Java1_6=158#486f760 Line 4 Column 27 File C:/temp/Person.java)parameters
   |   (brackets@Java~Java1_6=157#486f820 Line 5 Column 7 File C:/temp/Person.java)brackets
   |   (block@Java~Java1_6=217#486f780 Line 5 Column 7 File C:/temp/Person.java
   |   |(statement_sequence@Java~Java1_6=218#486f6e0 Line 5 Column 9 File C:/temp/Person.java
   |   | (statement_sequence_member@Java~Java1_6=223#486f6c0 Line 5 Column 9 File C:/temp/Person.java
   |   |  (executable_statement@Java~Java1_6=243#486f6a0 Line 5 Column 9 File C:/temp/Person.java
   |   |   (unary_expression_not_plus_minus@Java~Java1_6=389#486f720 Line 5 Column 16 File C:/temp/Person.java
   |   |   |(literal@Java~Java1_6=390#486f280 Line 5 Column 16 File C:/temp/Person.java
   |   |   | (STRING@Java~Java1_6=536#486f160[`name'] Line 5 Column 16 File C:/temp/Person.java)STRING
   |   |   |)literal
   |   |   )unary_expression_not_plus_minus
   |   |  )executable_statement
   |   | )statement_sequence_member
   |   |)statement_sequence
   |   )block
   |  )method_declaration
   | )class_body_declaration
   |)class_body_declarations
   )class_body
  )type_declaration
 )type_declarations
 (optional_CONTROL_Z@Java~Java1_6=5#486f4e0 Line 7 Column 1 File C:/temp/Person.java)optional_CONTROL_Z
)compilation_unit
```

EDIT March 2015: [Here's a link to some C++ AST examples](https://stackoverflow.com/a/17393852/120163)

Edit May 2015: DMS has long done Java 1.7 and 1.8, too.





# [DMS Software Reengineering Toolkit](https://en.wikipedia.org/wiki/DMS_Software_Reengineering_Toolkit)





# [Abstract vs. Concrete Syntax Trees](https://eli.thegreenplace.net/2009/02/16/abstract-vs-concrete-syntax-trees)





# [Compiling an AST back to source code](https://stackoverflow.com/questions/5832412/compiling-an-ast-back-to-source-code)