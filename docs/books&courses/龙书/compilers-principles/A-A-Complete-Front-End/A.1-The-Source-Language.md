## A.1 The Source Language

A program in the language consists of a block with optional declarations and statements. Token basic represents basic types.
program block block { decls stmts } decls decls decl
! j decl type id ;
type type [ num ] basic
! j stmts stmts stmt
! j
Treating assignments as statements, rather than as operators within expressions, simplifies translation.
Object-Oriented Versus Phase-Oriented
With an object-oriented approach, all the code for a construct is collected in the class for the construct. Alternatively, with a phase-oriented approach, the code is grouped by phase, so a type checking procedure would have a case for each construct, and a code generation procedure would have a case for each construct, and so on.
The tradeoff is that an object-oriented approach makes it easier to change or add a construct, such as \for" statements, and a phase-oriented approach makes it easier to change or add a phase, such as type checking.
With objects, a new construct can be added by writing a self-contained class, but a change to a phase, such as inserting code for coercions, requires changes across all the affected classes. With phases, a new construct can result in changes across the procedures for the phases.
stmt loc = bool ;
if ( bool ) stmt j if ( bool ) stmt else stmt j while ( bool ) stmt j do stmt while ( bool ) ;
j break ;
j block j loc loc [ bool ] id
! j
The productions for expressions handle associativity and precedence of operators. They use a nonterminal for each level of precedence and a nonterminal, factor, for parenthesized expressions, identifiers, array references, and constants.
bool bool || join join
! j join join && equality equality
! j equality equality == rel equality != rel rel
! j j rel expr < expr expr <= expr expr >= expr
! j j j expr > expr expr j expr expr + term expr - term term
! j j term term * unary term / unary unary
! j j unary ! unary - unary factor
! j j factor ( bool ) loc num real true false
! j j j j j
