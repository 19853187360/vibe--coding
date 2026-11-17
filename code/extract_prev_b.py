# -*- coding: utf-8 -*-
"""extract_prev_b.py  抽取全部87家t-1期MD&A(前置检验用; A组t-1已抽则跳过)"""
import os, sys
import pandas as pd
sys.path.insert(0, "code")
from extract_mda import extract

sample = pd.read_csv("data/tables/sample_all.csv")
sample["code"] = sample.code.astype(str).str.zfill(6)
n_ok = n_miss = n_skip = 0
for _, r in sample.iterrows():
    code, yr = r.code, int(r.year_t) - 1
    pdf = f"pdfs/{code}_{yr}.pdf"
    out = f"data/mdas/{code}_{yr}.txt"
    if not os.path.exists(pdf) or os.path.exists(out):
        n_skip += 1
        continue
    txt = extract(pdf)
    if txt:
        open(out, "w", encoding="utf-8").write(txt); n_ok += 1
    else:
        open("logs/mda_miss.txt", "a", encoding="utf-8").write(pdf + "\n"); n_miss += 1
print(f"t-1抽取: 成功{n_ok} / 失败{n_miss} / 跳过{n_skip}")
