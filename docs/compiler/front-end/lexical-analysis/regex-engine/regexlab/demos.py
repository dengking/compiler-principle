"""生成报告中引用的全部实测数据：python3 -m regexlab.demos > run_output.txt"""
import random
import re
import time

from .syntax import parse, RegexError
from .compiler import compile_regex, compile_ast, dump, estimate_size, Unsupported
from .backtrack import Backtracker, StepLimit
from .pikevm import pike_vm, spans, backtrack_prog, pike_search
from .dfa import DFA, LazyDFA, GaveUp, minimize_dfa, moore, hopcroft, reverse_prog, class_starts
from .direct import (PosDFA, Glushkov, DerivDFA, to_pos, to_deriv, analyze, Cat, Sym, End,
                     and_, not_, contains, equivalent)
from .lexgen import LexerDFA, tokenize, tokenize_linear, comb_pack, HandLexer
from .antlr_lexer import ATNLexer
from . import allstar
from .literals import prefix_literals, AhoCorasick, shift_and, Prefilter
from .meta import Regex, ThreePhase
from .utf8 import utf8_sequences, fmt_seq
from .redos import analyze_redos
from . import fuzz


def H(title):
    print('\n' + '=' * 78 + f'\n{title}\n' + '=' * 78)


def timeit(f, repeat=3):
    best = 1e9
    for _ in range(repeat):
        t = time.perf_counter()
        f()
        best = min(best, time.perf_counter() - t)
    return best


def ch2():
    H('第 2 章  解析器')
    print(parse(r'(a|b)*c{2,3}'))
    for bad in ['(ab', 'a**+?{', '[z-a]', '(' * 300 + 'a' + ')' * 300, 'a{2000}']:
        try:
            parse(bad)
        except RegexError as e:
            print(f"{bad[:20]!r:24} -> {e.msg}")


def ch3():
    H('第 3 章  AST 回溯：灾难性回溯与防御')
    print(f"{'n':>3} {'(a+)+$ 步数':>14} {'耗时(s)':>9} {'(?>a+)+$ 步数':>14} {'a++$ 步数':>10}")
    for n in range(8, 21, 2):
        text = 'a' * n + 'b'
        b = Backtracker(r'(a+)+$')
        t = time.perf_counter()
        b.search(text)
        dt = time.perf_counter() - t
        b2 = Backtracker(r'(?>a+)+$')
        b2.search(text)
        b3 = Backtracker(r'a++$')
        b3.search(text)
        print(f"{n:>3} {b.steps:>14,} {dt:>9.3f} {b2.steps:>14,} {b3.steps:>10,}")
    try:
        Backtracker(r'(a+)+$', budget=100_000).search('a' * 40 + 'b')
    except StepLimit as e:
        print('budget exceeded after', e.args[0], 'steps')
    for p, s in [(r'(a*)*', 'b'), (r'(a+)b\1', 'xaaabaa'), (r'(a)?b\1', 'b'),
                 (r'\w+(?=,)', 'ab,cd'), (r'(?<=\$)\d+', 'cost $42'), (r'(?<!\$)\b\d+', '$42 and 17'),
                 (r'^b.(?:(?:[ab])*?)*', 'baaabba')]:
        print(f"{p:24} {s!r:14} perl={Backtracker(p).search(s)}  fail={Backtracker(p, empty_iter='fail').search(s)}  "
              f"python={None if (m := re.search(p, s)) is None else [m.span(g) for g in range(m.re.groups + 1)]}")


def ch4():
    H('第 4 章  Thompson 构造')
    prog, _ = compile_regex('a(b|c)*d')
    print(dump(prog))
    prog, _ = compile_regex('x{2,4}')
    print(dump(prog))
    for p in ['(?:a{100}){10}', '(?:a{100}){100}', '(?:(?:a{100}){100}){100}']:
        ast, _ = parse(p)
        print(f"{p:28} 估计指令数 {estimate_size(ast):>12,}", end='  ')
        try:
            compile_ast(ast)
            print('ok')
        except Unsupported as e:
            print('rejected:', e)


def ch5():
    H('第 5 章  Pike VM 与有界回溯')
    for p, s in [(r'a(b|c)*d', 'xxabcbd'), (r'a(.*)b', 'aXbYb'), (r'a(.*?)b', 'aXbYb'),
                 (r'(a+)+$', 'a' * 30 + 'b'), (r'(a*)*', 'b'), (r'(a|ab)(c|bcd)(d*)', 'abcd')]:
        prog, ng = compile_regex(p)
        caps = pike_vm(prog, ng, s)
        print(f"{p:20} {s[:12]!r:15} -> {None if caps is None else spans(caps, ng)}")
    print('BitState 步数（(a+)+$，文本 a^n b）：')
    prog, ng = compile_regex(r'(a+)+$')
    for n in [10, 100, 1000, 10000]:
        _, steps = backtrack_prog(prog, ng, 'a' * n + 'b', memo=True)
        print(f"  n={n:>6}  steps={steps:>12,}  len(prog)*(n+2)={len(prog) * (n + 2):>12,}")
    print('不带记忆化的程序回溯（同一模式）：')
    for n in [10, 14, 18]:
        _, steps = backtrack_prog(prog, ng, 'a' * n + 'b', memo=False)
        print(f"  n={n:>3}  steps={steps:>12,}")
    print('线程数上界验证：最多活跃线程数 <= len(prog)')
    text = 'ab' * 2000
    for p in [r'(a|b)*a(a|b){8}', r'(?:a|ab|b)*c']:
        prog, ng = compile_regex(p)
        t = timeit(lambda: pike_vm(prog, ng, text), 1)
        print(f"  {p:22} len(prog)={len(prog):3}  Pike VM 处理 {len(text)} 字符耗时 {t:.3f}s")


def ch6():
    H('第 6 章  DFA')
    prog, _ = compile_regex(r'(a|b)*abb')
    d = DFA(prog)
    print('(a|b)*abb 非锚定 DFA 状态数', d.nstates, ' 等价类数', len(d.starts),
          ' 最小化后', minimize_dfa(d)[2])
    da = DFA(prog, anchored=True)
    print('(a|b)*abb 锚定 DFA 状态数', da.nstates, ' 最小化后', minimize_dfa(da)[2])
    prog, _ = compile_regex(r'[a-z]x')
    print('[a-z]x 等价类起点:', [repr(chr(c)) for c in class_starts(prog)])
    print(f"{'k':>3} {'NFA 指令':>8} {'DFA 状态':>9} {'Moore':>7} {'Hopcroft':>9} {'Moore(s)':>9} {'Hopcroft(s)':>11}")
    for k in range(1, 11):
        prog, _ = compile_regex(rf'(a|b)*a(a|b){{{k}}}')
        d = DFA(prog, anchored=True)
        tm = timeit(lambda: minimize_dfa(d, moore), 1)
        th = timeit(lambda: minimize_dfa(d, hopcroft), 1)
        print(f"{k:>3} {len(prog):>8} {d.nstates:>9} {minimize_dfa(d, moore)[2]:>7} "
              f"{minimize_dfa(d, hopcroft)[2]:>9} {tm:>9.3f} {th:>11.3f}")
    print('惰性 DFA：(a|b)*a(a|b){k}c 在 2×10^4 个随机 a/b 上搜索（不会匹配，必须读完全文）')
    random.seed(0)
    text = ''.join(random.choice('ab') for _ in range(20_000))
    print(f"{'k':>3} {'最小DFA状态':>10} {'生成状态':>8} {'清空':>4} {'放弃?':>6} {'三段式(s)':>9} {'PikeVM(s)':>9}")
    for k in [3, 6, 8, 9, 12]:
        prog, ng = compile_regex(rf'(a|b)*a(a|b){{{k}}}c')
        tp = ThreePhase(prog, ng, use_prefilter=False, max_states=1000)
        t = time.perf_counter()
        res = tp.search(text)
        tl = time.perf_counter() - t
        tpk = timeit(lambda: pike_search(prog, text), 1)
        st = tp.fwd.stats
        print(f"{k:>3} {2 ** (k + 1):>10} {st['states']:>8} {st['clears']:>4} {'是' if tp.gave_up else '否':>6} "
              f"{tl:>9.3f} {tpk:>9.3f}")
    rev = reverse_prog(compile_regex('ab|cd')[0])
    print('reverse_prog(ab|cd):')
    print(dump(rev))


def ch7():
    H('第 7 章  直接构造')
    ast, _ = parse(r'(a|b)*abb')
    syms, follow = [], {}
    analyze(Cat(to_pos(ast), Sym(End())), syms, follow)
    for p in range(len(syms)):
        print(f"  位置 {p + 1} {syms[p]!r:6} followpos={sorted(q + 1 for q in follow[p])}")
    pd = PosDFA(to_pos(ast))
    print('followpos DFA 状态数:', pd.nstates, ' 状态=', [sorted(x + 1 for x in S) for S in pd.sets])
    prog, _ = compile_regex(r'(a|b)*abb')
    print('Thompson+子集构造（锚定）状态数:', DFA(prog, anchored=True).nstates)
    r = and_(contains('ab'), not_(contains('ba')))
    dd = DerivDFA(r)
    print('“含 ab 且不含 ba” 导数 DFA 状态数', dd.nstates,
          {s: dd.fullmatch(s) for s in ['ab', 'aab', 'abb', 'aba', 'bab', 'xaby', 'ba', '']})
    for a, b in [('(a|b)*', '(a*b*)*'), ('(ab)*a', 'a(ba)*'), ('a*', 'a+')]:
        print(f"  equivalent({a}, {b}) = {equivalent(to_deriv(parse(a)[0]), to_deriv(parse(b)[0]))}")
    g = Glushkov(to_pos(parse(r'(a|b)*abb')[0]))
    print('Glushkov: 位置数', len(g.syms), ' first=', bin(g.first), ' last=', bin(g.last))


def ch8():
    H('第 8 章  词法分析器生成器')
    pats = ['if', '[a-z][a-z0-9]*', '[0-9]+', '>=', '>', '[ \t\n]+']
    names = ['KW_IF', 'IDENT', 'NUMBER', 'GE', 'GT', 'WS']
    d = LexerDFA(pats)
    print('DFA 状态数', d.nstates, ' 等价类数', len(d.starts))
    print([(names[k], s) for k, s in tokenize(d, 'if x1 >= 42 iffy', skip={5})])
    print('把 IDENT 写在 KW_IF 前面时永远不会被选中的规则:', LexerDFA([pats[1], pats[0]]).unreachable_rules(2))
    print('最长匹配的平方级回退（规则 a 与 a*b，输入 a^n）：')
    for n in [1000, 2000, 4000, 8000]:
        dd = LexerDFA(['a', 'a*b'])
        s1, s2 = {}, {}
        t1 = timeit(lambda: tokenize(dd, 'a' * n, stats=s1), 1)
        t2 = timeit(lambda: tokenize_linear(dd, 'a' * n, stats=s2), 1)
        print(f"  n={n:>5}  朴素读入 {s1['reads']:>11,} ({t1:.3f}s)   Reps 读入 {s2['reads']:>7,} ({t2:.3f}s)")
    dd = LexerDFA(['a', 'a*b', 'a+'])
    s1 = {}
    tokenize(dd, 'a' * 4000, stats=s1)
    print('  加兜底规则 a+ 后朴素驱动读入:', s1['reads'])
    rows = [{c: t for c, t in enumerate(row) if t != d.dead} for row in d.trans]
    base, nxt, chk = comb_pack(rows, len(d.starts), d.dead)
    print(f"梳状压缩: 完整表 {d.nstates}×{len(d.starts)}={d.nstates * len(d.starts)} 项 → nxt/chk 长度 {len(nxt)}")
    src = 'if x1 >= 42 /* a /* b */ c */ r#"say "hi""# else'
    print(list(HandLexer(src).tokens()))


def ch9():
    H('第 9 章  ANTLR')
    lx = ATNLexer(['if', '[a-z]+', '[0-9]+', '[ ]+'], skip={3})
    print(list(lx.tokens('if ifx 42')), '缓存的转移数', len(lx.trans), 'misses', lx.misses, 'hits', lx.hits)
    lx2 = ATNLexer(['if', '[a-z]+', '[0-9]+', '[ ]+'], skip={3})
    src = ' '.join(random.choice(['if', 'x', 'foo', '42', 'iffy', 'bar7']) for _ in range(2000))
    toks = list(lx2.tokens(src))
    print(f'{len(toks)} 个记号后：缓存转移 {len(lx2.trans)}，命中率 {lx2.hits / (lx2.hits + lx2.misses):.4f}')
    g, c = allstar.build(allstar.G_CTX)
    for t in ['y b a', 'x b a']:
        tree, _ = allstar.parse(g, c, t, trace=True)
        print(tree)
    print(dict(c.stats))
    g, c = allstar.build(allstar.G_DECL)
    allstar.parse(g, c, 'unsigned unsigned unsigned int x ;', trace=True)


def ch10():
    H('第 10 章  元引擎')
    for p in ['hello', r'^\d+$', r'hello\w+', r'\bfoo\b', r'(a+)b\1', r'(\w+)@(\w+)\.com', r'[a-z]+ing']:
        r = Regex(p)
        tp = getattr(r, 'tp', None)
        print(f"{p:20} strategy={r.strategy:9} prefilter={None if tp is None or tp.pre is None else tp.pre.lits}")
    r = Regex(r'(\w+)@(\w+)\.com')
    print(r.search('mail: bob@ex.com!'), r.captures('mail: bob@ex.com!'))
    print(list(Regex('a*').finditer('baa')))


def ch12():
    H('第 12 章  字面量与预过滤')
    for p in ['hello\\w+', 'GET|POST', 'a?b', 'x(ab)*y', '\\d+px', 'a*b', '.*foo', '(xa|y)b', '[ab]x', '^ab']:
        print(f"  {p:12} -> {prefix_literals(compile_regex(p)[0])}")
    ac = AhoCorasick(['he', 'she', 'hers', 'his'])
    print('AhoCorasick earliest start in "ushers":', ac.find('ushers', 0), ' Prefilter:',
          Prefilter(['he', 'she', 'hers', 'his']).find('ushers', 0))
    print('Shift-And [ab]c 在 "xacbcabc" 的匹配终点:', shift_and([set('ab'), set('c')], 'xacbcabc'))
    random.seed(1)
    words = ['the', 'quick', 'brown', 'fox', 'jumps', 'over', 'lazy', 'dog', 'error', 'warning']
    text = ' '.join(random.choice(words) for _ in range(40000)) + ' ERROR: 404 found'
    for p in [r'ERROR: \d+', r'e\w+g']:
        prog, ng = compile_regex(p)
        tp_on = ThreePhase(prog, ng, use_prefilter=True)
        tp_off = ThreePhase(prog, ng, use_prefilter=False)
        r1 = tp_on.search(text)
        r2 = tp_off.search(text)
        assert r1 == r2
        t_on = timeit(lambda: tp_on.search(text))
        t_off = timeit(lambda: tp_off.search(text))
        t_py = timeit(lambda: re.search(p, text))
        print(f"  {p:14} 结果{r1}  预过滤开 {t_on * 1000:8.2f}ms  关 {t_off * 1000:8.2f}ms  Python re {t_py * 1000:6.2f}ms")


def ch11():
    H('第 11 章  Unicode 与断言')
    for lo, hi in [(0, 0x10FFFF), (0xE0, 0xFF), (0x4E00, 0x9FFF)]:
        print(f"  U+{lo:04X}–U+{hi:04X}:")
        for s in utf8_sequences(lo, hi):
            print('     ', fmt_seq(s))
    print('  \\b 由 Pike VM 处理:', Regex(r'\bcat\b').search('concat cat'))
    print("  'İ'.lower() 长度:", len('İ'.lower()), "  'ß'.upper():", 'ß'.upper(),
          "  'K'(U+212A).lower():", repr('\u212a'.lower()))


def ch14():
    H('第 14 章  ReDoS')
    rows = [r'(a+)+$', r'(a|a)*$', r'(a|aa)*$', r'(?:a*)*b', r'(\w+\s?)*$', r'a*a*$', r'\s*\w*\s*x',
            r'.*a.*a.*a', r'.*(?:.*=.*)', r'a+b', r'^a+b', r'[a-z]+@[a-z]+\.com', r'^[a-z]+@[a-z]+\.com$', 'abc']
    for p in rows:
        r1, r2 = analyze_redos(p), analyze_redos(p, search=False)
        # 实测：AST 回溯在失败输入上的步数增长
        if p == '.*a.*a.*a':
            make = lambda n: 'a' + 'b' * n + 'a'          # 只有两个 a：注定失败
        elif p == '.*(?:.*=.*)':
            make = lambda n: 'x' * n                       # Cloudflare 2019：没有 '='
        elif p == '(?:a*)*b':
            make = lambda n: 'a' * n
        elif p == r'\s*\w*\s*x':
            make = lambda n: ' ' * n + '!'
        else:
            make = lambda n: 'a' * n + '!'
        steps = []
        for n in (8, 16):
            b = Backtracker(p, budget=5_000_000)
            try:
                b.search(make(n))
                steps.append(f'{b.steps:,}')
            except StepLimit:
                steps.append('>5,000,000')
        fmt = lambda c: c['class'] + (f"(n^{c['degree']})" if c['class'] == 'polynomial' else '')
        print(f"  {p:24} 搜索:{fmt(r1):18} 锚定:{fmt(r2):18} 步数 n=8:{steps[0]:>9}  n=16:{steps[1]:>11}")


def ch15():
    H('第 15 章  差分模糊测试')
    total = None
    for seed in (1, 2, 3):
        st, _ = fuzz.run(700, 60, seed=seed, verbose=False)
        total = st if total is None else total + st
    for k, v in sorted(total.items()):
        print(f"  {k:48} {v}")
    from . import mutation
    mutation.main(random_pos=False)
    mutation.main(random_pos=True)


def bench():
    H('附：性能对比（Python 实现，单位 ms，仅看相对量级）')
    random.seed(2)
    text = ''.join(random.choice('abcdefghij ') for _ in range(50_000)) + 'needle42'
    for p in [r'needle\d+', r'[a-c]+j', r'(a|b)*c(a|b){3}d', r'needle(\d+)']:
        prog, ng = compile_regex(p)
        r = Regex(p)
        res = r.search(text)
        assert res == pike_search(prog, text), p
        t_pike = timeit(lambda: pike_search(prog, text), 1)
        t_lazy = timeit(lambda: ThreePhase(prog, ng, use_prefilter=False).search(text), 1)
        t_meta = timeit(lambda: r.search(text))
        t_py = timeit(lambda: re.search(p, text))
        print(f"  {p:22} {res}  PikeVM {t_pike * 1000:9.1f}  惰性DFA {t_lazy * 1000:8.1f}  "
              f"元引擎 {t_meta * 1000:7.1f}  Python re {t_py * 1000:6.2f}")


if __name__ == '__main__':
    random.seed(0)
    for f in [ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, ch11, ch12, ch14, ch15, bench]:
        f()
