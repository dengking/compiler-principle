"""第 15 章：变异测试 —— 故意往引擎里注入错误，看差分模糊测试能否发现。

运行：python3 -m regexlab.mutation
"""
import sys

from . import fuzz
from . import dfa as dfa_mod
from . import literals as lit_mod
from . import pikevm as pike_mod


def patch(name, new):
    """把所有 regexlab 模块里名为 name 的同一对象替换成 new，返回恢复函数。"""
    saved = []
    for mname, m in list(sys.modules.items()):
        if mname.startswith('regexlab') and m is not None and hasattr(m, name):
            saved.append((m, getattr(m, name)))
            setattr(m, name, new)

    def restore():
        for m, old in saved:
            setattr(m, name, old)
    return restore


def mut_reverse_no_swap():
    orig = dfa_mod.reverse_prog

    def bad(prog):
        rev = orig(prog)
        flip = {'bol': 'eol', 'eol': 'bol'}
        return [('assert', flip[op[1]]) if op[0] == 'assert' and op[1] in flip else op for op in rev]
    return patch('reverse_prog', bad)


def mut_inject_after_match():
    orig = dfa_mod.LazyDFA.compute

    def bad(self, key, rep):
        S, matched = key
        nxt = dfa_mod.step(self.prog, S, rep)
        inject = not self.anchored                   # 错误：找到匹配后仍继续注入
        T = self.closure(nxt + [0] if inject else nxt, False, False)
        return (T, self.flag(matched, T))
    dfa_mod.LazyDFA.compute = bad
    return lambda: setattr(dfa_mod.LazyDFA, 'compute', orig)


def mut_keep_longer_literal():
    def bad(lits):
        keep = []
        for s in sorted(lits, key=len, reverse=True):  # 错误：保留较长的字面量
            if not any(t.startswith(s) for t in keep):
                keep.append(s)
        return sorted(keep)
    return patch('minimize_literals', bad)


def mut_anchored_on_eol():
    def bad(prog):
        stack, seen = [0], set()
        while stack:
            pc = stack.pop()
            if pc in seen:
                continue
            seen.add(pc)
            op = prog[pc]
            k = op[0]
            if k == 'assert':                          # 错误：把 $ 也当作起始锚点
                continue
            if k == 'jmp':
                stack.append(op[1])
            elif k == 'split':
                stack.extend((op[1], op[2]))
            elif k == 'save':
                stack.append(pc + 1)
            else:
                return False
        return True
    return patch('anchored_start', bad)


def mut_prefilter_end_bound():
    orig = lit_mod.Prefilter.find

    def bad(self, text, pos):
        best = -1
        for L in self.lits:
            j = text.find(L, pos, best if best >= 0 else len(text))   # 错误的边界
            if j >= 0:
                best = j
        return best
    lit_mod.Prefilter.find = bad
    return lambda: setattr(lit_mod.Prefilter, 'find', orig)


MUTANTS = [
    ('reverse_prog 不交换 ^ 与 $', mut_reverse_no_swap),
    ('惰性 DFA 找到匹配后仍注入新线程', mut_inject_after_match),
    ('minimize_literals 保留较长的字面量', mut_keep_longer_literal),
    ('anchored_start 把 $ 当作起始锚点', mut_anchored_on_eol),
    ('Prefilter.find 的搜索上界写成 best', mut_prefilter_end_bound),
]


def main(rounds=300, seed=11, random_pos=True):
    print(f"—— 差分测试{'包含' if random_pos else '不含'}随机起点 pos 的检查 ——")
    for name, mk in MUTANTS:
        restore = mk()
        try:
            st, diffs = fuzz.run(rounds, 60, seed=seed, verbose=False, random_pos=random_pos)
        finally:
            restore()
        found = {k: v for k, v in st.items() if k.startswith('diff')}
        first = diffs[0] if diffs else None
        print(f"{name:34} {'发现' if found else '未发现'}  {found}")
        if first:
            print(f"{'':34} 首个反例: 检查项={first[0]!r} 模式={first[1]!r} 文本={first[2]!r} "
                  f"得到={first[3]} 期望={first[4]}")


if __name__ == '__main__':
    main(random_pos=False)
    main(random_pos=True)
