# -*- coding: utf-8 -*-
"""llm_score_fewshot.py  少样本标定版打分: 把6条人工标注样例嵌入提示词, 让模型对齐人的刻度
用法: LLM_API_KEY=... LLM_BASE_URL=... py -3.14 code\\llm_score_fewshot.py
输出 logs/llm_scores.jsonl (覆盖式, 断点续传)"""
import os, sys, json, time, hashlib, re, glob
from openai import OpenAI

# 6条标定样例(文本摘录 + 人工打分) —— 来自 v2 人工打分表
FEWSHOT = [
    ("002164_2017", "宁波东力", 9, 2, 2),
    ("600298_2018", "安琪酵母", 5, 8, 3),
    ("600518_2015", "康美药业", 9, 2, 7),
    ("600818_2018", "中路股份", 4, 2, 6),
    ("300285_2016", "国瓷材料", 8, 2, 3),
    ("603588_2017", "高能环境", 7, 5, 3),
]

def snippet(fid, n=350):
    t = open(f"data/mdas/{fid}.txt", encoding="utf-8").read()
    return re.sub(r"\s+", "", t)[:n]

def build_prompt():
    p = "你是财务文本分析师，请按量表为以下\"管理层讨论与分析\"段落打分（0—10整数）。\n"
    p += "三个维度：optimism（乐观度，10=极度乐观自信）；risk（风险披露充分度，10=充分且具体）；vague（模糊度，10=通篇套话无实质）。\n"
    p += "重要：请用满0—10的刻度，不要都挤在中间。下面给你6条已由人工仔细标注的样例，学习其打分刻度：\n"
    for fid, name, o, r, v in FEWSHOT:
        p += f"样例（{name}）：\"{snippet(fid)}\"\n人工打分：{{\"optimism\": {o}, \"risk\": {r}, \"vague\": {v}}}\n"
    p += "\n规则：只依据文本判断；拿不准给5；只输出JSON，不要解释。\n"
    p += "段落：【"
    return p

PROMPT = build_prompt()
PHASH = hashlib.md5(PROMPT.encode()).hexdigest()[:8]

client = OpenAI(api_key=os.environ["LLM_API_KEY"], base_url=os.environ.get("LLM_BASE_URL"))
MODEL = os.environ.get("LLM_MODEL", "deepseek-chat")

files = sorted(glob.glob("data/mdas/*_*.txt"))
done = set()
if os.path.exists("logs/llm_scores.jsonl"):
    for line in open("logs/llm_scores.jsonl", encoding="utf-8"):
        try:
            done.add(json.loads(line)["file"])
        except Exception:
            pass
log = open("logs/llm_log.tsv", "a", encoding="utf-8")
out = open("logs/llm_scores.jsonl", "a", encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")

for fp in files:
    fid = os.path.basename(fp).replace(".txt", "")
    if fid in done:
        continue
    text = open(fp, encoding="utf-8").read()[:8000]
    scores, n_try = None, 0
    while scores is None and n_try < 2:
        n_try += 1
        try:
            r = client.chat.completions.create(
                model=MODEL, temperature=0,
                messages=[{"role": "user", "content": PROMPT + text + "】"}])
            c = r.choices[0].message.content.strip()
            scores = json.loads(c[c.index("{"): c.rindex("}") + 1])
            assert all(0 <= int(scores[k]) <= 10 for k in ("optimism", "risk", "vague"))
            tk = getattr(getattr(r, "usage", None), "completion_tokens", "?")
            log.write(f"{time.strftime('%F %T')}\t{MODEL}\t{PHASH}\t{fid}\t{tk}\n"); log.flush()
        except Exception as e:
            print("retry", fid, repr(e)[:80]); time.sleep(3 * n_try)
    if scores:
        out.write(json.dumps({"file": fid, **scores}, ensure_ascii=False) + "\n"); out.flush()
        print("ok", fid, scores)
    else:
        print("SKIP", fid)
log.close(); out.close()
print("少样本标定打分完成")
