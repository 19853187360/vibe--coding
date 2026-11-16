# -*- coding: utf-8 -*-
"""build_features.py  财务特征表: Z'' + M-score 8指数 + 11数值红旗 (4事件红旗由events.xlsx合并)
⚠ Beneish系数按原文(Beneish 1999, FAJ 55(5))对应: 0.115→DEPI, -0.172→SGAI, -0.327→LVGI
  (教程手册曾把系数挂错变量名, 见 lit_check.xlsx 疑点记录; 此处已按原文修正)
用法: py -3.14 code\\build_features.py            # 全样本
      py -3.14 code\\build_features.py 600518 2016 # 单家手算核对(康美验收)
"""
import os, sys
import numpy as np
import pandas as pd

RAW = "data/raw"

def sheet(code, name):
    f = f"{RAW}/{str(code).zfill(6)}_{name}.csv"
    if not os.path.exists(f):
        return None
    df = pd.read_csv(f)
    df["REPORT_DATE"] = pd.to_datetime(df["REPORT_DATE"])
    return df.sort_values("REPORT_DATE").reset_index(drop=True)

def g(df, col, year):     # 取year年度年报某字段(年报按REPORT_DATE年匹配)
    if df is None or col not in df.columns:
        return np.nan
    hit = df[df["REPORT_DATE"].dt.year == year]
    return float(hit.iloc[-1][col]) if len(hit) else np.nan

def first(df, year, names):   # 从候选字段名里取第一个存在且非空的
    if df is None:
        return np.nan
    for c in names:
        v = g(df, c, year)
        if not pd.isna(v):
            return v
    return np.nan

def ratio(x, y):
    try:
        return x / y if (not pd.isna(x) and not pd.isna(y) and y != 0) else np.nan
    except Exception:
        return np.nan

# 单家手算核对模式: py -3.14 code\build_features.py 600518 2016
if len(sys.argv) >= 3:
    code, y = sys.argv[1], int(sys.argv[2])
    bal, pro, cas = sheet(code, "balance"), sheet(code, "profit"), sheet(code, "cashflow")
    ta = g(bal, "TOTAL_ASSETS", y); tcl = g(bal, "TOTAL_CURRENT_LIAB", y)
    tca = g(bal, "TOTAL_CURRENT_ASSETS", y)
    re_ = g(bal, "SURPLUS_RESERVE", y) + g(bal, "UNDISTRIBUTE_PROFIT", y)
    ebit = g(pro, "OPERATE_PROFIT", y) + g(pro, "INTEREST_EXPENSE", y)
    tl, te = g(bal, "TOTAL_LIABILITIES", y), g(bal, "TOTAL_EQUITY", y)
    x1, x2, x3, x4 = ratio(tca - tcl, ta), ratio(re_, ta), ratio(ebit, ta), ratio(te, tl)
    print(f"{code} {y}年: X1={x1:.4f} X2={x2:.4f} X3={x3:.4f} X4={x4:.4f}")
    print(f"Z'' = 6.56*{x1:.4f} + 3.26*{x2:.4f} + 6.72*{x3:.4f} + 1.05*{x4:.4f} = {6.56*x1+3.26*x2+6.72*x3+1.05*x4:.4f}")
    sys.exit(0)

sample = pd.read_csv("data/tables/sample_all.csv")
events = None
if os.path.exists("data/tables/events.xlsx"):
    events = pd.read_excel("data/tables/events.xlsx")     # D3手工记, 模板见附录C

rows = []
for _, r in sample.iterrows():
    code, y = str(r.code).zfill(6), int(r.year_t)
    bal, pro = sheet(code, "balance"), sheet(code, "profit")
    cas = sheet(code, "cashflow")
    ta   = g(bal, "TOTAL_ASSETS", y)
    ta_p = g(bal, "TOTAL_ASSETS", y - 1)
    tca, tcl = g(bal, "TOTAL_CURRENT_ASSETS", y), g(bal, "TOTAL_CURRENT_LIAB", y)
    re_ = g(bal, "SURPLUS_RESERVE", y) + g(bal, "UNDISTRIBUTE_PROFIT", y)
    ebit = g(pro, "OPERATE_PROFIT", y) + g(pro, "INTEREST_EXPENSE", y)
    tl, te = g(bal, "TOTAL_LIABILITIES", y), g(bal, "TOTAL_EQUITY", y)
    tl_p, te_p = g(bal, "TOTAL_LIABILITIES", y-1), g(bal, "TOTAL_EQUITY", y-1)
    # ---- Z'' (Altman 1983 新兴市场版; 系数以 lit_check 核对原文为准) ----
    x1, x2, x3, x4 = ratio(tca - tcl, ta), ratio(re_, ta), ratio(ebit, ta), ratio(te, tl)
    z2 = 6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4
    # ---- M-score 8 指数 (全部为 t 与 t-1 两期对比; Beneish 1999 原文系数) ----
    ar_t, ar_p = g(bal, "ACCOUNTS_RECE", y), g(bal, "ACCOUNTS_RECE", y - 1)
    rv_t, rv_p = g(pro, "OPERATE_INCOME", y), g(pro, "OPERATE_INCOME", y - 1)
    oc_t, oc_p = g(pro, "OPERATE_COST", y), g(pro, "OPERATE_COST", y - 1)
    gm_t = ratio(rv_t - oc_t, rv_t); gm_p = ratio(rv_p - oc_p, rv_p)
    dsri = ratio(ratio(ar_t, rv_t), ratio(ar_p, rv_p))          # 应收天数指数
    gmi  = ratio(gm_p, gm_t)                                    # 毛利率指数
    ca_fa_t = g(bal, "TOTAL_CURRENT_ASSETS", y) + g(bal, "FIXED_ASSET", y)
    ca_fa_p = g(bal, "TOTAL_CURRENT_ASSETS", y-1) + g(bal, "FIXED_ASSET", y-1)
    aqi  = ratio(ratio(ta - ca_fa_t, ta), ratio(ta_p - ca_fa_p, ta_p))  # 资产质量指数
    sgi  = ratio(rv_t, rv_p)                                    # 销售增长指数
    dep_t = first(cas, y,   ["DEPR_FIXED_ASSET", "FIXED_ASSETS_DEPR", "DEPRECIATION", "DEPR_OCFA"])
    dep_p = first(cas, y-1, ["DEPR_FIXED_ASSET", "FIXED_ASSETS_DEPR", "DEPRECIATION", "DEPR_OCFA"])
    fa_t, fa_p = g(bal, "FIXED_ASSET", y), g(bal, "FIXED_ASSET", y - 1)
    depr_t = ratio(dep_t, dep_t + fa_t); depr_p = ratio(dep_p, dep_p + fa_p)
    depi  = ratio(depr_p, depr_t)                               # 折旧指数
    exp_t = g(pro, "SALE_EXPENSE", y) + g(pro, "MANAGE_EXPENSE", y)
    exp_p = g(pro, "SALE_EXPENSE", y-1) + g(pro, "MANAGE_EXPENSE", y-1)
    sgai  = ratio(ratio(exp_p, rv_p), ratio(exp_t, rv_t))       # 费用指数
    ocf, npf = g(cas, "NETCASH_OPERATE", y), g(pro, "NETPROFIT", y)
    tata  = ratio(npf - ocf, ta)                                # 应计/总资产
    lvgi  = ratio(ratio(tl, ta), ratio(tl_p, ta_p))             # 杠杆指数
    m = (-4.84 + 0.920 * dsri + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi
         + 0.115 * depi - 0.172 * sgai + 4.679 * tata - 0.327 * lvgi)
    # ---- 11 数值红旗 ----
    rec_gap = ratio(ratio(ar_t - ar_p, ar_p), ratio(rv_t - rv_p, rv_p))  # 应收增速/营收增速
    rows.append(dict(
        code=code, company=r.company, year_t=y, fraud=int(r.fraud),
        industry_l1=r.industry_l1, matched_to=r.matched_to, total_assets=ta,
        z_prime2=z2, m_score=m,
        dsri=dsri, gmi=gmi, aqi=aqi, sgi=sgi, depi=depi, sgai=sgai, tata=tata, lvgi=lvgi,
        rec_gap=rec_gap,                                        # 红旗1
        inv_ratio=ratio(g(bal, "INVENTORY", y), ta),            # 红旗2
        gm_t=gm_t,                                              # (gm_gap 全表算完再减行业中位)
        ocf_np=ratio(ocf, npf),                                 # 红旗4
        other_rec=ratio(g(bal, "OTHER_RECEIVABLES", y), ta),    # 红旗5
        fa_turn_chg=ratio(ratio(rv_t, fa_t), ratio(rv_p, fa_p)),# 红旗6 固定资产周转率变化
        ta_turn_chg=ratio(ratio(rv_t, ta), ratio(rv_p, ta_p)),  # 红旗7 总资产周转率变化(替代员工数)
        cip_ratio=ratio(g(bal, "CIP", y), ta),                  # 红旗8
        goodwill_ne=ratio(g(bal, "GOODWILL", y), te),           # 红旗14
        subsidy_pt=ratio(first(pro, y, ["SUBSIDIZE_INCOME", "SUBSIDY_INCOME", "OTHER_INCOME"]),
                         g(pro, "TOTAL_PROFIT", y)),            # 红旗15
    ))

feats = pd.DataFrame(rows)
# 毛利率-行业中位数(红旗3) 与 存贷双高(红旗9, 均高于行业中位数记1)
feats["gm_gap"] = feats.gm_t - feats.groupby("industry_l1").gm_t.transform("median")
feats["cash_hi"] = feats["inv_ratio"].groupby(feats["industry_l1"]).transform(lambda s: s > s.median())  # 占位(被下面覆盖)
# 存贷双高: 货币资金/总资产 与 短期借款/总资产 均高于行业中位数
for _, r in sample.iterrows():
    code, y = str(r.code).zfill(6), int(r.year_t)
    bal = sheet(code, "balance")
    ta_ = g(bal, "TOTAL_ASSETS", y)
    feats.loc[feats.code.eq(code) & feats.year_t.eq(y), "cash_ta"] = ratio(g(bal, "MONETARYFUNDS", y), ta_)
    feats.loc[feats.code.eq(code) & feats.year_t.eq(y), "loan_ta"] = ratio(g(bal, "SHORT_LOAN", y), ta_)
for ind in feats.industry_l1.unique():
    m = feats.industry_l1.eq(ind)
    mh_c = feats.loc[m, "cash_ta"].median(); mh_l = feats.loc[m, "loan_ta"].median()
    feats.loc[m, "double_high"] = ((feats.loc[m, "cash_ta"] > mh_c) & (feats.loc[m, "loan_ta"] > mh_l)).astype(int)
feats = feats.drop(columns=["cash_hi"])

if events is not None:
    feats = feats.merge(events, on=["code", "year_t"], how="left")
feats.to_csv("data/tables/fin_features.csv", index=False, encoding="utf-8-sig")
print(feats.isna().mean().round(3).sort_values(ascending=False).head(10))
print("行数:", len(feats))
