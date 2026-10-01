# CHAPTER 4 A Quick Tour

So far, we have learned how to install ANTLR and have looked at the key processes, terminology, and building blocks needed to build a language application. In this chapter, we’re going to take a whirlwind tour of ANTLR by racing through a number of examples that illustrate its capabilities. We’ll be glossing over a lot of details in the interest of brevity(简洁), so don’t worry if things aren’t crystal clear. The goal is just to get a feel for what you can do with ANTLR. We’ll look underneath the hood starting in Chapter 5, *Designing Grammars*, on page 57. For those with experience using previous versions of ANTLR, this chapter is a great way to retool.

> 翻译: 到目前为止，我们已经学习了如何安装 ANTLR，并且了解了构建语言应用所需的核心流程、术语与基础组件。本章将快速概览 ANTLR，通过多个示例来展示它的各项能力。为保证行文简洁，很多细节会一笔带过，所以如果有些内容不是完全理解也无需担心。本章目标只是让你直观感受 ANTLR 能做什么。从第 5 章《设计文法》（57 页）开始，我们再深入探究底层原理。如果你之前使用过旧版 ANTLR，本章也非常适合用来更新知识体系。

This chapter is broken down into four broad topics that nicely illustrate the feature set. It’s a good idea to download the code¹ for this book (or follow the links in the ebook version) and work through the examples as we go along. That way, you’ll get used to working with grammar files and building ANTLR applications. Keep in mind that many of the code snippets you see interspersed in the text aren’t complete files so that we can focus on the interesting bits.

> 翻译: 本章分为四大主题，充分展示 ANTLR 的功能集。建议下载本书配套源码 ¹（或在电子书里点击链接），跟着动手跑一遍示例。这样你就能熟悉文法文件的编写以及 ANTLR 应用的构建流程。请注意：文中穿插的大量代码片段并不是完整文件，目的是让我们聚焦核心内容。

First, we’re going to work with a grammar for a simple **arithmetic expression language**. We’ll test it initially using ANTLR’s built-in test rig and then learn more about the boilerplate main program that launches parsers shown in Section 3.3, *Integrating a Generated Parser into a Java Program*, on page 26. Then, we’ll look at a nontrivial **parse tree** for the **expression grammar**. (Recall that a parse tree records how a parser matches an input phrase.) For dealing with very large grammars, we’ll see how to split a grammar into manageable chunks using **grammar** imports. Next, we’ll check out how ANTLR-generated parsers respond to invalid input.

> 翻译: 首先，我们将编写一套简单算术表达式语言的文法。先用 ANTLR 内置的测试工具测试文法，之后进一步学习 3.3 节（26 页）介绍的、用于启动语法分析器的样板主程序。然后，我们观察表达式文法对应的复杂语法树。（回顾：语法树记录语法分析器匹配输入短语的全过程。）针对超大型文法，我们会学习如何通过文法导入，将文法拆分为多个便于维护的模块。接下来，我们看一看 ANTLR 生成的语法分析器如何处理非法输入。

Second, after looking at the parser for arithmetic expressions, we’ll use a visitor pattern to build a calculator that walks expression grammar parse trees. ANTLR parsers automatically generate visitor interfaces and blank method implementations so we can get started painlessly.

> 翻译: 第二，在学习算术表达式语法分析器之后，我们将使用**访问者模式**构建一个计算器，遍历表达式文法的语法树。ANTLR 语法分析器会自动生成访问者接口与空方法实现，让我们可以轻松上手。

Third, we’ll build a translator that reads in a Java class definition and spits out a Java interface derived from the methods in that class. Our implementation will use the tree listener mechanism that ANTLR also generates automatically.

> 翻译: 第三，我们构建一个转换器：读取 Java 类定义，然后根据该类中的方法，输出对应的 Java 接口。实现将使用 ANTLR 自动生成的语法树监听器机制。

Fourth, we’ll learn how to embed actions (arbitrary code) directly in the grammar. Most of the time, we can build language applications with visitors or listeners, but for the ultimate flexibility, ANTLR allows us to inject our own application-specific code into the generated parser. These actions execute during the parse and can collect information or generate output like any other arbitrary code snippets. In conjunction with **semantic predicates** (Boolean expressions), we can even make parts of our grammar disappear at runtime! For example, we might want to turn the enum keyword on and off in a Java grammar to parse different versions of the language. Without semantic predicates, we’d need two different versions of the grammar.

> 翻译: 第四，我们学习如何在文法中直接嵌入**动作（自定义代码）**。大多数场景下，我们用访问者或监听器就能构建语言应用；但如果需要最大灵活性，ANTLR 支持向生成的语法分析器注入业务自定义代码。这些动作会在语法分析阶段执行，可以收集信息、生成输出，和普通代码片段一样。配合**语义谓词（布尔表达式）**，我们甚至能在运行时让文法的部分规则 “失效”！例如，在 Java 文法中，可以动态启用 / 禁用`enum`关键字，以此解析不同版本的 Java 语言。如果没有语义谓词，我们就需要维护两套不同的文法。

Finally, we’ll zoom in on a few ANTLR features at the lexical (token) level. We’ll see how ANTLR deals with input files that contain more than one language. Then we’ll look at the awesome `TokenStreamRewriter` class that lets us tweak, mangle, or otherwise manipulate token streams, all without disturbing the original input stream. Finally, we’ll revisit our interface generator example to learn how ANTLR can ignore whitespace and comments during Java parsing but retain them for later processing.

> 翻译: 最后，我们聚焦词法（token）层面的若干 ANTLR 特性。我们会看到 ANTLR 如何处理包含多种语言的输入文件。然后介绍强大的`TokenStreamRewriter`类，它可以修改、调整、操作 token 流，**不会改动原始输入流**。最后，我们重新回顾接口生成器示例，学习 ANTLR 在解析 Java 代码时，可以跳过空格与注释，同时保留这些内容供后续处理。

Let’s begin our tour by getting acquainted with ANTLR grammar notation.
Make sure you have the `antlr4` and `grun` aliases or scripts defined, as explained in Section 1.2, *Executing ANTLR and Testing Recognizers*, on page 6.

# 4.1 Matching an Arithmetic Expression Language

For our first grammar, we’re going to build a simple calculator. Doing something with expressions makes sense because they’re so common. To keep things simple, we’ll allow only the basic **arithmetic operators** (add, subtract, multiply, and divide), parenthesized expressions, integer numbers, and variables. We’ll also restrict ourselves to integers instead of allowing floating-point numbers.

Here’s some sample input that illustrates all language features:

```markdown
tour/t.expr
```

```
193
a = 5
b = 6
a+b*2
(1+2)*3
```

In English, a program in our expression language is a sequence of statements terminated by newlines. A statement is either an expression, an assignment, or a blank line. Here’s an ANTLR grammar that’ll parse those statements and expressions for us:

> tour/Expr.g4

```antlr
grammar Expr;

/** The start rule; begin parsing here. */
prog: stat+ ;

stat: expr NEWLINE
    | ID '=' expr NEWLINE
    | NEWLINE
    ;

expr: expr ( '*'|'/' ) expr
    | expr ( '+'|'-' ) expr
    | INT
    | ID
    | '(' expr ')'
    ;

ID  : [a-zA-Z]+ ;      // match identifiers
INT : [0-9]+ ;         // match integers
NEWLINE: '\r'? '\n' ; // return newlines to parser (is end-statement signal)
WS  : [ \t]+ -> skip ; // toss out whitespace
```

Without going into too much detail, let’s look at some of the key elements of ANTLR’s grammar notation.

- Grammars consist of a set of rules that describe language syntax. There are rules for syntactic structure like `stat` and `expr` as well as rules for vocabulary symbols (tokens) such as identifiers and integers.
- Rules starting with a **lowercase letter** comprise the **parser rules**.
- Rules starting with an **uppercase letter** comprise the **lexical (token) rules**.
- We separate the alternatives of a rule with the `|` operator, and we can group symbols with parentheses into **subrules**. For example, **subrule** `('*'|'/')` matches either a multiplication symbol or a division symbol.

We’ll tackle all of this stuff in detail when we get to Chapter 5, *Designing Grammars*, on page 57.



One of ANTLR v4’s most significant new features is its ability to handle (most kinds of) **left-recursive rules**. A **left-recursive rule** is one that invokes itself at the start of an alternative. For example, in this grammar, rule `expr` has alternatives on lines 11 and 12 that recursively invoke `expr` on the left edge. Specifying arithmetic expression notation this way is dramatically easier than what we’d need for the typical **top-down parser** strategy. In that strategy, we’d need multiple rules, one for each operator precedence level. For more on this feature, see Section 5.4, *Dealing with Precedence, Left Recursion, and Associativity*, on page 69.

> 翻译: ANTLR v4最重要的新特性之一，就是**可以处理大多数类型的左递归规则**。左递归规则指：在某个候选分支的开头调用自身。例如在本文的文法中，`expr`规则第11、12行的分支，就在最左侧递归调用`expr`。
> 用这种方式定义算术表达式，远比传统自顶向下语法分析方案简单得多。传统方案中，需要为每一级运算符优先级单独写一条规则。更多相关内容，参见5.4节《处理优先级、左递归与结合性》（69页）。



The notation for the token definitions should be familiar to those with regular expression experience. We’ll look at lots of lexical (token) rules in Chapter 6, *Exploring Some Real Grammars*, on page 83. The only unusual syntax is the `-> skip` operation on the WS whitespace rule. It’s a **directive**(指令) that tells the lexer to match but throw out whitespace. (Every possible input character must be matched by at least one **lexical rule**.) We avoid tying the grammar to a specific target language by using formal ANTLR notation instead of an arbitrary code snippet in the grammar that tells the lexer to skip.

> 翻译: 有正则表达式基础的读者，对token定义的这套语法会比较熟悉。第6章《探究真实文法》（83页）会介绍大量词法（token）规则。唯一特殊的语法是空白符规则WS里的`-> skip`操作。这是一条指令，告诉词法分析器：匹配空白字符但是直接丢弃。（输入里所有字符，都必须至少能被一条词法规则匹配。）
> 我们使用标准ANTLR语法，而不是在文法里嵌入任意代码片段来通知词法分析器跳过字符，这样可以避免文法绑定到某一门目标编程语言。

OK, let’s take grammar `Expr` out for a joy ride. Download the `tour/Expr.g4` link on the previous code listing, if you’re viewing the ebook version, or by cutting and pasting the grammar into a file called `Expr.g4`.

> 翻译: 好了，让我们动手跑一遍Expr文法。如果你在读电子书，可以点击上一段代码清单里的`tour/Expr.g4`链接下载源码；也可以直接复制文法，保存为`Expr.g4`文件。

The easiest way to test grammars is with the built-in TestRig, which we can access using alias `grun`. For example, here is the build and test sequence on a Unix box:

```shell
$ antlr4 Expr.g4
$ ls Expr*.java
ExprBaseListener.java  ExprListener.java
ExprLexer.java         ExprParser.java
$ javac Expr*.java
$ grun Expr prog -gui t.expr # launches org.antlr.v4.runtime.misc.TestRig
```

Because of the `-gui` option, the test rig pops up a window showing the parse tree, as shown in Figure 2, *Window showing the parse tree*, on page 35.

The parse tree is analogous to the function call tree our parser would trace as it recognizes input. (ANTLR generates a function for each rule.)

It’s OK to develop and test grammars using the test rig, but ultimately we’ll need to integrate our ANTLR-generated parser into an application. The main program given below shows the code necessary to create all necessary objects and launch our expression language parser starting at rule prog:

> 翻译: 加上`-gui`参数后，测试工具会弹出窗口展示语法树，详见图2《语法树展示窗口》（35页）。
> 
> 语法树，类似于语法分析器识别输入时产生的函数调用树。（ANTLR会为每一条规则生成一个对应的函数。）可以使用TestRig开发、测试文法，但最终我们还是要把ANTLR生成的语法分析器集成到应用程序中。




