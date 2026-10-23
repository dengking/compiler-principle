"""第 5 章：Pike VM 与有界回溯（BitState）—— 两个线性时间、支持捕获组的引擎。"""
from .syntax import in_class, assert_ok


def consumes(op, ch):
    """消耗型指令能否吃下字符 ch（ch 为 None 表示文本结束）。"""
    if ch is None:
        return False
    k = op[0]
    if k == 'char':
        return ch == op[1]
    if k == 'any':
        return ch != '\n'
    if k == 'class':
        return in_class(ch, op[1]) != op[2]
    return False


def pike_vm(prog, ngroups, text, pos=0, anchored=False, end=None):
    """Pike VM。返回捕获槽元组或 None。
    end 不为 None 时：从 pos 锚定开始，只读到 end，并且只接受恰好在 end 处的匹配
    （用于三段式搜索的第三段：在已知区间内求捕获组）。"""
    n = len(text)
    limit = n if end is None else end
    nslots = 2 * (ngroups + 1)
    seen = [-1] * len(prog)            # seen[pc] == 位置戳，免去每步清空
    matched = None
    if end is not None:
        anchored = True

    def add(lst, pc, caps, at):
        """把线程及其 ε 闭包按优先级顺序加入 lst（显式栈，不递归）。"""
        stack = [(pc, caps)]
        while stack:
            pc, caps = stack.pop()
            if seen[pc] == at:
                continue
            seen[pc] = at
            op = prog[pc]
            k = op[0]
            if k == 'jmp':
                stack.append((op[1], caps))
            elif k == 'split':
                stack.append((op[2], caps))     # 后压入的先弹出，
                stack.append((op[1], caps))     # 所以 op[1] 优先
            elif k == 'save':
                if op[1] < nslots:              # 只追踪调用者需要的槽
                    c = list(caps)
                    c[op[1]] = at
                    caps = tuple(c)
                stack.append((pc + 1, caps))
            elif k == 'assert':
                if assert_ok(op[1], text, at):
                    stack.append((pc + 1, caps))
            else:                               # char / any / class / match
                lst.append((pc, caps))

    clist = []
    for at in range(pos, limit + 1):
        # 尚未找到匹配时，在每个位置以最低优先级启动一个新线程（隐式的 .*? 前缀）
        if matched is None and (not anchored or at == pos):
            add(clist, 0, (None,) * nslots, at)
        if not clist and (matched is not None or anchored):
            break
        ch = text[at] if at < limit else None
        nlist = []
        for pc, caps in clist:
            op = prog[pc]
            if op[0] == 'match':
                if end is not None and at != end:
                    continue                    # 区间模式：提前到达的匹配优先级必然更低，丢弃
                matched = caps
                break                           # 截断：丢弃更低优先级的线程
            if consumes(op, ch):
                add(nlist, pc + 1, caps, at + 1)
        clist = nlist
    return matched


def spans(caps, ngroups):
    return [(caps[2 * g], caps[2 * g + 1]) for g in range(ngroups + 1)]


def pike_search(prog, text, pos=0):
    caps = pike_vm(prog, 0, text, pos)          # 只要整体匹配：只追踪槽 0、1
    return None if caps is None else (caps[0], caps[1])


def pike_captures(prog, ngroups, text, s, e):
    caps = pike_vm(prog, ngroups, text, s, end=e)
    return None if caps is None else spans(caps, ngroups)


def pike_finditer(prog, text):
    """Rust 约定：紧贴上一个匹配终点的空匹配被跳过。"""
    pos, last_end = 0, -1
    while pos <= len(text):
        m = pike_search(prog, text, pos)
        if m is None:
            return
        s, e = m
        if s == e == last_end:
            pos = e + 1
            continue
        yield m
        last_end = e
        pos = e if e > s else e + 1


# ------------------------------------------------------------------ 有界回溯
class StepLimit(Exception):
    pass


def backtrack_prog(prog, ngroups, text, pos=0, memo=True, budget=None,
                   anchored=False, end=None):
    """在编译后的程序上做显式栈回溯。memo=True 即 RE2 的 BitState /
    Rust 的 BoundedBacktracker：visited 位图让每个 (pc, 位置) 至多被访问一次。
    返回 (捕获槽元组或 None, 步数)。"""
    n = len(text)
    limit = n if end is None else end
    if end is not None:
        anchored = True
    nslots = 2 * (ngroups + 1)
    visited = bytearray(len(prog) * (limit + 1)) if memo else None
    steps = 0
    starts = [pos] if anchored else range(pos, limit + 1)
    for start in starts:
        stack = [(0, start, (None,) * nslots)]
        while stack:
            pc, at, caps = stack.pop()
            while True:                         # 沿一条路径一直走，直到失败
                steps += 1
                if budget is not None and steps > budget:
                    raise StepLimit(steps)
                if visited is not None:
                    key = pc * (limit + 1) + at
                    if visited[key]:
                        break                   # (pc, at) 已试过且失败
                    visited[key] = 1
                op = prog[pc]
                k = op[0]
                if k in ('char', 'any', 'class'):
                    if at < limit and consumes(op, text[at]):
                        pc += 1
                        at += 1
                        continue
                    break
                if k == 'split':
                    stack.append((op[2], at, caps))   # 低优先级分支留待回溯
                    pc = op[1]
                    continue
                if k == 'jmp':
                    pc = op[1]
                    continue
                if k == 'save':
                    if op[1] < nslots:
                        c = list(caps)
                        c[op[1]] = at
                        caps = tuple(c)
                    pc += 1
                    continue
                if k == 'assert':
                    if assert_ok(op[1], text, at):
                        pc += 1
                        continue
                    break
                if k == 'match':
                    if end is not None and at != end:
                        break
                    return caps, steps
    return None, steps


def backtrack_captures(prog, ngroups, text, s, e):
    caps, _ = backtrack_prog(prog, ngroups, text, s, end=e)
    return None if caps is None else spans(caps, ngroups)
