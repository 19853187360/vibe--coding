# -*- coding: utf-8 -*-
"""env_check.py 环境自检：包 + 接口 + key 提示，每天开工前重跑"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
items = []

for m in ["pandas", "numpy", "sklearn", "lightgbm", "statsmodels", "akshare", "pdfplumber", "openai"]:
    try:
        mod = __import__(m)
        items.append((m, getattr(mod, "__version__", "ok")))
    except Exception as e:
        items.append((m, "FAIL " + repr(e)[:60]))

import akshare as ak
for name, sym in [("资产负债表", "SH600519"), ("利润表", "SH600519"), ("现金流量表", "SH600519")]:
    fn = {"资产负债表": ak.stock_balance_sheet_by_report_em,
          "利润表": ak.stock_profit_sheet_by_report_em,
          "现金流量表": ak.stock_cash_flow_sheet_by_report_em}[name]
    try:
        df = fn(symbol=sym)
        items.append((name + "接口", "OK rows=%d" % len(df)))
    except Exception as e:
        items.append((name + "接口", "FAIL " + repr(e)[:80]))

try:  # 退市通道(A组关键), 用康美药业试
    df = ak.stock_balance_sheet_by_report_delisted_em(symbol="SH600518")
    items.append(("退市公司接口", "OK rows=%d" % len(df)))
except Exception as e:
    items.append(("退市公司接口", "FAIL " + repr(e)[:80]))

items.append(("LLM_API_KEY", "已设置" if os.environ.get("LLM_API_KEY") else "未设置(见D4步骤1)"))

def good(v):
    return not v.startswith("FAIL")
print("=" * 46)
for k, v in items:
    print((" PASS " if good(v) else " WARN ") + f"{k:12s} {v}")
print("=" * 46)
core = [v for k, v in items if k.endswith("接口") or k in ("akshare", "pandas", "pdfplumber")]
print("核心检查全部通过" if all(good(v) for v in core) else "存在FAIL: 先处理再开工")
