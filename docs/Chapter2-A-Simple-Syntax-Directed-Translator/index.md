[TOC]



# Introduction

This chapter is an introduction to the compiling techniques in Chapters 3 through 6 of this book. It illustrates the techniques by developing a working Java program that translates representative programming language statements into [three-address code](https://en.wikipedia.org/wiki/Three-address_code), an intermediate representation. 

We start small by creating a syntax-directed translator that maps infix arithmetic expressions into postfix expressions. We then extend this translator to map code fragments as shown in Fig. 2.1 into three-address code of the form in Fig. 2.2.

> TIPS: It is not easy to implement mapping infix arithmetic expressions into postfix expressions, there are some algorithms
>
> - [Shunting-yard algorithm](https://en.wikipedia.org/wiki/Shunting-yard_algorithm)


```java
{
    int i; int j; float[100] a; float v; float x;
    while ( true ) {
        do i = i+1; while ( a[i] < v );
        do j = j-1; while ( a[j] > v );
        if ( i >= j ) break;
        x = a[i]; a[i] = a[j]; a[j] = x;
    }
}
```


Figure 2.1: A code fragment to be translated









|      |                         |
| :--: | :---------------------: |
|  1:  |       `i = i + 1`       |
|  2:  |     `t1 = a [ i ]`      |
|  3:  |   `if t1 < v goto 1`    |
|  4:  |       `j = j - 1`       |
|  5:  |     `t2 = a [ j ]`      |
|  6:  |   `if t2 > v goto 4`    |
|  7:  | `ifFalse i >= j goto 9` |
|  8:  |        `goto 14`        |
|  9:  |      `x = a [ i ]`      |
| 10:  |     `t3 = a [ j ]`      |
| 11:  |     `a [ i ] = t3`      |
| 12:  |      `a [ j ] = x`      |
| 13:  |        `goto 1`         |
| 14:  |                         |

Figure 2.2: Simplified intermediate code for the program fragment in Fig. 2.1