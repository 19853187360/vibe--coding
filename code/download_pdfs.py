# -*- coding: utf-8 -*-
"""download_pdfs.py  批量下载年报PDF到 pdfs/{code}_{year}.pdf
来源: 巨潮资讯网 cninfo (akshare 定期报告披露接口 + static.cninfo.com.cn 直链)
规律: year财年年报在 year+1 年的1~6月披露 → 查询窗口设为 year+1 全年
断点续传: 已存在的PDF跳过; 失败记 logs/pdf_errors.txt
用法: py -3.14 code\\download_pdfs.py                # 全样本 t 期
      py -3.14 code\\download_pdfs.py --prev        # 追加 A组 t-1 期(前置检验用)
"""
import os, sys, time, re
import requests
import pandas as pd
import akshare as ak

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def find_annual_report(code, year):
    """查 year 财年的年报公告, 返回 (announcementTime, announcementId) 或 None"""
    try:
        df = ak.stock_zh_a_disclosure_report_cninfo(
            symbol=str(code).zfill(6), market="沪深京", category="年报",
            start_date=f"{year+1}0101", end_date=f"{year+1}1231")
    except Exception as e:
        return None
    if df is None or len(df) == 0:
        return None
    for _, r in df.iterrows():
        t = str(r["公告标题"])
        # 要"年度报告"正文: 排除摘要/英文版/更正/取消
        if "摘要" in t or "英文" in t or "更正" in t or "取消" in t:
            continue
        if re.search(rf"{year}\s*年\s*年\s*度\s*报告", t) or t.strip() == f"{year}年年度报告":
            m = re.search(r"announcementId=(\d+)", str(r["公告链接"]))
            if m:
                return str(r["公告时间"]), m.group(1)
    return None

def download(code, year):
    hit = find_annual_report(code, year)
    if not hit:
        return "NOT_FOUND"
    atime, aid = hit
    atime = atime[:10]   # 只取日期部分, 防止"2011-04-14 06:30:00"拼进URL导致404
    url = f"http://static.cninfo.com.cn/finalpage/{atime}/{aid}.PDF"
    out = f"pdfs/{str(code).zfill(6)}_{year}.pdf"
    if os.path.exists(out):
        return "EXISTS"
    try:
        r = requests.get(url, headers=HEADERS, timeout=120)
        if r.status_code == 200 and len(r.content) > 100000 and r.content[:4] == b"%PDF":
            open(out, "wb").write(r.content)
            return f"OK {len(r.content)//1024}KB"
        return f"BAD_HTTP {r.status_code}"
    except Exception as e:
        return f"ERR {repr(e)[:60]}"

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs("pdfs", exist_ok=True)
    sample = pd.read_csv("data/tables/sample_all.csv")
    a_codes = set(pd.read_csv("data/tables/sample_a.csv").code.astype(str).str.zfill(6))
    do_prev = "--prev" in sys.argv
    tasks = []
    for _, r in sample.iterrows():
        code, y = str(r.code).zfill(6), int(r.year_t)
        tasks.append((code, y, r.get("company", "")))
        if do_prev and code in a_codes:
            tasks.append((code, y - 1, r.get("company", "")))
    n_ok = n_fail = n_exist = 0
    errf = open("logs/pdf_errors.txt", "a", encoding="utf-8")
    for i, (code, year, comp) in enumerate(tasks, 1):
        res = download(code, year)
        if res.startswith("OK"): n_ok += 1
        elif res == "EXISTS": n_exist += 1
        else:
            n_fail += 1
            errf.write(f"{code}_{year} {comp} {res}\n"); errf.flush()
        print(f"[{i}/{len(tasks)}] {code}_{year} {comp}: {res}")
        time.sleep(0.8)   # 温和限速
    errf.close()
    print(f"完成: 新下载 {n_ok} / 已存在 {n_exist} / 失败 {n_fail} (见 logs/pdf_errors.txt)")
