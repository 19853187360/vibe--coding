# -*- coding: utf-8 -*-
"""make_templates.py 一次性生成 events.xlsx(4事件红旗) / human_check.xlsx(人工复核打分) 模板"""
import xlsxwriter

# events.xlsx: 4个事件型红旗, D3翻年报PDF时手工填
wb = xlsxwriter.Workbook("data/tables/events.xlsx")
ws = wb.add_worksheet("events")
fmt_bold = wb.add_format({"bold": True})
for j, h in enumerate(["code", "year_t", "qualified_op", "auditor_chg", "exec_depart", "related_pct"]):
    ws.write(0, j, h, fmt_bold)
ws.write(1, 0, "600518"); ws.write(1, 1, 2016)   # 示例行, 照此填
ws.write(1, 2, ""); ws.write(1, 3, ""); ws.write(1, 4, ""); ws.write(1, 5, "")
ws2 = wb.add_worksheet("说明")
for i, (k, v) in enumerate([
    ("qualified_op", "1=非标审计意见(保留/无法表示/带强调事项), 0=标准无保留; 来源: 年报审计报告首页"),
    ("auditor_chg", "1=t年更换会计师事务所, 0=否; 来源: 年报'聘请事务所'节/公告"),
    ("exec_depart", "1=t年董事长/总经理/CFO有异常离职, 0=否; 来源: 年报董监高变动表"),
    ("related_pct", "关联交易金额÷总资产(连续值; 查不到填0并记缺失); 来源: 年报'重大关联交易'节"),
    ("code/year_t", "与 sample_all.csv 对齐; 每家公司每个观测年一行"),
]):
    ws2.write(i, 0, k, fmt_bold); ws2.write(i, 1, v)
ws2.set_column(1, 1, 90)
wb.close()

# human_check.xlsx: D4人工复核20条(随机抽, 不看机器分按量表打分)
wb3 = xlsxwriter.Workbook("data/tables/human_check.xlsx")
ws3 = wb3.add_worksheet("human_check")
for j, h in enumerate(["file", "optimism", "risk", "vague"]):
    ws3.write(0, j, h, fmt_bold)
ws3.write(1, 0, "600518_2016")   # 示例行, 照此填
ws3.set_column(0, 0, 16)
wb3.close()
print("已生成 data/tables/events.xlsx 与 data/tables/human_check.xlsx")
