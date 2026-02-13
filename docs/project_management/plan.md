# 全流程研究流水线计划 (Full Research Pipeline Plan)

## 目标
执行完整的数据流水线（抓取、清洗、识别、建模、稳健性、审计），并更新所有论文及附录文件，确保全文与最新结果和方法论完全一致。

## 里程碑

### Milestone 1: Data Pipeline (数据流水线)
- **Objective**: 从原始数据生成可用于回归的面板数据。
- **Tasks**:
  - [ ] Task 1.1: 数据抓取 (Fetch) - `src/data/fetch.py`
  - [ ] Task 1.2: 数据清洗 (Clean) - `src/data/clean.py`
  - [ ] Task 1.3: 事件识别 (Detect) - `src/identification/detect_events.py`
- **Output**: `data/processed/panel_with_wedge.parquet`
- **Gate**: Gate 3 (Data Quality)

### Milestone 2: Core Analysis (核心实证)
- **Objective**: 运行主模型、基准比较与机制检验。
- **Tasks**:
  - [ ] Task 2.1: 主模型回归 (Main Models) - `src/analysis/models.py`
  - [ ] Task 2.2: Benzarti 基准复现 - `src/analysis/benchmark_benzarti.py`
  - [ ] Task 2.3: 机制检验 (Mechanisms) - `src/analysis/mechanism_testing.py`
- **Output**: `output/tables/`, `output/figures/`
- **Gate**: Gate 4 (Results Closure)

### Milestone 3: Robustness & Audit (稳健性与审计)
- **Objective**: 验证结论的稳健性并进行元数据匹配审计。
- **Tasks**:
  - [ ] Task 3.1: 稳健性测试 - `src/analysis/robustness.py`
  - [ ] Task 3.2: 自动化审计 - `src/audit/metadata_match.py`
- **Output**: `output/tables/robustness_summary.csv`, `docs/audit/AUDIT_REPORT.md`
- **Gate**: Gate 2 (Design) & Gate 6 (Repro)

### Milestone 4: Paper & Appendix Update (论文与附录更新)
- **Objective**: 同步所有文本叙述与图表结果。
- **Tasks**:
  - [ ] Task 4.1: 更新论文正文 - `submission_package/paper.tex`
  - [ ] Task 4.2: 更新附录 - `docs/analysis/robustness_appendix.md`
  - [ ] Task 4.3: 同步说明文字 - `docs/captions.md`
- **Gate**: Gate 5 (Narrative)

## 依赖关系
- `src/data/clean.py` 依赖于 `src/data/fetch.py` 的输出。
- `src/analysis/models.py` 依赖于 `src/identification/detect_events.py` 的输出。
- 论文更新依赖于所有实证脚本的完成。

## 风险清单
- **API 限制**: 频繁抓取可能导致 Eurostat API 锁定。
- **内存压力**: 处理全量面板数据可能导致内存溢出。
- **结果波动**: 新数据可能导致部分稳健性测试不再显著。
