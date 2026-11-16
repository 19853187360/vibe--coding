# -*- coding: utf-8 -*-
"""backtest.py  分年度回测: train=2019-2021 → test=2022-2023
  注: FIN/TXT 两个列表从 baseline_first.py 复制过来(不要import, 那样会重跑首轮实验)"""
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score, recall_score, confusion_matrix

FIN = ["z_prime2", "m_score", "dsri", "gmi", "aqi", "sgi", "depi", "sgai", "tata", "lvgi",
       "rec_gap", "inv_ratio", "gm_gap", "ocf_np", "other_rec", "cip_ratio",
       "goodwill_ne", "ta_turn_chg", "fa_turn_chg", "subsidy_pt", "double_high",
       "qualified_op", "auditor_chg", "exec_depart", "related_pct"]
TXT = ["optimism", "risk", "vague", "mda_sim"]

df = pd.read_csv("data/tables/dataset.csv").dropna(subset=["z_prime2", "optimism"])
tr = df[df.year_t <= 2021]; te = df[df.year_t >= 2022]
for name, cols in [("基线(仅财务)", FIN), ("改进(财务+文本)", FIN + TXT)]:
    m = LGBMClassifier(n_estimators=300, learning_rate=0.05,
                       class_weight="balanced", verbosity=-1)
    m.fit(tr[cols].fillna(-999), tr["fraud"])
    proba = m.predict_proba(te[cols].fillna(-999))[:, 1]
    pred = (proba >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(te["fraud"], pred).ravel()
    print(f"{name}  AUC={roc_auc_score(te['fraud'], proba):.3f}  "
          f"召回={recall_score(te['fraud'], pred):.3f}  误报={fp/(fp+tn):.3f}")
# 手工把输出抄进 results/backtest.csv(模型,期间,AUC,召回,误报)
# 前置检验(t-1)操作序列:
# ① s = pd.read_csv("data/tables/sample_all.csv"); s["year_t"] = s["year_t"] - 1
#    s.to_csv("data/tables/sample_prev.csv", index=False, encoding="utf-8-sig")
# ② 用 sample_prev.csv 再跑 build_features.py(输出名改为 fin_features_prev.csv)
# ③ data/mdas/ 里 t-1 文件已被 llm_score.py 打过(A组), 按 merge_features 方式合成 dataset_prev.csv
# ④ 再跑本脚本得 AUC/召回 → 论文表述: "以 t-1 期信号预测 t 期被查处的公司, 改进模型AUC仍为X"
