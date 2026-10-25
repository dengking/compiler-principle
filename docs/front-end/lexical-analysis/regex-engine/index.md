# 正则表达式引擎实现技术报告

## 从三十行回溯到工业级混合引擎：兼论 lex/flex、re2c、ANTLR、RE2、Rust regex、Go、PCRE2、Java、.NET、V8、Python、Hyperscan 的实现

---

### 摘要

本报告系统讲解正则表达式引擎的实现原理与工程实践，按由易到难的顺序展开：

1. 先实现一个约 100 行的**回溯引擎**，弄清“正则匹配到底在做什么”，并亲手观察**灾难性回溯**；
2. 再引入 **Thompson 构造**与 **Pike VM**，获得与模式无关的线性时间保证，同时保留捕获组；
3. 进入 **DFA** 世界：子集构造、字符等价类、最小化（Moore / Hopcroft）、惰性 DFA；以及不经过 ε-NFA 的**直接构造**（followpos、Glushkov、Brzozowski 导数）；
4. 转向“编译器里的正则引擎”：**词法分析器生成器**（lex/flex、re2c）、主流编译器的**手写词法器**，以及 **ANTLR 4** 在运行时模拟 ATN、增量缓存 DFA 的做法（词法器与 ALL(\*) 预测）；
5. 最后剖析工业引擎的**混合架构**（RE2、Rust `regex`、Go、PCRE2、Java、.NET、V8、Python、Hyperscan、GNU grep），并讨论 Unicode、锚点与环视、计数重复、字面量预过滤与 SIMD、匹配语义差异、ReDoS 攻防、差分测试。

报告配套一个只依赖 Python 标准库的教学代码包 `regexlab/`（约 3500 行，16 个模块），文中每个算法都有可运行的实现。**文中引用的所有输出、状态数、步数、耗时都来自 `python3 -m regexlab.demos` 的实际运行**（完整输出见 `run_output.txt`），没有手工编造的数字。所有引擎还经过同一套差分模糊测试互相对拍：1896 个随机模式、113,760 个用例，各引擎之间**零差异**（第 15 章）。

### 阅读路线

| 读者 | 建议路线 |
|---|---|
| 想搞懂“正则是怎么跑起来的” | 第 0–6 章，配合代码逐章运行 |
| 编译器 / DSL 工程师 | 第 1、4、6、7 章 → 第 8、9 章 → 第 13 章 |
| 关心性能 | 第 5、6 章 → 第 10、12 章 |
| 关心安全（ReDoS、不可信模式） | 第 3 章 → 第 5.5 节 → 第 14 章 |
| 要自己实现或维护一个正则库 | 全部，重点第 10、13、15、16 章 |

### 配套代码 `regexlab/`

```text
regex-engine/
├── 正则引擎实现技术报告.md     ← 本报告
├── run_output.txt              ← python3 -m regexlab.demos 的完整输出
└── regexlab/
    ├── syntax.py       第 2 章   解析器、字符类规范化、特性分析、断言判定
    ├── backtrack.py    第 3 章   AST 上的续延式回溯（反向引用、环视、原子组、占有量词）
    ├── compiler.py     第 4 章   Thompson 构造：AST → 指令程序；规模估算
    ├── pikevm.py       第 5 章   Pike VM、有界回溯（BitState）
    ├── dfa.py          第 6 章   子集构造、Moore/Hopcroft 最小化、惰性 DFA、反向程序
    ├── direct.py       第 7 章   followpos、Glushkov 位掩码、Brzozowski 导数（交、补、等价判定）
    ├── lexgen.py       第 8 章   多规则 DFA、最长匹配驱动、Reps 线性化、梳状压缩、手写词法器
    ├── antlr_lexer.py  第 9 章   ATN 词法器 + 运行时 DFA 缓存
    ├── allstar.py      第 9 章   ALL(*) 自适应预测（SLL/LL 两阶段）
    ├── meta.py         第 10 章  三段式搜索、元引擎
    ├── utf8.py         第 11 章  码点区间 → UTF-8 字节序列
    ├── literals.py     第 12 章  前缀字面量、预过滤、Aho–Corasick、Shift-And
    ├── redos.py        第 14 章  ReDoS 静态检测（EDA / IDA）
    ├── fuzz.py         第 15 章  差分模糊测试
    ├── mutation.py     第 15 章  变异测试：注入错误，检验测试本身
    └── demos.py        生成本报告引用的全部实测数据
```

```bash
cd regex-engine
python3 -m regexlab.demos > run_output.txt   # 复现全部数据（约 1 分钟）
python3 -m regexlab.fuzz 500                 # 500 个随机模式的差分测试
```

```python
from regexlab.meta import Regex
r = Regex(r'(\w+)@(\w+)\.com')
r.search('mail: bob@ex.com!')     # (6, 16)
r.captures('mail: bob@ex.com!')   # [(6, 16), (6, 9), (10, 12)]
r.strategy                        # 'dfa'：惰性 DFA 三段式 + 有界回溯求捕获
```

> 说明：Python 实现只用于讲清算法和验证正确性。它比 C 实现慢两到三个数量级，所以耗时只能用来比较**同一表格内**各引擎的相对快慢，不能和生产引擎的绝对速度比较。

### 约定

- $m$ 表示模式长度（或编译后的指令数），$n$ 表示文本长度，$k$ 表示捕获槽数，$\Sigma$ 表示字母表。
- “最左优先”（leftmost-first）指 Perl 语义：在最左的起点上，选优先级最高的匹配。“最左最长”（leftmost-longest）指 POSIX 语义。二者的区别见第 13 章。
- 文中的工业实现细节以各项目公开的源码与文档为依据。版本在演进，具体常量（例如缓存大小）以对应版本为准。

---

## 目录

- 第 0 章　导读与全景图
- 第 1 章　理论基础：正则语言、自动机与两大流派
- 第 2 章　前端：词法、语法与 AST
- 第 3 章　最简单的引擎：回溯
- 第 4 章　Thompson 构造：从正则到 NFA
- 第 5 章　Pike VM：线性时间并支持捕获组
- 第 6 章　DFA：子集构造、惰性 DFA 与最小化
- 第 7 章　直接构造 DFA：followpos、Glushkov 与 Brzozowski 导数
- 第 8 章　词法分析器生成器：lex/flex、re2c 与编译器手写词法器
- 第 9 章　ANTLR：ATN 模拟与自适应 DFA 缓存
- 第 10 章　工业引擎剖析
- 第 11 章　高级专题：Unicode、锚点、环视、反向引用、计数重复
- 第 12 章　性能工程：字面量提取、预过滤、SIMD 与位并行
- 第 13 章　匹配语义：leftmost-first 与 leftmost-longest
- 第 14 章　安全：ReDoS 及其防御
- 第 15 章　测试与验证
- 第 16 章　横向对比与设计建议
- 附录 A　参考文献
- 附录 B　术语表
- 附录 C　练习提示

---

## 第 0 章　导读与全景图

### 0.1 三类“正则引擎”

“正则引擎”这个词背后至少是三类不同的系统：

| 类别 | 代表 | 核心诉求 |
|---|---|---|
| 通用正则库 | PCRE2、Java `java.util.regex`、.NET `Regex`、V8 Irregexp、Python `re`、RE2、Rust `regex`、Go `regexp` | 功能丰富、API 灵活、运行时编译 |
| 词法分析器生成器 | lex/flex、re2c、JFlex、ocamllex、Alex、ml-ulex、ANTLR lexer、Rust `logos` | 多规则同时匹配、最长匹配、离线生成、极致速度 |
| 高吞吐多模式匹配 | Hyperscan / Vectorscan、Snort / Suricata 的匹配层 | 成千上万条规则、流式扫描、SIMD |

它们共享同一套理论：正则语言与有限自动机等价。但工程取舍截然不同：

- 通用库要支持反向引用、环视，还要报告捕获组；
- 词法器只要“哪条规则、多长”，但要求每字节只花几个时钟周期；
- 多模式匹配要同时跑上万条规则，而且不能回头读已经流过去的数据。

### 0.2 全景图

```text
                    ┌──────────────┐
  pattern string ──►│ Parser (§2)  │──► AST ──► HIR（规范化、字面量提取、规模估算）
                    └──────────────┘
                           │
       ┌───────────────────┼─────────────────────┬────────────────────┐
       ▼                   ▼                     ▼                    ▼
  回溯字节码/树        Thompson NFA (§4)       Glushkov NFA (§7)    正则导数 (§7)
 (PCRE/Java/.NET/V8/    (RE2/Rust/Go/ANTLR)    (Hyperscan)        (.NET NonBacktracking,
  Python)  (§3)             │                     │                  ml-ulex)
       │                   ├──► Pike VM (§5)     ├──► 位并行 NFA (§12)  │
       ▼                   ├──► BitState (§5)    └──► DFA             ▼
   回溯执行器               ├──► OnePass DFA (§10)                  导数 DFA
   (+JIT 机器码 §10)       ├──► 惰性 DFA (§6) ──► 三段式搜索 / 元引擎 (§10)
                           └──► 完全 DFA (§6) ──► 最小化 ──► 表压缩 / 直接编码 (§8)
                                                               (flex / re2c)
   编译器词法器 (§8)：最长匹配 + 规则优先级；ANTLR (§9)：ATN 模拟 + 运行时 DFA 缓存
```

后面每一章都在展开图中的一个方框。

### 0.3 一条贯穿全书的主线

> **特性集合决定算法上限，算法决定复杂度保证。**

| 模式用到的特性                  | 能用的算法                                   | 能给的保证     |
| ------------------------ | --------------------------------------- | --------- |
| 纯正则（连接、选择、闭包、字符类）        | DFA、惰性 DFA、Pike VM、BitState             | 线性时间      |
| + 捕获组、非贪婪                | Pike VM、BitState、OnePass、TDFA；DFA 只能求边界 | 线性时间      |
| + `^` `$` `\b` 等**零宽断言** | 上述全部，状态里需额外记录上下文                        | 线性时间      |
| + 环视                     | 回溯；线性引擎需要专门扩展（第 11 章）                   | 一般无保证     |
| + 反向引用                   | 只有回溯                                    | NP 完全，指数级 |

`regexlab.meta.Regex` 就是按这张表选择引擎的（第 10 章）：

```text
hello                strategy=literal   prefilter=None
^\d+$                strategy=dfa       prefilter=None
hello\w+             strategy=dfa       prefilter=['hello']
\bfoo\b              strategy=pikevm    prefilter=None
(a+)b\1              strategy=backtrack prefilter=None
```

---

## 第 1 章　理论基础：正则语言、自动机与两大流派

### 1.1 正则表达式的形式定义

设字母表为 $\Sigma$。正则表达式归纳定义如下：

- $\varnothing$ 表示空语言；$\varepsilon$ 表示只含空串的语言；
- 对 $a \in \Sigma$，$a$ 表示 $\{a\}$；
- 若 $r$、$s$ 是正则表达式，则 $rs$（连接）、$r\mid s$（选择）、$r^*$（Kleene 闭包）也是。

实践中的 `+`、`?`、`{m,n}`、`[a-z]`、`.` 都是语法糖：

```text
r+      = r r*
r?      = r | ε
r{2,4}  = r r (r (r)?)?
[a-c]   = a | b | c
```

**Kleene 定理**：正则表达式、NFA、DFA 描述的语言类完全相同，都是**正则语言**。这是一切自动机引擎的理论根基。

但要注意，**现代“正则”早已不是正则**：

- 反向引用 `(a*)b\1` 描述的 $\{a^n b a^n\}$ 不是正则语言，用**泵引理**即可证明；
- 带反向引用的匹配问题是 **NP 完全**的（Aho 1990）；
- 环视、递归 `(?R)`、条件分支走得更远，PCRE 的**递归模式**甚至能描述括号配对这样的**上下文无关语言**。

### 1.2 NFA 与 DFA

- **NFA**：一个状态在同一字符上可以有多个后继，还可以有 ε 转移。
- **DFA**：每个状态在每个字符上恰有一个后继。

任何 NFA 都能通过**子集构造**转换为 DFA，但状态数最坏可达 $2^n$。经典例子是 `(a|b)*a(a|b){k}`，意思是“倒数第 $k+1$ 个字符是 a”。它的 NFA 只有 $O(k)$ 个状态，而**任何** DFA 都至少需要 $2^{k+1}$ 个状态，因为它必须记住最近 $k+1$ 个字符。

这一下界由 **Myhill–Nerode 定理**保证。语言 $L$ 的最小 DFA 状态数，等于等价关系

$$x \equiv_L y \iff \forall z\in\Sigma^*:\ xz\in L \Leftrightarrow yz\in L$$

的等价类个数。取两个长度为 $k+1$ 的不同 a/b 串，设它们在倒数第 $i$ 位不同，在后面补 $k+1-i$ 个 b，恰好一个被接受、一个被拒绝。所以这 $2^{k+1}$ 个串两两不等价。第 6 章会实测这个爆炸：$k=10$ 时程序只有 72 条指令，DFA 却有 2049 个状态。

### 1.3 历史脉络

| 年份          | 里程碑                                                                   |
| ----------- | --------------------------------------------------------------------- |
| 1951/1956   | Kleene 提出正则事件与正则表达式                                                   |
| 1959        | Rabin & Scott：NFA 与子集构造                                               |
| 1961        | Glushkov：位置自动机（无 ε 的 NFA）                                             |
| 1964        | Brzozowski：正则表达式的导数                                                   |
| 1968        | Thompson：正则 → NFA 程序，并行模拟；用于 QED、ed、grep                              |
| 1971        | Hopcroft：$O(n\log n)$ DFA 最小化                                         |
| 1975        | Lesk & Schmidt：lex                                                    |
| 1986        | Aho、Sethi、Ullman《龙书》：followpos 构造                                     |
| 1986–1987   | Henry Spencer 的回溯正则库；Perl 1.0；Paxson 的 flex                           |
| 1990        | Aho：反向引用匹配是 NP 完全                                                     |
| 1992        | Baeza-Yates & Gonnet：Shift-And 位并行                                    |
| 1994        | Bumbulis & Cowan：re2c                                                 |
| 1997        | Philip Hazel：PCRE                                                     |
| 2000        | Laurikari：带标签的 NFA/DFA（TNFA/TDFA）                                     |
| 2007–2010   | Russ Cox 系列文章与 RE2（Google Code Search）                                |
| 2011 / 2014 | Parr 等：ANTLR 3 的 LL(\*) / ANTLR 4 的 ALL(\*)                           |
| 2015        | Intel 开源 Hyperscan                                                    |
| 2016–2019   | Stack Overflow、Cloudflare 等 ReDoS 事故；Rust `regex` 1.0（2018）           |
| 2022–2023   | .NET 7 `RegexOptions.NonBacktracking`（基于导数）；Rust `regex-automata` 0.3 |

### 1.4 两大流派

Jeffrey Friedl 在《Mastering Regular Expressions》中把引擎分为两类：

| 流派 | 别称 | 工作方式 | 代表 |
|---|---|---|---|
| **正则导向**（regex-directed） | “传统 NFA”、回溯 | 按模式结构逐个尝试，失败则回退 | Perl、PCRE、Java、.NET、Python、Ruby、JavaScript |
| **文本导向**（text-directed） | DFA、自动机模拟 | 每读一个字符，同时推进所有可能状态 | awk、GNU grep 的 DFA 部分、RE2、Rust、Go、lex |

Friedl 所说的“NFA 引擎”其实是**回溯**引擎，与理论上的 NFA 模拟不是一回事。Russ Cox 在 *Regular Expression Matching Can Be Simple And Fast*（2007）中专门澄清了这一点。本文统一使用：

- **回溯引擎**：深度优先搜索；
- **自动机引擎**：广度优先的 NFA 模拟，或者确定化后的 DFA。

### 1.5 复杂度速览

| 方法 | 编译 | 匹配（时间） | 额外空间 | 捕获组 | 反向引用 / 环视 |
|---|---|---|---|---|---|
| 回溯（第 3 章） | $O(m)$ | 最坏 $O(2^n)$ | 栈 $O(n)$ 起 | ✅ | ✅ |
| 有界回溯 BitState（第 5 章） | $O(m)$ | $O(mn)$ | $O(mn)$ 位 | ✅ | ❌ |
| Pike VM（第 5 章） | $O(m)$ | $O(mn)$ | $O(mk)$ | ✅ | ❌ |
| 完全 DFA（第 6 章） | 最坏 $O(2^m\lvert\Sigma\rvert)$ | $O(n)$ | 表 | ❌（TDFA 可以，第 8 章） | ❌ |
| 惰性 DFA（第 6 章） | $O(m)$ | 典型 $O(n)$，最坏 $O(mn)$ | 有上限的缓存 | ❌，只给边界 | ❌ |
| 位并行（第 7、12 章） | $O(m\lvert\Sigma\rvert)$ | $O(n\lceil m/w\rceil)$ | $O(m)$ 位 | ❌ | ❌ |

其中 $w$ 是机器字长。工业引擎极少只用其中一种，它们是**混合**的（第 10 章）。

---
## 第 2 章　前端：词法、语法与 AST

引擎的第一步是把模式字符串变成一棵语法树。这一步看似平凡，却决定了后面几个关键问题：

- 编号规则：捕获组按什么顺序编号；
- 资源上限：嵌套多深、重复多少次会被拒绝；
- 报错质量：用户看到的错误能否指出真正的原因；
- 特性划分：哪些特性交给哪个引擎。

### 2.1 正则自身的文法

**正则语法**本身是一个小型的上下文无关语言。优先级从低到高依次是：选择 `|`、连接、量词、原子。

```EBNF
alt     ::= concat ('|' concat)*
concat  ::= repeat*
repeat  ::= atom quant*
quant   ::= ('*' | '+' | '?' | '{' m (',' n?)? '}') ('?' | '+')?
atom    ::= literal | '.' | '^' | '$' | '(' alt ')' | '(?:' alt ')' | '(?>' alt ')'
          | '(?=' alt ')' | '(?!' alt ')' | '(?<=' alt ')' | '(?<!' alt ')'
          | class | escape
class   ::= '[' '^'? item+ ']'
escape  ::= '\d' | '\w' | '\s' | '\D' | '\W' | '\S' | '\b' | '\B' | '\1'..'\9' | '\' char
```

量词后面的 `?` 表示**非贪婪**，`+` 表示**占有**（possessive，第 3 章）。

### 2.2 AST 表示

`regexlab` 用元组表示 AST 节点，所有引擎共用这一种表示：

```text
('char', c)   ('any',)   ('class', ranges, negated)   ('empty',)
('cat', [nodes])   ('alt', a, b)
('star', n, greedy)   ('plus', n, greedy)   ('quest', n, greedy)
('repeat', n, lo, hi, greedy)        # hi 为 None 表示 {lo,}
('group', n, idx)                    # 捕获组，idx 从 1 开始
('bol',) ('eol',) ('wordb',) ('nwordb',)             # ^ $ \b \B
('backref', k)   ('look', n, ahead, negated)   ('atomic', n)
```

```python
>>> parse(r'(a|b)*c{2,3}')
(('cat', [('star', ('group', ('alt', ('char', 'a'), ('char', 'b')), 1), True),
          ('repeat', ('char', 'c'), 2, 3, True)]), 1)
```

### 2.3 递归下降解析器

完整代码见 `regexlab/syntax.py`。核心是与文法一一对应的四个函数：

```python
class Parser:
    def alt(self):
        node = self.concat()
        while self.eat('|'):
            node = ('alt', node, self.concat())
        return node

    def concat(self):
        items = []
        while self.peek() not in (None, '|', ')'):
            items.append(self.repeat())
        if not items:
            return ('empty',)
        return items[0] if len(items) == 1 else ('cat', items)

    def repeat(self):
        saved = self.depth
        node = self.atom()
        while True:
            c = self.peek()
            if c in ('*', '+', '?'):
                self.i += 1
                kind = {'*': 'star', '+': 'plus', '?': 'quest'}[c]
                greedy = not self.eat('?')                 # a*? 非贪婪
                possessive = greedy and self.eat('+')      # a*+ 占有
                self.enter()                               # 量词链也计入嵌套深度
                node = (kind, node, greedy)
                if possessive:
                    node = ('atomic', node)
                continue
            m = self._COUNTED.match(self.p, self.i) if c == '{' else None
            if m:
                ...                                        # 解析 {m} {m,} {m,n}，检查上限
                node = ('repeat', node, lo, hi, greedy)
                continue
            self.depth = saved
            return node        # 不是合法计数量词的 '{' 按字面处理（与 Perl 一致）

    def atom(self):
        start = self.i
        c = self.next()
        if c == '(':
            self.enter()
            if self.eat('?:'):    node = self.alt()
            elif self.eat('?>'):  node = ('atomic', self.alt())
            elif self.eat('?='):  node = ('look', self.alt(), True, False)
            ...
            else:
                self.ngroups += 1
                idx = self.ngroups                 # 先分配编号：按左括号的出现顺序
                node = ('group', self.alt(), idx)
            if not self.eat(')'):
                self.err("unclosed group", start)  # 错误指向“原因”而不是“发现处”
            self.depth -= 1
            return node
        ...
```

有三个细节值得注意。

**捕获组按左括号的出现顺序编号，并且在解析时就分配。** 在 `((a)(b))` 中，外层是 1，`(a)` 是 2，`(b)` 是 3。编号必须在解析阶段确定。`(a){3}` 编译时会把子树复制三份（第 4 章），如果在编译阶段才编号，每一份都会得到不同的编号。

**字符类在解析时就规范化。** 区间被排序，重叠或相邻的区间被合并：

```python
def normalize(ranges):
    out = []
    for lo, hi in sorted(ranges):
        if out and ord(lo) <= ord(out[-1][1]) + 1:
            if hi > out[-1][1]:
                out[-1] = (out[-1][0], hi)
        else:
            out.append((lo, hi))
    return out
```

规范化之后，成员判定可以二分查找（`in_class`），字符等价类的计算（第 6 章）也只需要收集区间端点。

**`{` 不一定是量词。** `a{`、`a{x}` 中的 `{` 按字面处理，这与 Perl 和 PCRE 一致。但 Rust `regex` 会把它们当作错误，这又是一处“各家不一样”的地方。

### 2.4 资源上限与报错

模式经常来自不可信的输入，比如搜索框、配置文件、WAF 规则。解析器是第一道防线。

**嵌套上限。** 递归下降解析器的递归深度等于模式的嵌套深度。一万个 `(` 就能让 Python 抛出 `RecursionError`，让 C/Rust 程序栈溢出。常见对策有两种：

1. **设置嵌套上限。** Rust `regex-syntax` 默认 `nest_limit = 250`，`regexlab` 采用同样的值。量词链 `a*****` 虽然由 `while` 循环解析，但生成的 AST 同样很深，所以也要计数。
2. **改用显式栈。** Go 的 `regexp/syntax` 和 Rust 的 `regex-syntax` 都用基于栈的循环解析，不依赖调用栈。

即使解析器不递归，**后续阶段**也可能递归：化简、编译，甚至析构一棵很深的 AST。所以嵌套上限通常要和显式栈配合使用。Rust 的 `regex-syntax` 甚至为 `Ast` 和 `Hir` 手写了非递归的 `Drop`。

**重复上限。** `(?:a{100}){100}` 编译后有一万条指令，再嵌套一层就是一百万条。RE2 规定计数重复的上限为 1000，`regexlab` 也采用这个值。此外，在编译**之前**还要按“子树规模 × 重复次数”估算程序大小（第 4.4 节）。

**错误要指向原因。** 对于 `(ab`，解析器是在模式末尾才发现错误的，但对用户有用的位置是那个没有闭合的 `(`。所以要在进入分组时记下 `start`：

```text
regex parse error:
    (ab
    ^
error: unclosed group
```

`regexlab` 对几种典型错误的实际输出：

```text
'(ab'                    -> unclosed group
'[z-a]'                  -> bad range z-a
'((((((((((((((((((((('   -> nesting limit 250 exceeded      （300 层嵌套）
'a{2000}'                -> repeat count exceeds 1000
```

**区分“语法错误”与“不支持”。** Go 遇到 `(?=...)` 时报的是 `invalid or unsupported Perl syntax`。Rust 报 `look-around, including look-ahead and look-behind, is not supported`，而不是笼统的语法错误。这样用户能立刻明白，问题在引擎能力，不在自己写错了。

### 2.5 从 AST 到 HIR：解析之后的规范化

工业实现通常区分两层中间表示。以 Rust 的 `regex-syntax` 为例：

| 层 | 作用 | 内容 |
|---|---|---|
| `Ast` | 忠实保留源码 | 位置区间（用于报错）、注释、原始转义写法 |
| `Hir`（高级中间表示） | 供编译器使用 | 字符类已展开为区间集合，大小写折叠已完成，`\d` 已按 Unicode 或 ASCII 模式解析 |

常见的规范化步骤：

1. **字符类代数。** 并、交、差、补，对称差都要支持。这是 `[\w&&[^\d]]`（Java/Rust 的类内交集）、大小写折叠和 UTF-8 编译（第 11 章）的基础。
2. **大小写折叠。** `(?i)k` 在 Unicode 下应当匹配 `k`、`K` 和 `K`（U+212A，开尔文符号）。这需要查 Unicode 的 `CaseFolding.txt`，不能简单调用 `lower()`（第 11 章）。
3. **代数化简。** `a|a → a`，`(?:x*)* → x*`，`[a] → a`，`x{1} → x`，`x{0} → ε`。
4. **字面量提取。** 计算必须出现的前缀、后缀或内部字面量，供预过滤器使用（第 12 章）。
5. **特性分析。** 判断模式是否用到了反向引用、环视、原子组、单词边界，决定哪些引擎可用：

```python
def features(n, out=None):
    out = set() if out is None else out
    k = n[0]
    if k in ('backref', 'look', 'atomic', 'wordb', 'nwordb'):
        out.add({'nwordb': 'wordb'}.get(k, k))
    for c in children(n):
        features(c, out)
    return out
```

6. **可空性分析。** `nullable(n)` 判断子树能否匹配空串。它决定了空循环的处理方式（第 3、5 章），也被第 7 章的 followpos 构造使用。

### 2.6 小结与练习

本章的解析器覆盖了分组（捕获、非捕获、原子、四种环视）、选择、贪婪/非贪婪/占有量词、计数重复、字符类、常用转义和反向引用，并内置了嵌套上限、重复上限和指向原因的报错。

**练习**

1. 加入命名分组 `(?P<name>...)`，返回 `name → index` 的映射。注意 Python 用 `(?P<name>)`，.NET 和 JavaScript 用 `(?<name>)`，后者与后行断言 `(?<=` 共享前缀。
2. 实现内联标志 `(?i)` 和 `(?i:...)`，在 `cls()` 中对区间做 ASCII 大小写折叠。思考：`(?i)[^a]` 应当先折叠再取反，还是先取反再折叠？
3. 写一个 `unparse(ast)`，把 AST 打印回最简正则，并用随机测试验证 `parse(unparse(parse(p))) == parse(p)`。
4. 把 `alt`、`concat`、`repeat` 改写成不递归的 shunting-yard 形式，去掉 `MAX_NEST` 后，用 10 万层嵌套的模式验证它不会栈溢出。

---
## 第 3 章　最简单的引擎：回溯

Perl、PCRE、Python `re`、Java、JavaScript、Ruby 和 .NET（默认模式）的正则引擎，本质上都是**回溯引擎**。它们做的事情就是对模式结构做一次深度优先搜索：遇到选择，先试左边，失败了再回来试右边。

这一章直接在 AST 上实现一个回溯引擎。它是全书**功能最全**的引擎，支持捕获组、贪婪/非贪婪、反向引用、四种环视、原子组和占有量词；同时也是**保证最差**的引擎，最坏情况下是指数级。

### 3.1 续延传递：把“接下来要做什么”作为参数

回溯的难点在于：匹配完一个子表达式后，要能“接着匹配剩下的部分”，而且剩下的部分失败时，还要能回到这个子表达式，让它换一种匹配方式。

最简洁的写法是**续延传递风格**（continuation-passing style）。函数 `m(n, i, caps, k)` 的含义是：

> 尝试从位置 `i` 开始用节点 `n` 匹配；每找到一种匹配方式（终点 `j`、新的捕获 `caps'`），就调用续延 `k(j, caps')`，问它“剩下的部分能不能成功”。`k` 成功就返回结果，`k` 失败就换下一种方式。所有方式都失败时返回 `None`。

```python
def m(self, n, i, caps, k):
    self.steps += 1
    T = self.text
    t = n[0]
    if t == 'char':
        return k(i + 1, caps) if i < len(T) and T[i] == n[1] else None
    if t == 'class':
        ok = i < len(T) and in_class(T[i], n[1]) != n[2]
        return k(i + 1, caps) if ok else None
    if t == 'cat':
        items = n[1]
        def go(idx, j, c):
            if idx == len(items):
                return k(j, c)
            return self.m(items[idx], j, c, lambda j2, c2: go(idx + 1, j2, c2))
        return go(0, i, caps)
    if t == 'alt':                       # 先试左边，失败再试右边：有序选择
        r = self.m(n[1], i, caps, k)
        return r if r is not None else self.m(n[2], i, caps, k)
    if t == 'group':                     # 进入时记录起点，离开时记录终点
        idx = n[2]
        c1 = caps[:2 * idx] + (i,) + caps[2 * idx + 1:]
        return self.m(n[1], i, c1,
                      lambda j, c2: k(j, c2[:2 * idx + 1] + (j,) + c2[2 * idx + 2:]))
    if t in ('star', 'plus', 'quest', 'repeat'):
        return self.rep(...)             # 见 3.2 节
    ...
```

捕获数组用不可变元组表示，并随续延传递。回溯时，状态会自动恢复为分叉那一刻的值，不需要显式“撤销”。真实引擎为了省内存，通常采用相反的做法：原地修改，并在栈上记录撤销日志。

`alt` 的两行代码就是回溯语义的全部：**有序选择**。`a|ab` 匹配 `"ab"` 时，左分支 `a` 先成功，右分支 `ab` 根本不会被尝试，结果是 `"a"`。这就是 leftmost-first 语义的来源（第 13 章）。

### 3.2 量词：贪婪、非贪婪与空循环

所有量词统一由 `rep(sub, lo, hi, greedy, count, ...)` 处理，`count` 是已经完成的迭代次数：

```python
def rep(self, sub, lo, hi, greedy, count, i, caps, k):
    def more():                          # 再迭代一次
        if hi is not None and count >= hi:
            return None
        def after(j, c):
            if j == i and count >= lo:   # 这次迭代没有前进：空循环
                return k(j, c) if self.empty_iter == 'perl' else None
            return self.rep(sub, lo, hi, greedy, count + 1, j, c, k)
        return self.m(sub, i, caps, after)

    def stop():                          # 到此为止
        return k(i, caps) if count >= lo else None

    if greedy:                           # 贪婪：先多后少
        r = more()
        return r if r is not None else stop()
    r = stop()                           # 非贪婪：先少后多
    return r if r is not None else more()
```

贪婪与非贪婪的区别只有 `more()` 和 `stop()` 的先后顺序。

**空循环必须特殊处理。** `(a*)*` 的外层循环体可以不消耗任何字符就完成一次迭代。如果不加检查，`rep` 会在同一位置无限递归下去。`after` 中的 `j == i` 检查有两种处理方式：

| 方案 | 做法 | `(a*)*` 匹配 `"b"` 时第 1 组 |
|---|---|---|
| `'perl'` | 保留这次空迭代，然后**退出循环** | `(0, 0)`，即 `""` |
| `'fail'` | 让这条路径**失败** | 未参与匹配 |

Perl 和 Python 采用前者。`regexlab` 默认也采用前者。第 15 章的差分测试显示，在 1896 个随机模式、113,760 个用例上，`Backtracker` 的整体区间和全部捕获组都与 Python `re` **完全一致**。

两种方案在一般情况下会给出**不同的整体匹配**，不只是捕获组不同：

```text
^b.(?:(?:[ab])*?)*    'baaabba'   perl=[(0, 2)]   fail=[(0, 7)]   python=[(0, 2)]
```

外层是贪婪的 `*`，内层是非贪婪的 `*?`。第一次外层迭代时，内层非贪婪先尝试匹配空串：

- `'perl'` 方案保留这次空迭代并退出循环，于是匹配在位置 2 结束；
- `'fail'` 方案判定这次迭代失败，逼迫内层至少吃一个字符，外层于是一直迭代到文本末尾。

第 5 章的 Pike VM 会给出**第三种**答案 `(0, 3)`。第 13 章会把这三种语义放在一起比较。

### 3.3 运行

```text
模式                      文本            结果（[(整体), (第1组), ...]）
(a+)b\1                  'xaaabaa'      [(2, 7), (2, 4)]
(a)?b\1                  'b'            None            ← 第 1 组未参与，Python 视为失败
\w+(?=,)                 'ab,cd'        [(0, 2)]
(?<=\$)\d+               'cost $42'     [(6, 8)]
(?<!\$)\b\d+             '$42 and 17'   [(8, 10)]
```

这些结果与 Python `re` 完全相同。

### 3.4 现场观察“爆炸”

用 `(a+)+$` 匹配 n 个 `a` 后面跟一个 `b`。下面是 `python3 -m regexlab.demos` 的实测结果：

```text
  n      (a+)+$ 步数     耗时(s)    (?>a+)+$ 步数    a++$ 步数
  8          2,560     0.002            118         84
 10         10,240     0.007            155        113
 12         40,960     0.026            196        146
 14        163,840     0.106            241        183
 16        655,360     0.466            290        224
 18      2,621,440     2.304            343        269
 20     10,485,760     8.413            400        318
```

n 每增加 2，步数恰好乘以 4，即 $\Theta(2^n)$。n = 30 时要算上几个小时。

**为什么是指数级？** 失败要等到 `$` 遇上 `b` 才能确定。在此之前，引擎会把 n 个 `a` 的**每一种**切分方式都试一遍：

```text
(aaaa)          (aaa)(a)        (aa)(aa)        (aa)(a)(a)
(a)(aaa)        (a)(aa)(a)      (a)(a)(aa)      (a)(a)(a)(a)
```

n 个字符之间有 $n-1$ 个“切或不切”的位置，共 $2^{n-1}$ 种切分。外层还要在每个起点各重复一次。

**灾难性回溯的一般形态：** 同一段输入可以被模式以多种方式匹配，即模式存在**歧义**；而这次匹配最终又会失败，迫使引擎穷举所有方式。歧义加上失败，就是指数级的配方。第 14 章会把这个直觉变成可以自动检测的判据。

最后一道防线是**步数预算**，PCRE 的 `match_limit` 就是这个机制：

```python
>>> Backtracker(r'(a+)+$', budget=100_000).search('a' * 40 + 'b')
StepLimit: budget exceeded after 100001 steps
```

它只能把“卡死”变成“报错”。

### 3.5 原子组与占有量词：回溯引擎的自救

上表后两列是同一个语言的另外两种写法：

- **原子组** `(?>a+)`：子表达式只取**第一个**解，之后不再回溯进去；
- **占有量词** `a++`：等价于 `(?>a+)`，吞下去的字符不再吐出来。

实现只需几行。求出子表达式的第一个解后，直接把它交给续延，不再给子表达式“换一种方式”的机会：

```python
if t == 'atomic':
    r = self.m(n[1], i, caps, lambda j, c: (j, c))   # 续延直接返回：只要第一个解
    return None if r is None else k(r[0], r[1])
```

从实测数据看，步数从指数级降到了线性。原子组切断了“同一段输入被多种方式匹配”的歧义来源。

代价是语义改变了。`(?>a+)ab` 永远匹配不了 `"aab"`：`a+` 吞下全部两个 `a` 之后不肯吐出一个给后面的 `a`。所以原子组只能由**理解模式的人**手工添加，不能由引擎自动插入。

Python 从 3.11 起支持原子组和占有量词。Java、.NET、PCRE 和 Ruby 早就支持。

### 3.6 反向引用：为什么线性引擎放弃了它

`(a+)b\1` 中的 `\1` 要求重复第 1 组**刚才匹配到的那段文本**。在回溯引擎里实现它只需几行：

```python
if t == 'backref':
    s, e = caps[2 * n[1]], caps[2 * n[1] + 1]
    if s is None or e is None:
        return None                  # 组未参与匹配：Python 视为失败，JavaScript 视为匹配空串
    return k(i + e - s, caps) if T.startswith(T[s:e], i) else None
```

注释里的分歧是真实存在的：`(a)?b\1` 匹配 `"b"`，在 Python、PCRE、Java 中失败，在 JavaScript 中成功。

但从理论上看，反向引用改变了一切。**支持反向引用的正则匹配是 NP 完全的。** 可以从 3-SAT 规约：每个变量 $x_i$ 用一个捕获组表示，组匹配 `"x"` 表示真，匹配空串表示假；每个子句用若干个反向引用的选择来检查“至少一个文字为真”。所以不存在已知的多项式算法。

后面几章的线性时间引擎都依赖“从 (位置, 状态) 出发的成败与历史无关”这个前提。反向引用让成败取决于捕获的内容，这个前提随之失效。RE2、Go 和 Rust 因此选择**直接不支持**反向引用：对它们来说，线性时间保证比这项特性更重要。

### 3.7 环视

```python
if t == 'look':
    sub, ahead, neg = n[1], n[2], n[3]
    if ahead:
        r = self.m(sub, i, caps, lambda j, c: c)          # 只问“能否匹配”，不前进
    else:                                                 # 后行断言：枚举起点，要求恰好在 i 结束
        r = None
        for j in range(i, -1, -1):
            r = self.m(sub, j, caps, lambda e, c: c if e == i else None)
            if r is not None:
                break
    if neg:
        return k(i, caps) if r is None else None
    return k(i, r) if r is not None else None             # 正向环视里的捕获保留下来
```

环视在回溯引擎中是**原子**的：一旦断言成立，引擎就不会再回溯进环视内部，去寻找另一种匹配方式。各引擎对后行断言的限制差别很大：

| 引擎 | 后行断言的限制 |
|---|---|
| Python `re` | 必须定长（`look-behind requires fixed-width pattern`） |
| PCRE2 | 每个分支定长；10.43 起支持有上限的变长 |
| Java | 必须有长度上限 |
| .NET、JavaScript（ES2018 起） | 任意变长 |
| RE2、Go、Rust | 不支持任何环视 |

`regexlab` 的实现允许变长，代价是对每个起点都要试一遍。这正是许多引擎限制后行断言长度的原因：定长的后行断言只需从 $i - L$ 处试一次。

### 3.8 递归深度：回溯引擎的另一个隐患

续延传递的写法很优雅，但每消耗一个字符，调用链就会加深几层。`regexlab` 把 Python 的递归上限调到了 20000，即便如此，`a*` 匹配几千个字符就会触顶。这不只是玩具实现的问题：

- 早期 PCRE（PCRE1）用 C 递归实现回溯，长文本会耗尽栈。PCRE2 10.30 起改为在堆上分配回溯帧，并提供 `heap_limit` 和 `depth_limit`；
- Perl 5.10 把正则引擎改写成了非递归形式；
- Java 的 `java.util.regex` 至今仍会在 `(a|b)*` 这类模式匹配很长的输入时抛出 `StackOverflowError`；
- Python 的 `_sre` 在 C 层使用显式的数据栈。

工业级回溯引擎大多采用**字节码加显式栈**：先把模式编译成类似第 4 章的指令序列，再用一个循环加一个堆上的栈来执行。第 5.5 节会给出这种写法，并在其上加一个位图，把指数级的回溯变成线性的。

### 3.9 小结与练习

| 优点 | 缺点 |
|---|---|
| 实现简单，常数小 | 最坏指数级（歧义 + 失败） |
| 最容易扩展：反向引用、环视、原子组、递归、条件分支 | 栈深度与文本长度成正比 |
| 直接给出 Perl 语义的捕获组 | 空循环需要特殊处理，各引擎细节不同 |

**练习**

1. 实现条件分支 `(?(1)yes|no)`：第 1 组参与了匹配就用 `yes`，否则用 `no`。
2. 实现递归 `(?R)`，用 `\((?:[^()]|(?R))*\)` 匹配平衡括号。说明为什么这已经超出了正则语言。
3. 把 `Backtracker` 改写成显式栈版本，去掉对 `sys.setrecursionlimit` 的依赖，并用十万个 `a` 测试 `a*`。提示：续延变成栈上的“待办事项”。
4. 第 14 章的实测中，`(a|aa)*$` 在 n = 8 和 n = 16 时的步数分别是 1,485 和 72,344，比值约为 48.7。证明它的步数按斐波那契数增长，并解释比值为什么接近 $\varphi^8 \approx 47$，其中 $\varphi$ 是黄金分割比。
5. 在 3-SAT 规约的提示下，写一个函数，把一个 3-CNF 公式翻译成带反向引用的正则表达式和一个输入串，使得“匹配成功”当且仅当“公式可满足”。用 `Backtracker` 验证几个小公式。

---
## 第 4 章　Thompson 构造：从正则到 NFA

1968 年，Ken Thompson 在 CACM 上发表了一页半的论文 *Regular Expression Search Algorithm*。他把正则表达式**编译成 IBM 7094 的机器码**，再在运行时并行模拟所有可能的执行路径。这个想法有两半：编译和模拟。本章实现前一半，第 5 章实现后一半。

### 4.1 指令集

我们沿用 Russ Cox 在 *Regular Expression Matching: the Virtual Machine Approach*（2009）中的指令设计，并补上断言指令：

| 指令 | 含义 |
|---|---|
| `char c` | 当前字符为 `c` 则前进到下一条指令，否则该线程死亡 |
| `any` | 匹配除 `\n` 之外的任意字符 |
| `class ranges neg` | 当前字符落在（或不落在）区间集合中 |
| `split x, y` | 分叉为两个线程，**x 的优先级高于 y** |
| `jmp x` | 跳转 |
| `save n` | 把当前位置记录到捕获槽 `n` |
| `assert kind` | 零宽断言：`bol`、`eol`、`wordb`、`nwordb` |
| `match` | 匹配成功 |

`split` 的两个分支是**有序**的，这一点至关重要。贪婪与非贪婪的唯一区别，就是 `split` 两个目标的先后顺序：

- 在纯集合语义的 DFA（第 6 章）中，这个顺序会被丢弃；
- 在需要报告 Perl 语义匹配的 Pike VM 和回溯引擎中，它决定了结果。

把程序看成一张图，“程序”和“NFA”就是同一个东西：`char`、`any`、`class` 是消耗字符的边，`split`、`jmp`、`save`、`assert` 是 ε 边。这种线性的程序表示便于序列化、反汇编和做窥孔优化。

### 4.2 各结构的编译模板

用 `L1`、`L2`、`L3` 表示标号：

```text
e1|e2:            split L1, L2
              L1: <e1>
                  jmp L3
              L2: <e2>
              L3:

e? (贪婪):        split L1, L2         非贪婪: split L2, L1
              L1: <e>
              L2:

e* (贪婪):    L1: split L2, L3         非贪婪: split L3, L2
              L2: <e>
                  jmp L1
              L3:

e+ (贪婪):    L1: <e>                  非贪婪: split L2, L1
                  split L1, L2
              L2:

(e) 第 k 组:      save 2k
                  <e>
                  save 2k+1
```

每个运算符只增加常数条指令，所以**程序长度为 $O(m)$**。计数重复 `{lo,hi}` 是例外，它需要展开。

### 4.3 实现

完整代码见 `regexlab/compiler.py`：

```python
class Compiler:
    def emit(self, *ins):
        self.prog.append(list(ins))
        return len(self.prog) - 1

    def set_split(self, s, prefer, other, greedy):
        """greedy 时优先 prefer，否则优先 other。"""
        self.prog[s][1:3] = [prefer, other] if greedy else [other, prefer]

    def c(self, n):
        k = n[0]
        if k == 'char':
            self.emit('char', n[1])
        elif k == 'group':
            _, sub, idx = n
            self.emit('save', 2 * idx)
            self.c(sub)
            self.emit('save', 2 * idx + 1)
        elif k == 'alt':
            s = self.emit('split', None, None)
            l1 = self.pc(); self.c(n[1])
            j = self.emit('jmp', None)
            l2 = self.pc(); self.c(n[2])
            self.prog[s][1:3] = [l1, l2]
            self.prog[j][1] = self.pc()
        elif k == 'star':
            _, sub, g = n
            s = self.emit('split', None, None)
            body = self.pc(); self.c(sub)
            self.emit('jmp', s)
            self.set_split(s, body, self.pc(), g)
        elif k == 'repeat':
            _, sub, lo, hi, g = n
            for _ in range(lo):                     # 必选部分：原样复制 lo 份
                self.c(sub)
            if hi is None:                          # {lo,}  →  sub{lo} sub*
                self.c(('star', sub, g))
            else:                                   # {lo,hi} → 嵌套可选 x(x(x)?)?
                splits = []
                for _ in range(hi - lo):
                    s = self.emit('split', None, None)
                    splits.append(s)
                    self.prog[s][1] = self.pc()     # 暂存“继续”分支
                    self.c(sub)
                end = self.pc()
                for s in splits:                    # 每个“跳过”都直接跳到末尾
                    self.set_split(s, self.prog[s][1], end, g)
        ...                                         # quest、plus、class、assert 类似

def compile_ast(ast):
    bad = features(ast) & {'backref', 'look', 'atomic'}
    if bad:
        raise Unsupported(f"pattern uses {sorted(bad)}")   # 自动机引擎做不到
    if estimate_size(ast) > MAX_PROG:
        raise Unsupported(...)
    cp = Compiler()
    cp.emit('save', 0)        # 第 0 组 = 整个匹配
    cp.c(ast)
    cp.emit('save', 1)
    cp.emit('match')
    return cp.prog
```

`compile_ast` 在入口处就拒绝反向引用、环视和原子组。这是“特性决定算法”在代码里的直接体现：从这里往后的所有引擎都是自动机引擎。

`a(b|c)*d` 的实际编译结果：

```text
  0  save    0
  1  char    a
  2  split   3 10      # star：优先进入循环体(3)，否则跳出(10)
  3  save    2
  4  split   5 7       # alt：b 优先于 c
  5  char    b
  6  jmp     8
  7  char    c
  8  save    3
  9  jmp     2         # 回到 star 的 split
 10  char    d
 11  save    1
 12  match
```

`x{2,4}` 的编译结果，可以看到嵌套形式中每个 `split` 的“跳过”分支都直接指向末尾（7）：

```text
  0  save    0
  1  char    x
  2  char    x
  3  split   4 7
  4  char    x
  5  split   6 7
  6  char    x
  7  save    1
  8  match
```

**为什么用嵌套形式 `x(x(x)?)?`，而不是平铺的 `x?x?x?`？** 在平铺形式中，“只匹配一个 x”可以由三个不同位置的 `x?` 实现，会产生大量等价路径，这正是第 3 章所说的**歧义**。对回溯引擎来说，这可能导致指数级的重复尝试。在嵌套形式中，每一种匹配次数只对应唯一的一条路径。

### 4.4 几个容易踩的坑

**1. 空循环：`(a*)*`、`(|a)*`、`(^)*`。** 外层 `*` 的循环体可以不消耗任何字符就回到 `split`。在程序中，这表现为一个只由 ε 边组成的环。

- 朴素的回溯器会在这里无限循环（第 3 章、第 5.5 节）；
- Pike VM 天然免疫：同一个位置上，每个 pc 只加入一次线程（第 5 章）；
- 但不同引擎打断这个环的方式不同，会导致**匹配结果不同**（第 13 章）。

**2. 重复内的捕获组会被复制。** `(a){3}` 展开后有三份 `save 2 / save 3`，最后一次迭代的值胜出。这正是 Perl 的语义，无需特殊处理。前提是组编号已经在解析阶段分配好（第 2.3 节）。

**3. 展开导致程序膨胀。** 大小估算必须在编译**之前**完成：

```python
def estimate_size(n):
    k = n[0]
    if k in ('char', 'any', 'class', 'bol', 'eol', 'wordb', 'nwordb'):
        return 1
    if k == 'repeat':
        _, sub, lo, hi, _ = n
        s = estimate_size(sub)
        return s * lo + (s + 2 if hi is None else (s + 1) * (hi - lo))
    ...
```

```text
(?:a{100}){10}               估计指令数        1,000  ok
(?:a{100}){100}              估计指令数       10,000  ok
(?:(?:a{100}){100}){100}     估计指令数    1,000,000  rejected: program would exceed 100000 instructions
```

RE2 默认的内存上限 `max_mem` 是 8 MB，程序和 DFA 缓存都在这个预算里分配。Rust `regex` 的 `size_limit` 默认约 10 MB。

**4. 编译器本身也是递归的。** `Compiler.c` 的递归深度等于 AST 的深度，所以解析阶段的嵌套上限同时也在保护编译器。

### 4.5 工业实现中的程序表示

| 实现 | 表示 | 特点 |
|---|---|---|
| Thompson 1968 | IBM 7094 机器码 | 每个 NFA 状态是一段代码；“线程列表”是待执行的代码地址表 |
| RE2 | `Prog`，指令包括 `kInstByteRange`、`kInstAlt`、`kInstCapture`、`kInstEmptyWidth`、`kInstMatch` | **按字节**运行，Unicode 字符类在编译时展开为 UTF-8 字节序列；编译后会把 `Alt` 链“压平”成列表 |
| Go `regexp/syntax` | `Prog`，`InstAlt`、`InstRune`、`InstCapture`、`InstEmptyWidth` | **按 rune**（码点）运行，字符类保留为区间列表 |
| Rust `regex-automata` | `thompson::NFA`，状态包括 `ByteRange`、`Sparse`、`Union`、`BinaryUnion`、`Capture`、`Look`、`Match` | 按字节运行；`Sparse` 把多条字节区间转移放在一个状态里；编译时会对 UTF-8 后缀做共享 |
| PCRE2、Python `sre`、Java、.NET | 回溯字节码或节点树 | 指令里直接带有贪婪/非贪婪、原子、环视等语义，没有“NFA”的抽象 |

“按字节”还是“按码点”是一个影响深远的选择：

- 按字节运行，DFA 的字母表最多只有 256，等价类表可以直接用数组索引；
- 代价是编译器要把 `[\u4e00-\u9fff]` 这样的字符类翻译成 UTF-8 字节序列的选择（第 11 章）。

### 4.6 另一种构造：Glushkov

Thompson 构造得到的 NFA 带有 ε 边。另一种经典构造 **Glushkov 自动机**没有 ε 边，状态与模式中的字符出现位置一一对应，非常适合位并行模拟。Hyperscan 就建立在它之上。第 7 章会详细讨论。

| | Thompson | Glushkov |
|---|---|---|
| 状态数 | $\le 2m$ | $m+1$ |
| ε 转移 | 有 | 无 |
| 边数 | $O(m)$ | 最坏 $O(m^2)$ |
| 适合 | Pike VM、回溯、子集构造 | 位并行、硬件实现 |

### 4.7 练习

1. 实现一个窥孔优化：把 `jmp → jmp` 链压缩为直接跳转，并删除不可达指令。
2. 当 `sub` 不含捕获组且是单个字符类时，为 `repeat` 生成一条专用指令 `repeat_class ranges lo hi`。它在回溯引擎和 Pike VM 中分别该如何执行？
3. 用 `dump` 比较 `a{0,3}` 的嵌套展开与平铺展开 `a?a?a?`，再用第 3 章的 `Backtracker` 统计二者匹配 `"aaaa!"`（`$` 结尾）时的步数差异。
4. 设计一条 `split_n x1, x2, ..., xn` 指令代替 `split` 链，说明它对 `[a-z]|[0-9]|_|...` 这类大选择的好处。RE2 的 `Alt` 压平就是这个思路。

---
## 第 5 章　Pike VM：线性时间并支持捕获组

回溯引擎一次只走一条路径，走不通就退回去换一条，最坏情况下要尝试指数级的路径。Thompson 的思路正好相反：**同时走所有路径**，并让所有线程按输入位置同步推进。每读一个字符，全体线程一起前进一步。

Thompson 的原始算法只回答“是否匹配”。Rob Pike 在 1980 年代为 `sam` 编辑器扩展了它：每个线程携带自己的捕获位置，线程列表按优先级排序。这样就能在**线性时间**内得到与回溯引擎相同的匹配结果和子匹配。这就是 **Pike VM**，也是 RE2、Go `regexp` 和 Rust `regex` 中“永远可用”的保底引擎。

### 5.1 核心思想

1. **线程** = (pc, 捕获数组)。
2. 维护两个列表：`clist` 存放当前位置的线程，`nlist` 存放下一位置的线程。
3. **ε 闭包**：`jmp`、`split`、`save`、`assert` 都不消耗字符。把一个线程加入列表时，要立即沿这些指令走到底，直到遇到 `char`、`any`、`class` 或 `match`。
4. **去重：同一个输入位置上，每个 pc 至多保留一个线程。** 这是整个算法的关键，有两层作用：
   - **复杂度**：线程数不超过程序长度 $m$，所以总时间为 $O(nm)$；
   - **语义**：同一位置、同一 pc 的两个线程，未来的行为完全相同，能接受的后缀一样。列表中先到的线程优先级更高，所有平局都由它胜出，所以后到的线程可以直接丢弃，即使它携带不同的捕获值。
5. **优先级 = 列表顺序。** `split x, y` 先展开 x，再展开 y。
6. **截断**：某个线程到达 `match` 时，记录结果，并**丢弃列表中排在它后面的所有线程**，因为它们优先级更低。排在前面的线程继续运行，它们日后的匹配会覆盖当前结果。

### 5.2 实现

完整代码见 `regexlab/pikevm.py`。ε 闭包用显式栈实现，深层嵌套不会压垮调用栈：

```python
def pike_vm(prog, ngroups, text, pos=0, anchored=False, end=None):
    n = len(text)
    limit = n if end is None else end
    nslots = 2 * (ngroups + 1)
    seen = [-1] * len(prog)            # seen[pc] == 位置戳，免去每步清空
    matched = None
    if end is not None:
        anchored = True

    def add(lst, pc, caps, at):
        """把线程及其 ε 闭包按优先级顺序加入 lst。"""
        stack = [(pc, caps)]
        while stack:
            pc, caps = stack.pop()
            if seen[pc] == at:
                continue                        # 本位置已有更高优先级的线程到过这里
            seen[pc] = at
            op = prog[pc]
            k = op[0]
            if k == 'jmp':
                stack.append((op[1], caps))
            elif k == 'split':
                stack.append((op[2], caps))     # 后压入的先弹出，
                stack.append((op[1], caps))     # 所以 op[1] 优先
            elif k == 'save':
                if op[1] < nslots:              # 只追踪调用者需要的槽
                    c = list(caps); c[op[1]] = at; caps = tuple(c)
                stack.append((pc + 1, caps))
            elif k == 'assert':
                if assert_ok(op[1], text, at):
                    stack.append((pc + 1, caps))
            else:                               # char / any / class / match
                lst.append((pc, caps))

    clist = []
    for at in range(pos, limit + 1):
        # 尚未找到匹配时，在每个位置以最低优先级启动一个新线程（隐式的 .*? 前缀）
        if matched is None and (not anchored or at == pos):
            add(clist, 0, (None,) * nslots, at)
        if not clist and (matched is not None or anchored):
            break
        ch = text[at] if at < limit else None
        nlist = []
        for pc, caps in clist:
            op = prog[pc]
            if op[0] == 'match':
                if end is not None and at != end:
                    continue                    # 区间模式：提前到达的匹配优先级必然更低（5.6 节）
                matched = caps
                break                           # 截断：丢弃更低优先级的线程
            if consumes(op, ch):
                add(nlist, pc + 1, caps, at + 1)
        clist = nlist
    return matched
```

有两个容易写错的地方。

**`seen` 用位置戳，而不是每步清空。** 处理位置 `at` 时，`clist` 的闭包标记为 `at`，向 `nlist` 添加线程时标记为 `at + 1`，两者互不干扰。RE2 用的是另一种方案，即 Briggs–Torczon **稀疏集合**，同样能 $O(1)$ 清空，还能保持插入顺序。

**提前退出的条件。** `clist` 为空时不能无条件退出。比如 `\ba`，在某个位置上 `\b` 不成立，新注入的线程会立即死亡，`clist` 变空，但后面的位置仍可能匹配。只有在已经找到匹配，或者是锚定搜索时，空列表才意味着“不会再有匹配”。无条件退出是一个很容易犯的错误，而且手写用例很难发现它。第 15 章的随机测试只要把 `^`、`$` 也当作原子参与生成，就能立刻抓到它，最小反例是 `($)` 匹配 `"a"`：正确答案是 `(1, 1)`，错误实现返回 `None`。

### 5.3 运行

```text
a(b|c)*d             'xxabcbd'       -> [(2, 7), (5, 6)]        # 第 1 组取最后一次迭代的 "b"
a(.*)b               'aXbYb'         -> [(0, 5), (1, 4)]        # 贪婪：第 1 组为 "XbY"
a(.*?)b              'aXbYb'         -> [(0, 3), (1, 2)]        # 非贪婪：第 1 组为 "X"
(a+)+$               'aaaaaaaaaaaa'  -> None                    # a^30 b：瞬间返回
(a*)*                'b'             -> [(0, 0), (None, None)]  # 与 Python 不同，见 5.4 节
(a|ab)(c|bcd)(d*)    'abcd'          -> [(0, 4), (0, 1), (1, 4), (4, 4)]
```

以非贪婪的例子为例，看截断是怎么起作用的。在位置 2 读到 `b` 后，有两个线程存活：一个是“退出 `.*?` 并匹配 `b`”，另一个是“继续 `.*?`”。由于是非贪婪的，前者优先级更高。到位置 3 时，前者走到 `match`，排在它后面的“继续”线程被截断，结果停在 `(0, 3)`。在贪婪版本中两者的顺序相反，“继续”线程排在前面而得以存活，最终在位置 5 产生了更长的匹配，覆盖了早先的结果。

### 5.4 回到空循环

用 `(a*)*` 匹配 `"b"`，跟踪一遍 `add` 的展开过程。程序如下：

```text
  0  save    0
  1  split   2 8       # 外层 *
  2  save    2
  3  split   4 6       # 内层 *
  4  char    a
  5  jmp     3
  6  save    3
  7  jmp     1         # 没有消耗任何字符就回到了外层 split
  8  save    1
  9  match
```


1. `save 0`，到达外层 `split`（记入 seen），优先进入循环体；
2. `save 2`，到达内层 `split`：`char a` 被加入列表，退出分支继续展开；
3. `save 3`，`jmp` 回到外层 `split`。它**已经 seen**，这条路径被丢弃，ε 环就此断开；
4. 回到外层 `split` 的第二个分支：`save 1`，然后 `match`。

结论有两点：

- **不会死循环。** `seen` 保证每个 pc 在每个位置只展开一次，任何 ε 环都会自动终止；
- **但捕获结果是 `group 1 = None`。** 第 3 步中那条“进入一次循环体、匹配空串后退出”的路径被丢弃了，存活下来的是“一次也没进入循环体”的路径。Perl 和 Python 在这里报告 `""`（位置 0–0），因为它们的规则是“允许进入一次，但空迭代后退出循环”（第 3.2 节）。

第 3.2 节的 `^b.(?:(?:[ab])*?)*` 上，Pike VM 给出的是 `(0, 3)`，与 Perl 的 `(0, 2)` 和“空迭代即失败”的 `(0, 7)` 都不同。三种引擎对同一个模式给出三种整体匹配，原因都在“如何打断 ε 环”。第 15 章的差分测试统计了这类差异出现的频率，第 13 章讨论各家工业引擎的取舍。

### 5.5 BitState：用记忆化换回线性时间

Pike VM 的常数很大：每个字符都要遍历全部活跃线程，还要复制捕获元组。对于**短文本**，有一个更快的选择：在回溯器上加记忆化。

先把第 3 章的回溯器改写成在**程序**上运行的显式栈版本：

```python
def backtrack_prog(prog, ngroups, text, pos=0, memo=True, budget=None, anchored=False, end=None):
    ...
    visited = bytearray(len(prog) * (limit + 1)) if memo else None
    for start in starts:
        stack = [(0, start, (None,) * nslots)]
        while stack:
            pc, at, caps = stack.pop()
            while True:                         # 沿一条路径一直走，直到失败
                if visited is not None:
                    key = pc * (limit + 1) + at
                    if visited[key]:
                        break                   # (pc, at) 已试过且失败
                    visited[key] = 1
                op = prog[pc]
                k = op[0]
                if k in ('char', 'any', 'class'):
                    if at < limit and consumes(op, text[at]):
                        pc += 1; at += 1; continue
                    break
                if k == 'split':
                    stack.append((op[2], at, caps))   # 低优先级分支留待回溯
                    pc = op[1]; continue
                ...
                if k == 'match':
                    return caps, steps
    return None, steps
```

`split` 的处理是：把 y 压栈，然后立即沿 x 前进。`split` 的优先级语义被直接翻译成了搜索顺序。

记忆化之所以成立，依据是：

> **在不含反向引用的程序里，从 (pc, pos) 出发能否最终到达 `match`，只取决于 pc 和 pos，与捕获值和来路无关。**

回溯器按优先级顺序搜索，一旦成功就立即返回。所以如果某个 (pc, pos) 被**第二次**访问，说明第一次从这里出发的搜索已经失败了，可以直接剪枝。

更进一步，这个位图**可以在不同起点之间共享**：从起点 3 走到 (pc, pos) 失败了，从起点 5 走到同一个 (pc, pos) 照样会失败。程序中依赖起点的只有 `save 0`，而它不影响成败。所以总访问次数不超过 $m \times (n+1)$，整体复杂度为 $O(nm)$。

实测 `(a+)+$` 匹配 $a^n b$：

```text
BitState 步数：
  n=    10  steps=          96  len(prog)*(n+2)=         108
  n=   100  steps=         906  len(prog)*(n+2)=         918
  n=  1000  steps=       9,006  len(prog)*(n+2)=       9,018
  n= 10000  steps=      90,006  len(prog)*(n+2)=      90,018
不带记忆化的程序回溯（同一模式）：
  n= 10  steps=      14,288
  n= 14  steps=     229,312
  n= 18  steps=   3,669,936
```

步数严格不超过 $m(n+1)$ 这个上界。不带记忆化时，n 每增加 4，步数约乘 16。

位图还顺带解决了空循环问题：ε 环会在第二次进入同一 (pc, pos) 时被切断，语义与 Pike VM 一致。第 15 章的测试中，BitState 与 Pike VM 在全部 113,760 个用例上捕获组完全相同。

代价是**空间**：位图有 $m(n+1)$ 位，与文本长度成正比。所以各家都只在“程序 × 文本”足够小时才启用它：

| 实现 | 名称 | 位图上限 |
|---|---|---|
| RE2 | `BitState` | 256 Kbit |
| Go | `backtrack.go` | 程序 ≤ 500 条指令，且位图 ≤ 256 Kbit |
| Rust `regex-automata` | `BoundedBacktracker` | `visited_capacity`，默认 256 KB |
| `regexlab` | `backtrack_prog(memo=True)` | 元引擎中 `bt_limit = 256 * 1024` |

典型场景是：DFA 已经找出了匹配区间，只需在这一小段上提取捕获组（第 10 章）。

### 5.6 在已知区间内求捕获组

第 10 章的三段式搜索会先用 DFA 求出匹配区间 $[s, e]$，然后只在这个区间里求捕获组。`pike_vm` 的 `end` 参数就是为此准备的：从 $s$ 锚定开始，只读到 $e$，只接受恰好在 $e$ 到达的 `match`。

有一个细节：在 $e$ 之前到达 `match` 的线程，**不能**像普通 Pike VM 那样截断它之后的线程，只能直接丢弃它。理由如下。如果这个线程的优先级高于真正的匹配路径，它就会截断那条路径，leftmost-first 的终点就不会是 $e$，与前提矛盾。所以它的优先级一定更低，丢弃即可。只有在位置 $e$，按优先级第一个到达 `match` 的线程才是结果。

### 5.7 复杂度与工程代价

| 项目 | Pike VM | BitState |
|---|---|---|
| 时间 | $O(nm)$ 次线程操作，与模式写得好不好无关 | $O(nm)$ |
| 每次 `save` | 复制捕获数组，$O(k)$ | 同左，但只沿一条路径 |
| 额外空间 | 两个线程列表加 `seen`，$O(mk)$ | $O(nm)$ 位 |
| 常数 | 大 | 小 |

$O(nm)$ 是**保证**，但常数不小。实测中，Pike VM 通常比 DFA 慢一个数量级以上（第 6 章、第 12 章附表）。减少捕获复制开销的常用技巧有：

- **写时复制加引用计数**：RE2 的 NFA 线程共享捕获数组，只在 `save` 时复制；
- **只追踪必要的槽**：调用者只要整体匹配时，只保留槽 0、1。`regexlab` 的 `pike_search` 就传 `ngroups=0`；
- **按状态预分配槽位**：Rust 的 `PikeVM` 把捕获存放在按状态索引的二维表 `SlotTable` 里，避免分配。

所以工业引擎的典型做法是分层执行：先用 DFA 判断是否匹配并求出区间（第 6、10 章），只有需要捕获组时才在区间内运行 Pike VM 或 BitState；如果模式满足 one-pass 条件，就改用 OnePass DFA（第 10 章）。

### 5.8 最左优先与最左最长

截断规则实现的是 **leftmost-first**（Perl 语义）。POSIX 要求的是 **leftmost-longest**：

```text
模式 a|ab，文本 "ab"
  leftmost-first   →  "a"
  leftmost-longest →  "ab"
```

让 Pike VM 支持最左最长，看起来只要“不截断，并保留最长的匹配”。但 POSIX 对**子匹配**也有逐级取最长的规则，按 pc 去重会错误地丢弃某些线程：同 pc 的两个线程捕获不同，按 POSIX 规则未必是先到者胜出。正确实现需要在去重时比较捕获向量。这是 TRE、musl 等 POSIX 引擎最微妙的部分，第 13 章再回到这个话题。

### 5.9 练习

1. 增加 `findall`：找到一个匹配后，从其结束位置继续搜索。注意空匹配，例如 `a*` 匹配 `"baa"`：结束位置必须至少前进一个字符，否则会无限循环。`regexlab` 的结果是 `[(0, 0), (1, 3)]`，与 Python 的 `['', 'aa', '']` 不同，原因见第 13 章。
2. 支持多行模式：`bol` 在 `pos == 0` 或 `text[pos-1] == '\n'` 时成立，`eol` 相应修改。
3. `\b` 需要同时查看 `text[pos-1]` 和 `text[pos]`。说明为什么它仍然可以在 `add` 中处理，而 DFA 处理它时需要额外的状态（第 11 章）。
4. 统计每一步的活跃线程数，验证它不超过 `len(prog)`。
5. 把 `seen` 改成 Briggs–Torczon 稀疏集合，同时用它保存 `clist`，比较两种实现的速度。

---
## 第 6 章　DFA：子集构造、惰性 DFA 与最小化

回顾 Pike VM。每个输入位置上的那组线程虽然各自带着捕获值，但**决定未来能否匹配的只有它们的 pc 集合**。所以可以把每一种可能出现的 pc 集合预先算好，把“集合 + 字符 → 新集合”做成一张表。匹配时，每读一个字符只需查一次表，不再遍历线程。

这就是 Rabin 与 Scott 在 1959 年给出的**子集构造**（powerset construction）。代价也随之而来：

- **捕获组丢失**：状态里只有 pc，没有位置信息；
- **优先级丢失**：集合是无序的，`split` 两个分支的先后顺序不复存在；
- **状态数可能指数爆炸**：$m$ 条指令最多对应 $2^m$ 个子集。

本章先构造一个只回答“是否匹配”的完全 DFA，再讨论状态爆炸与最小化，然后用**惰性 DFA**同时解决爆炸问题和优先级问题，最后构造**反向程序**，为第 10 章的三段式搜索做准备。

### 6.1 三个前置问题

**1. 字母表太大：字符等价类。** Unicode 有 110 多万个码点，不可能给每个状态开一行这么宽的表。但程序里真正“被区分”的字符很少：对 `[a-z]x` 来说，`b` 和 `q` 的行为完全相同。把所有 `char`、`any`、`class` 指令的区间端点收集起来，就能切出若干个**等价类**，同一类内的字符在任何指令下的表现都一样：

```python
def class_starts(prog):
    cuts = {0}
    def add(lo, hi):
        cuts.add(lo)
        if hi + 1 < MAXCP:
            cuts.add(hi + 1)
    for op in prog:
        if op[0] == 'char':    add(ord(op[1]), ord(op[1]))
        elif op[0] == 'any':   add(10, 10)                 # '\n' 自成一类
        elif op[0] == 'class':
            for lo, hi in op[1]:
                add(ord(lo), ord(hi))
    return sorted(cuts)
```

`[a-z]x` 的实际结果是 5 个等价类，起点分别为 `'\x00'`、`'a'`、`'x'`、`'y'`、`'{'`。表的宽度从 110 多万列缩小到 5 列。RE2 和 Rust 在**字节**上运行 DFA，等价类最多 256 个，称为 *byte classes*。

**2. 非锚定搜索。** Pike VM 在每个位置以最低优先级注入一个新线程。DFA 中对应的做法是：每次转移后，把“从 pc 0 出发的闭包”并入新状态。由于不再区分优先级，这等价于在模式前加上 `.*`。

**3. 断言。** `^` 只在位置 0 成立，所以初始闭包以 `at_start=True` 计算，后续注入的闭包以 `at_start=False` 计算。`$` 更麻烦：读入字符时还不知道后面是否就是文本末尾。我们把遇到的 `assert eol` 指令**原样留在状态集合里**，作为“悬而未决”的线程。它不消耗字符，所以在下一次转移中自然死亡；只有在文本结束时，才以 `at_end=True` 再展开一次。

### 6.2 实现

完整代码见 `regexlab/dfa.py`：

```python
def closure(prog, pcs, at_start, at_end):
    """无序 ε 闭包，只保留消耗字符的指令、match 和悬而未决的 eol。"""
    out, seen, stack = set(), set(), list(pcs)
    while stack:
        pc = stack.pop()
        if pc in seen:
            continue
        seen.add(pc)
        op = prog[pc]
        k = op[0]
        if k == 'jmp':        stack.append(op[1])
        elif k == 'split':    stack += [op[1], op[2]]
        elif k == 'save':     stack.append(pc + 1)          # DFA 不关心捕获
        elif k == 'assert':
            if op[1] == 'bol':
                if at_start: stack.append(pc + 1)
            elif at_end:      stack.append(pc + 1)
            else:             out.add(pc)                   # eol：留待文本结束时裁决
        else:
            out.add(pc)
    return frozenset(out)

class DFA:
    def __init__(self, prog, anchored=False, max_states=100_000):
        self.starts = class_starts(prog)
        reps = [chr(c) for c in self.starts]       # 每个等价类取一个代表字符
        inject = frozenset() if anchored else closure(prog, [0], False, False)
        start = closure(prog, [0], True, False)
        index, sets, self.table = {start: 0}, [start], []
        i = 0
        while i < len(sets):                       # BFS 生成所有可达状态
            S = sets[i]
            row = []
            for rep in reps:
                T = closure(prog, step(prog, S, rep), False, False) | inject
                if T not in index:
                    if len(sets) >= max_states:
                        raise MemoryError(f"DFA exceeds {max_states} states")
                    index[T] = len(sets)
                    sets.append(T)
                row.append(index[T])
            self.table.append(row)
            i += 1
        match_pc = len(prog) - 1
        self.accept = [match_pc in S for S in sets]
        self.eof_accept = [match_pc in closure(prog, S, False, True) for S in sets]
        self.empty_ok = match_pc in closure(prog, [0], True, True)
        self.dead = index.get(frozenset())

    def is_match(self, text):
        if not text:
            return self.empty_ok                   # ^ 与 $ 同时成立的唯一情形
        s, table, accept = 0, self.table, self.accept
        for ch in text:
            if accept[s]:
                return True                        # 最早匹配：立即停止
            s = table[s][self.cls(ch)]
            if s == self.dead:
                return False
        return self.eof_accept[s]
```

有三处细节值得说明：

- **`empty_ok` 单独计算。** 只有空文本时，位置 0 同时是开头和结尾。如果直接复用 `eof_accept`，`^$` 这类模式在空串上的结果会出错；
- **死状态。** 锚定模式下，所有线程死亡后集合为空，之后不可能再匹配，可以立即返回。非锚定模式每一步都有注入，空集合通常不可达；
- **最早匹配。** 只回答“是否匹配”时，状态中一出现 `match` 就可以返回，不必读完文本。这是 DFA 用于 `is_match` 和预过滤时最快的形态。

实测 `(a|b)*abb`：非锚定 DFA 有 4 个状态、4 个等价类；锚定 DFA 有 5 个状态，其中一个是遇到 a、b 以外字符时的死状态。`(a+)+$` 匹配十万个 `a` 加一个 `b`，每个字符一次查表，与模式结构无关。

### 6.3 状态爆炸

DFA 的问题不在匹配阶段，而在构造阶段。用 `(a|b)*a(a|b){k}` 实测（锚定）：

```text
  k   NFA 指令    DFA 状态   Moore  Hopcroft  Moore(s) Hopcroft(s)
  1       18         5       5         5     0.000       0.000
  2       24         9       9         9     0.000       0.000
  3       30        17      17        17     0.000       0.000
  4       36        33      33        33     0.000       0.000
  5       42        65      65        65     0.000       0.000
  6       48       129     129       129     0.000       0.000
  7       54       257     257       257     0.001       0.001
  8       60       513     513       513     0.001       0.002
  9       66      1025    1025      1025     0.003       0.003
 10       72      2049    2049      2049     0.007       0.006
```

DFA 状态数恰好是 $2^{k+1}+1$（多出的 1 是死状态），而程序只增长了 $6k$ 条指令。最小化之后状态数不变，与第 1.2 节 Myhill–Nerode 论证给出的下界一致：**任何** DFA 都至少需要这么多状态，最小化也无济于事。

这类模式在实践中并不罕见，`[^x]*x.{30}` 或带长计数重复的日志规则都会引起类似的爆炸。工程上有三种对策：

1. **状态上限**：`max_states` 的做法，超过就放弃 DFA，回退到 Pike VM；
2. **惰性构造**：只在实际遇到时才生成状态，并用固定大小的缓存保存。这是 RE2 和 Rust 的主力方案，见 6.5 节；
3. **位并行**：状态集合用一个机器字表示，根本不显式枚举（第 7、12 章）。

### 6.4 最小化

子集构造得到的 DFA 往往有冗余：两个状态对任何后缀的接受行为都相同，却被分成了两个。最小化就是合并这些**等价状态**。

**Moore 算法**是反复细分划分：

1. 初始按接受标志把状态分组；
2. 对每个状态计算签名：（所在块，读入每个等价类后到达的块）。签名相同的留在同一块，否则拆开；
3. 重复第 2 步，直到块数不再增加。

```python
def moore(table, labels):
    ids = {}
    block = [ids.setdefault(l, len(ids)) for l in labels]
    nblocks = len(ids)
    while True:
        ids = {}
        new = [ids.setdefault((block[i], tuple(block[t] for t in row)), len(ids))
               for i, row in enumerate(table)]
        if len(ids) == nblocks:                    # 没有任何块被拆开：已稳定
            return new, nblocks
        block, nblocks = new, len(ids)
```

签名中包含旧的块号，所以新划分一定是旧划分的细化，至多迭代 $s$ 轮。每轮代价 $O(s\sigma)$，其中 $s$ 是状态数，$\sigma$ 是等价类数，总复杂度 $O(s^2\sigma)$。

**Hopcroft 算法**（1971）把复杂度降到 $O(s\sigma\log s)$。它维护一个“待处理的分割者”集合，用每个分割者 $A$ 和每个字符 $c$ 去切分其他块。关键技巧是**处理较小的一半**：一个块被拆成两半时，如果它已经在待处理集合里，两半都放进去；否则只放较小的那一半。每个状态至多参与 $\log s$ 次切分，由此得到对数因子。

```python
def hopcroft(table, labels):
    ...
    while work:
        A = blocks[work.pop()]
        for c in range(sigma):
            X = {s for t in A for s in inv[c][t]}   # 读入 c 后落入 A 的状态
            for b, inter in group_by_block(X):
                Y = blocks[b]
                if len(inter) == len(Y):
                    continue
                rest = Y - inter                     # 把 Y 拆成 inter 与 rest
                blocks[b], blocks[nb] = inter, rest
                if b in work:
                    work.add(nb)
                else:                                # 只把较小的一半放进工作集
                    work.add(b if len(inter) <= len(rest) else nb)
```

上表中两种算法得到的块数完全相同。第 15 章的测试对每个随机模式都核对了这一点。在状态数只有几千的规模上，两者的耗时都可以忽略；状态数达到数十万时，对数因子才显出优势。

**Brzozowski 算法**是一个优雅的替代：把 DFA 反转、确定化，再反转、确定化一次，结果必然是最小 DFA。它的最坏复杂度是指数级的，但在某些输入上表现意外地好。

**正则引擎很少真正做最小化。** 最小化需要先构造完整的 DFA，而惰性 DFA 恰恰回避了完整构造。最小化主要用于预先编译、需要序列化保存的场景：Rust `regex-automata` 的 `dense::DFA` 提供可选的 `minimize`，词法分析器生成器 flex 和 re2c 也会做（第 8 章）。

### 6.5 惰性 DFA

6.3 节的反例有 $2^{k+1}$ 个可达状态，但扫描一段长度为 $n$ 的文本时，DFA 只会经过 $n+1$ 个状态。所以：

- **最坏情况**：每读一个字符都遇到新状态，需要 $O(m)$ 时间计算，总时间退化为 $O(nm)$，与 Pike VM 同阶；
- **典型情况**：文本反复落入少数几个状态，几乎所有转移都命中缓存，每字符 $O(1)$。

惰性 DFA 把“构造时的指数风险”变成了“运行时的线性风险”，剩下的问题只是**内存**。

#### 6.5.1 把优先级编进状态

完全 DFA 用无序集合作状态，只能回答“是否匹配”。要得到 leftmost-first 的匹配终点，DFA 必须复现 Pike VM 的三条规则：

1. **线程有序**：闭包按 `split` 的优先级做深度优先展开，先到者优先级更高；
2. **遇到 `match` 就截断**：闭包中一旦出现 `match`，排在它后面的线程全部丢弃；
3. **找到匹配后停止注入**：一旦已经找到匹配，后面起点的匹配不可能比它更靠左，就不再注入新线程。

这三条都只依赖“当前线程的有序 pc 序列”和“是否已经见过匹配”。所以只要把状态定义为

```text
状态 = (有序 pc 元组, 是否已见过匹配)
```

子集构造照样成立。代价是同一集合的不同排列会成为不同的状态。扫描过程中，**每当状态里含有 `match`，就把当前位置记为候选终点**，然后继续扫描，直到死状态或文本结束。最后记下的位置就是 leftmost-first 的匹配终点。

```python
def closure(self, roots, at_start, at_end):
    """有序 ε 闭包。roots 按优先级从高到低排列，共享同一个 seen。"""
    prog, out, seen = self.prog, [], set()
    for root in roots:
        stack = [root]
        while stack:
            pc = stack.pop()
            if pc in seen:
                continue
            seen.add(pc)
            op = prog[pc]
            k = op[0]
            if k == 'jmp':     stack.append(op[1])
            elif k == 'split':
                stack.append(op[2])           # 后压入低优先级
                stack.append(op[1])           # 先弹出高优先级
            elif ...                          # save / assert 同 6.2 节
            else:
                out.append(pc)
                if k == 'match' and not self.longest:
                    return tuple(out)         # 规则 2：截断
    return tuple(sorted(out)) if self.longest else tuple(out)

def compute(self, key, rep):
    S, matched = key
    nxt = step(self.prog, S, rep)             # 保持顺序
    inject = not (self.anchored or matched)   # 规则 3
    T = self.closure(nxt + [0] if inject else nxt, False, False)   # 新线程优先级最低
    return (T, self.flag(matched, T))
```

`longest=True` 是给反向扫描用的（6.6 节）：此时只需要最长匹配，状态退化为无序集合，不截断。

#### 6.5.2 缓存、清空与放弃

转移表的每一项初始为 `None`，表示尚未计算。状态在第一次需要时才计算并登记：

```python
for i, ch in enumerate(text):
    c = bisect_right(starts, ord(ch)) - 1
    t = self.trans[s][c]
    if t is None:                             # 缓存未命中：现算
        key = self.compute(self.keys[s], self.reps[c])
        if key not in self.ids and len(self.keys) >= self.max_states:
            clears += 1
            if clears >= self.min_clears and since < self.min_chars_per_state * self.max_states:
                raise GaveUp(i)               # 缓存几乎没有被复用：放弃
            self.reset()                      # 清空，从当前状态重新开始
            since, s = 0, None
        t = self.intern(key)
        if s is not None:
            self.trans[s][c] = t
    s = t
    since += 1
    if self.dead[s]:
        return last                           # 所有线程死亡，不会再有匹配
    if self.acc[s]:
        last = i + 1
```

**清空缓存时为什么不会丢失进度？** 惰性 DFA 的状态完全由它的键 `(pc 元组, matched)` 决定，转移表只是记忆化的结果。清空之后，只要把当前状态的键重新登记一次，扫描就能无缝继续。代价只是之前算过的转移需要重算。

**放弃的启发式。** 如果缓存反复被填满，而平均每个状态只服务了寥寥几个字符，说明惰性 DFA 在做 Pike VM 的工作，还额外承担了哈希和分配的开销。这时应主动放弃，回退到 Pike VM。RE2 和 Rust `regex-automata` 的 hybrid DFA 都用类似的规则，Rust 中对应的配置是 `minimum_cache_clear_count` 和 `minimum_bytes_per_state`。

实测：`(a|b)*a(a|b){k}c` 在 2 万个随机 a/b 上搜索。模式不会匹配，必须读完全文。`max_states = 1000`：

```text
  k    最小DFA状态     生成状态   清空    放弃?    三段式(s) PikeVM(s)
  3         16       16    0      否     0.003     0.054
  6        128      128    0      否     0.004     0.077
  8        512      512    0      否     0.008     0.094
  9       1024     3000    3      是     0.135     0.105
 12       8192     3000    3      是     0.150     0.123
```

- $k \le 8$ 时，需要的状态全部装进缓存，惰性 DFA 比 Pike VM 快 10 到 20 倍；
- $k = 9$ 时，需要的状态略多于缓存容量，连续三次清空后放弃，回退到 Pike VM，总耗时比直接用 Pike VM 稍长。这就是放弃启发式要避免的局面：如果不放弃，惰性 DFA 会在每个字符上都重算状态。

缓存大小的选择因此很关键。RE2 把 `max_mem`（默认 8 MB）的约三分之二分给正向程序及其 DFA 缓存，其余留给反向程序。Rust 的 hybrid DFA 缓存默认容量约 2 MB。

### 6.6 反向程序

正向 DFA 只告诉我们匹配在哪里**结束**。要知道它从哪里**开始**，就从终点往回扫描，这需要一个识别“反转语言”的程序：$L(\mathrm{rev}) = \{\, s^R \mid s \in L(\mathrm{prog}) \,\}$。

反转可以在 AST 上做（交换连接的顺序），也可以直接在编译好的程序上做，后者不依赖语法树的具体形式。思路是把程序看成一张图，把边反向：

- 正向从 `q` 消耗一个字符到达 `q+1`，反向则从 `q+1` 消耗同样的字符回到 `q`；
- ε 边（`jmp`、`split`、`save`）直接反向；
- 断言反向时要交换 `bol` 和 `eol`，因为文本的开头和结尾在反向扫描时互换了；
- 反向的起点是正向的 `match`，终点是正向的 pc 0。

对每个正向 pc `p`，生成一个代码块 `B(p)`，用一串 `split` 列出它的所有前驱：

```python
def reverse_prog(prog):
    M = len(prog) - 1
    preds = [[] for _ in prog]
    for q, op in enumerate(prog):
        if op[0] == 'jmp':     preds[op[1]].append(q)
        elif op[0] == 'split': preds[op[1]].append(q); preds[op[2]].append(q)
        elif op[0] != 'match': preds[q + 1].append(q)
    swap = {'bol': 'eol', 'eol': 'bol', 'wordb': 'wordb', 'nwordb': 'nwordb'}
    out, label = [], {}
    for p in [M] + list(range(M)):                   # B(M) 放在开头，作为反向起点
        label[p] = len(out)
        alts = [('edge', q) for q in preds[p]]
        if p == 0:
            alts.append(('accept', None))            # 回到正向起点：反向匹配成功
        if not alts:
            out.append(('class', (), False))         # 没有前驱：永不成立的死指令
            continue
        for i, (kind, q) in enumerate(alts):
            last_alt = (i == len(alts) - 1)
            if not last_alt:
                sp = len(out); out.append(None)      # 稍后回填 split
            if kind == 'accept':
                out.append(('jmp', 'MATCH'))
            else:
                op = prog[q]
                if op[0] in ('char', 'any', 'class'):
                    out.append(op)                   # 消耗同一个字符
                elif op[0] == 'assert':
                    out.append(('assert', swap[op[1]]))
                out.append(('jmp', q))               # 继续寻找 q 的前驱
            if not last_alt:
                out[sp] = ('split', sp + 1, len(out))
    ...                                              # 把符号目标改写为真实地址，末尾追加 match
```

`ab|cd` 的反向程序（实际输出）：

```text
  0  jmp     11        # B(match) → B(save 1)
  1  jmp     15        # B(0)：到达正向起点 → match
  2  jmp     1
  3  jmp     2
  4  char    a
  5  jmp     3
  6  char    b
  7  jmp     4
  8  jmp     2
  9  char    c
 10  jmp     8
 11  split   12 13     # B(save 1)：两个前驱，jmp（b 分支之后）与 char d
 12  jmp     6
 13  char    d
 14  jmp     9
 15  match
```

正向程序的每条边在反向程序中最多产生 3 条指令，所以反向程序仍是 $O(m)$。反向程序中各分支的优先级没有意义，因为第 10 章会用“最长匹配”模式运行它。

**自检方法**：对任意模式 `p` 和字符串 `s`，`fullmatch(p, s)` 应当等于 `fullmatch(reverse_prog(p), s[::-1])`。第 15 章对每个随机模式都检验了这条性质。

### 6.7 工程实现要点

真实引擎在表的布局上会花很多心思：

- **预乘状态编号。** 把状态编号直接存为 `state * nclasses`，内层循环变成 `s = table[s + cls[byte]]`，省去一次乘法。Rust `regex-automata` 的 dense DFA 就这样做；
- **特殊状态集中编号。** 把死状态、接受状态、需要特殊处理的状态安排在编号最小的区间里，循环中只需一次比较 `if s <= MAX_SPECIAL` 就能判断是否要跳出快速路径；
- **按字节而非码点运行。** 把 UTF-8 解码编进自动机本身（第 11 章），等价类表只有 256 项，查表不需要二分，内层循环里也没有解码分支；
- **循环展开。** 一次处理 4 个字节，只在展开块的末尾检查特殊状态。

这些手段加在一起，DFA 的内层循环可以接近每字节一个时钟周期，比 Pike VM 快一到两个数量级。

### 6.8 DFA 丢掉了什么

| 丢失的信息 | 后果 | 找回的方法 |
|---|---|---|
| 线程优先级 | 无法实现 leftmost-first | 有序状态加截断（6.5.1 节） |
| 匹配的起点 | 不知道匹配从哪里开始 | 正向找终点，再用反向 DFA 往回扫描（6.6 节、第 10 章） |
| 捕获组 | 无法提取子匹配 | 在已确定的区间内运行 Pike VM 或 BitState（第 5、10 章）；或者用带标签的 DFA（第 8 章 re2c） |

### 6.9 练习

1. 在 $k$ 较小时用 `minimize_dfa` 验证：`(a|b)*a(a|b){k}` 最小化后的状态数确实等于 $2^{k+1}+1$。若把字母表限制为 `{a, b}`（不出现死状态），结果是多少？
2. 支持多行模式。提示：`bol` 是否成立取决于**上一个字符**，所以状态需要额外记住“上一个字符是否为 `\n`”。RE2 把这类信息编成状态的标志位。
3. 修改 `DFA`，让等价类在字节上计算：先把文本编码成 UTF-8，再思考为什么 `class` 指令此时不能简单地按码点区间判断（第 11 章）。
4. 用有序元组代替 `frozenset` 实现完全 DFA，并用随机测试验证：对任意模式和文本，它报告的匹配终点与 Pike VM 一致。比较两种 DFA 的状态数。
5. 用 Brzozowski 的“两次反转加确定化”实现最小化，与 Hopcroft 的结果对拍。

---
## 第 7 章　直接构造 DFA：followpos、Glushkov 与 Brzozowski 导数

第 4–6 章走的是“两步走”的路线：先用 Thompson 构造得到带 ε 边的 NFA，再用子集构造得到 DFA。这条路线清晰、通用，但多了一个中间产物。ε 边本身不对应任何输入，子集构造的大部分工作其实都花在 ε 闭包上。

本章介绍三种**不经过 ε-NFA** 的构造：

1. **followpos 构造**（龙书 3.9 节）：在语法树上计算几个集合，直接得到 DFA；
2. **Glushkov 自动机**（位置自动机）：没有 ε 边的 NFA，状态数恰好是字符出现次数加一，适合位并行；
3. **Brzozowski 导数**：把“读入一个字符之后还剩什么要匹配”本身当作状态，天然支持交集与补集。

它们看似出发点不同，实际上关系密切。读完本章你会看到，它们只是从不同角度描述同一个对象。代码见 `regexlab/direct.py`。

### 7.1 位置与线性化

给正则表达式中的**每一次字符出现**编一个号，称为**位置**（position）：

```text
(a|b)*abb
 1 2  345
```

同一个字符 `a` 出现了两次，分别是位置 1 和位置 3。编号之后，每个位置只出现一次，这样的表达式称为**线性化**的表达式。线性化的好处是：“刚读完的字符来自哪个位置”是唯一确定的，这个信息足以充当自动机的状态。

字符类 `[ab]`、`.` 也各算一个位置，只是这个位置能接受多个字符。代码中每个位置带一个区间表示的字符集合 `CSet`，构造 DFA 时同样使用第 6 章的全局字符等价类。

### 7.2 四个函数

对语法树的每个节点 $n$ 定义：

- **nullable(n)**：$n$ 能否匹配空串；
- **firstpos(n)**：$n$ 匹配的串中，可能作为**第一个**字符的位置集合；
- **lastpos(n)**：可能作为**最后一个**字符的位置集合；
- **followpos(p)**：对每个位置 $p$，在某个匹配串中可能**紧跟在 $p$ 之后**的位置集合。

前三个函数自底向上计算：

| 节点 | nullable | firstpos | lastpos |
|---|---|---|---|
| ε | 真 | ∅ | ∅ |
| 位置 $p$ | 假 | $\{p\}$ | $\{p\}$ |
| $r \mid s$ | $\nu(r) \lor \nu(s)$ | $f(r)\cup f(s)$ | $l(r)\cup l(s)$ |
| $r\,s$ | $\nu(r) \land \nu(s)$ | $\nu(r)\ ?\ f(r)\cup f(s) : f(r)$ | $\nu(s)\ ?\ l(r)\cup l(s) : l(s)$ |
| $r^*$ | 真 | $f(r)$ | $l(r)$ |

followpos 只在两处产生：

- **连接 $r\,s$**：对 lastpos(r) 中的每个 $p$，把 firstpos(s) 加入 followpos(p)。$r$ 的最后一个字符之后，可以紧跟 $s$ 的第一个字符；
- **星号 $r^*$**：对 lastpos(r) 中的每个 $p$，把 firstpos(r) 加入 followpos(p)。一次迭代结束后，可以紧接着开始下一次。

`r+` 转换为 `r r*`，`r?` 转换为 `r | ε`。注意 `r+` 会把 `r` 复制一份，它的位置也被重复编号。这不影响正确性，只是位置变多了。

```python
def analyze(n, syms, follow):
    """返回 (nullable, firstpos, lastpos)；顺带给位置编号并填写 followpos。"""
    if isinstance(n, Eps):
        return True, frozenset(), frozenset()
    if isinstance(n, Sym):
        p = len(syms)
        syms.append(n.chars)
        follow[p] = set()
        return False, frozenset([p]), frozenset([p])
    if isinstance(n, Alt):
        n1, f1, l1 = analyze(n.l, syms, follow)
        n2, f2, l2 = analyze(n.r, syms, follow)
        return n1 or n2, f1 | f2, l1 | l2
    if isinstance(n, Cat):
        n1, f1, l1 = analyze(n.l, syms, follow)
        n2, f2, l2 = analyze(n.r, syms, follow)
        for p in l1:
            follow[p] |= f2
        return n1 and n2, (f1 | f2 if n1 else f1), (l1 | l2 if n2 else l2)
    if isinstance(n, Star):
        _, f, l = analyze(n.r, syms, follow)
        for p in l:
            follow[p] |= f
        return True, f, l
```

### 7.3 从 followpos 到 DFA

在表达式末尾连接一个特殊的**结束标记** `#`，它也占一个位置。于是“匹配结束”就变成了“下一个位置可以是 `#`”。DFA 的每个状态是一个位置集合，含义是“下一个字符可以来自这些位置”：

- 初始状态是 firstpos(root)；
- 状态 $S$ 读入字符 $c$，转移到 $\bigcup\{\mathrm{followpos}(p) \mid p\in S,\ \text{位置 } p \text{ 接受 } c\}$；
- $S$ 包含 `#` 的位置时，$S$ 是接受状态。

整个过程没有 ε 闭包：ε 已经在计算 nullable 和 firstpos 时被消化掉了。

**例：`(a|b)*abb`。** 实际运行结果：

```text
  位置 1 [a]    followpos=[1, 2, 3]
  位置 2 [b]    followpos=[1, 2, 3]
  位置 3 [a]    followpos=[4]
  位置 4 [b]    followpos=[5]
  位置 5 [b]    followpos=[6]
  位置 6 #      followpos=[]
followpos DFA 状态数: 5  状态= [[1, 2, 3], [], [1, 2, 3, 4], [1, 2, 3, 5], [1, 2, 3, 6]]
```

| 状态 | 位置集合 | a | b | 其他字符 | 接受 |
|---|---|---|---|---|---|
| A | {1,2,3} | B | A | ∅ | |
| B | {1,2,3,4} | B | C | ∅ | |
| C | {1,2,3,5} | B | D | ∅ | |
| D | {1,2,3,6} | B | A | ∅ | ✓ |
| ∅ | {} | ∅ | ∅ | ∅ | |

去掉死状态 ∅，正好是 4 个状态，这也是这个语言最小 DFA 的状态数。

**与 Thompson 加子集构造对比。** 龙书用同一个例子演示 Thompson 加子集构造，得到 5 个状态（A–E），其中 A 与 C 等价，最小化后才是 4 个。而 `regexlab` 第 6 章的实现在锚定模式下得到的也是“4 个活状态加 1 个死状态”。区别在于：龙书的子集里包含**所有** NFA 状态，而第 6 章的 `closure` 只保留消耗字符的指令和 `match`。龙书把这类状态称为“重要状态”，并指出只按重要状态判等就能合并一部分等价状态。

即便如此，followpos 构造得到的 DFA **一般也不是最小的**，仍然需要第 6 章的最小化。

### 7.4 Glushkov 自动机

如果不做子集构造，位置本身就可以直接当作 NFA 的状态。这就是 **Glushkov 自动机**，也称**位置自动机**：

- 状态：初始状态 0，加上每个位置 $1\ldots m$；
- 从 0 读入 $c$：到达 firstpos 中能接受 $c$ 的位置；
- 从 $p$ 读入 $c$：到达 followpos(p) 中能接受 $c$ 的位置；
- 接受状态：lastpos 中的所有位置；如果整个表达式可空，0 也是接受状态。

注意状态含义的差别：在 Glushkov 自动机中，状态 $p$ 表示“**刚读完**位置 $p$ 的字符”；在 7.3 节的 DFA 中，状态表示“**下一个**字符可以来自哪些位置”。两者只差一次 followpos。7.3 节的 DFA 恰好是对 Glushkov 自动机做子集构造的结果。

Glushkov 自动机有几条很有用的性质：

1. **没有 ε 边，恰好 $m+1$ 个状态。**
2. **同质性（homogeneous）。** 进入状态 $p$ 的所有边，标签都是位置 $p$ 的字符集合。所以“读入 $c$ 后能到达哪些状态”可以先算出一个只依赖 $c$ 的掩码。这是位并行模拟的基础。
3. **转移数可能是平方级。** `(a₁|a₂|…|aₘ)*` 中每个位置都能跟在任一位置之后，转移数是 $m^2$；Thompson NFA 的转移数始终是 $O(m)$。这是“没有 ε 边”的代价：ε 边本来起到了共享转移的作用。
4. **与确定性表达式的联系。** 如果 Glushkov 自动机本身就是确定的，原表达式称为**一义的**（one-unambiguous，Brüggemann-Klein 与 Wood）。XML DTD 和 XML Schema 要求内容模型满足这一条件，即 XSD 中的“唯一粒子归属”（UPA）约束。所以 XML 验证器可以不做子集构造，直接把 Glushkov 自动机当作 DFA 使用。

此外，对 Thompson NFA 做标准的 ε 消除并删去不可达状态，对常见的构造变体，得到的自动机与 Glushkov 自动机同构。Glushkov 自动机可以看成“ε 已经被消化掉的 Thompson NFA”。

#### 7.4.1 用位掩码模拟

利用同质性，状态集合可以表示成一个整数，第 $p$ 位表示位置 $p$：

- `B[c]`：所有能接受 $c$ 的位置构成的掩码；
- `F[p]`：followpos(p) 的掩码；
- 一步转移：$D' = \left(\bigcup_{p\in D} F[p]\right) \,\&\, B[c]$。

```python
def fullmatch(self, s):
    if not s:
        return self.nullable
    D = self.first & self.char_mask(s[0])
    for c in s[1:]:
        if D == 0:
            return False
        F, x, p = 0, D, 0
        while x:                      # 对 D 中每个置位的 p，合并 F[p]
            if x & 1:
                F |= self.follow[p]
            x >>= 1
            p += 1
        D = F & self.char_mask(c)
    return (D & self.last) != 0
```

`(a|b)*abb` 的实测：5 个位置，`first = 0b111`（位置 1–3），`last = 0b10000`（位置 5）。

内循环要逐位合并 `F[p]`，代价是 $O(m)$。Navarro 与 Raffinot 的做法是把 $D$ 切成若干个 8 位的块，为每块预先计算 256 种取值对应的合并结果，一步转移只需 $\lceil m/8\rceil$ 次查表。当 $m$ 不超过机器字长时，整个状态集合放在一个寄存器里，模拟速度接近 DFA，而且完全不需要构造 DFA。Hyperscan 的 LimEx NFA 引擎就建立在这个思路上（第 10、12 章）。

### 7.5 Brzozowski 导数

前面的方法都以位置为中心。Brzozowski 在 1964 年提出了另一个思路：**不给字符编号，直接对表达式本身做变换。** 语言 $L$ 关于字符 $c$ 的**导数**定义为

$$D_c(L) = \{\, w \mid c\,w \in L \,\}$$

也就是“读入 $c$ 之后，剩下的部分还需要匹配什么”。对字符串 $w = c_1c_2\cdots c_n$，有

$$w \in L \iff \varepsilon \in D_{c_n}(\cdots D_{c_2}(D_{c_1}(L))\cdots)$$

关键在于，导数可以**在正则表达式上按语法直接计算**，结果仍是一个正则表达式：

| $r$ | $\nu(r)$ | $D_c(r)$ |
|---|---|---|
| ∅ | 假 | ∅ |
| ε | 真 | ∅ |
| 字符集 $S$ | 假 | $c\in S\ ?\ \varepsilon : \varnothing$ |
| $r \mid s$ | $\nu(r)\lor\nu(s)$ | $D_c(r) \mid D_c(s)$ |
| $r\,s$ | $\nu(r)\land\nu(s)$ | $D_c(r)\,s \mid (\nu(r)\ ?\ D_c(s) : \varnothing)$ |
| $r^*$ | 真 | $D_c(r)\,r^*$ |
| $r \,\&\, s$ | $\nu(r)\land\nu(s)$ | $D_c(r) \,\&\, D_c(s)$ |
| $\lnot r$ | $\lnot\nu(r)$ | $\lnot D_c(r)$ |

最后两行是导数方法最显著的优势：**交集和补集的规则与并集一样简单。** 在 Thompson 构造中，交集需要构造乘积自动机，补集需要先确定化再翻转接受状态；在导数方法中，它们只是两条普通的改写规则。

#### 7.5.1 终止性与智能构造函数

把每个导数看成一个 DFA 状态，从 $r$ 出发反复求导，就能构造 DFA。问题在于导数会不断变长，例如对 `a*` 连续求导会得到 $\varepsilon\cdot a^*$、$\varnothing\cdot a^* \mid \varepsilon\cdot a^*$ ……它们在语法上各不相同，语言却相同。

Brzozowski 证明：只要把并集的**结合律、交换律、幂等律**（ACI）视为相等，任何表达式的不同导数都只有有限多个，构造一定会终止。工程上，这一点通过**智能构造函数**保证：每次构造新表达式时立即化简。

```python
def alt(*rs):                     # 展开嵌套并集，用集合去重，删去 ∅
    s = _flatten('alt', rs) - {EMPTY}
    if not s:
        return EMPTY
    return next(iter(s)) if len(s) == 1 else ('alt', frozenset(s))

def cat(a, b):
    if a == EMPTY or b == EMPTY: return EMPTY
    if a == EPS: return b
    if b == EPS: return a
    if a[0] == 'cat':             # 统一成右结合
        return cat(a[1], cat(a[2], b))
    return ('cat', a, b)

def deriv(c, r):
    k = r[0]
    if k in ('empty', 'eps'): return EMPTY
    if k == 'sym':  return EPS if sym_accepts(r, c) else EMPTY
    if k == 'alt':  return alt(*(deriv(c, x) for x in r[1]))
    if k == 'and':  return and_(*(deriv(c, x) for x in r[1]))
    if k == 'cat':
        d = cat(deriv(c, r[1]), r[2])
        return alt(d, deriv(c, r[2])) if d_nullable(r[1]) else d
    if k == 'star': return cat(deriv(c, r[1]), r)
    if k == 'not':  return not_(deriv(c, r[1]))
```

#### 7.5.2 字母表与示例

字母表可能很大，不可能逐个字符求导。一个简单而正确的观察是：**表达式中从未出现过的字符，行为完全相同。** 所以只对出现过的字符逐个求导，再用一个代表 `OTHER` 处理其余所有字符。

**交集与补集：** “包含 `ab`、但不包含 `ba`”的串：

```python
r = and_(contains('ab'), not_(contains('ba')))
dd = DerivDFA(r)
```

```text
“含 ab 且不含 ba” 导数 DFA 状态数 12
{'ab': True, 'aab': True, 'abb': True, 'aba': False, 'bab': False, 'xaby': True, 'ba': False, '': False}
```

12 个状态没有经过最小化，ACI 只能识别一部分等价的表达式。用 Thompson 构造实现同样的功能，就必须先对 `.*ba.*` 做子集构造，翻转接受状态，再与 `.*ab.*` 的自动机求乘积。

**语言等价判定：** $r \equiv s$ 当且仅当 $(r \,\&\, \lnot s) \mid (s \,\&\, \lnot r)$ 的 DFA 没有可达的接受状态：

```text
  equivalent((a|b)*, (a*b*)*) = True
  equivalent((ab)*a, a(ba)*) = True
  equivalent(a*, a+) = False
```

这为“这两个过滤规则是否等价”“新规则是否被旧规则包含”这类工程问题提供了直接的判定方法。

#### 7.5.3 导数类与偏导数

`OTHER` 的方法把出现过的字符逐个拿出来求导，遇到 `[a-z]` 就要求 26 次，而结果往往完全相同。Owens、Reppy 与 Turon（2009）给出了**导数类**的计算方法：为每个表达式计算字母表的一个划分，使同一块中的字符导数相同。

- $C(S) = \{S, \Sigma\setminus S\}$；
- $C(r\mid s) = C(r\,\&\,s) = C(r)\wedge C(s)$，$\wedge$ 表示取两个划分的所有非空交集；
- $C(r\,s) = \nu(r)\ ?\ C(r)\wedge C(s) : C(r)$；
- $C(r^*) = C(\lnot r) = C(r)$。

SML 的词法分析器生成器 ml-ulex 就采用这种方法。

Antimirov（1996）把导数中的并集“拆开”：$D_c(r\mid s)$ 不再是一个表达式，而是两个表达式组成的**集合**，称为**偏导数**。以偏导数为状态得到的是 NFA，状态数至多为 $m+1$，并且不需要 ACI 化简就能保证终止。Champarnaud 与 Ziadi 证明了：**偏导数自动机是 Glushkov 自动机的商**。

### 7.6 几种方法的关系

| 方法 | 状态 | 产物 | ε 边 | 状态数上界 | 交集与补集 |
|---|---|---|---|---|---|
| Thompson（第 4 章） | NFA 节点 | NFA | 有 | $O(m)$ | 困难 |
| Glushkov | 位置 | NFA | 无 | $m+1$ | 困难 |
| Antimirov 偏导数 | 偏导数 | NFA | 无 | $m+1$ | 不直接支持 |
| followpos | 位置集合 | DFA | 无 | $2^m$ | 困难 |
| Brzozowski 导数 | 导数（模 ACI） | DFA | 无 | 有限，可能为指数级 | 直接支持 |

竖着看，关系一目了然：

- **followpos DFA = Glushkov 自动机的子集构造**；
- **Antimirov 自动机 = Glushkov 自动机的一个商**；
- **Brzozowski DFA ≈ Antimirov 自动机的子集构造**：一个 Brzozowski 导数可以看成一组偏导数的并集；
- **Glushkov 自动机 ≈ Thompson NFA 的 ε 消除**。

它们都是在“位置”这一个基本概念上，选择了不同的合并方式、不同的确定化时机。第 15 章的差分测试对每个不含锚点的随机模式，都把 followpos DFA、Glushkov 位掩码、导数 DFA 与 Pike VM 的整串匹配结果做了对拍，没有发现任何差异。

### 7.7 语义上的局限

本章的所有构造都只回答一个问题：**这个串属于语言吗？** 它们处理的是**语言**，不是**匹配**：

1. **没有捕获组。** 位置集合和导数都不记录“哪个字符属于哪个组”。
2. **没有优先级。** ACI 化简把 `a|ab` 和 `ab|a` 视为同一个表达式。这对语言判定完全正确，但 leftmost-first 语义恰恰依赖分支的顺序。要保留优先级，就不能使用交换律，终止性也必须重新论证。.NET 7 引入的 `RegexOptions.NonBacktracking` 正是基于导数的。根据 Moseley 等人在 PLDI 2023 上的论文，它使用保留分支顺序的导数，得到与回溯引擎一致的匹配结果（在它支持的特性范围内）。
3. **锚点和环视需要扩展。** `^`、`$`、`\b` 依赖上下文，而不只依赖下一个字符（第 11 章）。所以 `regexlab` 的位置构造在遇到断言时直接报 `Unsupported`。

### 7.8 选型建议

- **需要交集、补集，或需要在表达式层面推理**（等价、包含、规则冲突检测）：选 **Brzozowski 导数**；
- **模式较短，希望不构造 DFA 就能高速匹配**：选 **Glushkov 加位并行**（第 12 章）；
- **离线生成表驱动的 DFA**（词法分析器生成器）：followpos 与 Thompson 加子集构造都可以。前者通常状态更少，两者最小化后结果相同；
- **需要捕获组或 leftmost-first 语义**：本章的方法只能承担判定和求终点这部分工作，其余仍交给 Pike VM 等引擎。

### 7.9 练习

1. 对随机表达式，比较 `PosDFA`、第 6 章锚定 `DFA` 的状态数，最小化后二者应当相同。解释为什么最小化之前可能不同，并找出一个使它们不同的例子。
2. 实现 7.5.3 节的导数类 $C(r)$，用它替换 `DerivDFA` 中的字母表，在 `[a-z]+@[a-z]+\.com` 上比较求导次数。
3. 用 `equivalent` 判断 `(a|b)*a(a|b)` 与 `(a|b)*(aa|ab)` 是否等价（答案：等价）。再把后者改成 `(a|b)*(aa|ba)`，扩展 `equivalent`，让它返回一个区分二者的最短串（提示：在差集 DFA 上做 BFS，答案是 `ab`）。
4. **ACI 与优先级（思考题）。** 设 `alt` 不再用集合存储分支，而是用元组保持原有顺序，只删除重复项。举例说明这样的“有序导数”在某些表达式上会产生更多状态，并思考它是否仍保证状态数有限。
5. **一义性检查。** 对 Glushkov 自动机，判断是否存在某个状态在同一字符上有两个不同的后继位置。检查 `(a|b)*a` 和 `a(a|b)*` 是否一义，并直观解释为什么 `(a|b)*a` 无法改写成等价的一义表达式。

---
## 第 8 章　词法分析器生成器：lex/flex、re2c 与编译器手写词法器

第 6、7 章把**一个**正则表达式变成一个 DFA。词法分析器面对的问题略有不同：它手里有**一组**正则表达式，每条对应一种记号（token），要把整段输入**切分**成记号序列：

```text
if x1 >= 42 { ... }
→ KW_IF  IDENT("x1")  GE  NUMBER("42")  LBRACE ...
```

本章依次讨论：

- 词法分析的匹配语义；
- 多规则 DFA 与驱动循环，以及驱动循环中一个容易被忽视的平方级陷阱；
- 两种代表性的生成器：表驱动的 lex/flex 和直接生成代码的 re2c；
- 为什么大多数主流编译器选择手写词法器，以及哪些编译器不这样做。

代码见 `regexlab/lexgen.py`。

### 8.1 词法分析的语义：最长匹配与规则优先级

词法分析器在每个位置上做的事情，与“搜索”有两点不同：

1. **锚定**：记号必须从当前位置开始，中间不能跳过字符；
2. **跨规则取最长**：在所有规则中，选能匹配最长前缀的那一条。长度相同时，选**书写在最前面**的那一条。

这两条合称**最长匹配**（maximal munch），lex、flex、re2c、JFlex 和 ANTLR 的词法部分都遵循它。它与第 13 章的 leftmost-first 不同：leftmost-first 在分支间按书写顺序优先，一旦某个分支成功就不再尝试更长的可能；最长匹配先比长度，长度相同时才看书写顺序。

两条规则各自解决一类问题：

- **最长匹配**让 `iffy` 成为一个标识符，而不是关键字 `if` 加标识符 `fy`；让 `>=` 成为一个运算符，而不是 `>` 加 `=`；
- **规则优先级**让 `if` 成为关键字：`if` 同时匹配关键字规则和标识符规则 `[a-z]+`，长度都是 2，只能靠书写顺序区分。所以**关键字规则必须写在标识符规则之前**。

最长匹配是贪心的，只看当前这一个记号，从不考虑后续切分能否成功。经典的例子是 C 语言中的 `x+++++y`：它被切分成 `x ++ ++ + y`，语法上是错误的；而 `x ++ + ++ y` 本来是一个合法的切分。C 标准明确规定按最长匹配处理，所以这段代码就是编译错误。

### 8.2 多规则 DFA

第 7 章的 followpos 构造只需要一处改动就能处理多条规则：**每条规则使用各自的结束标记**。

- 规则 $k$ 写成 $r_k\,\#_k$，各规则的位置统一编号；
- 初始状态是所有规则的 firstpos 之并；
- 一个状态如果包含某些 $\#_k$ 的位置，它就是接受状态，并记录其中**编号最小**的 $k$。

```python
class LexerDFA:
    def __init__(self, patterns):
        syms, follow, start = [], {}, set()
        for k, p in enumerate(patterns):
            ast, _ = parse(p)
            _, f, _ = analyze(Cat(to_pos(ast), Sym(End(k))), syms, follow)   # 每条规则一个结束标记
            start |= f
        ...                                   # 与 PosDFA 相同的子集构造
        ks = [syms[p].rule for p in S if isinstance(syms[p], End)]
        self.accept.append(min(ks) if ks else None)    # 编号小者优先
```

对 `['if', '[a-z][a-z0-9]*', '[0-9]+', '>=', '>', '[ \t\n]+']` 这组规则，实测 DFA 有 9 个状态、16 个字符等价类。

对这个 DFA 做最小化时要注意：初始划分不能只分“接受”和“不接受”两块，而要**按接受的规则编号分块**。接受 `IDENT` 的状态和接受 `KW_IF` 的状态即使后续行为完全相同，也不能合并。

**被遮蔽的规则。** 如果某条规则的编号不出现在任何接受状态里，它就被优先级更高的规则完全遮蔽了。把 `IDENT` 写在 `KW_IF` 之前：

```text
把 IDENT 写在 KW_IF 前面时永远不会被选中的规则: [1]
```

flex 对这种情况会给出 `rule cannot be matched` 警告。

### 8.3 驱动循环

DFA 只回答“这个前缀能否被接受”。要实现最长匹配，驱动循环必须在 DFA 无法继续时**回退**到最后一次经过接受状态的位置：

```python
def tokenize(dfa, text, skip=()):
    if dfa.accept[0] is not None:
        raise ValueError('存在能匹配空串的规则，驱动循环会原地打转')
    pos, out = 0, []
    while pos < len(text):
        q, i = 0, pos
        last_rule = last_end = None
        while i < len(text):
            q = dfa.trans[q][dfa.cls(text[i])]
            if q == dfa.dead:
                break
            i += 1
            if dfa.accept[q] is not None:
                last_rule, last_end = dfa.accept[q], i      # 记住最后一次接受
        if last_rule is None:
            raise LexError(f'位置 {pos} 处无法识别：{text[pos]!r}')
        if last_rule not in skip:
            out.append((last_rule, text[pos:last_end]))
        pos = last_end                                        # 回退
    return out
```

```text
[('KW_IF', 'if'), ('IDENT', 'x1'), ('GE', '>='), ('NUMBER', '42'), ('IDENT', 'iffy')]
```

开头的检查不可省略。如果某条规则能匹配空串（比如 `[0-9]*`），驱动循环会在无法识别的字符上不断输出空记号而不前进。有些生成器用一条“匹配任意一个字符”的隐含默认规则来避免这个问题，flex 就是如此：一个字符的匹配总胜过空匹配。re2c 会在生成代码时给出 `-Wmatch-empty-string` 警告。自己编写的驱动循环则必须显式检查。

### 8.4 最长匹配的平方级陷阱

回退意味着同一段输入可能被扫描多次。考虑两条规则 `a` 和 `a*b`，输入是 $n$ 个 `a`，没有 `b`。在位置 0，DFA 一直读到输入末尾，期待遇到 `b`，最后只能回退到位置 1，输出规则 0 的 `a`。在位置 1，同样的事情再发生一遍……总共读入 $n + (n-1) + \cdots + 1 = O(n^2)$ 个字符。

这不是理论上的玩具。只要某条规则带有一个“可能很长、但最后才决定是否成功”的部分，就会出现这种情况，例如未闭合的块注释、未闭合的字符串、允许跨行的复杂字面量。这本质上也是一种拒绝服务风险（第 14 章）。

Reps（1998）给出了一个简单的修正：**记住失败过的 (状态, 位置) 对。**

关键的观察是：DFA 从状态 $q$、位置 $i$ 出发后会发生什么，只取决于 $(q, i)$，与这次扫描从哪里开始无关。如果某次扫描在最后一次接受之后经过了 $(q, i)$，并且最终停了下来，那么从 $(q, i)$ 出发**一定**到不了任何接受状态。以后再遇到 $(q, i)$，可以立即停下。

```python
def tokenize_linear(dfa, text, skip=()):
    failed = set()                     # 已知到不了接受状态的 (q, i)
    pos, out = 0, []
    while pos < len(text):
        q, i = 0, pos
        last_rule = last_end = None
        since = []                     # 自最后一次接受以来经过的 (q, i)
        while i < len(text) and (q, i) not in failed:
            since.append((q, i))
            q = dfa.trans[q][dfa.cls(text[i])]
            if q == dfa.dead:
                break
            i += 1
            if dfa.accept[q] is not None:
                last_rule, last_end = dfa.accept[q], i
                since.clear()          # 接受之前经过的状态对后面能到达接受，不能标记
        failed.update(since)
        ...
```

每个 $(q, i)$ 至多被加入 `failed` 一次，所以总时间是 $O(n\lvert Q\rvert)$，实际中接近线性。实测：

```text
  n= 1000  朴素读入     500,500 (0.052s)   Reps 读入   2,997 (0.001s)
  n= 2000  朴素读入   2,001,000 (0.203s)   Reps 读入   5,997 (0.002s)
  n= 4000  朴素读入   8,002,000 (0.851s)   Reps 读入  11,997 (0.003s)
  n= 8000  朴素读入  32,004,000 (3.303s)   Reps 读入  23,997 (0.006s)
  加兜底规则 a+ 后朴素驱动读入: 4000
```

flex 和 re2c 都没有采用 Reps 的修正，而是假定规则写得足够好，不会出现严重回退。flex 的 `-b` 选项会生成一个 `lex.backup` 文件，列出所有需要回退的状态。flex 手册专门有一节讲如何通过添加**兜底规则**消除回退：让每个非接受状态都有一个接受的后继，DFA 就不会读到很远之后再回退。最后一行实测正是这个效果：加上规则 `a+` 后，“读了一串 `a` 但还没读到 `b`”的状态都成了接受状态，朴素驱动循环也只读 4000 次。

### 8.5 lex 与 flex

lex 由 Lesk 和 Schmidt 在 1975 年为 Unix 编写。flex（fast lex）是 Vern Paxson 在 1987 年前后重写的自由软件版本，今天几乎所有的“lex”实际上都是 flex。

#### 8.5.1 输入格式

一个 flex 文件分成三段，用 `%%` 分隔：

```lex
%{
#include "tokens.h"
%}
DIGIT    [0-9]
ID       [a-z][a-z0-9]*
%%
"if"            { return KW_IF; }
{ID}            { yylval.s = strdup(yytext); return IDENT; }
{DIGIT}+        { yylval.n = atoi(yytext); return NUMBER; }
">="            { return GE; }
">"             { return GT; }
[ \t\n]+        { /* 跳过空白 */ }
.               { error("非法字符 %c", yytext[0]); }
%%
int yywrap(void) { return 1; }
```

- 第一段是**定义**：`%{ %}` 中的 C 代码原样复制，其余是命名的正则表达式，在规则中用 `{ID}` 引用；
- 第二段是**规则**：每条规则是“模式加动作”，`yytext` 指向匹配文本，`yyleng` 是长度；
- 第三段是**用户代码**，原样复制到生成文件末尾。

生成的 `yylex()` 每次被调用时从上次停下的地方继续扫描。动作中执行 `return` 时，`yylex` 返回这个记号；不 `return` 的动作（比如跳过空白）让扫描继续。

#### 8.5.2 超出正则语言的特性

**起始条件（start conditions）。** 规则可以带一个前缀 `<COND>`，只在对应条件下生效，动作中用 `BEGIN(COND)` 切换：

```lex
%x COMMENT
%%
"/*"              { BEGIN(COMMENT); }
<COMMENT>"*/"     { BEGIN(INITIAL); }
<COMMENT>.|\n     { /* 忽略注释内容 */ }
```

`%x` 声明**排他**条件，处于该条件时只有带这个前缀的规则生效；`%s` 声明**包含**条件，不带前缀的规则同样生效。实现上，每个起始条件对应 DFA 的一个不同的初始状态，没有运行时开销。起始条件让词法器成为一个“由多个 DFA 组成的小型状态机”，是处理字符串、注释、模板等嵌套结构的主要手段。ANTLR 的**词法模式**（mode，第 9 章）就是同一个思想。

**尾部上下文（trailing context）。** 规则 `r/s` 匹配 `r`，但要求它后面紧跟 `s`；`s` 部分不计入 `yytext`。经典的例子来自 Fortran：

```lex
DO/[A-Z0-9]*=[A-Z0-9]*,     { return KW_DO; }
```

Fortran 忽略空格，`DO 10 I = 1,10` 是循环，而 `DO 10 I = 1.10` 是给变量 `DO10I` 赋值，只有看到逗号才能确定 `DO` 是关键字。

flex 把 `r` 和 `s` 连接后放进 DFA，再设法确定 `r` 在哪里结束。如果 `r` 或 `s` 长度固定，这很简单；如果两者都可变长，`r` 的结束位置就可能有歧义，比如 `a*/a*b`，flex 会给出 “dangerous trailing context” 警告，结果可能不正确。re2c 用 8.6.3 节的**标签**机制精确解决了这个问题。

**REJECT。** 动作中执行 `REJECT` 表示“当作这条规则没有匹配”，扫描器退而选择次优的匹配。为了支持它，DFA 必须在每个状态上记录**所有**可能接受的规则。只要规则中出现一次 `REJECT`，**整个**扫描器都会变慢。flex 手册的建议很直接：尽量不要用它。

#### 8.5.3 表压缩

一个 DFA 的转移表有 $\lvert Q\rvert\times\lvert\Sigma\rvert$ 项。中等规模的语言 $\lvert Q\rvert$ 有几百到几千，$\lvert\Sigma\rvert = 256$，完整的表有几十万到上百万项。1970 年代的内存装不下，今天的 CPU 缓存也装不下。flex 用了三层压缩：

1. **字符等价类**：即第 6 章的方法，`yy_ec[c]` 给出字符 $c$ 所属的类；
2. **元等价类**：对字符类再做一次粗分类，`yy_meta[ec]`，只在默认状态链上使用；
3. **梳状压缩**（comb vector）：用四个数组表示整张表。

| 数组 | 含义 |
|---|---|
| `yy_def[s]` | 状态 $s$ 的“默认状态”：没有单独列出的转移都与它相同 |
| `yy_base[s]` | 状态 $s$ 的转移在 `yy_nxt` 中的起始偏移 |
| `yy_nxt[base[s] + c]` | 状态 $s$ 在字符类 $c$ 上的转移 |
| `yy_chk[base[s] + c]` | 这一项属于哪个状态 |

多个状态的转移行在 `yy_nxt` 中**交错**存放，像把几把梳子的齿互相插在一起。只要两行的非空项互不重叠，就可以共用同一段数组，`yy_chk` 用来辨别某一项究竟属于哪一行：

```c
while (yy_chk[yy_base[s] + c] != s) {
    s = yy_def[s];                       // 不是自己的项，转到默认状态继续查
    if (s >= JAM_STATE) c = yy_meta[c];
}
s = yy_nxt[yy_base[s] + c];
```

`regexlab` 的 `comb_pack` 是不带默认状态链的简化版本。对 8.2 节的规则集：

```text
梳状压缩: 完整表 9×16=144 项 → nxt/chk 长度 45
```

flex 允许用户在空间和时间之间选择：

| 选项 | 含义 | 表的大小 | 速度 |
|---|---|---|---|
| `-Cem`（默认） | 等价类、元等价类、梳状压缩 | 最小 | 最慢 |
| `-Ce` | 只用等价类和梳状压缩 | 小 | 较快 |
| `-CF` | 不压缩的“快速”表示 | 大 | 快 |
| `-Cf` | 不压缩的完整二维表 | 最大 | 最快 |

在今天的机器上，表的大小很少是瓶颈，最影响速度的往往是回退（8.4 节）和 `REJECT`。

### 8.6 re2c：直接生成代码

re2c 由 Bumbulis 和 Cowan 在 1994 年发表，现在由 Ulya Trofimovich 等人维护。它与 flex 有两点根本区别：

1. **不生成转移表，而是把 DFA 直接编译成代码**：每个状态是一段代码，每个转移是一个 `switch` 分支或一次 `goto`；
2. **不提供驱动循环，也不管理输入缓冲区**：生成的代码嵌入用户自己的函数，用户通过几个宏告诉它如何读取输入。

#### 8.6.1 输入与生成的代码

```c
int lex(const char **cur) {
    const char *YYCURSOR = *cur, *YYMARKER, *tok;
loop:
    tok = YYCURSOR;
    /*!re2c
        re2c:define:YYCTYPE = char;
        re2c:yyfill:enable  = 0;

        "if"              { *cur = YYCURSOR; return KW_IF; }
        [a-z][a-z0-9]*    { *cur = YYCURSOR; return IDENT; }
        [0-9]+            { *cur = YYCURSOR; return NUMBER; }
        "..."             { *cur = YYCURSOR; return ELLIPSIS; }
        "."               { *cur = YYCURSOR; return DOT; }
        [ \t\n]+          { goto loop; }
        "\x00"            { return END; }
        *                 { return ERROR; }
    */
}
```

`YYCURSOR` 是当前位置；`YYMARKER` 是回退点，只有当某个状态需要回退时生成的代码才会用到它；`*` 是默认规则；`"\x00"` 是**哨兵**，所以生成的代码不需要每读一个字符就检查是否越界。生成的代码大致如下（删减并重新排版）：

```c
yy0:
    yych = *YYCURSOR;
    switch (yych) {
    case 0x00: goto yy1;
    case '.':  goto yy5;
    case 'i':  goto yy8;
    case 'a': ... case 'h':
    case 'j': ... case 'z': goto yy10;
    ...
    }
yy5:
    yych = *(YYMARKER = ++YYCURSOR);   // 已经能接受 "."，记下回退点
    if (yych == '.') goto yy6;
yy4:
    { *cur = YYCURSOR; return DOT; }
yy6:
    yych = *++YYCURSOR;
    if (yych == '.') goto yy7;
    YYCURSOR = YYMARKER;               // 只读到 ".."，回退到第一个 "."
    goto yy4;
yy7:
    ++YYCURSOR;
    { *cur = YYCURSOR; return ELLIPSIS; }
```

8.3 节驱动循环的每个部分都被展开到了代码中：`last_end` 变成了 `YYMARKER`，“记录最后一次接受”变成一次赋值，回退变成 `YYCURSOR = YYMARKER`。而且只有真正需要回退的路径上才有这些操作：对 `[a-z][a-z0-9]*` 这样“每一步都接受”的规则，生成的代码中完全不会出现 `YYMARKER`。

直接生成代码的好处是：

- **没有查表开销**，转移就是一次分支；现代编译器会把密集的 `switch` 编译成跳转表，稀疏的编译成比较序列或二分查找；
- **re2c 自己也做优化**：对 DFA 做最小化，并为每个状态选择最合适的分支形式。可选形式包括 `switch` 语句、按区间二分的嵌套 `if`（`-s`）、多个状态共用的**位图**（`-b`，在 `[a-z0-9_]*` 这样的循环中每步只需一次查表和一次按位与），以及 GCC 的计算跳转 `goto *table[c]`（`-g`）。

#### 8.6.2 输入缓冲：YYFILL 与哨兵

re2c 把缓冲区完全交给用户，只通过两个宏与外界交互：`YYLIMIT` 是缓冲区中有效数据的末尾；`YYFILL(n)` 要求用户保证缓冲区中至少还有 $n$ 个字符可读。

朴素的做法是每读一个字符检查一次 `YYCURSOR < YYLIMIT`。re2c 更聪明：它分析 DFA 的结构，在每个**强连通分量**的入口处计算“到下一个检查点之前最多会读多少个字符”，只在这些位置生成一次检查：

```c
if ((YYLIMIT - YYCURSOR) < 3) YYFILL(3);
```

在没有环路的路径上（例如识别关键字 `while`），只检查一次；在环路上（例如 `[a-z0-9]*`），每一圈检查一次。另一种做法是**哨兵**：在输入末尾放一个规则中不会正常出现的字符，完全不做边界检查，只在读到哨兵时才判断“这是真正的结束，还是输入中恰好有这个字符”。re2c 从 1.2 版开始用 `re2c:eof` 配置支持这种方式。

#### 8.6.3 标签：在 DFA 上提取子匹配

第 6 章反复强调：DFA 只回答“是否匹配”。re2c 从 1.0 版（2017 年）开始突破了这个限制，引入了**标签**（tag）：

```c
/*!re2c
    @y [0-9]{4} "-" @m [0-9]{2} "-" @d [0-9]{2} {
        return make_date(y, m, d);     // y、m、d 分别指向年、月、日的起始位置
    }
*/
```

`@y` 表示“记下此刻 `YYCURSOR` 的值，存入变量 `y`”。一个捕获组正好是一对标签。

难点在于：同一个 DFA 状态对应 NFA 中的多个状态，它们可能处在“标签已经设置”和“尚未设置”的不同情形。Laurikari（2000）提出的**带标签 DFA**（TDFA）解决了这个问题：

- 每个标签可能需要多个**寄存器**，各自保存一个候选值；
- DFA 的每个转移上附带一组**寄存器操作**，例如“把当前位置写入 r3”“把 r1 复制到 r2”；
- 到达接受状态时，由一个最终映射决定每个标签取哪个寄存器的值。

子匹配提取就变成了 DFA 转移上的附加动作，整个过程仍是线性时间、无回溯。代价是 DFA 的状态可能更多。Trofimovich（2017）在 re2c 中实现了 TDFA，并做了两点改进：一是加入一个字符的**前瞻**，大大减少寄存器操作的数量；二是同时支持 leftmost greedy 和 POSIX 最长子匹配两种消歧语义（第 13 章）。

标签也顺带解决了 flex 的尾部上下文难题：re2c 把 `r/s` 处理成 `r @t s`，匹配结束后令 `YYCURSOR = t`。在 TDFA 中，`a*/a*b` 这种两边都可变长的情形也能得到精确结果。

### 8.7 编译器为什么大多手写词法器

有了 flex 和 re2c 这样成熟的工具，人们可能以为主流编译器都在用它们。实际情况是：

| 编译器 / 解释器 | 词法器 | 位置 |
|---|---|---|
| GCC | 手写 | `libcpp/lex.cc` |
| Clang | 手写 | `clang/lib/Lex/Lexer.cpp` |
| javac | 手写 | `JavaTokenizer.java` |
| Go | 手写 | `go/scanner`、`cmd/compile/internal/syntax/scanner.go` |
| rustc | 手写 | `rustc_lexer` |
| CPython | 手写 | `Parser/tokenizer.c` |
| V8 | 手写 | `src/parsing/scanner.cc` |
| TypeScript | 手写 | `scanner.ts` |
| Roslyn（C#） | 手写 | `Lexer.cs` |
| Swift | 手写 | `lib/Parse/Lexer.cpp` |
| PHP（Zend） | **re2c** | `Zend/zend_language_scanner.l` |
| PostgreSQL | **flex** | `src/backend/parser/scan.l` |
| OCaml | **ocamllex** | `parsing/lexer.mll` |
| GHC | **Alex** | `compiler/GHC/Parser/Lexer.x` |
| Kotlin | **JFlex** | `Kotlin.flex` |

C 家族和主流工业语言几乎都手写；ML 家族的编译器则习惯用自己生态中的生成器（ocamllex、Alex、ml-ulex）。原因并不是工程师不懂自动机。

#### 8.7.1 词法本身不是正则的

- **嵌套注释**：Rust 允许 `/* 外 /* 内 */ 外 */`。识别它需要一个计数器，是上下文无关语言；
- **原始字符串**：Rust 的 `r##"……"##` 要求结尾 `#` 的个数与开头相同；C++11 的 `R"delim(……)delim"` 要求结尾分隔符与开头相同；
- **缩进**：Python 根据行首缩进的变化产生 `INDENT` 和 `DEDENT`，需要维护一个缩进栈。

#### 8.7.2 词法依赖语法上下文

- **JavaScript 的 `/`**：`a / b / c` 中是除号，`x = /b/g` 中是正则字面量。词法器单凭字符无法区分。TypeScript 编译器默认把 `/` 当作除号，语法分析器在“期待表达式”的位置调用 `reScanSlashToken()`，要求词法器从同一位置**重新扫描**；模板字符串的 `}` 和类型参数中的 `>` 也是同样的处理；
- **C 语言的 typedef 名称**：`T * x;` 可以是乘法表达式，也可以是声明指针，取决于 `T` 是否是 typedef 名称。传统的 **lexer hack** 让词法器查询符号表，对 typedef 名称返回 `TYPE_NAME`；
- **C++ 的 `>>`**：从 C++11 开始，`vector<vector<int>>` 中的 `>>` 要理解为两个 `>`。Clang 仍然生成一个 `>>` 记号，由语法分析器在关闭模板参数列表时把它拆开。

这些需求都要求词法器能被语法分析器“驱动”。表驱动的生成器可以通过起始条件和动作代码勉强做到，手写词法器做起来自然得多。

#### 8.7.3 性能

- **关键字不进入 DFA。** 为每个关键字写一条规则会让 DFA 多出许多状态。手写词法器的标准做法是先按标识符规则扫描出一个单词，再查一次表。GCC 和 Clang 都在初始化时把关键字预先放入标识符哈希表，查到的条目上直接带有“这是哪个关键字”的标记。较小的工具也常用 gperf 生成完美哈希表来完成这一步；
- **为常见情况写快速路径。** 绝大多数源代码是 ASCII，先用一张 128 项的表判断字符类别，遇到非 ASCII 字节时才进入较慢的 Unicode 处理。还可以用 SIMD 跳过长注释和空白，例如 Clang 跳过块注释时用 SSE2 一次检查 16 个字节中是否有 `/`；
- **不需要回退。** 作者对语言很清楚，知道每一个 `.` 之后最多再看两个字符就能区分 `.`、`..`、`...`、`.5`，8.4 节的平方级陷阱根本不会出现。

#### 8.7.4 错误处理与工具支持

- **错误信息**：未闭合的字符串、非法的转义、数字后紧跟字母（`123abc`），手写词法器都可以给出精确的位置和有针对性的提示，并从合理的位置继续扫描；生成器只能报告“没有规则匹配”；
- **无损记号流**：IDE 和格式化工具需要保留每一个空白和注释，并能从记号流原样还原源文本。Roslyn 和 rust-analyzer 把它们作为记号的附属信息（trivia）保留。`rustc_lexer` 只输出每个记号的类别和长度，不分配字符串，也不在词法阶段报错，只在记号上做标记，因此同一个词法器既能用于编译器，也能用于 IDE；
- **增量与可重入**：编辑器需要在用户修改一个字符后只重新扫描受影响的一小段。手写词法器的全部状态通常就是一个位置加几个计数器，很容易保存和恢复。

#### 8.7.5 一个手写词法器的骨架

`regexlab.lexgen.HandLexer` 集中体现了上面的要点：关键字查表，嵌套注释用计数器，原始字符串按 `#` 的个数配对，运算符靠向前看一两个字符区分：

```python
def block_comment(self):
    start, depth = self.i, 0                  # 计数器：超出正则语言的部分
    while True:
        if self.i >= len(self.s):
            raise LexError(f'位置 {start} 处的块注释未闭合')
        if self.s.startswith('/*', self.i):
            depth += 1; self.i += 2
        elif self.s.startswith('*/', self.i):
            depth -= 1; self.i += 2
            if depth == 0:
                return
        else:
            self.i += 1

def raw_string(self, start):
    self.i += 1                               # 跳过 r
    n = 0
    while self.peek() == '#':
        n += 1; self.i += 1
    ...
    close = '"' + '#' * n                     # 结束标记取决于开头：非正则
    j = self.s.find(close, self.i)
```

```text
输入: if x1 >= 42 /* a /* b */ c */ r#"say "hi""# else
[('KW_IF', 'if', 0), ('IDENT', 'x1', 3), ('GE', '>=', 6), ('NUMBER', '42', 9),
 ('RAW_STR', 'say "hi"', 30), ('KW_ELSE', 'else', 44), ('EOF', '', 48)]
```

嵌套注释被整体跳过，原始字符串中的 `"` 没有提前结束字符串。

把这段代码和 re2c 生成的代码放在一起对比：`next` 开头的一串 `if` 就是 DFA 初始状态的 `switch`，每个 `while` 循环就是 DFA 中的一个自环。**手写词法器本质上仍是一个手工编码的 DFA**，只是作者可以在任意位置附加计数器、查表和重新扫描，从而跳出正则语言的限制。

### 8.8 横向对比

| | flex | re2c | ANTLR 词法器（第 9 章） | 手写 |
|---|---|---|---|---|
| 产物 | 压缩的转移表加驱动循环 | 直接生成的 C/C++/Go 等代码 | ATN 加运行时 DFA 缓存 | 普通代码 |
| 匹配语义 | 最长匹配加规则优先级 | 同左 | 同左，另有谓词和动作 | 由作者决定 |
| 超出正则的能力 | 起始条件、REJECT、动作代码 | 条件、标签、动作代码 | 模式、语义谓词、动作代码 | 任意 |
| 子匹配 | 无（只有尾部上下文） | 有（TDFA 标签） | 无 | 任意 |
| 输入缓冲 | 内置 | 由用户提供 | 由运行时提供 | 由作者决定 |
| 回退开销 | 可能平方级，`-b` 可诊断 | 同左 | 同左 | 通常没有 |
| 典型用户 | PostgreSQL、传统 Unix 工具 | PHP、Ninja | DSL、IDE 插件 | GCC、Clang、Go、rustc、V8、CPython |

经验法则：**语言的词法越接近正则、越稳定，越适合用生成器；越依赖上下文、越重视错误信息和工具支持，越适合手写。** 对一门新的 DSL，生成器能让你在半小时内得到一个正确的词法器；对一门有数百万用户的通用语言，手写词法器多付出的几千行代码，会在错误信息、IDE 体验和性能上得到回报。

### 8.9 练习

1. 修改第 6 章的 Hopcroft 算法，使初始划分按 `accept[q]` 的取值分块。故意只按“接受/不接受”分块，构造一个输入，说明错误的最小化会把 `if` 识别成 `IDENT`。
2. 为 `comb_pack` 加入默认状态：为每个状态选择一个转移最相似的已放置状态作为 `def`，只存放二者不同的项，比较压缩率。
3. 用第 5 章的 Pike VM 实现尾部上下文 `r/s`：把规则写成 `(r)s`，记号的结束位置取组 1 的结束位置。在输入 `aaab` 上验证 `a*/a*b`。
4. 为 `HandLexer` 增加 `rescan_slash(pos)`，并写一个极小的表达式解析器，在“期待操作数”的位置调用它。用 `a / b / c` 和 `x = /b/g` 验证。
5. **无损记号流（思考题）。** 把空白和注释作为附属信息挂在记号上，使所有记号拼接起来恰好还原原文。行尾注释应当挂在前一个记号上，还是后一个记号上？这对代码格式化工具有什么影响？

---
## 第 9 章　ANTLR：ATN 模拟与自适应 DFA 缓存

第 8 章的生成器都在**生成时**把规则编译成 DFA。ANTLR 4 换了一种做法：生成时只构造一张类似 NFA 的图，称为 **ATN**（augmented transition network，增广转移网络）；真正的 DFA 在**运行时**按需构造，并缓存起来供后续使用。词法器和语法分析器都用这一机制。

这与第 6 章的惰性 DFA 本质相同：状态是 NFA 状态的集合，转移在第一次用到时才计算。区别在于 ANTLR 把它推广到了语法分析的**预测**问题上。这时“NFA 状态”还附带调用栈和语义谓词，于是“缓存什么、不能缓存什么”都需要重新考虑。

代码见 `regexlab/antlr_lexer.py`（词法器）和 `regexlab/allstar.py`（语法预测）。

### 9.1 从 LL(k) 到 ALL(\*)

自顶向下的语法分析器在每个**决策点**都要回答一个问题：当前规则有多个备选分支，应该选哪一个？

```antlr
stat : ID '=' expr ';'          // 赋值
     | ID '(' args ')' ';'      // 调用
     | expr ';'                 // 表达式语句
     ;
```

只看一个记号不够，三个分支都可能以 `ID` 开头。更麻烦的是，有些决策需要的前瞻长度没有上界：

```antlr
decl : mods 'int' ID ';'        // unsigned unsigned int x;
     | mods ID ID ';'           // unsigned unsigned T x;
     ;
mods : 'unsigned' mods | ;
```

两个分支都以任意多个 `unsigned` 开头，固定的 $k$ 总有不够用的时候。ANTLR 的演进是这样的：

- **ANTLR 2** 用 LL(k)，$k$ 由用户指定；
- **ANTLR 3** 引入 **LL(\*)**（Parr 与 Fisher，PLDI 2011）：生成时对每个决策做静态分析，构造一个**前瞻 DFA**，用正则语言描述“读到什么样的记号序列就选哪个分支”。这能处理 `mods*`，但静态分析并不总能成功：当前瞻语言不是正则语言时，比如分支的区别出现在一个递归结构之后，分析就会失败，只能退回到回溯；
- **ANTLR 4** 引入 **ALL(\*)**（Adaptive LL(\*)，Parr、Harwell 与 Fisher，OOPSLA 2014）：放弃生成时的静态分析，改为在运行时针对**实际的输入**模拟所有分支，并把模拟结果缓存成 DFA。

ALL(\*) 的核心想法可以用一句话概括：**静态分析必须对所有可能的输入给出答案，动态分析只需要对实际出现的输入给出答案。** 后者总能做到，而实际出现的输入往往只覆盖可能情况的很小一部分。这与惰性 DFA 回避状态爆炸的道理完全相同。

### 9.2 ATN

ATN 一词来自 Woods（1970）的自然语言处理工作。ANTLR 4 的 ATN 中，每条规则对应一个子图，有一个入口状态和一个**规则停止状态**（rule stop state）。边有以下几种：

| 边的类型 | 含义 |
|---|---|
| 原子 / 区间 / 集合 | 匹配一个字符或一个记号，与 NFA 的普通转移相同 |
| ε | 不消耗输入 |
| 规则调用 | 进入被调用规则的入口状态，同时把“返回后去哪里”压栈 |
| 谓词 | 一个布尔表达式，为真时才能通过 |
| 动作 | 一段用户代码，预测时不执行 |
| 优先级谓词 | 用于左递归消除，见 9.6 节 |

如果没有规则调用、谓词和动作，ATN 就是第 4 章的 Thompson NFA。规则调用让 ATN 能识别上下文无关语言，相当于一个**下推自动机**；谓词则让它的行为可以依赖运行时的任意状态。

模拟 ATN 时，NFA 中的“状态”变成了**配置**（configuration）。ANTLR 的配置是四元组：

```text
(ATN 状态, 预测的备选分支, 调用栈上下文, 语义上下文)
```

- **调用栈上下文**：一串返回地址。多个配置的栈共享公共后缀，合并成一张**图结构栈**，ANTLR 中称为 `PredictionContext`。这与 GLR 分析器的 GSS 是同一种数据结构；
- **语义上下文**：沿途经过的谓词的合取式，在预测结束时求值。

### 9.3 词法器：在 ATN 上做惰性子集构造

ANTLR 的词法语义与第 8 章相同：最长匹配，长度相同时选书写在前的规则。实现方法不同：不在生成时构造 DFA，而是在运行时模拟 ATN，每算出一条 DFA 边就缓存起来。

先用 Thompson 构造把所有规则编译进一张 ATN，所有规则共用一个起始状态，每条规则的终点登记为规则停止状态：

```python
def compile_lexer(patterns):
    atn = ATN()
    start = atn.state()
    for i, p in enumerate(patterns):
        ast, _ = parse(p)
        s, t = atn.state(), atn.state()
        atn.eps[start].append(s)
        build(atn, to_pos(ast), s, t)        # Thompson 构造：从 s 到 t 识别该规则
        atn.stop[t] = i
    return atn, start
```

因为各条规则的子图互不相交，词法器中的配置只需要 ATN 状态编号：一个状态属于哪条规则是确定的。运行时只需要两个基本操作：沿 ε 边求闭包，读入一个字符后前进一步。以 `(状态集合, 字符)` 为键做缓存，就得到一个惰性构造的 DFA：

```python
class ATNLexer:
    def step(self, D, c):
        key = (D, c)
        if key not in self.trans:                  # 缓存未命中：在 ATN 上模拟一步
            self.trans[key] = closure(self.atn, move(self.atn, D, c))
        return self.trans[key]

    def rule_of(self, D):                          # 接受状态：编号最小的规则
        if D not in self.accept:
            rs = [self.atn.stop[p] for p in D if p in self.atn.stop]
            self.accept[D] = min(rs) if rs else None
        return self.accept[D]

    def tokens(self, text):
        pos = 0
        while pos < len(text):
            D, i, best = self.s0, pos, None
            while D:                               # 空集合 = 死状态，布尔值为假
                r = self.rule_of(D)
                if r is not None:
                    best = (i, r)                  # 记住最后一次接受
                if i == len(text):
                    break
                D = self.step(D, text[i])
                i += 1
            if best is None or best[0] == pos:     # 拒绝空匹配，否则原地打转
                raise LexError(f"无法识别的输入，位置 {pos}")
            end, rule = best
            if rule not in self.skip:
                yield rule, text[pos:end]
            pos = end
```

实测：

```text
[(0, 'if'), (1, 'ifx'), (2, '42')] 缓存的转移数 10 misses 10 hits 3
2322 个记号后：缓存转移 26，命中率 0.9978
```

第一行：输入 `if ifx 42` 时，`ifx` 是标识符（最长匹配），`if` 是关键字（先写者优先）。整个运行只构造了 10 条 DFA 边。第二行：随机生成 2000 多个记号后，缓存里也只有 26 条边，99.8% 的转移直接命中缓存。一个完整的 DFA 要为每个状态、每个可能的字符都建表，这里只建了实际用到的部分。

### 9.4 真实 ANTLR 词法器的其他要素

- **按模式分开缓存。** 每个词法模式（`mode`，相当于 flex 的排他起始条件）有自己的起始状态和 DFA，`pushMode`、`popMode` 维护一个模式栈；
- **`fragment` 与规则调用。** 词法规则可以引用其他规则，子图被共享，所以配置里重新带上了返回栈；
- **谓词与动作会抑制缓存。** 语义谓词 `{...}?` 的结果依赖运行时状态，经过谓词的模拟结果不能缓存进 DFA。ANTLR 的 `LexerATNSimulator` 遇到这种配置集时会跳过添加 DFA 边，以后每次都在 ATN 上重新模拟；
- **非贪婪循环。** `'/*' .*? '*/'` 中的 `.*?` 在 ANTLR 词法器里表示“匹配尽可能少的字符，只要整条规则还能成功”。实现上，配置记录自己是否经过了非贪婪决策，到达规则停止状态后，同一备选中更长的路径会被剪掉；
- **命令。** `skip`、`more`、`type(...)`、`channel(...)`、`mode(...)` 改变的是记号产出之后做什么，不影响匹配本身。

### 9.5 语法预测：ALL(\*)

语法分析的预测要复杂得多：配置里必须带上调用栈。这里给出与正则引擎对照所需的要点，`regexlab/allstar.py` 是一个约 350 行的完整教学实现。

#### 9.5.1 配置、closure 与 reach

配置 $c = (p, i, \gamma)$：ATN 状态 $p$、它代表的备选 $i$、调用栈 $\gamma$（栈顶在左）。

$$\mathrm{closure}(p,i,\gamma) = \{(p,i,\gamma)\} \cup
\begin{cases}
\mathrm{closure}(q,i,\gamma) & p\xrightarrow{\varepsilon} q \\
\mathrm{closure}(p_B,i,\ q\gamma) & p\xrightarrow{B} q\quad\text{（调用：压入返回点）}\\
\mathrm{closure}(q,i,\gamma') & p=p'_B,\ \gamma=q\gamma'\quad\text{（返回：弹栈）}\\
\bigcup_{p_1\xrightarrow{B}q}\mathrm{closure}(q,i,\#) & p=p'_B,\ \gamma=\#\quad\text{（SLL：调用者未知）}
\end{cases}$$

$$\mathrm{reach}(D,a) = \bigcup_{(p,i,\gamma)\in D,\ p\xrightarrow{a}q} \mathrm{closure}(q,i,\gamma)$$

这与第 6 章的 `closure` 和 `step` 是同一回事，只是多了规则调用与返回。终止条件也与正则引擎对应：

- 只剩**唯一备选**：预测完成；
- **全部死亡**：语法错误（`no viable alternative`）；
- **冲突**：两个不同备选的配置走到了同一个 (状态, 栈)。

#### 9.5.2 SLL 与 DFA 缓存

预测结果要能缓存，就不能依赖“谁调用了我”。所以第一阶段用 **SLL**：起始栈用通配符 `#` 代替真实调用栈。走到规则出口而栈底是 `#` 时，就去**所有**调用点。每个决策维护一个 DFA，DFA 状态是配置集。`decl` 决策的实际跟踪：

```text
[SLL] 决策 decl @ 'unsigned'
  ATN 模拟 D0 --'unsigned'--> D0 {(p12,1,[#]), (p21,1,[p12 #]), (p17,2,[#]), (p21,2,[p17 #])}
  DFA 命中 D0 --'unsigned'--> D0
  DFA 命中 D0 --'unsigned'--> D0
  ATN 模拟 D0 --'int'--> D1 {(p13,1,[#])}
  SLL 预测 alt 1（向前看 4 个记号）
```

吃掉一个 `unsigned` 后，配置集与起始状态完全相同，所以 DFA 出现了 `D0 --'unsigned'--> D0` 这个**环**。它用有限个状态表达了“任意多个 `unsigned` 之后看到 `int` 就选 alt 1”，这正是 ANTLR 3 的 LL(\*) 前瞻 DFA 想表达的东西，只是现在在运行时按需长出来。

#### 9.5.3 SLL 冲突与全上下文 LL

SLL 合并了所有调用点。如果一个决策的正确答案**取决于是谁调用了它**，合并就会把本来能区分的情况混成冲突。来自原论文的例子：

```antlr
s : 'x' b EOF | 'y' c EOF ;
b : a 'a' ;          // a 后面跟 'a'
c : a 'b' 'a' ;      // a 后面跟 'b' 'a'
a : 'b' | ;          // ← 决策点
```

输入 `y b a` 时，`a` 是从 `c` 里调用的，正确答案是 alt 2（`a` 为空）。实际跟踪：

```text
[SLL] 决策 a @ 'b'
  ATN 模拟 D0 --'b'--> D1 {(p17,1,[#]), (p20,1,[#]), (p21,2,[#])}
  ATN 模拟 D1 --'a'--> D2 {(p10,1,[#]), (p14,2,[#])}
  ATN 模拟 D2 --'EOF'--> D3 {(p1,1,[#]), (p1,2,[#])}
  D3 是 SLL 冲突状态 → 全上下文 LL
  [LL] γ0=[p20 p14] {(p23,1,[p20 p14]), (p20,2,[p14])}
  [LL] --'b'--> {(p20,1,[p14]), (p21,2,[p14])}
  [LL] --'a'--> {(p14,2,[ε])}
['s#2', 'y', ['c#1', ['a#2'], 'b', 'a'], '<EOF>']
```

SLL 一直看到 `EOF` 也分不出来：alt 1 的分身沿着“`a` 吃掉 `b`，然后接 `b` 里的 `'a'`”这条在真实输入中不可能出现的虚构路线一直活着，最后两个备选在 (p1, #) 会合。这时 DFA 状态 D3 被标记为“需要全上下文”，预测**用真实调用栈 γ0 重新模拟**，只看 2 个记号就选出 alt 2。

同一文法再解析 `x b a`：

```text
[SLL] 决策 a @ 'b'
  DFA 命中 D0 --'b'--> D1
  DFA 命中 D1 --'a'--> D2
  DFA 命中 D2 --'EOF'--> D3
  D3 是 SLL 冲突状态 → 全上下文 LL
  [LL] γ0=[p17 p10] {(p23,1,[p17 p10]), (p17,2,[p10])}
  [LL] --'b'--> {(p17,1,[p10])}
```

SLL 部分**全部命中缓存**，直接走到冲突状态；但 **LL 的结果不缓存**，因为它依赖调用栈。上下文相关的决策每次都要付一次全上下文模拟的代价，这是 ALL(\*) 的性能瓶颈。两次解析的统计：

```text
{'atn_steps': 5, 'sll_ok': 2, 'sll_conflict': 2, 'll_predict': 2, 'dfa_hits': 3}
```

**SLL 何时停止**（`PredictionMode.hasSLLConflictTerminatingPrediction`）：存在一个按 (状态, 栈) 分组后含多个备选的子集，**并且**没有任何状态只关联一个备选；或者所有配置都已到达规则出口。

**LL 何时停止**：只剩唯一备选；或者每个冲突子集的**最小备选都相同**，此时无论往后看多远都会选它。后一种情况就是真二义性，ANTLR 报告 `reportAmbiguity` 并选择编号最小的备选。这与 POSIX 和回溯引擎“写在前面的分支优先”是同一个约定。

### 9.6 左递归与优先级谓词

自顶向下预测碰到左递归 `expr : expr '*' expr | ...` 时，closure 会无限地“调用 expr → 调用 expr”。ANTLR 4 允许**直接左递归**，生成 parser 前做一次改写：

```antlr
expr : <assoc=right> expr '^' expr     // 优先级 3（越靠前越高）
     | expr '*' expr                   // 优先级 2
     | expr '+' expr                   // 优先级 1
     | INT
     ;
// 改写为（示意）
expr[int _p]
  : INT
    ( {precpred(_p <= 3)}? '^' expr[3]      // 右结合：右操作数用同一优先级
    | {precpred(_p <= 2)}? '*' expr[3]      // 左结合：右操作数用 优先级+1
    | {precpred(_p <= 1)}? '+' expr[2]
    )*
  ;
```

这就是经典的**优先级爬升**。`{...}?` 是语义谓词，预测时会被求值。由于谓词的结果依赖参数 `_p`，这类决策的 DFA 不能按普通方式缓存。ANTLR 为此建立了专门的**优先级 DFA**（precedence DFA），按 `_p` 区分起始状态。间接左递归 ANTLR 4 仍然报错。

### 9.7 与正则引擎的对照

| | 惰性 DFA（第 6 章） | ANTLR 词法器 | ANTLR 语法预测 |
|---|---|---|---|
| 底层自动机 | Thompson NFA | ATN（无规则调用时即 NFA） | ATN（下推） |
| DFA 状态 | 有序 pc 元组 + matched 标志 | ATN 状态集合 | 配置集 (p, alt, γ, π) |
| 缓存粒度 | 每个正则一个 | 每个词法模式一个 | 每个决策一个 |
| 不可缓存的情况 | 无 | 经过语义谓词 | 全上下文 LL；谓词 |
| 缓存满了怎么办 | 清空；过于频繁则放弃 | 不清空，一直增长（Java 运行时提供 `clearDFA()`） | 同左 |
| 结果语义 | leftmost-first | 最长匹配 + 规则优先级 | 选唯一可行的备选；二义时选最小 |
| 复杂度 | 典型 $O(n)$，最坏 $O(nm)$ | 典型 $O(n)$，回退时最坏 $O(n^2)$ | 理论 $O(n^4)$，实践接近线性 |

ANTLR 的缓存是**静态共享**的（Java 运行时里是 `static DFA[] _decisionToDFA`），同一个 Parser 类的所有实例共用。所以 parser 有明显的预热效应：前几个文件解析时不断模拟 ATN 并填充 DFA，之后几乎全部是查表。

**两阶段解析**是官方推荐的提速技巧：先用纯 SLL 加 `BailErrorStrategy`（一出错立即抛异常）解析一遍；失败了再切回完整的 LL 模式重来。大多数输入第一阶段就能成功，而第一阶段成功时结果一定正确。

### 9.8 练习

1. 为 `ATNLexer` 加入词法模式：每条规则可以带一个模式名，动作可以切换模式。每个模式使用独立的起始状态和缓存。用它实现 Python 风格的三引号字符串。
2. 实现 ANTLR 词法器的非贪婪循环：让 `'/*' .*? '*/'` 在输入 `/* a */ b */` 上只匹配到第一个 `*/`。提示：在规则停止状态处剪掉“经过非贪婪决策、且同一规则已经接受过”的配置。
3. 在 `allstar.py` 中加入语义谓词：配置携带一个谓词集合，遇到谓词时不添加 DFA 边。设计一个例子，说明如果错误地缓存了经过谓词的边，会得到错误的预测。
4. 在 `allstar.py` 中实现两阶段解析：第一阶段把 SLL 冲突直接当作错误抛出，第二阶段才用全上下文 LL。统计上面两个文法在随机输入上的第一阶段成功率。

---
## 第 10 章　工业引擎剖析

前面九章分别实现了回溯、Pike VM、BitState、完全 DFA、惰性 DFA、反向程序，以及词法器与 ANTLR 的变体。生产级的正则库对外只暴露一个 `Regex` 类型，内部则根据模式和输入组合这些部件。本章先把 `regexlab` 的部件组装成一个“元引擎”，然后逐一剖析主流实现。

### 10.1 三段式搜索

DFA 不知道匹配从哪里开始，也不知道捕获组。RE2 和 Rust `regex` 在绝大多数搜索中走的快速路径是把问题拆成三段：

1. **正向惰性 DFA**（leftmost-first，第 6.5 节）求匹配**终点** $e$；
2. **反向惰性 DFA**（锚定、最长匹配，第 6.6 节）从 $e$ 往回扫描，求**起点** $s$；
3. 只在 $[s, e]$ 内运行 Pike VM 或 BitState 求**捕获组**（第 5.6 节）。

```python
class ThreePhase:
    def __init__(self, prog, ngroups, use_prefilter=True, **lazy_kw):
        self.fwd = LazyDFA(prog, **lazy_kw)                       # 非锚定，leftmost-first
        self.rev = LazyDFA(reverse_prog(prog), anchored=True, longest=True, **lazy_kw)
        lits = prefix_literals(prog) if use_prefilter else None   # 第 12 章
        self.pre = Prefilter(lits) if lits else None

    def search(self, text, pos=0):
        if self.pre is not None:
            i = self.pre.find(text, pos)
            if i < 0:
                return None               # 没有候选，必然没有匹配
            pos = i                       # 起点不可能早于 i
        n = len(text)
        try:
            k = self.fwd.run(View(text, pos, n), at_start=(pos == 0), at_end=True)
            if k is None:
                return None
            e = pos + k
            k = self.rev.run(View(text, pos, e, backward=True),
                             at_start=(e == n),           # 反向的 ^ 就是正向的 $
                             at_end=(pos == 0))           # 反向的 $ 就是正向的 ^
            return (e - k, e)
        except GaveUp:                    # 惰性 DFA 放弃：退回 Pike VM
            return pike_search(self.prog, text, pos)
```

`View` 是一个不复制的只读视图，`backward=True` 时倒着迭代。反向扫描通常只走很短一段就停下，如果每次都构造 `text[:e][::-1]`，复制本身就要 $O(e)$。

#### 10.1.1 为什么这样得到的就是正确的匹配

设 $s_0$ 是**最左**的、存在匹配的起点，$(s_0, e)$ 是 Pike VM 给出的 leftmost-first 匹配。分两步论证 `search` 返回的正是 $(s_0, e)$。

**第一步：正向扫描返回 $e$。** 正向 DFA 在每个位置以最低优先级注入新线程，起点越早的线程优先级越高。在 $s_0$ 之前注入的线程永远不会到达 `match`，对结果没有影响。由 $s_0$ 派生的线程，在截断规则下与 Pike VM 的行为逐步一致；在 $s_0$ 之后注入的线程优先级更低，会被截断。一旦见过匹配，注入就停止。所以正向扫描记录的最后一个终点就是 Pike VM 的 $e$。

**第二步：反向扫描返回 $s_0$。** 反向 DFA 以最长匹配模式运行，求的是满足“`text[s:e]` 完整匹配模式”的**最小** $s$（$s \ge$ `pos`）。已知 `text[s₀:e]` 是一个匹配，所以最小的 $s$ 不大于 $s_0$。反过来，任何满足条件的 $s$ 本身就是某个匹配的起点，而 $s_0$ 是所有匹配起点中最左的，所以 $s \ge s_0$。两者结合，$s = s_0$。

第二步用到的是“$s_0$ 是最左起点”，**没有**用到优先级。这就是反向程序可以忽略分支顺序、直接求最长匹配的原因。

> **一个常见的误解：** 不能反过来，先用反向 DFA 求起点，再用正向 DFA 求终点。那样求出的是“最左起点 + 该起点上的**最长**终点”，即 POSIX 语义的终点，而不是 leftmost-first。例如模式 `a|ab`、文本 `ab`：leftmost-first 的结果是 `a`，最长匹配会给出 `ab`。终点必须由带优先级的正向扫描确定。

#### 10.1.2 第三段：限定终点后求捕获组仍然正确

leftmost-first 的匹配，就是从 $s$ 出发、按优先级顺序第一条到达 `match` 的路径 $\pi$，它的终点是 $e$。在所有终点为 $e$ 的路径中，$\pi$ 的优先级仍然最高，所以限定终点后，回溯找到的第一条路径还是 $\pi$。“只读到 $e$”只会砍掉越过 $e$ 的路径，而它们的优先级都低于 $\pi$，否则正向扫描给出的终点就不是 $e$ 了。

这一步的代价是 $O((e-s)\,m)$，与文本总长度无关。对“在一大段日志里找一个短匹配”这种典型场景，Pike VM 只在几十个字符上运行，开销可以忽略。

### 10.2 元引擎

| 引擎 | 优势 | 劣势 |
|---|---|---|
| 字面量搜索 | 极快 | 只适用于纯字面量 |
| BitState | 小输入上常数极小，直接给出捕获 | 需要 $O(nm)$ 位图，只适合短区间 |
| Pike VM | 总能给出捕获，最坏 $O(nm)$ | 常数大 |
| 惰性 DFA | 典型线性，常数小 | 只给终点；缓存可能失效 |
| 反向 DFA | 给出起点 | 依赖正向扫描的结果 |
| 回溯 | 支持反向引用、环视 | 最坏指数级，必须加预算 |

`regexlab.meta.Regex` 的决策分为两个阶段。

**编译时**，根据模式本身决定：

1. 用到反向引用、环视或原子组吗？用到了，就只能交给带步数预算的回溯引擎；
2. 是纯字面量吗？是的话直接用 `str.find`；
3. 是起始锚定的吗？是的话 `pos > 0` 时直接返回 `None`；
4. 用到 `\b` 吗？本实现的 DFA 不支持，交给 Pike VM；
5. 能提取前缀字面量吗？能就启用预过滤。

**运行时**，根据输入决定：

6. 用三段式求匹配区间；惰性 DFA 放弃时退回 Pike VM；
7. 需要捕获组时，区间足够短（`(e - s + 1) × len(prog) ≤ 256K`）就用 BitState，否则用 Pike VM。

```text
hello                strategy=literal   prefilter=None
^\d+$                strategy=dfa       prefilter=None
hello\w+             strategy=dfa       prefilter=['hello']
\bfoo\b              strategy=pikevm    prefilter=None
(a+)b\1              strategy=backtrack prefilter=None
(\w+)@(\w+)\.com     strategy=dfa       prefilter=None
[a-z]+ing            strategy=dfa       prefilter=None

Regex(r'(\w+)@(\w+)\.com').search('mail: bob@ex.com!')    → (6, 16)
Regex(r'(\w+)@(\w+)\.com').captures('mail: bob@ex.com!')  → [(6, 16), (6, 9), (10, 12)]
list(Regex('a*').finditer('baa'))                          → [(0, 0), (1, 3)]
```

`(\w+)@(\w+)\.com` 和 `[a-z]+ing` 没有前缀字面量，但它们分别**包含** `@` 和**以** `ing` **结尾**。第 12 章会讨论如何利用这类“内部字面量”和“后缀字面量”。

### 10.3 OnePass DFA

如果模式满足：**在任意位置，至多只有一个分支能继续前进**，那么捕获组可以在一次确定性扫描中完成，不需要维护线程列表。例如 `(\d+)-(\d+)`：读到数字时只能留在第一个循环，读到 `-` 时只能进入第二部分。这样的模式称为 **one-pass**（一遍）的。

OnePass DFA 的每个状态对应一个 NFA 状态（而不是状态集合），每条转移上附带“在这里保存哪些捕获槽”的动作。构造时检查 one-pass 条件，不满足就放弃。它把第三段的代价从 $O((e-s)\,m)$ 降到 $O(e-s)$，是捕获组性能的关键。RE2（`onepass.cc`）、Go（`onepass.go`）和 Rust（`dfa::onepass`）都实现了它，通常只用于**锚定**的搜索，也就是三段式的第三段。

### 10.4 RE2

RE2 由 Russ Cox 在 Google 开发，最初用于 Google Code Search，2010 年开源。设计目标只有一条：**不管模式和输入是什么，都保证线性时间和有界内存**。

- **前端**：`Regexp` 解析树 → `Simplify`（化简、展开计数重复）→ 编译为 `Prog`。`Prog` 在**字节**上运行，Unicode 字符类在编译时展开为 UTF-8 字节序列；
- **引擎**：
  - `DFA`：惰性 DFA，支持 `kFirstMatch`、`kLongestMatch`、`kFullMatch` 三种模式，状态缓存超出内存预算时清空重建，频繁清空则报告失败；
  - `OnePass`：one-pass 模式的捕获；
  - `BitState`：位图不超过 256 Kbit 时的有界回溯；
  - `NFA`：Pike VM，最后的保底；
- **执行流程**（`RE2::Match`）：先尝试正向 DFA 求终点、反向 DFA 求起点；需要捕获组时，在区间内依次尝试 OnePass、BitState、NFA。DFA 内存耗尽时整次搜索退回 NFA；
- **加速**：前缀字面量用 `memchr` 或大小写不敏感的前缀搜索跳过；
- **多模式**：`RE2::Set` 把多个模式编译进一个 DFA，一遍扫描报告哪些模式匹配；`FilteredRE2` 先提取每个模式的必需字面量，用字面量匹配过滤后，只对候选模式运行完整匹配；
- **不支持**：反向引用、环视。

### 10.5 Go `regexp`

Go 的 `regexp` 也由 Russ Cox 编写，与 RE2 同源，但实现更简单：

- 在**码点**（rune）上运行，字符类保留为区间列表；
- 引擎只有三个：`onepass`、`backtrack`（BitState，要求程序不超过 500 条指令、位图不超过 256 Kbit）、Pike VM。**没有 DFA。** 这是 Go 正则在很多基准中比 RE2 和 Rust 慢一个数量级的主要原因；
- 前缀字面量用 `strings.Index` 加速；
- 同样保证线性时间，不支持反向引用和环视。

### 10.6 Rust `regex` 与 `regex-automata`

Rust 的 `regex` crate 由 Andrew Gallant（BurntSushi）维护。1.9 版（2023）起，内部由 `regex-automata` 实现，模块划分与本报告的章节几乎一一对应：

| 模块 | 内容 | 本报告 |
|---|---|---|
| `regex-syntax` | `Ast` → `Hir`；Unicode 表；字面量提取；UTF-8 序列 | 第 2、11、12 章 |
| `nfa::thompson` | 字节级 Thompson NFA，`PikeVM`，`BoundedBacktracker` | 第 4、5 章 |
| `dfa::onepass` | OnePass DFA | 10.3 节 |
| `hybrid` | 惰性 DFA（含 `Cache`、清空与放弃策略） | 第 6 章 |
| `dfa::dense` / `dfa::sparse` | 完全 DFA，可最小化，可序列化后在编译期嵌入 | 第 6 章 |
| `meta` | 元引擎 | 本章 |
| `util::prefilter` | 预过滤：`memchr`、`memmem`、`aho-corasick`（含 Teddy） | 第 12 章 |

`meta::Regex` 在编译时选择**策略**：

- `Pre`：模式就是若干个字面量的选择，直接用预过滤器求匹配；
- `Core`：通用路径，即三段式加捕获引擎选择；
- `ReverseAnchored`：模式以 `$` 结尾，直接从文本末尾反向扫描；
- `ReverseSuffix`：模式有一个后缀字面量，先找后缀，再从后缀处反向扫描求起点；
- `ReverseInner`：模式有一个内部字面量，先找它，再分别向两侧扫描。

后两种策略在 leftmost-first 语义下有微妙的正确性与复杂度问题，实现中带有一组检查，一旦发现可能退化为二次时间就退回 `Core`（第 12 章）。

Unicode 单词边界 `\b` 需要知道相邻字符是否是 Unicode 单词字符，而惰性 DFA 在字节上运行。`hybrid` DFA 的做法是：遇到非 ASCII 字节时**放弃**，交给 Pike VM 等引擎处理。

### 10.7 PCRE2

PCRE（Perl Compatible Regular Expressions）由 Philip Hazel 在 1997 年开始编写，PCRE2 是 2015 年起的新 API。它被 PHP、Nginx、R、Git（可选）、Apache 等大量项目使用。

- **`pcre2_match()`**：解释执行的回溯引擎。10.30 版起把回溯帧从 C 调用栈移到堆上分配的向量中，解决了深度递归导致的栈溢出问题；
- **`pcre2_dfa_match()`**：另一种匹配算法。它在一个起点上同时推进所有路径，报告**所有**能匹配的长度（最长的在前）。它不支持捕获组和反向引用，名字里的“DFA”其实是 NFA 模拟；
- **JIT**：`pcre2_jit_compile()` 用 sljit 把模式编译成本机代码，通常比解释器快数倍到一个数量级；
- **启动优化**：编译时计算“第一个代码单元”“必需的代码单元”“最小匹配长度”，搜索时用它们快速跳过不可能的位置；
- **资源限制**：`match_limit`（回溯步数）、`depth_limit`、`heap_limit`；
- **功能最全**：反向引用、所有环视、递归 `(?R)`、条件分支、回调、`\K`、Unicode 属性。

### 10.8 Java `java.util.regex`

- `Pattern` 把正则编译成一棵 `Node` 对象树（`CharProperty`、`Branch`、`Loop`、`GroupHead`、`BnM` 等），`Matcher` 沿这棵树递归调用 `match()`，本质是回溯；
- 纯字面量部分会用 Boyer–Moore 风格的 `BnM` 节点加速；
- 回溯深度受 Java 线程栈限制，`(a|b)*` 这类模式匹配很长的输入时会抛出 `StackOverflowError`；
- **没有超时 API。** 常见的变通办法是传入一个自定义的 `CharSequence`，在 `charAt` 中检查时间或中断标志并抛出异常；
- 支持占有量词、原子组、有长度上限的后行断言、类内交集 `[a-z&&[^aeiou]]`。

### 10.9 .NET `System.Text.RegularExpressions`

.NET 是功能最丰富、执行方式最多样的引擎之一：

| 模式 | 执行方式 |
|---|---|
| 默认 | `RegexInterpreter`：解释执行回溯操作码 |
| `RegexOptions.Compiled` | 运行时用 `Reflection.Emit` 生成 IL，再由 JIT 编译为本机代码 |
| 源生成器（.NET 7） | `[GeneratedRegex]` 在**编译期**生成 C# 源码，没有启动开销，代码可读、可调试 |
| `RegexOptions.NonBacktracking`（.NET 7） | 基于**符号导数**的自动机引擎（第 7 章），惰性构造 DFA，必要时退回 NFA 模拟，保证线性时间；不支持反向引用、环视、原子组等 |

- **超时**：构造 `Regex` 时可以传入 `matchTimeout`，也可以通过 `AppContext` 设置进程级默认值。超时后抛出 `RegexMatchTimeoutException`；
- **向量化**：.NET 7 起，对模式开头的字符集合用 SIMD 加速的 `IndexOfAny` 系列方法跳过不可能的位置；
- **独特功能**：平衡组 `(?<open-close>...)` 可以匹配嵌套结构；后行断言支持任意变长；`RightToLeft` 模式从右向左匹配。

### 10.10 V8 Irregexp（JavaScript）

- **Irregexp**（2008，Erik Corry 等）把正则编译为本机代码，是回溯引擎；
- **分层执行**（2019 年前后）：新正则先编译成字节码由解释器执行，执行足够多次后再编译成本机代码。大量只执行一两次的正则因此省去了昂贵的编译；
- **线性引擎**（2021）：V8 加入了一个实验性的非回溯引擎（`--enable-experimental-regexp-engine`，配合 `l` 标志），并且可以在回溯次数过多时自动切换到它（`--enable-experimental-regexp-engine-on-excessive-backtracks`）。它只支持不含反向引用、环视等特性的模式；
- JavaScript 的语义细节与 Perl 系不同：未参与匹配的组被反向引用时匹配空串；`u`/`v` 标志切换到 Unicode 码点语义；`y`（sticky）标志要求在 `lastIndex` 处锚定。

### 10.11 Python `re`

- `sre_parse`（Python 代码）把模式解析成中间表示，`sre_compile` 编译成一个整数列表形式的代码，由 C 实现的 `_sre` 执行。`_sre` 是回溯引擎，用显式的数据栈而不是 C 递归；
- 编译结果开头有一个 `INFO` 块，记录前缀字面量、首字符集合、最小/最大长度，`search` 用它们快速跳过不可能的起点；
- `re` 模块缓存最近编译的模式；
- 3.11 起支持原子组和占有量词；后行断言必须定长；
- 第三方 `regex` 模块提供更完整的功能：变长后行断言、模糊匹配、`\X` 字素簇、POSIX 最长匹配模式等。

### 10.12 Hyperscan / Vectorscan

Hyperscan 由 Sensory Networks 开发，后被 Intel 收购，2015 年开源，面向网络入侵检测、深度包检测这类**成千上万条规则同时匹配**的场景。Vectorscan 是支持 ARM 等平台的社区分支。

- **编译**：每条规则构造成 Glushkov 风格的 NFA 图，再按其中的**字面量**拆解。由 Rose 组件协调：先用字面量匹配器找候选，再按需启动局部的自动机；
- **字面量匹配器**：**FDR**（基于 SIMD 的分桶哈希，适合大量字面量）和 **Teddy**（用 `pshufb` 在半字节上查表，适合几十个短字面量，第 12 章）；
- **自动机引擎**：McClellan（普通 DFA）、Sheng（状态不超过 16 个的小 DFA，用一条 `pshufb` 完成一次转移）、LimEx NFA（位并行 NFA，最多数百个状态）、Castle（有界重复 `x{m,n}`）等；
- **流式模式**：数据分块到达，每条流只保留固定大小的状态，可以跨包匹配；
- **语义**：默认只报告匹配的**终点**（以及规则编号），起点（SOM）需要额外开启并付出代价；不支持捕获组、反向引用、环视。

### 10.13 GNU grep

- `dfa.c`：在匹配过程中按需构造 DFA 状态，也就是惰性 DFA；
- `kwset.c`：多字符串搜索，用于从模式中提取的必需字面量；
- 编译时用 `dfamust` 提取每个匹配都必须包含的字面量，先用 kwset 找候选行，再用 DFA 确认；
- 遇到反向引用等 DFA 无法处理的特性时，在候选行上退回 glibc 的 `regexec`。

grep 以“行”为单位工作，这让它的很多优化变得简单：任何匹配都不会跨行，所以字面量过滤可以直接定位到行。

### 10.14 汇总

| 实现 | 回溯 | BitState | Pike VM | OnePass | 惰性 DFA | 完全 DFA | 预过滤 | JIT / 代码生成 | 线性保证 |
|---|---|---|---|---|---|---|---|---|---|
| RE2 | | ✓ | ✓ | ✓ | ✓ | | 前缀 | | ✓ |
| Go `regexp` | | ✓ | ✓ | ✓ | | | 前缀 | | ✓ |
| Rust `regex` | | ✓ | ✓ | ✓ | ✓ | 可选 | 前缀/后缀/内部，SIMD | | ✓ |
| PCRE2 | ✓ | | | | | | 首字符、必需字符 | ✓（sljit） | |
| Java | ✓ | | | | | | Boyer–Moore | | |
| .NET | ✓ | | | | ✓（NonBacktracking） | | SIMD 首字符集 | ✓（IL、源生成器） | 仅 NonBacktracking |
| V8 | ✓ | | | | | | | ✓（本机代码） | 仅实验引擎 |
| Python `re` | ✓ | | | | | | 前缀、首字符集 | | |
| Hyperscan | | | | | | ✓ | FDR / Teddy | | ✓ |
| GNU grep | 退回 glibc | | | | ✓ | | kwset | | 无反向引用时 ✓ |
| `regexlab` | ✓ | ✓ | ✓ | | ✓ | ✓ | 前缀 | | 无反向引用/环视时 ✓ |

### 10.15 练习

1. 用 `regexlab` 的部件实现 `ReverseAnchored` 策略：对以 `$` 结尾、开头没有 `^` 的模式，从文本末尾直接运行反向 DFA。说明它为什么不需要正向扫描。
2. 实现 OnePass 检查：对编译后的程序，判断是否存在某个状态集合中，两个线程在同一个字符上都能前进。在 `(\d+)-(\d+)`、`(a*)(a*)`、`(a|ab)c` 上测试。
3. 为 `Regex.is_match` 实现“最早匹配”快速路径：正向扫描进入含 `match` 的状态就立即返回，不做反向扫描（`LazyDFA.run(earliest=True)`）。在一段很长、匹配出现得很早的文本上比较它与 `search` 的速度。
4. 阅读 Rust `regex-automata` 中 `meta::strategy` 的源码，找出 `ReverseSuffix` 在什么条件下会退回 `Core`，并用 10.1.1 节的论证解释原因。

---
## 第 11 章　高级专题：Unicode、锚点、环视、反向引用、计数重复

前面各章的核心算法都建立在“单行、ASCII、纯正则”的简化之上。本章逐一拆掉这些简化，看每一项特性会给各类引擎带来什么问题。

### 11.1 Unicode：码点还是字节

一个引擎首先要决定在什么单位上运行：

| 单位 | 代表 | 好处 | 代价 |
|---|---|---|---|
| UTF-16 代码单元 | Java、.NET、JavaScript（无 `u` 标志） | 与语言的字符串表示一致 | 代理对拆成两个“字符”；`.` 可能只匹配半个字符 |
| 码点 | Go、Python、`regexlab` | 语义直观 | 字母表巨大，DFA 需要等价类和二分查找；通常要先解码 |
| 字节（UTF-8） | RE2、Rust、Hyperscan、grep | DFA 字母表只有 256，查表无分支；不解码 | 编译器要把码点区间翻译成字节序列的选择；匹配可能落在字符中间 |

#### 11.1.1 把码点区间编译成 UTF-8 字节序列

在字节上运行时，`[\u00e0-\u00ff]` 这样的字符类必须翻译成一组字节序列。难点在于 UTF-8 的变长编码：一个码点区间对应的字节串，一般不能用“每个字节一个区间”的乘积来表示。`regexlab/utf8.py` 实现了 Rust `regex-syntax` 中 `Utf8Sequences` 的思路，分三步切分：

1. **去掉代理区** U+D800–U+DFFF，它们没有合法的 UTF-8 编码；
2. **按编码长度切开**：在 U+007F、U+07FF、U+FFFF 处切分，使每段内所有码点的编码长度相同；
3. **让续字节覆盖完整范围**：如果区间的高位前缀不同，就在低位全 0 或全 1 的边界处继续切分，直到每一段的字节可以逐位配对。

```python
def utf8_sequences(lo, hi):
    out, stack = [], [(lo, hi)]
    while stack:
        lo, hi = stack.pop()
        if lo <= 0xDFFF and hi >= 0xD800:          # 1) 去掉代理区
            stack.append((0xE000, hi)); stack.append((lo, 0xD7FF)); continue
        for b in (0x7F, 0x7FF, 0xFFFF):            # 2) 按编码长度切开
            if lo <= b < hi:
                stack.append((b + 1, hi)); stack.append((lo, b)); break
        else:
            if hi <= 0x7F:
                out.append([(lo, hi)]); continue
            for i in range(1, 4):                  # 3) 让续字节覆盖完整的 0x80–0xBF
                m = (1 << (6 * i)) - 1
                if lo & ~m != hi & ~m:
                    if lo & m != 0:
                        stack.append(((lo | m) + 1, hi)); stack.append((lo, lo | m)); break
                    if hi & m != m:
                        stack.append((hi & ~m, hi)); stack.append((lo, (hi & ~m) - 1)); break
            else:
                out.append(list(zip(encode(lo), encode(hi))))   # 逐字节配对
    return out
```

实际输出：

```text
  U+0000–U+10FFFF:              （即 Rust 的“任意合法 UTF-8 码点”）
      [00-7F]
      [C2-DF] [80-BF]
      [E0] [A0-BF] [80-BF]
      [E1-EC] [80-BF] [80-BF]
      [ED] [80-9F] [80-BF]          ← 跳过了代理区 ED A0–BF
      [EE-EF] [80-BF] [80-BF]
      [F0] [90-BF] [80-BF] [80-BF]
      [F1-F3] [80-BF] [80-BF] [80-BF]
      [F4] [80-8F] [80-BF] [80-BF]
  U+00E0–U+00FF:
      [C3] [A0-BF]
  U+4E00–U+9FFF:                （CJK 统一表意文字）
      [E4] [B8-BF] [80-BF]
      [E5-E9] [80-BF] [80-BF]
```

第一组正是 UTF-8 规范中“合法字节序列”的表格，它同时排除了超长编码（`C0`、`C1`、`E0 80`–`E0 9F`）和超出 U+10FFFF 的码点。`regexlab` 用两千个随机区间、每个区间二十个随机码点验证了切分的正确性。

这些序列编进 NFA 后会有大量公共后缀（`[80-BF]`），Rust 的编译器会对后缀做共享，以免 `\w` 这样的大字符类产生上万个状态。RE2 的编译器对此也有专门的缓存。

#### 11.1.2 Unicode 字符类有多大

`\w` 在 ASCII 模式下只有 63 个字符，在 Unicode 模式下有十几万个码点，分布在数百个区间中。按字节编译后的 NFA 状态数也随之增长。Rust `regex` 的文档专门提醒：Unicode 版的 `\w` 会让编译后的程序显著变大，必要时可以用 `(?-u:\w)` 退回 ASCII 语义。

#### 11.1.3 大小写折叠

`(?i)` 远不止 `lower()`：

```text
'İ'.lower() 长度: 2       'ß'.upper(): SS       'K'(U+212A).lower(): 'k'
```

- **简单折叠与完全折叠。** Unicode 的 `CaseFolding.txt` 区分简单折叠（一个码点对一个码点）和完全折叠（可能一对多，如 `ß → ss`）。正则引擎几乎都只用**简单折叠**，所以 `(?i)ß` 不匹配 `"SS"`；
- **折叠等价类。** `(?i)k` 要匹配 `k`、`K` 和开尔文符号 `K`（U+212A）。编译时需要为每个码点计算它的完整折叠等价类，而不是只取大小写两个变体；
- **字符类先折叠还是先取反？** `(?i)[^k]` 应当排除 `k`、`K`、`K` 三者。正确顺序是先对类中的字符做折叠闭包，再取反；
- **对预过滤的影响。** `(?i)hello` 展开后有 32 种大小写组合，很快超出字面量集合的上限。“先把文本整体转小写再查找”在 ASCII 范围内可行，在 Unicode 范围内不可行：`'İ'.lower()` 有两个码点，转换后偏移整体错位。

#### 11.1.4 不归一化

`é` 可以写成一个码点 U+00E9，也可以写成 `e` 加组合重音符 U+0301。几乎所有正则引擎都**不做**归一化：`é` 只匹配与模式中相同的码点序列。需要归一化语义的程序应当先对文本和模式统一做 NFC 或 NFD。

### 11.2 锚点与多行模式

| 写法 | 含义 | 注意 |
|---|---|---|
| `^`、`$` | 单行模式下是文本开头、结尾 | Python、Perl、PCRE 的 `$` 还匹配**末尾换行符之前**的位置；Rust、Go、RE2 不这样做 |
| `(?m)^`、`(?m)$` | 行首、行尾 | “行”的定义：只认 `\n`，还是也认 `\r\n`、U+2028？各家不同 |
| `\A`、`\z` | 永远是文本开头、结尾 | Python 用 `\Z` 表示 `\z` |

在自动机中，`^` 和 `$` 都是“看一眼相邻字符”的零宽断言：

- **Pike VM 与回溯**：在 ε 闭包里直接判断，`assert_ok(kind, text, i)` 同时能看到 `text[i-1]` 和 `text[i]`；
- **DFA**：转移只看**下一个**字符，看不到上一个字符。多行的 `^` 依赖上一个字符是否为 `\n`，所以 DFA 状态必须额外记住这个信息。RE2 把“上一个字符是否为换行、是否为单词字符”编码成状态的标志位；Rust 的 DFA 在状态中保存“look-behind”信息。`$` 则用第 6 章的“悬而未决”技巧：把断言留在状态里，等看到下一个字符或文本结尾时再裁决。

### 11.3 单词边界 `\b`

`\b` 的成立取决于**前后两个**字符是否为单词字符：

```python
def assert_ok(kind, text, i):
    ...
    before = text[i - 1] if i > 0 else None
    after = text[i] if i < len(text) else None
    b = is_word(before) != is_word(after)
    return b if kind == 'wordb' else not b
```

```text
\b 由 Pike VM 处理: Regex(r'\bcat\b').search('concat cat') → (7, 10)
```

在 DFA 中实现 `\b`，需要状态同时记住“上一个字符是否为单词字符”，并把 `\b` 的裁决推迟到读入下一个字符时。ASCII 的 `\b` 只看一个字节，容易做；**Unicode** 的 `\b` 需要解码前一个完整的码点，在字节 DFA 中很难。Rust 的惰性 DFA 遇到非 ASCII 字节时会放弃，交给其他引擎（第 10.6 节）。`regexlab` 的 DFA 干脆不支持 `\b`，元引擎把含 `\b` 的模式交给 Pike VM，这正是“特性决定算法”的又一例。

### 11.4 环视

回溯引擎实现环视非常自然（第 3.7 节），代价是失去了复杂度保证。线性引擎能不能支持环视？

- **正向先行断言 `(?=r)`** 本质上是交集：$x(?=r)y$ 要求 $y$ 处开始的后缀同时匹配 $r$ 和 $y\ldots$。在导数框架中，可以用 `&` 直接表达（第 7 章）；在自动机中，相当于在乘积自动机上运行；
- **后行断言**可以用反向扫描预先计算“哪些位置满足断言”，再在正向扫描时查询。

研究上已经有线性时间支持环视的方法。例如 Barrière 与 Pit-Claudel 在 PLDI 2024 上给出了 JavaScript 正则（含环视）的线性匹配算法，并以 V8 的非回溯引擎为基础做了实现。但工业界的主流线性引擎（RE2、Go、Rust、.NET NonBacktracking）目前仍然不支持环视。用户需要环视时，通常用“先匹配再用代码检查”或“两个正则组合”来替代。

### 11.5 反向引用

第 3.6 节已经说明：带反向引用的匹配是 NP 完全的。所有线性引擎都拒绝它。少数引擎做了折中：

- GNU grep 在候选行上退回 glibc 的回溯实现，候选行通常很短；
- V8 在回溯次数过多时可以切换到线性引擎，但含反向引用的模式不能切换。

如果业务确实需要“前后相同”的约束（例如 HTML 标签配对 `<(\w+)>.*</\1>`），更稳妥的做法是用正则提取候选，再用代码比较。

### 11.6 计数重复

`x{m,n}` 是正则中最容易让人掉以轻心的语法糖：

| 引擎 | 处理方式 | 风险 |
|---|---|---|
| Thompson 构造（RE2、Rust、`regexlab`） | 展开成 $n$ 份子程序 | 程序膨胀：`(?:a{100}){100}` 就是一万条指令（第 4.4 节） |
| DFA | 在展开后的程序上做子集构造 | `.{30}x` 类模式状态爆炸；`(a\|b)*a(a\|b){k}` 需要 $2^{k+1}$ 个状态（第 6.3 节） |
| 回溯 | 用计数器循环，不展开 | 程序不膨胀，但回溯的歧义问题依旧 |
| Hyperscan | Castle 引擎专门处理有界重复，用环形缓冲记录重复的起点 | 状态大小与 $n$ 有关 |
| 计数自动机（研究） | 状态里带计数器，或用“计数集合”表示所有可能的计数值 | Turoňová 等（OOPSLA 2020）的计数集合自动机能在很多情况下避免爆炸 |

工程上的底线是：**在编译之前估算规模，超过阈值就拒绝**（RE2 的计数上限 1000、程序内存上限；`regexlab` 的 `estimate_size`）。

### 11.7 非贪婪量词在 DFA 中的意义

非贪婪量词只影响**选择哪一个匹配**，不影响**是否匹配**。所以：

- 对 `is_match` 和完全 DFA，`a*?` 与 `a*` 完全等价；
- 对 leftmost-first 的惰性 DFA，非贪婪通过 `split` 的顺序进入有序状态，再通过截断规则生效（第 6.5.1 节）；
- 对 POSIX 的 leftmost-longest 语义，非贪婪没有意义。POSIX 本身也没有定义它。

### 11.8 练习

1. 把第 6 章的 `DFA` 改造成按字节运行：用 `utf8_sequences` 把每个字符类编译成字节序列的选择，文本先编码成 UTF-8。用 `'aé中'` 作字母表做差分测试，并写一个从字节偏移换算回码点偏移的函数。提示：码点数等于不是续字节（`b & 0xC0 != 0x80`）的字节数。
2. 为 Pike VM 实现多行模式的 `^`、`$`，并考虑 `\r\n`：`(?m)$` 是否应在 `\r` 之前成立？比较 Python、PCRE2（`PCRE2_NEWLINE_ANYCRLF`）和 Rust 的选择。
3. 在第 6 章的完全 DFA 中支持 ASCII `\b`：状态键增加“上一个字符是否为单词字符”的标志位，`\b` 断言像 `$` 一样悬而未决，读入下一个字符时裁决。与 Pike VM 做差分测试。
4. 用导数实现正向先行断言：把 `x(?=r)` 翻译成乘积形式，验证 `a(?=b)` 在 `ab`、`ac` 上的结果。说明为什么这种方法不能直接推广到需要报告捕获组的情形。

---
## 第 12 章　性能工程：字面量提取、预过滤、SIMD 与位并行

到目前为止，所有引擎都逐个字符地检查文本。即使是惰性 DFA，每个字符也要做一次等价类查找和一次表查找。但实际使用中，大多数模式都含有一段**固定的字符串**，例如 `ERROR: \d+`、`hello\w+`、`(GET|POST) /`。“这段字符串出现在哪里”可以用 `memchr`、`memmem` 这类高度优化的子串搜索来回答，它们用 SIMD 一次检查 16 到 64 个字节，比任何通用自动机快一个数量级以上。

本章的思路是：先用便宜的字面量搜索找出**候选位置**，再只在候选位置启动正则引擎。这称为**预过滤**（prefilter）。代码见 `regexlab/literals.py`。

### 12.1 正确性条件

预过滤只能加速，不能改变结果。我们要提取的字符串集合 $P$ 必须满足：

> **前缀完备性：** 模式在文本中的**每一个**匹配 `text[s:e]`，都以 $P$ 中的某个字符串开头。

这里只要求“每个匹配都以某个元素开头”，**不**要求“以某个元素开头的地方都有匹配”。$P$ 可以偏大，误报只会浪费时间；$P$ 一旦漏掉了某种匹配的开头，结果就错了。

有了这条性质，搜索可以这样进行：设 $i$ 是 $P$ 中任一字符串在 `pos` 之后最早出现的位置，那么任何匹配的起点都不早于 $i$。直接从 $i$ 开始做三段式搜索，得到的仍是全局最左的匹配。如果 $P$ 中含有空串，这条性质对候选位置就毫无约束，预过滤也就失去了意义。

### 12.2 从程序中提取前缀

直接在编译好的程序上提取：从 pc 0 出发做一次搜索，沿途记录已经确定的字符。

- `char c`：把 `c` 接到当前前缀后面，继续；
- `class`：很小的非取反字符类（比如 `[ab]`）为每个字符分出一个分支，否则在这里停下；
- `any`、`match`：停下；
- `jmp`、`split`、`save`、`assert`：不消耗字符，沿 ε 边继续。

“停下”的意思是把当前前缀加入结果。这个前缀可能比实际的字面量短，但仍满足前缀完备性。对断言直接跳过也是安全的：它只会让我们多考虑一些走不通的路径，$P$ 偏大，但不会漏掉匹配。循环会让前缀无限增长，所以要设长度上限，截断后的前缀依然是合法的前缀。

```python
def prefix_literals(prog, max_len=8, max_count=16, class_limit=4, budget=2000):
    out, seen = set(), set()
    stack = [(0, '')]
    while stack:
        pc, pre = stack.pop()
        if (pc, pre) in seen:             # 同一 pc、同一前缀只处理一次，避免 ε 环
            continue
        seen.add((pc, pre))
        if len(seen) > budget or len(out) > max_count:
            return None                   # 组合爆炸：放弃
        if len(pre) >= max_len:
            out.add(pre)                  # 截断：仍是合法前缀
            continue
        op = prog[pc]
        k = op[0]
        if k == 'char':
            stack.append((pc + 1, pre + op[1]))
        elif k == 'class':
            cs = class_chars(op, class_limit)
            if cs is None:
                out.add(pre)
            else:
                for c in cs:
                    stack.append((pc + 1, pre + c))
        elif k in ('any', 'match'):
            out.add(pre)
        elif k == 'jmp':
            stack.append((op[1], pre))
        elif k == 'split':
            stack.append((op[1], pre)); stack.append((op[2], pre))
        else:                             # save、assert
            stack.append((pc + 1, pre))
    if '' in out or not out:
        return None
    return minimize_literals(out)         # 若 a 是 b 的前缀，去掉 b
```

实际提取结果：

```text
  hello\w+     -> ['hello']                    遇到 \w 停下
  GET|POST     -> ['GET', 'POST']
  a?b          -> ['ab', 'b']                  看起来以 a 开头，其实不是
  x(ab)*y      -> ['xabababa', 'xabababy', 'xababy', 'xaby', 'xy']   循环展开到长度上限
  \d+px        -> None                         \d 太大，第一个字符就停下，得到空串
  a*b          -> ['aaaaaaaa', 'aaaaaaab', 'aaaaaab', 'aaaaab', 'aaaab', 'aaab', 'aab', 'ab', 'b']
  .*foo        -> None                         开头是 any
  (xa|y)b      -> ['xab', 'yb']
  [ab]x        -> ['ax', 'bx']
  ^ab          -> ['ab']                       断言被跳过，集合偏大但正确
```

`a*b` 的结果说明了另一个问题：集合虽然正确，但对 `a*b` 来说最有用的信息其实是“每个匹配都**以 `b` 结尾**”。`\d+px` 和 `.*foo` 也一样：它们显然含有字面量，只是不在开头。12.5 节讨论这种情况。

第 15 章的差分测试对每个随机模式都直接检验了前缀完备性：只要 Pike VM 找到匹配，就检查它的起点处是否出现了 $P$ 中的某个字符串。这条断言比端到端对拍更容易定位错误：一旦失败，问题一定出在 `prefix_literals`。

### 12.3 候选搜索

单个字面量直接用 `str.find`。多个字面量的最简单做法是分别查找，取最早的位置：

```python
class Prefilter:
    def find(self, text, pos):
        best = -1
        for L in self.lits:
            # 只在“能比当前最好结果更早开始”的范围内查找：
            # 起点 j < best 意味着整个出现落在 [pos, best + len(L) - 1) 之内
            j = text.find(L, pos, best + len(L) - 1 if best >= 0 else len(text))
            if j >= 0:
                best = j
        return best
```

注意第三个参数的边界：`str.find(sub, start, end)` 要求整个 `sub` 落在 `[start, end)` 内。要让后续字面量只找“起点早于 `best`”的出现，`end` 应当是 `best + len(L) - 1`，而不是 `best`。写成 `best` 会漏掉跨过 `best` 的更早出现。

即便如此，$k$ 个字面量的代价仍是 $O(kn)$。字面量较多时，生产级实现会改用：

- **Aho–Corasick 自动机**：一遍扫描同时查找所有字面量。`regexlab` 实现了一个版本，返回任一字面量**最早的起点**。标准 Aho–Corasick 按**终点**顺序报告，较长的字面量起点更早却报告得更晚，所以要一直扫描到“当前位置减最大长度”超过当前最早起点为止：

  ```text
  AhoCorasick(['he', 'she', 'hers', 'his']).find('ushers', 0) → 1      （she 从 1 开始）
  ```

- **Teddy**：Hyperscan 发明、Rust `aho-corasick` 移植的 SIMD 算法，专门处理几十个以内的短字面量。它用字面量的前几个字节构造半字节掩码，借助 `pshufb` 在一条指令内并行查 16 或 32 个位置的“桶”，再对候选做精确验证；
- **FDR**：Hyperscan 的大规模字面量匹配器，用 SIMD 分桶哈希处理成千上万个字面量。

### 12.4 在 DFA 内部反复跳跃

12.3 节的做法只在搜索开始时跳一次。如果第一个候选是误报，正向 DFA 接下来就会逐字符扫描，再也用不上预过滤。RE2 和 Rust `regex` 的做法是：**每当正向 DFA 回到起始状态，就调用一次预过滤，跳到下一个候选位置。**

为什么这样是安全的？设 DFA 在位置 $i$ 处于“非开头位置的起始状态”，即状态键等于 `(closure([0]), False)`。这说明此前注入的线程已全部死亡，只剩刚注入的那一个。设预过滤给出的下一个候选位置是 $j$：

- 在 $[i, j)$ 之间注入的线程，起点处都没有 $P$ 中的字符串，由前缀完备性，它们都不可能到达 `match`；
- 所以可以直接丢弃它们，把 DFA 设回起始状态，从 $j$ 继续扫描；
- 状态中的 `matched` 为假，说明还没有记录过匹配终点，跳跃不会丢失结果。

实现时要注意：起始状态的判断必须用**状态键**，不能用状态编号。缓存清空后编号会重新分配。

### 12.5 后缀与内部字面量

`\d+px` 和 `.*foo` 没有可用的前缀，但每个匹配都**包含** `px` 或 `foo`。这类**必需字面量**也能用来加速，只是用法不同。

**快速拒绝**是最简单且一定正确的用法：文本中根本没有某个必需字面量，就直接返回 `None`。对于“用一个模式过滤日志的每一行”这种大量不匹配的输入，这一行判断就能拦掉绝大部分工作。GNU grep 的 `dfamust` 就是这个思路。

**后缀字面量**可以用反向程序提取。由 $L(\mathrm{rev}) = \{\,s^R\,\}$，“反向程序的每个匹配以 $P$ 中某个字符串开头”等价于“原模式的每个匹配以 $P$ 中某个字符串的反转结尾”。所以：

```python
suffixes = [L[::-1] for L in prefix_literals(reverse_prog(prog))]
```

**必需字面量的一般提取**需要在语法树上为每个节点计算一个四元组 `(exact, prefix, suffix, inner)`。其中 `exact` 是该节点能匹配的全部字符串（太多时记为“未知”），`inner` 是“每个匹配都包含它”的字符串。合并规则如下，Ø 表示未知，`""` 表示没有约束：

| 节点 | exact | prefix | suffix | inner |
|---|---|---|---|---|
| 连接 $XY$ | $X.e\times Y.e$ | $X.e$ 已知时取 $X.e\times Y.p$，否则 $X.p$ | 对称 | 在 $X.i$、$Y.i$ 以及 $X.s\times Y.p$ 的公共子串中取最长 |
| 选择 $X\mid Y$ | 并集 | 并集 | 并集 | $X.i$ 与 $Y.i$ 的最长公共子串 |
| $X^+$ | Ø | $X.p$ | $X.s$ | $X.i$ |
| $X^*$、$X?$ | Ø（$X?$ 可取 $X.e\cup\{\text{""}\}$） | 含 `""` | 含 `""` | `""` |

按这个规则，`(ab|cb)d` 的必需字面量是 `bd`。只看各部分自己的 `inner` 只能得到 `b`，必须利用 $\{ab, cb\}\times\{d\} = \{abd, cbd\}$ 才能看出两者都包含 `bd`。这说明 `exact` 和 `suffix` 这类信息不能省略。

**反向后缀 / 反向内部策略**：先找到后缀或内部字面量，再从它的位置往回做反向扫描求起点。这条路线快得多，但保持 leftmost-first 语义很微妙：

- 字面量第一次出现的位置不一定对应最左的匹配。一个起点更早的匹配，可能在字面量更后面的一次出现处才结束；
- 即使找到了起点，正确的终点仍必须由带优先级的正向扫描确定（第 10.1.1 节的“常见误解”）；
- 如果每次都从字面量处向两侧扫描，而大部分候选都是误报，总代价可能退化成二次。

Rust `regex-automata` 实现了 `ReverseSuffix` 和 `ReverseInner`，并附带一组检查：一旦发现可能退化，就在本次搜索的剩余部分退回 `Core` 策略。

### 12.6 何时预过滤反而无用

预过滤不总是划算。实测两个模式在一段约 21 万字符的英文单词文本上的搜索：

```text
  ERROR: \d+     结果(215844, 215854)  预过滤开     0.10ms  关    28.29ms  Python re   0.04ms
  e\w+g          结果None              预过滤开    31.82ms  关    31.67ms  Python re   0.33ms
```

- `ERROR: \d+` 的前缀 `ERROR: ` 很长，在文本中只出现一次，预过滤把搜索变成了一次 `str.find`，快了约 280 倍；
- `e\w+g` 的前缀只有一个 `e`，而英文文本里几乎每隔几个字符就有一个 `e`。`regexlab` 只在搜索开始时跳一次，第一个候选马上就是误报，之后惰性 DFA 照样逐字符扫描，预过滤完全没有帮助。如果实现了 12.4 节的“在 DFA 内部反复跳跃”，每个 `e` 都要付出一次函数调用和重新进入 DFA 的开销，结果可能比不用预过滤还慢。

一般规律是：**字面量越长、越罕见，预过滤收益越大。** 生产实现结合两种手段：

1. **静态估计**：根据字面量的长度和字节的常见程度打分。Rust 的 `memchr` crate 内置了一张按字节统计的频率表，优先挑选罕见字节作为搜索锚点；分数太低就不启用预过滤；
2. **动态退出**：运行时统计每次跳跃平均前进了多少字符，连续多次都很短，就在本次搜索的剩余部分关闭预过滤：

```python
class AdaptivePrefilter(Prefilter):
    def find(self, text, pos):
        if not self.enabled:
            return pos                    # 关闭后：候选就是当前位置，相当于不跳
        j = super().find(text, pos)
        self.calls += 1
        self.skipped += (len(text) if j < 0 else j) - pos
        if self.calls >= self.warmup and self.skipped < self.min_avg_skip * self.calls:
            self.enabled = False
        return j
```

关闭之后返回 `pos` 而不是 -1。返回 -1 会被理解为“没有匹配”，那就错了。这再次体现了预过滤的基本原则：**任何启发式只能影响速度，不能影响结果。**

### 12.7 SIMD：memchr 与 memmem

预过滤的威力来自底层的子串搜索。现代实现的核心技巧是：

- **SWAR / SIMD 的 memchr**：把要找的字节广播到一个 16 或 32 字节的寄存器，与文本做一次逐字节比较（`pcmpeqb`），再用 `pmovmskb` 把比较结果压成位掩码，最后用 `tzcnt` 找出第一个置位。一次迭代检查 16 或 32 个字节；
- **memmem 的“双字节过滤”**：Rust `memchr::memmem` 选出模式中两个罕见的字节，同时检查文本中相隔固定距离的两个位置，只有两者都命中的候选才做完整比较。比只看第一个字节的误报率低得多；
- **Two-Way 算法**：作为最坏情况的保底，保证线性时间、常数空间。

### 12.8 位并行：Shift-And

当模式较短且没有可用的字面量时，可以把状态集合放进一个机器字。**Shift-And**（Baeza-Yates 与 Gonnet，1992）处理“每个位置是一个字符集合”的模式：

- 状态 $D$ 的第 $j$ 位为 1，表示“模式的前 $j+1$ 个位置与以当前字符结尾的文本匹配”；
- 预先为每个字符 $c$ 算出掩码 $B[c]$：第 $j$ 位为 1 当且仅当位置 $j$ 接受 $c$；
- 每读一个字符：$D \leftarrow ((D \ll 1) \mid 1) \,\&\, B[c]$。

```python
def shift_and(pattern_sets, text):
    m = len(pattern_sets)
    B = {}
    for j, cs in enumerate(pattern_sets):
        for c in cs:
            B[c] = B.get(c, 0) | (1 << j)
    D, hit, ends = 0, 1 << (m - 1), []
    for i, c in enumerate(text):
        D = ((D << 1) | 1) & B.get(c, 0)
        if D & hit:
            ends.append(i + 1)
    return ends
```

```text
Shift-And [ab]c 在 "xacbcabc" 的匹配终点: [3, 5, 8]
```

每个字符只需要一次移位、一次或、一次与，没有分支。Wu 与 Manber 把它扩展到允许 $k$ 处错误的近似匹配，这就是 `agrep` 的核心。第 7 章的 Glushkov 位掩码模拟是它对任意正则表达式的推广；Hyperscan 的 LimEx NFA 用 SIMD 寄存器把同样的思路扩展到数百个状态。BNDM 等算法则把位并行与“从右往左跳跃”的思想结合起来。

### 12.9 DFA 内层循环与 JIT

- **DFA 内层循环**：预乘状态编号、特殊状态集中编号、按字节运行、循环展开（第 6.7 节）。Rust 的 dense DFA 在常见输入上可以达到每秒数 GB；
- **JIT / 代码生成**：PCRE2 的 sljit、.NET 的 `RegexOptions.Compiled` 与源生成器、V8 的本机代码，把回溯引擎的解释开销去掉。re2c 把 DFA 直接编译成 C 代码（第 8 章）也是同一个思路：用编译器替代表查找；
- **避免重复编译**：Python `re` 和 .NET 都缓存最近编译的模式。在热循环里反复调用 `re.compile`（或者每次传入不同的字符串字面量）会让缓存失效。

### 12.10 一张粗略的性能对比

下表在约 5 万个随机字符上搜索。所有 `regexlab` 引擎都是纯 Python，Python `re` 是 C 实现，所以**只看同一行内 `regexlab` 各引擎的相对快慢**：

```text
  模式                    结果            PikeVM   惰性DFA    元引擎   Python re   （单位 ms）
  needle\d+              (50000, 50008)    22.0      7.8      0.0       0.01
  [a-c]+j                (11, 13)           0.0      0.0      0.0       0.00
  (a|b)*c(a|b){3}d       (2156, 2161)       2.7      0.4      0.3       0.06
  needle(\d+)            (50000, 50008)    21.8      7.2      0.0       0.01
```

- `needle\d+` 的匹配在文本最末尾：Pike VM 要处理 5 万个位置的线程，惰性 DFA 快近 3 倍，元引擎用前缀 `needle` 直接跳到匹配处，几乎不花时间；
- `[a-c]+j` 的匹配就在开头，所有引擎都瞬间完成；
- `(a|b)*c(a|b){3}d` 没有前缀字面量，元引擎与惰性 DFA 走同一条路径，惰性 DFA 比 Pike VM 快约 7 倍。

### 12.11 练习

1. 实现 12.4 节的“在 DFA 内部反复跳跃”，并在一段含有大量 `hello ` 误报的 10⁶ 字符文本上，比较修改前后 `hello\w+` 的速度。
2. 实现 12.5 节表中的四元组分析，提取 `\d+px`、`.*foo`、`(ab|cb)d` 的必需字面量，并在元引擎中加入“快速拒绝”。
3. 把 `AhoCorasick` 接入 `ThreePhase`，替换 `Prefilter`，用第 15 章的差分测试验证结果不变。
4. 把 `AdaptivePrefilter` 接入练习 1 的实现。关闭预过滤后 `find` 返回 `pos`，DFA 会被“跳”回原位。论证这不会导致死循环，并说明 `start()` 应当在哪里调用。如果忘记调用，会出现什么问题？
5. 用 Shift-And 实现 `[a-z]{3}\d{2}` 这类“定长字符类序列”的搜索，并与惰性 DFA 比较速度。

---
## 第 13 章　匹配语义：leftmost-first 与 leftmost-longest

“正则表达式匹配”这个问题在定义上就有歧义：一段文本里可能有许多子串匹配同一个模式，每个子串的捕获组也可能有多种分配方式。引擎必须选出**一个**结果报告给用户，选择的规则就是**匹配语义**。前面各章在不同地方各用了一种语义，本章把它们放在一起比较。

### 13.1 四种语义

| 语义 | 规则 | 使用者 |
|---|---|---|
| **leftmost-first**（Perl 语义） | 在最左的起点上，选**优先级最高**的匹配：选择按书写顺序、贪婪优先多、非贪婪优先少 | Perl、PCRE、Python、Java、.NET、JavaScript、RE2、Go、Rust |
| **leftmost-longest**（POSIX 语义） | 在最左的起点上，选**最长**的匹配；子表达式也逐级取最左最长 | POSIX `regexec`、awk、grep、egrep、TRE、musl |
| **最长匹配 + 规则优先级**（maximal munch） | 锚定在当前位置；所有规则中最长的胜出，同长时书写在前的胜出 | lex/flex、re2c、JFlex、ANTLR 词法器（第 8、9 章） |
| **报告所有匹配 / 最早匹配** | 报告每一个匹配终点；或者一旦确定存在匹配就返回 | Hyperscan、`is_match` 快速路径、RE2 的 `Set` |

```text
模式 a|ab，文本 "ab"
  leftmost-first   →  "a"      左分支先成功，右分支不会被尝试
  leftmost-longest →  "ab"
  最长匹配（词法）  →  "ab"
```

Go 的 `regexp` 同时提供两种语义：默认是 leftmost-first，`regexp.CompilePOSIX` 或 `Longest()` 切换到 leftmost-longest。

### 13.2 leftmost-first 与“优先级”

leftmost-first 可以精确地定义为：**所有从最左起点出发的成功路径中，按优先级字典序最小的那一条。** 路径的优先级由它在每个 `split` 处选择了哪个分支决定，优先分支记为 0，另一个记为 1，整条路径就是一个 0/1 序列。

- 回溯引擎按字典序深度优先搜索，第一个成功的路径就是答案（第 3 章）；
- Pike VM 用有序线程列表和截断规则在线性时间内得到同一条路径（第 5 章）；
- 惰性 DFA 用有序状态得到同一条路径的终点，反向 DFA 得到起点（第 6、10 章）。

第 10.1.1 节证明了三段式搜索与 Pike VM 给出相同的区间。第 15 章的差分测试在全部随机用例上验证了这一点。

### 13.3 POSIX：最长匹配与子匹配规则

POSIX 规定：

1. 整体匹配取**最左**起点上的**最长**匹配；
2. 在整体匹配确定之后，每个子表达式按从左到右的顺序，依次取在**不影响前面已确定部分**的前提下最左、最长的匹配。

第二条才是难点。看一个经典例子：

```text
模式 (a|ab)(c|bcd)(d*)，文本 "abcd"
  leftmost-first  : 整体 (0,4)，组 1 = "a"  (0,1)，组 2 = "bcd" (1,4)，组 3 = ""  (4,4)
  leftmost-longest: 整体 (0,4)，组 1 = "ab" (0,2)，组 2 = "c"   (2,3)，组 3 = "d" (3,4)
```

第一行是 `regexlab` 的 Pike VM 与 Python `re` 的实际输出。两种语义的整体匹配相同，子匹配完全不同：POSIX 要求组 1 先取最长的 `ab`，再在剩下的部分里为组 2、组 3 分配。

POSIX 子匹配语义出了名地难以正确实现：

- 按 pc 去重的 Pike VM 会丢掉“同 pc、捕获不同”的线程，而按 POSIX 规则，后到的那个可能才是正确的（第 5.8 节）；
- 正确实现需要在去重时比较两个线程的捕获历史，Laurikari（2001）的 TRE、Okui 与 Suzuki（2010）、Trofimovich（2017–2020）先后给出了不同的算法；
- Chris Kuklewicz 曾系统测试过各个 POSIX 实现，发现大多数在嵌套重复与子匹配的组合上给出错误结果。Glenn Fowler 整理的 AT&T POSIX 测试集至今被 RE2、Rust 等项目用来测试 leftmost-longest 模式。

re2c 的 `--posix-captures` 和 musl libc 的正则实现都基于这些研究。

### 13.4 空循环：三种引擎，三种答案

第 3 章和第 5 章都碰到了空循环：循环体可以匹配空串时，如何打断 ε 环？不同的打断方式会给出不同的**整体匹配**：

```text
模式 ^b.(?:(?:[ab])*?)*，文本 'baaabba'
  Perl / Python（空迭代保留并退出循环）           → (0, 2)
  Pike VM / BitState（同一位置每个 pc 只展开一次） → (0, 3)
  “空迭代即失败”的回溯                          → (0, 7)
```

这不是边角问题。第 15 章的差分测试统计了 `regexlab` 的 Pike VM 与 Python `re` 的差异：在所有随机用例中，整体区间不同的情况全部来自**循环体可空**的模式，捕获组不同的情况也同样如此。除此之外，二者没有任何差异。

工业引擎的选择：

- **Perl、PCRE、Python、Java、JavaScript**：都采用“空迭代后退出循环”的规则，细节上仍有差别，例如空迭代中设置的捕获是否保留；
- **RE2、Go、Rust**：采用 Pike VM 式的“同一位置每个状态只展开一次”的语义，因此在这类模式上会与 Perl 系引擎给出不同的结果；
- 想让线性引擎完全复现 Perl 的空迭代语义，需要把“这次迭代是否前进”编进线程状态，破坏了按 pc 去重的前提（第 3.2、5.4 节）。目前没有主流线性引擎这样做。

### 13.5 其他常见的语义差异

| 现象 | 例子 | 各家行为 |
|---|---|---|
| 未参与匹配的组被反向引用 | `(a)?b\1` 匹配 `"b"` | Python、PCRE、Java：失败；JavaScript：`\1` 匹配空串，成功 |
| 量词内的捕获是否在每轮迭代时重置 | `(?:(a)\|b)*` 匹配 `"ab"` | Perl、Python、PCRE：组 1 保留上一轮的 `"a"`；JavaScript：每轮迭代开始时清空，组 1 为 `undefined` |
| `$` 与末尾换行 | `a$` 匹配 `"a\n"` | Python、Perl、PCRE：成功（`$` 也匹配末尾换行之前）；Rust、Go、RE2：失败 |
| `\d`、`\w` 的范围 | `\d` 匹配 `"٣"`（阿拉伯-印度数字 3） | Python（str）、Rust、.NET：成功；JavaScript、RE2（默认）、Go：失败 |
| 迭代中的空匹配 | `a*` 在 `"baa"` 上找所有匹配 | Python 3.7+：`['', 'aa', '']`，允许空匹配紧贴前一个非空匹配；Rust、`regexlab`：`(0,0), (1,3)`，跳过紧贴的空匹配 |
| `.` 是否匹配 `\r` | `.` 匹配 `"\r"` | 大多数引擎：成功；某些 CRLF 模式下的引擎：失败 |
| 后行断言 | `(?<=a+)b` | Python：编译错误（必须定长）；.NET、JavaScript：成功 |

**迭代的复杂度。** leftmost-first 语义下，单次 `search` 是线性的，但 `finditer` 在最坏情况下不是。考虑模式 `a[^z]*z|a` 和一段含有 $k$ 个 `a`、但没有 `z` 的文本：每次搜索，正向扫描都要为了 `[^z]*z` 这个高优先级分支一路读到文本末尾，最后才退回到 `a` 这个结果，总代价为 $O(nk)$。这是语义本身的要求：在看到文本末尾之前，无法排除高优先级分支。Rust `regex` 的文档也明确说明了迭代在最坏情况下可能是二次的。

### 13.6 词法语义与搜索语义的区别

第 8 章的最长匹配和 leftmost-first 经常被混淆：

| | leftmost-first | 最长匹配 + 规则优先级 |
|---|---|---|
| 起点 | 在文本中搜索最左起点 | 固定在当前位置 |
| 选择 | 按优先级，第一个成功即停止 | 先比长度，同长时比规则顺序 |
| `if\|[a-z]+` 在 `iffy` 上 | `if` | `iffy`（标识符） |
| 需要的结构 | 有序线程 / 有序状态 | 无序状态集合 + 每个状态记录最小规则号 |
| 回退 | 不需要 | 需要回到最后一次接受的位置 |

如果用通用正则库实现词法器（比如把所有规则连成一个大的 `|`），得到的是 leftmost-first，而不是最长匹配。`if|[a-z]+` 会把 `iffy` 切成 `if` 加 `fy`。要么把规则按“最长的放前面”排序（这通常做不到），要么像 ANTLR 和 flex 那样单独实现最长匹配。

### 13.7 小结

1. **选定一种语义，并精确地写下来。** leftmost-first 是事实上的主流；需要兼容 POSIX 工具时才选 leftmost-longest；词法器用最长匹配。
2. **同一种语义下，各引擎仍有细节差异。** 空循环、未参与组的反向引用、`$` 与换行、Unicode 字符类、空匹配迭代，这几处最常见。
3. **线性引擎与回溯引擎在空循环上不可能完全一致**，除非付出破坏去重前提的代价。写文档时要说清楚。
4. **用差分测试把差异找出来，并逐一归类。** 每一类差异要么修复，要么写进文档（第 15 章）。

### 13.8 练习

1. 用 `regexlab` 的 Pike VM 实现 POSIX 的整体匹配：不截断，保留每个位置最后一个到达 `match` 的线程。验证 `a|ab` 在 `ab` 上得到 `ab`，并说明为什么子匹配仍然不符合 POSIX。
2. 在 `Backtracker` 中加入 JavaScript 的“每轮迭代清空捕获”语义，复现 13.5 节表中的第二行。
3. 写一个 `finditer_python`，复现 Python 3.7 起的空匹配规则，并与 `re.finditer` 在随机模式上对拍。
4. 对 `a[^z]*z|a` 在 $k$ 个 `a` 的文本上测量 `Regex.finditer` 的耗时，验证 $O(nk)$。把模式改写成 `a(?:[^z]*z)?`，它的语义变了吗？复杂度呢？

---
## 第 14 章　安全：ReDoS 及其防御

**ReDoS**（Regular expression Denial of Service）是指攻击者通过精心构造的输入，让正则匹配消耗极多的 CPU 时间。它有两种威胁模型：

1. **模式可信，文本不可信**：最常见。服务端的校验规则、WAF 规则、日志解析规则是开发者写的，但待匹配的文本来自用户；
2. **模式和文本都不可信**：搜索框支持正则、用户可以配置过滤规则、多租户的日志平台等。此时连**编译**模式本身都可能成为攻击面。

### 14.1 灾难性回溯的几种形态

第 3 章已经给出了指数爆炸的配方：**歧义加失败**。下表把常见形态汇总在一起：

| 模式 | 歧义来源 | 回溯最坏复杂度 |
|---|---|---|
| `(a+)+`、`(a*)*`、`(a\|a)*` | 嵌套量词，或可重叠的选择分支 | 指数 |
| `(a\|aa)*`、`(\w+\s?)*` | 分支之间可以相互拼出 | 指数 |
| `\s*\w*\s*x` 在长空白串上 | 相邻量词的字符集重叠 | 多项式 |
| `.*a.*a.*a`、`.*(?:.*=.*)` | 多个 `.*` 对同一段输入“抢地盘” | $O(n^k)$ |
| `a+b` 的非锚定搜索 | 隐式的 `.*?` 前缀与 `a+` 重叠 | $O(n^2)$ |

不要小看“只是多项式”的那几行：

- **2016 年 Stack Overflow 宕机。** 一个去除首尾空白的模式 `^[\s\u200c]+|[\s\u200c]+$`，遇到一条含约两万个连续空白字符的帖子。在每个起点上，`[\s\u200c]+` 都贪婪地吞下后续所有空白，再因为 `$` 失败而逐个退回，总代价 $O(n^2)$，约两亿步，足以拖垮首页；
- **2019 年 7 月 Cloudflare 全球故障。** WAF 规则中含有 `.*(?:.*=.*)` 这样的子模式，部署后全球 CPU 打满，服务中断约半小时。事后报告明确把原因归结为回溯引擎上的灾难性回溯，并决定迁移到线性时间引擎。

### 14.2 从直觉到判据：EDA 与 IDA

“歧义”可以在自动机上精确定义。把模式编译成**无 ε 的 NFA**，回溯引擎在最坏情况下要遍历从起点出发、读入同一个串的**所有路径**。路径条数随输入长度的增长方式，决定了回溯的复杂度：

- **EDA（指数歧义）**：存在状态 $q$，从 $q$ 出发有**两条不同的路径**读同一个串 $w$ 回到 $q$。把 $w$ 重复 $k$ 次，就有 $2^k$ 条不同的路径，回溯最坏是指数级；
- **IDA（多项式歧义）**：存在两个不同的状态 $p \ne q$，以及同一个串 $w$，使得 $p \xrightarrow{w} p$、$p \xrightarrow{w} q$、$q \xrightarrow{w} q$。读入 $w^k$ 时，“在哪一轮从 $p$ 跳到 $q$”有 $k$ 种选择；$d$ 个这样的状态链成一串，就有 $O(k^{d-1})$ 条路径。

Weideman、van der Merwe、Berglund 与 Watson（2016）给出了在 NFA 上判定 EDA 与 IDA 的方法，并据此构造攻击串。判定的核心是**乘积自动机**：

- **EDA**：在 $A\times A$ 中，状态对 $(u, v)$ 读 $c$ 转移到 $(x, y)$，当且仅当 $u\xrightarrow{c}x$ 且 $v\xrightarrow{c}y$。如果某个强连通分量同时包含对角点 $(q, q)$ 和非对角点 $(r, s)$（$r \ne s$），就存在两条读同一个串、从 $q$ 回到 $q$ 的不同路径；
- **IDA**：在 $A\times A\times A$ 中，判断从 $(p, p, q)$ 能否到达 $(p, q, q)$。

`regexlab/redos.py` 实现了这个判定。它有一个关键细节：**分析的必须是回溯引擎实际遍历的结构。** 如果用第 7 章的 Glushkov 构造，`(a*)*` 会被“消化”成和 `a*` 一样的自动机，歧义消失了；但回溯引擎在 `(a*)*` 上确实会穷举“把 n 个 a 切成若干段”的所有方式。所以 `redos.py` 从 Thompson 程序做 ε 消除，并且**保留 ε 路径的条数**：同一对状态之间如果有两条不同的 ε 路径，就记为重数为 2 的平行边。平行边本身就构成两条不同的路径。

```python
def eps_targets(self, prog, pc):
    """枚举从 pc 出发的 ε 路径，统计到达每个消耗型指令的路径条数。
    每条指令在一条路径上最多经过两次：允许“上一轮迭代刚结束、新一轮迭代开始”。"""
    count = {}
    def walk(pc, on_path):
        op = prog[pc]
        if op[0] in ('char', 'any', 'class'):
            q = self.ids[pc]
            count[q] = count.get(q, 0) + 1
            return
        if op[0] == 'match' or on_path.count(pc) >= 2:
            return
        on_path = on_path + (pc,)
        ...                                   # 沿 jmp / split / save / assert 继续
    walk(pc, ())
    return count
```

此外，回溯引擎的**非锚定搜索**会在每个起点重试一次，相当于在模式前加了 `.*`。分析时要把它加上，除非模式以 `^` 开头。

### 14.3 实测：判据与回溯步数

下表同时给出静态分析的结论和第 3 章 `Backtracker` 在失败输入上的实测步数（预算 500 万步）：

```text
  模式                     搜索                 锚定                 步数 n=8      n=16
  (a+)+$                   exponential          exponential          2,560        655,360
  (a|a)*$                  exponential          exponential          5,090      1,310,666
  (a|aa)*$                 exponential          exponential          1,485         72,344
  (?:a*)*b                 exponential          exponential          2,564        655,372
  (\w+\s?)*$               exponential          exponential          4,086      1,048,558
  a*a*$                    polynomial(n^3)      polynomial(n^2)        444          2,284
  \s*\w*\s*x               polynomial(n^3)      polynomial(n^2)        536          2,592
  .*a.*a.*a                polynomial(n^4)      polynomial(n^3)        208            512
  .*(?:.*=.*)              polynomial(n^4)      polynomial(n^3)        483          2,431
  a+b                      polynomial(n^2)      linear                 102            326
  ^a+b                     linear               linear                  38             70
  [a-z]+@[a-z]+\.com       polynomial(n^2)      linear                 102            326
  ^[a-z]+@[a-z]+\.com$     linear               linear                  38             70
  abc                      linear               linear                  28             52
```

几点观察：

- **指数类**：n 从 8 翻倍到 16，步数增长约 50 到 260 倍，大多数恰好约为 $2^8 = 256$ 倍。`(a|aa)*$` 增长较慢，因为它的路径数按斐波那契数增长，底数是黄金分割比 1.618；
- **多项式类**：n 翻倍时步数增长约 4 到 5 倍，n 还小的时候，低阶项的影响仍然明显；
- **锚定与否**：`a+b`、`[a-z]+@[a-z]+\.com` 只在非锚定搜索时是二次的，加上 `^` 就变成线性。这是一个非常实用的结论：**给校验类的正则加上 `^...$`，不只是语义更准确，也能消除一整类 ReDoS**；
- **判据只是必要条件。** `.*a.*a.*a` 被判为 $O(n^4)$，实测增长却接近线性。原因是：能让三个 `.*` 抢地盘的“泵”是字母 `a`，而只要文本里有三个 `a`，模式就匹配成功了，不会触发回溯；要让匹配失败，文本里最多只能有两个 `a`，泵也就失效了。真正的攻击串必须同时满足“能泵”和“最终失败”。完整的工具会在判定歧义之后，再验证是否存在导致失败的后缀，并构造出具体的攻击串。`.*(?:.*=.*)` 则不同：泵是任意非 `=` 字符，失败条件是“没有 `=`”，两者可以同时满足，所以它是真实可利用的，这正是 Cloudflare 事故的模式。

### 14.4 防御：纵深体系

| 层次 | 手段 | 说明 |
|---|---|---|
| 选引擎 | **线性时间引擎** | Go、Rust、RE2 默认就是线性的；.NET 用 `RegexOptions.NonBacktracking`；V8 可以在回溯过多时切换到实验性线性引擎。这是最根本的方案 |
| 选引擎 | **混合策略** | 先检查模式是否用到只有回溯才能支持的特性，没有就交给线性引擎，有才交给带预算的回溯器。`regexlab.meta.Regex` 就是这样做的 |
| 写模式 | **加锚点** | 校验类正则一律写 `^...$`（或用 `fullmatch`），消除非锚定搜索带来的二次复杂度 |
| 写模式 | **消除歧义** | `(a+)+` 改成 `a+`；`(\w+\s?)*` 改成 `\w+(?:\s\w+)*`；让相邻量词的字符集不重叠 |
| 写模式 | **原子组 / 占有量词** | `(?>a+)+$`、`a++$` 把指数降到线性（第 3.5 节）；前提是作者理解语义变化 |
| 运行时 | **步数或时间预算** | PCRE 的 `match_limit`、.NET 的 `matchTimeout`、Python 第三方 `regex` 模块的 `timeout`；只能把卡死变成报错，是最后一道防线 |
| 运行时 | **限制输入长度** | 对校验类正则，先检查长度上限，再匹配。指数爆炸在 n = 30 时就足够致命，长度限制只能缓解多项式类 |
| 开发流程 | **静态检测** | 在 CI 中扫描代码库里的正则字面量，用 EDA/IDA 判据报警。现成工具有 Weideman 等人的 RegexStaticAnalysis、rxxr2、npm 生态的 `safe-regex` 等 |
| 开发流程 | **模糊测试** | 对关键正则做基于覆盖率的模糊测试，以耗时作为反馈信号 |

### 14.5 不可信的模式

当模式本身来自用户时，攻击面扩大到**编译阶段**：

- **解析**：深度嵌套导致栈溢出。对策是嵌套上限或显式栈（第 2.4 节）；
- **编译**：`(?:(?:a{100}){100}){100}` 展开成一百万条指令。对策是在编译前估算规模（第 4.4 节），RE2 和 Rust 都有程序大小上限；
- **DFA 构造**：`(a|b)*a(a|b){20}` 的完全 DFA 有两百万个状态。对策是惰性 DFA 加缓存上限加放弃回退（第 6.5 节），以及对完全 DFA 设状态上限；
- **Unicode 展开**：`\w{50}` 在 Unicode 模式下编译出的程序可能非常大。Rust 的 `size_limit` 会拒绝它；
- **回溯引擎**：即便模式是“安全”的，用户也可以直接提交一个 `(a+)+$`。对不可信模式只能使用线性引擎，或者用严格的步数预算。

Google Code Search 正是因为要让用户提交任意正则，才催生了 RE2。

### 14.6 词法器里的 ReDoS

第 8.4 节说明了：最长匹配的驱动循环在 `a` 与 `a*b` 这类规则上是二次的。实测 n = 8000 时读入了 3200 万个字符。对处理不可信输入的词法器（例如解析用户上传的配置文件、模板、代码片段），这同样是拒绝服务的风险。对策是 Reps 的线性化方法，或者为每个可能长距离回退的结构（未闭合的字符串、注释）添加兜底规则。

### 14.7 练习

1. 扩展 `redos.py`：在判定 EDA 之后，构造攻击串“前缀 + 泵 × k + 失败后缀”。前缀用 BFS 求从初始状态到 $q$ 的最短串，泵取乘积自动机中经过非对角点、回到 $(q, q)$ 的环，失败后缀要求从 $q$ 出发的所有路径都无法接受。用 `Backtracker` 验证生成的攻击串确实触发了指数增长。
2. `redos.py` 把 `^`、`$` 当作 ε 处理，这是一种过近似。举一个因此产生误报的例子，并说明如何改进。
3. 把 `(\w+\s?)*$` 改写成无歧义的等价形式，用 `redos.py` 和 `Backtracker` 分别验证。
4. 为 `Backtracker` 加入时间预算（而不仅是步数预算），并讨论两者各自的优缺点：可预测性、开销、跨机器的一致性。
5. 收集你所在项目代码库中的正则字面量，用 `redos.py` 扫描一遍。报告了哪些？其中哪些是真实可利用的？

---
## 第 15 章　测试与验证

正则引擎是“组合”出来的：解析器、编译器、四五种执行引擎、反向程序、预过滤、元引擎的选择逻辑。每个部件单独看都可能是对的，组合起来却在某个角落出错。本章介绍 `regexlab` 采用的测试方法，并用**变异测试**检验这套测试本身是否有效。

### 15.1 原则：慢而简单的实现是最有价值的测试工具

Pike VM 在生产环境中很少是最快的选择，但它直接对应 leftmost-first 语义的定义（第 13.2 节），代码短，没有缓存、没有启发式。每一个更快的引擎都靠和它对拍来证明自己。外部参照则选 Python `re`：它是一个独立实现的回溯引擎，语义同为 leftmost-first。

三条配套的原则：

1. **语义先于速度**：每一种优化都要附带一个论证，说明它为什么不改变结果（第 6.5、10.1、12.1 节）；
2. **启发式只影响速度**：缓存大小、清空与放弃的阈值、预过滤的开关、捕获引擎的选择阈值，这些参数随便调，结果都必须不变；
3. **把参数调到极端来测试**：测试时故意把惰性 DFA 的缓存设成 4 个状态，逼它不断清空、放弃。

### 15.2 差分模糊测试

`regexlab/fuzz.py` 随机生成**模式**和**文本**，让所有引擎互相对拍。

```python
ATOMS = ['a', 'b', '.', '[ab]', '[^a]', 'ab', '', '^', '$']

def rand_pattern(depth=3, anchors=True):
    if depth == 0 or random.random() < 0.3:
        return random.choice(ATOMS)
    kind = random.choice(['cat', 'cat', 'alt', 'star', 'plus', 'opt', 'lazy', 'group', 'rep', 'anchor'])
    sub = lambda: rand_pattern(depth - 1, anchors)
    if kind == 'alt':   return '(?:' + sub() + '|' + sub() + ')'
    if kind == 'lazy':  return '(?:' + sub() + ')' + random.choice(['*?', '+?', '??'])
    if kind == 'rep':   ...                  # {lo,hi}、{lo,}、{lo}
    ...
```

几个设计要点：

- **随机生成模式，而不只是随机生成文本**。组合错误往往藏在“某种模式结构”里，固定的几个模式覆盖不到；
- **小字母表、短文本**。字母表只有 `a`、`b`（以及 `.`、`[^a]` 等能匹配它们的原子），文本不超过 8 个字符。这样各种分支和循环才会频繁地“撞在一起”；
- **把锚点当作原子**。`^`、`$` 出现在选择和循环内部时，才能触发第 5.2 节那类“某个位置上闭包为空”的边界情况；
- **异常也是结果**。被测引擎抛出的异常记为一种错误的结果，而不是让测试中断。

每个用例检查的项目：

| 检查项 | 被测 | 参照 |
|---|---|---|
| 捕获组 | BitState | Pike VM |
| 区间 | 三段式搜索（缓存只有 4 个状态） | Pike VM |
| 区间、捕获组 | 元引擎 `Regex` | Pike VM |
| 从随机位置 `pos` 开始搜索 | `Regex.search(s, pos)` | `pike_search(prog, s, pos)` |
| 所有匹配 | `Regex.finditer` | `pike_finditer` |
| 是否匹配 | 完全 DFA | Pike VM |
| 整串匹配 | 反向程序 `fullmatch(rev, s[::-1])` | `fullmatch(prog, s)` |
| 整串匹配（不含锚点时） | followpos DFA、Glushkov 位掩码、导数 DFA | Pike VM |
| 性质 | 每个匹配的起点处都出现某个前缀字面量 | — |
| 最小化 | Moore 与 Hopcroft 的块数 | 互相 |
| 区间、捕获组（外部） | AST 回溯（Perl 空迭代规则） | Python `re` |
| 区间、捕获组（只统计） | Pike VM | Python `re` |

三个随机种子、各 700 轮的结果：

```text
  cases                                            113760
  note: pike captures != python captures           821
  note: span != python re (nullable loop body)     417
  patterns                                         1896
  skipped_patterns                                 204
```

- 1896 个模式、113,760 个用例上，**所有 `diff:` 项都是 0**：各引擎之间、AST 回溯与 Python `re` 之间没有任何差异；
- 204 个随机模式被解析器拒绝，主要是“零宽断言后面跟量词”（如 `^*`）；
- Pike VM 与 Python `re` 的差异只作统计，不算错误：整体区间不同的 417 例**全部**来自循环体可空的模式，捕获组的差异同样如此（第 13.4 节）。这是两种空循环语义的预期差异，测试代码会把“循环体不可空却出现差异”单独标为 `OTHER!`，它没有出现过。

测试失败时，断言信息给出的模式和文本通常又长又乱。手动删减几次，把它化简成最小的反例再调试，往往能节省大量时间。这个过程也可以自动化，称为**测试用例约简**：在语法树上把子表达式替换为它的一个分支或单个原子，在文本上删除字符，只要仍然失败就接受修改。

### 15.3 变异测试：测试本身可信吗

“所有检查都通过”只说明没有发现错误。测试能不能发现错误？`regexlab/mutation.py` 往引擎里**故意注入错误**，看差分测试能否发现：

| 注入的错误 | 不含随机 `pos` | 含随机 `pos` | 最小反例（含随机 `pos` 时） |
|---|---|---|---|
| `reverse_prog` 不交换 `^` 与 `$` | 发现 | 发现 | `(?:b\|[^a])(?:[^a])+?$` 在 `aabb` 上：反向扫描找不到起点，触发断言 |
| 惰性 DFA 找到匹配后仍注入新线程 | 发现 | 发现 | `((?:[^a])*?)(?:($)\|(?:)*)` 在 `aa` 上：得到 `(2, 2)`，应为 `(0, 0)` |
| `minimize_literals` 保留较长的字面量 | 发现 | 发现 | `(?:ab)+` 在 `babbab` 上：得到 `None`，应为 `(1, 3)` |
| `anchored_start` 把 `$` 当作起始锚点 | **未发现** | 发现 | `$` 从随机位置搜索 `bbbabbaa`：得到 `None`，应为 `(8, 8)` |
| `Prefilter.find` 的搜索上界写成 `best` | 发现 | 发现 | `(?:b)+ab` 在 `bbbbabba` 上：得到 `(3, 6)`，应为 `(0, 6)` |

最有启发性的是第四行。`anchored_start` 只在 `pos > 0` 时才起作用，而最初的测试只调用 `search(s)`，`pos` 总是 0。`finditer` 虽然会用 `pos > 0` 调用 `search`，但对于 `$` 这类模式，第一次搜索就已经找到了文本末尾的匹配，后续搜索根本不会发生。**测试覆盖不到的代码路径，对测试来说等于不存在。** 加入“从随机位置开始搜索”这一项检查后，错误立即暴露。

最后一行也值得一提。`str.find(sub, start, end)` 要求整个 `sub` 落在 `[start, end)` 内，所以“只找起点早于 `best` 的出现”时，上界应当是 `best + len(L) - 1`。写成 `best` 看上去很自然，却会漏掉跨过 `best` 的更早出现。这个错误只在多个字面量互相重叠时才会触发，手写用例很难想到，随机测试在几百个模式里就找到了它。

### 15.4 性质测试

差分测试之外，几条**性质**可以直接检验，失败时也更容易定位：

- **反向程序**：$\mathrm{fullmatch}(p, s) = \mathrm{fullmatch}(\mathrm{rev}(p), s^R)$；
- **前缀完备性**：每个匹配的起点处都出现 $P$ 中的某个字符串（第 12.1 节）；
- **缓存无关性**：惰性 DFA 的缓存大小取 4 和取 1000 时，结果完全相同；
- **最小化**：Moore 与 Hopcroft 的块数相同，且最小化后的 DFA 与原 DFA 判定结果相同；
- **线程数上界**：Pike VM 每一步的活跃线程数不超过程序长度；
- **BitState 步数上界**：不超过 $m(n+1)$（第 5.5 节的实测）。

### 15.5 外部测试集与持续模糊测试

成熟的正则库都积累了大量测试用例，值得借用：

| 来源 | 内容 |
|---|---|
| PCRE2 `testdata/` | 数千个 Perl 兼容的输入/输出用例，覆盖几乎所有特性 |
| RE2 `re2/testing/` | 搜索测试、与 PCRE 的穷举对拍（在小字母表上枚举所有短模式） |
| Rust `regex` `testdata/*.toml` | 结构化的 TOML 用例，标注了语义、锚定、Unicode 等属性 |
| AT&T POSIX 测试集（Glenn Fowler） | leftmost-longest 与子匹配语义，被 RE2、Rust、Go 用来测试 POSIX 模式 |
| OSS-Fuzz | RE2、PCRE2、Rust `regex` 都接入了持续的覆盖率引导模糊测试，主要发现崩溃、超时和内存问题 |

RE2 的**穷举测试**思路值得特别一提：在 `{a, b}` 字母表上枚举所有不超过一定长度的模式和文本，与 PCRE 逐一对拍。随机测试擅长发现“意料之外的组合”，穷举测试则保证“小规模内没有遗漏”。

### 15.6 形式化方法

正则语义适合机械化证明：

- 在 Coq、Isabelle、Lean 中都有经过证明的导数匹配器，证明“匹配器返回真当且仅当串属于语言”；
- Warblre（ITP 2024）在 Coq 中机械化了 ECMAScript 规范的正则语义，可以用来判定 JavaScript 引擎的行为是否符合规范；
- 线性引擎的正确性论证（例如第 10.1.1 节对三段式搜索的证明）也可以形式化，用来回答“这个优化是否改变结果”。

### 15.7 性能测试

- **预热**：惰性 DFA 和 ANTLR 这类带缓存的实现，前几次运行明显更慢。计时前先预热，或者分别报告冷启动与稳定状态的数据；
- **分开报告编译时间与匹配时间**：对一次性使用的模式，编译时间可能占大头；
- **覆盖“病态”输入**：除了典型输入，还要测试第 6.3 节的状态爆炸、第 14 章的 ReDoS 输入，确认放弃与回退机制按预期工作；
- **跨引擎基准**：Andrew Gallant 的 rebar 汇集了数十个引擎和数百个基准，方法论值得参考：每个基准都标明“测的是什么”，以及结果是否被验证为正确。

### 15.8 练习

1. 实现 15.2 节提到的自动约简 `shrink(p, s, fails)`，在语法树上操作，并用 15.3 节的变异体验证：约简后的反例应当短于 10 个字符。
2. 给 `mutation.py` 再加三个变异体：Pike VM 的 `split` 压栈顺序颠倒；Hopcroft 在块不在工作集时把**较大**的一半放进去；`LazyDFA.closure` 在 `longest=True` 时也截断。哪些能被发现？对于没被发现的，它真的是错误吗？
3. 实现 RE2 风格的穷举测试：在 `{a, b}` 上枚举所有不超过 4 个原子的模式，与 Python `re` 对拍，统计差异并归类。
4. 把 `fuzz.py` 的字母表扩展为 `'aé中'`，配合第 11 章练习 1 的字节级 DFA 做差分测试。

---
## 第 16 章　横向对比与设计建议

### 16.1 算法维度的对比

| 算法 | 时间 | 额外空间 | 捕获组 | 优先级语义 | 反向引用 / 环视 | 典型用途 |
|---|---|---|---|---|---|---|
| 回溯（第 3 章） | 最坏指数 | 栈，随文本增长 | ✅ | ✅ | ✅ | 功能优先的通用库 |
| BitState（第 5 章） | $O(nm)$ | $O(nm)$ 位 | ✅ | ✅ | ❌ | 短区间内求捕获 |
| Pike VM（第 5 章） | $O(nm)$ | $O(mk)$ | ✅ | ✅ | ❌ | 保底引擎、测试参照 |
| OnePass DFA（第 10 章） | $O(n)$ | $O(m)$ 状态 | ✅ | ✅ | ❌ | 满足 one-pass 条件时的锚定捕获 |
| 完全 DFA（第 6 章） | $O(n)$ | 最坏 $O(2^m\lvert\Sigma\rvert)$ | ❌ | 需有序状态 | ❌ | 离线生成：词法器、预编译规则 |
| 惰性 DFA（第 6 章） | 典型 $O(n)$，最坏 $O(nm)$ | 有上限的缓存 | ❌ | ✅（有序状态） | ❌ | 通用搜索的快速路径 |
| TDFA（第 8 章） | $O(n)$ | 状态与寄存器 | ✅ | ✅ 或 POSIX | ❌ | re2c 的子匹配 |
| 导数 DFA（第 7 章） | $O(n)$ | 惰性构造 | 需扩展 | 需保序变体 | 交、补 ✅ | .NET NonBacktracking、规则推理 |
| 位并行（第 7、12 章） | $O(n\lceil m/w\rceil)$ | $O(m)$ 位 | ❌ | ❌ | ❌ | 短模式、近似匹配、Hyperscan |
| 字面量预过滤（第 12 章） | 亚线性到线性 | 很小 | — | — | — | 所有引擎的加速层 |
| ATN + 运行时 DFA（第 9 章） | 典型线性 | 增长的缓存 | — | 最长匹配 / 预测 | 谓词 ✅ | ANTLR 词法与语法 |

### 16.2 实现维度的对比

| 实现 | 执行模型 | 单位 | 线性保证 | 反向引用 / 环视 | 超时 / 预算 | 突出之处 |
|---|---|---|---|---|---|---|
| RE2 | 惰性 DFA + OnePass + BitState + Pike VM | 字节 | ✅ | ❌ | 内存预算 | 线性时间与有界内存的标杆 |
| Go `regexp` | OnePass + BitState + Pike VM | 码点 | ✅ | ❌ | — | 简单可靠；没有 DFA，速度较慢 |
| Rust `regex` | 元引擎：惰性/完全 DFA、OnePass、BitState、Pike VM | 字节 | ✅ | ❌ | 大小上限 | 字面量优化最激进；模块化的 `regex-automata` |
| PCRE2 | 回溯 + JIT；另有 `dfa_match` | 代码单元 | ❌ | ✅ | `match_limit` 等 | 功能最全；JIT 很快 |
| Java | 回溯（对象树） | UTF-16 | ❌ | ✅ | 无内置超时 | 类内交集；栈溢出风险 |
| .NET | 回溯（解释 / IL / 源生成）+ NonBacktracking | UTF-16 | 仅 NonBacktracking | ✅（回溯模式） | `matchTimeout` | 平衡组；四种执行方式 |
| V8 | 回溯（字节码 → 本机代码）+ 实验线性引擎 | UTF-16 / 码点 | 仅实验引擎 | ✅ | — | 分层编译 |
| Python `re` | 回溯（C 字节码解释器） | 码点 | ❌ | ✅ | 无（第三方 `regex` 有） | 内置、语义稳定 |
| Hyperscan | 字面量 + 多种自动机，流式 | 字节 | ✅ | ❌ | — | 万级规则、SIMD、流式 |
| GNU grep | 惰性 DFA + kwset，必要时退回 glibc | 字节 / 多字节 | 无反向引用时 ✅ | 仅反向引用 | — | 按行处理，字面量过滤极快 |
| flex / re2c | 离线完全 DFA（表 / 代码） | 字节 | 线性（不计回退） | ❌ | — | 词法器；re2c 支持 TDFA 子匹配 |
| ANTLR 4 | ATN 模拟 + 运行时 DFA 缓存 | 字符 / 记号 | 典型线性 | 谓词 | — | 词法与语法统一的自适应预测 |

### 16.3 选型：作为使用者

1. **处理不可信的输入**，优先选线性引擎：Go、Rust、RE2；.NET 用 `NonBacktracking`；
2. **需要反向引用或环视**，只能用回溯引擎，但一定要设置预算或超时，并在 CI 中用静态分析扫描模式（第 14 章）；
3. **校验类正则**一律加 `^...$` 或用 `fullmatch`，这既是语义正确性问题，也消除了一整类二次复杂度；
4. **成千上万条规则同时匹配**，用 Hyperscan/Vectorscan 或 RE2 的 `Set`，不要循环调用单个正则；
5. **热循环中**提前编译模式并复用，不要依赖库的隐式缓存；
6. **跨语言迁移正则**时，对照第 13.5 节的差异表逐项检查：`$` 与换行、`\d` 的范围、未参与组的反向引用、空匹配迭代。

### 16.4 设计：作为实现者

如果要从头实现一个正则库，建议的顺序是：

1. **先写 Pike VM。** 它是语义的“可执行定义”，也是之后一切优化的测试参照（第 15 章）；
2. **从一开始就设资源上限**：嵌套深度、计数重复、程序大小、DFA 缓存。不可信的模式会在编译阶段就攻击你（第 2、4、14 章）；
3. **决定运行单位**：要做 DFA，就按字节运行，把 UTF-8 编进自动机（第 11 章）；
4. **加惰性 DFA 与反向扫描**，得到典型线性、常数很小的快速路径（第 6、10 章）；
5. **加 BitState 和 OnePass** 处理捕获组（第 5、10 章）；
6. **加字面量提取与预过滤**。对真实工作负载，它往往比自动机本身的优化更重要（第 12 章）；
7. **写下语义规范**：leftmost-first 还是 leftmost-longest，空循环、`$`、Unicode 如何处理（第 13 章）；
8. **差分测试加变异测试**，并持续运行（第 15 章）。

几条贯穿全书的原则：

- **特性集合决定算法上限，算法决定复杂度保证。** 在设计 API 时就决定支持哪些特性，后面的选择都由此而来；
- **语义先于速度。** 每一种优化都附带一个“为什么不改变结果”的论证；
- **启发式只影响速度。** 所有阈值都可以随意调整，结果必须不变；
- **把一个难问题拆成几个容易的问题。** 正向求终点需要优先级，反向求起点只需最长匹配，捕获组只在小区间里求。每一步交给最适合它的引擎。

### 16.5 设计：作为编译器 / DSL 作者

| 场景 | 建议 |
|---|---|
| 新 DSL、原型、配置语言 | 用生成器（flex、re2c、JFlex、ANTLR），半小时得到正确的词法器 |
| 词法依赖语法上下文（`/` 的歧义、模板字符串、typedef） | 手写，或使用支持模式切换与重新扫描的工具 |
| 需要 IDE 支持（增量、容错、无损记号流） | 手写，参考 `rustc_lexer` 与 Roslyn 的设计 |
| 对速度要求极高、嵌入已有缓冲区 | re2c |
| 词法与语法一起快速迭代 | ANTLR 4；注意 SLL 冲突带来的性能问题，用两阶段解析 |
| 不可信输入 | 检查是否存在长距离回退（flex `-b`），必要时加兜底规则或用 Reps 的线性化 |

### 16.6 未来方向

- **线性时间的环视与有界重复**：计数集合自动机、带环视的线性匹配（第 11 章）已经从研究走向实现；
- **基于导数的工业引擎**：.NET NonBacktracking 证明了导数方法在工业规模上可行，并且天然支持交集、补集；
- **SIMD 与位并行的进一步融合**：Hyperscan 的 Teddy、Sheng，Rust 的 Teddy 移植，把“每次处理一个字节”推进到“每次处理一个向量”；
- **形式化验证**：机械化的语义（如 Warblre）让“引擎是否符合规范”成为可以判定的问题。

---

## 附录 A　参考文献

**经典论文与著作**

1. S. C. Kleene. *Representation of Events in Nerve Nets and Finite Automata*. Automata Studies, 1956.
2. M. O. Rabin, D. Scott. *Finite Automata and Their Decision Problems*. IBM Journal of Research and Development, 1959.
3. V. M. Glushkov. *The Abstract Theory of Automata*. Russian Mathematical Surveys, 1961.
4. J. A. Brzozowski. *Derivatives of Regular Expressions*. Journal of the ACM, 1964.
5. K. Thompson. *Programming Techniques: Regular Expression Search Algorithm*. Communications of the ACM, 1968.
6. J. Hopcroft. *An n log n Algorithm for Minimizing States in a Finite Automaton*. 1971.
7. M. E. Lesk, E. Schmidt. *Lex — A Lexical Analyzer Generator*. Bell Labs, 1975.
8. A. V. Aho. *Algorithms for Finding Patterns in Strings*. Handbook of Theoretical Computer Science, 1990.
9. R. Baeza-Yates, G. Gonnet. *A New Approach to Text Searching*. Communications of the ACM, 1992.
10. S. Wu, U. Manber. *Fast Text Searching Allowing Errors*. Communications of the ACM, 1992.
11. P. Bumbulis, D. D. Cowan. *RE2C: A More Versatile Scanner Generator*. ACM LOPLAS, 1993.
12. V. Antimirov. *Partial Derivatives of Regular Expressions and Finite Automaton Constructions*. Theoretical Computer Science, 1996.
13. T. Reps. *“Maximal-Munch” Tokenization in Linear Time*. ACM TOPLAS, 1998.
14. A. Brüggemann-Klein, D. Wood. *One-Unambiguous Regular Languages*. Information and Computation, 1998.
15. V. Laurikari. *NFAs with Tagged Transitions, Their Conversion to Deterministic Automata and Application to Regular Expressions*. SPIRE, 2000.
16. G. Navarro, M. Raffinot. *Flexible Pattern Matching in Strings*. Cambridge University Press, 2002.
17. A. V. Aho, M. S. Lam, R. Sethi, J. D. Ullman. *Compilers: Principles, Techniques, and Tools*（第 2 版，第 3 章）. 2006.
18. J. Friedl. *Mastering Regular Expressions*（第 3 版）. O'Reilly, 2006.
19. S. Owens, J. Reppy, A. Turon. *Regular-expression Derivatives Re-examined*. Journal of Functional Programming, 2009.
20. S. Okui, T. Suzuki. *Disambiguation in Regular Expression Matching via Position Automata with Augmented Transitions*. CIAA, 2010.
21. T. Parr, K. Fisher. *LL(\*): The Foundation of the ANTLR Parser Generator*. PLDI, 2011.
22. T. Parr, S. Harwell, K. Fisher. *Adaptive LL(\*) Parsing: The Power of Dynamic Analysis*. OOPSLA, 2014.
23. N. Weideman, B. van der Merwe, M. Berglund, B. Watson. *Analyzing Matching Time Behavior of Backtracking Regular Expression Matchers by Using Ambiguity of NFA*. CIAA, 2016.
24. U. Trofimovich. *Tagged Deterministic Finite Automata with Lookahead*. arXiv, 2017.
25. L. Turoňová, L. Holík, O. Lengál, O. Saarikivi, M. Veanes, T. Vojnar. *Regex Matching with Counting-Set Automata*. OOPSLA, 2020.
26. D. Moseley, M. Nishio, J. Perez Rodriguez, O. Saarikivi, S. Toub, M. Veanes, T. Wan, E. Xu. *Derivative Based Nonbacktracking Real-World Regex Matching with Backtracking Semantics*. PLDI, 2023.
27. A. Barrière, C. Pit-Claudel. *Linear Matching of JavaScript Regular Expressions*. PLDI, 2024.

**文章与文档**

28. R. Cox. *Regular Expression Matching Can Be Simple And Fast*（2007）；*Regular Expression Matching: the Virtual Machine Approach*（2009）；*Regular Expression Matching in the Wild*（2010）。
29. A. Gallant. *Regex engine internals as a library*（2023），以及 `regex-automata`、`aho-corasick`、`memchr`、rebar 的文档。
30. RE2、Go `regexp`、PCRE2、.NET `System.Text.RegularExpressions`、V8 Irregexp、CPython `sre`、Hyperscan、GNU grep、flex、re2c、ANTLR 4 的源码与官方文档。
31. Stack Exchange. *Outage Postmortem — July 20, 2016*.
32. Cloudflare. *Details of the Cloudflare outage on July 2, 2019*.
33. V8 团队博客：*Improving V8 regular expressions*（2019）；*An additional non-backtracking RegExp engine*（2021）。

---

## 附录 B　术语表

| 中文 | 英文 | 首次出现 |
|---|---|---|
| 回溯 | backtracking | 第 3 章 |
| 续延传递风格 | continuation-passing style | 3.1 |
| 灾难性回溯 | catastrophic backtracking | 3.4 |
| 原子组 / 占有量词 | atomic group / possessive quantifier | 3.5 |
| 反向引用 | backreference | 3.6 |
| 环视（先行 / 后行断言） | lookaround (lookahead / lookbehind) | 3.7 |
| Thompson 构造 | Thompson's construction | 第 4 章 |
| ε 闭包 | ε-closure | 5.1 |
| 截断（低优先级线程） | cutoff | 5.1 |
| 有界回溯 | bounded backtracking / BitState | 5.5 |
| 子集构造 | subset (powerset) construction | 第 6 章 |
| 字符等价类 / 字节类 | equivalence classes / byte classes | 6.1 |
| 最小化 | minimization | 6.4 |
| 惰性 DFA / 混合 DFA | lazy DFA / hybrid DFA | 6.5 |
| 位置自动机 | position (Glushkov) automaton | 7.4 |
| 导数 / 偏导数 | derivative / partial derivative | 7.5 |
| 一义的表达式 | one-unambiguous expression | 7.4 |
| 最长匹配 | maximal munch | 8.1 |
| 起始条件 / 词法模式 | start condition / lexer mode | 8.5.2 |
| 尾部上下文 | trailing context | 8.5.2 |
| 梳状压缩 | comb vector compression | 8.5.3 |
| 带标签 DFA | tagged DFA (TDFA) | 8.6.3 |
| 增广转移网络 | augmented transition network (ATN) | 第 9 章 |
| 自适应 LL(\*) | adaptive LL(\*), ALL(\*) | 9.1 |
| 图结构栈 | graph-structured stack | 9.2 |
| 三段式搜索 | three-phase search | 10.1 |
| 元引擎 | meta engine | 10.2 |
| 一遍 DFA | one-pass DFA | 10.3 |
| 预过滤 | prefilter | 第 12 章 |
| 前缀完备性 | prefix completeness | 12.1 |
| 最左优先 / 最左最长 | leftmost-first / leftmost-longest | 第 13 章 |
| 指数歧义 / 多项式歧义 | EDA / IDA | 14.2 |
| 差分测试 / 变异测试 | differential testing / mutation testing | 第 15 章 |

---

## 附录 C　练习提示

**第 3 章**

- **3-4**：设 $f(n)$ 为 $n$ 个 `a` 被切成若干段 `a` 或 `aa` 的方式数，则 $f(n) = f(n-1) + f(n-2)$。回溯的步数与所有前缀的切分数之和成正比，所以按 $\varphi^n$ 增长，n 增加 8 时比值约为 $\varphi^8 \approx 47$。
- **3-5**：对变量 $x_i$ 用组 `(x?)` 表示真假；输入串为若干个 `x` 和分隔符；每个子句用 `(?:\1|\3|...)` 形式的选择检查“至少一个文字为真”，取反的文字用另一个组 `(x?)` 并约束两组拼起来恰好是 `x`。

**第 5 章**

- **5-3**：`add` 在位置 `at` 处展开闭包时，`text[at-1]` 与 `text[at]` 都已知。DFA 的转移只看下一个字符，“上一个字符”必须编进状态。

**第 6 章**

- **6-1**：字母表限制为 `{a, b}` 时没有死状态，最小 DFA 恰好是 $2^{k+1}$ 个状态。
- **6-4**：有序状态的状态数不少于无序状态，因为同一集合的不同排列会成为不同的状态。

**第 7 章**

- **7-1**：`(a|b)*abb` 上两者去掉死状态后都是 4 个状态，因为第 6 章的闭包只保留“重要状态”。要找出最小化前状态数不同的例子，可以直接写一个随机测试：生成随机模式，比较 `PosDFA(...).nstates` 与 `DFA(prog, anchored=True).nstates`，打印第一个不同的模式。
- **7-5**：`a(a|b)*` 是一义的；`(a|b)*a` 不是，因为读到 `a` 时无法确定它是循环里的 `a` 还是最后那个 `a`。直观上，这个语言要求“最后一个字符是 a”，而一义的表达式必须在读到每个字符时就确定它对应哪个位置，不能等到读完才决定。

**第 8 章**

- **8-1**：按“接受/不接受”分块时，接受 `KW_IF` 的状态和接受 `IDENT` 的状态可能被合并，合并后的状态只能记录一个规则号。
- **8-3**：leftmost-first 下，`(a*)a*b` 在 `aaab` 上组 1 为 `aaa`，所以 `r` 的部分是 `aaa`。单靠驱动循环做不到，因为 DFA 状态里没有“r 在哪里结束”的信息。

**第 10 章**

- **10-1**：模式以 `$` 结尾且开头没有 `^` 时，任何匹配都必须在文本末尾结束，终点已知为 $n$，只需反向扫描求最小的起点。注意这给出的是“在 $n$ 结束的最左匹配”，只有当 leftmost-first 的匹配一定在 $n$ 结束时才等价。Rust 用这个策略时附带了检查。
- **10-2**：在子集构造中，若某个状态集合中有两个线程在同一个等价类上都能前进，模式就不是 one-pass。`(a*)(a*)` 不是 one-pass：读到 `a` 时无法确定属于哪一组。

**第 12 章**

- **12-2**：`\d+px` 的 inner 为 `px`、suffix 为 `{px}`；`.*foo` 的 inner 为 `foo`；`(ab|cb)d` 的 inner 为 `bd`。
- **12-4**：不会死循环，因为 DFA 在跳跃之后至少消耗一个字符才会再次检查是否回到起始状态。`start()` 应在每次 `search`（或每次 `finditer`）开始时调用。忘记调用时，计数会跨越多次搜索累积，一旦在某段文本上被关闭，之后所有搜索都保持关闭。这只损失性能，不影响结果。

**第 13 章**

- **13-1**：不截断只能保证整体最长；子匹配仍由“同 pc 先到者胜出”决定，而 POSIX 要求按子表达式逐级比较。

**第 14 章**

- **14-2**：`(?:^a|a)*$` 被判为指数级：把 `^` 当作 ε 后，两个分支都是 `a`，与 `(a|a)*` 无异。但 `^a` 只能在位置 0 成立，第一次迭代之后只剩第二个分支，歧义并不存在。实测失败输入上 n = 8 与 n = 16 的步数分别是 291 和 887，远非指数。改进方法是在乘积自动机中携带“当前位置是否为文本开头”的标志，让 `^` 只在开头处放行。
- **14-3**：`(\w+\s?)*$` 可改写为 `(?:\w+(?:\s\w+)*\s?)?$`：单词之间的分界由空白唯一确定。`regexlab.direct.equivalent` 验证二者等价，`redos.py` 对改写后的模式在锚定时判为线性（非锚定搜索时仍有隐式 `.*` 前缀带来的二次项）。

**第 15 章**

- **15-2**：Pike VM 压栈顺序颠倒会改变优先级，与有序惰性 DFA 的结果不一致，能被发现。Hopcroft 放入较大的一半仍然正确，只是更慢，所以“未发现”恰恰是对的：它不是错误。

---

*（全文完）*
