# 2 A Simple Syntax-Directed Translator

- [2.1 Introduction](2.1-Introduction.md)
- [2.2 Syntax Definition](2.2-Syntax-Definition.md)
- [2.3 Syntax-Directed Translation](2.3-Syntax-Directed-Translation.md)
- [2.4 Parsing](2.4-Parsing.md)
- [2.5 A Translator for Simple Expressions](2.5-A-Translator-for-Simple-Expressions.md)
- [2.6 Lexical Analysis](2.6-Lexical-Analysis.md)
- [2.7 Symbol Tables](2.7-Symbol-Tables.md)
- [2.8 Intermediate Code Generation](2.8-Intermediate-Code-Generation.md)
- [2.9 Summary of Chapter 2](2.9-Summary-of-Chapter-2.md)

## 章首内容

A Simple Syntax-Directed
Translator
This chapter is an introduction to the compiling techniques in Chapters 3 through 6 of this book. It illustrates the techniques by developing a working
Java program that translates representative programming language statements into three-address code, an intermediate representation. In this chapter, the emphasis is on the front end of a compiler, in particular on lexical analysis, parsing, and intermediate code generation. Chapters 7 and 8 show how to generate machine instructions from three-address code.
We start small by creating a syntax-directed translator that maps infix arithmetic expressions into postfix expressions. We then extend this translator to map code fragments as shown in Fig. 2.1 into three-address code of the form in Fig. 2.2.
The working Java translator appears in Appendix A. The use of Java is convenient, but not essential. In fact, the ideas in this chapter predate the creation of both Java and C.
int i; int j; float[100] a; float v; float x;
while ( true ) { do i = i+1; while ( a[i] < v );
do j = j-1; while ( a[j] > v );
if ( i >= j ) break;
x = a[i]; a[i] = a[j]; a[j] = x;
Figure 2.1: A code fragment to be translated
1: i = i + 1
2: t1 = a [ i ]
3: if t1 < v goto 1
4: j = j - 1
5: t2 = a [ j ]
6: if t2 > v goto 4
7: ifFalse i >= j goto 9
8: goto 14
9: x = a [ i ]
10: t3 = a [ j ]
11: a [ i ] = t3
12: a [ j ] = x
13: goto 1
Figure 2.2: Simplified intermediate code for the program fragment in Fig. 2.1
