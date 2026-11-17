# -*- coding: utf-8 -*-
"""md2docx.py  论文初稿.md → 规范排版docx (黑体标题/宋体正文/1.5倍行距)"""
import re, sys
import docx
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn

d = docx.Document()
sec = d.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.top_margin = sec.bottom_margin = Cm(2.54)
sec.left_margin = sec.right_margin = Cm(3.0)

def set_font(run, name_east, size, bold=False, italic=False):
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name_east)

def title(t):
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10)
    set_font(p.add_run(t), "黑体", 16, bold=True)

def h2(t):
    p = d.add_paragraph()
    p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(4)
    set_font(p.add_run(t), "黑体", 13, bold=True)

def para(t, size=12):
    p = d.add_paragraph()
    pf = p.paragraph_format
    pf.first_line_indent = Pt(size * 2)
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_after = Pt(2)
    set_font(p.add_run(t), "宋体", size)

def ref(t):
    p = d.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.left_indent = Pt(24); pf.first_line_indent = Pt(-24)   # 悬挂缩进
    set_font(p.add_run(t), "宋体", 10.5)

src = sys.argv[1] if len(sys.argv) > 1 else "paper/论文初稿.md"
out = sys.argv[2] if len(sys.argv) > 2 else "paper/论文初稿.docx"
in_refs = False
for line in open(src, encoding="utf-8"):
    line = line.rstrip()
    if not line.strip():
        continue
    if line.startswith("# "):
        title(line[2:])
    elif line.startswith("## "):
        if line[3:].startswith("参考文献"):
            in_refs = True
        h2(line[3:])
    elif line.startswith("[") and re.match(r"^\[\d+\]", line):
        ref(line)
    elif line.startswith("- ") or line.startswith("> "):
        para(line[2:], size=11)
    else:
        para(line)
d.save(out)
print("saved", out)
