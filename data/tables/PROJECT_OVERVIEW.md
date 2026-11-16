# PROJECT_OVERVIEW — "账外之意"（选题B · 赛道四）

> 本文件是培训流水线 d1-1 的交接产物（接力棒），供 Research Brain / WorkBuddy 读取上下文使用。
> 编制：D1（2026-11-16）· 状态：比赛中（2026-11-16 ~ 11-22 Research Week）

## 1. Project Information
- 赛事：山东财经大学首届智能体科研创新挑战赛（数据文化节系列活动）
- 赛道：赛道四 经济金融与社会科学智能分析
- 选题：选题B "账外之意"——大模型文本信号对财务舞弊识别的增益研究
- 组别：□本科生组 / □研究生组（待填）  团队名称：（待填）

## 2. Research Question
在经典财务比率基线（账面权益版 Z″ / M-score / 逻辑回归）之上，年报 MD&A 的大模型语义信号
（乐观度 optimism / 风险披露 risk / 模糊度 vague / 年度间相似度 mda_sim）能否显著提升
财务舞弊识别的命中率与精确度？

## 3. Problem Boundary（黑名单自查）
- 不使用任何股价、市值、交易数据；不涉及证券估值或投资建议
- 结论表述为"识别增益"（审计辅助含义），非投资建议
- 样本：2019—2023 年处罚公司与配对对照（A组标签挂造假起始年）

## 4. Sample Design
- A组：30—50 家被处罚公司（名单v0见 data/tables/group_a_v0.xlsx，51家候选，逐条待人工核验）
- B组：1:2 配对（同行业门类 + 总资产±30% + 同年度），合计 90—150 公司-年度
- 每家 A 组公司只取一个观测 = 造假起始年（fraud_year_start）

## 5. Variables（19变量 + 控制）
- 标签 y = fraud（A=1 / B=0）
- 财务特征17个：Z″（Altman 1983新兴市场版）、M-score（Beneish 1999 八指数，系数以原文为准）、
  15 红旗（11数值 + 4事件型 qualified_op / auditor_chg / exec_depart / related_pct）
- 文本特征4个：optimism / risk / vague（LLM固定量表0—10打分）+ mda_sim（TF-IDF余弦相似度）
- 控制：行业门类哑变量、ln总资产（上市年限若取不到则论文如实声明"未含"）

## 6. Methods & Validation
- 基线：逻辑回归（仅财务）| 改进：LightGBM（财务+文本），class_weight=balanced
- 指标：AUC / 召回率 / 误报率（不报准确率，样本不平衡）
- 验证四件套：分年度回测（train≤2021 → test≥2022）/ 消融（仅财务 vs 仅文本 vs 全部）/
  前置检验（t-1 信号预测 t 期曝光）/ 失败案例 2—3 例

## 7. Data Sources（白名单）
- 财报数字：AkShare 财务报表类接口（东财；仅财务类接口，不调用任何行情数据）
- MD&A 文本：巨潮资讯网 cninfo.com.cn 年报 PDF → pdfplumber 抽取
- 舞弊标签：证监会 / 交易所处罚公告（官网原文逐条核验）

## 8. Timeline（D1—D7）
D1 备案+名单+文献核验 → D2 样本定稿+财务特征 → D3 MD&A语料+LLM打分+中期checkpoint →
D4 主结果（不可砍）→ D5 验证四件套 → D6 论文6000—9000字+4图5表 → D7 九件套+答辩PPT

## 9. Red Lines（违反即取消资格）
1. 引用逐条人工核验（虚构引用=取消资格）；2. 不伪造/篡改任何财务数字与打分结果；
3. 全流程不碰股价/市值/交易数据；4. 无法解释的内容不写进核心贡献。
Agent 使用日志全程留痕（logs/llm_log.tsv + 每日协作流水）。

## 10. 关键待办
- [ ] 备案表提交（12h时限）+ 截图存 logs/
- [ ] A组名单逐条点开原文核验（fraud_year_start + source_url + 行业门类）
- [ ] lit_check 6篇人工核验（Altman 1983 四系数 / Beneish 1999 九个数必核）
- [ ] events.xlsx 模板（D3 翻 PDF 时填写）
- [ ] LLM_API_KEY 环境变量（D4 前配好）
