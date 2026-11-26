"""第 11 章：Unicode —— 把码点区间编译成 UTF-8 字节序列的选择（regex-syntax 的 Utf8Sequences 思想）。"""

MAX = 0x10FFFF


def encode(cp):
    return list(chr(cp).encode('utf-8', 'surrogatepass'))


def utf8_sequences(lo, hi):
    """把码点区间 [lo, hi]（自动去掉代理区）切成若干条字节区间序列。
    每条序列形如 [(b1lo, b1hi), (b2lo, b2hi), ...]，它匹配的字节串恰好是
    某个码点子区间的 UTF-8 编码；全部序列的并恰好是 [lo, hi] 的编码。"""
    out, stack = [], [(lo, hi)]
    while stack:
        lo, hi = stack.pop()
        if lo > hi:
            continue
        if lo <= 0xDFFF and hi >= 0xD800:          # 代理区没有合法编码
            stack.append((0xE000, hi))
            stack.append((lo, 0xD7FF))
            continue
        split = False
        for b in (0x7F, 0x7FF, 0xFFFF):            # 1) 按编码长度切开
            if lo <= b < hi:
                stack.append((b + 1, hi))
                stack.append((lo, b))
                split = True
                break
        if split:
            continue
        if hi <= 0x7F:
            out.append([(lo, hi)])
            continue
        for i in range(1, 4):                      # 2) 让每个续字节都覆盖完整的 0x80–0xBF
            m = (1 << (6 * i)) - 1
            if lo & ~m != hi & ~m:
                if lo & m != 0:
                    stack.append(((lo | m) + 1, hi))
                    stack.append((lo, lo | m))
                    split = True
                    break
                if hi & m != m:
                    stack.append((hi & ~m, hi))
                    stack.append((lo, (hi & ~m) - 1))
                    split = True
                    break
        if split:
            continue
        a, b = encode(lo), encode(hi)              # 3) 现在逐字节配对即可
        out.append(list(zip(a, b)))
    return out


def seq_matches(seq, bs):
    return len(seq) == len(bs) and all(lo <= b <= hi for (lo, hi), b in zip(seq, bs))


def fmt_seq(seq):
    return ' '.join(f'[{lo:02X}]' if lo == hi else f'[{lo:02X}-{hi:02X}]' for lo, hi in seq)
