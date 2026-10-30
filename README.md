# 《LaTeX 上手即用》LaTeX 版书稿

## 文件结构

- `main.tex` — 主文件（文档类 ctexbook，含封面、前言、目录、全部章节引入）
- `chapters/ch01.tex` ~ `ch16.tex` — 16 章正文（由 markdown 自动转换，`tools/md2tex.py` 生成）
- `tools/md2tex.py` — markdown → LaTeX 转换脚本（改了 md 源文件后重跑它，再编译）
- `build.bat` — 一键编译（xelatex 跑两遍）
- `main.pdf` — 成品

## 怎么编译

任选其一：

1. **TeXworks**：打开 `main.tex`，引擎选 **XeLaTeX**，点绿色"排版"按钮，**连点两遍**（目录和引用需要第二遍）。
2. **命令行**：双击 `build.bat`，或在终端里：

```
cd latex-book
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```

## 修改流程

内容源头是工作区根目录的 markdown 章节文件（`第N章-*.md` 和 `样稿-第1/2章-*.md`）。要改内容：

1. 改对应的 md 文件；
2. 运行 `python tools/md2tex.py` 重新生成 `chapters/*.tex`；
3. 重新编译 `main.tex` 两遍。

也可以直接改 `chapters/*.tex`，但下次重跑转换脚本会被覆盖。

## 版式说明

- 中文文档类 `ctexbook`，12pt，A4；
- 【烦恼】【现象】【解决线路】等结构标题渲染为深蓝色横条（`\painhead`）；
- 引用提示框为浅灰圆角盒（`notebox` 环境）；
- 代码块用 `listings`，等宽字体 DejaVu Sans Mono（字符全，目录树制表符不缺字）；
- 表格统一 `tabularx` + `booktabs` 三线表，等宽三列；
- 页码：前言/目录罗马数字，正文从 1 开始（正好呼应第 10 章教学内容）。
