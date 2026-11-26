#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mini_allstar.py —— ANTLR4 ALL(*)（Adaptive LL(*)）预测算法的教学版 Python 复现

只依赖标准库，运行：  python3 mini_allstar.py

覆盖内容（与技术文档章节一一对应）：
  1. 文法文本解析（ANTLR 风格 BNF 子集）+ 左递归检测
  2. 文法 → ATN（Augmented Transition Network，增强转移网络）
  3. ATN 配置 (p, i, γ)、closure、move
  4. SLL 预测 + 按决策缓存的 DFA（栈底通配符 #）
  5. SLL 冲突 → 全上下文 LL 回退
  6. 真二义性检测（报告并选择最小编号备选）
  7. 由 adaptive_predict 驱动的递归下降解释器，输出语法树
  8. 左递归改写后的优先级爬升（precedence climbing + 语义谓词 precpred）

与真实 ANTLR4 runtime 的主要差异（为了可读性做的简化）：
  - 栈 γ 用 Python tuple 表示，没有做图结构栈（GSS / PredictionContext）合并；
  - 只支持 BNF（无 EBNF 的 ? * +），子规则需要写成辅助规则；
  - 决策点只有“规则的多个备选”这一种（ANTLR 中子规则、循环也各是一个决策点）；
  - 通用解释器不支持语义谓词，谓词只在第 8 部分的表达式解析器中演示。
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

EOF = "EOF"
WILDCARD = "#"  # SLL 模式下的栈底通配符：表示“调用者未知，任何调用者都可能”


class GrammarError(Exception):
    pass


# =====================================================================
# 1. 文法
# =====================================================================
class Grammar:
    """
    解析 ANTLR 风格的 BNF 子集：

        rule : sym sym ...
             | sym ...
             |              // 空备选 ε
             ;

    符号约定：'xxx' 为字面量记号；大写开头（ID、INT、EOF）为记号类型；小写开头为非终结符。
    第一条规则为起始规则。
    """

    _TOKEN_RE = re.compile(r"//[^\n]*|'(?:\\.|[^'\\])*'|[A-Za-z_]\w*|[:|;]|\S")

    def __init__(self, text: str):
        self.rules: Dict[str, List[List[str]]] = {}
        self.start: Optional[str] = None
        toks = [t for t in self._TOKEN_RE.findall(text) if not t.startswith("//")]
        i = 0
        while i < len(toks):
            name = toks[i]
            if i + 1 >= len(toks) or toks[i + 1] != ":":
                raise GrammarError(f"规则 {name} 后缺少 ':'")
            i += 2
            alts: List[List[str]] = [[]]
            while i < len(toks) and toks[i] != ";":
                if toks[i] == "|":
                    alts.append([])
                else:
                    alts[-1].append(toks[i])
                i += 1
            if i >= len(toks):
                raise GrammarError(f"规则 {name} 缺少结尾 ';'")
            i += 1
            self.rules[name] = alts
            self.start = self.start or name
        self._check_undefined()
        self._check_left_recursion()

    # ---------- 符号工具 ----------
    @staticmethod
    def is_terminal(sym: str) -> bool:
        return sym.startswith("'") or sym[0].isupper()

    @staticmethod
    def token_type(sym: str) -> str:
        return sym[1:-1] if sym.startswith("'") else sym

    def literals(self) -> Set[str]:
        return {s[1:-1] for alts in self.rules.values() for alt in alts for s in alt if s.startswith("'")}

    # ---------- 静态检查 ----------
    def _check_undefined(self):
        for r, alts in self.rules.items():
            for alt in alts:
                for s in alt:
                    if not self.is_terminal(s) and s not in self.rules:
                        raise GrammarError(f"规则 {r} 引用了未定义的规则 {s}")

    def nullable(self) -> Set[str]:
        """不动点迭代求可推导出 ε 的非终结符集合。"""
        result: Set[str] = set()
        changed = True
        while changed:
            changed = False
            for r, alts in self.rules.items():
                if r in result:
                    continue
                if any(all(not self.is_terminal(s) and s in result for s in alt) for alt in alts):
                    result.add(r)
                    changed = True
        return result

    def _check_left_recursion(self):
        """
        自顶向下的预测会在左递归上无限下降（closure 里栈无限增长）。
        ANTLR4 会把“直接左递归”自动改写（见第 8 部分）；间接左递归则直接报错。
        这里统一检测并报错。
        """
        nullable = self.nullable()
        left: Dict[str, Set[str]] = {r: set() for r in self.rules}
        for r, alts in self.rules.items():
            for alt in alts:
                for s in alt:
                    if self.is_terminal(s):
                        break
                    left[r].add(s)
                    if s not in nullable:
                        break
        color: Dict[str, int] = {}

        def dfs(r: str, path: List[str]):
            color[r] = 1
            for n in left[r]:
                if color.get(n) == 1:
                    cycle = path[path.index(n):] + [n]
                    raise GrammarError("检测到左递归: " + " -> ".join(cycle))
                if n not in color:
                    dfs(n, path + [n])
            color[r] = 2

        for r in self.rules:
            if r not in color:
                dfs(r, [r])


# =====================================================================
# 词法
# =====================================================================
@dataclass(frozen=True)
class Token:
    type: str
    text: str
    pos: int

    def __repr__(self):
        return repr(self.text)


class Lexer:
    """最长匹配；长度相同时字面量（关键字）优先于正则记号。"""

    def __init__(self, literals: Set[str], patterns: Dict[str, str]):
        self.literals = sorted(literals, key=len, reverse=True)
        self.patterns = [(name, re.compile(p)) for name, p in patterns.items()]

    def tokenize(self, text: str) -> List[Token]:
        toks, pos = [], 0
        while pos < len(text):
            if text[pos].isspace():
                pos += 1
                continue
            cands = []
            for lit in self.literals:
                if text.startswith(lit, pos):
                    cands.append((len(lit), 1, lit, lit))
            for name, rx in self.patterns:
                m = rx.match(text, pos)
                if m and m.end() > pos:
                    cands.append((m.end() - pos, 0, name, m.group()))
            if not cands:
                raise SyntaxError(f"无法识别的字符 {text[pos]!r}（位置 {pos}）")
            length, _, ttype, lexeme = max(cands)
            toks.append(Token(ttype, lexeme, pos))
            pos += length
        toks.append(Token(EOF, "<EOF>", pos))
        return toks


DEFAULT_PATTERNS = {"ID": r"[A-Za-z_]\w*", "INT": r"\d+"}


# =====================================================================
# 2. ATN
# =====================================================================
@dataclass(eq=False)
class ATNState:
    id: int
    rule: str
    kind: str  # 'start' | 'stop' | 'basic'
    transitions: List["Transition"] = field(default_factory=list)
    is_tail: bool = False  # 规则调用的返回点是否紧接着就是规则结束（尾调用）

    def __repr__(self):
        return f"p{self.id}"


@dataclass(eq=False)
class Transition:
    kind: str  # 'eps' | 'atom' | 'rule'
    target: ATNState
    label: Optional[str] = None  # atom: 记号类型；rule: 被调用的规则名
    follow: Optional[ATNState] = None  # rule: 被调用规则返回后继续的状态


class ATN:
    """
    构造规则（与 ANTLR4 论文一致）：
      - 每条规则 A 有入口 p_A 与出口 p'_A；
      - 第 i 个备选：p_A --ε--> p_{A,i} --X1--> ... --Xm--> q --ε--> p'_A；
      - 终结符 a 生成 atom 边；非终结符 B 生成 rule 边：跳到 p_B，并记录返回点 follow。
    """

    def __init__(self, g: Grammar):
        self.g = g
        self.states: List[ATNState] = []
        self.rule_start: Dict[str, ATNState] = {}
        self.rule_stop: Dict[str, ATNState] = {}
        self.alt_path: Dict[Tuple[str, int], List[ATNState]] = {}
        self.callers: Dict[str, List[ATNState]] = defaultdict(list)  # 规则 -> 所有调用点的返回状态

        for r in g.rules:
            self.rule_start[r] = self._new(r, "start")
            self.rule_stop[r] = self._new(r, "stop")
        for r, alts in g.rules.items():
            for i, alt in enumerate(alts, 1):
                cur = self._new(r, "basic")
                self.rule_start[r].transitions.append(Transition("eps", cur))
                path = [cur]
                for sym in alt:
                    nxt = self._new(r, "basic")
                    if g.is_terminal(sym):
                        cur.transitions.append(Transition("atom", nxt, g.token_type(sym)))
                    else:
                        cur.transitions.append(Transition("rule", self.rule_start[sym], sym, nxt))
                        self.callers[sym].append(nxt)
                    path.append(nxt)
                    cur = nxt
                cur.transitions.append(Transition("eps", self.rule_stop[r]))
                self.alt_path[(r, i)] = path
        # 返回点之后只剩一条 ε 到本规则出口 → 尾调用，预测时无需压栈（等价于 ANTLR 中用 EBNF 循环代替右递归）
        for s in self.states:
            if s.kind == "basic" and len(s.transitions) == 1:
                t = s.transitions[0]
                s.is_tail = t.kind == "eps" and t.target is self.rule_stop[s.rule]

    def _new(self, rule: str, kind: str) -> ATNState:
        s = ATNState(len(self.states), rule, kind)
        self.states.append(s)
        return s

    def dump(self) -> str:
        lines = []
        for r in self.g.rules:
            lines.append(f"规则 {r}: 入口 {self.rule_start[r]}  出口 {self.rule_stop[r]}")
            for s in self.states:
                if s.rule != r:
                    continue
                for t in s.transitions:
                    if t.kind == "eps":
                        lines.append(f"    {s} --ε--> {t.target}")
                    elif t.kind == "atom":
                        lines.append(f"    {s} --'{t.label}'--> {t.target}")
                    else:
                        lines.append(f"    {s} --{t.label}--> {t.target}   (调用 {t.label}，返回到 {t.follow})")
        return "\n".join(lines)


# =====================================================================
# 3. ATN 配置、closure、move
# =====================================================================
Stack = Tuple  # 栈顶在下标 0；元素为状态编号或 WILDCARD
Config = Tuple[int, int, Stack]  # (状态 p, 预测的备选 i, 调用栈 γ)


def fmt_stack(stack: Stack) -> str:
    if not stack:
        return "ε"
    return " ".join(x if x == WILDCARD else f"p{x}" for x in stack)


def fmt_configs(configs) -> str:
    items = sorted(configs, key=lambda c: (c[1], c[0], str(c[2])))
    return "{" + ", ".join(f"(p{s},{a},[{fmt_stack(st)}])" for s, a, st in items) + "}"


def alts_of(configs) -> Set[int]:
    return {c[1] for c in configs}


def unique_alt(configs) -> Optional[int]:
    alts = alts_of(configs)
    return next(iter(alts)) if len(alts) == 1 else None


def conflicting_alt_subsets(configs) -> List[Set[int]]:
    """按 (状态, 栈) 分组得到的备选集合；某组含多个备选 = 这些备选“走到了同一处”。"""
    groups: Dict[Tuple[int, Stack], Set[int]] = defaultdict(set)
    for s, a, st in configs:
        groups[(s, st)].add(a)
    return list(groups.values())


def state_to_alts(configs) -> List[Set[int]]:
    groups: Dict[int, Set[int]] = defaultdict(set)
    for s, a, _ in configs:
        groups[s].add(a)
    return list(groups.values())


def single_viable_alt(subsets: List[Set[int]]) -> Optional[int]:
    """每个冲突子集的最小备选都相同 → 无论往后看多远，最终都会选它。"""
    mins = {min(s) for s in subsets}
    return mins.pop() if len(mins) == 1 else None


class ATNSimulator:
    def __init__(self, atn: ATN):
        self.atn = atn

    def start_configs(self, rule: str, stack: Stack) -> FrozenSet[Config]:
        out: Set[Config] = set()
        busy: Set[Config] = set()
        for i in range(1, len(self.atn.g.rules[rule]) + 1):
            self.closure((self.atn.alt_path[(rule, i)][0].id, i, stack), out, busy)
        return frozenset(out)

    def closure(self, c: Config, out: Set[Config], busy: Set[Config]):
        """
        沿所有 ε 边（含规则调用 / 返回）扩展配置，只把“下一步要匹配记号”的配置
        以及“走完起始规则”的配置放进结果集（与 ANTLR 的优化一致）。
        """
        if c in busy:
            return
        busy.add(c)
        sid, alt, stack = c
        st = self.atn.states[sid]

        if st.kind == "stop":
            if stack and stack[0] == WILDCARD:
                # SLL：不知道是谁调用的 → 跳到“所有调用点”的返回状态（相当于全局 FOLLOW）
                if st.rule == self.atn.g.start:
                    out.add(c)  # 起始规则结束：后面只能是输入结尾
                for f in self.atn.callers[st.rule]:
                    self.closure((f.id, alt, stack), out, busy)
            elif not stack:
                out.add(c)  # LL：真实调用栈已空 → 整个输入的起始规则结束
            else:
                self.closure((stack[0], alt, stack[1:]), out, busy)  # 弹栈返回
            return

        matchable = False
        for t in st.transitions:
            if t.kind == "eps":
                self.closure((t.target.id, alt, stack), out, busy)
            elif t.kind == "rule":
                push = () if t.follow.is_tail else (t.follow.id,)
                self.closure((t.target.id, alt, push + stack), out, busy)  # 压栈调用
            else:
                matchable = True
        if matchable:
            out.add(c)

    def reach(self, configs, ttype: str) -> FrozenSet[Config]:
        """reach = closure(move(D, a))"""
        out: Set[Config] = set()
        busy: Set[Config] = set()
        for sid, alt, stack in configs:
            for t in self.atn.states[sid].transitions:
                if t.kind == "atom" and t.label == ttype:
                    self.closure((t.target.id, alt, stack), out, busy)
        return frozenset(out)

    def sll_should_stop(self, configs) -> bool:
        """对应 ANTLR 的 PredictionMode.hasSLLConflictTerminatingPrediction"""
        if all(self.atn.states[s].kind == "stop" for s, _, _ in configs):
            return True
        has_conflict = any(len(x) > 1 for x in conflicting_alt_subsets(configs))
        has_state_with_one_alt = any(len(x) == 1 for x in state_to_alts(configs))
        return has_conflict and not has_state_with_one_alt


# =====================================================================
# 4. 决策 DFA（预测缓存）
# =====================================================================
@dataclass(eq=False)
class DFAState:
    id: int
    configs: FrozenSet[Config]
    edges: Dict[str, "DFAState"] = field(default_factory=dict)
    prediction: Optional[int] = None
    requires_full_ctx: bool = False
    conflicting_alts: Optional[Set[int]] = None


class DFA:
    def __init__(self, rule: str):
        self.rule = rule
        self.s0: Optional[DFAState] = None
        self.states: Dict[FrozenSet[Config], DFAState] = {}

    def add(self, configs: FrozenSet[Config], sim: ATNSimulator) -> DFAState:
        if configs in self.states:  # 配置集相同 → 同一个 DFA 状态（这就是 DFA 能出现环的原因）
            return self.states[configs]
        d = DFAState(len(self.states), configs)
        u = unique_alt(configs)
        if u is not None:
            d.prediction = u
        elif sim.sll_should_stop(configs):
            d.requires_full_ctx = True
            d.conflicting_alts = alts_of(configs)
        self.states[configs] = d
        return d

    def dump(self) -> str:
        lines = [f"DFA[{self.rule}]  共 {len(self.states)} 个状态"]
        for d in sorted(self.states.values(), key=lambda x: x.id):
            tag = "  (s0)" if d is self.s0 else ""
            if d.prediction is not None:
                tag += f"  ⇒ 预测 alt {d.prediction}"
            if d.requires_full_ctx:
                tag += f"  ⇒ SLL 冲突 {sorted(d.conflicting_alts)}，需全上下文 LL"
            lines.append(f"  D{d.id}{tag}")
            for t, nd in d.edges.items():
                lines.append(f"      --{t!r}--> D{nd.id}")
        return "\n".join(lines)


class PredictionCache:
    """跨 Parser 实例共享的“每个决策一个 DFA”（对应 ANTLR 的 decisionToDFA，静态共享）"""

    def __init__(self, atn: ATN):
        self.atn = atn
        self.sim = ATNSimulator(atn)
        self.dfas = {r: DFA(r) for r, alts in atn.g.rules.items() if len(alts) > 1}
        self.stats: Counter = Counter()


# =====================================================================
# 5~7. 由 adaptive_predict 驱动的解析器
# =====================================================================
class ParseTree:
    def __init__(self, rule: str, alt: int):
        self.rule, self.alt = rule, alt
        self.children: List = []

    def to_lisp(self) -> str:
        """类似 ANTLR 的 toStringTree：(rule child child ...)"""
        parts = [c.to_lisp() if isinstance(c, ParseTree) else c.text for c in self.children]
        return "(" + " ".join([f"{self.rule}#{self.alt}"] + parts) + ")"


class NoViableAltError(SyntaxError):
    pass


class Parser:
    def __init__(self, cache: PredictionCache, tokens: List[Token], trace: bool = False):
        self.cache, self.atn, self.sim = cache, cache.atn, cache.sim
        self.g = self.atn.g
        self.tokens = tokens
        self.i = 0
        self.call_stack: List[int] = []  # 真实调用栈：保存返回状态编号（栈顶在末尾）
        self.trace = trace
        self.ambiguities: List[Tuple[str, List[int], str]] = []

    # ---------- 基础 ----------
    def la(self, idx: int) -> Token:
        return self.tokens[min(idx, len(self.tokens) - 1)]

    def log(self, msg: str):
        if self.trace:
            print(msg)

    def _span(self, a: int, b: int) -> str:
        return " ".join(t.text for t in self.tokens[a:b + 1])

    def parse(self, rule: Optional[str] = None) -> ParseTree:
        return self._rule(rule or self.g.start)

    def _rule(self, rule: str) -> ParseTree:
        alts = self.g.rules[rule]
        alt = 1 if len(alts) == 1 else self.adaptive_predict(rule)
        node = ParseTree(rule, alt)
        path = self.atn.alt_path[(rule, alt)]
        for k, sym in enumerate(alts[alt - 1]):
            if self.g.is_terminal(sym):
                node.children.append(self._match(self.g.token_type(sym)))
            else:
                self.call_stack.append(path[k + 1].id)
                node.children.append(self._rule(sym))
                self.call_stack.pop()
        return node

    def _match(self, ttype: str) -> Token:
        tok = self.la(self.i)
        if tok.type != ttype:
            raise SyntaxError(f"位置 {tok.pos}：期望 {ttype!r}，实际是 {tok.text!r}")
        self.i += 1
        return tok

    def outer_context(self) -> Stack:
        return tuple(reversed(self.call_stack))

    # ---------- 核心：自适应预测 ----------
    def adaptive_predict(self, rule: str) -> int:
        dfa = self.cache.dfas[rule]
        stats = self.cache.stats
        start = self.i
        self.log(f"[预测] 决策 {rule}，从记号 #{start} {self.la(start).text!r} 开始")
        if dfa.s0 is None:
            dfa.s0 = dfa.add(self.sim.start_configs(rule, (WILDCARD,)), self.sim)
            self.log(f"  构造 s0 = D{dfa.s0.id} {fmt_configs(dfa.s0.configs)}")
        d, i = dfa.s0, start
        while True:
            if d.requires_full_ctx:
                stats["sll_conflict"] += 1
                self.log(f"  D{d.id} 是 SLL 冲突状态 {sorted(d.conflicting_alts)} → 回退全上下文 LL")
                return self.ll_predict(rule, start)
            if d.prediction is not None:
                stats["sll_ok"] += 1
                self.log(f"  ✔ SLL 预测 alt {d.prediction}（向前看 {i - start} 个记号）")
                return d.prediction
            t = self.la(i).type
            nxt = d.edges.get(t)
            if nxt is None:
                stats["atn_steps"] += 1
                reach = self.sim.reach(d.configs, t)
                if not reach:
                    raise NoViableAltError(
                        f"no viable alternative：规则 {rule} 从 {self.la(start).text!r} 开始，"
                        f"读到 {self.la(i).text!r} 时所有备选都走不通（输入片段：{self._span(start, i)}）")
                nxt = dfa.add(reach, self.sim)
                d.edges[t] = nxt
                self.log(f"  ATN 模拟 D{d.id} --{t!r}--> D{nxt.id} {fmt_configs(reach)}")
            else:
                stats["dfa_hits"] += 1
                self.log(f"  DFA 命中 D{d.id} --{t!r}--> D{nxt.id}")
            d, i = nxt, i + 1

    def ll_predict(self, rule: str, start: int) -> int:
        stats = self.cache.stats
        stats["ll_predict"] += 1
        gamma0 = self.outer_context()
        configs = self.sim.start_configs(rule, gamma0)
        self.log(f"  [LL] 真实调用栈 γ0 = [{fmt_stack(gamma0)}]，起始 {fmt_configs(configs)}")
        i = start
        while True:
            t = self.la(i).type
            reach = self.sim.reach(configs, t)
            self.log(f"  [LL] --{t!r}--> {fmt_configs(reach)}")
            if not reach:
                raise NoViableAltError(f"no viable alternative：规则 {rule}（全上下文）在 {self.la(i).text!r} 处失败")
            u = unique_alt(reach)
            if u is not None:
                self.log(f"  ✔ LL 预测 alt {u}（向前看 {i - start + 1} 个记号；SLL 做不到，属于上下文相关决策）")
                return u
            alt = single_viable_alt(conflicting_alt_subsets(reach))
            if alt is not None:
                amb = sorted(alts_of(reach))
                self.ambiguities.append((rule, amb, self._span(start, i)))
                stats["ambiguity"] += 1
                self.log(f"  ⚠ 真二义性：备选 {amb} 都能匹配 {self._span(start, i)!r}，按规则选最小编号 alt {alt}")
                return alt
            configs, i = reach, i + 1


def build(grammar_text: str):
    g = Grammar(grammar_text)
    atn = ATN(g)
    cache = PredictionCache(atn)
    lexer = Lexer(g.literals(), DEFAULT_PATTERNS)
    return g, atn, cache, lexer


def parse(cache: PredictionCache, lexer: Lexer, text: str, trace: bool = False) -> Parser:
    p = Parser(cache, lexer.tokenize(text), trace)
    tree = p.parse()
    p.tree = tree
    return p


# =====================================================================
# 8. 左递归改写：优先级爬升（precedence climbing）
# =====================================================================
class ExprParser:
    """
    原始（直接左递归）文法，ANTLR4 允许直接这样写：
        expr : <assoc=right> expr '^' expr      // 优先级 3（越靠前越高）
             | expr ('*'|'/') expr             // 优先级 2
             | expr ('+'|'-') expr             // 优先级 1
             | INT
             | '(' expr ')'
             ;
    ANTLR4 自动改写为（示意）：
        expr[int _p]
          : ( INT | '(' expr[0] ')' )                        // 非左递归备选 = primary
            ( {precpred(_p <= 3)}? '^' expr[3]                // 右结合：右操作数用同一优先级
            | {precpred(_p <= 2)}? ('*'|'/') expr[3]          // 左结合：右操作数用 优先级+1
            | {precpred(_p <= 1)}? ('+'|'-') expr[2]
            )*
          ;
    """

    BINARY = {"^": (3, "right"), "*": (2, "left"), "/": (2, "left"), "+": (1, "left"), "-": (1, "left")}

    def __init__(self, text: str, trace: bool = False):
        self.tokens = Lexer(set("^*/+-()"), {"INT": r"\d+"}).tokenize(text)
        self.i, self.trace, self.depth = 0, trace, 0

    def la(self) -> Token:
        return self.tokens[self.i]

    def log(self, msg: str):
        if self.trace:
            print("  " * self.depth + msg)

    def parse(self):
        tree = self.expr(0)
        if self.la().type != EOF:
            raise SyntaxError(f"多余的输入 {self.la().text!r}")
        return tree

    def expr(self, p: int):
        self.log(f"expr[_p={p}]")
        self.depth += 1
        tok = self.la()
        if tok.type == "INT":
            self.i += 1
            left = int(tok.text)
        elif tok.type == "(":
            self.i += 1
            left = self.expr(0)
            if self.la().type != ")":
                raise SyntaxError("缺少 ')'")
            self.i += 1
        else:
            raise SyntaxError(f"no viable alternative at {tok.text!r}")
        while self.la().type in self.BINARY:
            op = self.la().type
            prec, assoc = self.BINARY[op]
            if not p <= prec:  # 语义谓词 precpred 失败 → 这个运算符归外层处理
                self.log(f"precpred({p} <= {prec}) 为假，遇到 {op!r} 退出循环")
                break
            self.log(f"precpred({p} <= {prec}) 为真，吃掉 {op!r}")
            self.i += 1
            right = self.expr(prec if assoc == "right" else prec + 1)
            left = (op, left, right)
        self.depth -= 1
        return left


def tree_str(t) -> str:
    return str(t) if not isinstance(t, tuple) else f"({t[0]} {tree_str(t[1])} {tree_str(t[2])})"


def evaluate(t):
    if not isinstance(t, tuple):
        return t
    op, a, b = t[0], evaluate(t[1]), evaluate(t[2])
    return {"+": a + b, "-": a - b, "*": a * b, "/": a / b, "^": a ** b}[op]


# =====================================================================
# 演示
# =====================================================================
G_STAT = r"""
stat : 'if' ID 'then' stat
     | 'print' ID ';'
     | ID '=' ID ';'
     ;
"""

G_DECL = r"""
prog : decl prog
     | EOF
     ;
decl : mods 'int' ID ';'      // int x;   unsigned unsigned int x;
     | mods ID ID ';'         // T x;     unsigned T x;
     ;
mods : 'unsigned' mods
     |
     ;
"""

G_CTX = r"""
s : 'x' b EOF
  | 'y' c EOF
  ;
b : a 'a' ;
c : a 'b' 'a' ;
a : 'b'
  |
  ;
"""

G_AMBIG = r"""
prog      : stat EOF ;
stat      : decl
          | expr_stmt
          ;
decl      : ID '(' ID ')' ';' ;   // T(x);  声明类型为 T 的变量 x
expr_stmt : ID '(' ID ')' ';' ;   // f(x);  调用函数 f
"""


def banner(title: str):
    print("\n" + "=" * 72 + f"\n{title}\n" + "=" * 72)


def demo_ll1():
    banner("Demo 1  LL(1) 决策：看 1 个记号就够")
    g, atn, cache, lexer = build(G_STAT)
    p = parse(cache, lexer, "if a then print b ;", trace=True)
    print("语法树:", p.tree.to_lisp())


def demo_atn():
    banner("Demo 2  文法 → ATN")
    g, atn, cache, lexer = build(G_CTX)
    print(atn.dump())


def demo_llstar():
    banner("Demo 3  任意长度向前看（LL(*)）+ DFA 缓存")
    g, atn, cache, lexer = build(G_DECL)
    p = parse(cache, lexer, "unsigned unsigned unsigned int x ;", trace=True)
    print("语法树:", p.tree.to_lisp())
    print()
    print(cache.dfas["decl"].dump())
    print()
    print("—— 用同一个缓存继续解析（模拟同一 Parser 类处理更多输入）——")
    inputs = ["unsigned int y ;", "unsigned unsigned T z ;", "int a ; T b ; unsigned unsigned unsigned unsigned int c ;"]
    for text in inputs:
        before = Counter(cache.stats)
        parse(cache, lexer, text)
        delta = cache.stats - before
        print(f"  {text:<55} ATN 模拟 {delta['atn_steps']:>2} 步，DFA 命中 {delta['dfa_hits']:>2} 次")
    print()
    print(cache.dfas["decl"].dump())


def demo_context():
    banner("Demo 4  SLL 冲突 → 全上下文 LL")
    g, atn, cache, lexer = build(G_CTX)
    for text in ["y b a", "x b a"]:
        print(f"\n>>> 输入: {text}")
        p = parse(cache, lexer, text, trace=True)
        print("语法树:", p.tree.to_lisp())
    print()
    print(cache.dfas["a"].dump())
    print("统计:", dict(cache.stats))


def demo_ambiguity():
    banner("Demo 5  真二义性：T(x); 是声明还是函数调用？")
    g, atn, cache, lexer = build(G_AMBIG)
    p = parse(cache, lexer, "T ( x ) ;", trace=True)
    print("语法树:", p.tree.to_lisp())
    print("二义性报告:", p.ambiguities)


def demo_errors():
    banner("Demo 6  错误：no viable alternative / 左递归")
    g, atn, cache, lexer = build(G_DECL)
    try:
        parse(cache, lexer, "unsigned unsigned ;")
    except NoViableAltError as e:
        print("NoViableAltError:", e)
    try:
        Grammar("expr : expr '+' expr | INT ;")
    except GrammarError as e:
        print("GrammarError:", e)
    try:
        Grammar("a : b 'x' | 'y' ;  b : opt a ;  opt : 'z' | ;")
    except GrammarError as e:
        print("GrammarError:", e)


def demo_precedence():
    banner("Demo 7  左递归改写 + 优先级谓词")
    for text in ["1 + 2 * 3", "2 ^ 3 ^ 2", "8 - 3 - 2", "1 + 2 * 3 ^ 2 ^ 2", "( 1 + 2 ) * 3"]:
        t = ExprParser(text).parse()
        print(f"  {text:<20} => {tree_str(t):<32} = {evaluate(t)}")
    print("\n逐步跟踪 1 + 2 * 3 - 4 ：")
    ExprParser("1 + 2 * 3 - 4", trace=True).parse()


if __name__ == "__main__":
    demo_ll1()
    demo_atn()
    demo_llstar()
    demo_context()
    demo_ambiguity()
    demo_errors()
    demo_precedence()
