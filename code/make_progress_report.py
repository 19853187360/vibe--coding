# -*- coding: utf-8 -*-
"""生成工作进度报告 docx (规范排版: 黑体标题/宋体正文/1.5倍行距/首行缩进)"""
import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn

d = docx.Document()

# 页面设置
sec = d.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.top_margin = sec.bottom_margin = Cm(2.54)
sec.left_margin = sec.right_margin = Cm(3.0)

def set_font(run, name_east, size, bold=False, color=None):
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.bold = bold
    r = run._element.rPr.rFonts
    r.set(qn("w:eastAsia"), name_east)
    if color:
        run.font.color.rgb = RGBColor(*color)

def title(t):
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    set_font(p.add_run(t), "黑体", 16, bold=True)

def subtitle(t):
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(14)
    set_font(p.add_run(t), "楷体", 11)

def h2(t):
    p = d.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    set_font(p.add_run(t), "黑体", 13, bold=True)

def para(t, bold=False, size=12):
    p = d.add_paragraph()
    pf = p.paragraph_format
    pf.first_line_indent = Pt(size * 2)          # 首行缩进2字符
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_after = Pt(2)
    set_font(p.add_run(t), "宋体", size, bold=bold)
    return p

def kv(label, text, size=12):
    p = d.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    set_font(p.add_run(label + "　"), "黑体", size)
    set_font(p.add_run(text), "宋体", size)
    return p

def note(t):
    p = d.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_before = Pt(8)
    set_font(p.add_run(t), "楷体", 10.5)
    return p

# ============ 正文 ============
title("智能体科研创新挑战赛·选题B“账外之意”")
title("工作进度报告")
subtitle("汇报日期：2026年11月17日　|　汇报人：（团队名称）　|　指导教师：（姓名）")

h2("〇、赛事背景与赛制说明（供未接触赛程的老师参考）")
para("本团队参加的“山东财经大学首届智能体科研创新挑战赛”由统计与数学学院主办、可信人工智能实验室承办，主题为“智能体驱动的科研创新”。比赛采用“7天科研创造挑战”形式：11月16日至22日连续7天，参赛队伍须完成“问题定义—文献检索—数据准备—基线实验—方法改进—验证—论文表达”的完整科研循环。")
para("为便于团队内部管理，我们将7天赛程记为D1—D7（即比赛第1天至第7天），每天对应一个阶段目标：D1选题备案与名单核验、D2样本与财务特征、D3年报文本语料、D4核心实验、D5稳健性验证、D6论文成稿、D7成果打包。赛制设有选题备案（开赛12小时内）、过程检查（中期checkpoint）、代码时间戳等过程锁定机制，最终提交Research Package（论文PDF、代码与README、数据说明、引用核验表、Agent使用日志、可复现说明、人机分工声明等）。本报告中的“D1—D3”即指上述阶段，当前为赛程第2天。")

h2("一、项目概况")
kv("题目", "“账外之意”识破财务造假迷雾——大模型文本信号对财务舞弊识别的增益研究（赛道四：经济金融与社会科学智能分析）")
kv("科学问题", "在经典财务比率基线（账面权益版Z″ / M-score / 逻辑回归）之上，年报“管理层讨论与分析”（MD&A）的大模型语义信号（乐观度、风险披露、模糊度、年度间相似度）能否显著提升财务舞弊识别的命中率与精确度？")
kv("问题边界", "会计信息质量研究；不使用任何股价与交易数据；结论表述为“识别增益”（审计辅助含义），不构成投资建议；样本为2019—2023年被处罚公司与配对对照。")

h2("二、研究创新点")
para("1. 增量证据设计（研究设计创新）：不追求“更准的模型”，而是严格测度文本信号在财务基线之上的增量——三重财务基线（Altman Z″、Beneish M-score、逻辑回归）＋相同样本与数据划分下的消融实验＋t-1期前置性检验（用上一期年报文本预测本期被查处），直接回应“文本只是事后回声”的质疑，形成可证伪的证据链。")
para("2. 大模型测量中文文本（方法创新）：传统词典法依赖英文金融情感词典（如Loughran-McDonald词典），对中文年报适应性差、无法捕捉“稳中向好”类套话的模糊性。本研究采用大模型固定量表四维打分（乐观度、风险披露、模糊度、年度间相似度），temperature=0、提示词固定、20条人工复核（一致率≥80%）、换模型重打做稳健性，兼顾语义深度与可复现性。中文年报文本信号研究稀缺，中文＋大模型测量更为少见。")
para("3. 样本与边界新意（对象创新）：样本覆盖2019—2023年新《证券法》时代处罚案例，含泽达易盛、紫晶存储等科创板首批造假退市案（现有文献尚未覆盖）；全流程“去股票化”（不使用任何股价、市值数据），避免市场数据混入带来的前视偏差，结论定位于审计师与监管者“红旗筛查”的辅助工具而非投资策略。")

h2("三、总体进度（执行进度超前于计划）")
para("D1 选题备案：已完成，按12小时时限在官网系统提交；处罚名单与文献核验：已完成，30家被处罚公司逐条经全队人工核验原文确认。")
para("D2 样本定稿与财务特征：已提前完成（87个公司-年度观测，17个财务特征全部计算落盘）。")
para("D3 年报文本语料：基本完成（年报PDF 100%覆盖，MD&A文本抽取收尾中；大模型打分与建模即将启动）。")

h2("四、已完成的具体工作")
para("1. 样本构造：A组29家被处罚公司（证监会/交易所处罚公告，造假起始年2010—2021）+ B组58家配对对照（同行业门类＋同年度＋总资产±30%，三级放宽均记录在案），共87个公司-年度观测。")
para("2. 数据获取：87家公司资产负债表、利润表、现金流量表全部到齐（AkShare财务报表类接口，261份文件零缺失）；年报PDF 87份全部下载（巨潮资讯网），含2份“已取消”但可获取的造假时点原版年报。")
para("3. 特征工程：Z″分数（Altman 1983新兴市场版）、M-score（Beneish 1999八指数）、15个红旗比率全部计算完成，缺失率控制良好（Z″缺失<4%）。")
para("4. 初步信号验证（描述性统计，即论文表2素材）：造假公司Z″均值3.37显著低于对照6.06；M-score（-0.57对-2.27）、应收异常指数DSRI（11.3对1.1）、存贷双高比例（41%对9%）均显示财务特征本身具有区分力——这为“文本信号增量”研究提供了有效且诚实的基线。")
para("5. 文献与公式核验：Altman(1983)四个系数、Beneish(1999)截距与八个系数逐一核对；核验中发现并修正了训练材料中的两处错误（Beneish系数与变量名错位：+0.115应为DEPI、-0.172应为SGAI、-0.327应为LVGI；期刊名应为Financial Analysts Journal而非The Accounting Review）。")
para("6. 过程留痕：git仓库每日提交（代码时间戳证据）；Agent使用日志与人工核验清单全程记录（30家处罚决定书原文逐一核对）。")

h2("五、数据处理中的关键决策（如实记录，论文数据节将注明）")
para("1. 剔除欢瑞世纪：其造假年度（2013—2015）处于借壳前空壳阶段，报表资产不足600万元，无分析意义。")
para("2. 泽达易盛、紫晶存储为上市前造假（IPO阶段），无对应年度公开年报：观测年度调整为“首个含造假的公开年报年度”（2020、2019）。")
para("3. 广州浪奇、胜利精密年报原版被交易所标“已取消”（因造假被追溯调整），PDF仍可获取：采用造假时点原版文本——这正是本研究的对象。")
para("4. 14家对照公司因“对应年度尚未上市”无法提供年报，已替换为同行业、规模接近且年报齐全的公司。")

h2("六、正在进行（未来24—48小时）")
para("1. 年报MD&A文本批量抽取（87份t期＋29份t-1期，收尾中）；2. 大模型固定量表打分（乐观度/风险披露/模糊度，temperature=0，DeepSeek），并做20条人工复核（一致率≥80%方可进入建模）；3. 基线（逻辑回归，仅财务）与改进模型（LightGBM，财务＋文本）主结果；4. 中期checkpoint材料提交（提交渠道待官网/群内确认）。")

h2("七、后续计划")
para("D4—D5：主结果＋验证四件套（分年度回测、消融实验、t-1前置检验、失败案例分析）；D6：论文6000—9000字及4图5表；D7：Research Package打包与一键复现自测。")
para("注：已收到组委会最新通知——本届不设现场答辩、无需PPT，评分以论文质量与提交材料为准。团队将把原答辩准备的精力全部投入论文质量与可复现性。")

h2("八、需要向老师请教的事项")
para("1. 中期checkpoint的提交要求与渠道（官网系统或邮箱），如老师了解请指点；2.（可选）对“观测年度调整”与“配对放宽”两处处理是否有改进建议。")

note("附：本报告所涉全部数据与代码已存入项目仓库（git时间戳可查），Agent使用日志、人工核验清单备查。")

out = "paper/工作进度报告_20261117.docx"
d.save(out)
print("saved", out)
