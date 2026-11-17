# -*- coding: utf-8 -*-
"""robustness.py  稳健性两件套:
① 抽样敏感性: 随机种子0/1/7重跑主对比(LogReg仅财务 vs LGBM财务+文本)
② Z′替代Z″(Altman私有公司五项版 0.717/0.847/3.107/0.420/0.998, 从原始三表重算)
输出 results/robustness.csv"""
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score, recall_score, confusion_matrix
from sklearn.model_selection import train_test_split

RAW = "data/raw"
df = pd.read_csv("data/tables/dataset.csv").dropna(subset=["z_prime2", "optimism"])
FIN = ["z_prime2", "m_score"] + [c for c in df.columns if c in (
        "dsri", "gmi", "aqi", "sgi", "depi", "sgai", "tata", "lvgi",
        "rec_gap", "inv_ratio", "gm_gap", "ocf_np", "other_rec", "cip_ratio",
        "goodwill_ne", "ta_turn_chg", "fa_turn_chg", "subsidy_pt", "double_high", "qualified_op")]
TXT = ["optimism", "risk", "vague", "mda_sim"]
rows = []

def run(tag, name, model, tr, te, cols):
    model.fit(tr[cols].fillna(-999), tr["fraud"])
    proba = model.predict_proba(te[cols].fillna(-999))[:, 1]
    pred = (proba >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(te["fraud"], pred).ravel()
    rows.append(dict(设定=tag, 模型=name, AUC=round(roc_auc_score(te["fraud"], proba), 3),
                     召回率=round(recall_score(te["fraud"], pred), 3),
                     误报率=round(fp / (fp + tn), 3)))

# ---- ① 抽样敏感性 ----
for seed in [0, 1, 7]:
    tr, te = train_test_split(df, test_size=0.3, stratify=df.fraud, random_state=seed)
    run(f"种子{seed}", "LogReg仅财务", LogisticRegression(class_weight="balanced", max_iter=5000), tr, te, FIN)
    run(f"种子{seed}", "LGBM财务+文本", LGBMClassifier(n_estimators=100, learning_rate=0.05,
                                                        class_weight="balanced", verbosity=-1, random_state=42), tr, te, FIN + TXT)

# ---- ② Z′替代 (从原始三表重算五项版) ----
def g(d, col, year):
    if d is None or col not in d.columns:
        return np.nan
    dd = d.copy(); dd["REPORT_DATE"] = pd.to_datetime(dd["REPORT_DATE"])
    hit = dd[dd["REPORT_DATE"].dt.year == year]
    return float(hit.iloc[-1][col]) if len(hit) else np.nan

z1 = {}
for _, r in df.iterrows():
    code, y = str(r.code).zfill(6), int(r.year_t)
    bf, pf = f"{RAW}/{code}_balance.csv", f"{RAW}/{code}_profit.csv"
    if not (os.path.exists(bf) and os.path.exists(pf)):
        continue
    bal, pro = pd.read_csv(bf), pd.read_csv(pf)
    ta = g(bal, "TOTAL_ASSETS", y)
    if pd.isna(ta) or ta == 0:
        continue
    x1 = (g(bal, "TOTAL_CURRENT_ASSETS", y) - g(bal, "TOTAL_CURRENT_LIAB", y)) / ta
    re_ = g(bal, "SURPLUS_RESERVE", y)
    up = g(bal, "UNASSIGN_RPOFIT", y)
    x2 = (re_ + (0 if pd.isna(up) else up)) / ta
    interest = g(pro, "FE_INTEREST_EXPENSE", y)
    if pd.isna(interest): interest = g(pro, "INTEREST_EXPENSE", y)
    if pd.isna(interest): interest = g(pro, "FINANCE_EXPENSE", y)
    ebit = g(pro, "OPERATE_PROFIT", y) + (0 if pd.isna(interest) else interest)
    x3 = ebit / ta
    tl = g(bal, "TOTAL_LIABILITIES", y); te_ = g(bal, "TOTAL_EQUITY", y)
    x4 = te_ / tl if (not pd.isna(tl) and tl != 0) else np.nan
    rv = g(pro, "OPERATE_INCOME", y)
    x5 = rv / ta if not pd.isna(rv) else np.nan
    z1[(code, y)] = 0.717*x1 + 0.847*x2 + 3.107*x3 + 0.420*x4 + 0.998*x5

df_z = df.copy()
df_z["z_prime1"] = [z1.get((str(r.code).zfill(6), int(r.year_t)), np.nan) for _, r in df.iterrows()]
print("Z′缺失率:", round(df_z.z_prime1.isna().mean(), 3))
FIN_Z = ["z_prime1", "m_score"] + FIN[2:]
for seed in [42]:
    tr, te = train_test_split(df_z, test_size=0.3, stratify=df_z.fraud, random_state=seed)
    run("Z′替代(种子42)", "LogReg仅财务", LogisticRegression(class_weight="balanced", max_iter=5000), tr, te, FIN_Z)
    run("Z′替代(种子42)", "LGBM财务+文本", LGBMClassifier(n_estimators=100, learning_rate=0.05,
                                                            class_weight="balanced", verbosity=-1, random_state=42), tr, te, FIN_Z + TXT)

out = pd.DataFrame(rows)
out.to_csv("results/robustness.csv", index=False, encoding="utf-8-sig")
print(out.to_string(index=False))
