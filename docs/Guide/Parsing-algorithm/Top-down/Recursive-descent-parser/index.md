# Recursive descent parser



## wikipedia [Recursive descent parser](https://en.wikipedia.org/wiki/Recursive_descent_parser)



## code

**LeetCode**:

https://leetcode.com/problems/basic-calculator-ii/solutions/63140/recursive-descent-parser-in-c/

https://leetcode.com/problems/basic-calculator/solutions/685876/c-recursive-descent-parser/

https://leetcode.com/problems/basic-calculator/solutions/1464026/c-recursive-descent-parser/







prgwonders.blogspot [Recursive Descent Parser in C++ for a sample grammar](https://prgwonders.blogspot.com/2017/10/recursive-descent-parser-in-c-for.html)

stackoverflow [Recursive Descent Parser](https://stackoverflow.com/questions/8767965/recursive-descent-parser)

github [yildizan/recursive-descent-parser](https://github.com/yildizan/recursive-descent-parser)



### geeksforgeeks [Recursive Descent Parser](https://www.geeksforgeeks.org/recursive-descent-parser/)



|               Before removing left recursion               |                After removing left recursion                 |
| :--------------------------------------------------------: | :----------------------------------------------------------: |
| E –> E + T \| T<br>  T –> T * F \| F<br>  F –> ( E ) \| id | E –> T E’<br>  E’ –> + T E’ \| e<br>  T –> F T’<br>  T’ –> * F T’ \| e<br>  F –> ( E ) \| id |

Here `e` is Epsilon

For **Recursive Descent Parser**, we are going to write one program for every variable. 

