"""第 14 章：ReDoS 静态检测 —— 在无 ε 的 Glushkov NFA 上找指数歧义（EDA）与多项式歧义（IDA）。

  EDA：存在状态 q，从 q 出发有两条不同路径读同一个串回到 q          → 回溯最坏指数级
  IDA：存在 p≠q，p→p、p→q、q→q 三条路径读同一个串                  → 回溯最坏多项式级
（Weideman, van der Merwe, Berglund, Watson, 2016 的判定思路；这里只做教学版。）
注意：分析的是回溯引擎实际遍历的结构（Thompson 程序），零宽断言按 ε 处理（过近似）。"""
from functools import lru_cache

from .syntax import parse
from .compiler import compile_ast
from .literals import anchored_start
from .direct import CSet


def common(*sets):
    """若干 CSet 是否有公共字符。"""
    cuts = {0}
    for s in sets:
        cuts.update(s.cuts())
    return any(all(chr(c) in s for s in sets) for c in cuts)


class NFA:
    """从 Thompson 程序做 ε 消除，但**保留 ε 路径的条数**：同一对状态之间若有两条不同的
    ε 路径，就记为重数 2 的平行边。(a*)* 的歧义正藏在这里——Glushkov 构造会把它抹掉。"""

    def __init__(self, pattern, search=True):
        ast, _ = parse(pattern)
        prog = compile_ast(ast)
        if search and not anchored_start(prog):     # 回溯式搜索 = 在每个起点重试 ≈ 前面加 .*
            prog = compile_ast(('cat', [('star', ('any',), True), ast]))
        cons = [pc for pc, op in enumerate(prog) if op[0] in ('char', 'any', 'class')]
        self.ids = {pc: i + 1 for i, pc in enumerate(cons)}   # 状态 0 为初始
        self.n = len(cons) + 1
        self.label = [None] + [to_cset(prog[pc]) for pc in cons]
        self.mult = [self.eps_targets(prog, 0)] + [self.eps_targets(prog, pc + 1) for pc in cons]
        self.succ = [sorted(m) for m in self.mult]

    def eps_targets(self, prog, pc):
        """枚举从 pc 出发的 ε 路径，统计到达每个消耗型指令的路径条数。
        每条指令在一条路径上最多经过两次：允许“上一轮迭代刚结束、新一轮迭代开始”
        （(a*)* 的外层循环正是这样重入内层 split 的），又保证枚举有限。"""
        count = {}

        def walk(pc, on_path):
            op = prog[pc]
            k = op[0]
            if k in ('char', 'any', 'class'):
                q = self.ids[pc]
                count[q] = count.get(q, 0) + 1
                return
            if k == 'match' or on_path.count(pc) >= 2:
                return
            on_path = on_path + (pc,)
            if k == 'jmp':
                walk(op[1], on_path)
            elif k == 'split':
                walk(op[1], on_path)
                walk(op[2], on_path)
            else:                                    # save / assert：当作 ε
                walk(pc + 1, on_path)
        walk(pc, ())
        return count

    @lru_cache(maxsize=None)
    def can(self, *qs):
        return common(*(self.label[q] for q in qs))


def to_cset(op):
    if op[0] == 'char':
        return CSet([(op[1], op[1])])
    if op[0] == 'any':
        return CSet([('\n', '\n')], neg=True)
    return CSet(op[1], op[2])


def sccs(nodes, succ):
    """Tarjan 强连通分量（迭代版）。"""
    index, low, on, stack, out, counter = {}, {}, set(), [], [], [0]
    for root in nodes:
        if root in index:
            continue
        work = [(root, iter(succ(root)))]
        index[root] = low[root] = counter[0]
        counter[0] += 1
        stack.append(root)
        on.add(root)
        while work:
            v, it = work[-1]
            advanced = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = counter[0]
                    counter[0] += 1
                    stack.append(w)
                    on.add(w)
                    work.append((w, iter(succ(w))))
                    advanced = True
                    break
                if w in on:
                    low[v] = min(low[v], index[w])
            if advanced:
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[v])
            if low[v] == index[v]:
                comp = []
                while True:
                    w = stack.pop()
                    on.discard(w)
                    comp.append(w)
                    if w == v:
                        break
                out.append(comp)
    return out


def reachable(start, succ):
    seen, stack = {start}, [start]
    while stack:
        v = stack.pop()
        for w in succ(v):
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return seen


def analyze_redos(pattern, search=True):
    a = NFA(pattern, search)

    def succ2(v):
        u, w = v
        return [(x, y) for x in a.succ[u] for y in a.succ[w] if a.can(x, y)]

    # EDA：某个 SCC 同时含对角点 (q,q) 与非对角点 (r,s)
    nodes = reachable((0, 0), succ2)
    for comp in sccs(sorted(nodes), succ2):
        cs = set(comp)
        diag = [v for v in comp if v[0] == v[1]]
        off = [v for v in comp if v[0] != v[1]]
        parallel = [(u, x) for (u, _) in diag for x in a.succ[u]
                    if a.mult[u][x] > 1 and (x, x) in cs]
        if diag and (off or parallel):
            return {'class': 'exponential', 'witness_state': diag[0][0]}

    # IDA：(p,p,q) ⇝ (p,q,q)
    def succ3(v):
        x, y, z = v
        return [(i, j, k) for i in a.succ[x] for j in a.succ[y] for k in a.succ[z]
                if a.can(i, j, k)]

    live = {u for u, _ in nodes}
    ida = set()
    for p in live:
        for q in live:
            if p != q and (p, q, q) in reachable((p, p, q), succ3):
                ida.add((p, q))
    # 多项式次数 = IDA 关系上最长链的结点数（迭代松弛，最多 |Q| 轮）
    deg = {p: 1 for p in live}
    for _ in range(len(live)):
        changed = False
        for p, q in ida:
            if deg[p] < deg[q] + 1:
                deg[p] = deg[q] + 1
                changed = True
        if not changed:
            break
    degree = max(deg.values()) if ida else 1
    return {'class': 'polynomial' if degree > 1 else 'linear', 'degree': degree}
