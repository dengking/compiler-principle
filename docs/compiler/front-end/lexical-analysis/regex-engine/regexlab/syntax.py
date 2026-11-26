"""第 2 章：正则表达式前端 —— 递归下降解析器、字符类规范化、特性分析。

AST 节点统一使用元组：
    ('char', c)                    ('any',)                 ('class', ranges, negated)
    ('cat', [nodes])               ('alt', a, b)            ('empty',)
    ('star', n, greedy)            ('plus', n, greedy)      ('quest', n, greedy)
    ('repeat', n, lo, hi, greedy)  # hi 为 None 表示 {lo,}
    ('group', n, idx)              # 捕获组，idx 从 1 开始
    ('bol',) ('eol',) ('wordb',) ('nwordb',)                # 零宽断言 ^ $ \\b \\B
    ('backref', k)                 # \\k，只有回溯引擎支持
    ('look', n, ahead, negated)    # (?=) (?!) (?<=) (?<!)，只有回溯引擎支持
    ('atomic', n)                  # (?>...) 与占有量词 a*+，只有回溯引擎支持
"""
import re as _re
from bisect import bisect_right

MAX_NEST = 250           # 与 Rust regex-syntax 的默认 nest_limit 相同
MAX_REPEAT = 1000        # 与 RE2 的计数重复上限相同

DIGIT = [('0', '9')]
WORD = [('0', '9'), ('A', 'Z'), ('_', '_'), ('a', 'z')]
SPACE = [('\t', '\r'), (' ', ' ')]
ESC_CLASSES = {'d': DIGIT, 'w': WORD, 's': SPACE}
ESC_CHARS = {'n': '\n', 't': '\t', 'r': '\r', 'f': '\f', 'v': '\v', '0': '\0'}


class RegexError(Exception):
    """带位置信息的解析错误，打印时用 ^ 指出出错位置。"""

    def __init__(self, msg, pattern, pos):
        super().__init__(msg)
        self.msg, self.pattern, self.pos = msg, pattern, pos

    def __str__(self):
        return (f"regex parse error:\n    {self.pattern}\n    {' ' * self.pos}^\n"
                f"error: {self.msg}")


def normalize(ranges):
    """排序并合并重叠或相邻的区间，得到规范形式（不相交、有序）。"""
    out = []
    for lo, hi in sorted(ranges):
        if out and ord(lo) <= ord(out[-1][1]) + 1:
            if hi > out[-1][1]:
                out[-1] = (out[-1][0], hi)
        else:
            out.append((lo, hi))
    return out


def in_class(ch, ranges):
    """ranges 是 normalize() 之后的有序不相交区间，二分查找。"""
    i = bisect_right(ranges, (ch, '\U0010FFFF')) - 1
    return i >= 0 and ranges[i][0] <= ch <= ranges[i][1]


class Parser:
    _COUNTED = _re.compile(r'\{(\d+)(,(\d*))?\}')

    def __init__(self, pattern):
        self.p = pattern
        self.i = 0
        self.ngroups = 0
        self.depth = 0

    # ---------- 基础工具 ----------
    def err(self, msg, pos=None):
        raise RegexError(msg, self.p, self.i if pos is None else pos)

    def peek(self):
        return self.p[self.i] if self.i < len(self.p) else None

    def next(self):
        c = self.peek()
        if c is None:
            self.err("unexpected end of pattern")
        self.i += 1
        return c

    def eat(self, s):
        if self.p.startswith(s, self.i):
            self.i += len(s)
            return True
        return False

    def enter(self):
        self.depth += 1
        if self.depth > MAX_NEST:
            self.err(f"nesting limit {MAX_NEST} exceeded")

    # ---------- 文法规则 ----------
    def parse(self):
        node = self.alt()
        if self.i != len(self.p):
            self.err(f"unexpected {self.peek()!r}")
        return node

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
                if node[0] in ('bol', 'eol', 'wordb', 'nwordb', 'look'):
                    self.err("quantifier after zero-width assertion")
                self.i += 1
                kind = {'*': 'star', '+': 'plus', '?': 'quest'}[c]
                greedy = not self.eat('?')                 # a*? 非贪婪
                possessive = greedy and self.eat('+')      # a*+ 占有
                self.enter()
                node = (kind, node, greedy)
                if possessive:
                    node = ('atomic', node)
                continue
            m = self._COUNTED.match(self.p, self.i) if c == '{' else None
            if m:
                self.i = m.end()
                lo = int(m.group(1))
                if m.group(2) is None:
                    hi = lo                                # {m}
                elif m.group(3) == '':
                    hi = None                              # {m,}
                else:
                    hi = int(m.group(3))
                if hi is not None and hi < lo:
                    self.err("bad repeat range", m.start())
                if max(lo, hi or 0) > MAX_REPEAT:
                    self.err(f"repeat count exceeds {MAX_REPEAT}", m.start())
                greedy = not self.eat('?')
                self.enter()
                node = ('repeat', node, lo, hi, greedy)
                continue
            self.depth = saved      # 量词链结束，恢复嵌套深度
            return node             # 不是合法计数量词的 '{' 按字面处理（与 Perl 一致）

    def atom(self):
        start = self.i
        c = self.next()
        if c == '(':
            self.enter()
            if self.eat('?:'):
                node = self.alt()
            elif self.eat('?>'):
                node = ('atomic', self.alt())
            elif self.eat('?='):
                node = ('look', self.alt(), True, False)
            elif self.eat('?!'):
                node = ('look', self.alt(), True, True)
            elif self.eat('?<='):
                node = ('look', self.alt(), False, False)
            elif self.eat('?<!'):
                node = ('look', self.alt(), False, True)
            elif self.peek() == '?':
                self.err("unsupported group syntax")
            else:
                self.ngroups += 1
                idx = self.ngroups                 # 先分配编号：按左括号顺序编号
                node = ('group', self.alt(), idx)
            if not self.eat(')'):
                self.err("unclosed group", start)  # 错误指向“原因”而不是“发现处”
            self.depth -= 1
            return node
        if c == ')':
            self.err("unopened group", start)
        if c == '.':
            return ('any',)
        if c == '^':
            return ('bol',)
        if c == '$':
            return ('eol',)
        if c == '[':
            return self.cls(start)
        if c == '\\':
            return self.escape(in_class=False)
        if c in '*+?':
            self.err("nothing to repeat", start)
        return ('char', c)

    def escape(self, in_class):
        c = self.next()
        if c.lower() in ESC_CLASSES:
            return ('class', ESC_CLASSES[c.lower()], c.isupper())  # \D \W \S 取反
        if not in_class:
            if c == 'b':
                return ('wordb',)
            if c == 'B':
                return ('nwordb',)
            if c.isdigit() and c != '0':
                return ('backref', int(c))
        return ('char', ESC_CHARS.get(c, c))

    def cls(self, start):
        neg = self.eat('^')
        ranges, first = [], True
        while True:
            if self.peek() is None:
                self.err("unclosed character class", start)
            c = self.next()
            if c == ']' and not first:             # []] 中第一个 ] 是字面量
                break
            first = False
            if c == '\\':
                e = self.escape(in_class=True)
                if e[0] == 'class':
                    if e[2]:
                        self.err("negated escape inside [] not supported")
                    ranges += e[1]
                    continue
                c = e[1]
            # a-z 形式；'-' 出现在末尾时按字面处理
            if self.peek() == '-' and self.p[self.i + 1:self.i + 2] not in ('', ']'):
                self.i += 1
                hi = self.next()
                if hi == '\\':
                    hi = self.escape(in_class=True)[1]
                if hi < c:
                    self.err(f"bad range {c}-{hi}")
                ranges.append((c, hi))
            else:
                ranges.append((c, c))
        return ('class', normalize(ranges), neg)


def parse(pattern):
    """返回 (ast, 捕获组个数)。"""
    ps = Parser(pattern)
    return ps.parse(), ps.ngroups


# ---------------------------------------------------------------- 分析函数
def children(n):
    k = n[0]
    if k == 'cat':
        return list(n[1])
    if k == 'alt':
        return [n[1], n[2]]
    if k in ('star', 'plus', 'quest', 'repeat', 'group', 'look', 'atomic'):
        return [n[1]]
    return []


def features(n, out=None):
    """模式用到了哪些“非正则”特性。特性集合决定算法上限。"""
    out = set() if out is None else out
    k = n[0]
    if k in ('backref', 'look', 'atomic', 'wordb', 'nwordb'):
        out.add({'nwordb': 'wordb'}.get(k, k))
    for c in children(n):
        features(c, out)
    return out


def nullable(n):
    """n 能否匹配空串（断言视为可空）。"""
    k = n[0]
    if k in ('empty', 'bol', 'eol', 'wordb', 'nwordb', 'star', 'quest', 'look', 'backref'):
        return True
    if k in ('char', 'any', 'class'):
        return False
    if k in ('plus', 'group', 'atomic'):
        return nullable(n[1])
    if k == 'cat':
        return all(nullable(x) for x in n[1])
    if k == 'alt':
        return nullable(n[1]) or nullable(n[2])
    if k == 'repeat':
        return n[2] == 0 or nullable(n[1])
    raise ValueError(k)


def is_word(ch):
    return ch is not None and (ch.isalnum() or ch == '_')


def assert_ok(kind, text, i):
    """零宽断言在位置 i 是否成立（单行模式）。"""
    if kind == 'bol':
        return i == 0
    if kind == 'eol':
        return i == len(text)
    before = text[i - 1] if i > 0 else None
    after = text[i] if i < len(text) else None
    b = is_word(before) != is_word(after)
    return b if kind == 'wordb' else not b
