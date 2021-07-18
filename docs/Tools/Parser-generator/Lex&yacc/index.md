# Lex & Yacc 



## compilertools [The Lex & Yacc Page](http://dinosaur.compilertools.net/)



## wikipedia [Lex (software)](https://en.wikipedia.org/wiki/Lex_(software))

**Lex** is a [computer program](https://en.wikipedia.org/wiki/Computer_program) that generates [lexical analyzers](https://en.wikipedia.org/wiki/Lexical_analysis) ("scanners" or "lexers").[[1\]](https://en.wikipedia.org/wiki/Lex_(software)#cite_note-1)[[2\]](https://en.wikipedia.org/wiki/Lex_(software)#cite_note-2)

Lex is commonly used with the [yacc](https://en.wikipedia.org/wiki/Yacc) [parser generator](https://en.wikipedia.org/wiki/Parser_generator). Lex, originally written by [Mike Lesk](https://en.wikipedia.org/wiki/Mike_Lesk) and [Eric Schmidt](https://en.wikipedia.org/wiki/Eric_Schmidt)[[3\]](https://en.wikipedia.org/wiki/Lex_(software)#cite_note-3) and described in 1975,[[4\]](https://en.wikipedia.org/wiki/Lex_(software)#cite_note-4)[[5\]](https://en.wikipedia.org/wiki/Lex_(software)#cite_note-5) is the standard [lexical analyzer](https://en.wikipedia.org/wiki/Lexical_analyzer) generator on many [Unix](https://en.wikipedia.org/wiki/Unix) systems, and an equivalent tool is specified as part of the [POSIX](https://en.wikipedia.org/wiki/POSIX) standard.[*citation needed*]

Lex reads an input [stream](https://en.wikipedia.org/wiki/Stream_(computing)) specifying the lexical analyzer and outputs [source code](https://en.wikipedia.org/wiki/Source_code) implementing the lexer in the [C programming language](https://en.wikipedia.org/wiki/C_(programming_language)). In addition to C, some old versions of Lex could also generate a lexer in [Ratfor](https://en.wikipedia.org/wiki/Ratfor).[[6\]](https://en.wikipedia.org/wiki/Lex_(software)#cite_note-6)



### Open source

Though originally distributed as proprietary software, some versions of Lex are now [open source](https://en.wikipedia.org/wiki/Open-source_software). Open source versions of Lex, based on the original AT&T code are now distributed as a part of open source operating systems such as [OpenSolaris](https://en.wikipedia.org/wiki/OpenSolaris) and [Plan 9 from Bell Labs](https://en.wikipedia.org/wiki/Plan_9_from_Bell_Labs).[*clarification needed*] One popular open source version of Lex, called [flex](https://en.wikipedia.org/wiki/Flex_lexical_analyser), or the "fast lexical analyzer", is not derived from proprietary coding.



### Structure of a Lex file

The structure of a Lex file is intentionally similar to that of a yacc file; files are divided into three sections, separated by lines that contain only two percent signs, as follows

1、The **definition** section defines [macros](https://en.wikipedia.org/wiki/Macro_(computer_science)) and imports [header files](https://en.wikipedia.org/wiki/Header_file) written in [C](https://en.wikipedia.org/wiki/C_(programming_language)). It is also possible to write any C code here, which will be copied verbatim into the generated source file.

2、The **rules** section associates [regular expression](https://en.wikipedia.org/wiki/Regular_expression) patterns with C [statements](https://en.wikipedia.org/wiki/Statement_(programming)). When the lexer sees text in the input matching a given pattern, it will execute the associated C code.

3、The **C code** section contains C statements and [functions](https://en.wikipedia.org/wiki/Function_(programming)) that are copied verbatim to the generated source file. These statements presumably contain code called by the rules in the rules section. In large programs it is more convenient to place this code in a separate file linked in at [compile](https://en.wikipedia.org/wiki/Compiler) time.

