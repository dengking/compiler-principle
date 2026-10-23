"""第 8 章：词法分析器生成器 —— 多规则 DFA（最长匹配 + 规则优先级）、驱动循环、
Reps 线性化、flex 式梳状压缩、编译器风格的手写词法器。"""
from bisect import bisect_right

from .syntax import parse
from .direct import analyze, to_pos, Cat, Sym, End, CSet, class_reps


class LexError(Exception):
    pass


class LexerDFA:
    """每条规则 r_k 拼接各自的结束标记 #k；接受状态记录编号最小的规则。"""

    def __init__(self, patterns):
        syms, follow, start = [], {}, set()
        for k, p in enumerate(patterns):
            ast, _ = parse(p)
            _, f, _ = analyze(Cat(to_pos(ast), Sym(End(k))), syms, follow)
            start |= f
        self.starts, reps = class_reps([s for s in syms if isinstance(s, CSet)])
        start = frozenset(start)
        index, self.sets, self.trans, self.accept = {start: 0}, [start], [], []
        i = 0
        while i < len(self.sets):
            S = self.sets[i]
            i += 1
            ks = [syms[p].rule for p in S if isinstance(syms[p], End)]
            self.accept.append(min(ks) if ks else None)
            row = []
            for c in reps:
                T = frozenset(q for p in S if c in syms[p] for q in follow[p])
                if T not in index:
                    index[T] = len(self.sets)
                    self.sets.append(T)
                row.append(index[T])
            self.trans.append(row)
        self.dead = index.get(frozenset())
        self.nstates = len(self.sets)

    def cls(self, ch):
        return bisect_right(self.starts, ord(ch)) - 1

    def unreachable_rules(self, n):
        """被优先级更高的规则完全遮蔽、永远不会被选中的规则（flex: rule cannot be matched）。"""
        return sorted(set(range(n)) - {a for a in self.accept if a is not None})


def tokenize(dfa, text, skip=(), stats=None):
    """最长匹配驱动循环：走到不能再走，然后回退到最后一次接受的位置。"""
    if dfa.accept[0] is not None:
        raise ValueError('存在能匹配空串的规则，驱动循环会原地打转')
    pos, out, reads = 0, [], 0
    while pos < len(text):
        q, i = 0, pos
        last_rule = last_end = None
        while i < len(text):
            q = dfa.trans[q][dfa.cls(text[i])]
            reads += 1
            if q == dfa.dead:
                break
            i += 1
            if dfa.accept[q] is not None:
                last_rule, last_end = dfa.accept[q], i
        if last_rule is None:
            raise LexError(f'位置 {pos} 处无法识别：{text[pos]!r}')
        if last_rule not in skip:
            out.append((last_rule, text[pos:last_end]))
        pos = last_end
    if stats is not None:
        stats['reads'] = reads
    return out


def tokenize_linear(dfa, text, skip=(), stats=None):
    """Reps (1998)：记住“失败过的 (状态, 位置)”，保证 O(n·|Q|)。"""
    if dfa.accept[0] is not None:
        raise ValueError('存在能匹配空串的规则')
    failed = set()
    pos, out, reads = 0, [], 0
    while pos < len(text):
        q, i = 0, pos
        last_rule = last_end = None
        since = []                     # 自最后一次接受以来经过的 (q, i)
        while i < len(text) and (q, i) not in failed:
            since.append((q, i))
            q = dfa.trans[q][dfa.cls(text[i])]
            reads += 1
            if q == dfa.dead:
                break
            i += 1
            if dfa.accept[q] is not None:
                last_rule, last_end = dfa.accept[q], i
                since.clear()          # 接受之前经过的状态对后面能到达接受，不能标记
        failed.update(since)
        if last_rule is None:
            raise LexError(f'位置 {pos} 处无法识别：{text[pos]!r}')
        if last_rule not in skip:
            out.append((last_rule, text[pos:last_end]))
        pos = last_end
    if stats is not None:
        stats['reads'] = reads
    return out


# ------------------------------------------------------------------ flex 式表压缩
def comb_pack(rows, n_classes, dead=None):
    """rows[s] 是 {字符类: 目标状态}，只列出非 dead 的项。返回 (base, nxt, chk)。
    多个状态的行在 nxt 中交错存放，chk 记录每一项属于哪一行。"""
    nxt, chk = [], []
    base = [0] * len(rows)
    order = sorted(range(len(rows)), key=lambda s: -len(rows[s]))  # 先放密集的行
    for s in order:
        row = rows[s]
        b = 0
        while any(b + c < len(chk) and chk[b + c] is not None for c in row):
            b += 1                                # 第一个不冲突的偏移
        need = b + n_classes
        if len(chk) < need:
            nxt.extend([dead] * (need - len(nxt)))
            chk.extend([None] * (need - len(chk)))
        for c, t in row.items():
            nxt[b + c] = t
            chk[b + c] = s
        base[s] = b
    while chk and chk[-1] is None:                # 去掉尾部空位
        chk.pop()
        nxt.pop()
    return base, nxt, chk


def comb_lookup(base, nxt, chk, s, c, dead=None):
    i = base[s] + c
    return nxt[i] if i < len(chk) and chk[i] == s else dead


# ------------------------------------------------------------------ 手写词法器
KEYWORDS = {'if': 'KW_IF', 'else': 'KW_ELSE', 'while': 'KW_WHILE'}


class HandLexer:
    """GCC/Clang/rustc 风格：关键字查表、嵌套注释用计数器、原始字符串按 # 个数配对。"""

    def __init__(self, text):
        self.s, self.i = text, 0

    def peek(self, k=0):
        j = self.i + k
        return self.s[j] if j < len(self.s) else ''

    def tokens(self):
        while True:
            tok = self.next()
            yield tok
            if tok[0] == 'EOF':
                return

    def next(self):
        self.skip_trivia()
        start, c = self.i, self.peek()
        if c == '':
            return ('EOF', '', start)
        if c == 'r' and self.peek(1) in ('"', '#'):
            return self.raw_string(start)
        if c.isalpha() or c == '_':
            while self.peek().isalnum() or self.peek() == '_':
                self.i += 1
            word = self.s[start:self.i]
            return (KEYWORDS.get(word, 'IDENT'), word, start)  # 关键字不进 DFA，查表
        if c.isdigit():
            while self.peek().isdigit():
                self.i += 1
            if self.peek().isalpha():                         # 有针对性的错误信息
                raise LexError(f'位置 {self.i}：数字字面量后不能紧跟字母')
            return ('NUMBER', self.s[start:self.i], start)
        if c == '>':
            if self.peek(1) == '=':
                self.i += 2
                return ('GE', '>=', start)
            self.i += 1
            return ('GT', '>', start)
        raise LexError(f'位置 {start} 处无法识别：{c!r}')

    def skip_trivia(self):
        while True:
            c = self.peek()
            if c in (' ', '\t', '\n'):
                self.i += 1
            elif c == '/' and self.peek(1) == '*':
                self.block_comment()
            else:
                return

    def block_comment(self):
        start, depth = self.i, 0                  # 计数器：超出正则语言的部分
        while True:
            if self.i >= len(self.s):
                raise LexError(f'位置 {start} 处的块注释未闭合')
            if self.s.startswith('/*', self.i):
                depth += 1
                self.i += 2
            elif self.s.startswith('*/', self.i):
                depth -= 1
                self.i += 2
                if depth == 0:
                    return
            else:
                self.i += 1

    def raw_string(self, start):
        self.i += 1                               # 跳过 r
        n = 0
        while self.peek() == '#':
            n += 1
            self.i += 1
        if self.peek() != '"':
            raise LexError(f'位置 {start}：原始字符串缺少开头的引号')
        self.i += 1
        close = '"' + '#' * n                     # 结束标记取决于开头：非正则
        j = self.s.find(close, self.i)
        if j < 0:
            raise LexError(f'位置 {start} 处的原始字符串未闭合')
        body = self.s[self.i:j]
        self.i = j + len(close)
        return ('RAW_STR', body, start)
