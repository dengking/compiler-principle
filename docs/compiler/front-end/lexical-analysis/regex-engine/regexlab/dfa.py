"""第 6 章：DFA —— 子集构造、字符等价类、最小化（Moore / Hopcroft）、
惰性 DFA（有序状态 + 缓存清空 + 放弃回退）、反向程序。"""
from bisect import bisect_right

from .syntax import in_class
from .compiler import Unsupported

MAXCP = 0x110000


# ------------------------------------------------------------------ 字符等价类
def class_starts(prog):
    """收集所有区间端点，返回每个等价类的起始码点（有序）。"""
    cuts = {0}

    def add(lo, hi):
        cuts.add(lo)
        if hi + 1 < MAXCP:
            cuts.add(hi + 1)
    for op in prog:
        if op[0] == 'char':
            add(ord(op[1]), ord(op[1]))
        elif op[0] == 'any':
            add(10, 10)                            # '\n' 自成一类
        elif op[0] == 'class':
            for lo, hi in op[1]:
                add(ord(lo), ord(hi))
    return sorted(cuts)


def check_dfa_ok(prog):
    for op in prog:
        if op[0] == 'assert' and op[1] not in ('bol', 'eol'):
            raise Unsupported("DFA here supports only ^ and $ (\\b needs look-behind state)")


def step(prog, S, rep):
    """状态 S（有序或无序的 pc 集合）读入代表字符 rep 后，存活线程的下一条 pc（保持顺序）。"""
    nxt = []
    for pc in S:
        op = prog[pc]
        k = op[0]
        if k == 'char':
            ok = rep == op[1]
        elif k == 'any':
            ok = rep != '\n'
        elif k == 'class':
            ok = in_class(rep, op[1]) != op[2]
        else:
            ok = False                             # match / 悬而未决的 eol
        if ok:
            nxt.append(pc + 1)
    return nxt


# ------------------------------------------------------------------ 完整 DFA
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
        if k == 'jmp':
            stack.append(op[1])
        elif k == 'split':
            stack += [op[1], op[2]]
        elif k == 'save':
            stack.append(pc + 1)                   # DFA 不关心捕获
        elif k == 'assert':
            if op[1] == 'bol':
                if at_start:
                    stack.append(pc + 1)
            elif at_end:
                stack.append(pc + 1)
            else:
                out.add(pc)                        # eol：留待文本结束时裁决
        else:
            out.add(pc)
    return frozenset(out)


class DFA:
    """子集构造得到的完整 DFA，只回答“是否匹配”。"""

    def __init__(self, prog, anchored=False, max_states=100_000):
        check_dfa_ok(prog)
        self.starts = class_starts(prog)
        reps = [chr(c) for c in self.starts]       # 每个等价类取一个代表字符
        inject = frozenset() if anchored else closure(prog, [0], False, False)

        start = closure(prog, [0], True, False)
        index = {start: 0}
        sets = [start]
        self.table = []
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
        self.sets = sets
        self.accept = [match_pc in S for S in sets]
        self.eof_accept = [match_pc in closure(prog, S, False, True) for S in sets]
        self.empty_ok = match_pc in closure(prog, [0], True, True)
        self.dead = index.get(frozenset())
        self.nstates = len(sets)

    def cls(self, ch):
        return bisect_right(self.starts, ord(ch)) - 1

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


# ------------------------------------------------------------------ 最小化
def moore(table, labels):
    """Moore 划分细化。labels[i] 给出状态 i 的初始分组依据。
    返回 (每个状态的块号, 块数)。复杂度 O(s²·σ)。"""
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


def hopcroft(table, labels):
    """Hopcroft 算法，“处理较小的一半”，复杂度 O(s·σ·log s)。"""
    n = len(table)
    sigma = len(table[0]) if table else 0
    inv = [[[] for _ in range(n)] for _ in range(sigma)]   # inv[c][t] = {s | δ(s,c)=t}
    for s, row in enumerate(table):
        for c, t in enumerate(row):
            inv[c][t].append(s)
    groups = {}
    for s, l in enumerate(labels):
        groups.setdefault(l, set()).add(s)
    blocks = list(groups.values())
    where = [0] * n
    for b, B in enumerate(blocks):
        for s in B:
            where[s] = b
    work = set(range(len(blocks)))
    while work:
        A = blocks[work.pop()]
        for c in range(sigma):
            X = {s for t in A for s in inv[c][t]}  # 读入 c 后落入 A 的状态
            touched = {}
            for s in X:
                touched.setdefault(where[s], set()).add(s)
            for b, inter in touched.items():
                Y = blocks[b]
                if len(inter) == len(Y):
                    continue
                rest = Y - inter
                blocks[b] = inter
                nb = len(blocks)
                blocks.append(rest)
                for s in rest:
                    where[s] = nb
                if b in work:
                    work.add(nb)
                else:                              # 只把较小的一半放进工作集
                    work.add(b if len(inter) <= len(rest) else nb)
    # 规范化编号：按状态 0 出现的顺序
    remap, out = {}, []
    for s in range(n):
        out.append(remap.setdefault(where[s], len(remap)))
    return out, len(remap)


def minimize_dfa(d, algo=hopcroft):
    labels = list(zip(d.accept, d.eof_accept))
    block, n = algo(d.table, labels)
    table = [None] * n
    for i, row in enumerate(d.table):
        table[block[i]] = [block[t] for t in row]
    return table, block[0], n


# ------------------------------------------------------------------ 惰性 DFA
class GaveUp(Exception):
    """缓存清空过于频繁，惰性 DFA 放弃。pos 是放弃时的位置。"""

    def __init__(self, pos):
        super().__init__(pos)
        self.pos = pos


class View:
    """text[lo:hi] 的只读视图；backward=True 时从 hi-1 往 lo 倒着迭代。"""

    def __init__(self, text, lo, hi, backward=False):
        self.text, self.lo, self.hi, self.backward = text, lo, hi, backward

    def __len__(self):
        return self.hi - self.lo

    def __iter__(self):
        t = self.text
        rng = range(self.hi - 1, self.lo - 1, -1) if self.backward else range(self.lo, self.hi)
        for i in rng:
            yield t[i]


class LazyDFA:
    """状态 = (有序 pc 元组, 是否已见过匹配)。转移在第一次用到时才计算。
    longest=True：无序、不截断，用于反向扫描求最长匹配。"""

    def __init__(self, prog, anchored=False, longest=False,
                 max_states=1000, min_clears=3, min_chars_per_state=10):
        check_dfa_ok(prog)
        self.prog = prog
        self.anchored = anchored          # 不注入新线程
        self.longest = longest
        self.starts = class_starts(prog)
        self.reps = [chr(c) for c in self.starts]
        self.match_pc = len(prog) - 1
        self.max_states = max_states
        self.min_clears = min_clears
        self.min_chars_per_state = min_chars_per_state
        self.stats = {'states': 0, 'clears': 0, 'misses': 0, 'hits': 0}
        self.reset()

    def reset(self):
        self.ids, self.keys, self.trans = {}, [], []
        self.acc, self.dead = [], []

    def intern(self, key):
        i = self.ids.get(key)
        if i is None:
            i = len(self.keys)
            self.ids[key] = i
            self.keys.append(key)
            self.trans.append([None] * len(self.reps))
            self.acc.append(self.match_pc in key[0])
            self.dead.append(not key[0])
            self.stats['states'] += 1
        return i

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
                if k == 'jmp':
                    stack.append(op[1])
                elif k == 'split':
                    stack.append(op[2])           # 后压入低优先级
                    stack.append(op[1])           # 先弹出高优先级
                elif k == 'save':
                    stack.append(pc + 1)
                elif k == 'assert':
                    if op[1] == 'bol':
                        if at_start:
                            stack.append(pc + 1)
                    elif at_end:
                        stack.append(pc + 1)
                    else:
                        out.append(pc)            # 悬而未决的 eol
                else:
                    out.append(pc)
                    if k == 'match' and not self.longest:
                        return tuple(out)         # 截断：丢弃更低优先级的线程
        return tuple(sorted(out)) if self.longest else tuple(out)

    def flag(self, matched, S):
        return (not self.anchored) and (matched or self.match_pc in S)

    def start_key(self, at_start):
        S = self.closure([0], at_start, False)
        return (S, self.flag(False, S))

    def compute(self, key, rep):
        S, matched = key
        nxt = step(self.prog, S, rep)
        inject = not (self.anchored or matched)   # 找到匹配后停止注入
        T = self.closure(nxt + [0] if inject else nxt, False, False)
        return (T, self.flag(matched, T))

    def accepts_at_eof(self, key):
        return self.match_pc in self.closure(key[0], False, True)

    def run(self, text, at_start=True, at_end=True, earliest=False):
        """扫描 text（字符串或 View），返回最后记录的匹配终点（相对偏移）；没有匹配返回 None。"""
        n = len(text)
        if n == 0:                                # 开头与结尾重合，单独处理
            S = self.closure([0], at_start, at_end)
            return 0 if self.match_pc in S else None

        s = self.intern(self.start_key(at_start))
        last = 0 if self.acc[s] else None         # 空匹配
        if earliest and last is not None:
            return last
        clears, since = 0, 0
        starts, trans = self.starts, self.trans
        for i, ch in enumerate(text):
            c = bisect_right(starts, ord(ch)) - 1
            t = self.trans[s][c]
            if t is None:                         # 缓存未命中：现算
                self.stats['misses'] += 1
                key = self.compute(self.keys[s], self.reps[c])
                if key not in self.ids and len(self.keys) >= self.max_states:
                    clears += 1
                    self.stats['clears'] += 1
                    if clears >= self.min_clears and since < self.min_chars_per_state * self.max_states:
                        raise GaveUp(i)           # 缓存几乎没有被复用
                    self.reset()                  # 清空，从当前状态重新开始
                    since, s = 0, None
                t = self.intern(key)
                if s is not None:
                    self.trans[s][c] = t
            else:
                self.stats['hits'] += 1
            s = t
            since += 1
            if self.dead[s]:
                return last                       # 所有线程死亡，不会再有匹配
            if self.acc[s]:
                last = i + 1
                if earliest:
                    return last
        if at_end and self.accepts_at_eof(self.keys[s]):
            last = n
        return last


# ------------------------------------------------------------------ 反向程序
def reverse_prog(prog):
    """构造识别“反转语言”的程序：L(rev) = { s[::-1] | s ∈ L(prog) }。"""
    M = len(prog) - 1                                # 正向 match
    preds = [[] for _ in prog]
    for q, op in enumerate(prog):
        k = op[0]
        if k == 'jmp':
            preds[op[1]].append(q)
        elif k == 'split':
            preds[op[1]].append(q)
            preds[op[2]].append(q)
        elif k != 'match':                           # char/any/class/save/assert 落到 q+1
            preds[q + 1].append(q)

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
                sp = len(out)
                out.append(None)                     # 稍后回填 split
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

    match = len(out)
    rev = []
    for op in out:                                   # 把符号目标改写为真实地址
        if op[0] == 'jmp':
            rev.append(('jmp', match if op[1] == 'MATCH' else label[op[1]]))
        else:
            rev.append(op)
    rev.append(('match',))
    return rev
