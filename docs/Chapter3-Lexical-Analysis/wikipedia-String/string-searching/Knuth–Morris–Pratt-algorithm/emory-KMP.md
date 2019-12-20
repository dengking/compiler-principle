[TOC]

# [Computing the KMP failure function (f(k))](http://www.mathcs.emory.edu/~cheung/Courses/323/Syllabus/Text/Matching-KMP2.html)



Naive way to find ***f(k)***:

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



The values `f(k)` are computed easily using **existing prefix overlap information**:

- `f(0) = 0` (`f(0)` is always 0)
- `f(1)` is computing using (already computed) value `f(0)`
- `f(2)` is computing using (already computed) value `f(0)`, `f(1)`
- `f(3)` is computing using (already computed) value `f(0)`, `f(1)`, `f(2)`
  And so on



Suppose that we know that: `f(k−1) = x`

In other words: the longest overlapping suffix and prefix in "`p0 p1 ... pk-1`" has `x` characters:

```
                     f(k-1) = x characters               
                  <----------------------->
      p1 p2 p3 ... pk-x-2 pk-x-3 pk-x-4 .... pk-1 
                       ^     ^     ^         ^
                       |     |     |  equal  |
                       v     v     v         v
                       p0    p1    p2 ....    px-1   px ... pk-1 
```







# KMP in leetcode

http://www.voidcn.com/article/p-uuefgkai-bnw.html

https://leetcode-cn.com/problems/implement-strstr/comments/

https://leetcode.com/problems/shortest-palindrome/discuss/60113/clean-kmp-solution-with-super-detailed-explanation