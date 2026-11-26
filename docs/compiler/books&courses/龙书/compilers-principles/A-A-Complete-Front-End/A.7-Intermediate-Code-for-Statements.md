## A.7 Intermediate Code for Statements

Each statement construct is implemented by a subclass of Stmt. The fields for the components of a construct are in the relevant subclass; for example, class
While has fields for a test expression and a substatement, as we shall see.
Lines 3-4 in the following code for class Stmt deal with syntax-tree construction. The constructor Stmt() does nothing, since the work is done in the subclasses. The static object Stmt.Null (line 4) represents an empty sequence of statements.
1) package inter; // File Stmt.java
2) public class Stmt extends Node {
3) public Stmt() { }
4) public static Stmt Null = new Stmt();
5) public void gen(int b, int a) {} // called with labels begin and after
6) int after = 0; // saves label after
7) public static Stmt Enclosing = Stmt.Null; // used for break stmts
Lines 5-7 deal with the generation of three-address code. The method gen is called with two labels b and a, where b marks the beginning of the code for this statement and a marks the first instruction after the code for this statement.
Method gen (line 5) is a placeholder for the gen methods in the subclasses.
The subclasses While and Do save their label a in the field after (line 6) so it can be used by any enclosed break statement to jump out of its enclosing construct. The object Stmt.Enclosing is used during parsing to keep track of the enclosing construct. (For a source language with continue statements, we can use the same approach to keep track of the enclosing construct for a continue statement.)
The constructor for class If builds a node for a statement if (E) S. Fields expr and stmt hold the nodes for E and S, respectively. Note that expr in lower-case letters names a field of class Expr; similarly, stmt names a field of class Stmt.
1) package inter; // File If.java
2) import symbols.*;
3) public class If extends Stmt {
4) Expr expr; Stmt stmt;
5) public If(Expr x, Stmt s) {
6) expr = x; stmt = s;
7) if( expr.type != Type.Bool ) expr.error("boolean required in if");
9) public void gen(int b, int a) {
10) int label = newlabel(); // label for the code for stmt
11) expr.jumping(0, a); // fall through on true, goto a on false
12) emitlabel(label); stmt.gen(label, a);
The code for an If object consists of jumping code for expr followed by the code for stmt. As discussed in Section A.6, the call expr.jumping(0,a) on line
11 specifies that control must fall through the code for expr if expr evaluates to true, and must flow to label a otherwise.
The implementation of class Else, which handles conditionals with else parts, is analogous to that of class If:
1) package inter; // File Else.java
2) import symbols.*;
3) public class Else extends Stmt {
4) Expr expr; Stmt stmt1, stmt2;
5) public Else(Expr x, Stmt s1, Stmt s2) {
6) expr = x; stmt1 = s1; stmt2 = s2;
7) if( expr.type != Type.Bool ) expr.error("boolean required in if");
9) public void gen(int b, int a) {
10) int label1 = newlabel(); // label1 for stmt1
11) int label2 = newlabel(); // label2 for stmt2
12) expr.jumping(0,label2); // fall through to stmt1 on true
13) emitlabel(label1); stmt1.gen(label1, a); emit("goto L" + a);
14) emitlabel(label2); stmt2.gen(label2, a);
The construction of a While object is split between the constructor While(), which creates a node with null children (line 5), and an initialization function init(x,s), which sets child expr to x and child stmt to s (lines 6{9). Function gen(b,a) for generating three-address code (lines 10{16) is in the spirit of the corresponding function gen() in class If. The difference is that label a is saved in field after (line 11) and that the code for stmt is followed by a jump to b
(line 15) for the next iteration of the while loop.
1) package inter; // File While.java
2) import symbols.*;
3) public class While extends Stmt {
4) Expr expr; Stmt stmt;
5) public While() { expr = null; stmt = null; }
6) public void init(Expr x, Stmt s) {
7) expr = x; stmt = s;
8) if( expr.type != Type.Bool ) expr.error("boolean required in while");
10) public void gen(int b, int a) {
11) after = a; // save label a
12) expr.jumping(0, a);
13) int label = newlabel(); // label for stmt
14) emitlabel(label); stmt.gen(label, b);
15) emit("goto L" + b);
Class Do is very similar to class While.
1) package inter; // File Do.java
2) import symbols.*;
3) public class Do extends Stmt {
4) Expr expr; Stmt stmt;
5) public Do() { expr = null; stmt = null; }
6) public void init(Stmt s, Expr x) {
7) expr = x; stmt = s;
8) if( expr.type != Type.Bool ) expr.error("boolean required in do");
10) public void gen(int b, int a) {
11) after = a;
12) int label = newlabel(); // label for expr
13) stmt.gen(b,label);
14) emitlabel(label);
15) expr.jumping(b,0);
Class Set implements assignments with an identifier on the left side and an expression on the right. Most of the code in class Set is for constructing a node and checking types (lines 5-13). Function gen emits a three-address instruction
(lines 14-16).
1) package inter; // File Set.java
2) import lexer.*; import symbols.*;
3) public class Set extends Stmt {
4) public Id id; public Expr expr;
5) public Set(Id i, Expr x) {
6) id = i; expr = x;
7) if ( check(id.type, expr.type) == null ) error("type error");
9) public Type check(Type p1, Type p2) {
10) if ( Type.numeric(p1) && Type.numeric(p2) ) return p2;
11) else if ( p1 == Type.Bool && p2 == Type.Bool ) return p2;
12) else return null;
14) public void gen(int b, int a) {
15) emit( id.toString() + " = " + expr.gen().toString() );
Class SetElem implements assignments to an array element:
1) package inter; // File SetElem.java
2) import lexer.*; import symbols.*;
3) public class SetElem extends Stmt {
4) public Id array; public Expr index; public Expr expr;
5) public SetElem(Access x, Expr y) {
6) array = x.array; index = x.index; expr = y;
7) if ( check(x.type, expr.type) == null ) error("type error");
9) public Type check(Type p1, Type p2) {
10) if ( p1 instanceof Array || p2 instanceof Array ) return null;
11) else if ( p1 == p2 ) return p2;
12) else if ( Type.numeric(p1) && Type.numeric(p2) ) return p2;
13) else return null;
15) public void gen(int b, int a) {
16) String s1 = index.reduce().toString();
17) String s2 = expr.reduce().toString();
18) emit(array.toString() + " [ " + s1 + " ] = " + s2);
Class Seq implements a sequence of statements. The tests for null statements on lines 6-7 are for avoiding labels. Note that no code is generated for the null statement, Stmt.Null, since method gen in class Stmt does nothing.
1) package inter; // File Seq.java
2) public class Seq extends Stmt {
3) Stmt stmt1; Stmt stmt2;
4) public Seq(Stmt s1, Stmt s2) { stmt1 = s1; stmt2 = s2; }
5) public void gen(int b, int a) {
6) if ( stmt1 == Stmt.Null ) stmt2.gen(b, a);
7) else if ( stmt2 == Stmt.Null ) stmt1.gen(b, a);
8) else {
9) int label = newlabel();
10) stmt1.gen(b,label);
11) emitlabel(label);
12) stmt2.gen(label,a);
A break statement sends control out of an enclosing loop or switch statement. Class Break uses field stmt to save the enclosing statement construct
(the parser ensures that Stmt.Enclosing denotes the syntax-tree node for the enclosing construct). The code for a Break object is a jump to the label stmt.after, which marks the instruction immediately after the code for stmt.
1) package inter; // File Break.java
2) public class Break extends Stmt {
3) Stmt stmt;
4) public Break() {
5) if( Stmt.Enclosing == Stmt.Null ) error("unenclosed break");
6) stmt = Stmt.Enclosing;
8) public void gen(int b, int a) {
9) emit( "goto L" + stmt.after);
