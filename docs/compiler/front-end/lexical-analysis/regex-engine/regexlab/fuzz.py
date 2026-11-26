"""第 15 章：差分模糊测试 —— 随机模式 × 随机文本，让所有引擎互相对拍。

运行：python3 -m regexlab.fuzz [轮数]
"""
import random
import re
import sys
from collections import Counter

from .syntax import parse, nullable, children
from .compiler import compile_ast
from .backtrack import Backtracker
from .pikevm import (pike_vm, pike_search, pike_captures, pike_finditer,
                     backtrack_prog, spans)
from .dfa import DFA, LazyDFA, reverse_prog, minimize_dfa, moore, hopcroft
from .direct import PosDFA, Glushkov, DerivDFA, to_pos, to_deriv
from .literals import prefix_literals
from .meta import Regex, ThreePhase

ATOMS = ['a', 'b', '.', '[ab]', '[^a]', 'ab', '', '^', '$']


def rand_pattern(depth=3, anchors=True):
    if depth == 0 or random.random() < 0.3:
        return random.choice(ATOMS)
    kinds = ['cat', 'cat', 'alt', 'star', 'plus', 'opt', 'lazy', 'group', 'rep']
    if anchors:
        kinds.append('anchor')
    kind = random.choice(kinds)
    sub = lambda: rand_pattern(depth - 1, anchors)
    if kind == 'cat':
        return sub() + sub()
    if kind == 'alt':
        return '(?:' + sub() + '|' + sub() + ')'
    if kind == 'star':
        return '(?:' + sub() + ')*'
    if kind == 'plus':
        return '(?:' + sub() + ')+'
    if kind == 'opt':
        return '(?:' + sub() + ')?'
    if kind == 'lazy':
        return '(?:' + sub() + ')' + random.choice(['*?', '+?', '??'])
    if kind == 'group':
        return '(' + sub() + ')'
    if kind == 'rep':
        lo = random.randint(0, 2)
        hi = random.choice([lo, lo + 1, lo + 2, ''])
        return '(?:' + sub() + '){%d,%s}' % (lo, hi)
    return random.choice(['^', '']) + sub() + random.choice(['$', ''])


def rand_text(alphabet='ab', maxlen=8):
    return ''.join(random.choice(alphabet) for _ in range(random.randint(0, maxlen)))


def fullmatch(prog, s):
    return pike_vm(prog, 0, s, 0, end=len(s)) is not None


def py_spans(p, s):
    m = re.search(p, s)
    return None if m is None else [m.span(g) if m.span(g) != (-1, -1) else (None, None)
                                   for g in range(m.re.groups + 1)]


def nullable_loop(n):
    """模式中是否有“循环体可空”的 * / + / {m,}。"""
    k = n[0]
    if k in ('star', 'plus') or (k == 'repeat' and n[3] != n[2]):
        if nullable(n[1]):
            return True
    return any(nullable_loop(c) for c in children(n))


def safe(f, *args):
    """被测引擎抛出异常也算一种（错误的）结果，而不是让测试中断。"""
    try:
        return f(*args)
    except Exception as e:                 # noqa: BLE001
        return f'EXC:{type(e).__name__}'


def run(rounds=300, texts=60, seed=None, verbose=True, random_pos=True):
    rnd_seed = seed if seed is not None else random.randrange(1 << 30)
    random.seed(rnd_seed)
    stats = Counter()
    diffs, notes = [], []
    for _ in range(rounds):
        p = rand_pattern()
        try:
            ast, ng = parse(p)
            prog = compile_ast(ast)
        except Exception:
            stats['skipped_patterns'] += 1
            continue
        stats['patterns'] += 1
        rev = reverse_prog(prog)
        dfa = DFA(prog)
        tp_small = ThreePhase(prog, ng, max_states=4, min_clears=10 ** 9)   # 逼迫缓存频繁清空
        meta = Regex(p)
        has_anchor = '^' in p or '$' in p
        if not has_anchor:
            pos_dfa = PosDFA(to_pos(ast))
            glu = Glushkov(to_pos(ast))
            der = DerivDFA(to_deriv(ast))
        lits = prefix_literals(prog)
        bt_perl = Backtracker(p)
        for _ in range(texts):
            s = rand_text()
            stats['cases'] += 1
            ref = pike_vm(prog, ng, s)
            ref_span = None if ref is None else (ref[0], ref[1])
            ref_caps = None if ref is None else spans(ref, ng)

            def check(name, got, want):
                if got != want:
                    stats['diff:' + name] += 1
                    if len(diffs) < 40:
                        diffs.append((name, p, s, got, want))

            # —— 同一语义（Pike VM 语义）的引擎必须完全一致 ——
            bs = safe(backtrack_prog, prog, ng, s)
            check('bitstate captures', bs if isinstance(bs, str) else (None if bs[0] is None else spans(bs[0], ng)), ref_caps)
            check('lazy-dfa three-phase span', safe(tp_small.search, s), ref_span)
            check('meta span', safe(meta.search, s), ref_span)
            check('meta captures', safe(meta.captures, s), ref_caps)
            check('full DFA is_match', safe(dfa.is_match, s), ref is not None)
            if random_pos:                     # 覆盖 pos > 0 的代码路径（锚点、预过滤跳跃）
                pos = random.randint(0, len(s))
                check('search from random pos', safe(meta.search, s, pos), pike_search(prog, s, pos))
            check('finditer', safe(lambda: list(meta.finditer(s))), list(pike_finditer(prog, s)))
            fm = fullmatch(prog, s)
            check('reverse program', safe(fullmatch, rev, s[::-1]), fm)
            if not has_anchor:
                check('followpos DFA', pos_dfa.fullmatch(s), fm)
                check('Glushkov bitmask', glu.fullmatch(s), fm)
                check('Brzozowski derivatives', der.fullmatch(s), fm)
            if lits and ref is not None:
                check('prefix completeness', any(s.startswith(L, ref[0]) for L in lits), True)
            # —— 与外部参照（Python re）比较：整体匹配区间，以及 Perl 语义的捕获组 ——
            py = None if (m := re.search(p, s)) is None else m.span()
            if py != ref_span:
                stats['note: span != python re' + (' (nullable loop body)' if nullable_loop(ast)
                                                    else ' (OTHER!)')] += 1
                notes.append(('span vs python', p, s, ref_span, py))
            check('backtrack(AST,perl) vs python re captures', bt_perl.search(s), py_spans(p, s))
            if ref_caps != py_spans(p, s):
                stats['note: pike captures != python captures'] += 1
        # 最小化：两种算法给出相同的块数
        if minimize_dfa(dfa, moore)[2] != minimize_dfa(dfa, hopcroft)[2]:
            stats['diff:minimize moore vs hopcroft'] += 1
    if verbose:
        print(f"seed={rnd_seed}")
        for k, v in sorted(stats.items()):
            print(f"  {k:48} {v}")
        for d in diffs[:10]:
            print('  DIFF', d)
    return stats, diffs


if __name__ == '__main__':
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 300)
