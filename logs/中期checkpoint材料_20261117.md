# 中期 Checkpoint 材料（2026-11-17 · Day 3）

## 一、代码进展
- 项目仓库：D:\账外之意\（git 管理，D1—D3 每日提交共 8 次，代码时间戳可查）
- 已完成脚本（code/ 目录共 17 个）：
  - 数据获取：pull_financials.py（87 家公司三表 261 文件零缺失，含断点续传与退市公司通道）
  - 样本构造：build_group_a_v0.py（52 家候选名单）、build_d2_inputs.py（A组定稿+B组候选池）、pair_b.py（1:2 配对，三级放宽记录在案）
  - 特征工程：build_features.py（Z″/M-score/15 红旗共 17 个财务特征）
  - 年报处理：download_pdfs.py（巨潮批量下载 87 份）、extract_mda.py（MD&A 章节定位抽取）、extract_audit_opinion.py（审计意见自动识别）
  - 实验：fin_baseline.py（仅财务基线）、baseline_first.py / backtest.py（改进模型与验证，待文本特征就绪后运行）
  - 合规：env_check.py、build_lit_check.py（文献核验表）、make_templates.py
- 环境自检 env_check.py 输出"核心检查全部通过"（pandas/akshare/lightgbm 等 12 项）

## 二、Baseline 结果（仅财务特征，文本特征尚未合入）
- 样本：A 组 29 家造假公司 + B 组 58 家配对对照 = 87 个公司-年度
- 特征：Z″ 分数、M-score、15 个红旗比率（缺失率：Z″<4%，M-score 5.7%）
- 结果（随机划分 70/30，stratify，class_weight=balanced）：

| 模型 | AUC | 召回率 | 误报率 |
|---|---|---|---|
| 逻辑回归（仅财务） | 0.765 | 0.556 | 0.167 |
| LightGBM（仅财务） | 0.667 | 0.333 | 0.111 |

- 描述性证据（A 组 vs B 组均值）：Z″ 3.37 vs 6.06；M-score −0.57 vs −2.27；DSRI 11.3 vs 1.1；存贷双高 41% vs 9%
- 说明：年度回测口径将在样本年度分布确认后调整（当前 A 组观测年度 2010—2021，测试期改为 ≥2017）

## 三、Agent 使用日志（摘要）
- 数据 Agent（AkShare 财报接口取数）：D2 完成，261 文件；字段名探针核实（UNASSIGN_RPOFIT 等）
- 文献检索 Agent：Altman(1968/1983)、Beneish(1999) 等 6 篇核验表已建，30 家处罚公司原文链接由人工逐条核验完成
- 年报文本处理：PDF 下载 87 份 + MD&A 抽取（进行中）+ 审计意见识别（进行中）
- LLM 文本打分：D4 启动（DeepSeek 固定量表，temperature=0，含 20 条人工复核）
- 全程留痕：git 提交记录、logs/llm_log.tsv、人工核验清单（全队逐一核对）

## 四、后续计划（D4—D7）
D4：LLM 打分 → 合并 19 变量 → 基线 vs 改进主结果
D5：验证四件套（分年度回测、消融、t-1 前置检验、失败案例）
D6：论文 6000—9000 字 + 4 图 5 表
D7：Research Package 九件套 + 一键复现自测
