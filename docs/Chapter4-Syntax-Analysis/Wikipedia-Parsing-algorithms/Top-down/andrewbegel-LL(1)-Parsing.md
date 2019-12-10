[TOC]



# [LL(1) Parsing](https://andrewbegel.com/cs164/ll1.html)

The following grammar comes from Written Assignment 2.

```
E -> E + T | T
T -> T * F | F
F -> (E) | int
```

This is a grammar for arithmetic. There are several orders of precedence here: `()`'s beat `*`, and `*` beats `+`. We'd like to parse sentences using this grammar using a top-down, recursive descent algorithm.

## [left-recursion](https://en.wikipedia.org/wiki/Left_recursion) elimination

This algorithm traverses the grammar looking for matches between terminals (`*`, `+`, `(`, `)`, and `int`) and the input sentence. We do this search depth-first, which presents a problem. If we start at the starting production `E`, and derive the production `E + T`, we have `E` still on the left. In recursive-descent parsing, we can only expand the left-most non-terminal at each step! We're going to infinitely loop if we try to parse sentences using this grammar.

How do we fix it? We use a technique known as [left-recursion](https://en.wikipedia.org/wiki/Left_recursion) elimination to get rid of the non-terminals on the left-hand side of each production that cause us to infinitely loop. (Note: not all grammars have left recursion. You can identify the ones that have *immediate* left recursion by looking at all of the productions -- if the non-terminal on the left side of the arrow is the same as the non-terminal in the left-most position of any phrase on the right side of the arrow, then this grammar is left-recursive. There are other forms of left recursion that can show up if you were to "recurse" down multiple rules in the grammar. If you eventually will cause any infinite loop, the grammar is left-recursive.)

Let's take a look at the first one:

```
E -> E + T | T
```

What we do is this. For each production where the non-terminal on the left (`E`) of the arrow is the same as the left-side of a production on the right-hand side of the arrow (`E + T`), we take the part of the production without the `E` (`+T`) and move it down into its own new production (we'll call it `E'`).

```
E' -> + T
```

We're not done yet. Now, after each of the new productions, add `E'` to the end.

```
E' -> + T E'
```

Nope, still not done yet. Now add an extra production to epsilon.

```
E' -> + T E' | epsilon
```

Good. Now we must fix up the original `E` productions. Here, we take all of the right-hand sides that **didn't** start with `E`, and add `E'` to the end of them.

```
E  -> T E'
```

If we do this for the `T` productions as well, we get the following grammar:

```
E  -> T E'
E' -> + T E' | epsilon
T  -> F T'
T' -> * F T' | epsilon
F  -> (E) | int
```

Note, the F production didn't get changed at all. That's because `F` didn't appear on the leftmost position of any of the productions on the right-hand side of the arrow.

## [LL(1) parsing](https://en.wikipedia.org/wiki/LL_parser)

Once we have performed left-recursion elimination on our grammar, we need to construct our parser. We're going to use an algorithm called LL(1) parsing. This is an algorithm that utilizes a **lookup table** to parse an expression. On top, we list all of the **terminals**, and on the left, we list the **non-terminals** (we include `$` to signify end-of-file).

|      |  +   |  *   |  (   |  )   | int  |  $   |
| :--: | :--: | :--: | :--: | :--: | :--: | :--: |
|  E   |      |      |      |      |      |      |
|  E'  |      |      |      |      |      |      |
|  T   |      |      |      |      |      |      |
|  T'  |      |      |      |      |      |      |
|  F   |      |      |      |      |      |      |

Our LL(1) parser also contains a stack of **non-terminals**. Initially, we'll only put the starting state (`E`) on the stack. As we parse, we'll be putting non-terminals on and popping them off this stack. When they're all gone, and our stack is empty (and there is no more input), we're done.

At each step, there is a grammar symbol at the top of the stack. When we see an input token from the lexer, we look in the table to see what to do. Each cell in the table is going to tell our LL(1) parser what to do when it sees the terminal on the top when the non-terminal on the left is at the top of the stack.

Right now, our table is empty. Let's fill it up.

We do this by computing two functions called **FIRST** and **FOLLOW**.

### FIRST

**FIRST** is a function on each **non-terminal** (`E`, `E'`, `T`, `T'`, and `F`) that tells us which **terminals** (tokens from the lexer) can appear as the first part of one of these **non-terminals**. Epsilon (neither a terminal nor a non-terminal) may also be included in this **FIRST** function. (**FIRST** is also defined for terminals, but its value is just equal to the terminal itself, so we won't talk about it more.) What this means is that the parser is going to invoke some of these productions in the grammar. We need to know which one to pick when we see a particular token in the input stream.

> NOTE: To be predictive.

So, let's start computing. What is the **FIRST**(`E`)? What are the terminals that can appear at the beginning of the stream when we're looking for an `E`? Well, `E -> T E'`, so whatever occurs at the beginning of `E` will be the same as what happens at the beginning of `T`.

```
FIRST(E) => FIRST(T)
```

How about **FIRST**(`E'`)? This one is easy, we have the terminal `+`, and epsilon.

```
FIRST(E') = { +, epsilon }
```

And we'll continue with the others:

```
FIRST(T) => FIRST(F)
FIRST(T') = { *, epsilon }
FIRST(F) = { (, int }
```

See? **FIRST**(`F`) is just the set of terminals that are at the beginnings of its productions.

So, to sum up:

```
FIRST(E) = { (, int }
FIRST(E') = { +, epsilon }
FIRST(T) = { (, int }
FIRST(T') = { *, epsilon }
FIRST(F) = { (, int }
```

### FOLLOW

Now, let's do **FOLLOW**. Just as **FIRST** shows us the **terminals** that can be at the beginning of a derived non-terminal, **FOLLOW** shows us the **terminals** that can come *after* a derived non-terminal. Note, this does *not* mean the last terminal derived from a non-terminal. It's the set of terminals that can come after it. We define **FOLLOW** for all the **non-terminals** in the grammar.

How do we figure out **FOLLOW**? Instead of looking at the first terminal for each phrase on the right side of the arrow, we find every place our **non-terminal** is located on the right side of *any* of the arrows. Then we look for some **terminals**. As we go through our example, you'll see almost all of the different ways we figure out the **FOLLOW** of a non-terminal.

First, however, let's pretend that our grammar starts with a unique starting production (it's not really part of the grammar):

```
S  -> E
```

We start our journey at `S`, but rewrite it a bit to reflect the `EOF` that can be at the end. In parser-land, `EOF` is represented by `$`. So our production is really:

```
S -> E $
```

What is **FOLLOW**(`E`)? (Note: We don't really care about **FOLLOW**(`S`) because it's just imaginary.) Look on all of the right-hand sides (after the arrow) of all of the productions in the grammar. What terminals appear on the right of the `E`? Well, I see a `$` and `a` ).

```
FOLLOW(E) = { $, ) }
```

