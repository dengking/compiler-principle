"""第 12 章：性能工程 —— 字面量提取、预过滤、Aho–Corasick、Shift-And 位并行。"""


# ------------------------------------------------------------------ 字面量分析
def exact_literal(prog):
    """模式恰好匹配一个非空的固定字符串时返回该字符串，否则返回 None。"""
    chars = []
    for op in prog:
        k = op[0]
        if k == 'char':
            chars.append(op[1])
        elif k == 'save':
            continue
        elif k == 'match':
            break
        else:
            return None
    return ''.join(chars) or None


def anchored_start(prog):
    """是否每条路径在消耗第一个字符之前都经过了 ^。"""
    stack, seen = [0], set()
    while stack:
        pc = stack.pop()
        if pc in seen:
            continue
        seen.add(pc)
        op = prog[pc]
        k = op[0]
        if k == 'assert' and op[1] == 'bol':
            continue                      # 这条路径已被锚定
        if k == 'jmp':
            stack.append(op[1])
        elif k == 'split':
            stack.extend((op[1], op[2]))
        elif k in ('save', 'assert'):     # 其他断言：继续向后看
            stack.append(pc + 1)
        else:
            return False                  # char/any/class/match：存在未锚定的路径
    return True


def class_chars(op, limit):
    """把小的非取反字符类展开成字符列表；太大或取反时返回 None。"""
    _, ranges, negated = op
    if negated:
        return None
    chars = []
    for lo, hi in ranges:
        for c in range(ord(lo), ord(hi) + 1):
            chars.append(chr(c))
            if len(chars) > limit:
                return None
    return chars


def minimize_literals(lits):
    """如果 a 是 b 的前缀，以 b 开头的地方一定也以 a 开头，所以 b 可以去掉。"""
    keep = []
    for s in sorted(lits, key=len):
        if not any(s.startswith(t) for t in keep):
            keep.append(s)
    return sorted(keep)


def prefix_literals(prog, max_len=8, max_count=16, class_limit=4, budget=2000):
    """返回满足“前缀完备性”的字符串列表：每个匹配都以其中某个字符串开头。
    无法提取（含空串或组合爆炸）时返回 None。"""
    out, seen = set(), set()
    stack = [(0, '')]
    while stack:
        pc, pre = stack.pop()
        if (pc, pre) in seen:             # 同一 pc、同一前缀只处理一次，避免 ε 环
            continue
        seen.add((pc, pre))
        if len(seen) > budget or len(out) > max_count:
            return None                   # 组合爆炸：放弃
        if len(pre) >= max_len:
            out.add(pre)                  # 截断：仍是合法前缀
            continue
        op = prog[pc]
        k = op[0]
        if k == 'char':
            stack.append((pc + 1, pre + op[1]))
        elif k == 'class':
            cs = class_chars(op, class_limit)
            if cs is None:
                out.add(pre)
            else:
                for c in cs:
                    stack.append((pc + 1, pre + c))
        elif k in ('any', 'match'):
            out.add(pre)
        elif k == 'jmp':
            stack.append((op[1], pre))
        elif k == 'split':
            stack.append((op[1], pre))
            stack.append((op[2], pre))
        else:                             # save、assert：不消耗字符（断言跳过只会让集合偏大）
            stack.append((pc + 1, pre))
    if '' in out or not out:
        return None
    return minimize_literals(out)


# ------------------------------------------------------------------ 候选搜索
class Prefilter:
    def __init__(self, lits):
        self.lits = lits

    def find(self, text, pos):
        """返回 pos 之后任一字面量最早出现的位置；没有则返回 -1。"""
        best = -1
        for L in self.lits:
            j = text.find(L, pos, best + len(L) - 1 if best >= 0 else len(text))
            if j >= 0:
                best = j
        return best


class AdaptivePrefilter(Prefilter):
    """运行时统计平均跳跃距离，太短就关闭。关闭后返回 pos 而不是 -1。"""

    def __init__(self, lits, min_avg_skip=16, warmup=32):
        super().__init__(lits)
        self.min_avg_skip, self.warmup = min_avg_skip, warmup
        self.start()

    def start(self):                      # 每次搜索开始时调用
        self.calls, self.skipped, self.enabled = 0, 0, True

    def find(self, text, pos):
        if not self.enabled:
            return pos
        j = super().find(text, pos)
        self.calls += 1
        self.skipped += (len(text) if j < 0 else j) - pos
        if self.calls >= self.warmup and self.skipped < self.min_avg_skip * self.calls:
            self.enabled = False
        return j


class AhoCorasick:
    """多字面量一遍扫描，返回任一字面量最早出现的起点（不是终点）。"""

    def __init__(self, lits):
        self.goto, self.fail, self.out = [{}], [0], [[]]
        for w in lits:
            s = 0
            for ch in w:
                if ch not in self.goto[s]:
                    self.goto.append({})
                    self.fail.append(0)
                    self.out.append([])
                    self.goto[s][ch] = len(self.goto) - 1
                s = self.goto[s][ch]
            self.out[s].append(len(w))
        self.maxlen = max(len(w) for w in lits)
        queue = list(self.goto[0].values())
        while queue:                       # BFS 计算失败链，并沿失败链合并输出
            r = queue.pop(0)
            for ch, s in self.goto[r].items():
                queue.append(s)
                f = self.fail[r]
                while f and ch not in self.goto[f]:
                    f = self.fail[f]
                self.fail[s] = self.goto[f].get(ch, 0) if self.goto[f].get(ch, 0) != s else 0
                self.out[s] = self.out[s] + self.out[self.fail[s]]

    def find(self, text, pos):
        s, best = 0, -1
        for j in range(pos, len(text)):
            ch = text[j]
            while s and ch not in self.goto[s]:
                s = self.fail[s]
            s = self.goto[s].get(ch, 0)
            for L in self.out[s]:          # 报告所有以 j 结尾的字面量
                st = j - L + 1
                if best < 0 or st < best:
                    best = st
            if best >= 0 and j - self.maxlen + 1 >= best:
                return best                # 之后不可能再出现更早的起点
        return best


# ------------------------------------------------------------------ 位并行
def shift_and(pattern_sets, text):
    """Shift-And（Baeza-Yates–Gonnet）：pattern_sets 是每个位置可接受的字符集合。
    状态 D 的第 j 位为 1 表示“模式前 j+1 个位置与以当前字符结尾的文本匹配”。
    返回所有匹配的终点（不含）。"""
    m = len(pattern_sets)
    B = {}
    for j, cs in enumerate(pattern_sets):
        for c in cs:
            B[c] = B.get(c, 0) | (1 << j)
    D, hit, ends = 0, 1 << (m - 1), []
    for i, c in enumerate(text):
        D = ((D << 1) | 1) & B.get(c, 0)
        if D & hit:
            ends.append(i + 1)
    return ends
