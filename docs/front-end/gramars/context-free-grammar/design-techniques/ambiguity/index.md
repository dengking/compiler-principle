# 二义性

一份文法若能为同一个句子给出两棵不同的树,就是**二义的(ambiguous)**。二义性本身不是语法错误,而是"同一形状有多种含义"——这又一次说明语法与语义的纠缠。

消除二义有两条路:

1. **改写文法**:像 E-T-F 那样分层,让多余的树无法推导;
2. **外挂消歧规则(disambiguating rules)**:文法保持二义,另加规则选择其中一棵。yacc 的 `%left` / `%right` / `%prec`、dangling else 的"就近匹配"(else 与最近的未匹配 if 结合)都属此类。

## examples

结合性的歧义: [[single-list|一个常见的错误写法：歧义]] 

### C++ most vexing parse
C++ 的 **most vexing parse** 是消歧规则的极端例子:

```cpp
Widget w(Thing());   // 变量定义?还是函数声明?
```

规则是"只要能解释成声明,就解释成声明"——消歧规则本身就是语法与语义混合的产物。