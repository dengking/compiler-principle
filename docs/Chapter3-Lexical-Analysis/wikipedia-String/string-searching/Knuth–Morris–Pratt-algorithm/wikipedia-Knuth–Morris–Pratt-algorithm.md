[TOC]



# [Knuth–Morris–Pratt algorithm](https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm)

In [computer science](https://en.wikipedia.org/wiki/Computer_science), the **Knuth–Morris–Pratt [string-searching algorithm](https://en.wikipedia.org/wiki/String-searching_algorithm)** (or **KMP algorithm**) searches for occurrences of a "word" `W` within a main "text string" `S` by employing the observation that when a mismatch occurs, the word itself embodies sufficient information to determine where the next match could begin, thus bypassing re-examination of previously matched characters.

The [algorithm](https://en.wikipedia.org/wiki/Algorithm) was conceived by [James H. Morris](https://en.wikipedia.org/wiki/James_H._Morris) and independently discovered by [Donald Knuth](https://en.wikipedia.org/wiki/Donald_Knuth) "a few weeks later" from automata theory.[[1\]](https://en.wikipedia.org/wiki/Knuth–Morris–Pratt_algorithm#cite_note-knuth1977-1)[[2\]](https://en.wikipedia.org/wiki/Knuth–Morris–Pratt_algorithm#cite_note-2) Morris and [Vaughan Pratt](https://en.wikipedia.org/wiki/Vaughan_Pratt) published a technical report in 1970.[[3\]](https://en.wikipedia.org/wiki/Knuth–Morris–Pratt_algorithm#cite_note-3) The three also published the algorithm jointly in 1977.[[1\]](https://en.wikipedia.org/wiki/Knuth–Morris–Pratt_algorithm#cite_note-knuth1977-1) Independently, in 1969, [Matiyasevich](https://en.wikipedia.org/wiki/Yuri_Matiyasevich)[[4\]](https://en.wikipedia.org/wiki/Knuth–Morris–Pratt_algorithm#cite_note-4)[[5\]](https://en.wikipedia.org/wiki/Knuth–Morris–Pratt_algorithm#cite_note-5) discovered a similar algorithm, coded by a two-dimensional Turing machine, while studying a string-pattern-matching recognition problem over a binary alphabet. This was the first linear-time algorithm for string matching.

## Background

A string-matching algorithm wants to find the starting index `m` in string `S[]` that matches the search word `W[]`.

The most straightforward algorithm, known as the "[Brute-force](https://en.wikipedia.org/wiki/Brute-force_search)" or "Naive" algorithm, is to look for a **word match** at each index `m`, the position in the string being searched, i.e. `S[m]`. At each position `m` the algorithm first checks for equality of the first character in the word being searched, i.e. `S[m] =? W[0]`. If a match is found, the algorithm tests the other characters in the word being searched by checking successive values of the word position index, `i`. The algorithm retrieves the character `W[i]` in the word being searched and checks for equality of the expression `S[m+i] =? W[i]`. If all successive characters match in `W` at position `m`, then a match is found at that position in the search string. If the index `m` reaches the end of the string then there is no match, in which case the search is said to "fail".

Usually, the trial check will quickly reject the trial match. If the strings are uniformly distributed random letters, then the chance that characters match is 1 in 26. In most cases, the trial check will reject the match at the initial letter. The chance that the first two letters will match is 1 in $26^2$ (1 in 676). So if the characters are random, then the expected complexity of searching string `S[]` of length *k* is on the order of *k* comparisons or *O*(*k*). The expected performance is very good. If `S[]` is 1 million characters and `W[]` is 1000 characters, then the string search should complete after about 1.04 million character comparisons.

That expected performance is not guaranteed. If the strings are not random, then checking a trial `m` may take many character comparisons. The worst case is if the two strings match in all but the last letter. Imagine that the string `S[]` consists of 1 million characters that are all *A*, and that the word `W[]` is 999 *A* characters terminating in a final *B* character. The simple string-matching algorithm will now examine 1000 characters at each trial position before rejecting the match and advancing the trial position. The simple string search example would now take about 1000 character comparisons times 1 million positions for 1 billion character comparisons. If the length of `W[]` is *n*, then the worst-case performance is *O*(*k*⋅*n*).

The KMP algorithm has a better worst-case performance than the straightforward algorithm. KMP spends a little time precomputing a table (on the order of the size of `W[]`, *O*(*n*)), and then it uses that table to do an efficient search of the string in *O*(*k*).

The difference is that KMP makes use of previous match information that the straightforward algorithm does not. In the example above, when KMP sees a trial match fail on the 1000th character (`i` = 999) because `S[m+999] ≠ W[999]`, it will increment `m` by 1, but it will know that the first 998 characters at the new position already match. KMP matched 999 *A* characters before discovering a mismatch at the 1000th character (position 999). Advancing the trial match position `m` by one throws away the first *A*, so KMP knows there are 998 *A* characters that match `W[]` and does not retest them; that is, KMP sets `i` to 998. KMP maintains its knowledge in the precomputed table and two state variables. When KMP discovers a mismatch, the table determines how much KMP will increase (variable `m`) and where it will resume testing (variable `i`).





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

如果是人为来寻找的话，肯定不会再把`i`移动回第1位，**因为主串匹配失败的位置前面除了第一个`A`之外再也没有`A`**了，我们为什么能知道主串前面只有一个`A`？**因为我们已经知道前面三个字符都是匹配的！（这很重要）**。移动过去肯定也是不匹配的！有一个想法，`i`可以不动，我们只需要移动`j`即可，如下图：

 ![img](https://images0.cnblogs.com/blog/416010/201308/17083828-cdb207f5460f4645982171e58571a741.png)

上面的这种情况还是比较理想的情况，我们最多也就多比较了两次。但假如是在主串`SSSSSSSSSSSSSA`中查找`SSSSB`，比较到最后一个才知道不匹配，然后`i`**回溯**，这个的效率是显然是最低的。

> NOTE: 此处的回溯是使用它的广义的概念。

大牛们是无法忍受“暴力破解”这种低效的手段的，于是他们三个研究出了KMP算法。其思想就如同我们上边所看到的一样：“**利用已经部分匹配这个有效信息，保持`i`指针不回溯，通过修改`j`指针，让模式串尽量地移动到有效的位置**。”

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

> NOTE: 作者这里的总结不够直接，下面是摘自[kmp算法](https://baike.baidu.com/item/kmp%E7%AE%97%E6%B3%95/10951804?fr=aladdin)中对这个结论的总结，它非常直接：
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



> NOTE: 构建`next`数组的算法是一个递归算法



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

