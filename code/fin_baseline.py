# -*- coding: utf-8 -*-
"""fin_baseline.py  仅财务特征的基线模型(中期checkpoint用, 不需文本特征)
逻辑回归 + LightGBM, 分年度回测口径(训练<=2021/测试>=2022)与随机划分双口径
输出 results/fin_baseline.csv"""
import pandas as pd
from sklearn.linear_model import LogisticRegression
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score, recall_score, confusion_matrix
from sklearn.model_selection import train_test_split

df = pd.read_csv("data/tables/fin_features.csv").dropna(subset=["z_prime2"])
FIN = ["z_prime2", "m_score"] + [c for c in df.columns if c in (
        "dsri", "gmi", "aqi", "sgi", "depi", "sgai", "tata", "lvgi",
        "rec_gap", "inv_ratio", "gm_gap", "ocf_np", "other_rec", "cip_ratio",
        "goodwill_ne", "ta_turn_chg", "fa_turn_chg", "subsidy_pt", "double_high",
        "qualified_op", "auditor_chg", "exec_depart", "related_pct")]
y = df["fraud"]

def run(name, model, tr, te):
    model.fit(tr[FIN].fillna(-999), tr["fraud"])
    proba = model.predict_proba(te[FIN].fillna(-999))[:, 1]
    pred = (proba >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(te["fraud"], pred).ravel()
    return dict(模型=name, 样本=len(tr), 测试=len(te),
                AUC=round(roc_auc_score(te["fraud"], proba), 3),
                召回率=round(recall_score(te["fraud"], pred), 3),
                误报率=round(fp / (fp + tn), 3))

rows = []
# 口径1: 随机划分 70/30 (stratify)
tr, te = train_test_split(df, test_size=0.3, stratify=y, random_state=42)
rows.append(run("LogReg-随机划分", LogisticRegression(class_weight="balanced", max_iter=2000), tr, te))
rows.append(run("LGBM-随机划分", LGBMClassifier(n_estimators=300, learning_rate=0.05,
                                                class_weight="balanced", verbosity=-1), tr, te))
# 口径2: 分年度回测 (train<=2021, test>=2022)
tr2, te2 = df[df.year_t <= 2021], df[df.year_t >= 2022]
if len(te2) >= 6:
    rows.append(run("LogReg-年度回测", LogisticRegression(class_weight="balanced", max_iter=2000), tr2, te2))
    rows.append(run("LGBM-年度回测", LGBMClassifier(n_estimators=300, learning_rate=0.05,
                                                    class_weight="balanced", verbosity=-1), tr2, te2))
out = pd.DataFrame(rows)
out.to_csv("results/fin_baseline.csv", index=False, encoding="utf-8-sig")
print(out.to_string(index=False))
