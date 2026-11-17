# -*- coding: utf-8 -*-
"""extract_mda.py  从年报PDF定位并抽取"管理层讨论与分析"(及等价章节), 截断8000字
定位策略: ①标题在页首(优先) ②标题在页中(次之) ③"公司业务概要"节(老式年报兜底)
         逐个候选生成窗口, 用正文特征验证开头, 第一个通过者胜出; 失败记 logs/mda_miss.txt
"""
import os, re, sys
import pandas as pd
import pdfplumber

START_KWS = ["管理层讨论与分析", "经营情况讨论与分析", "董事会报告"]   # 2015年前老年报用"董事会报告"
FALLBACK_KWS = ["公司业务概要"]                                        # 部分年报将经营讨论并入该节
BUSI_MARKERS = ["报告期内", "营业收入", "主营业务", "毛利率", "同比", "经营情况", "一、概述"]
BAD_HEADS = ["重要提示", "备查文件"]
END_KWS = ["重要事项", "财务报告", "公司治理"]

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
    """开头必须是MD&A正文特征, 不能是重要提示/目录"""
    head = text[:400]
    if any(b in head[:80] for b in BAD_HEADS):
        return False
    return any(k in head for k in START_KWS + FALLBACK_KWS + BUSI_MARKERS)

def extract(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    cands = []          # (优先级, 页码)
    for i, t in enumerate(pages):
        if re.search(r"目\s*录", t[:300]):
            continue
        if any(k in t[:300] for k in START_KWS):
            cands.append((0, i))          # 标题在页首
        elif any(k in t for k in START_KWS):
            cands.append((1, i))          # 标题在页中(可能为封面小目录)
        elif any(k in t[:300] for k in FALLBACK_KWS):
            cands.append((2, i))          # 老式年报: 公司业务概要
    for _, i in sorted(cands):
        text = window(pages, i)
        if len(text) > 1500 and plausible(text):
            return text[:8000]
    for _, i in sorted(cands):            # 兜底: 最长窗口
        text = window(pages, i)
        if len(text) > 1500:
            return text[:8000]
    return None

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sample = pd.read_csv("data/tables/sample_all.csv")
    a_codes = set(pd.read_csv("data/tables/sample_a.csv").code.astype(str).str.zfill(6))
    n_ok = n_miss = 0
    for _, r in sample.iterrows():
        years = [int(r.year_t)] + ([int(r.year_t) - 1] if str(r.code).zfill(6) in a_codes else [])
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
