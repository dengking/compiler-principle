"""第 10 章：组装 —— 三段式搜索（正向惰性 DFA 求终点、反向 DFA 求起点、
区间内求捕获）与元引擎（按模式与输入选择引擎）。"""
from .syntax import parse, features
from .compiler import compile_ast, Unsupported
from .pikevm import pike_search, pike_captures, backtrack_captures, pike_vm, spans
from .dfa import LazyDFA, GaveUp, View, reverse_prog
from .literals import exact_literal, anchored_start, prefix_literals, Prefilter
from .backtrack import Backtracker


class ThreePhase:
    """RE2 / Rust regex 的快速路径。"""

    def __init__(self, prog, ngroups, use_prefilter=True, **lazy_kw):
        self.prog, self.ngroups = prog, ngroups
        self.fwd = LazyDFA(prog, **lazy_kw)                       # 非锚定，leftmost-first
        self.rev = LazyDFA(reverse_prog(prog), anchored=True, longest=True, **lazy_kw)
        lits = prefix_literals(prog) if use_prefilter else None
        self.pre = Prefilter(lits) if lits else None
        self.gave_up = 0

    def search(self, text, pos=0):
        if self.pre is not None:
            i = self.pre.find(text, pos)
            if i < 0:
                return None               # 没有候选，必然没有匹配
            pos = i                       # 起点不可能早于 i
        n = len(text)
        try:
            # 第一段：正向扫描，求终点
            k = self.fwd.run(View(text, pos, n), at_start=(pos == 0), at_end=True)
            if k is None:
                return None
            e = pos + k
            # 第二段：从 e 反向扫描到 pos，求起点（反向程序交换了 ^ 与 $）
            k = self.rev.run(View(text, pos, e, backward=True),
                             at_start=(e == n), at_end=(pos == 0))
            assert k is not None, "forward scan proved a match exists"
            return (e - k, e)
        except GaveUp:
            self.gave_up += 1
            return pike_search(self.prog, text, pos)


class Regex:
    """元引擎：对外一个类型，内部按模式特性与输入选择引擎。"""

    def __init__(self, pattern, bt_limit=256 * 1024, budget=1_000_000, **kw):
        self.pattern = pattern
        self.ast, self.ngroups = parse(pattern)
        feats = features(self.ast)
        self.bt_limit = bt_limit
        if feats & {'backref', 'look', 'atomic'}:
            self.strategy = 'backtrack'                   # 只有回溯能实现，带步数预算
            self.bt = Backtracker(pattern, budget=budget)
            return
        self.prog = compile_ast(self.ast)
        self.lit = exact_literal(self.prog)
        self.anchored = anchored_start(self.prog)
        if self.lit is not None:
            self.strategy = 'literal'
        elif 'wordb' in feats:
            self.strategy = 'pikevm'                      # 本实现的 DFA 不支持 \b
        else:
            self.strategy = 'dfa'
            self.tp = ThreePhase(self.prog, self.ngroups, **kw)

    def search(self, text, pos=0):
        """返回 (start, end) 或 None。"""
        if self.strategy == 'backtrack':
            r = self.bt.search(text, pos)
            return None if r is None else r[0]
        if self.anchored and pos > 0:
            return None
        if self.strategy == 'literal':
            i = text.find(self.lit, pos)
            return None if i < 0 else (i, i + len(self.lit))
        if self.strategy == 'pikevm':
            return pike_search(self.prog, text, pos)
        return self.tp.search(text, pos)

    def captures(self, text, pos=0):
        if self.strategy == 'backtrack':
            return self.bt.search(text, pos)
        m = self.search(text, pos)
        if m is None:
            return None
        s, e = m
        if (e - s + 1) * len(self.prog) <= self.bt_limit:
            return backtrack_captures(self.prog, self.ngroups, text, s, e)
        return pike_captures(self.prog, self.ngroups, text, s, e)

    def finditer(self, text):
        pos, last_end = 0, -1
        while pos <= len(text):
            m = self.search(text, pos)
            if m is None:
                return
            s, e = m
            if s == e == last_end:            # 紧贴上一个匹配的空匹配：跳过
                pos = e + 1
                continue
            yield m
            last_end = e
            pos = e if e > s else e + 1
