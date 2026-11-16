# -*- coding: utf-8 -*-
"""merge_features.py  合成建模主表 dataset.csv"""
import json
import numpy as np
import pandas as pd

feats = pd.read_csv("data/tables/fin_features.csv")
feats["code"] = feats["code"].astype(str).str.replace(".0", "", regex=False).str.zfill(6)
feats["file"] = feats.code + "_" + feats.year_t.astype(int).astype(str)

scores = {}
for line in open("logs/llm_scores.jsonl", encoding="utf-8"):
    d = json.loads(line); scores[d["file"]] = d
sc = pd.DataFrame([{"file": k, "optimism": v["optimism"], "risk": v["risk"],
                    "vague": v["vague"]} for k, v in scores.items()])
sim = pd.read_csv("data/tables/mda_sim.csv")

df = (feats.merge(sc, on="file", how="left").merge(sim, on="file", how="left"))
df["ln_ta"] = np.log(df["total_assets"].clip(lower=1))
dum = pd.get_dummies(df["industry_l1"], prefix="ind", dummy_na=True).astype(int)
df = pd.concat([df, dum], axis=1)
df.to_csv("data/tables/dataset.csv", index=False, encoding="utf-8-sig")
print("合并完成:", df.shape, "| LLM三大缺失率:",
      df[["optimism", "risk", "vague"]].isna().mean().round(3).tolist())
