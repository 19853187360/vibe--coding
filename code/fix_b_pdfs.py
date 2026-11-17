# -*- coding: utf-8 -*-
"""fix_b_pdfs.py  B组年报缺失的公司(多因该年度尚未上市) → 依次尝试池中下一候选, 直至成功
跑完 download_pdfs.py 后执行: 检查每个B组观测的t期PDF, 缺则按TA差距顺序换候选并即时下载。
"""
import os, sys
import pandas as pd
sys.path.insert(0, "code")
from download_pdfs import download  # 复用下载函数

sample = pd.read_csv("data/tables/sample_all.csv")
pool = pd.read_csv("data/tables/candidate_pool.csv")
pool["code"] = pool.code.astype(str).str.zfill(6)
sample["code"] = sample.code.astype(str).str.zfill(6)

used = set(sample.code)

def get_ta(code, year):
    f = f"data/raw/{code}_balance.csv"
    if not os.path.exists(f):
        return None
    df = pd.read_csv(f)
    df["REPORT_DATE"] = pd.to_datetime(df["REPORT_DATE"])
    hit = df[df["REPORT_DATE"].dt.year == year]
    return float(hit.iloc[-1]["TOTAL_ASSETS"]) if len(hit) else None

a_ta = {c: get_ta(c, y) for c, y in zip(sample[sample.fraud == 1].code, sample[sample.fraud == 1].year_t)}
pool["ta"] = [get_ta(c, y) for c, y in zip(pool.code, pool.year)]

changed = 0
for idx, r in sample[sample.fraud == 0].iterrows():
    code, year = r.code, int(r.year_t)
    pdf = f"pdfs/{code}_{year}.pdf"
    if os.path.exists(pdf):
        continue
    # 同行业同年度候选, 按TA差距排序(相对原A组公司)
    a_code = str(r.matched_to).zfill(6)
    ta_a = a_ta.get(a_code)
    cand = pool[(pool.industry_l1 == r.industry_l1) & (pool.year == year) & (~pool.code.isin(used))]
    if ta_a is not None:
        cand = cand.assign(gap=(cand.ta / ta_a - 1).abs())
        cand = cand.sort_values("gap")
    for _, cb in cand.iterrows():
        res = download(cb.code, year)
        if res.startswith("OK") or res == "EXISTS":
            sample.at[idx, "code"] = cb.code
            sample.at[idx, "company"] = cb.company
            sample.at[idx, "pair_mode"] = str(sample.at[idx, "pair_mode"]) + "→替换"
            used.add(cb.code)
            changed += 1
            print(f"替换 {a_code} 的对照: {r.code}({r.company}) → {cb.code}({cb.company}) {res}")
            break
        else:
            print(f"  跳过 {cb.code} {cb.company}: {res}")

sample.to_csv("data/tables/sample_all.csv", index=False, encoding="utf-8-sig")
print(f"共替换 {changed} 家B组公司")
