[TOC]



# [String-searching algorithm](https://en.wikipedia.org/wiki/String-searching_algorithm)



## Basic classification of search algorithms

The various [algorithms](https://en.wikipedia.org/wiki/Algorithm) can be classified by the number of patterns each uses.

### Single-pattern algorithms

Let *m* be the length of the pattern, *n* be the length of the searchable text and *k* = |Σ| be the size of the alphabet.

|                          Algorithm                           | Preprocessing time | Matching time[[1\]](https://en.wikipedia.org/wiki/String-searching_algorithm#endnote_Asymptotic_times) | Space |
| :----------------------------------------------------------: | :----------------: | :----------------------------------------------------------: | :---: |
|                Naïve string-search algorithm                 |        none        |                            Θ(nm)                             | none  |
| [Rabin–Karp algorithm](https://en.wikipedia.org/wiki/Rabin–Karp_algorithm) |        Θ(m)        |              average Θ(n + m), worst Θ((n−m)m)               | O(1)  |
| [Knuth–Morris–Pratt algorithm](https://en.wikipedia.org/wiki/Knuth–Morris–Pratt_algorithm) |        Θ(m)        |                             Θ(n)                             | Θ(m)  |
| [Boyer–Moore string-search algorithm](https://en.wikipedia.org/wiki/Boyer–Moore_string-search_algorithm) |      Θ(m + k)      |                   best Ω(n/m), worst O(mn)                   | Θ(k)  |
| [Bitap algorithm](https://en.wikipedia.org/wiki/Bitap_algorithm) (*shift-or*, *shift-and*, *Baeza–Yates–Gonnet*; fuzzy; agrep) |      Θ(m + k)      |                            O(mn)                             |       |
| [Two-way string-matching algorithm](https://en.wikipedia.org/wiki/Two-way_string-matching_algorithm) (glibc memmem/strstr)[[3\]](https://en.wikipedia.org/wiki/String-searching_algorithm#cite_note-3) |        Θ(m)        |                            O(n+m)                            | O(1)  |
| BNDM (Backward Non-Deterministic DAWG Matching) (fuzzy + regex; nrgrep)[[4\]](https://en.wikipedia.org/wiki/String-searching_algorithm#cite_note-4) |        O(m)        |                             O(n)                             |       |
| BOM (Backward Oracle Matching)[[5\]](https://en.wikipedia.org/wiki/String-searching_algorithm#cite_note-5) |        O(m)        |                            O(mn)                             |       |

1.**[^](https://en.wikipedia.org/wiki/String-searching_algorithm#ref_Asymptotic_times)** Asymptotic times are expressed using [O, Ω, and Θ notation](https://en.wikipedia.org/wiki/Big_O_notation).

The **[Boyer–Moore string-search algorithm](https://en.wikipedia.org/wiki/Boyer–Moore_string-search_algorithm)** has been the standard benchmark for the practical string-search literature.[[6\]](https://en.wikipedia.org/wiki/String-searching_algorithm#cite_note-:0-6)

### Algorithms using a finite set of patterns

- [Aho–Corasick string matching algorithm](https://en.wikipedia.org/wiki/Aho–Corasick_string_matching_algorithm) (extension of Knuth-Morris-Pratt)
- [Commentz-Walter algorithm](https://en.wikipedia.org/wiki/Commentz-Walter_algorithm) (extension of Boyer-Moore)
- Set-BOM (extension of Backward Oracle Matching)
- [Rabin–Karp string search algorithm](https://en.wikipedia.org/wiki/Rabin–Karp_string_search_algorithm)

### Algorithms using an infinite number of patterns

Naturally, the patterns can not be enumerated finitely in this case. They are represented usually by a [regular grammar](https://en.wikipedia.org/wiki/Regular_grammar) or [regular expression](https://en.wikipedia.org/wiki/Regular_expression).



## Other classification

Other classification approaches are possible. One of the most common uses preprocessing as main criteria.

**Classes of string searching algorithms**[[7\]](https://en.wikipedia.org/wiki/String-searching_algorithm#cite_note-7)

|                           |   Text not preprocessed    |                      Text preprocessed                       |
| :-----------------------: | :------------------------: | :----------------------------------------------------------: |
| Patterns not preprocessed |   Elementary algorithms    |                        Index methods                         |
|   Patterns preprocessed   | Constructed search engines | Signature methods :[[8\]](https://en.wikipedia.org/wiki/String-searching_algorithm#cite_note-8) |

Another one classifies the algorithms by their matching strategy:[[9\]](https://en.wikipedia.org/wiki/String-searching_algorithm#cite_note-9)

- Match the prefix first (Knuth-Morris-Pratt, Shift-And, Aho-Corasick)
- Match the suffix first (Boyer-Moore and variants, Commentz-Walter)
- Match the best factor first (BNDM, BOM, Set-BOM)
- Other strategy (Naive, Rabin-Karp)



### Naïve string search

A simple and inefficient way to see where one string occurs inside another is to check each place it could be, one by one, to see if it's there. So first we see if there's a copy of the needle in the first character of the haystack; if not, we look to see if there's a copy of the needle starting at the second character of the haystack; if not, we look starting at the third character, and so forth. In the normal case, we only have to look at one or two characters for each wrong position to see that it is a wrong position, so in the average case, this takes [O](https://en.wikipedia.org/wiki/Big_O_notation)(*n* + *m*) steps, where *n* is the length of the haystack and *m* is the length of the needle; but in the worst case, searching for a string like "aaaab" in a string like "aaaaaaaaab", it takes [O](https://en.wikipedia.org/wiki/Big_O_notation)(*nm*)



### Finite-state-automaton-based search

In this approach, we avoid backtracking by constructing a [deterministic finite automaton](https://en.wikipedia.org/wiki/Deterministic_finite_automaton) (DFA) that recognizes stored search string. These are expensive to construct—they are usually created using the [powerset construction](https://en.wikipedia.org/wiki/Powerset_construction)—but are very quick to use. For example, the [DFA](https://en.wikipedia.org/wiki/Deterministic_finite_automaton) shown to the right recognizes the word "MOMMY". This approach is frequently generalized in practice to search for arbitrary [regular expressions](https://en.wikipedia.org/wiki/Regular_expression).



### Stubs

[Knuth–Morris–Pratt](https://en.wikipedia.org/wiki/Knuth–Morris–Pratt_algorithm) computes a [DFA](https://en.wikipedia.org/wiki/Deterministic_finite_automaton) that recognizes inputs with the string to search for as a suffix, [Boyer–Moore](https://en.wikipedia.org/wiki/Boyer–Moore_string_search_algorithm) starts searching from the end of the needle, so it can usually jump ahead a whole needle-length at each step. Baeza–Yates keeps track of whether the previous *j* characters were a prefix of the search string, and is therefore adaptable to [fuzzy string searching](https://en.wikipedia.org/wiki/Fuzzy_string_searching). The [bitap algorithm](https://en.wikipedia.org/wiki/Bitap_algorithm) is an application of Baeza–Yates' approach.



### Index methods

Faster search algorithms preprocess the text. After building a [substring index](https://en.wikipedia.org/wiki/Substring_index), for example a [suffix tree](https://en.wikipedia.org/wiki/Suffix_tree) or [suffix array](https://en.wikipedia.org/wiki/Suffix_array), the occurrences of a pattern can be found quickly. As an example, a suffix tree can be built in $ \Theta (n) $ time, and all $ z $ occurrences of a pattern can be found in $ O(m) $ time under the assumption that the alphabet has a constant size and all inner nodes in the suffix tree know what leaves are underneath them. The latter can be accomplished by running a [DFS algorithm](https://en.wikipedia.org/wiki/Depth-first_search) from the root of the suffix tree.

> NOTE: https://github.com/fxsjy/jieba



### Other variants

Some search methods, for instance [trigram search](https://en.wikipedia.org/wiki/Trigram_search), are intended to find a "closeness" score between the search string and the text rather than a "match/non-match". These are sometimes called ["fuzzy" searches](https://en.wikipedia.org/wiki/Approximate_string_matching).