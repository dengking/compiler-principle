## A.9 Creating the Front End

The code for the packages appears in five directories: main, lexer, symbol, parser, and inter. The commands for creating the compiler vary from system to system. The following are from a UNIX implementation:
javac lexer/*.java javac symbols/*.java javac inter/*.java javac parser/*.java javac main/*.java
The javac command creates .class files for each class. The translator can then be exercised by typing java main.Main followed by the source program to be translated; e.g., the contents of file test
1) { // File test
2) int i; int j; float v; float x; float[100] a;
3) while( true ) {
4) do i = i+1; while( a[i] < v);
5) do j = j-1; while( a[j] > v);
6) if( i >= j ) break;
7) x = a[i]; a[i] = a[j]; a[j] = x;
On this input, the front end produces
1) L1:L3: i = i + 1
2) L5: t1 = i * 8
3) t2 = a [ t1 ]
4) if t2 < v goto L3
5) L4: j = j - 1
6) L7: t3 = j * 8
7) t4 = a [ t3 ]
8) if t4 > v goto L4
9) L6: iffalse i >= j goto L8
10) L9: goto L2
11) L8: t5 = i * 8
12) x = a [ t5 ]
13) L10: t6 = i * 8
14) t7 = j * 8
15) t8 = a [ t7 ]
16) a [ t6 ] = t8
17) L11: t9 = j * 8
18) a [ t9 ] = x
19) goto L1
20) L2:
Try it.
This page intentionally left blank
