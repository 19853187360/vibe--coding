# -*- coding: utf-8 -*-
"""lead_test.py  前置性检验: 以t-1期信号(上年财务+上年文本)预测t期被查处
训练: t期特征; 测试: 同观测的t-1期特征, 标签不变(A=1/B=0)
口径1: 随机划分42; 口径2: 年度划分(训练<=2016, 测试>=2017)"""
import pandas as pd
from sklearn.linear_model import LogisticRegression
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score, recall_score, confusion_matrix
from sklearn.model_selection import train_test_split
import json, numpy as np

FIN = ["z_prime2", "m_score", "dsri", "gmi", "aqi", "sgi", "depi", "sgai", "tata", "lvgi",
       "rec_gap", "inv_ratio", "gm_gap", "ocf_np", "other_rec", "cip_ratio",
       "goodwill_ne", "ta_turn_chg", "fa_turn_chg", "subsidy_pt", "double_high", "qualified_op"]
TXT = ["optimism", "risk", "vague"]   # t-1的mda_sim需t-2文本, 本检验不含(论文注明)

# ---- dataset (t期) ----
df = pd.read_csv("data/tables/dataset.csv").dropna(subset=["z_prime2", "optimism"])
df = df[FIN + TXT + ["code", "year_t", "fraud", "file"]]

# ---- dataset_prev (t-1期特征, 行与标签同t期) ----
fp = pd.read_csv("data/tables/fin_features_prev.csv")
fp["code"] = fp.code.astype(str).str.replace(".0", "", regex=False).str.zfill(6)
fp["file_prev"] = fp.code + "_" + fp.year_t.astype(int).astype(str)
scores = {}
for line in open("logs/llm_scores.jsonl", encoding="utf-8"):
    d = json.loads(line); scores[d["file"]] = d
sc = pd.DataFrame([{"file_prev": k, "optimism": v["optimism"], "risk": v["risk"],
                    "vague": v["vague"]} for k, v in scores.items()])
prev = fp.merge(sc, on="file_prev", how="left")
prev["ln_ta"] = np.log(prev["total_assets"].clip(lower=1))
dum = pd.get_dummies(prev["industry_l1"], prefix="ind", dummy_na=True).astype(int)
prev = pd.concat([prev, dum], axis=1)
prev = prev[df.file.tolist()] if False else prev   # 占位
# 对齐: t期file → t-1期file(同code, year-1)
prev["file_t"] = prev.code + "_" + (prev.year_t + 1).astype(int).astype(str)
prev = prev[prev.file_t.isin(df.file)]
prev.to_csv("data/tables/dataset_prev.csv", index=False, encoding="utf-8-sig")

def run(name, model, tr_df, te_prev):
    """tr_df: 训练行(t期特征); te_prev: 测试行(t-1期特征), 含fraud标签"""
    Xtr, ytr = tr_df[FIN + TXT].fillna(-999), tr_df["fraud"]
    model.fit(Xtr, ytr)
    proba = model.predict_proba(te_prev[FIN + TXT].fillna(-999))[:, 1]
    pred = (proba >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(te_prev["fraud"], pred).ravel()
    return dict(设定=name, AUC=round(roc_auc_score(te_prev["fraud"], proba), 3),
                召回率=round(recall_score(te_prev["fraud"], pred), 3),
                误报率=round(fp / (fp + tn), 3))

rows = []
# 口径1: 随机划分42
tr_idx, te_idx = train_test_split(df.index, test_size=0.3, stratify=df.fraud, random_state=42)
te_prev = prev[prev.file_t.isin(df.loc[te_idx, "file"])]
te_prev = te_prev.merge(df[["file", "fraud"]], left_on="file_t", right_on="file", suffixes=("", "_t"))
rows.append(run("前置检验-随机划分(LogReg)", LogisticRegression(class_weight="balanced", max_iter=5000), df.loc[tr_idx], te_prev))
rows.append(run("前置检验-随机划分(LGBM)", LGBMClassifier(n_estimators=100, learning_rate=0.05,
                                                          class_weight="balanced", verbosity=-1, random_state=42), df.loc[tr_idx], te_prev))
# 口径2: 年度划分
tr_y = df[df.year_t <= 2016]
te_y = prev[prev.year_t >= 2016]   # prev.year_t = t-1 → t>=2017
te_y = te_y.merge(df[["file", "fraud"]], left_on="file_t", right_on="file", suffixes=("", "_t"))
rows.append(run("前置检验-年度划分(LogReg)", LogisticRegression(class_weight="balanced", max_iter=5000), tr_y, te_y))
rows.append(run("前置检验-年度划分(LGBM)", LGBMClassifier(n_estimators=100, learning_rate=0.05,
                                                          class_weight="balanced", verbosity=-1, random_state=42), tr_y, te_y))
out = pd.DataFrame(rows)
out.to_csv("results/lead_test.csv", index=False, encoding="utf-8-sig")
print(out.to_string(index=False))
