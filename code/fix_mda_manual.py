# -*- coding: utf-8 -*-
"""fix_mda_manual.py  对定位失败的6份年报按人工核定的起始页重抽MD&A
600251_2021 冠农: 第三节标题页为扫描件, 正文自页7起
600399_2010 抚顺特钢: 老式年报"董事会报告"节正文自页17起(经营回顾)
600438_2010 通威: 同上, 页16起
688083_2020 中望: 业务概要正文页35起
603899_2015 晨光: 业务概要(品牌优势)页10起
600145_2018 新亿: 年报无标准MD&A节(恢复上市筹备期, 章节极简), 保留现有文本并在数据说明注明
"""
import sys
sys.path.insert(0, "code")
from extract_mda import window, clean
import pdfplumber

MANUAL = {
    "600251_2021": 7,
    "600399_2010": 17,
    "600438_2010": 16,
    "688083_2020": 35,
    "603899_2015": 10,
}

for fid, start in MANUAL.items():
    code, year = fid.split("_")
    with pdfplumber.open(f"pdfs/{fid}.pdf") as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    text = window(pages, start)
    out = f"data/mdas/{fid}.txt"
    open(out, "w", encoding="utf-8").write(text[:8000])
    print(fid, "→ 页", start, "长度", len(text[:8000]), "| 开头:", clean(text)[:50])
print("600145_2018: 保持原文本(年报无标准MD&A节, 数据说明注明)")
