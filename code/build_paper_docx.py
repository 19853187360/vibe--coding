# -*- coding: utf-8 -*-
"""build_paper_docx.py  论文初稿.md → 规范排版 docx(加粗/标题/表格/插图)
处理: ①**加粗** ②#/##标题 ③悬挂缩进参考文献 ④插入表1-5与图1-4"""
import re
import pandas as pd
import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

d = docx.Document()
sec = d.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.top_margin = sec.bottom_margin = Cm(2.3)
sec.left_margin = sec.right_margin = Cm(2.6)

def set_font(run, east="宋体", size=12, bold=False, italic=False):
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run._element.rPr.rFonts.set(qn("w:eastAsia"), east)

def add_runs(p, text, size=12, east="宋体", base_bold=False):
    """解析 **加粗** 内联标记"""
    for i, seg in enumerate(text.split("**")):
        if seg == "":
            continue
        r = p.add_run(seg)
        set_font(r, east, size, bold=base_bold or (i % 2 == 1))

def title(t):
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10)
    set_font(p.add_run(t), "黑体", 16, bold=True)

def author(t):
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    set_font(p.add_run(t), "宋体", 12)

def h2(t):
    p = d.add_paragraph()
    p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(4)
    set_font(p.add_run(t), "黑体", 13, bold=True)

def para(t, size=12, indent=True):
    p = d.add_paragraph()
    pf = p.paragraph_format
    if indent:
        pf.first_line_indent = Pt(size * 2)
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_after = Pt(2)
    add_runs(p, t, size)
    return p

def ref(t):
    p = d.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.left_indent = Pt(24); pf.first_line_indent = Pt(-24)
    add_runs(p, t, 10.5)
    return p

def caption(t):
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(6)
    set_font(p.add_run(t), "黑体", 10.5, bold=True)

def add_table(title, df, caption_font=10.5):
    caption(title)
    tbl = d.add_table(rows=len(df) + 1, cols=len(df.columns))
    tbl.style = "Table Grid"; tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, col in enumerate(df.columns):
        c = tbl.rows[0].cells[j]; c.text = ""
        r = c.paragraphs[0].add_run(str(col)); set_font(r, "黑体", caption_font, bold=True)
    for i, (_, row) in enumerate(df.iterrows(), start=1):
        for j, v in enumerate(row):
            c = tbl.rows[i].cells[j]; c.text = ""
            r = c.paragraphs[0].add_run(str(v)); set_font(r, "宋体", caption_font)
    d.add_paragraph().paragraph_format.space_after = Pt(4)

def add_fig(path, width_cm=13.5):
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(path, width=Cm(width_cm))

# ===== 表格数据 =====
t1 = pd.DataFrame({
    "项目": ["A组(舞弊公司)", "B组(配对对照)", "合计", "观测年度区间", "配对规则(三级)"],
    "说明": ["29 家，处罚事由为财务数据造假，逐条人工核验",
             "58 家，1:2 配对(同行业+同年度+总资产±30%)",
             "87 个公司-年度", "2010—2021 年",
             "±30%优先；不足放宽±50%；仍不足取规模最近(全部记录)"]})
t2 = pd.read_csv("results/main_result_v1.csv")
t3 = pd.read_csv("results/ablation.csv")
t4 = pd.read_csv("results/robustness.csv")
ff = pd.read_csv("data/tables/fin_features.csv")
g = ff.groupby("fraud")[["z_prime2", "m_score", "dsri", "gm_gap", "double_high", "qualified_op"]].mean().round(3)
t5 = g.T.reset_index()
t5.columns = ["变量", "B组均值", "A组均值"]
t5["变量"] = t5["变量"].map({"z_prime2": "Z″分数", "m_score": "M-score", "dsri": "应收异常指数DSRI",
                             "gm_gap": "毛利率-行业中位数", "double_high": "存贷双高比例", "qualified_op": "审计意见(非标比例)"})

# ===== 逐行渲染 =====
in_refs = False
for line in open("paper/论文初稿.md", encoding="utf-8"):
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
    elif line.startswith("陈欣语"):
        author(line)
    elif line.startswith("（山东财经大学）"):
        author(line)
    else:
        para(line)
    # 插图插表(紧跟对应段落之后)
    if "**描述性统计。**" in line:
        add_table("表5 描述性统计（A组 n=29 vs B组 n=58）", t5)
        add_fig("paper/f4_zm.png")
    elif "**样本构造。**" in line:
        add_table("表1 样本构成与配对规则", t1)
    elif "**主结果。**" in line:
        add_table("表2 主结果（同模型公平对比，随机划分42）", t2)
        add_fig("paper/f1_roc.png")
    elif "**消融实验。**" in line:
        add_table("表3 消融实验（同模型同切分）", t3)
    elif "**单变量分析。**" in line:
        add_fig("paper/f2_importance.png")
        add_fig("paper/f3_sim.png")
    elif "**前置性检验。**" in line:
        add_table("表4 稳健性检验", t4)

d.save("paper/论文初稿.docx")
print("saved paper/论文初稿.docx")
