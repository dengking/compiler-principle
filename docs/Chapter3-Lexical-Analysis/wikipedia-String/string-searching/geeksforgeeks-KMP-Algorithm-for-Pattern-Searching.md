[TOC]



# [KMP Algorithm for Pattern Searching](https://www.geeksforgeeks.org/kmp-algorithm-for-pattern-searching/)



## KMP (Knuth Morris Pratt) Pattern Searching

The [Naive pattern searching algorithm](https://www.geeksforgeeks.org/searching-for-patterns-set-1-naive-pattern-searching/) doesn’t work well in cases where we see many matching characters followed by a mismatching character. Following are some examples.

```
   txt[] = "AAAAAAAAAAAAAAAAAB"
   pat[] = "AAAAB"

   txt[] = "ABABABCABABABCABABABC"
   pat[] =  "ABABAC" (not a worst case, but a bad case for Naive)
```

The KMP matching algorithm uses degenerating property (pattern having same **sub-patterns** appearing more than once in the pattern) of the pattern and improves the worst case complexity to `O(n)`. The basic idea behind KMP’s algorithm is: whenever we detect a mismatch (after some matches), we already know some of the characters in the text of the next window. We take advantage of this information to avoid matching the characters that we know will anyway match. Let us consider below example to understand this.

```
Matching Overview
txt = "AAAAABAAABA" 
pat = "AAAA"

We compare first window of txt with pat
txt = "AAAAABAAABA" 
pat = "AAAA"  [Initial position]
We find a match. This is same as Naive String Matching.

In the next step, we compare next window of txt with pat.
txt = "AAAAABAAABA" 
pat =  "AAAA" [Pattern shifted one position]
This is where KMP does optimization over Naive. In this 
second window, we only compare fourth A of pattern
with fourth character of current window of text to decide 
whether current window matches or not. Since we know 
first three characters will anyway match, we skipped 
matching first three characters. 

Need of Preprocessing?
An important question arises from the above explanation, 
how to know how many characters to be skipped. To know this, 
we pre-process pattern and prepare an integer array 
lps[] that tells us the count of characters to be skipped. 
```



### Preprocessing Overview:

- KMP algorithm preprocesses `pat[]` and constructs an auxiliary `lps[]` of size `m` (same as size of pattern) which is used to skip characters while matching.

- **name `lps` indicates longest proper prefix which is also suffix.**. A proper prefix is prefix with whole string **not** allowed. For example, prefixes of “ABC” are “”, “A”, “AB” and “ABC”. Proper prefixes are “”, “A” and “AB”. Suffixes of the string are “”, “C”, “BC” and “ABC”.

- We search for `lps` in sub-patterns. More clearly we focus on sub-strings of patterns that are either prefix and suffix.

- For each sub-pattern `pat[0..i]` where `i = 0` to `m-1`, `lps[i]` stores length of the maximum matching proper prefix which is also a suffix of the sub-pattern `pat[0..i]`.

  ```
     lps[i] = the longest proper prefix of pat[0..i] 
                which is also a suffix of pat[0..i]. 
  ```

  

**Note :** `lps[i]` could also be defined as longest prefix which is also proper suffix. We need to use properly at one place to make sure that the whole substring is not considered.



### Searching Algorithm:

Unlike [Naive algorithm](https://www.geeksforgeeks.org/searching-for-patterns-set-1-naive-pattern-searching/), where we slide the pattern by one and compare all characters at each shift, we use a value from `lps[]` to decide the next characters to be matched. The idea is to not match a character that we know will anyway match.

How to use `lps[]` to decide next positions (or to know a number of characters to be skipped)?

- We start comparison of `pat[j]` with `j = 0` with characters of current window of text.
- We keep matching characters `txt[i]` and `pat[j]` and keep incrementing `i` and `j` while `pat[j]` and `txt[i]` keep **matching**.
- When we see a mismatch
    - We know that characters `pat[0..j-1]` match with `txt[i-j…i-1]` (Note that `j` starts with `0` and increment it only when there is a match).
    - We also know (from above definition) that `lps[j-1]` is count of characters of `pat[0…j-1]` that are both proper prefix and suffix.
    - From above two points, we can conclude that we do not need to match these `lps[j-1]` characters with `txt[i-j…i-1]` because we know that these characters will anyway match. Let us consider above example to understand this.

