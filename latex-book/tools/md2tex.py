#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把本书的 markdown 章节转成 LaTeX（ctexbook）。"""
import re
import sys
from pathlib import Path

SRC = Path(r"C:/Users/lidajiao/WorkBuddy/2026-10-11_LaTeX实用教材写作")
OUT = Path(r"C:/Users/lidajiao/WorkBuddy/2026-10-11_LaTeX实用教材写作/latex-book/chapters")

FILES = [
    ("ch01", "样稿-第1章-Word好好的我为什么要受这个罪.md"),
    ("ch02", "样稿-第2章-改一个标题的字号后面跟着全乱了.md"),
    ("ch03", "第3章-目录和页码交稿前又得手动刷新一遍.md"),
    ("ch04", "第4章-图一插进来后面的字全飞了.md"),
    ("ch05", "第5章-删了一张图后面几十个编号全要手动改.md"),
    ("ch06", "第6章-Word的公式编辑器是反人类设计.md"),
    ("ch07", "第7章-调个三线表半小时竖线还总对不齐.md"),
    ("ch08", "第8章-参考文献格式导师要国标我手打了一下午.md"),
    ("ch09", "第9章-中文排版设置藏得比迷宫还深.md"),
    ("ch10", "第10章-页码要从正文才开始编.md"),
    ("ch11", "第11章-多人合稿格式五花八门.md"),
    ("ch12", "第12章-文档一长Word打开都要等半天.md"),
    ("ch13", "第13章-导师扔来一个PDF照这个格式做.md"),
    ("ch14", "第14章-数学建模组会汇报还要另做一套幻灯片.md"),
    ("ch15", "第15章-综合实战从空白到一篇能交的小论文.md"),
    ("ch16", "第16章-急救手册.md"),
]

ESC = {
    "\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$",
    "&": r"\&", "#": r"\#", "%": r"\%", "_": r"\_",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    # 正文里直接出现的 Unicode 数学符号，统一交给数学模式，避免字体缺字
    "∪": r"\ensuremath{\cup}", "∩": r"\ensuremath{\cap}",
    "⊂": r"\ensuremath{\subset}", "⊆": r"\ensuremath{\subseteq}",
    "⊇": r"\ensuremath{\supseteq}", "∈": r"\ensuremath{\in}",
    "∉": r"\ensuremath{\notin}", "≤": r"\ensuremath{\leq}",
    "≥": r"\ensuremath{\geq}", "≠": r"\ensuremath{\neq}",
    "≈": r"\ensuremath{\approx}", "∞": r"\ensuremath{\infty}",
    "→": r"\ensuremath{\rightarrow}", "←": r"\ensuremath{\leftarrow}",
    "↔": r"\ensuremath{\leftrightarrow}", "⇒": r"\ensuremath{\Rightarrow}",
    "⇔": r"\ensuremath{\Leftrightarrow}", "×": r"\ensuremath{\times}",
    "÷": r"\ensuremath{\div}", "±": r"\ensuremath{\pm}",
    "∑": r"\ensuremath{\sum}", "∏": r"\ensuremath{\prod}",
    "∫": r"\ensuremath{\int}", "∀": r"\ensuremath{\forall}",
    "∃": r"\ensuremath{\exists}", "∅": r"\ensuremath{\varnothing}",
    "∂": r"\ensuremath{\partial}", "∇": r"\ensuremath{\nabla}",
    "√": r"\ensuremath{\surd}",
    # 希腊字母（正文/表格里出现的）
    "α": r"\ensuremath{\alpha}", "β": r"\ensuremath{\beta}",
    "γ": r"\ensuremath{\gamma}", "δ": r"\ensuremath{\delta}",
    "ε": r"\ensuremath{\varepsilon}", "ζ": r"\ensuremath{\zeta}",
    "η": r"\ensuremath{\eta}", "θ": r"\ensuremath{\theta}",
    "κ": r"\ensuremath{\kappa}", "λ": r"\ensuremath{\lambda}",
    "μ": r"\ensuremath{\mu}", "ν": r"\ensuremath{\nu}",
    "ξ": r"\ensuremath{\xi}", "π": r"\ensuremath{\pi}",
    "ρ": r"\ensuremath{\rho}", "σ": r"\ensuremath{\sigma}",
    "τ": r"\ensuremath{\tau}", "φ": r"\ensuremath{\varphi}",
    "χ": r"\ensuremath{\chi}", "ψ": r"\ensuremath{\psi}",
    "ω": r"\ensuremath{\omega}",
    "Γ": r"\ensuremath{\Gamma}", "Δ": r"\ensuremath{\Delta}",
    "Θ": r"\ensuremath{\Theta}", "Λ": r"\ensuremath{\Lambda}",
    "Ξ": r"\ensuremath{\Xi}", "Π": r"\ensuremath{\Pi}",
    "Σ": r"\ensuremath{\Sigma}", "Φ": r"\ensuremath{\Phi}",
    "Ψ": r"\ensuremath{\Psi}", "Ω": r"\ensuremath{\Omega}",
    # 带圈数字、叉号
    "①": r"\textcircled{\scriptsize 1}", "②": r"\textcircled{\scriptsize 2}",
    "③": r"\textcircled{\scriptsize 3}", "④": r"\textcircled{\scriptsize 4}",
    "⑤": r"\textcircled{\scriptsize 5}", "✕": r"\ensuremath{\times}",
    # 上下标小字符（正文示例用）
    "ᵢ": "i", "₌": "=", "₁": "1", "ⁿ": "n", "ₙ": "n",
}


def esc(t: str) -> str:
    return "".join(ESC.get(c, c) for c in t)


CJK = re.compile(r"[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef]")


def smart_quotes(t: str) -> str:
    """把成对的英文直引号换成中文引号（只处理成对出现的情况）。"""
    def repl(m):
        return "“" + m.group(1) + "”"
    return re.sub(r'"([^"\n]{1,80})"', repl, t)


def inline(t: str) -> str:
    """处理行内代码、加粗，再整体转义。"""
    codes = []

    def stash(m):
        codes.append(m.group(1))
        return "\x01%d\x02" % (len(codes) - 1)

    t = re.sub(r"`([^`]+)`", stash, t)

    bolds = []

    def bold(m):
        bolds.append(inline(m.group(1)))
        return "\x03%d\x04" % (len(bolds) - 1)

    t = re.sub(r"\*\*(.+?)\*\*", bold, t)
    t = esc(t)
    t = t.replace("*", r"\textasteriskcentered{}") if False else t

    def restore_bold(m):
        k = int(m.group(1))
        if k >= len(bolds):
            return m.group(0)          # 属于外层调用的占位符，交给外层还原
        return r"\textbf{" + bolds[k] + "}"

    t = re.sub("\x03(\\d+)\x04", restore_bold, t)

    def restore_code(m):
        k = int(m.group(1))
        if k >= len(codes):
            return m.group(0)          # 同上
        return r"\texttt{" + esc(codes[k]) + "}"

    t = re.sub("\x01(\\d+)\x02", restore_code, t)
    return t


def join_par(lines):
    out = ""
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        if not out:
            out = ln
        elif CJK.search(out[-1]) and CJK.search(ln[0]):
            out += ln
        else:
            out += " " + ln
    return out


def heading(level, text):
    text = text.strip()
    if level == 1:
        t = re.sub(r"^第\s*\d+\s*章[\s:：]*", "", text)
        t = t.strip().strip('"')
        return "\\chapter{%s}\n" % inline(smart_quotes(t))
    if level == 2:
        m = re.match(r"^【(.+?)】(.*)$", text)
        if m:
            label, rest = m.group(1), m.group(2).strip()
            if rest:
                label = label + " · " + rest
            return "\\painhead{%s}\n" % inline(label)
        m = re.match(r"^(\d+\.\d+)\s+(.*)$", text)
        if m:
            # 保留原编号（【解决线路】等结构标题不编号，自动编号会出现 2.0.x）
            return "\\subsection*{%s}\n" % inline(smart_quotes(text))
        m = re.match(r"^第\s*\d+\s*步\s*(.*)$", text)
        if m:
            return "\\section*{%s}\n\\addcontentsline{toc}{section}{%s}\n" % (
                inline(smart_quotes(text)), inline(smart_quotes(text)).replace("\\", "\\\\") if False else inline(smart_quotes(text))
            )
        return "\\section*{%s}\n" % inline(smart_quotes(text))
    if level == 3:
        m = re.match(r"^(\d+\.\d+(?:\.\d+)?)\s+(.*)$", text)
        if m:
            return "\\subsection*{%s}\n" % inline(smart_quotes(text))
        return "\\subsubsection*{%s}\n" % inline(smart_quotes(text))
    return ""


def is_table_sep(line):
    s = line.strip()
    if not s.startswith("|"):
        return False
    cells = [c.strip() for c in s.strip("|").split("|")]
    return all(re.fullmatch(r":?-{2,}:?", c) for c in cells) and len(cells) >= 2


def cells_of(row):
    """按 | 切分单元格，但跳过行内代码里的 | 和转义的 \\|。"""
    s = row.strip().strip("|")
    cells, cur, in_code, i = [], "", False, 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur += "|"
            i += 2
            continue
        if c == "`":
            in_code = not in_code
            cur += c
            i += 1
            continue
        if c == "|" and not in_code:
            cells.append(cur)
            cur = ""
            i += 1
            continue
        cur += c
        i += 1
    cells.append(cur)
    return [c.strip() for c in cells]


def emit_table(rows):
    """rows: list of raw '| a | b |' lines, first is header."""
    header = cells_of(rows[0])
    body = [cells_of(r) for r in rows[2:]]
    n = len(header)
    spec = "@{}*{%d}{>{\\raggedright\\arraybackslash}X}@{}" % n
    out = ["\\begin{table}[htbp]", "\\centering", "\\small",
           "\\begin{tabularx}{\\linewidth}{%s}" % spec, "\\toprule"]
    out.append(" & ".join("\\textbf{%s}" % inline(c) for c in header) + " \\\\")
    out.append("\\midrule")
    for r in body:
        if len(r) < n:
            r = r + [""] * (n - len(r))
        out.append(" & ".join(inline(c) for c in r[:n]) + " \\\\")
    out += ["\\bottomrule", "\\end{tabularx}", "\\end{table}", ""]
    return "\n".join(out)


def convert(md: str) -> str:
    lines = md.splitlines()
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        s = line.strip()

        if not s:
            i += 1
            continue

        # 代码块
        if s.startswith("```"):
            lang = s[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            body = "\n".join(buf)
            out.append("\\begin{lstlisting}\n%s\n\\end{lstlisting}\n" % body)
            continue

        # 标题
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            out.append(heading(len(m.group(1)), m.group(2)))
            i += 1
            continue

        # 分隔线
        if re.fullmatch(r"-{3,}|\*{3,}", s):
            i += 1
            continue

        # 表格
        if s.startswith("|") and i + 1 < n and is_table_sep(lines[i + 1]):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            if len(rows) >= 2:
                out.append(emit_table(rows))
            continue

        # 引用块
        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("\\begin{notebox}\n%s\n\\end{notebox}\n"
                       % inline(smart_quotes(join_par(buf))))
            continue

        # 列表
        if re.match(r"^(\s*)([-*+]|\d+[.)])\s+", line):
            base = len(line) - len(line.lstrip())
            block = []
            while i < n:
                cur = lines[i]
                if not cur.strip():
                    break
                if re.match(r"^(\s*)([-*+]|\d+[.)])\s+", cur) and (len(cur) - len(cur.lstrip())) >= base:
                    block.append(cur)
                    i += 1
                elif block and (len(cur) - len(cur.lstrip())) > base:
                    block.append(cur)   # 续行
                    i += 1
                else:
                    break
            out.append(render_list(block, base))
            continue

        # 普通段落
        buf = []
        while i < n and lines[i].strip() and not re.match(r"^(#{1,6})\s+", lines[i].strip()) \
                and not lines[i].strip().startswith("```") \
                and not lines[i].strip().startswith("|") \
                and not lines[i].strip().startswith(">") \
                and not re.match(r"^(\s*)([-*+]|\d+[.)])\s+", lines[i]):
            buf.append(lines[i])
            i += 1
        if buf:
            out.append(inline(smart_quotes(join_par(buf))) + "\n")
        else:
            i += 1

    return "\n".join(out)


def render_list(block, base):
    """把一段列表按缩进渲染成 itemize/enumerate（支持一级嵌套）。"""
    # 拆分条目
    items = []   # (indent, ordered, text_lines)
    for line in block:
        m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", line)
        indent = len(line) - len(line.lstrip())
        if m:
            ordered = m.group(2)[0].isdigit()
            items.append([indent, ordered, [m.group(3)]])
        elif items:
            items[-1][2].append(line.strip())

    top_indent = items[0][0] if items else base
    top = [it for it in items if it[0] == top_indent]
    ordered = top[0][1] if top else False
    env = "enumerate" if ordered else "itemize"

    out = ["\\begin{%s}" % env, "\\setlength{\\itemsep}{2pt}"]
    idx = 0
    while idx < len(items):
        indent, is_ord, texts = items[idx]
        if indent != top_indent:
            idx += 1
            continue
        out.append("\\item %s" % inline(smart_quotes(join_par(texts))))
        # 紧跟的更深缩进条目 -> 子列表
        sub = []
        j = idx + 1
        while j < len(items) and items[j][0] > top_indent:
            sub.append((items[j][0], items[j][1], items[j][2]))
            j += 1
        if sub:
            sub_env = "enumerate" if sub[0][1] else "itemize"
            out.append("\\begin{%s}" % sub_env)
            for _, _, t in sub:
                out.append("\\item %s" % inline(smart_quotes(join_par(t))))
            out.append("\\end{%s}" % sub_env)
        idx = j

    out.append("\\end{%s}" % env)
    return "\n".join(out) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in FILES:
        src = SRC / fn
        tex = convert(src.read_text(encoding="utf-8"))
        (OUT / (name + ".tex")).write_text(tex, encoding="utf-8")
        print("%-6s %-45s %5d lines" % (name, fn[:40], tex.count("\n")))


if __name__ == "__main__":
    main()
