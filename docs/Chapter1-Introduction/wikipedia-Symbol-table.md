# [Symbol table](https://en.wikipedia.org/wiki/Symbol_table)

In [computer science](https://en.wikipedia.org/wiki/Computer_science), a **symbol table** is a [data structure](https://en.wikipedia.org/wiki/Data_structure) used by a language [translator](https://en.wikipedia.org/wiki/Translator) such as a [compiler](https://en.wikipedia.org/wiki/Compiler) or [interpreter](https://en.wikipedia.org/wiki/Interpreter_(computing)), where each [identifier](https://en.wikipedia.org/wiki/Identifier) (a.k.a. [symbol](https://en.wikipedia.org/wiki/Symbol_(programming))) in a program's [source code](https://en.wikipedia.org/wiki/Source_code) is associated with information relating to its declaration or appearance in the source. In other words, the entries of a symbol table store the information related to the entry's corresponding symbol.

## Background

A symbol table may only exist in memory during the translation process, or it may be embedded in the output of the translation, such as in an [ABI](https://en.wikipedia.org/wiki/Application_binary_interface) [object file](https://en.wikipedia.org/wiki/Object_file) for later use. For example, it might be used during an interactive [debugging session](https://en.wikipedia.org/wiki/Debugger), or as a resource for formatting a diagnostic report during or after [execution](https://en.wikipedia.org/wiki/Execution_(computers)) of a program.[[1\]](https://en.wikipedia.org/wiki/Symbol_table#cite_note-1)

## Description

The minimum information contained in a symbol table used by a translator includes the symbol's name, its relocatability attributes (absolute, relocatable, etc.), and its location or address. For relocatable symbols, some relocation information must be stored. Symbol tables for [high-level programming languages](https://en.wikipedia.org/wiki/High-level_programming_language) store the symbol's type: string, integer, floating-point, etc., its size, and its dimensions and its bounds. Not all of this information is included in the output file, but may be provided for use in [debugging](https://en.wikipedia.org/wiki/Debugging). In many cases, the symbol's [cross-reference](https://en.wikipedia.org/wiki/Cross-reference) information is stored with or linked to the symbol table. Most compilers print some or all of this information in symbol table and cross-reference listings at the end of translation.

## Implementation

Numerous [data structures](https://en.wikipedia.org/wiki/Data_structure) are available for implementing tables. Trees, linear lists and [self-organizing lists](https://en.wikipedia.org/wiki/Self-organizing_list) can all be used to implement a symbol table. The symbol table is accessed by most phases of a compiler, beginning with [lexical analysis](https://en.wikipedia.org/wiki/Lexical_analysis), and continuing through optimization.

A compiler may use one large symbol table for all symbols or use separated, hierarchical symbol tables for different [scopes](https://en.wikipedia.org/wiki/Scope_(programming)). For example, in a scoped language such as [Algol](https://en.wikipedia.org/wiki/ALGOL) or [PL/I](https://en.wikipedia.org/wiki/PL/I) a symbol "p" can be declared separately in several procedures, perhaps with different attributes. The scope of each declaration is the section of the program in which references to "p" resolve to that declaration. Each declaration represents a unique identifier "p". The symbol table must have some means of differentiating references to the different "p"s.

A common data structure used to implement symbol tables is the [hash table](https://en.wikipedia.org/wiki/Hash_table). The time for searching in hash tables is independent of the number of elements stored in the table, so it is efficient for a large number of elements. It also simplifies[*[how?](https://en.wikipedia.org/wiki/Wikipedia:Please_clarify)*] the classification of literals in tabular format.

As the lexical analyser spends a great proportion of its time looking up the symbol table, this activity has a crucial effect on the overall speed of the compiler. A symbol table must be organised in such a way that entries can be found as quickly as possible. **Hash tables** are usually used to organise a symbol table, where the keyword or identifier is 'hashed' to produce an array subscript. Collisions are inevitable in a hash table, and a common way of handling them is to store the synonym in the next available free space in the table.

> NOTE: 如果使用hash table的话，那么symbol table如何实现区分？

## Applications

An [object file](https://en.wikipedia.org/wiki/Object_file) will contain a symbol table of the identifiers it contains that are **externally visible**. During the linking of different object files, a [linker](https://en.wikipedia.org/wiki/Linker_(computing)) will identify and resolve these symbol references. Usually all **undefined external symbols** will be searched for in one or more [object libraries](https://en.wikipedia.org/wiki/Library_(computing)). If a module is found that defines that symbol it is linked with together with the first object file, and any **undefined external identifiers** are added to the list of identifiers to be looked up. This process continues until all external references have been resolved. It is an error if one or more remains unresolved at the end of the process.

While [reverse engineering](https://en.wikipedia.org/wiki/Reverse_engineering) an executable, many tools refer to the symbol table to check what addresses have been assigned to global variables and known functions. If the symbol table has been [stripped](https://en.wikipedia.org/wiki/Strip_(Unix)) or cleaned out before being converted into an executable, tools will find it harder to determine addresses or understand anything about the program.

## Example

Consider the following program written in [C](https://en.wikipedia.org/wiki/C_(programming_language)):

```c
// Declare an external function
extern double bar(double x);

// Define a public function
double foo(int count)
{
    double sum = 0.0;

    // Sum all the values bar(1) to bar(count)
    for (int i = 1; i <= count; i++)
        sum += bar((double) i);
    return sum;
}
```

A C compiler that parses this code will contain at least the following symbol table entries:

| Symbol name |       Type       |       Scope        |
| :---------: | :--------------: | :----------------: |
|    `bar`    | function, double |       extern       |
|     `x`     |      double      | function parameter |
|    `foo`    | function, double |       global       |
|   `count`   |       int        | function parameter |
|    `sum`    |      double      |    block local     |
|     `i`     |       int        | for-loop statement |

In addition, the symbol table will also contain entries generated by the compiler for intermediate expression values (e.g., the expression that casts the `i` loop variable into a `double`, and the return value of the call to function `bar()`), statement labels, and so forth.

## Example: SysV ABI

An example of a symbol table can be found in the [SysV](https://en.wikipedia.org/wiki/SysV) [Application Binary Interface](https://en.wikipedia.org/wiki/Application_Binary_Interface) (ABI) specification, which mandates how [symbols](https://en.wikipedia.org/wiki/Symbol_(programming)) are to be laid out in a binary file, so that different compilers, linkers and loaders can all consistently find and work with the symbols in a compiled object.

The SysV ABI is implemented in the [GNU binutils'](https://en.wikipedia.org/wiki/GNU_Binary_Utilities) [nm](https://en.wikipedia.org/wiki/Nm_(Unix)) utility. This format uses a sorted [memory address](https://en.wikipedia.org/wiki/Memory_address) field, a "[The symbol type](http://sourceware.org/binutils/docs-2.17/binutils/nm.html#nm)" field, and a symbol identifier (called "Name").

One entry is a data symbol, denoted by the type "D". Many functions, including both user-defined functions and library functions are also present.[*[further explanation needed](https://en.wikipedia.org/wiki/Wikipedia:Please_clarify)*]

## Example: the Python symbol table

The [Python](https://en.wikipedia.org/wiki/Python_(programming_language)) programming language includes extensive support for creating and manipulating symbol tables.[[2\]](https://en.wikipedia.org/wiki/Symbol_table#cite_note-2) Properties that can be queried include whether a given symbol is a [free variable](https://en.wikipedia.org/wiki/Free_variable) or a [bound variable](https://en.wikipedia.org/wiki/Bound_variable), whether it is [block scope](https://en.wikipedia.org/wiki/Block_scope) or [global scope](https://en.wikipedia.org/wiki/Global_scope), whether it is imported, and what [namespace](https://en.wikipedia.org/wiki/Namespace) it belongs to.

## Example: Dynamic symbol tables

Some programming languages allow the **symbol table** to be manipulated at run-time, so that symbols can be added at any time. [Racket](https://en.wikipedia.org/wiki/Racket_(programming_language)) is an example of such a language[[3\]](https://en.wikipedia.org/wiki/Symbol_table#cite_note-3).

Both the [LISP](https://en.wikipedia.org/wiki/LISP) and the [Scheme](https://en.wikipedia.org/wiki/Scheme_(programming_language)) programming languages allow arbitrary, generic properties to be associated with each symbol.[[4\]](https://en.wikipedia.org/wiki/Symbol_table#cite_note-4)

The [Prolog](https://en.wikipedia.org/wiki/Prolog) programming language is essentially a symbol-table manipulation language; symbols are called *atoms*, and the relationships between symbols can be reasoned over. Similarly, [OpenCog](https://en.wikipedia.org/wiki/OpenCog) provides a dynamic symbol table, called the *atomspace*, which is used for [knowledge representation](https://en.wikipedia.org/wiki/Knowledge_representation).

