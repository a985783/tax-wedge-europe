# 交接文档 (Handoff)

## 流程编排

| 阶段 | 执行者 (Agent) | 输入 | 输出 | 交付物验证 |
| :--- | :--- | :--- | :--- | :--- |
| 数据准备 | data-pipeline-engineer | Eurostat API | `panel_with_wedge.parquet` | Gate 3 |
| 事件识别 | identification-architect | `panel_with_wedge.parquet` | `events_list.parquet` | Gate 2 |
| 实证分析 | empirical-analyst | `panel_with_wedge.parquet` | `output/tables/*.tex` | Gate 4 |
| 机制构建 | mechanism-builder | 实证结果 | `heterogeneity_mechanism.tex` | Gate 4 |
| 质量审计 | repro-auditor | 代码 + 结果 | `AUDIT_REPORT.md` | Gate 6 |
| 论文写作 | academic-writer | 所有图表 + 审计报告 | `paper.tex` | Gate 5 |

## 交接说明
- 每个 Agent 在完成任务后，必须更新 `plan.yaml` 中的 `status` 为 `completed`。
- 如果 Gate 验证失败，必须将任务退回上一个阶段。
