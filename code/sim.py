# -*- coding: utf-8 -*-
"""sim.py  每家公司的t期与t-1期MD&A余弦相似度(字符级TF-IDF, 免分词)"""
import glob, os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def read(cy):
    f = f"data/mdas/{cy}.txt"
    return open(f, encoding="utf-8").read() if os.path.exists(f) else None

rows = []
for f in sorted(glob.glob("data/mdas/*_*.txt")):
    fid = os.path.basename(f)[:-4]              # 600518_2016
    code, yr = fid.split("_")
    prev = read(f"{code}_{int(yr)-1}")
    cur = open(f, encoding="utf-8").read()
    if prev:
        X = TfidfVectorizer(analyzer="char", ngram_range=(2, 3)).fit_transform([prev, cur])
        rows.append(dict(file=fid, mda_sim=float(cosine_similarity(X)[0, 1])))
pd.DataFrame(rows).to_csv("data/tables/mda_sim.csv", index=False, encoding="utf-8-sig")
print("有相似度观测:", len(rows), "(A组t-1齐全时约等于A组数量)")
