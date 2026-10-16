## A.2 Main

Execution begins in method main in class Main. Method main creates a lexical analyzer and a parser and then calls method program in the parser:
1) package main; // File Main.java
2) import java.io.*; import lexer.*; import parser.*;
3) public class Main {
4) public static void main(String[] args) throws IOException {
5) Lexer lex = new Lexer();
6) Parser parse = new Parser(lex);
7) parse.program();
8) System.out.write('\n');
