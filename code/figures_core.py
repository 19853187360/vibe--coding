# -*- coding: utf-8 -*-
"""figures_core.py  图1 ROC / 图2 特征重要性 / 图3 相似度箱线 / 图4 Z''-M散点"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]   # 中文防豆腐块
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv("data/tables/dataset.csv").dropna(subset=["z_prime2", "optimism"])

# 图1 ROC: 用backtest.py同口径的两模型概率重画并叠加基线对角线 → paper/f1_roc.png
from lightgbm import LGBMClassifier
from sklearn.linear_model import LogisticRegression
FIN = ["z_prime2", "m_score", "dsri", "gmi", "aqi", "sgi", "depi", "sgai", "tata", "lvgi",
       "rec_gap", "inv_ratio", "gm_gap", "ocf_np", "other_rec", "cip_ratio",
       "goodwill_ne", "ta_turn_chg", "fa_turn_chg", "subsidy_pt", "double_high",
       "qualified_op", "auditor_chg", "exec_depart", "related_pct"]
TXT = ["optimism", "risk", "vague", "mda_sim"]
tr = df[df.year_t <= 2021]; te = df[df.year_t >= 2022]

fig, ax = plt.subplots(figsize=(6, 6), dpi=300)
for name, cols, model in [
    ("基线(仅财务)", FIN, LogisticRegression(class_weight="balanced", max_iter=2000)),
    ("改进(财务+文本)", FIN + TXT, LGBMClassifier(n_estimators=300, learning_rate=0.05,
                                                  class_weight="balanced", verbosity=-1))]:
    model.fit(tr[cols].fillna(-999), tr["fraud"])
    p = model.predict_proba(te[cols].fillna(-999))[:, 1]
    fpr, tpr, _ = roc_curve(te["fraud"], p)
    ax.plot(fpr, tpr, label=f"{name} (AUC={auc(fpr, tpr):.3f})")
ax.plot([0, 1], [0, 1], "k--", lw=0.8)
ax.set_xlabel("误报率 FPR"); ax.set_ylabel("命中率 TPR (召回)")
ax.set_title("图1 财务舞弊识别 ROC：基线 vs 财务+文本")
ax.legend(loc="lower right")
fig.savefig("paper/f1_roc.png"); plt.close(fig)

# 图2: LGBM.feature_importances_ 排序取前10横向条形 → paper/f2_importance.png
lgb = LGBMClassifier(n_estimators=300, learning_rate=0.05,
                     class_weight="balanced", verbosity=-1)
lgb.fit(df[FIN + TXT].fillna(-999), df["fraud"])
imp = pd.Series(lgb.feature_importances_, index=FIN + TXT).sort_values().tail(10)
fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
colors = ["#C0392B" if c in TXT else "#2E86C1" for c in imp.index]
ax.barh(imp.index, imp.values, color=colors)
ax.set_title("图2 LightGBM 特征重要性 Top10（红=文本特征，蓝=财务特征）")
fig.tight_layout(); fig.savefig("paper/f2_importance.png"); plt.close(fig)

# 图3: dataset按fraud分组画mda_sim箱线图 → paper/f3_sim.png
if "mda_sim" in df.columns:
    fig, ax = plt.subplots(figsize=(5, 5), dpi=300)
    ax.boxplot([df[df.fraud == 0].mda_sim.dropna(), df[df.fraud == 1].mda_sim.dropna()],
               tick_labels=["对照B组", "舞弊A组"])
    ax.set_ylabel("MD&A 年度间相似度")
    ax.set_title("图3 A/B 组文本相似度分布")
    fig.savefig("paper/f3_sim.png"); plt.close(fig)

# 图4: Z''为x轴, M为y轴, 颜色=fraud, 横线M=-2.22, 竖线Z''=1.1 → paper/f4_zm.png
fig, ax = plt.subplots(figsize=(6, 6), dpi=300)
for f, c, lab in [(0, "#2E86C1", "对照B组"), (1, "#C0392B", "舞弊A组")]:
    d = df[df.fraud == f]
    ax.scatter(d.z_prime2, d.m_score, s=18, c=c, label=lab, alpha=0.7)
ax.axhline(-2.22, color="k", ls="--", lw=0.8, label="M=-2.22 阈值")
ax.axvline(1.1, color="k", ls=":", lw=0.8, label="Z''=1.1 阈值")
ax.set_xlabel("Z'' 分数"); ax.set_ylabel("M-score")
ax.set_title("图4 Z″—M 双轴散点")
ax.legend()
fig.savefig("paper/f4_zm.png"); plt.close(fig)

print("4图已存 paper/ (D4有真实数据后按此脚本口径重跑)")
