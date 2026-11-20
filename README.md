# 账外之意 — 大模型文本信号对财务舞弊识别的增益研究

山东财经大学首届智能体科研创新挑战赛 · 赛道四 · 选题B · Research Week 2026-11-16 ~ 11-22

**结论摘要**：在87个公司-年度的处罚-配对样本上，财务比率基线（逻辑回归）AUC达0.765；加入MD&A文本特征后为0.772（+0.007），未发现文本信号在财务基线之上提供显著增量。研究贡献集中于方法学：可复现的中文年报LLM测量流程与严格的增量检验（含标签泄露排查）。

## 一键复现

环境: Python 3.12+，依赖 `pip install -r code/requirements.txt`
前置: 大模型打分需自备 OpenAI 兼容服务的 key，设置环境变量 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`（不随包分发）；或用已随包提供的 `logs/llm_scores.jsonl` 跳过打分。

```
py -3.14 code\env_check.py          # ① 环境自检 → 核心检查全部通过
py -3.14 code\build_features.py     # ② 财务特征（data/raw 已随包提供，无需联网）
py -3.14 code\llm_score.py          # ③ 文本打分（约40-60分钟；可跳过，直接用 logs/llm_scores.jsonl）
py -3.14 code\merge_features.py     # ④ 合表 → data/tables/dataset.csv
py -3.14 code\baseline_first.py     # ⑤ 主结果 → results/main_result_v1.csv
```

复现耗时（不含打分）约 2 分钟。核心数字核对：主结果 0.765→0.772（+0.007）、消融 0.673→0.691（+0.018）、年度回测 0.740→0.760（+0.020），见 `results/结果汇总.md` 与 `logs/可复现测试记录.md`。

## 目录结构
```
code/        全部脚本
data/raw/    原始财报 CSV（325 份，随包提供）
data/mdas/   各公司各年度 MD&A 文本（144 份，随包提供）
data/tables/ 样本表 / 特征表 / 引用核验表等
pdfs/        年报 PDF（431MB，不入 git，可自巨潮网重新下载）
logs/        Agent 使用日志、LLM 打分日志、可复现测试记录
paper/       论文（docx/md）与 4 图
results/     实验输出（main_result_v1 / ablation / backtest / robustness / lead_test / 结果汇总）
```

## 变量清单
- 标签：fraud（A组舞弊=1 / B组对照=0）
- 财务特征 22 个：Z″、M-score 及其 8 个分项指数（DSRI/GMI/AQI/SGI/DEPI/SGAI/TATA/LVGI）、11 个数值型红旗、审计意见（qualified_op）
- 文本特征 4 个：optimism / risk / vague（LLM 固定量表三维打分，少样本标定一致率 75%）+ mda_sim（TF-IDF 年度间相似度）
- 控制：行业与规模已通过 1:2 配对设计控制，模型不引入额外控制变量

## 学术边界声明
- 全流程未使用任何股价、市值、交易数据（仅财务报表类接口）
- 结论为"文本无显著增量"的诚实阴性结果，不构成投资建议
- 参考文献逐条人工核验（lit_check.xlsx，核验人已填）；Agent 使用日志全程留痕
