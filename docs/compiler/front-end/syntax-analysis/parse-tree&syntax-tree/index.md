# Parse tree、syntax tree

parse tree和syntax tree在本书中多次出现，有必要对它们进行对比一下。



介绍parse tree的主要章节有：

一、2.2.3 Parse Trees

二、2.4 Parsing

三、2.9 Summary of Chapter 2

四、Chapter 4 Syntax Analysis

五、Chapter 5 Syntax-Directed Translation



介绍syntax tree的章节有：

一、2.1 Introduction

二、2.8.2 Construction of Syntax Trees

三、2.8.4 Three-Address Code

四、5.3.1 Construction of Syntax Trees

五、6.1 Variants of Syntax Trees



## TODO

### Parse tree VS DFA

在cpython的`pgen`中，使用DFA来表示production的body，这是因为python的grammar所使用的是EBNF，其中扩展了对regular expression的支持。

在[Natural Language Processing with Python](http://www.nltk.org/book/)的[8. Analyzing Sentence Structure](http://www.nltk.org/book/ch08.html)中给我们演示了定义CFG，并按照这个CFG来对文本进行解析得到parse tree。那在nltk中是如何来表示它的grammar的呢？nltk的parser是如何运用它的grammar的来实现parse的呢？

