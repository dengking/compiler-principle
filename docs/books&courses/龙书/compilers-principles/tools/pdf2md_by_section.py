#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""龙书（Compilers: Principles, Techniques, and Tools, 2nd ed）PDF → 按"节"拆分的 Markdown。

为什么不用 markitdown 直接转：
    这本 PDF 用的是 Type3 子集字体，字体 /Differences 里的字形名是 `#XX` 形式的占位名，
    同时文本按"逐字形定位"排版。结果是所有常规提取器都会出问题：
      * 数字 0-9 被解成控制字符 U+0000~U+0009（`1986` → `\\x01\\x09\\x08\\x06`）
      * 连字 ff/fi/fl/ffi 被解成 U+000B~U+000E（`first` → `\\x0crst`）
      * 词内被插入断点（`modern` → `mo dern`，因为字距 0.24pt 被判成词边界）
    实测 markitdown(pdfminer) 输出为逐字符空格分隔的垃圾文本（`P r o g r a m m in g`），
    故这里改用 pymupdf 的字符级数据自行重建，并按码位修复控制字符。

本脚本做的事：
    1) 字符级提取（rawdict）→ 按 y 聚类成行 → 按字距补空格（重建词）
    2) 修复控制码位：数字 0-9、连字 ff/fi/fl/ffi，以及由上下文推断出的少量符号（ε/≤/≥）
    3) 按 PDF 书签切分：level1 = 章（目录），level2 = 节（一个 .md 文件），level3 = 小节（###）
    4) 剔除页眉页脚（含逐页变化的"页码 + 章/节名"行），合并连字符断词

用法：
    python pdf2md_by_section.py [--pdf PATH] [--out DIR] [--pages N M]
"""
from __future__ import annotations

import argparse
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import pymupdf

# ---------------------------------------------------------------- 码位修复
# 控制码位 -> 真实字符（规则来自对全书上下文的统计，见 docstring）
CTRL_FIX = {
    0x00: "0", 0x01: "1", 0x02: "2", 0x03: "3", 0x04: "4",
    0x05: "5", 0x06: "6", 0x07: "7", 0x08: "8", 0x09: "9",
    0x0B: "ff", 0x0C: "fi", 0x0D: "fl", 0x0E: "ffi",
}
# 歧义码位：按上下文判定（0x0F 在词内是 ffl，在 "ε-P..." 之类术语里是 ε）
AMBIGUOUS = {0x0F, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x18, 0x19, 0x1A, 0x1E}
GAP_RATIO = 0.18          # 字符间距 > 0.18 * 字号 => 空格
SKIP_LEVEL1 = {"Cover", "Title Page", "Copyright", "Table of Contents"}
# 文件名里保持小写的虚词（对齐仓库既有命名：1.2-The-Structure-of-a-Compiler）
MINOR = {"of", "a", "an", "the", "to", "for", "in", "on", "and", "or", "with", "at", "by", "from", "as"}
# 章目录名：沿用仓库既有命名（其余按标题自动生成）
EXISTING_DIRS = {
    "1": "1-Introduction", "2": "2-A-Simple-Syntax-Directed-Translator",
    "3": "3-Lexical-Analysis", "4": "4-Syntax-Analysis",
    "5": "5-Syntax-Directed-Translation", "6": "6-Intermediate-Code-Generation",
    "7": "7-Run-Time-Environments", "8": "8-Code-generation",
    "9": "9-Machine-Independent-Optimizations", "10": "10-Instruction-Level-Parallelism",
    "11": "11-Optimizing-for-Parallelism-and-Locality", "12": "12-Interprocedural-Analysis",
}


def fix_text(text: str) -> str:
    """修复控制码位；歧义码位按左右邻居判定，无法判定的一律丢弃"""
    out = []
    for i, ch in enumerate(text):
        code = ord(ch)
        if code in CTRL_FIX:
            out.append(CTRL_FIX[code])
            continue
        if code in AMBIGUOUS:
            before = text[i - 1] if i else " "
            after = text[i + 1] if i + 1 < len(text) else " "
            if code == 0x0F:
                if before.isalpha() and after.isalpha():
                    out.append("ffl")                 # offload / shuffle
                elif after == "-" or before.isalpha():
                    out.append("ε")                   # ε-productions / ε-free
            elif code in (0x14, 0x15) and (before.isalpha() or after.isalpha()):
                out.append("≤" if code == 0x14 else "≥")
            elif before.isalpha() and after.isalpha():
                out.append("")                        # 其余多为图形装饰，丢弃
            continue
        out.append(ch)
    return "".join(out)


def norm(s: str) -> str:
    """归一化：去掉所有非字母数字，用于标题匹配（PDF 里标题字距会被拆开）"""
    return re.sub(r"[^0-9a-z]+", "", unicodedata.normalize("NFKD", s).lower())


def page_lines(page: pymupdf.Page) -> list[str]:
    """重建行：字符级提取 -> 按 y 聚类成行 -> 按字距补空格。

    必须用 rawdict（字符级）：连字字形在 words 模式下会被丢弃并断开单词
    （first -> " rst"、files -> " les"），只有字符级才能拿到被解成控制码位的字形。
    """
    chars = []
    for blk in page.get_text("rawdict")["blocks"]:
        for line in blk.get("lines", []):
            for span in line["spans"]:
                for ch in span["chars"]:
                    x0, y0, x1, y1 = ch["bbox"]
                    chars.append((x0, x1, (y0 + y1) / 2, span["size"], ch["c"]))
    chars.sort(key=lambda c: (c[2], c[0]))

    clusters: list[list] = []
    for c in chars:
        for cl in reversed(clusters[-3:]):
            if abs(cl[0] - c[2]) <= 2.5:
                cl[1].append(c)
                cl[0] = sum(x[2] for x in cl[1]) / len(cl[1])
                break
        else:
            clusters.append([c[2], [c]])

    lines = []
    for _, cs in sorted(clusters, key=lambda c: c[0]):
        cs.sort(key=lambda c: c[0])
        out, prev_x1, size = [], None, cs[0][3]
        for x0, x1, _yc, sz, ch in cs:
            if prev_x1 is not None and x0 - prev_x1 > max(1.0, GAP_RATIO * size):
                out.append(" ")
            out.append(ch)
            prev_x1, size = x1, sz
        text = re.sub(r" {2,}", " ", fix_text("".join(out))).strip()
        if text:
            lines.append(text)
    return lines


def collect_running_heads(doc: pymupdf.Document) -> set[str]:
    """跨页重复出现的首/尾行 => 页眉页脚"""
    seen = Counter()
    for pno in range(doc.page_count):
        lines = page_lines(doc[pno])
        for ln in lines[:2] + lines[-2:]:
            seen[norm(ln)] += 1
    return {k for k, n in seen.items() if n > 20 and k}


def slugify(title: str) -> str:
    """'Language Processors' -> 'Language-Processors'（首字母大写、虚词小写、缩写原样）"""
    out = []
    for i, w in enumerate(re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", title)):
        if w.isupper() or any(c.isupper() for c in w[1:]) or any(c.isdigit() for c in w):
            out.append(w)                          # LR / LR-Parsing / 1.1
        elif i and w.lower() in MINOR:
            out.append(w.lower())
        else:
            out.append(w[0].upper() + w[1:])
    return "-".join(out)


def split_num(title: str) -> tuple[str, str]:
    """'1.1 Language Processors' -> ('1.1', 'Language Processors')；支持 A.1 / A: 形式"""
    m = re.match(r"^((?:\d+|[A-Z])(?:\.\d+)*):?\s+(.*)$", title.strip())
    return (m.group(1), m.group(2)) if m else ("", title.strip())


def build(pdf: Path, out: Path, only: tuple[int, int] | None) -> None:
    doc = pymupdf.open(pdf)
    blacklist = collect_running_heads(doc)
    toc = doc.get_toc()

    # 书签 -> 结构（pymupdf 顺序为 [级别, 标题, 页码]；索引页的字母组标题需排除）
    raw_chapters = [(p, t) for lvl, t, p in toc if lvl == 1]
    raw_sections = [(p, t) for lvl, t, p in toc
                    if lvl == 2 and not re.fullmatch(r"[A-Z]", t)]
    subs = {(p, norm(t)): t for lvl, t, p in toc if lvl == 3}

    ch_slug = {"0": "0-Front-Matter"}
    ch_title = {"0": "前置部分（封面/版权/目录/前言）"}
    ch_order: list[str] = []
    page_chapter: dict[int, str] = {}
    chapter_start_page: dict[int, str] = {}
    skip_pages: set[int] = set()
    for i, (p, t) in enumerate(raw_chapters):
        end = raw_chapters[i + 1][0] if i + 1 < len(raw_chapters) else doc.page_count + 1
        if t == "Table of Contents":
            skip_pages |= set(range(p, end))       # 目录页（点线）不转换
        key = "0" if t in SKIP_LEVEL1 else (split_num(t)[0] or t)
        if key != "0":
            ch_slug[key] = EXISTING_DIRS.get(key, slugify(t))
            ch_title[key] = t
            ch_order.append(key)
        chapter_start_page[p] = key
        for pg in range(p, end):
            page_chapter[pg] = key

    # 页眉页脚识别：全大写、去掉数字后与某章/节标题一致的短行
    strip_digits = lambda s: re.sub(r"\d+", "", s)
    titles_norm: set[str] = set()
    for t in list(ch_title.values()) + [t for _, t in raw_sections]:
        d = strip_digits(norm(t))
        titles_norm |= {d, "chapter" + d, "appendix" + d}

    sections_by_page: dict[int, list[str]] = defaultdict(list)
    for p, t in raw_sections:
        sections_by_page[p].append(t)

    docs: dict[str, list[str]] = defaultdict(list)      # 文件键 -> 行
    started: set[str] = set()
    fallback: list[str] = []                            # 靠页尾兜底才切出来的节
    curr: str | None = None

    def start_section(title: str) -> None:
        nonlocal curr
        num, name = split_num(title)
        slug = f"{num}-{slugify(name)}" if num else slugify(title)
        chnum = num.split(".")[0] if num else ""
        key = f"{ch_slug.get(chnum, chnum)}/{slug}.md"
        if key in started:
            key = key.replace(".md", "-dup.md")
        started.add(title)
        curr = key
        docs[key] += [f"## {title}", ""]

    lo, hi = (only if only else (1, doc.page_count))
    for pno in range(lo - 1, min(hi, doc.page_count)):
        pg = pno + 1
        if pg in skip_pages:
            continue
        if pg in chapter_start_page:
            # 章首页：其首个节标题之前的内容归入"章首内容"
            curr = f"CH:{chapter_start_page[pg]}"
            docs[curr] = [f"# {ch_title[chapter_start_page[pg]]}", ""]
        if curr is None:
            curr = f"CH:{page_chapter.get(pg, '0')}"

        lines = page_lines(doc[pno])
        i = 0
        while i < len(lines):
            ln = lines[i]
            nxt = lines[i + 1] if i + 1 < len(lines) else None
            i += 1
            if norm(ln) in blacklist or re.fullmatch(r"\d{1,4}", ln):
                continue
            n = norm(ln)
            # 页眉页脚 / 章标题行
            if not any(c.islower() for c in ln) and len(ln) < 70 and (
                    strip_digits(n) in titles_norm or n in titles_norm):
                continue
            if re.fullmatch(r"(?i)(chapter|appendix)\s+[0-9a-z]{1,2}\.?", ln.strip()):
                continue
            # 节标题（书签声明的页上；标题可能折行，故尝试拼接下一行）
            pending = [t for t in sections_by_page.get(pg, []) if t not in started]
            hit = next((t for t in pending if norm(t) == n and any(c.islower() for c in ln)), None)
            if hit is None and nxt:
                hit = next((t for t in pending if norm(t) == norm(ln + " " + nxt)
                            and any(c.islower() for c in ln)), None)
                if hit:
                    i += 1                         # 第二行属于标题，吃掉
            if hit:
                start_section(hit)
                continue
            # 小节标题
            if (pg, n) in subs and any(c.islower() for c in ln):
                docs[curr] += [f"### {subs[(pg, n)]}", ""]
                continue
            # 正文：续行合并（连字符断词 / 未断句）
            body = docs[curr]
            if body and body[-1] and not body[-1].endswith((".", "!", "?", ":", ";", "|")):
                prev = body[-1]
                if prev.endswith("-") and ln[:1].islower():
                    body[-1] = prev[:-1] + ln
                    continue
                if ln[:1].islower():
                    body[-1] = prev + " " + ln
                    continue
            body.append(ln)
        # 页尾兜底：书签显示本节在本页开始但没匹配到标题（标题折行/排版异常）
        for t in sections_by_page.get(pg, []):
            if t not in started:
                start_section(t)
                fallback.append(t)

    # ---------------- 落盘
    out.mkdir(parents=True, exist_ok=True)
    index_lines = ["# Compilers: Principles, Techniques, and Tools (2nd ed)", "",
                   "由 `tools/pdf2md_by_section.py` 从 `compilers-principles.pdf` 转换而来："
                   "按 PDF 书签切分，**一级标题=章目录、二级标题（如 1.1 节）=一个 markdown 文件**、"
                   "三级标题=文件内的 `###` 小标题。", ""]
    for num in ch_order:
        cdir = out / ch_slug[num]
        cdir.mkdir(parents=True, exist_ok=True)
        secs = sorted(k for k in docs if k.startswith(ch_slug[num] + "/"))
        idx = [f"# {ch_title[num]}", ""]
        for k in secs:
            title = next((ln[3:] for ln in docs[k] if ln.startswith("## ")), Path(k).name)
            idx.append(f"- [{title}]({Path(k).name})")
        pre = [ln for ln in docs.get(f"CH:{num}", []) if ln and not ln.startswith("# ")]
        if pre:
            idx += ["", "## 章首内容", ""] + pre
        (cdir / "index.md").write_text("\n".join(idx) + "\n", encoding="utf-8")
        for k in secs:
            text = re.sub(r"\n{3,}", "\n\n", "\n".join(docs[k]))
            (out / k).write_text(text + "\n", encoding="utf-8")
        index_lines.append(f"- [{ch_title[num]}]({ch_slug[num]}/index.md) — {len(secs)} 节")
    fm = out / ch_slug["0"]
    fm.mkdir(exist_ok=True)
    body = [ln for ln in docs.get("CH:0", []) if ln and not ln.startswith("# ")]
    (fm / "index.md").write_text("\n".join([f"# {ch_title['0']}", ""] + body) + "\n", encoding="utf-8")
    index_lines.append(f"- [{ch_title['0']}]({ch_slug['0']}/index.md)")
    (out / "index.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    n_files = sum(1 for k in docs if "/" in k)
    print(f"完成：章目录 {len(ch_order)} 个，节文件 {n_files} 个，兜底切分 {len(fallback)} 个")
    for t in fallback:
        print("   兜底:", t)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", type=Path,
                    default=Path(__file__).resolve().parents[2] / "compilers-principles.pdf")
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--pages", nargs=2, type=int, default=None, help="仅转换指定页码范围（调试用）")
    a = ap.parse_args()
    build(a.pdf, a.out, (a.pages[0], a.pages[1]) if a.pages else None)


if __name__ == "__main__":
    main()
