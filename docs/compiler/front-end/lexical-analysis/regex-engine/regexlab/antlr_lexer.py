"""第 9 章（上）：ANTLR 风格的词法器 —— 在 ATN 上做惰性子集构造。

语义与第 8 章相同（最长匹配 + 先写者优先），但不在生成时构造 DFA，
而是在运行时模拟 ATN，每算出一条 DFA 边就缓存起来（ANTLR 的 LexerATNSimulator 思想）。
语法分析的自适应预测 ALL(*) 见 allstar.py。"""
from .syntax import parse
from .direct import to_pos, Eps, Sym, Alt, Cat, Star


class LexError(Exception):
    pass


class ATN:
    def __init__(self):
        self.eps = []      # eps[s]：ε 转移的目标列表
        self.edges = []    # edges[s]：(字符集合, 目标) 列表
        self.stop = {}     # 规则停止状态 -> 规则编号

    def state(self):
        self.eps.append([])
        self.edges.append([])
        return len(self.eps) - 1


def build(atn, r, s, t):
    """在 atn 中加入一段从 s 到 t、识别 r 的子图（Thompson 构造）。"""
    if isinstance(r, Eps):
        atn.eps[s].append(t)
    elif isinstance(r, Sym):
        atn.edges[s].append((r.chars, t))
    elif isinstance(r, Cat):
        m = atn.state()
        build(atn, r.l, s, m)
        build(atn, r.r, m, t)
    elif isinstance(r, Alt):
        for sub in (r.l, r.r):
            a, b = atn.state(), atn.state()
            atn.eps[s].append(a)
            build(atn, sub, a, b)
            atn.eps[b].append(t)
    elif isinstance(r, Star):
        a, b = atn.state(), atn.state()
        atn.eps[s] += [a, t]          # 进入循环，或者直接跳过
        build(atn, r.r, a, b)
        atn.eps[b] += [a, t]          # 再来一次，或者离开
    else:
        raise TypeError(r)


def compile_lexer(patterns):
    atn = ATN()
    start = atn.state()
    for i, p in enumerate(patterns):
        ast, _ = parse(p)
        s, t = atn.state(), atn.state()
        atn.eps[start].append(s)
        build(atn, to_pos(ast), s, t)
        atn.stop[t] = i
    return atn, start


def closure(atn, states):
    """从 states 出发，沿 ε 边能到达的全部状态。"""
    seen = set(states)
    stack = list(states)
    while stack:
        p = stack.pop()
        for q in atn.eps[p]:
            if q not in seen:
                seen.add(q)
                stack.append(q)
    return frozenset(seen)


def move(atn, states, c):
    """读入字符 c 后，从 states 能直接到达的状态。"""
    out = set()
    for p in states:
        for cs, q in atn.edges[p]:
            if c in cs:
                out.add(q)
    return out


class ATNLexer:
    """(状态集合, 字符) -> 状态集合 的缓存就是一个惰性构造的 DFA。"""

    def __init__(self, patterns, skip=()):
        self.atn, s = compile_lexer(patterns)
        self.s0 = closure(self.atn, [s])
        self.skip = set(skip)
        self.trans = {}              # (D, c) -> D'
        self.accept = {}             # D -> 规则编号或 None
        self.misses = self.hits = 0

    def step(self, D, c):
        key = (D, c)
        if key not in self.trans:
            self.misses += 1
            self.trans[key] = closure(self.atn, move(self.atn, D, c))
        else:
            self.hits += 1
        return self.trans[key]

    def rule_of(self, D):
        if D not in self.accept:
            rs = [self.atn.stop[p] for p in D if p in self.atn.stop]
            self.accept[D] = min(rs) if rs else None
        return self.accept[D]

    def tokens(self, text):
        pos = 0
        while pos < len(text):
            D, i, best = self.s0, pos, None
            while D:
                r = self.rule_of(D)
                if r is not None:
                    best = (i, r)
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
