# 现代编译器前端的"万能锤"：递归下降 + Pratt 解析

如果只能选一种技术打天下，业界的共识基本是：**手写递归下降解析器，表达式部分用 Pratt 解析（运算符优先级爬升）**。GCC、Clang、Go、Rust（rustc）、V8、TypeScript、Swift 等主流编译器的前端都是这样手写的，而不是用 yacc/bison 生成。

---

## 为什么是它？

| 优势 | 说明 |
|---|---|
| **直观** | 一个语法规则对应一个函数，代码结构就是文法结构 |
| **无需工具链** | 不依赖生成器，调试就是普通的函数调用栈 |
| **错误信息好** | 可以在任意位置定制报错和错误恢复（这是 LR 生成器的最大痛点） |
| **灵活** | 能轻松处理上下文相关的"脏"语法（如 C++ 的模板尖括号、JS 的 ASI） |
| **够用** | 加上回溯或多看几个 token，几乎能解析所有实际语言 |

递归下降唯一的软肋是**表达式**：左递归和优先级层级会导致函数爆炸（`parseOr → parseAnd → parseEq → parseCmp → parseAdd → parseMul → ...`）。**Pratt 解析**正好补上这块短板。

---

## 核心：Pratt 解析器

思想很简单：每个运算符有一个**绑定力（binding power）**，循环吃掉绑定力比当前更强的运算符。

```python
# 绑定力：(左, 右)。左 < 右 表示左结合，左 > 右 表示右结合
INFIX = {
    '=': (2, 1),               # 右结合
    '+': (10, 11), '-': (10, 11),
    '*': (20, 21), '/': (20, 21),
    '^': (31, 30),             # 右结合
}
PREFIX = {'-': 25, '!': 25}
POSTFIX = {'!': 40, '[': 40, '(': 40}

def parse_expr(lexer, min_bp=0):
    tok = lexer.next()

    # 1. 前缀 / 原子 (nud)
    if tok.kind in ('num', 'ident'):
        lhs = tok
    elif tok.text == '(':
        lhs = parse_expr(lexer, 0)
        lexer.expect(')')
    elif tok.text in PREFIX:
        rhs = parse_expr(lexer, PREFIX[tok.text])
        lhs = ('unary', tok.text, rhs)
    else:
        raise SyntaxError(f"意外的 token: {tok}")

    # 2. 中缀 / 后缀循环 (led)
    while True:
        op = lexer.peek()
        if op.text in POSTFIX:
            if POSTFIX[op.text] < min_bp: break
            lexer.next()
            if op.text == '[':
                idx = parse_expr(lexer, 0); lexer.expect(']')
                lhs = ('index', lhs, idx)
            elif op.text == '(':
                args = parse_args(lexer)
                lhs = ('call', lhs, args)
            else:
                lhs = ('postfix', op.text, lhs)
            continue

        if op.text in INFIX:
            l_bp, r_bp = INFIX[op.text]
            if l_bp < min_bp: break
            lexer.next()
            rhs = parse_expr(lexer, r_bp)
            lhs = ('binary', op.text, lhs, rhs)
            continue

        break
    return lhs
```

**几十行代码**搞定前缀、中缀、后缀、左/右结合、函数调用、下标，加新运算符只需改表。

---

## 完整的"万能锤"套装

```
源码 ──► 词法分析 ──► 语法分析 ──► AST ──► 语义分析
         手写状态机    递归下降        Visitor/模式匹配
                      + Pratt
```

1. **词法分析**：手写 `switch` 状态机，不用正则或 lex。记录行列号以便报错。
2. **语句/声明**：递归下降，`parseStatement()` 根据首 token 分派到 `parseIf()`、`parseWhile()`、`parseFn()`……
3. **表达式**：Pratt。
4. **错误恢复**：遇错后跳到"同步点"（`;`、`}`、关键字）继续解析，一次报出多个错误。
5. **AST**：用代数数据类型 / tagged union 表示，后续阶段用模式匹配或 Visitor 遍历。

---

## 什么时候不用这把锤子？

- **快速原型 / DSL**：用 ANTLR、parser combinator（如 Haskell 的 Parsec、Rust 的 nom/chumsky）更快
- **编辑器语法高亮 / 增量解析**：tree-sitter
- **需要形式化保证文法无歧义**：LR 生成器（bison、menhir）能在编译期检测冲突

---

## 推荐阅读

- **Bob Nystrom《Crafting Interpreters》**（免费在线）——递归下降 + Pratt 的最佳入门
- **Vaughan Pratt, "Top Down Operator Precedence" (1973)**——原始论文
- **matklad, "Simple but Powerful Pratt Parsing"**——rust-analyzer 作者的经典博客文章

一句话总结：**递归下降管结构，Pratt 管表达式，手写词法器打底**——这就是编译器前端的万能锤。