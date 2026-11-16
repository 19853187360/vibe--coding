# -*- coding: utf-8 -*-
"""llm_score.py  MD&A四维打分: 乐观/风险/模糊(0-10) + 相似度在sim.py
  断点续传(JSONL), 失败重试1次, temperature=0, 全过程记日志"""
import os, sys, json, time, hashlib
from openai import OpenAI

PROMPT = """你是财务文本分析师，请按量表为以下"管理层讨论与分析"段落打分：
- optimism（0—10）：语言乐观程度，10 为极度乐观自信；
- risk（0—10）：风险因素披露的充分与具体程度，10 为充分具体；
- vague（0—10）：表述模糊程度（多用"稳中向好""总体可控"类套话为高分）。
规则：只依据文本判断；不确定给 5；只输出 JSON，不要解释：
{"optimism": <int>, "risk": <int>, "vague": <int>}
段落：【"""

client = OpenAI(api_key=os.environ["LLM_API_KEY"],
                base_url=os.environ.get("LLM_BASE_URL"))
MODEL = os.environ.get("LLM_MODEL", "deepseek-chat")
PHASH = hashlib.md5(PROMPT.encode()).hexdigest()[:8]

import glob
files = sorted(glob.glob("data/mdas/*_*.txt"))      # 注意: t-1文件也会被抓到, 属正常(前置检验要用)
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
        continue                                   # 断点续传
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
        print("SKIP(记缺失)", fid)
log.close(); out.close()
print("打分完成, 缺失名单见上方SKIP行")
