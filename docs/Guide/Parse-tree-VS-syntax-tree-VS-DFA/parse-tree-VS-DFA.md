# parse tree VS DFA

在cpython的`pgen`中，使用DFA来表示production的body，这是因为python的grammar所使用的是EBNF，其中扩展了对regular expression的支持。

在[Natural Language Processing with Python](http://www.nltk.org/book/)的[8. Analyzing Sentence Structure](http://www.nltk.org/book/ch08.html)中给我们演示了定义CFG，并按照这个CFG来对文本进行解析得到parse tree。那在nltk中是如何来表示它的grammar的呢？nltk的parser是如何运用它的grammar的来实现parse的呢？

