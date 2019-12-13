[TOC]



# [Aho-Corasick algorithm](https://cp-algorithms.com/string/aho_corasick.html)

Let there be a set of strings with the total length mm (sum of all lengths). The Aho-Corasick algorithm constructs a data structure similar to a trie with some additional links, and then constructs a **finite state machine** (automaton) in $O(mk)$ time, where $k$ is the size of the used alphabet.

The algorithm was proposed by Alfred Aho and Margaret Corasick in 1975.

## Construction of the trie

Formally a trie is a rooted tree, where each edge of the tree is labeled by some letter. All outgoing edge from one vertex mush have different labels.

Consider any path in the trie from the root to any vertex. If we write out the labels of all edges on the path, we get a string that corresponds to this path. For any vertex in the trie we will associate the string from the root to the vertex.

Each vertex will also have a flag `leaf` which will be true, if any string from the given set corresponds to this vertex.

Accordingly to build a trie for a set of strings means to build a trie such that each `leaf` vertex will correspond to one string from the set, and conversely that each string of the set corresponds to one `leaf` vertex.

We now describe how to construct a trie for a given set of strings in linear time with respect to their total length.

We introduce a structure for the vertices of the tree.

```c++
const int K = 26;

struct Vertex {
    int next[K];
    bool leaf = false;

    Vertex() {
        fill(begin(next), end(next), -1);
    }
};

vector<Vertex> trie(1);
```

Here we store the trie as an array of `Vertex`. Each `Vertex` contains the flag `leaf`, and the edges in the form of ans array `next[]`, where `next[i]` is the index to the vertex that we reach by following the character `i`, or −1, if there is no such edge. Initially the trie consists of only one vertex - the root - with the index 0.

Now we implement a function that will add a string `s` to the trie. The implementation is extremely simple: we start at the root node, and as long as there are edges corresponding to the characters of `s` we follow them. If there is no edge for one character, we simply generate a new vertex and connect it via an edge. At the end of the process we mark the last vertex with flag `leaf`.

```c++
void add_string(string const& s) {
    int v = 0;
    for (char ch : s) {
        int c = ch - 'a';
        if (trie[v].next[c] == -1) {
            trie[v].next[c] = trie.size();
            trie.emplace_back();
        }
        v = trie[v].next[c];
    }
    trie[v].leaf = true;
}
```

The implementation obviously runs in linear time. And since every vertex store `k` links, it will use `O(mk)` memory.

It is possible to decrease the memory consumption to O(m) by using a map instead of an array in each vertex. However this will increase the complexity to `O(nlogk)`.

## Construction of an automaton

Suppose we have built a trie for the given set of strings. Now let's look at it from a different side. If we look at any vertex. The string that corresponds to it is a prefix of one or more strings in the set, thus each vertex of the trie can be interpreted as a position in one or more strings from the set.

In fact the trie vertices can be interpreted as **states** in a **finite deterministic automaton**. From any state we can transition - using some input letter - to other states, i.e. to another position in the set of strings. For example, if there is only one string in the trie `abc`, and we are standing at vertex `2` (which corresponds to the string `ab`), then using the letter `c` we can transition to the state `3`.

Thus we can understand the edges of the trie as **transitions** in an automaton according to the corresponding letter. However for an automaton we cannot restrict the possible transitions for each state. If we try to perform a transition using a letter, and there is no corresponding edge in the trie, then we nevertheless must go into some state.

Thus we can understand the edges of the trie as transitions in an automaton according to the corresponding letter. However for an automaton we cannot restrict the possible transitions for each state. If we try to perform a transition using a letter, and there is no corresponding edge in the trie, then we nevertheless must go into some state.

