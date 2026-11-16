# 账外之意 — 大模型文本信号对财务舞弊识别的增益研究

山东财经大学首届智能体科研创新挑战赛 · 赛道四 · 选题B · Research Week 2026-11-16 ~ 11-22

## 一键复现（README 三步跑通）
环境: Python 3.12+  依赖: `pip install -r code/requirements.txt`
前置: 设置环境变量 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL` (自备, 不随包分发)

```
py -3.14 code\env_check.py                 # ① 仪表盘全绿
py -3.14 code\build_features.py            # ② 财务特征(数据已随包提供data/raw可跳过pull)
py -3.14 code\llm_score.py                 # ③ 文本打分(约X分钟, 已含断点续传)
py -3.14 code\merge_features.py            # ④ 合表
py -3.14 code\baseline_first.py            # ⑤ 主结果 → results/main_result_v1.csv
```
复现耗时约 X 分钟; 输出与论文表3数字一致性: ___

## 目录结构
```
code/   全部脚本(见命名规范)
data/raw/      AkShare 原始财报 CSV(脚本自动存, 不手改)
data/mdas/     各公司各年度 MD&A 文本(600518_2018.txt)
data/tables/   样本表/特征表/文献核验表等中间成品
pdfs/   年报 PDF(不入git)
logs/   备案截图、LLM调用日志、Agent使用日志
paper/  论文 docx 与图
results/ 实验输出(main_result_v1.csv、ablation.csv…)
```

## 变量清单（19变量）
fraud(标签) · z_prime2 · m_score · dsri/gmi/aqi/sgi/depi/sgai/tata/lvgi(M八指数)
· 11数值红旗 · 4事件红旗(events.xlsx) · optimism/risk/vague(LLM固定量表)
· mda_sim(TF-IDF余弦) · 行业哑变量/ln_ta

## 学术边界声明
- 全流程未使用任何股价、市值、交易数据（仅财务报表类接口）
- 结论为"识别增益"（审计辅助含义），不构成投资建议
- 参考文献逐条人工核验（lit_check.xlsx）；Agent 使用日志全程留痕

## 赛事最新指示（2026-11-16 晚）
- 不答辩、不做 PPT，评分只看论文质量 + 全部数据材料
- 因此 PPT 从交付清单移除；论文质量与 Research Package 完整性为最高优先级
