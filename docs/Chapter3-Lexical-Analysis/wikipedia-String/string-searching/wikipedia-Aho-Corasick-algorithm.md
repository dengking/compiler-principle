[TOC]



# [Aho–Corasick algorithm](https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm)

In [computer science](https://en.wikipedia.org/wiki/Computer_science), the **Aho–Corasick algorithm** is a [string-searching algorithm](https://en.wikipedia.org/wiki/String-searching_algorithm) invented by [Alfred V. Aho](https://en.wikipedia.org/wiki/Alfred_V._Aho) and Margaret J. Corasick.[[1\]](https://en.wikipedia.org/wiki/Aho–Corasick_algorithm#cite_note-1) It is a kind of dictionary-matching algorithm that locates elements of a finite set of strings (the "dictionary") within an input text. It matches all strings simultaneously. The [complexity](https://en.wikipedia.org/wiki/Time_complexity) of the algorithm is linear in the length of the strings plus the length of the searched text plus the number of output matches. Note that because all matches are found, there can be a quadratic number of matches if every substring matches (e.g. dictionary = `a`, `aa`, `aaa`, `aaaa` and input string is `aaaa`).

Informally, the algorithm constructs a [finite-state machine](https://en.wikipedia.org/wiki/Finite-state_machine) that resembles a [trie](https://en.wikipedia.org/wiki/Trie) with additional links between the various internal nodes. These extra internal links allow fast transitions between failed string matches (e.g. a search for `cat` in a trie that does not contain `cat`, but contains `cart`, and thus would fail at the node prefixed by `ca`), to other branches of the trie that share a common prefix (e.g., in the previous case, a branch for attribute might be the best lateral transition). This allows the automaton to transition between string matches without the need for backtracking.

When the string dictionary is known in advance (e.g. a [computer virus](https://en.wikipedia.org/wiki/Computer_virus) database), the construction of the automaton can be performed once off-line and the compiled automaton stored for later use. In this case, its run time is linear in the length of the input plus the number of matched entries.

The Aho–Corasick string-matching algorithm formed the basis of the original [Unix command](https://en.wikipedia.org/wiki/List_of_Unix_commands) [fgrep](https://en.wikipedia.org/wiki/Grep#Variations).

## Example

In this example, we will consider a dictionary consisting of the following words: {`a`, `ab`, `bab`, `bc`, `bca`, `c`, `caa`}.

The graph below is the Aho–Corasick data structure constructed from the specified dictionary, with each **row** in the table representing a **node** in the trie, with the column **path** indicating the (unique) sequence of characters from the **root** to the node.

[![img](https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Ahocorasick.svg/220px-Ahocorasick.svg.png)](https://en.wikipedia.org/wiki/File:Ahocorasick.svg)

> A visualization of the trie for the dictionary on the right. **Suffix links** are in blue; **dictionary suffix links** in green. Nodes corresponding to dictionary entries are highlighted in blue.

The data structure has one node for every **prefix** of every string in the dictionary. So if (`bca`) is in the dictionary, then there will be nodes for (`bca`), (`bc`), (`b`), and (). If a node is in the dictionary then it is a **blue node**. Otherwise it is a **grey node**.

There is a **black directed "child" arc** from each node to a node whose name is found by appending one character. So there is a black arc from (`bc`) to (`bca`).

There is a **blue directed "suffix" arc** from each node to the node that is the longest possible strict suffix of it in the **graph**. For example, for node (`caa`), its strict suffixes are (`aa`) and (`a`) and (). The longest of these that exists in the graph is (`a`). So there is a blue arc from (`caa`) to (`a`). The **blue arcs** can be computed in linear time by repeatedly traversing the **blue arcs** of a node's **parent** until the traversing node has a child matching the character of the target node.

There is a **green "dictionary suffix" arc** from each node to the next node in the **dictionary** that can be reached by following **blue arcs**. For example, there is a green arc from (`bca`) to (`a`) because (`a`) is the first node in the dictionary (i.e. a blue node) that is reached when following the blue arcs to (`ca`) and then on to (a). The green arcs can be computed in linear time by repeatedly traversing blue arcs until a filled in node is found, and [memoizing](https://en.wikipedia.org/wiki/Memoization) this information.

**Dictionary {a, ab, bab, bc, bca, c, caa}**

| Path  | In dictionary | Suffix link | Dict suffix link |
| :---: | :-----------: | :---------: | :--------------: |
|  ()   |       –       |             |                  |
|  (a)  |       +       |     ()      |                  |
| (ab)  |       +       |     (b)     |                  |
|  (b)  |       –       |     ()      |                  |
| (ba)  |       –       |     (a)     |       (a)        |
| (bab) |       +       |    (ab)     |       (ab)       |
| (bc)  |       +       |     (c)     |       (c)        |
| (bca) |       +       |    (ca)     |       (a)        |
|  (c)  |       +       |     ()      |                  |
| (ca)  |       –       |     (a)     |       (a)        |
| (caa) |       +       |     (a)     |       (a)        |

At each step, the current node is extended by finding its child, and if that doesn't exist, finding its suffix's child, and if that doesn't work, finding its suffix's suffix's child, and so on, finally ending in the root node if nothing's seen before.

When the algorithm reaches a node, it outputs all the dictionary entries that end at the current character position in the input text. This is done by printing every node reached by following the dictionary suffix links, starting from that node, and continuing until it reaches a node with no dictionary suffix link. In addition, the node itself is printed, if it is a dictionary entry.

Execution on input string `abccab` yields the following steps:



# Implementation

https://github.com/WojciechMula/pyahocorasick