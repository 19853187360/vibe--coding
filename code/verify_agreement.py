# -*- coding: utf-8 -*-
"""verify_agreement.py  人工vs机器一致率: |差|<=1 记一致, 目标>=80%"""
import json
import pandas as pd
h = pd.read_excel("data/tables/human_check.xlsx")
m = {}
for line in open("logs/llm_scores.jsonl", encoding="utf-8"):
    d = json.loads(line); m[d["file"]] = d
rows = []
for _, r in h.iterrows():
    mm = m.get(r.file, {})
    for k in ("optimism", "risk", "vague"):
        if k in mm:
            rows.append(abs(r[k] - mm[k]) <= 1)
print(f"一致条目 {sum(rows)} / {len(rows)} = {100*sum(rows)/len(rows):.0f}%  (目标 >= 80%)")
