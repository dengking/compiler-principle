"""第 4 章：Thompson 构造 —— 把 AST 编译成 NFA“程序”。

指令集（沿用 Russ Cox《Regular Expression Matching: the Virtual Machine Approach》）：
    ('char', c) ('any',) ('class', ranges, neg)       消耗一个字符
    ('split', x, y)    分叉，x 的优先级高于 y
    ('jmp', x)         跳转
    ('save', n)        把当前位置写入捕获槽 n
    ('assert', kind)   零宽断言：bol / eol / wordb / nwordb
    ('match',)         匹配成功
"""
from .syntax import parse, features


class Unsupported(Exception):
    """模式用到了自动机引擎无法实现的特性（反向引用、环视、原子组）。"""


MAX_PROG = 100_000


def estimate_size(n):
    """编译前估算指令条数：子树大小 × 重复次数。"""
    k = n[0]
    if k in ('char', 'any', 'class', 'bol', 'eol', 'wordb', 'nwordb'):
        return 1
    if k == 'empty':
        return 0
    if k == 'cat':
        return sum(estimate_size(x) for x in n[1])
    if k == 'alt':
        return estimate_size(n[1]) + estimate_size(n[2]) + 2
    if k in ('star', 'plus', 'quest'):
        return estimate_size(n[1]) + 2
    if k == 'group':
        return estimate_size(n[1]) + 2
    if k == 'repeat':
        _, sub, lo, hi, _ = n
        s = estimate_size(sub)
        return s * lo + (s + 2 if hi is None else (s + 1) * (hi - lo))
    return 1


class Compiler:
    def __init__(self):
        self.prog = []

    def pc(self):
        return len(self.prog)

    def emit(self, *ins):
        self.prog.append(list(ins))
        return len(self.prog) - 1

    def set_split(self, s, prefer, other, greedy):
        """greedy 时优先 prefer，否则优先 other。贪婪与非贪婪的唯一区别就在这里。"""
        self.prog[s][1:3] = [prefer, other] if greedy else [other, prefer]

    def c(self, n):
        k = n[0]
        if k == 'char':
            self.emit('char', n[1])
        elif k == 'any':
            self.emit('any')
        elif k == 'class':
            self.emit('class', n[1], n[2])
        elif k in ('bol', 'eol', 'wordb', 'nwordb'):
            self.emit('assert', k)
        elif k == 'empty':
            pass
        elif k == 'cat':
            for x in n[1]:
                self.c(x)
        elif k == 'group':
            _, sub, idx = n
            self.emit('save', 2 * idx)
            self.c(sub)
            self.emit('save', 2 * idx + 1)
        elif k == 'alt':
            s = self.emit('split', None, None)
            l1 = self.pc()
            self.c(n[1])
            j = self.emit('jmp', None)
            l2 = self.pc()
            self.c(n[2])
            self.prog[s][1:3] = [l1, l2]
            self.prog[j][1] = self.pc()
        elif k == 'quest':
            _, sub, g = n
            s = self.emit('split', None, None)
            body = self.pc()
            self.c(sub)
            self.set_split(s, body, self.pc(), g)
        elif k == 'star':
            _, sub, g = n
            s = self.emit('split', None, None)
            body = self.pc()
            self.c(sub)
            self.emit('jmp', s)
            self.set_split(s, body, self.pc(), g)
        elif k == 'plus':
            _, sub, g = n
            body = self.pc()
            self.c(sub)
            s = self.emit('split', None, None)
            self.set_split(s, body, self.pc(), g)
        elif k == 'repeat':
            _, sub, lo, hi, g = n
            for _ in range(lo):                     # 必选部分：原样复制 lo 份
                self.c(sub)
            if hi is None:                          # {lo,}  →  sub{lo} sub*
                self.c(('star', sub, g))
            else:                                   # {lo,hi} → 嵌套可选 x(x(x)?)?
                splits = []
                for _ in range(hi - lo):
                    s = self.emit('split', None, None)
                    splits.append(s)
                    self.prog[s][1] = self.pc()     # 暂存“继续”分支
                    self.c(sub)
                end = self.pc()
                for s in splits:
                    self.set_split(s, self.prog[s][1], end, g)
        else:
            raise Unsupported(f"automata engines cannot implement {k!r}")


def compile_ast(ast):
    bad = features(ast) & {'backref', 'look', 'atomic'}
    if bad:
        raise Unsupported(f"pattern uses {sorted(bad)}")
    if estimate_size(ast) > MAX_PROG:
        raise Unsupported(f"program would exceed {MAX_PROG} instructions")
    cp = Compiler()
    cp.emit('save', 0)        # 第 0 组 = 整个匹配
    cp.c(ast)
    cp.emit('save', 1)
    cp.emit('match')
    return [tuple(ins) for ins in cp.prog]


def compile_regex(pattern):
    """返回 (prog, ngroups)。"""
    ast, ngroups = parse(pattern)
    return compile_ast(ast), ngroups


def fmt_ins(ins):
    op = ins[0]
    if op == 'class':
        body = ''.join(lo if lo == hi else f'{lo}-{hi}' for lo, hi in ins[1])
        return f"class   [{'^' if ins[2] else ''}{body}]"
    return f"{op:7} " + ' '.join(str(x) for x in ins[1:])


def dump(prog):
    return '\n'.join(f"{i:3}  {fmt_ins(ins)}" for i, ins in enumerate(prog))
