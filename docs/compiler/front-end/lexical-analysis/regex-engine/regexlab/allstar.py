"""第 9 章（下）：ANTLR 4 的自适应预测 ALL(*) 教学实现（精简版）。

  文法 → ATN；配置 (p, alt, γ)；closure / reach；
  SLL（栈底通配符 #）+ 每决策一个 DFA 缓存；SLL 冲突 → 全上下文 LL；真二义性选最小备选。
简化：栈用 tuple，不做图结构栈合并；只支持 BNF；决策点只有“规则的多个备选”。"""
import re
from collections import Counter, defaultdict

EOF = 'EOF'
WILDCARD = '#'


class GrammarError(Exception):
    pass


class NoViableAlt(SyntaxError):
    pass


class Grammar:
    _TOK = re.compile(r"//[^\n]*|'(?:\\.|[^'\\])*'|[A-Za-z_]\w*|[:|;]|\S")

    def __init__(self, text):
        self.rules, self.start = {}, None
        toks = [t for t in self._TOK.findall(text) if not t.startswith('//')]
        i = 0
        while i < len(toks):
            name = toks[i]
            if toks[i + 1] != ':':
                raise GrammarError(f"rule {name}: missing ':'")
            i += 2
            alts = [[]]
            while toks[i] != ';':
                if toks[i] == '|':
                    alts.append([])
                else:
                    alts[-1].append(toks[i])
                i += 1
            i += 1
            self.rules[name] = alts
            self.start = self.start or name
        self.check_left_recursion()

    @staticmethod
    def is_terminal(s):
        return s.startswith("'") or s[0].isupper()

    @staticmethod
    def ttype(s):
        return s[1:-1] if s.startswith("'") else s

    def literals(self):
        return {s[1:-1] for alts in self.rules.values() for a in alts for s in a if s.startswith("'")}

    def check_left_recursion(self):
        nullable, changed = set(), True
        while changed:
            changed = False
            for r, alts in self.rules.items():
                if r not in nullable and any(all(not self.is_terminal(s) and s in nullable
                                                 for s in a) for a in alts):
                    nullable.add(r)
                    changed = True
        left = {r: set() for r in self.rules}
        for r, alts in self.rules.items():
            for a in alts:
                for s in a:
                    if self.is_terminal(s):
                        break
                    left[r].add(s)
                    if s not in nullable:
                        break
        color = {}

        def dfs(r, path):
            color[r] = 1
            for n in left[r]:
                if color.get(n) == 1:
                    raise GrammarError("left recursion: " + " -> ".join(path[path.index(n):] + [n]))
                if n not in color:
                    dfs(n, path + [n])
            color[r] = 2
        for r in self.rules:
            if r not in color:
                dfs(r, [r])


class ATN:
    """每条规则：入口 start、出口 stop；第 i 个备选是一条状态链。
    states[s] = [kind, rule, transitions]，transition = (kind, target, label, follow)。"""

    def __init__(self, g):
        self.g, self.states = g, []
        self.rule_start, self.rule_stop, self.alt_path = {}, {}, {}
        self.callers = defaultdict(list)
        for r in g.rules:
            self.rule_start[r] = self.new(r, 'start')
            self.rule_stop[r] = self.new(r, 'stop')
        for r, alts in g.rules.items():
            for i, alt in enumerate(alts, 1):
                cur = self.new(r, 'basic')
                self.states[self.rule_start[r]][2].append(('eps', cur, None, None))
                path = [cur]
                for sym in alt:
                    nxt = self.new(r, 'basic')
                    if g.is_terminal(sym):
                        self.states[cur][2].append(('atom', nxt, g.ttype(sym), None))
                    else:
                        self.states[cur][2].append(('rule', self.rule_start[sym], sym, nxt))
                        self.callers[sym].append(nxt)
                    path.append(nxt)
                    cur = nxt
                self.states[cur][2].append(('eps', self.rule_stop[r], None, None))
                self.alt_path[(r, i)] = path
        # 返回点之后只剩一条 ε 到出口：尾调用，预测时不必压栈
        self.tail = {s for s, (k, r, ts) in enumerate(self.states)
                     if k == 'basic' and len(ts) == 1 and ts[0][0] == 'eps'
                     and ts[0][1] == self.rule_stop[r]}

    def new(self, rule, kind):
        self.states.append([kind, rule, []])
        return len(self.states) - 1


def fmt_stack(st):
    return 'ε' if not st else ' '.join(x if x == WILDCARD else f'p{x}' for x in st)


def fmt_configs(cs):
    return '{' + ', '.join(f'(p{s},{a},[{fmt_stack(st)}])'
                           for s, a, st in sorted(cs, key=lambda c: (c[1], c[0], str(c[2])))) + '}'


class Simulator:
    def __init__(self, atn):
        self.atn = atn

    def start_configs(self, rule, stack):
        out, busy = set(), set()
        for i in range(1, len(self.atn.g.rules[rule]) + 1):
            self.closure((self.atn.alt_path[(rule, i)][0], i, stack), out, busy)
        return frozenset(out)

    def closure(self, c, out, busy):
        if c in busy:
            return
        busy.add(c)
        s, alt, stack = c
        kind, rule, ts = self.atn.states[s]
        if kind == 'stop':
            if stack and stack[0] == WILDCARD:     # SLL：调用者未知 → 所有调用点
                if rule == self.atn.g.start:
                    out.add(c)
                for f in self.atn.callers[rule]:
                    self.closure((f, alt, stack), out, busy)
            elif not stack:
                out.add(c)                         # LL：真实调用栈已空
            else:
                self.closure((stack[0], alt, stack[1:]), out, busy)   # 弹栈返回
            return
        matchable = False
        for k, t, label, follow in ts:
            if k == 'eps':
                self.closure((t, alt, stack), out, busy)
            elif k == 'rule':
                push = () if follow in self.atn.tail else (follow,)
                self.closure((t, alt, push + stack), out, busy)        # 压栈调用
            else:
                matchable = True
        if matchable:
            out.add(c)

    def reach(self, configs, tt):
        out, busy = set(), set()
        for s, alt, stack in configs:
            for k, t, label, _ in self.atn.states[s][2]:
                if k == 'atom' and label == tt:
                    self.closure((t, alt, stack), out, busy)
        return frozenset(out)

    def sll_should_stop(self, cs):
        if all(self.atn.states[s][0] == 'stop' for s, _, _ in cs):
            return True
        by_ctx, by_state = defaultdict(set), defaultdict(set)
        for s, a, st in cs:
            by_ctx[(s, st)].add(a)
            by_state[s].add(a)
        return (any(len(x) > 1 for x in by_ctx.values())
                and not any(len(x) == 1 for x in by_state.values()))


class DFAState:
    def __init__(self, i, configs, sim):
        self.id, self.configs, self.edges = i, configs, {}
        alts = {a for _, a, _ in configs}
        self.prediction = next(iter(alts)) if len(alts) == 1 else None
        self.requires_full_ctx = self.prediction is None and sim.sll_should_stop(configs)


class Cache:
    """每个决策一个 DFA，跨解析器实例共享（ANTLR 的 decisionToDFA）。"""

    def __init__(self, atn):
        self.atn, self.sim = atn, Simulator(atn)
        self.dfa = {r: {} for r, alts in atn.g.rules.items() if len(alts) > 1}
        self.s0 = {}
        self.stats = Counter()

    def state(self, rule, configs):
        d = self.dfa[rule]
        if configs not in d:
            d[configs] = DFAState(len(d), configs, self.sim)
        return d[configs]


class Parser:
    def __init__(self, cache, tokens, trace=False):
        self.c, self.atn, self.sim = cache, cache.atn, cache.sim
        self.g, self.tokens, self.i = self.atn.g, tokens, 0
        self.call_stack, self.trace, self.ambiguities = [], trace, []

    def la(self, k):
        return self.tokens[min(k, len(self.tokens) - 1)]

    def log(self, m):
        if self.trace:
            print(m)

    def parse(self):
        return self.rule(self.g.start)

    def rule(self, r):
        alts = self.g.rules[r]
        alt = 1 if len(alts) == 1 else self.adaptive_predict(r)
        node, path = [f'{r}#{alt}'], self.atn.alt_path[(r, alt)]
        for k, sym in enumerate(alts[alt - 1]):
            if self.g.is_terminal(sym):
                tok = self.la(self.i)
                if tok[0] != self.g.ttype(sym):
                    raise SyntaxError(f"expected {sym}, got {tok[1]!r}")
                self.i += 1
                node.append(tok[1])
            else:
                self.call_stack.append(path[k + 1])
                node.append(self.rule(sym))
                self.call_stack.pop()
        return node

    def adaptive_predict(self, r):
        st, start = self.c.stats, self.i
        if r not in self.c.s0:
            self.c.s0[r] = self.c.state(r, self.sim.start_configs(r, (WILDCARD,)))
        d, i = self.c.s0[r], start
        self.log(f"[SLL] 决策 {r} @ {self.la(start)[1]!r}")
        while True:
            if d.requires_full_ctx:
                st['sll_conflict'] += 1
                self.log(f"  D{d.id} 是 SLL 冲突状态 → 全上下文 LL")
                return self.ll_predict(r, start)
            if d.prediction is not None:
                st['sll_ok'] += 1
                self.log(f"  SLL 预测 alt {d.prediction}（向前看 {i - start} 个记号）")
                return d.prediction
            t = self.la(i)[0]
            nxt = d.edges.get(t)
            if nxt is None:
                st['atn_steps'] += 1
                R = self.sim.reach(d.configs, t)
                if not R:
                    raise NoViableAlt(f"no viable alternative in {r} at {self.la(i)[1]!r}")
                nxt = d.edges[t] = self.c.state(r, R)
                self.log(f"  ATN 模拟 D{d.id} --{t!r}--> D{nxt.id} {fmt_configs(R)}")
            else:
                st['dfa_hits'] += 1
                self.log(f"  DFA 命中 D{d.id} --{t!r}--> D{nxt.id}")
            d, i = nxt, i + 1

    def ll_predict(self, r, start):
        self.c.stats['ll_predict'] += 1
        gamma0 = tuple(reversed(self.call_stack))
        cs, i = self.sim.start_configs(r, gamma0), start
        self.log(f"  [LL] γ0=[{fmt_stack(gamma0)}] {fmt_configs(cs)}")
        while True:
            t = self.la(i)[0]
            cs = self.sim.reach(cs, t)
            self.log(f"  [LL] --{t!r}--> {fmt_configs(cs)}")
            if not cs:
                raise NoViableAlt(f"no viable alternative in {r} (full context)")
            alts = {a for _, a, _ in cs}
            if len(alts) == 1:
                return alts.pop()
            groups = defaultdict(set)
            for s, a, stck in cs:
                groups[(s, stck)].add(a)
            mins = {min(x) for x in groups.values()}
            if len(mins) == 1:                     # 无论往后看多远都会选它
                self.ambiguities.append((r, sorted(alts)))
                self.log(f"  真二义性 {sorted(alts)} → 选最小备选 {min(mins)}")
                return mins.pop()
            i += 1


def tokenize(g, text):
    lits = sorted(g.literals(), key=len, reverse=True)
    out, pos = [], 0
    while pos < len(text):
        if text[pos].isspace():
            pos += 1
            continue
        m = re.compile(r'[A-Za-z_]\w*|\d+').match(text, pos)
        lit = next((l for l in lits if text.startswith(l, pos)), None)
        if m and (lit is None or len(m.group()) > len(lit) or
                  (len(m.group()) == len(lit) and lit not in g.literals())):
            w = m.group()
            out.append(('INT' if w.isdigit() else 'ID', w))
            pos = m.end()
        elif lit is not None:
            out.append((lit, lit))
            pos += len(lit)
        else:
            raise SyntaxError(f"bad char {text[pos]!r}")
    out.append((EOF, '<EOF>'))
    return out


def build(grammar_text):
    g = Grammar(grammar_text)
    return g, Cache(ATN(g))


def parse(g, cache, text, trace=False):
    p = Parser(cache, tokenize(g, text), trace)
    return p.parse(), p


G_CTX = """
s : 'x' b EOF | 'y' c EOF ;
b : a 'a' ;
c : a 'b' 'a' ;
a : 'b' | ;
"""

G_DECL = """
prog : decl prog | EOF ;
decl : mods 'int' ID ';' | mods ID ID ';' ;
mods : 'unsigned' mods | ;
"""
