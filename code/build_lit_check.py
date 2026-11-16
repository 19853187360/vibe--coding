# -*- coding: utf-8 -*-
"""build_lit_check.py 文献核验表v0
⚠ 红线: AI给出的每条引用必须人工逐条核验真实存在(标题/作者/卷期页码)后才能写入论文。
本表是"待核验清单 + 已发现的疑点记录", 核验人列留空待人工填写。
"""
import xlsxwriter

rows = [
    # (作者, 年份, 标题, 出处, DOI/链接, 关键系数/要点, 核验方式, 状态与疑点)
    ("Altman, E.I.", "1968",
     "Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy",
     "Journal of Finance, 23(4), 589-609",
     "DOI: 10.1111/j.1540-6261.1968.tb00843.x",
     "Z = 1.2X1+1.4X2+3.3X3+0.6X4+1.0X5 (X4=市值/负债, X5=销售/总资产); 判读 Z<1.81 高危 / 1.81-2.99 灰区 / >2.99 安全",
     "Google Scholar/知网下载原文, 核对5个系数与阈值",
     "待人工核验(必核, 交代基线工具出身)"),
    ("Altman, E.I.", "1983",
     "Corporate Financial Distress: A Complete Guide to Predicting, Avoiding, and Dealing with Bankruptcy (专著)",
     "John Wiley & Sons, New York (Z'' 新兴市场版所在章节)",
     "需人工核验具体页码; 二手来源确认系数 6.56/3.26/6.72/1.05",
     "Z'' = 6.56X1+3.26X2+6.72X3+1.05X4; X4=账面权益/总负债(非市值); 判读 Z''<1.1 高危 / 1.1-2.6 灰区 / >2.6 安全。注意存在+3.25常数的Z''变体(Heine & Altman 2011)——论文须注明采用无常数版",
     "下载专著或引用Z''的实证文献交叉核对4个系数",
     "待人工核验(必核, 4个系数逐一对)"),
    ("Beneish, M.D.", "1999",
     "The Detection of Earnings Manipulation",
     "Financial Analysts Journal, 55(5), 24-36",
     "DOI: 10.2469/faj.v55.n5.2296; JSTOR https://www.jstor.org/stable/4480190",
     "M = -4.84 + 0.920DSRI + 0.528GMI + 0.404AQI + 0.892SGI + 0.115DEPI - 0.172SGAI + 4.679TATA - 0.327LVGI; 阈值 M > -2.22 可疑(-1.78为Beneish, Lee & Nichols 2013后修正)",
     "下载原文核对9个数(截距+8系数)与阈值",
     "⚠待核验(必核)。发现两处疑点: ①手册/教程写'刊于The Accounting Review'——实际是Financial Analysts Journal; ②系数与变量名对应关系: 原文0.115→DEPI(折旧指数)、-0.172→SGAI(费用指数)、-0.327→LVGI(杠杆指数), 手册却把0.115挂在LVGI、-0.172挂在DEPI、-0.327挂在LEVI(费用指数)——数是对的但名张冠李戴, 写build_features时按原文对应"),
    ("Li, F.", "2010",
     "The Information Content of Forward-Looking Statements in Corporate Filings—A Naive Bayesian Machine Learning Approach",
     "Journal of Accounting Research, 48(5), 1049-1102",
     "DOI: 10.1111/j.1475-679X.2010.00382.x",
     "MD&A前瞻性语调对盈余有预测信息——文本信号有效性的经典证据(假说H1的理论支点)",
     "下载原文核对结论方向",
     "待人工核验"),
    ("Loughran, T. & McDonald, B.", "2011",
     "When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks",
     "Journal of Finance, 66(1), 35-65",
     "DOI: 10.1111/j.1540-6261.2010.01625.x",
     "金融文本专用词典(LM词典)优于通用词典——支持对MD&A做语义测量的方法论依据",
     "下载原文核对结论方向",
     "待人工核验"),
    ("Lopez-Lira, A. & Tang, Y.", "2023",
     "Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models",
     "SSRN working paper (后被Financial Analysts Journal接收, 60(4), 70-95, 2024)",
     "SSRN 4412788; DOI: 10.2469/faj.2023.0000",
     "LLM对新闻文本打分具有预测力——'LLM打分作为文本测量工具'范式的直接先例(论文定位: 我们把它用到舞弊识别)",
     "下载原文核对方法与结论",
     "待人工核验"),
]

wb = xlsxwriter.Workbook("data/tables/lit_check.xlsx")
ws = wb.add_worksheet("lit_check")
headers = ["作者", "年份", "标题", "期刊·卷·期·页", "DOI或链接", "关键系数/要点",
           "核验方式", "核验状态与疑点", "核验人", "核验日期"]
fmt_bold = wb.add_format({"bold": True})
fmt_red = wb.add_format({"bg_color": "#F4CCCC"})
fmt_yellow = wb.add_format({"bg_color": "#FFF2CC"})
for j, h in enumerate(headers):
    ws.write(0, j, h, fmt_bold)
for i, (au, yr, ti, src, doi, key, how, st) in enumerate(rows, start=1):
    ws.write(i, 0, au); ws.write(i, 1, yr); ws.write(i, 2, ti)
    ws.write(i, 3, src); ws.write(i, 4, doi); ws.write(i, 5, key)
    ws.write(i, 6, how)
    fmt = fmt_red if st.startswith("⚠") else fmt_yellow
    ws.write(i, 7, st, fmt)
    ws.write(i, 8, "")   # 核验人
    ws.write(i, 9, "")   # 核验日期
ws.set_column(0, 0, 22)
ws.set_column(2, 2, 58)
ws.set_column(3, 3, 32)
ws.set_column(4, 4, 42)
ws.set_column(5, 5, 70)
ws.set_column(6, 6, 32)
ws.set_column(7, 7, 80)
ws.freeze_panes(1, 0)
wb.close()
print("已写入 data/tables/lit_check.xlsx:", len(rows), "篇 (全部待人工核验)")
