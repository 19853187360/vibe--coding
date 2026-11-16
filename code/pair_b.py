# -*- coding: utf-8 -*-
"""pair_b.py  B组1:2配对: 同门类+同年度+总资产±30%
  前提: ①data/raw里已有A组的balance  ②candidate_pool.csv已备好
  动作: 自动拉候选池资产负债表取总资产 → 配对 → 输出sample_all.csv"""
import os, time
import pandas as pd
import akshare as ak

def mkt(code):
    c = str(code).zfill(6)
    return ("SH" if c[0] in "69" else "SZ") + c

a = pd.read_csv("data/tables/sample_a.csv")
pool = pd.read_csv("data/tables/candidate_pool.csv")
pool = pool[~pool.code.isin(a.code)].drop_duplicates("code")

def get_ta(code, year):                    # 拉一次balance取year年报总资产
    f = f"data/raw/{str(code).zfill(6)}_balance.csv"
    if not os.path.exists(f):
        try:
            df = ak.stock_balance_sheet_by_report_em(symbol=mkt(code))
            if df is None or df.empty:
                df = ak.stock_balance_sheet_by_report_delisted_em(symbol=mkt(code))
            df.to_csv(f, index=False, encoding="utf-8-sig"); time.sleep(1.8)
        except Exception:
            return None
    df = pd.read_csv(f)
    df["REPORT_DATE"] = pd.to_datetime(df["REPORT_DATE"])
    hit = df[df["REPORT_DATE"].dt.year == year]
    return float(hit.iloc[-1]["TOTAL_ASSETS"]) if len(hit) else None

a["total_assets"] = [get_ta(c, y) for c, y in zip(a.code, a.year_t)]   # A组t期总资产
pool["total_assets"] = [get_ta(c, y) for c, y in zip(pool.code, pool.year)]

rows = []
for _, ra in a.dropna(subset=["total_assets"]).iterrows():
    cand = pool.dropna(subset=["total_assets"])
    cand = cand[(cand.industry_l1 == ra.industry_l1) & (cand.year == ra.year_t)
                & (cand.total_assets / ra.total_assets).between(0.7, 1.3)]
    if len(cand) < 2:   # 不足2家 → 放宽±50%
        cand = pool.dropna(subset=["total_assets"])
        cand = cand[(cand.industry_l1 == ra.industry_l1) & (cand.year == ra.year_t)
                    & (cand.total_assets / ra.total_assets).between(0.5, 2.0)]
        print(f"提示: {ra.company} 已放宽到±50%")
    for _, rb in cand.sort_values("total_assets").head(2).iterrows():
        rows.append(dict(code=rb.code, company=rb.company, industry_l1=rb.industry_l1,
                         year_t=int(ra.year_t), fraud=0, matched_to=ra.code))
b = pd.DataFrame(rows)
allrows = pd.concat([a.assign(fraud=1, matched_to=a.code), b], ignore_index=True)
allrows["year_t"] = allrows["year_t"].astype(int)
allrows.to_csv("data/tables/sample_all.csv", index=False, encoding="utf-8-sig")
print(f"A组{sum(allrows.fraud)}行 + B组{sum(1-allrows.fraud)}行 = {len(allrows)}行 (目标90-150)")
