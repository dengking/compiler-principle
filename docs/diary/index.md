# TODO

## 20191231

### symbol table and AST

在[Abstract syntax tree](https://en.wikipedia.org/wiki/Abstract_syntax_tree)中有这样的描述：

> The compiler also generates [symbol tables](https://en.wikipedia.org/wiki/Symbol_table) based on the AST during semantic analysis.

我的疑惑是：symbol table到底是由谁创建的？记得上周末的时候，还在看python的symbol table的实现。所以，有必要对symbol table做一次专题的分析。





## how to write grammar

Expression grammar (4.1) 描述了如何实现precedence、associativity



4.2.5 描述了如何消除语法中的歧义



增加indirection、中间变量、增加层次、增加hierarchy



## epsilon的妙用

在regex、cfg中都用epsilon。