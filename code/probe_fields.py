# -*- coding: utf-8 -*-
"""probe_fields.py  导出三表全部列名到 data/raw/field_names.txt"""
import akshare as ak, sys
sys.stdout.reconfigure(encoding="utf-8")
lines = []
for tag, fn in [("balance", ak.stock_balance_sheet_by_report_em),
                ("profit", ak.stock_profit_sheet_by_report_em),
                ("cashflow", ak.stock_cash_flow_sheet_by_report_em)]:
    cols = list(fn(symbol="SH600519").columns)
    lines.append(f"[{tag}] {len(cols)} cols:")
    lines += ["  " + c for c in cols]
open("data/raw/field_names.txt", "w", encoding="utf-8").write("\n".join(lines))
print("已写入 field_names.txt, 找不到的列在其中搜同义词")
