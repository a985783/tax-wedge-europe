# 质量闸门 (Quality Gates)

## Gate 1: Research Question (RQ)
- [x] 研究问题明确：增值税传导的不对称性及其竞争机制。
- [x] 贡献点：区分商品与服务，复现 Benzarti (2020) 并提出调和解释。

## Gate 2: Identification Strategy
- [x] 识别策略齐全：双重差分 (DID) + 事件研究法。
- [x] 威胁对策：预趋势检验、安慰剂检验、排除金融危机干扰。

## Gate 3: Data Integrity
- [x] API 抓取可复现：使用固定时间窗口。
- [x] 数据字典匹配：所有 NACE 编码与 HICP 编码一一对应。
- [x] 字段校验：无缺失的时间序列，无异常的价格波动（>100%）。

## Gate 4: Results Closure
- [x] 主表主图闭环：主回归结果支持“传导对称”假设（更新后结果）。
- [x] 证据链完整：异质性结果（核心/外围）支持机制解释。

## Gate 5: Narrative Alignment
- [x] 叙述不跳步：结论与实证证据一一对应。
- [x] 术语一致：文中提到的变量名与代码输出的表头一致。

## Gate 6: Reproducibility
- [x] 一键复现：`replication/run_all.sh` 在干净环境下可运行。
- [x] 引用合规：所有数据来源均有 BibTeX 条目。
