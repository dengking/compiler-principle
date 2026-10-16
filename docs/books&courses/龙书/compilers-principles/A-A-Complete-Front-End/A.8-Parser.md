## A.8 Parser

The parser reads a stream of tokens and builds a syntax tree by calling the appropriate constructor functions from Sections A.5-A.7. The current symbol table is maintained as in the translation scheme in Fig. 2.38 in Section 2.7.
Package parser contains one class, Parser:
1) package parser; // File Parser.java
2) import java.io.*; import lexer.*; import symbols.*; import inter.*;
3) public class Parser {
4) private Lexer lex; // lexical analyzer for this parser
5) private Token look; // lookahead token
6) Env top = null; // current or top symbol table
7) int used = 0; // storage used for declarations
8) public Parser(Lexer l) throws IOException { lex = l; move(); }
9) void move() throws IOException { look = lex.scan(); }
10) void error(String s) { throw new Error("near line "+lex.line+": "+s); }
11) void match(int t) throws IOException {
12) if( look.tag == t ) move();
13) else error("syntax error");
Like the simple expression translator in Section 2.5, class Parser has a procedure for each nonterminal. The procedures are based on a grammar formed by removing left recursion from the source-language grammar in Section A.1.
Parsing begins with a call to procedure program, which calls block() (line
16) to parse the input stream and build the syntax tree. Lines 17-18 generate intermediate code.
15) public void program() throws IOException { // program -> block
16) Stmt s = block();
17) int begin = s.newlabel(); int after = s.newlabel();
18) s.emitlabel(begin); s.gen(begin, after); s.emitlabel(after);
Symbol-table handling is shown explicitly in procedure block. Variable top (declared on line 5) holds the top symbol table; variable savedEnv (line 21) is a link to the previous symbol table.
20) Stmt block() throws IOException { // block -> { decls stmts }
21) match('{'); Env savedEnv = top; top = new Env(top);
22) decls(); Stmt s = stmts();
23) match('}'); top = savedEnv;
24) return s;
Declarations result in symbol-table entries for identifiers (see line 30). Although not shown here, declarations can also result in instructions to reserve storage for the identifiers at run time.
26) void decls() throws IOException {
27) while( look.tag == Tag.BASIC ) { // D -> type ID ;
28) Type p = type(); Token tok = look; match(Tag.ID); match(';');
29) Id id = new Id((Word)tok, p, used);
30) top.put( tok, id );
31) used = used + p.width;
34) Type type() throws IOException {
35) Type p = (Type)look; // expect look.tag == Tag.BASIC
3An attractive alternative is to add methods push and pop to class Env, with the current table accessible through a static variable Env.top.
36) match(Tag.BASIC);
37) if( look.tag != '[' ) return p; // T -> basic
38) else return dims(p); // return array type
40) Type dims(Type p) throws IOException {
41) match('['); Token tok = look; match(Tag.NUM); match(']');
42) if( look.tag == '[' )
43) p = dims(p);
44) return new Array(((Num)tok).value, p);
Procedure stmt has a switch statement with cases corresponding to the productions for nonterminal Stmt. Each case builds a node for a construct, using the constructor functions discussed in Section A.7. The nodes for while and do statements are constructed when the parser sees the opening keyword.
The nodes are constructed before the statement is parsed to allow any enclosed break statement to point back to its enclosing loop. Nested loops are handled by using variable Stmt.Enclosing in class Stmt and savedStmt (declared on line 52) to maintain the current enclosing loop.
46) Stmt stmts() throws IOException {
47) if ( look.tag == '}' ) return Stmt.Null;
48) else return new Seq(stmt(), stmts());
50) Stmt stmt() throws IOException {
51) Expr x; Stmt s, s1, s2;
52) Stmt savedStmt; // save enclosing loop for breaks
53) switch( look.tag ) {
54) case ';':
55) move();
56) return Stmt.Null;
57) case Tag.IF:
58) match(Tag.IF); match('('); x = bool(); match(')');
59) s1 = stmt();
60) if( look.tag != Tag.ELSE ) return new If(x, s1);
61) match(Tag.ELSE);
62) s2 = stmt();
63) return new Else(x, s1, s2);
64) case Tag.WHILE:
65) While whilenode = new While();
66) savedStmt = Stmt.Enclosing; Stmt.Enclosing = whilenode;
67) match(Tag.WHILE); match('('); x = bool(); match(')');
68) s1 = stmt();
69) whilenode.init(x, s1);
70) Stmt.Enclosing = savedStmt; // reset Stmt.Enclosing
71) return whilenode;
72) case Tag.DO:
73) Do donode = new Do();
74) savedStmt = Stmt.Enclosing; Stmt.Enclosing = donode;
75) match(Tag.DO);
76) s1 = stmt();
77) match(Tag.WHILE); match('('); x = bool(); match(')'); match(';');
78) donode.init(s1, x);
79) Stmt.Enclosing = savedStmt; // reset Stmt.Enclosing
80) return donode;
81) case Tag.BREAK:
82) match(Tag.BREAK); match(';');
83) return new Break();
84) case '{':
85) return block();
86) default:
87) return assign();
For convenience, the code for assignments appears in an auxiliary procedure, assign.
90) Stmt assign() throws IOException {
91) Stmt stmt; Token t = look;
92) match(Tag.ID);
93) Id id = top.get(t);
94) if( id == null ) error(t.toString() + " undeclared");
95) if( look.tag == '=' ) { // S -> id = E ;
96) move(); stmt = new Set(id, bool());
98) else { // S -> L = E ;
99) Access x = offset(id);
100) match('='); stmt = new SetElem(x, bool());
102) match(';');
103) return stmt;
The parsing of arithmetic and boolean expressions is similar. In each case, an appropriate syntax-tree node is created. Code generation for the two is different, as discussed in Sections A.5-A.6.
105) Expr bool() throws IOException {
106) Expr x = join();
107) while( look.tag == Tag.OR ) {
108) Token tok = look; move(); x = new Or(tok, x, join());
110) return x;
112) Expr join() throws IOException {
113) Expr x = equality();
114) while( look.tag == Tag.AND ) {
115) Token tok = look; move(); x = new And(tok, x, equality());
117) return x;
119) Expr equality() throws IOException {
120) Expr x = rel();
121) while( look.tag == Tag.EQ || look.tag == Tag.NE ) {
122) Token tok = look; move(); x = new Rel(tok, x, rel());
124) return x;
126) Expr rel() throws IOException {
127) Expr x = expr();
128) switch( look.tag ) {
129) case '<': case Tag.LE: case Tag.GE: case '>':
130) Token tok = look; move(); return new Rel(tok, x, expr());
131) default:
132) return x;
135) Expr expr() throws IOException {
136) Expr x = term();
137) while( look.tag == '+' || look.tag == '-' ) {
138) Token tok = look; move(); x = new Arith(tok, x, term());
140) return x;
142) Expr term() throws IOException {
143) Expr x = unary();
144) while(look.tag == '*' || look.tag == '/' ) {
145) Token tok = look; move(); x = new Arith(tok, x, unary());
147) return x;
149) Expr unary() throws IOException {
150) if( look.tag == '-' ) {
151) move(); return new Unary(Word.minus, unary());
153) else if( look.tag == '!' ) {
154) Token tok = look; move(); return new Not(tok, unary());
156) else return factor();
The rest of the code in the parser deals with \factors" in expressions. The auxiliary procedure offset generates code for array address calculations, as discussed in Section 6.4.3.
158) Expr factor() throws IOException {
159) Expr x = null;
160) switch( look.tag ) {
161) case '(':
162) move(); x = bool(); match(')');
163) return x;
164) case Tag.NUM:
165) x = new Constant(look, Type.Int); move(); return x;
166) case Tag.REAL:
167) x = new Constant(look, Type.Float); move(); return x;
168) case Tag.TRUE:
169) x = Constant.True; move(); return x;
170) case Tag.FALSE:
171) x = Constant.False; move(); return x;
172) default:
173) error("syntax error");
174) return x;
175) case Tag.ID:
176) String s = look.toString();
177) Id id = top.get(look);
178) if( id == null ) error(look.toString() + " undeclared");
179) move();
180) if( look.tag != '[' ) return id;
181) else return offset(id);
184) Access offset(Id a) throws IOException { // I -> [E] | [E] I
185) Expr i; Expr w; Expr t1, t2; Expr loc; // inherit id
186) Type type = a.type;
187) match('['); i = bool(); match(']'); // first index, I -> [ E ]
188) type = ((Array)type).of;
189) w = new Constant(type.width);
190) t1 = new Arith(new Token('*'), i, w);
191) loc = t1;
192) while( look.tag == '[' ) { // multi-dimensional I -> [ E ] I
193) match('['); i = bool(); match(']');
194) type = ((Array)type).of;
195) w = new Constant(type.width);
196) t1 = new Arith(new Token('*'), i, w);
197) t2 = new Arith(new Token('+'), loc, t1);
198) loc = t2;
200) return new Access(a, loc, type);
