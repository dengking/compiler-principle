"""第 3 章：最简单的引擎 —— 直接在 AST 上做回溯（续延传递风格）。

这是“功能最全、保证最差”的引擎：支持捕获组、贪婪/非贪婪、反向引用、
环视、原子组与占有量词，但最坏情况指数级。steps 计数用于观察灾难性回溯。
"""
import sys

from .syntax import parse, in_class, assert_ok

sys.setrecursionlimit(20000)   # 递归引擎的老问题：深度与文本长度成正比


class StepLimit(Exception):
    pass


class Backtracker:
    def __init__(self, pattern, budget=None, empty_iter='perl'):
        """empty_iter：循环体匹配空串时的处理方式。
        'perl' —— 保留这次空迭代并退出循环（Perl / Python 的行为）
        'fail' —— 让这条路径失败（与 Pike VM 的结果一致）"""
        self.ast, self.ngroups = parse(pattern)
        self.budget = budget
        self.empty_iter = empty_iter
        self.steps = 0

    # ------------------------------------------------------------ 核心
    def m(self, n, i, caps, k):
        """尝试在位置 i 用节点 n 匹配；成功后调用续延 k(j, caps)。
        返回最终结果（捕获元组）或 None。"""
        self.steps += 1
        if self.budget is not None and self.steps > self.budget:
            raise StepLimit(self.steps)
        T = self.text
        t = n[0]
        if t == 'char':
            return k(i + 1, caps) if i < len(T) and T[i] == n[1] else None
        if t == 'any':
            return k(i + 1, caps) if i < len(T) and T[i] != '\n' else None
        if t == 'class':
            ok = i < len(T) and in_class(T[i], n[1]) != n[2]
            return k(i + 1, caps) if ok else None
        if t == 'empty':
            return k(i, caps)
        if t in ('bol', 'eol', 'wordb', 'nwordb'):
            return k(i, caps) if assert_ok(t, T, i) else None
        if t == 'cat':
            items = n[1]

            def go(idx, j, c):
                if idx == len(items):
                    return k(j, c)
                return self.m(items[idx], j, c, lambda j2, c2: go(idx + 1, j2, c2))
            return go(0, i, caps)
        if t == 'alt':                       # 先试左边，失败再试右边：有序选择
            r = self.m(n[1], i, caps, k)
            return r if r is not None else self.m(n[2], i, caps, k)
        if t == 'group':
            idx = n[2]
            c1 = caps[:2 * idx] + (i,) + caps[2 * idx + 1:]
            return self.m(n[1], i, c1,
                          lambda j, c2: k(j, c2[:2 * idx + 1] + (j,) + c2[2 * idx + 2:]))
        if t == 'star':
            return self.rep(n[1], 0, None, n[2], 0, i, caps, k)
        if t == 'plus':
            return self.rep(n[1], 1, None, n[2], 0, i, caps, k)
        if t == 'quest':
            return self.rep(n[1], 0, 1, n[2], 0, i, caps, k)
        if t == 'repeat':
            return self.rep(n[1], n[2], n[3], n[4], 0, i, caps, k)
        if t == 'backref':
            s, e = caps[2 * n[1]], caps[2 * n[1] + 1]
            if s is None or e is None:
                return None                  # 组未参与匹配：Python 视为失败，JS 视为空串
            L = e - s
            return k(i + L, caps) if T.startswith(T[s:e], i) else None
        if t == 'look':
            sub, ahead, neg = n[1], n[2], n[3]
            if ahead:
                r = self.m(sub, i, caps, lambda j, c: c)
            else:                            # 后行断言：枚举起点，要求恰好在 i 结束
                r = None
                for j in range(i, -1, -1):
                    r = self.m(sub, j, caps, lambda e, c: c if e == i else None)
                    if r is not None:
                        break
            if neg:
                return k(i, caps) if r is None else None
            return k(i, r) if r is not None else None   # 环视内的捕获保留下来
        if t == 'atomic':                    # 子表达式只取第一个解，不再回溯进去
            r = self.m(n[1], i, caps, lambda j, c: (j, c))
            return None if r is None else k(r[0], r[1])
        raise ValueError(t)

    def rep(self, sub, lo, hi, greedy, count, i, caps, k):
        def more():
            if hi is not None and count >= hi:
                return None

            def after(j, c):
                if j == i and count >= lo:   # 这次迭代没有前进：空循环
                    return k(j, c) if self.empty_iter == 'perl' else None
                return self.rep(sub, lo, hi, greedy, count + 1, j, c, k)
            return self.m(sub, i, caps, after)

        def stop():
            return k(i, caps) if count >= lo else None

        if greedy:
            r = more()
            return r if r is not None else stop()
        r = stop()
        return r if r is not None else more()

    # ------------------------------------------------------------ 接口
    def match_at(self, text, start):
        self.text = text
        caps = (start,) + (None,) * (2 * self.ngroups + 1)
        return self.m(self.ast, start, caps,
                      lambda j, c: c[:1] + (j,) + c[2:])

    def search(self, text, pos=0):
        """返回 [(start, end), (g1s, g1e), ...] 或 None。"""
        self.steps = 0
        for start in range(pos, len(text) + 1):      # 隐式的 .*? 前缀：逐个起点尝试
            r = self.match_at(text, start)
            if r is not None:
                return [(r[2 * g], r[2 * g + 1]) for g in range(self.ngroups + 1)]
        return None


def bt_search(pattern, text, **kw):
    return Backtracker(pattern, **kw).search(text)
