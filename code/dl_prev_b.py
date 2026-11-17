# -*- coding: utf-8 -*-
"""dl_prev_b.py  B组t-1年报PDF下载(前置检验用: 全部87家的t-1期特征)
用法: py -3.14 code\\dl_prev_b.py"""
import os, sys, time
import pandas as pd
sys.path.insert(0, "code")
from download_pdfs import download

sample = pd.read_csv("data/tables/sample_all.csv")
sample["code"] = sample.code.astype(str).str.zfill(6)
tasks = [(r.code, int(r.year_t) - 1, r.get("company", "")) for _, r in sample.iterrows()]
n_ok = n_exist = n_fail = 0
for i, (code, year, comp) in enumerate(tasks, 1):
    pdf = f"pdfs/{code}_{year}.pdf"
    if os.path.exists(pdf):
        n_exist += 1
        print(f"[{i}/{len(tasks)}] {code}_{year} {comp}: EXISTS")
        continue
    res = download(code, year)
    if res.startswith("OK"):
        n_ok += 1
    else:
        n_fail += 1
        open("logs/pdf_errors.txt", "a", encoding="utf-8").write(f"{code}_{year} {comp} {res}\n")
    print(f"[{i}/{len(tasks)}] {code}_{year} {comp}: {res}")
    time.sleep(0.8)
print(f"t-1下载: 新{n_ok} / 已有{n_exist} / 失败{n_fail}")
