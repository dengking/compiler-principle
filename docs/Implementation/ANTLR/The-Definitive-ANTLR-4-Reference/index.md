# The Definitive ANTLR 4 Reference

## Welcome Aboard!

From a **formal language description** called a ***grammar***, ANTLR generates a parser for that language that can automatically build **parse trees**, which are data structures representing how a **grammar** matches the input. ANTLR also automatically generates **tree walkers** that you can use to visit the nodes of those trees to execute application-specific code.

This book is both a reference for ANTLR v4 and a guide to using it to solve **language recognition problems**. You’re going to learn how to do the following:

- Identify **grammar patterns** in language samples and reference manuals in order to build your own grammars.

- Build **grammars** for simple languages like JSON all the way up to complex programming languages like R. You’ll also solve some tricky recognition problems from Python and XML.

- Implement language applications based upon those grammars by walking the automatically generated **parse trees**.

- Customize recognition error handling and error reporting for specific application domains.

- Take absolute control over parsing by embedding Java **actions** into a grammar.

## What’s So Cool About ANTLR V4?

### Adaptive LL(`*`)

The v4 release of ANTLR has some important new capabilities that reduce the learning curve and make developing grammars and language applications much easier. The most important new feature is that ANTLR v4 gladly accepts every grammar you give it (with one exception regarding **indirect left recursion**(间接左递归), described shortly). There are no grammar conflict or ambiguity warnings as ANTLR translates your grammar to executable, human-readable parsing code.

> 翻译: ANTLR v4 新增了多项核心能力，既降低了学习门槛，也让文法开发与语言类应用的构建变得更加简便。其中最重要的新特性是：ANTLR v4 可以兼容你给出的几乎所有文法（仅间接左递归除外，稍后会做说明）。在将文法转换为可执行、可读性良好的解析代码的过程中，不会产生任何文法冲突或歧义警告。

If you give your ANTLR-generated parser valid input, the parser will always recognize the input properly, no matter how complicated the grammar. Of course, it’s up to you to make sure the grammar accurately describes the language in question.

**ANTLR parsers** use a new parsing technology called Adaptive LL(`*`) or ALL(`*`) ("all star") that I developed with Sam Harwell.² ALL(`*`) is an extension to v3's LL(`*`) that performs grammar analysis dynamically at runtime rather than statically, before the generated parser executes. Because ALL(`*`) parsers have access to actual input sequences, they can always figure out how to recognize the sequences by appropriately weaving through the grammar. Static analysis, on the other hand, has to consider all possible (infinitely long) input sequences.

> 翻译: ANTLR 解析器采用了名为**自适应LL(`*`)（Adaptive LL(`*`)，简称ALL(`*`)，别称“全星”）**的新型解析技术，由我与萨姆·哈威尔（Sam Harwell）共同开发²。ALL(`*`) 是v3版本LL(`*`)算法的扩展：它不在生成的解析器执行前做静态文法分析，而是在**运行时动态完成文法分析**。 由于ALL(`*`)解析器可以读取实际输入序列，因此总能通过在文法中灵活回溯穿行，匹配出对应序列的识别路径。反观静态分析，则必须穷尽所有可能的（乃至无限长的）输入序列。

In practice, having ALL(`*`) means you don't have to contort your grammars to fit the underlying parsing strategy as you would with most other parser generator tools, including ANTLR v3. If you've ever pulled your hair out because of an ambiguity warning in ANTLR v3 or a reduce/reduce conflict in yacc, ANTLR v4 is for you!

> 翻译: 在实际开发中，得益于 ALL (`*`) 算法，你无需像使用 ANTLR v3 等绝大多数解析器生成工具那样，为了适配底层的解析策略而强行改写文法。如果你曾因为 ANTLR v3 的歧义警告、或是 yacc 的归约 - 归约冲突而焦头烂额，那 ANTLR v4 就是为你量身打造的！

### Simplify the grammar rules

The next awesome new feature is that ANTLR v4 dramatically simplifies the **grammar rules** used to match syntactic structures like programming language arithmetic expressions. **Expressions** have always been a hassle(麻烦事) to specify with ANTLR grammars (and to recognize by hand with **recursive-descent parsers**). The most natural grammar to recognize expressions is invalid for traditional top-down parser generators like ANTLR v3. Now, with v4, you can match expressions with rules that look like this:

> 翻译: 另一项出色的新特性是，ANTLR v4 大幅简化了文法规则的编写 —— 这类规则用于匹配程序语言算术表达式等各类句法结构。无论是用 ANTLR 文法定义表达式，还是手写递归下降解析器来识别表达式，历来都是一件棘手的事。对于 ANTLR v3 这类传统自顶向下解析器生成工具而言，用来识别表达式的最符合直觉的自然文法，是无法被支持的。而在 v4 版本中，你可以直接用如下形式的规则来匹配表达式：

```antlr
expr : expr '*' expr  // match subexpressions joined with '*' operator
     | expr '+' expr  // match subexpressions joined with '+' operator
     | INT            // matches simple integer atom
     ;
```

Self-referential rules like `expr` are recursive and, in particular, **left recursive** because at least one of its alternatives immediately refers to itself.

ANTLR v4 automatically rewrites **left-recursive rules** such as `expr` into **non-left-recursive** equivalents. The only constraint is that the left recursion must be **direct**, where rules immediately reference themselves. Rules cannot reference another rule on the left side of an alternative that eventually comes back to reference the original rule without matching a token. See Section 5.4, *Dealing with Precedence, Left Recursion, and Associativity*, on page 69 for more details.

> 翻译: 唯一的限制是：左递归必须是**直接左递归**，即规则在候选分支的起始位置直接引用自身。若规则在候选分支的最左侧引用了另一条非终结符规则，且该规则后续不经任何终结符匹配，最终又绕回引用原始规则，则这类规则无法被处理。
> 
> 补充说明：这句话明确了 ANTLR v4 仅支持直接左递归的自动改写，**不支持间接左递归**，也就是前文提到的「唯一例外」的具体含义。

ANTLR v4 is exactly what I want in a **parser generator**, so I can finally get back to the problem I was originally trying to solve in the 1980s. Now, if I could just remember what that was.


