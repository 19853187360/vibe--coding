# -*- coding: utf-8 -*-
"""baseline_first.py  基线(逻辑回归, 仅财务) vs 改进(LightGBM, 财务+文本)
  指标三件: AUC / 召回率(命中) / 误报率(FPR); 报告不平衡样本的合理指标"""
import pandas as pd
from sklearn.linear_model import LogisticRegression
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score, recall_score, confusion_matrix
from sklearn.model_selection import train_test_split

df = pd.read_csv("data/tables/dataset.csv").dropna(subset=["z_prime2", "optimism"])
FIN = ["z_prime2", "m_score"] + [c for c in df.columns if c in (
        "dsri", "gmi", "aqi", "sgi", "depi", "sgai", "tata", "lvgi",
        "rec_gap", "inv_ratio", "gm_gap", "ocf_np", "other_rec", "cip_ratio",
        "goodwill_ne", "ta_turn_chg", "fa_turn_chg", "subsidy_pt", "double_high",
        "qualified_op", "auditor_chg", "exec_depart", "related_pct")]
TXT = ["optimism", "risk", "vague", "mda_sim"]
y = df["fraud"]
tr, te = train_test_split(df, test_size=0.3, stratify=y, random_state=42)

def run(name, cols, model):
    model.fit(tr[cols].fillna(-999), tr["fraud"])
    proba = model.predict_proba(te[cols].fillna(-999))[:, 1]
    pred = (proba >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(te["fraud"], pred).ravel()
    return dict(模型=name, AUC=round(roc_auc_score(te["fraud"], proba), 3),
                召回率=round(recall_score(te["fraud"], pred), 3),
                误报率=round(fp / (fp + tn), 3))

res = [
    run("基线: 逻辑回归(仅财务)", FIN, LogisticRegression(class_weight="balanced", max_iter=2000)),
    run("改进: LightGBM(财务+文本)", FIN + TXT, LGBMClassifier(
        n_estimators=300, learning_rate=0.05, class_weight="balanced", verbosity=-1)),
]
out = pd.DataFrame(res)
out.to_csv("results/main_result_v1.csv", index=False, encoding="utf-8-sig")
print(out.to_string(index=False))
print("\n文末增益 = 改进AUC - 基线AUC =", round(out.AUC.iloc[1] - out.AUC.iloc[0], 3))
