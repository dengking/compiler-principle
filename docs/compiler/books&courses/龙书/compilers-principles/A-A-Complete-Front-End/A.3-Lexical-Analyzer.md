## A.3 Lexical Analyzer

Package lexer is an extension of the code for the lexical analyzer in Section 2.6.5. Class Tag defines constants for tokens:
1) package lexer; // File Tag.java
2) public class Tag {
3) public final static int
4) AND = 256, BASIC = 257, BREAK = 258, DO = 259, ELSE = 260,
5) EQ = 261, FALSE = 262, GE = 263, ID = 264, IF = 265,
6) INDEX = 266, LE = 267, MINUS = 268, NE = 269, NUM = 270,
7) OR = 271, REAL = 272, TEMP = 273, TRUE = 274, WHILE = 275;
Three of the constants, INDEX, MINUS, and TEMP, are not lexical tokens; they will be used in syntax trees.
Classes Token and Num are as in Section 2.6.5, with method toString added:
1) package lexer; // File Token.java
2) public class Token {
3) public final int tag;
4) public Token(int t) { tag = t; }
5) public String toString() {return "" + (char)tag;}
1) package lexer; // File Num.java
2) public class Num extends Token {
3) public final int value;
4) public Num(int v) { super(Tag.NUM); value = v; }
5) public String toString() { return "" + value; }
Class Word manages lexemes for reserved words, identifiers, and composite tokens like &&. It is also useful for managing the written form of operators in the intermediate code like unary minus; for example, the source text -2 has the intermediate form minus 2.
1) package lexer; // File Word.java
2) public class Word extends Token {
3) public String lexeme = "";
4) public Word(String s, int tag) { super(tag); lexeme = s; }
5) public String toString() { return lexeme; }
6) public static final Word
7) and = new Word( "&&", Tag.AND ), or = new Word( "||", Tag.OR ),
8) eq = new Word( "==", Tag.EQ ), ne = new Word( "!=", Tag.NE ),
9) le = new Word( "<=", Tag.LE ), ge = new Word( ">=", Tag.GE ),
10) minus = new Word( "minus", Tag.MINUS ),
11) True = new Word( "true", Tag.TRUE ),
12) False = new Word( "false", Tag.FALSE ),
13) temp = new Word( "t", Tag.TEMP );
Class Real is for floating point numbers:
1) package lexer; // File Real.java
2) public class Real extends Token {
3) public final float value;
4) public Real(float v) { super(Tag.REAL); value = v; }
5) public String toString() { return "" + value; }
The main method in class Lexer, function scan, recognizes numbers, identifiers, and reserved words, as discussed in Section 2.6.5.
Lines 9-13 in class Lexer reserve selected keywords. Lines 14-16 reserve lexemes for objects defined elsewhere. Objects Word.True and Word.False are defined in class Word. Objects for the basic types int, char, bool, and float are defined in class Type, a subclass of Word. Class Type is from package symbols.
1) package lexer; // File Lexer.java
2) import java.io.*; import java.util.*; import symbols.*;
3) public class Lexer {
4) public static int line = 1;
5) char peek = ' ';
6) Hashtable words = new Hashtable();
7) void reserve(Word w) { words.put(w.lexeme, w); }
8) public Lexer() {
9) reserve( new Word("if", Tag.IF) );
10) reserve( new Word("else", Tag.ELSE) );
11) reserve( new Word("while", Tag.WHILE) );
12) reserve( new Word("do", Tag.DO) );
13) reserve( new Word("break", Tag.BREAK) );
14) reserve( Word.True ); reserve( Word.False );
15) reserve( Type.Int ); reserve( Type.Char );
16) reserve( Type.Bool ); reserve( Type.Float );
Function readch() (line 18) is used to read the next input character into variable peek. The name readch is reused or overloaded (lines 19-24) to help recognize composite tokens. For example, once input < is seen, the call readch('=') reads the next character into peek and checks whether it is =.
18) void readch() throws IOException { peek = (char)System.in.read(); }
19) boolean readch(char c) throws IOException {
20) readch();
21) if( peek != c ) return false;
22) peek = ' ';
23) return true;
Function scan begins by skipping white space (lines 26-30). It recognizes composite tokens like <= (lines 31-44) and numbers like 365 and 3.14 (lines
45-58), before collecting words (lines 59-70).
25) public Token scan() throws IOException {
26) for( ; ; readch() ) {
27) if( peek == ' ' || peek == '\t' ) continue;
28) else if( peek == '\n' ) line = line + 1;
29) else break;
31) switch( peek ) {
32) case '&':
33) if( readch('&') ) return Word.and; else return new Token('&');
34) case '|':
35) if( readch('|') ) return Word.or; else return new Token('|');
36) case '=':
37) if( readch('=') ) return Word.eq; else return new Token('=');
38) case '!':
39) if( readch('=') ) return Word.ne; else return new Token('!');
40) case '<':
41) if( readch('=') ) return Word.le; else return new Token('<');
42) case '>':
43) if( readch('=') ) return Word.ge; else return new Token('>');
45) if( Character.isDigit(peek) ) {
46) int v = 0;
47) do {
48) v = 10*v + Character.digit(peek, 10); readch();
49) } while( Character.isDigit(peek) );
50) if( peek != '.' ) return new Num(v);
51) float x = v; float d = 10;
52) for(;;) {
53) readch();
54) if( ! Character.isDigit(peek) ) break;
55) x = x + Character.digit(peek, 10) / d; d = d*10;
57) return new Real(x);
59) if( Character.isLetter(peek) ) {
60) StringBuffer b = new StringBuffer();
61) do {
62) b.append(peek); readch();
63) } while( Character.isLetterOrDigit(peek) );
64) String s = b.toString();
65) Word w = (Word)words.get(s);
66) if( w != null ) return w;
67) w = new Word(s, Tag.ID);
68) words.put(s, w);
69) return w;
Finally, any remaining characters are returned as tokens (lines 71-72).
71) Token tok = new Token(peek); peek = ' ';
72) return tok;
