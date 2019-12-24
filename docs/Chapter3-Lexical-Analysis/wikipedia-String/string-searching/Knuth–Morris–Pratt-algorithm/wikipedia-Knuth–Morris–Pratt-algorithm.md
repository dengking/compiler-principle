[TOC]

# Introduction

It takes me some effort to master KMP algorithm. Here are three articles that helped me solve the mystery as I learned. 



# [Knuth–Morris–Pratt algorithm](https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm)

In [computer science](https://en.wikipedia.org/wiki/Computer_science), the **Knuth–Morris–Pratt [string-searching algorithm](https://en.wikipedia.org/wiki/String-searching_algorithm)** (or **KMP algorithm**) searches for occurrences of a "word" `W` within a main "text string" `S` by employing the observation that when a mismatch occurs, the word itself embodies sufficient information to determine where the next match could begin, thus bypassing re-examination of previously matched characters.

The [algorithm](https://en.wikipedia.org/wiki/Algorithm) was conceived by [James H. Morris](https://en.wikipedia.org/wiki/James_H._Morris) and independently discovered by [Donald Knuth](https://en.wikipedia.org/wiki/Donald_Knuth) "a few weeks later" from automata theory.[[1\]](https://en.wikipedia.org/wiki/Knuth–Morris–Pratt_algorithm#cite_note-knuth1977-1)[[2\]](https://en.wikipedia.org/wiki/Knuth–Morris–Pratt_algorithm#cite_note-2) Morris and [Vaughan Pratt](https://en.wikipedia.org/wiki/Vaughan_Pratt) published a technical report in 1970.[[3\]](https://en.wikipedia.org/wiki/Knuth–Morris–Pratt_algorithm#cite_note-3) The three also published the algorithm jointly in 1977.[[1\]](https://en.wikipedia.org/wiki/Knuth–Morris–Pratt_algorithm#cite_note-knuth1977-1) Independently, in 1969, [Matiyasevich](https://en.wikipedia.org/wiki/Yuri_Matiyasevich)[[4\]](https://en.wikipedia.org/wiki/Knuth–Morris–Pratt_algorithm#cite_note-4)[[5\]](https://en.wikipedia.org/wiki/Knuth–Morris–Pratt_algorithm#cite_note-5) discovered a similar algorithm, coded by a two-dimensional Turing machine, while studying a string-pattern-matching recognition problem over a binary alphabet. This was the first linear-time algorithm for string matching.

# [详解KMP算法](https://www.cnblogs.com/yjiyjige/p/3263858.html)

KMP算法要解决的问题就是在字符串（也叫主串）中的模式（pattern）定位问题。说简单点就是我们平时常说的关键字搜索。模式串就是关键字（接下来称它为`P`），如果它在一个主串（接下来称为`T`）中出现，就返回它的具体位置，否则返回`-1`（常用手段）。

 ![img](https://images0.cnblogs.com/blog/416010/201308/17083616-9b40c67ea22e449f813fb38fcfd3a4fb.png)

首先，对于这个问题有一个很单纯的想法：从左到右一个个匹配，如果这个过程中有某个字符不匹配，就跳回去，将模式串向右移动一位。这有什么难的？

我们可以这样初始化：

 ![img](https://images0.cnblogs.com/blog/416010/201308/17083647-9dfd3e4a709c40dd98d9817927651960.png)

之后我们只需要比较**`i`指针**指向的字符和**`j`指针**指向的字符是否一致。如果一致就都向后移动，如果不一致，如下图：

![img](https://images0.cnblogs.com/blog/416010/201308/17083659-e6718026bf4f48a0be2d5d6076be4c55.png) 

 

`A`和`E`不相等，那就把**`i`指针**移回第1位（假设下标从0开始），`j`移动到模式串的第0位，然后又重新开始这个步骤：

 ![img](https://images0.cnblogs.com/blog/416010/201308/17083714-7de56d2c1cc84dbfa376cf410ba6f053.png)

基于这个想法我们可以得到以下的程序：

```java
/**

 * 暴力破解法

 * @param ts 主串

 * @param ps 模式串

 * @return 如果找到，返回在主串中第一个字符出现的下标，否则为-1

 */

public static int bf(String ts, String ps) {

    char[] t = ts.toCharArray();

    char[] p = ps.toCharArray();

    int i = 0; // 主串的位置

    int j = 0; // 模式串的位置

    while (i < t.length && j < p.length) {

       if (t[i] == p[j]) { // 当两个字符相同，就比较下一个

           i++;

           j++;

       } else {

           i = i - j + 1; // 一旦不匹配，i后退

           j = 0; // j归0

       }

    }

    if (j == p.length) {

       return i - j;

    } else {

       return -1;

    }

}
```

上面的程序是没有问题的，但不够好！

> NOTE: geeksforgeeks的文章[Naive algorithm for Pattern Searching](https://www.geeksforgeeks.org/naive-algorithm-for-pattern-searching/)中给出的代码是比上述代码更加容易理解的。 



如果是人为来寻找的话，肯定不会再把`i`移动回第1位，**因为主串匹配失败的位置前面除了第一个`A`之外再也没有`A`**了，我们为什么能知道主串前面只有一个`A`？**因为我们已经知道前面三个字符都是匹配的！（这很重要）**。移动过去肯定也是不匹配的！有一个想法，`i`可以不动，我们只需要移动`j`即可，如下图：

 ![img](https://images0.cnblogs.com/blog/416010/201308/17083828-cdb207f5460f4645982171e58571a741.png)

上面的这种情况还是比较理想的情况，我们最多也就多比较了两次。但假如是在主串`SSSSSSSSSSSSSA`中查找`SSSSB`，比较到最后一个才知道不匹配，然后`i`**回溯**，这个的效率是显然是最低的。

> NOTE: 关于回溯，参见[Backtracking](https://en.wikipedia.org/wiki/Backtracking)

大牛们是无法忍受“暴力破解”这种低效的手段的，于是他们三个研究出了KMP算法。其思想就如同我们上边所看到的一样：“**利用已经部分匹配这个有效信息，保持`i`指针不回溯，通过修改`j`指针，让模式串尽量地移动到有效的位置**。”

> NOTE: 提醒你注意**尽量地**这个修饰语，等你完全理解了KMP算法，你就幡然醒悟这个修饰语是非常妙的。其实在这里，我是可以向你提前透露的，既然说是尽量，那么也就是说移动到的位置不一定是最最有效的位置，而是一个相对有效的位置，可能需要经过多次移动才能够到达正确的位置，毕竟计算机不是像我们人这样的智能。

所以，整个KMP的重点就在于**当某一个字符与主串不匹配时，我们应该知道`j`指针要移动到哪**？

接下来我们自己来发现`j`的移动规律：

 ![img](https://images0.cnblogs.com/blog/416010/201308/17083912-49365b7e67cd4877b2f501074dae68d2.png)

如图：`C`和`D`不匹配了，我们要把`j`移动到哪？显然是第1位。为什么？因为前面有一个`A`相同啊：

![img](https://images0.cnblogs.com/blog/416010/201308/17083929-a9ccfb08833e4cf1a42c30f05608f8f5.png)

如下图也是一样的情况：

![img](https://images0.cnblogs.com/blog/416010/201308/17084030-82e4b71b85a440c5a636d57503931415.png)

可以把`j`指针移动到第2位，因为前面有两个字母是一样的：

 ![img](https://images0.cnblogs.com/blog/416010/201308/17084037-cc3c34200809414e9421c316ceba2cda.png)

至此我们可以大概看出一点端倪，当匹配失败时，`j`要移动的下一个位置`k`。存在着这样的性质：**最前面的`k`字符和`j`之前的最后`k`个字符是一样的**。

如果用数学公式来表示是这样的

`P[0 ~ k-1] == P[j-k ~ j-1]`

这个相当重要，如果觉得不好记的话，可以通过下图来理解：

 ![img](https://images0.cnblogs.com/blog/416010/201308/17084056-66930855432b4357bafbf8d6c76c1840.png)

弄明白了这个就应该可能明白为什么可以直接将`j`移动到`k`位置了。

因为:

当`T[i] != P[j]`时

有`T[i-j ~ i-1] == P[0 ~ j-1]`

由`P[0 ~ k-1] == P[j-k ~ j-1]`

必然：`T[i-k ~ i-1] == P[0 ~ k-1]`

> NOTE: 上述公式其实就是a==b, b==c,则a==c

公式很无聊，能看明白就行了，不需要记住。

> NOTE: 作者这里的总结不够直接，下面是摘自百度百科[kmp算法](https://baike.baidu.com/item/kmp%E7%AE%97%E6%B3%95/10951804?fr=aladdin)中对这个结论的总结，它非常直接：
>
> 用暴力算法匹配字符串过程中，我们会把`T[0]` 跟 `W[0]` 匹配，如果相同则匹配下一个字符，直到出现不相同的情况，此时我们会丢弃前面的匹配信息，然后把`T[1]` 跟 `W[0]`匹配，循环进行，直到主串结束，或者出现匹配成功的情况。这种丢弃前面的匹配信息的方法，极大地降低了匹配效率。
>
> 而在KMP算法中，对于每一个模式串我们会事先计算出模式串的内部匹配信息，在匹配失败时最大的移动模式串，以减少匹配次数。
>
> 比如，在简单的一次匹配失败后，我们会想将模式串尽量的右移和主串进行匹配。右移的距离在KMP算法中是如此计算的：在**已经匹配的模式串子串**中，找出最长的相同的[前缀](https://baike.baidu.com/item/前缀)和[后缀](https://baike.baidu.com/item/后缀)，然后移动使它们重叠。



这一段只是为了证明我们为什么可以直接将`j`移动到`k`而无须再比较前面的`k`个字符。

## 求解next数组

好，接下来就是重点了，怎么求这个（这些）`k`呢？因为在`P`的每一个位置都可能发生不匹配，也就是说我们要计算每一个位置`j`对应的`k`，所以用一个数组`next`来保存，`next[j] = k`，表示当`T[i] != P[j]`时，**`j`指针**的下一个位置。

很多教材或博文在这个地方都是讲得比较含糊或是根本就一笔带过，甚至就是贴一段代码上来，为什么是这样求？怎么可以这样求？根本就没有说清楚。而这里恰恰是整个算法最关键的地方。

```java
public static int[] getNext(String ps) {

    char[] p = ps.toCharArray();

    int[] next = new int[p.length];

    next[0] = -1;

    int j = 0;

    int k = -1;

    while (j < p.length - 1) {

       if (k == -1 || p[j] == p[k]) {

            next[++j] = ++k;

       } else {

           k = next[k];

       }

    }

    return next;

}
```

这个版本的求`next`数组的算法应该是流传最广泛的，代码是很简洁。可是真的很让人摸不到头脑，它这样计算的依据到底是什么？

好，先把这个放一边，我们自己来推导思路，现在要始终记住一点，`next[j]`的值（也就是`k`）表示，当`P[j] != T[i]`时，`j`指针的下一步移动位置。

先来看第一个：当`j`为0时，如果这时候不匹配，怎么办？

![img](https://images0.cnblogs.com/blog/416010/201308/17084258-efd2e95d3644427ebc0304ed3d7adefb.png)

像上图这种情况，`j`已经在最左边了，不可能再移动了，这时候要应该是`i`指针后移。所以在代码中才会有`next[0] = -1;`这个初始化。

> NOTE: 看了下面的完整的代码就知道为什么使用`-1`来作为初始值，因为`i++`和`j++`是在相同的分支中，`j++`后`j`为0，这就保证了从P的第一个元素开始匹配。

如果是当`j`为1的时候呢？

 ![img](https://images0.cnblogs.com/blog/416010/201308/17084310-29f9f8dbb6034151a383e7ccf6f5583e.png)

显然，`j`指针一定是后移到0位置的。因为它前面也就只有这一个位置了。

下面这个是最重要的，请看如下图：

![img](https://images0.cnblogs.com/blog/416010/201308/17084327-8a3cdfab03094bfa9e5cace26796cae5.png) 

![img](https://images0.cnblogs.com/blog/416010/201308/17084342-616036472ab546c082aa991004bb0034.png)



请仔细对比这两个图。

我们发现一个规律：

### 当`P[k] == P[j]`时

当`P[k] == P[j]`时，有`next[j+1] == next[j] + 1`

其实这个是可以证明的：

因为在`P[j]`之前已经有`P[0 ~ k-1] == p[j-k ~ j-1]`。（`next[j] == k`）

这时候现有`P[k] == P[j]`，我们是不是可以得到`P[0 ~ k-1] + P[k] == p[j-k ~ j-1] + P[j]`。

即：`P[0 ~ k] == P[j-k ~ j]`，即`next[j+1] == k + 1 == next[j] + 1`。

这里的公式不是很好懂，还是看图会容易理解些。

### 当`P[k] != P[j]`时,

当`P[k] != P[j]`时，如下图所示：

![img](https://images0.cnblogs.com/blog/416010/201308/17122358-fd7e52dd382c4268a8ff52b85bff465d.png) 



像这种情况，如果你从代码上看应该是这一句：`k = next[k];`为什么是这样子？你看下面应该就明白了。

 ![img](https://images0.cnblogs.com/blog/416010/201308/17122439-e349fed25e974e7886a27d18871ae48a.png)

现在你应该知道为什么要`k = next[k]`了吧！像上边的例子，我们已经不可能找到`[ A，B，A，B ]`这个最长的后缀串了，但我们还是可能找到`[ A，B ]`、`[ B ]`这样的前缀串的。所以这个过程像不像在定位`[ A，B，A，C ]`这个串，当`C`和主串不一样了（也就是`k`位置不一样了），那当然是把指针移动到`next[k]`啦。

> NOTE: 这篇文章这里的分析还是比较难以理解的，下一篇在分析更加透彻。

> NOTE: 构建`next`数组的算法是使用的数学归纳法来求解next数组的每个值，即根据`next`数组中前`j`个元素的值来求解`next[j+1]`的值。



有了`next`数组之后就一切好办了，我们可以动手写KMP算法了：

```java
public static int KMP(String ts, String ps) {

    char[] t = ts.toCharArray();

    char[] p = ps.toCharArray();

    int i = 0; // 主串的位置

    int j = 0; // 模式串的位置

    int[] next = getNext(ps);

    while (i < t.length && j < p.length) {

       if (j == -1 || t[i] == p[j]) { // 当j为-1时，要移动的是i，当然j也要归0

           i++;

           j++;

       } else {

           // i不需要回溯了

           // i = i - j + 1;

           j = next[j]; // j回到指定位置

       }

    }

    if (j == p.length) {

       return i - j;

    } else {

       return -1;

    }

}
```

和暴力破解相比，就改动了4个地方。其中最主要的一点就是，`i`不需要回溯了。

最后，来看一下上边的算法存在的缺陷。来看第一个例子：

![img](https://images0.cnblogs.com/blog/416010/201308/17084712-f0d6998938764b309f61923452a2b20f.png) 

显然，当我们上边的算法得到的`next`数组应该是`[ -1，0，0，1 ]`

所以下一步我们应该是把`j`移动到第1个元素咯：

 ![img](https://images0.cnblogs.com/blog/416010/201308/17084726-790fc1b2c48c411b8011eab9de692f6d.png)

不难发现，**这一步是完全没有意义的。因为后面的`B`已经不匹配了，那前面的`B`也一定是不匹配的**，同样的情况其实还发生在第2个元素`A`上。

显然，**发生问题的原因在于`P[j] == P[next[j]]`**。

所以我们也只需要添加一个判断条件即可：

```java
public static int[] getNext(String ps) {

    char[] p = ps.toCharArray();

    int[] next = new int[p.length];

    next[0] = -1;

    int j = 0;

    int k = -1;

    while (j < p.length - 1) {

       if (k == -1 || p[j] == p[k]) {

           if (p[++j] == p[++k]) { // 当两个字符相等时要跳过

              next[j] = next[k];

           } else {

              next[j] = k;

           }

       } else {

           k = next[k];

       }

    }

    return next;

}
```



该算法的实现是非常类似于动态规划算法的

`next[j]`的值`k`就是`j`位之前的子串中，前缀集和后缀集中的最大重复子串的长度。

`abacabac`

|        |             |              | next[0]=-1;j=0;k=-1 |
| ------ | ----------- | ------------ | ------------------- |
| 条件1  | 条件2       | 分支2        | 分支1               |
| k==-1  |             |              | next[1]=0;j=1;k=0   |
|        | p[1]!=p[0]; | k=next[0]=-1 |                     |
| k==-1  |             |              | next[2]=0;j=2;k=0   |
|        | p[2]==p[0]; |              | next[3]=1;j=3;k=1   |
|        | p[3]!=p[1]; | k=next[1]=0  |                     |
|        | p[3]!=p[0]; | k=next[0]=-1 |                     |
| k==-1; |             |              | next[4]=0;j=4;k=0   |
|        | p[4]==p[0]  |              | next[5]=1;j=5;k=1   |
|        | p[5]==p[1]  |              | next[6]=2;j=6;k=2   |
|        | p[6]==p[2]  |              | next[7]=3;j=7;k=3   |
|        | p[7]==p[3]  |              | next[8]=4;j=8;k=4   |

要想得到`p[j+1]`，只需要比较`p[j]`和`p[k]`即可；



# [Computing the KMP failure function (f(k))](http://www.mathcs.emory.edu/~cheung/Courses/323/Syllabus/Text/Matching-KMP2.html)

## definition of `f(k)`

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
>  """
>  构建字符串p的最长公共前缀后缀数组
>  :param p:
>  :return:
>  """
>  failure_table = list()
>  len_of_p = len(p)
>  for len_of_sub_str in range(1, len_of_p + 1):
>      max_len_of_overlap = int(len_of_sub_str / 2)  # 最大重叠前缀后缀的长度
>      print("子串长度:{},最大重叠前缀后缀长度:{}".format(len_of_sub_str, max_len_of_overlap))
>      if max_len_of_overlap == 0:
>          # 长度为1的串，是没有重叠前缀后缀的
>          failure_table.append(0)
>      else:
>          found = False  # 是否找到重叠前缀后缀
>          for len_of_overlap in range(max_len_of_overlap, 0, -1):
>              print("重叠前缀后缀长度:{}".format(len_of_overlap))
>              # len_of_overlap 重叠前缀后缀的长度
>              for prefix_index in range(len_of_overlap):
>                  suffix_index = prefix_index + (len_of_sub_str - len_of_overlap)
>                  print("前缀起始位置:{},后缀起始位置:{}".format(prefix_index, suffix_index))
>                  if p[prefix_index] == p[suffix_index]:
>                      if suffix_index == len_of_sub_str - 1:
>                          # 找到了重叠部分
>                          failure_table.append(len_of_overlap)
>                          found = True
>                          break
>                  else:
>                      break
>              if found:
>                  break
>          if not found:
>              failure_table.append(0)
>  return failure_table
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