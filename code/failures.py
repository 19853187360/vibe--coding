# -*- coding: utf-8 -*-
"""failures.py  失败案例分析: 改进模型漏掉的A组(假阴性)与误伤的B组(假阳性)
输出 paper/failures.md (论文'失败案例与局限'节素材)"""
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split

df = pd.read_csv("data/tables/dataset.csv").dropna(subset=["z_prime2", "optimism"])
FIN = ["z_prime2", "m_score"] + [c for c in df.columns if c in (
        "dsri", "gmi", "aqi", "sgi", "depi", "sgai", "tata", "lvgi",
        "rec_gap", "inv_ratio", "gm_gap", "ocf_np", "other_rec", "cip_ratio",
        "goodwill_ne", "ta_turn_chg", "fa_turn_chg", "subsidy_pt", "double_high",
        "qualified_op", "auditor_chg", "exec_depart", "related_pct")]
TXT = ["optimism", "risk", "vague", "mda_sim"]

tr, te = train_test_split(df, test_size=0.3, stratify=df["fraud"], random_state=42)
m = LGBMClassifier(n_estimators=100, learning_rate=0.05, class_weight="balanced",
                   verbosity=-1, random_state=42)
m.fit(tr[FIN + TXT].fillna(-999), tr["fraud"])
te = te.assign(pred=m.predict(te[FIN + TXT].fillna(-999)),
               proba=m.predict_proba(te[FIN + TXT].fillna(-999))[:, 1])

fn = te[(te.fraud == 1) & (te.pred == 0)]
fp = te[(te.fraud == 0) & (te.pred == 1)]
print("假阴性(A组漏掉):", len(fn), "| 假阳性(B组误伤):", len(fp))

lines = ["# 失败案例分析（D5 · 改进模型 = LGBM 财务+文本, 随机划分42）", ""]
lines.append(f"## 一、漏掉的舞弊公司（假阴性 {len(fn)} 家）")
for _, r in fn.iterrows():
    lines.append(f"- **{r['company']}（{r['code']}_{int(r['year_t'])}）** 模型概率 {r['proba']:.2f}；"
                 f"Z″={r['z_prime2']:.2f}，M={r['m_score']:.2f}；"
                 f"文本分 optimism={r['optimism']:.0f}/risk={r['risk']:.0f}/vague={r['vague']:.0f}，mda_sim={r.get('mda_sim','NA')}")
lines.append("")
lines.append(f"## 二、误伤的对照公司（假阳性 {len(fp)} 家）")
for _, r in fp.iterrows():
    lines.append(f"- **{r['company']}（{r['code']}_{int(r['year_t'])}）** 模型概率 {r['proba']:.2f}；"
                 f"Z″={r['z_prime2']:.2f}，M={r['m_score']:.2f}；"
                 f"文本分 optimism={r['optimism']:.0f}/risk={r['risk']:.0f}/vague={r['vague']:.0f}，mda_sim={r.get('mda_sim','NA')}")
lines.append("")
lines.append("## 三、写作要点（每例3-5句）")
lines.append("- 假阴性：报表与文本分别长什么样？是否'报表撑得住、话没露馅'型？还是造假首年特征未显现？")
lines.append("- 假阳性：对照公司是否因行业下行/重组传闻导致文本悲观或异常？是否'虚惊'型信号？")
lines.append("- 共同点讨论 → 论文'失败案例与局限'节")
open("paper/failures.md", "w", encoding="utf-8").write("\n".join(lines))
print("已写 paper/failures.md")
