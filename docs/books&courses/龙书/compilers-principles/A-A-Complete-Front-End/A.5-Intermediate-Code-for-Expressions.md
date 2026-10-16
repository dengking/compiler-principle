## A.5 Intermediate Code for Expressions

Package inter contains the Node class hierarchy. Node has two subclasses: Expr for expression nodes and Stmt for statement nodes. This section introduces
Expr and its subclasses. Some of the methods in Expr deal with booleans and jumping code; they will be discussed in Section A.6, along with the remaining subclasses of Expr.
Nodes in the syntax tree are implemented as objects of class Node. For error reporting, field lexline (line 4, file Node.java) saves the source-line number of the construct at this node. Lines 7-10 are used to emit three-address code.
1) package inter; // File Node.java
2) import lexer.*;
3) public class Node {
4) int lexline = 0;
5) Node() { lexline = Lexer.line; }
6) void error(String s) { throw new Error("near line "+lexline+": "+s); }
7) static int labels = 0;
8) public int newlabel() { return ++labels; }
9) public void emitlabel(int i) { System.out.print("L" + i + ":"); }
10) public void emit(String s) { System.out.println("\t" + s); }
Expression constructs are implemented by subclasses of Expr. Class Expr has fields op and type (lines 4-5, file Expr.java), representing the operator and type, respectively, at a node.
1) package inter; // File Expr.java
2) import lexer.*; import symbols.*;
3) public class Expr extends Node {
4) public Token op;
5) public Type type;
6) Expr(Token tok, Type p) { op = tok; type = p; }
Method gen (line 7) returns a “term” that can fit the right side of a threeaddress instruction. Given expression E = E1+E2, method gen returns a term x1+x2, where x1 and x2 are addresses for the values of E1 and E2, respectively.
The return value this is appropriate if this object is an address; subclasses of
Expr typically reimplement gen.
Method reduce (line 8) computes or “reduces” an expression down to a single address; that is, it returns a constant, an identifier, or a temporary name.
Given expression E, method reduce returns a temporary t holding the value of
E. Again, this is an appropriate return value if this object is an address.
We defer discussion of methods jumping and emitjumps (lines 9-18) until
Section A.6; they generate jumping code for boolean expressions.
7) public Expr gen() { return this; }
8) public Expr reduce() { return this; }
9) public void jumping(int t, int f) { emitjumps(toString(), t, f); }
10) public void emitjumps(String test, int t, int f) {
11) if( t != 0 && f != 0 ) {
12) emit("if " + test + " goto L" + t);
13) emit("goto L" + f);
15) else if( t != 0 ) emit("if " + test + " goto L" + t);
16) else if( f != 0 ) emit("iffalse " + test + " goto L" + f);
17) else ; // nothing since both t and f fall through
19) public String toString() { return op.toString(); }
Class Id inherits the default implementations of gen and reduce in class
Expr, since an identifier is an address.
1) package inter; // File Id.java
2) import lexer.*; import symbols.*;
3) public class Id extends Expr {
4) public int offset; // relative address
5) public Id(Word id, Type p, int b) { super(id, p); offset = b; }
The node for an identifier of class Id is a leaf. The call super(id,p) (line 5, file Id.java) saves id and p in inherited fields op and type, respectively. Field offset (line 4) holds the relative address of this identifier.
Class Op provides an implementation of reduce (lines 5-10, file Op.java) that is inherited by subclasses Arith for arithmetic operators, Unary for unary operators, and Access for array accesses. In each case, reduce calls gen to generate a term, emits an instruction to assign the term to a new temporary name, and returns the temporary.
1) package inter; // File Op.java
2) import lexer.*; import symbols.*;
3) public class Op extends Expr {
4) public Op(Token tok, Type p) { super(tok, p); }
5) public Expr reduce() {
6) Expr x = gen();
7) Temp t = new Temp(type);
8) emit( t.toString() + " = " + x.toString() );
9) return t;
Class Arith implements binary operators like + and *. Constructor Arith begins by calling super(tok,null) (line 6), where tok is a token representing the operator and null is a placeholder for the type. The type is determined on line 7 by using Type.max, which checks whether the two operands can be coerced to a common numeric type; the code for Type.max is in Section A.4.
If they can be coerced, type is set to the result type; otherwise, a type error is reported (line 8). This simple compiler checks types, but it does not insert type conversions.
1) package inter; // File Arith.java
2) import lexer.*; import symbols.*;
3) public class Arith extends Op {
4) public Expr expr1, expr2;
5) public Arith(Token tok, Expr x1, Expr x2) {
6) super(tok, null); expr1 = x1; expr2 = x2;
7) type = Type.max(expr1.type, expr2.type);
8) if (type == null ) error("type error");
10) public Expr gen() {
11) return new Arith(op, expr1.reduce(), expr2.reduce());
13) public String toString() {
14) return expr1.toString()+" "+op.toString()+" "+expr2.toString();
Method gen constructs the right side of a three-address instruction by reducing the subexpressions to addresses and applying the operator to the addresses
(line 11, file Arith.java). For example, suppose gen is called at the root for a+b*c. The calls to reduce return a as the address for subexpression a and a temporary t as the address for b*c. Meanwhile, reduce emits the instruction t=b*c. Method gen returns a new Arith node, with operator * and addresses a and t as operands.
It is worth noting that temporary names are typed, along with all other expressions. The constructor Temp is therefore called with a type as a parameter
(line 6, file Temp.java).
1) package inter; // File Temp.java
2) import lexer.*; import symbols.*;
3) public class Temp extends Expr {
1For error reporting, field lexline in class Node records the current lexical line number when a node is constructed. We leave it to the reader to track line numbers when new nodes are constructed during intermediate code generation.
2An alternative approach might be for the constructor to take an expression node as a parameter, so it can copy the type and lexical position of the expression node.
4) static int count = 0;
5) int number = 0;
6) public Temp(Type p) { super(Word.temp, p); number = ++count; }
7) public String toString() { return "t" + number; }
Class Unary is the one-operand counterpart of class Arith:
1) package inter; // File Unary.java
2) import lexer.*; import symbols.*;
3) public class Unary extends Op {
4) public Expr expr;
5) public Unary(Token tok, Expr x) { // handles minus, for ! see Not
6) super(tok, null); expr = x;
7) type = Type.max(Type.Int, expr.type);
8) if (type == null ) error("type error");
10) public Expr gen() { return new Unary(op, expr.reduce()); }
11) public String toString() { return op.toString()+" "+expr.toString(); }
