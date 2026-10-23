"""第 7 章：不经过 ε-NFA 直接构造自动机 ——
followpos（龙书 3.9 节）、Glushkov 位置自动机（含位掩码模拟）、Brzozowski 导数（含交集与补集）。"""
from bisect import bisect_right
from dataclasses import dataclass

from .compiler import Unsupported

MAXCP = 0x110000


# ------------------------------------------------------------------ 字符集合
class CSet:
    """区间表示的字符集合（可取反），支持 in。"""
    __slots__ = ('ranges', 'neg')

    def __init__(self, ranges, neg=False):
        self.ranges, self.neg = tuple(ranges), neg

    def __contains__(self, c):
        if not isinstance(c, str):
            return False
        hit = any(lo <= c <= hi for lo, hi in self.ranges)
        return hit != self.neg

    def cuts(self):
        for lo, hi in self.ranges:
            yield ord(lo)
            if ord(hi) + 1 < MAXCP:
                yield ord(hi) + 1

    def __eq__(self, o):
        return isinstance(o, CSet) and (self.ranges, self.neg) == (o.ranges, o.neg)

    def __hash__(self):
        return hash((self.ranges, self.neg))

    def __repr__(self):
        body = ''.join(lo if lo == hi else f'{lo}-{hi}' for lo, hi in self.ranges)
        return f"[{'^' if self.neg else ''}{body}]"


def intersects(a, b):
    """两个 CSet 是否有公共字符：只需检查各基本区间的代表点。"""
    for cp in {0, *a.cuts(), *b.cuts()}:
        ch = chr(cp)
        if ch in a and ch in b:
            return True
    return False


def class_reps(csets):
    """全局字符等价类：返回 (每类起始码点, 每类代表字符)。"""
    cuts = {0}
    for cs in csets:
        cuts.update(cs.cuts())
    starts = sorted(cuts)
    return starts, [chr(c) for c in starts]


# ------------------------------------------------------------------ 位置 AST
@dataclass(frozen=True)
class Eps:
    pass


@dataclass(frozen=True)
class Sym:
    chars: object            # CSet，或者 End（结束标记）


@dataclass(frozen=True)
class Alt:
    l: object
    r: object


@dataclass(frozen=True)
class Cat:
    l: object
    r: object


@dataclass(frozen=True)
class Star:
    r: object


@dataclass(frozen=True)
class End:
    """结束标记 #k，不与任何真实字符相等。"""
    rule: int = 0

    def __contains__(self, c):
        return False


def to_pos(n, drop_asserts=False):
    """把第 2 章的 AST 转成位置 AST（只支持正则子集）。
    drop_asserts=True 时把零宽断言当作 ε（ReDoS 分析用的过近似）。"""
    k = n[0]
    if drop_asserts and k in ('bol', 'eol', 'wordb', 'nwordb'):
        return Eps()
    if k == 'char':
        return Sym(CSet([(n[1], n[1])]))
    if k == 'any':
        return Sym(CSet([('\n', '\n')], neg=True))
    if k == 'class':
        return Sym(CSet(n[1], n[2]))
    if k == 'empty':
        return Eps()
    if k == 'cat':
        r = to_pos(n[1][0], drop_asserts)
        for x in n[1][1:]:
            r = Cat(r, to_pos(x, drop_asserts))
        return r
    if k == 'alt':
        return Alt(to_pos(n[1], drop_asserts), to_pos(n[2], drop_asserts))
    if k == 'group':
        return to_pos(n[1], drop_asserts)
    if k == 'star':
        return Star(to_pos(n[1], drop_asserts))
    if k == 'plus':                       # r+ = r r*：r 被复制，位置也被重复编号
        return Cat(to_pos(n[1], drop_asserts), Star(to_pos(n[1], drop_asserts)))
    if k == 'quest':
        return Alt(to_pos(n[1], drop_asserts), Eps())
    if k == 'repeat':
        _, sub, lo, hi, _ = n
        parts = [to_pos(sub, drop_asserts) for _ in range(lo)]
        if hi is None:
            parts.append(Star(to_pos(sub, drop_asserts)))
        else:
            tail = Eps()
            for _ in range(hi - lo):      # 嵌套可选 x(x(x)?)?
                tail = Alt(Cat(to_pos(sub, drop_asserts), tail), Eps())
            parts.append(tail)
        r = parts[0]
        for x in parts[1:]:
            r = Cat(r, x)
        return r
    raise Unsupported(f"position automata do not support {k!r}")


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
        for p in l1:                      # r 的最后一个字符之后，可以紧跟 s 的第一个字符
            follow[p] |= f2
        return (n1 and n2,
                f1 | f2 if n1 else f1,
                l1 | l2 if n2 else l2)
    if isinstance(n, Star):
        _, f, l = analyze(n.r, syms, follow)
        for p in l:                       # 一次迭代结束后，可以紧接着开始下一次
            follow[p] |= f
        return True, f, l
    raise TypeError(n)


# ------------------------------------------------------------------ followpos DFA
class PosDFA:
    """状态 = “下一个字符可以来自这些位置”。"""

    def __init__(self, regex):
        syms, follow = [], {}
        _, first, _ = analyze(Cat(regex, Sym(End())), syms, follow)
        self.syms, self.follow = syms, follow
        endp = len(syms) - 1
        self.starts, reps = class_reps([s for s in syms if isinstance(s, CSet)])
        start = frozenset(first)
        index = {start: 0}
        self.sets, self.trans, self.accept = [start], [], []
        i = 0
        while i < len(self.sets):
            S = self.sets[i]
            i += 1
            self.accept.append(endp in S)
            row = []
            for c in reps:
                T = frozenset(q for p in S if c in syms[p] for q in follow[p])
                if T not in index:
                    index[T] = len(self.sets)
                    self.sets.append(T)
                row.append(index[T])
            self.trans.append(row)
        self.nstates = len(self.sets)

    def fullmatch(self, s):
        q = 0
        for ch in s:
            q = self.trans[q][bisect_right(self.starts, ord(ch)) - 1]
        return self.accept[q]


# ------------------------------------------------------------------ Glushkov 位掩码
class Glushkov:
    """状态 p = “刚读完位置 p 的字符”。同质性：进入 p 的边都标着 syms[p]，
    所以一步转移 D' = (⋃_{p∈D} F[p]) & B[c]。"""

    def __init__(self, regex):
        syms, follow = [], {}
        self.nullable, first, last = analyze(regex, syms, follow)
        mask = lambda ps: sum(1 << p for p in ps)
        self.syms = syms
        self.first, self.last = mask(first), mask(last)
        self.follow = [mask(follow[p]) for p in range(len(syms))]
        self.B = {}

    def char_mask(self, c):
        m = self.B.get(c)
        if m is None:
            m = sum(1 << p for p, cs in enumerate(self.syms) if c in cs)
            self.B[c] = m
        return m

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


# ------------------------------------------------------------------ Brzozowski 导数
EMPTY = ('empty',)
EPS = ('eps',)
OTHER = object()                  # 代表“表达式中未出现的任意字符”


def sym(chars, neg=False):
    return ('sym', frozenset(chars), neg)


def _flatten(kind, rs):
    out = set()
    for r in rs:
        if r[0] == kind:
            out |= r[1]
        else:
            out.add(r)
    return out


def alt(*rs):                     # 智能构造函数：结合、交换、幂等（ACI），删去 ∅
    s = _flatten('alt', rs) - {EMPTY}
    if not s:
        return EMPTY
    return next(iter(s)) if len(s) == 1 else ('alt', frozenset(s))


def and_(*rs):
    s = _flatten('and', rs)
    if EMPTY in s:
        return EMPTY
    s.discard(('not', EMPTY))     # 全集是交集的单位元
    if not s:
        return ('not', EMPTY)
    return next(iter(s)) if len(s) == 1 else ('and', frozenset(s))


def cat(a, b):
    if a == EMPTY or b == EMPTY:
        return EMPTY
    if a == EPS:
        return b
    if b == EPS:
        return a
    if a[0] == 'cat':             # 统一成右结合
        return cat(a[1], cat(a[2], b))
    return ('cat', a, b)


def star(r):
    if r in (EMPTY, EPS):
        return EPS
    return r if r[0] == 'star' else ('star', r)


def not_(r):
    return r[1] if r[0] == 'not' else ('not', r)


def d_nullable(r):
    k = r[0]
    if k in ('eps', 'star'):
        return True
    if k in ('empty', 'sym'):
        return False
    if k == 'alt':
        return any(d_nullable(x) for x in r[1])
    if k == 'and':
        return all(d_nullable(x) for x in r[1])
    if k == 'cat':
        return d_nullable(r[1]) and d_nullable(r[2])
    if k == 'not':
        return not d_nullable(r[1])
    raise ValueError(r)


def sym_accepts(r, c):
    _, chars, neg = r
    if c is OTHER:                # 未出现的字符不在任何 chars 中
        return neg
    return (c in chars) != neg


def deriv(c, r):
    k = r[0]
    if k in ('empty', 'eps'):
        return EMPTY
    if k == 'sym':
        return EPS if sym_accepts(r, c) else EMPTY
    if k == 'alt':
        return alt(*(deriv(c, x) for x in r[1]))
    if k == 'and':
        return and_(*(deriv(c, x) for x in r[1]))
    if k == 'cat':
        d = cat(deriv(c, r[1]), r[2])
        return alt(d, deriv(c, r[2])) if d_nullable(r[1]) else d
    if k == 'star':
        return cat(deriv(c, r[1]), r)
    if k == 'not':
        return not_(deriv(c, r[1]))
    raise ValueError(r)


def mentioned(r, out=None):
    out = set() if out is None else out
    k = r[0]
    if k == 'sym':
        out |= r[1]
    elif k in ('alt', 'and'):
        for x in r[1]:
            mentioned(x, out)
    elif k == 'cat':
        mentioned(r[1], out)
        mentioned(r[2], out)
    elif k in ('star', 'not'):
        mentioned(r[1], out)
    return out


class DerivDFA:
    def __init__(self, r):
        alphabet = sorted(mentioned(r)) + [OTHER]
        index, self.order, self.trans, self.accept = {r: 0}, [r], [], []
        i = 0
        while i < len(self.order):
            S = self.order[i]
            i += 1
            self.accept.append(d_nullable(S))
            row = {}
            for c in alphabet:
                T = deriv(c, S)
                if T not in index:
                    index[T] = len(self.order)
                    self.order.append(T)
                row[c] = index[T]
            self.trans.append(row)
        self.nstates = len(self.order)

    def fullmatch(self, s):
        q = 0
        for c in s:
            row = self.trans[q]
            q = row[c] if c in row else row[OTHER]
        return self.accept[q]

    def is_empty(self):
        return not any(self.accept)


def to_deriv(n, class_limit=512):
    """第 2 章 AST → 导数表达式。"""
    k = n[0]
    if k == 'char':
        return sym(n[1])
    if k == 'any':
        return sym('\n', neg=True)
    if k == 'class':
        chars = [chr(c) for lo, hi in n[1] for c in range(ord(lo), ord(hi) + 1)]
        if len(chars) > class_limit:
            raise Unsupported("class too large for this toy derivative engine")
        return sym(chars, n[2])
    if k == 'empty':
        return EPS
    if k == 'cat':
        r = EPS
        for x in reversed(n[1]):
            r = cat(to_deriv(x), r)
        return r
    if k == 'alt':
        return alt(to_deriv(n[1]), to_deriv(n[2]))
    if k == 'group':
        return to_deriv(n[1])
    if k == 'star':
        return star(to_deriv(n[1]))
    if k == 'plus':
        x = to_deriv(n[1])
        return cat(x, star(x))
    if k == 'quest':
        return alt(to_deriv(n[1]), EPS)
    if k == 'repeat':
        _, sub, lo, hi, _ = n
        x = to_deriv(sub)
        r = star(x) if hi is None else EPS
        if hi is not None:
            for _ in range(hi - lo):
                r = alt(cat(x, r), EPS)
        for _ in range(lo):
            r = cat(x, r)
        return r
    raise Unsupported(f"derivatives here do not support {k!r}")


def contains(w):
    """匹配包含子串 w 的所有串：.*w.*"""
    any_ = star(sym((), neg=True))
    body = sym(w[-1])
    for ch in reversed(w[:-1]):
        body = cat(sym(ch), body)
    return cat(any_, cat(body, any_))


def equivalent(r, s):
    """语言等价判定：(r & ¬s) | (s & ¬r) 为空。"""
    return DerivDFA(alt(and_(r, not_(s)), and_(s, not_(r)))).is_empty()
