# Lookahead(向前看符号)

lookahead: 向前看符号 / 前瞻符号，分析决策时提前读取、暂不消耗的输入记号

Lookahead establishes(定义) the maximum incoming tokens that a **parser** can use to decide which rule(production) it should use. Lookahead is especially relevant to [LL](https://en.wikipedia.org/wiki/LL_parser), [LR](https://en.wikipedia.org/wiki/LR_parser "LR parser"), and [LALR parsers](https://en.wikipedia.org/wiki/LALR_parser "LALR parser"), where it is often explicitly indicated(标注) by affixing the lookahead to the algorithm name in parentheses, such as LALR(1).

> 翻译: 向前看符号（lookahead）定义了语法分析器在判定应当选用哪条规则时，最多可提前查看的输入记号数量。这一概念与**LL 语法分析器**、**LR 语法分析器**、**LALR 语法分析器**的关联尤为密切：在这类分析器的命名规范中，通常会将向前看符号的数量标注在算法名称后的括号里以明确标识，例如 LALR (1)。

Most [programming languages](https://en.wikipedia.org/wiki/Programming_language "Programming language"), the primary target of parsers, are carefully defined in such a way that a parser with limited lookahead, typically one, can parse them, because parsers with limited lookahead are often more efficient. One important change to this trend came in 1990 when [Terence Parr](https://en.wikipedia.org/wiki/Terence_Parr "Terence Parr") created [ANTLR](https://en.wikipedia.org/wiki/ANTLR "ANTLR") for his Ph.D. thesis, a [parser generator](https://en.wikipedia.org/wiki/Parser_generator "Parser generator") for efficient LL(*k*) parsers, where *k* is any fixed value.

> 翻译: 大多数**编程语言**作为语法分析器的主要处理对象，在设计时都会经过严谨的定义，使得仅配备有限向前看符号（通常为 1 个）的语法分析器即可完成对它们的语法解析，因为有限前瞻的语法分析器通常运行效率更高。
> 
> 这一趋势在 1990 年出现了一项重要突破：特伦斯・帕尔（Terence Parr）在其博士论文中研发出了**ANTLR**，这是一款可高效生成 LL (k) 语法分析器的**语法分析器生成工具**，其中的 *k* 可取任意固定值。

**LR parsers** typically have only a few actions after seeing each token. They are shift (add this token to the stack for later reduction), reduce (pop tokens from the stack and form a syntactic construct), end, error (no known rule applies) or conflict (does not know whether to shift or reduce).

> 翻译: LR 语法分析器每读入一个输入记号后，通常仅有少数几种可选动作，分别是：**移进**（将当前记号压入栈中，留待后续归约）、**归约**（从栈中弹出对应符号串，将其组合为一个语法结构）、**接受**（分析成功结束）、**报错**（无适用的文法规则），以及**冲突**（无法判定应当移进还是归约）。


