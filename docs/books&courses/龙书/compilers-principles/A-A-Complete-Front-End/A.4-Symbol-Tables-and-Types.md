## A.4 Symbol Tables and Types

Package symbols implements symbol tables and types.
Class Env is essentially unchanged from Fig. 2.37. Whereas class Lexer maps strings to words, class Env maps word tokens to objects of class Id, which is defined in package inter along with the classes for expressions and statements.
1) package symbols; // File Env.java
2) import java.util.*; import lexer.*; import inter.*;
3) public class Env {
4) private Hashtable table;
5) protected Env prev;
6) public Env(Env n) { table = new Hashtable(); prev = n; }
7) public void put(Token w, Id i) { table.put(w, i); }
8) public Id get(Token w) {
9) for( Env e = this; e != null; e = e.prev ) {
10) Id found = (Id)(e.table.get(w));
11) if( found != null ) return found;
13) return null;
We define class Type to be a subclass of Word since basic type names like int are simply reserved words, to be mapped from lexemes to appropriate objects by the lexical analyzer. The objects for the basic types are Type.Int, Type.Float,
Type.Char, and Type.Bool (lines 7-10). All of them have inherited field tag set to Tag.BASIC, so the parser treats them all alike.
1) package symbols; // File Type.java
2) import lexer.*;
3) public class Type extends Word {
4) public int width = 0; // width is used for storage allocation
5) public Type(String s, int tag, int w) { super(s, tag); width = w; }
6) public static final Type
7) Int = new Type( "int", Tag.BASIC, 4 ),
8) Float = new Type( "float", Tag.BASIC, 8 ),
9) Char = new Type( "char", Tag.BASIC, 1 ),
10) Bool = new Type( "bool", Tag.BASIC, 1 );
Functions numeric (lines 11-14) and max (lines 15-20) are useful for type conversions.
11) public static boolean numeric(Type p) {
12) if (p == Type.Char || p == Type.Int || p == Type.Float) return true;
13) else return false;
15) public static Type max(Type p1, Type p2) {
16) if ( ! numeric(p1) || ! numeric(p2) ) return null;
17) else if ( p1 == Type.Float || p2 == Type.Float ) return Type.Float;
18) else if ( p1 == Type.Int || p2 == Type.Int ) return Type.Int;
19) else return Type.Char;
Conversions are allowed between the \numeric" types Type.Char, Type.Int, and Type.Float. When an arithmetic operator is applied to two numeric types, the result has the \max" of the two types.
Arrays are the only constructed type in the source language. The call to super on line 7 sets field width, which is essential for address calculations. It also sets lexeme and tok to default values that are not used.
1) package symbols; // File Array.java
2) import lexer.*;
3) public class Array extends Type {
4) public Type of; // array *of* type
5) public int size = 1; // number of elements
6) public Array(int sz, Type p) {
7) super("[]", Tag.INDEX, sz*p.width); size = sz; of = p;
9) public String toString() { return "[" + size + "] " + of.toString(); }
