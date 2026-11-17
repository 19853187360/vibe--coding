# -*- coding: utf-8 -*-
"""extract_audit_opinion.py  从年报PDF自动识别审计意见类型 → 填 events.xlsx 的 qualified_op
qualified_op: 1=非标(保留/无法表示/否定/带强调事项段), 0=标准无保留
识别方式: 在"审计报告"节附近搜索关键词; 无审计报告节则全文本搜索。
人工抽查: 抽10%对照审计报告原文(红线要求)。
"""
import os, re, sys
import glob
import pandas as pd
import pdfplumber

BAD_KWS = ["保留意见", "无法表示意见", "否定意见", "带强调事项", "带持续经营", "无法获取充分"]
# 注: "重大不确定性"已移除——标准审计报告含"是否存在重大不确定性…不存在重大不确定性"套话, 易误报;
# 真正的持续经营问题在非标报告中以"带强调事项段(持续经营)"表述, 由"带强调事项"捕获
GOOD_KWS = ["标准无保留意见", "无保留意见"]

def classify(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    full = "".join(pages)
    # 优先看审计报告节(通常带"审计报告"标题的那几页, 至"财务报表"标题为止)
    ar_text = ""
    for i, t in enumerate(pages):
        if "审计报告" in t[:300]:
            ar_text += t
            for j in range(i + 1, min(i + 8, len(pages))):
                ar_text += pages[j]
                if "财务报表" in pages[j][:200]:
                    break
            break
    scope = ar_text if len(ar_text) > 200 else full
    hits = [kw for kw in BAD_KWS if kw in scope]
    if "无保留意见" in scope and "保留意见" in hits:
        hits.remove("保留意见")     # "无保留意见"中的子串误命中
    if hits:
        return 1, "+".join(hits)
    # 无非标关键词: 标准审计报告通常不含"无保留"字样, 记佐证或默认
    if "标准无保留意见" in full or "无保留意见" in full:
        return 0, "标准无保留"
    return 0, "无非标关键词(默认标准)"

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    files = sorted(glob.glob("pdfs/*_*.pdf"))
    rows, miss = [], []
    for f in files:
        fid = os.path.basename(f)[:-4]           # 600518_2016
        code, year = fid.split("_")
        try:
            op, kw = classify(f)
        except Exception as e:
            op, kw = None, f"ERR {repr(e)[:40]}"
        rows.append(dict(code=code, year_t=int(year), qualified_op=op, note=kw))
        if op is None:
            miss.append(fid)
    df = pd.DataFrame(rows)
    df.to_csv("data/tables/audit_opinions.csv", index=False, encoding="utf-8-sig")
    print(df.groupby("qualified_op").size().to_dict())
    print("未识别:", miss if miss else "无")
