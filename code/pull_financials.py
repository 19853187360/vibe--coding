# -*- coding: utf-8 -*-
"""pull_financials.py  逐家拉三表(先普通接口, 空则试退市接口); 限速1.8s; 断点续传
用法: py -3.14 code\\pull_financials.py data\\tables\\sample_a.csv   (第2参数缺省用sample_all.csv)"""
import akshare as ak
import os, sys, time
import pandas as pd

sample_path = sys.argv[1] if len(sys.argv) > 1 else "data/tables/sample_all.csv"
sample = pd.read_csv(sample_path)

SHEETS = [
    ("balance",  ak.stock_balance_sheet_by_report_em,   ak.stock_balance_sheet_by_report_delisted_em),
    ("profit",   ak.stock_profit_sheet_by_report_em,    ak.stock_profit_sheet_by_report_delisted_em),
    ("cashflow", ak.stock_cash_flow_sheet_by_report_em, ak.stock_cash_flow_sheet_by_report_delisted_em),
]
os.makedirs("data/raw", exist_ok=True)
ERR = "logs/pull_errors.txt"

for _, r in sample.iterrows():
    code = str(r.code).zfill(6)
    mk = ("SH" if code[0] in "69" else "SZ") + code
    for name, fn, fn_dl in SHEETS:
        out = f"data/raw/{code}_{name}.csv"
        if os.path.exists(out):            # 断点续传: 已有文件跳过
            continue
        df = None
        try:
            df = fn(symbol=mk); df["DATA_SRC"] = "normal"
        except Exception:
            pass
        if df is None or len(df) == 0:     # 空 → 退市接口(康美类A组必需)
            try:
                df = fn_dl(symbol=mk); df["DATA_SRC"] = "delisted"
            except Exception as e:
                open(ERR, "a", encoding="utf-8").write(f"{code} {name}: {repr(e)[:110]}\n")
        if df is not None and len(df) > 0:
            df.to_csv(out, index=False, encoding="utf-8-sig")
        time.sleep(1.8)                    # 限流保命: 不要去掉
    print("done", r.get("company", ""), code)

n = sum(os.path.exists(f"data/raw/{str(r.code).zfill(6)}_{name}.csv")
        for _, r in sample.iterrows() for name, _, _ in SHEETS)
print(f"已完成 {n} / {len(sample)*3} 个文件")
