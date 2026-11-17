# -*- coding: utf-8 -*-
"""extract_mda.py  从年报PDF定位并抽取"管理层讨论与分析", 截断8000字
  防目录页: 命中页需同时含业务词; 失败件记入 logs/mda_miss.txt 人工兜底"""
import os, re, sys
import pandas as pd
import pdfplumber

START_KWS = ["管理层讨论与分析", "经营情况讨论与分析", "董事会报告"]   # 2015年前老年报用"董事会报告"
BUSI_WORDS = ["营业收入", "毛利率", "报告期", "实现", "同比"]
END_KWS   = ["重要事项", "财务报告", "公司治理"]

def clean(s):
    s = re.sub(r"\s+", "", s)
    return re.sub(r"第?[0-9]+\s*/\s*[0-9]+页|^目\s*录$", "", s)

def window(pages, start_i):
    end_i = None
    for j in range(start_i + 1, len(pages)):
        head = pages[j][:300]
        if any(k in head for k in END_KWS):
            end_i = j; break
    end_i = end_i or min(start_i + 25, len(pages))
    return "".join(clean(x) for x in pages[start_i:end_i])

def plausible(text):
    """开头像MD&A正文: 章节标题/一、/概述/报告期内等"""
    head = text[:500]
    return (any(k in head for k in START_KWS) or "一、" in head[:100]
            or "概述" in head[:100] or "报告期内" in head[:200]
            or any(w in head for w in BUSI_WORDS))

def extract(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    cands = []
    for i, t in enumerate(pages):
        if re.search(r"目\s*录", t[:300]):   # 跳过目录页(含全角/半角空格变体)
            continue
        head_ok = any(k in t[:300] for k in START_KWS)
        any_ok = any(k in t for k in START_KWS)
        if head_ok or any_ok:
            cands.append(i)
    for i in cands:   # 逐个候选试, 第一个"开头像正文"的窗口胜出
        text = window(pages, i)
        if len(text) > 1500 and plausible(text):
            return text[:8000]
    for i in cands:   # 兜底: 取最长窗口
        text = window(pages, i)
        if len(text) > 1500:
            return text[:8000]
    return None

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sample = pd.read_csv("data/tables/sample_all.csv")
    a_codes = set(pd.read_csv("data/tables/sample_a.csv").code)   # A组加抽t-1
    n_ok = n_miss = 0
    for _, r in sample.iterrows():
        years = [int(r.year_t)] + ([int(r.year_t) - 1] if r.code in a_codes else [])
        for yr in years:
            pdf = f"pdfs/{str(r.code).zfill(6)}_{yr}.pdf"
            out = f"data/mdas/{str(r.code).zfill(6)}_{yr}.txt"
            if not os.path.exists(pdf) or os.path.exists(out):
                continue
            txt = extract(pdf)
            if txt:
                open(out, "w", encoding="utf-8").write(txt); n_ok += 1
            else:
                open("logs/mda_miss.txt", "a", encoding="utf-8").write(pdf + "\n"); n_miss += 1
    print(f"成功 {n_ok} / 失败 {n_miss} (logs/mda_miss.txt 人工处理)")
