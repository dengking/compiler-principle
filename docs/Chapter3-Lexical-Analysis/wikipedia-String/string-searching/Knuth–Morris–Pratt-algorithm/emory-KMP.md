[TOC]

# [Computing the KMP failure function (f(k))](http://www.mathcs.emory.edu/~cheung/Courses/323/Syllabus/Text/Matching-KMP2.html)

# definition of `f(k)`

```
   f(k) = MaxOverlap ( "p0 p1 ... pk" )

   where:

      "p0 p1 ... pk" = the prefix of length k+1 of pattern P
```

**Graphically:**

![img](http://www.mathcs.emory.edu/~cheung/Courses/323/Syllabus/Text/FIGS/KMP/KMP22.gif)



## Naive way to find ***f(k)***:

```
   Given P = "p0 p1 ... pm-1"

   Given k = 1, 2, ..., m-1   (k = 0 ==> f(0) = 0)

         1. Extract the sub-pattern:   "p0 p1 ... pk"

         2. Find the first (= largest) overlap:

             Try: (p0) p1 p2 ... pk-1
                       p0 p1 ... pk-1 pk

            If (no match)
             Try: (p0) p1 p2 ... pk-1
                          p0 p1 ... pk-1 pk

            And so on... The first overlap is the longest ! 
```



> NOTE: 上述算法是一个循环算法，即`for k in range(1, m)`，下面是上述算法的python实现：
>
> ```python
> def build_failure_table(p):
>     """
>     构建字符串p的最长公共前缀后缀数组
>     :param p:
>     :return:
>     """
>     failure_table = list()
>     len_of_p = len(p)
>     for len_of_sub_str in range(1, len_of_p + 1):
>         max_len_of_overlap = int(len_of_sub_str / 2)  # 最大重叠前缀后缀的长度
>         print("子串长度:{},最大重叠前缀后缀长度:{}".format(len_of_sub_str, max_len_of_overlap))
>         if max_len_of_overlap == 0:
>             # 长度为1的串，是没有重叠前缀后缀的
>             failure_table.append(0)
>         else:
>             found = False  # 是否找到重叠前缀后缀
>             for len_of_overlap in range(max_len_of_overlap, 0, -1):
>                 print("重叠前缀后缀长度:{}".format(len_of_overlap))
>                 # len_of_overlap 重叠前缀后缀的长度
>                 for prefix_index in range(len_of_overlap):
>                     suffix_index = prefix_index + (len_of_sub_str - len_of_overlap)
>                     print("前缀起始位置:{},后缀起始位置:{}".format(prefix_index, suffix_index))
>                     if p[prefix_index] == p[suffix_index]:
>                         if suffix_index == len_of_sub_str - 1:
>                             # 找到了重叠部分
>                             failure_table.append(len_of_overlap)
>                             found = True
>                             break
>                     else:
>                         break
>                 if found:
>                     break
>             if not found:
>                 failure_table.append(0)
>     return failure_table
> ```



## Relating `f(k)` to `f(k−1)`

The values `f(k)` are computed easily using **existing prefix overlap information**:

- `f(0) = 0` (`f(0)` is always 0)
- `f(1)` is computing using (already computed) value `f(0)`
- `f(2)` is computing using (already computed) value `f(0)`, `f(1)`
- `f(3)` is computing using (already computed) value `f(0)`, `f(1)`, `f(2)`
  And so on



According to the definition of f(k):

![img](http://www.mathcs.emory.edu/~cheung/Courses/323/Syllabus/Text/FIGS/KMP/KMP23.gif)

> NOTE: 上面这种表示问题的方式是比较容易理解的，即在原问题的基础上添加一个新元素从而构成了一个规模更大的问题。

Suppose that we know that: `f(k−1) = x`

In other words: the **longest overlapping suffix and prefix** in "`p0 p1 ... pk-1`" has `x` characters:

```
                     f(k-1) = x characters               
                  <----------------------->
      p1 p2 p3 ... pk-x-2 pk-x-3 pk-x-4 .... pk-1 
                       ^     ^     ^         ^
                       |     |     |  equal  |
                       v     v     v         v
                       p0    p1    p2 ....    px-1   px ... pk-1 
```

**question:**

Can we use the fact that f(k−1) = x to compute f(k) ?

**answer:**

Yes, because f(k) is computed using a similar prefix as f(k−1):

```
    prefix used to compute f(k-1)
  +--------------------------------+
  |                                |
   p0   p1   p2 ....    px-1 ... pk-1  pk    
  |                                    |
  +------------------------------------+
      prefix used to compute f(k)
```

We will next learn how to exploit the similarity to compute f(k)

### Fact between `f(k)` and `f(k−1)`

**Fact:** f(k)   ≤   f(k−1) + 1

### Computation trick 1

Let use denote: `f(k−1) = x`

(Note: **`f(k−1)`** is **equal** to *some* value. The **above assumption** simply gave a more convenient ***notation*** for this value).

If `px == pk`, then:

```
   f(k) = x+1 

   (i.e., the maximum overlap of the prefix

                 p0   p1   p2 .... pk-1  pk    

     has x+1 characters 
```

**Proof:**

```

                   These x+1 characters match IF pk == px!               
                  <---------------------------->
      p1 p2 p3 ... pk-x-2 pk-x-3 pk-x-4 .... pk-1   pk
                   ^     ^     ^         ^     ^
                   |     |     |  equal  |     |equal
                   v     v     v         v     v
                   p0    p1    p2 .... 		 px-1   px ... pk-1  pk     
                  |                          |
	          +--------------------------+
                   These characters matches
		   because f(k-1) = x
```



### Prelude to computation trick 2

Consider the prefix `ababyabab` where f(8) = 4:

```

             012345678
    prefix = ababyabab

    f(8) = 4

    because:
               ababyabab
                    ababyabab                
                    <-->
                  4 characters overlap
```

We want to compute f(9) using f(8) , but now the next character does not match(that is the next char is not equal to y):



```
             0123456789
    prefix = ababyababa

             ababyababa
		  ababyababa  

    Conclusion:

       *** We CANNOT use f(8) to compute f(9) ***  
```

**question:**

- What should we try next to find the maximum overlap for the prefix "ababyababa"



**answer:**

To find the maximum overlap, we must slide the prefix down and look for matching letters !!!

> NOTE: 思路是使用已经匹配的字符串来尽可能减少匹配次数并且寻找第一个最可能的位置？

Now, let us use only the matching prefix information:

```
      ababyababa
           ababyababa  


 Look only at these characters:               

      ?????abab?
           abab??????
```

We can know for sure that the overlap cannot be found starting at these positions:

```

      ?????abab?
            abab??????   
```

> NOTE: 因为我们知道串`abab`的最长公共前缀后缀的长度是2，即`f(3)`，所以它的前两个元素可以匹配上的，所以第一个可能位置是如下图所示的，这就是对已经匹配信息的充分运用。至于第三个元素是否能够匹配上，就要比较的结果了。

The first possible way that overlap can be found is starting here:

```

      ?????abab?
             abab??????   
```

In other words: we can compute `f(9)` using `f(3)` :

```
             0123
    prefix = abab

             abab
	       abab         

    f(3) = 2
```

Notice that: 3 = 4−1 and f(8) = 4

Worked out further:

```
             0123456789
    prefix = ababyababa

             ababyababa
		    		ababyababa  
                      ^
		      		  |
          compare the character at position 2 (f(3) = 2)     

    Note:

       The prefix abab is hightlighted in yellow 
```

Because the characters are equal, we have found the maximum overlap:

```

     f(9) = f(3) + 1 
          =  2   + 1 
	  =  3           !!!  
```

> NOTE:  这里可以假设，如果`p[3]`和`p[9]`并不相等，则上述流程需要继续下去，至于终止条件，显然是直至比较到第一个元素都不相等。

### Computation trick #2

Let: f(k−1) = x

(Note: **`f(k−1)`** is **equal** to *some* value. The **above assumption** simply gave a more convenient ***notation*** for this value).

If `px ≠ pk`, then:

The next prefix that can be used to compute f(k) is:

```
p0 p1 .... px-1
```

In pseudo code:

```
    i = k-1;       // Try to use f(k-1) to compute f(k)
    x = f(i);	   // x = character position to match against pk    

    if  ( P[k] == P[x] )  then     

        f(k) = f(x−1) + 1

    else

        Use:  p0 p1 .... px-1 to compute f(k)

        What that means in terms of program statements:

	   i = x-1;    // Try to use f(x-1) to compute f(k) 
	   x = f(i);   // x = character position to match against pk
```

**Note:** We must repeat trick #2 as long as i ≥ 0, In other words: use a `while` loop instead of an `if` statement !





## Algorithm to compute KMP failure function

**Pseudo code:**

```pseudocode
   public static int[] KMP_failure_function( P )
   {
      int k, i, x, m;

      int f[] = new int[P.length()];    // f[] stores the function values

      m = P.length();

      f[0] = 0;                 // f[0] is always 0...

      for ( k = 1; k < m; k++ )
      {
         // Compute f(k) and store in f[k]

	 i = k-1;               // Try use f(k-1) to compute f(k)
	 x = f[i];		// Character position to match agains P[k]

	 if ( P[k] == P[x] )    // Note: make sure x is valid
         {
	    f[k] = f[i] + 1;
	    continue;           // Compute next f(k) value
	 }
	 else
	 {
	    i = x-1;            // Try next prefix (and next f(i)) to compute f(k)
	    x = f[i];		// Character position to match agains P[k]
	 }

	 if ( P[k] == P[x] )    // Note: make sure x is valid
         {
	    f[k] = f[i] + 1;
	    continue;           // Compute next f(k) value
	 }
	 else
	 {
	    i = x-1;            // Try next prefix (and next f(i)) to compute f(k)
	    x = f[i];		// Character position to match agains P[k]
	 }

	 .... (obviously we will make this into a loop !!!)

      }
   }
```

**Java code:**

```java
   public static int[] KMP_failure_function(String P)
   {
      int k, i, x, m;
      int f[] = new int[P.length()];

      m = P.length();

      f[0] = 0;            // f(0) is always 0

      for ( k = 1; k < m; k++ )
      {
         // Compute f[k]

         i = k-1;           // First try to use f(k-1) to compute f(k)
         x = f[i];

         while ( P.charAt(x) != P.charAt(k) )
         {
            i = x-1;        // Try the next candidate f(.) to compute f(k)     

            if ( i < 0 )    // Make sure x is valid
               break;       // STOP the search !!!

            x = f[i];
         }


         if ( i < 0  )
            f[k] = 0;          // No overlap at all: max overlap = 0 characters
         else
            f[k] = f[i] + 1;   // We can compute f(k) using f(i)
      }

      return(f);
   }
```



完整测试程序

```java
/* ----------------------------------
   My own KMP Failure function alg

     S.Y. Cheung - 3/3/2013
   ---------------------------------- */

import java.util.*;

public class ComputeF
{
   public static int[] KMP_failure_function(String P)
   {
      int k, i, x, m;
      int f[] = new int[P.length()];

      String s;
   
      m = P.length();
   
      f[0] = 0;

      for ( k = 1; k < m; k++ )
      {
         // Compute f[k]

         s = P.substring(0,k+1);
         System.out.println("-----------------------------------------------");
         System.out.println("Prefix = " + s + " --- Computing f("+k+"):");

         i = k-1;           // First try to use f(k-1) to compute f(k)
         x = f[i];
   
         System.out.println("===================================");
         System.out.println("Try using: f(" + i + ") = " + x );
         printState(s, s, k, x);

         while ( P.charAt(x) != P.charAt(k) )
         {
	    i = f[i]-1;     // Try the next candidate f(.) to compute f(k)

	    if ( i < 0 )    // Search ended in failure....
	       break;

            x = f[i];

            System.out.println("===================================");
            System.out.println("Try using: f(" + i + ") = " + x );
            printState(s, s, k, x);
         }

         if ( i < 0 )
         {
            System.out.println("No overlap possible... --> f["+k+"] = 0");
            f[k] = 0;          // No overlap possible
         }
         else
         {
            f[k] = f[i] + 1;   // Compute f(k) using f(i)

            System.out.println("Overlap found ... --> f["+k+"] = "+f[k]);
         }
      }

      return(f);
   }


   public static void main(String[] args)
   {
      String P;
      Scanner in;
      int[] f;


      in = new Scanner( System.in );

      System.out.print("P = ");
      P = in.nextLine();
      System.out.println();

      f = KMP_failure_function(P);

      for (int i = 0; i < P.length(); i++ )
      {
         System.out.println("f("+i+") = " + f[i]);
      }

      System.out.println();
   }



   /* =====================================================
      Variables and Methods to make the algorithm visual
      ===================================================== */
   public static String T_ruler, P_ruler;

   public static String ruler(int n)
   {
      String out = "";
      char   x = '0';

      for ( int i = 0; i < n; i++ )
      {
         out = out + x;
	 x++;
	 if ( x > '9' )
	    x = '0';
      }

      return out;
   }

   public static void printState(String T, String P, int i, int j)
   {
      T_ruler = ruler( T.length() );

      P_ruler = ruler( P.length() );

      System.out.println("=====================================");
      System.out.println("Matching: i = " + i + ", j = " + j);

      System.out.println("   " + T_ruler );
      System.out.println("   " + T);
      System.out.print("   ");
      for ( int k = 0; k < i-j; k++)
         System.out.print(" ");
      System.out.println(P);

      System.out.print("   ");
      for ( int k = 0; k < i-j; k++)
         System.out.print(" ");
      System.out.println( P_ruler );

      System.out.print("   ");
      for ( int k = 0; k < i; k++)
         System.out.print(" ");
      System.out.println("^");

      System.out.print("   ");
      for ( int k = 0; k < i; k++)
         System.out.print(" ");
      System.out.println("|");
      System.out.println();
   }
}
```







# KMP in leetcode

http://www.voidcn.com/article/p-uuefgkai-bnw.html

https://leetcode-cn.com/problems/implement-strstr/comments/

https://leetcode.com/problems/shortest-palindrome/discuss/60113/clean-kmp-solution-with-super-detailed-explanation



