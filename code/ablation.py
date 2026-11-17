# -*- coding: utf-8 -*-
"""ablation.py  消融实验: 同模型同切分下 仅财务 / 仅文本 / 财务+文本
消除"换模型"混杂: 三个设定都用LightGBM(同样超参) + 随机划分(random_state=42)"""
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, recall_score, confusion_matrix
from sklearn.model_selection import train_test_split

df = pd.read_csv("data/tables/dataset.csv").dropna(subset=["z_prime2", "optimism"])
FIN = ["z_prime2", "m_score"] + [c for c in df.columns if c in (
        "dsri", "gmi", "aqi", "sgi", "depi", "sgai", "tata", "lvgi",
        "rec_gap", "inv_ratio", "gm_gap", "ocf_np", "other_rec", "cip_ratio",
        "goodwill_ne", "ta_turn_chg", "fa_turn_chg", "subsidy_pt", "double_high",
        "qualified_op", "auditor_chg", "exec_depart", "related_pct")]
TXT = ["optimism", "risk", "vague", "mda_sim"]

tr, te = train_test_split(df, test_size=0.3, stratify=df["fraud"], random_state=42)

def run(name, cols, model):
    model.fit(tr[cols].fillna(-999), tr["fraud"])
    proba = model.predict_proba(te[cols].fillna(-999))[:, 1]
    pred = (proba >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(te["fraud"], pred).ravel()
    return dict(设定=name, AUC=round(roc_auc_score(te["fraud"], proba), 3),
                召回率=round(recall_score(te["fraud"], pred), 3),
                误报率=round(fp / (fp + tn), 3))

lgb = dict(n_estimators=100, learning_rate=0.05, class_weight="balanced", verbosity=-1, random_state=42)
res = [
    run("LGBM 仅财务", FIN, LGBMClassifier(**lgb)),
    run("LGBM 仅文本", TXT, LGBMClassifier(**lgb)),
    run("LGBM 财务+文本", FIN + TXT, LGBMClassifier(**lgb)),
    run("LogReg 仅财务", FIN, LogisticRegression(class_weight="balanced", max_iter=5000)),
    run("LogReg 财务+文本", FIN + TXT, LogisticRegression(class_weight="balanced", max_iter=5000)),
]
out = pd.DataFrame(res)
out.to_csv("results/ablation.csv", index=False, encoding="utf-8-sig")
print(out.to_string(index=False))
print("\n消融结论: 仅财务 vs 财务+文本 的AUC差 =",
      round(out[out.设定=="LGBM 财务+文本"].AUC.iloc[0] - out[out.设定=="LGBM 仅财务"].AUC.iloc[0], 3))
