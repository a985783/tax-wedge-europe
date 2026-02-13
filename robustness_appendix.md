# 稳健性检验附录

本附录汇总了针对主规格的稳健性检验结果，旨在验证核心结论的可靠性。

## 1. 剔除危机年份 (Exclude Crisis Years)
为了排除金融危机（2008-2009）和 COVID-19 疫情（2020-2021）期间宏观经济异常波动对估计结果的干扰，我们剔除了这些年份的样本进行回归。

- **结果文件**：`output/tables/robustness_crisis.tex`
- **核心发现**：
    - **t=0**: 系数为 **0.448** (SE = 0.092)，与主规格 (0.433) 高度接近。
    - **t=12**: 系数为 **0.716** (SE = 0.233)，略高于主规格 (0.658)。
- **结论**：剔除危机年份后，VAT 传导率依然显著且数值稳定。这表明主结果并非由危机期间的极端值或异常经济环境驱动。

## 2. 其他稳健性检验摘要
我们还执行了以下检验（汇总于 `output/tables/robustness_summary.csv` 与 `output/tables/placebo_summary.csv`）：

### 2.1 聚类标准误层级
- **Geo (Baseline)**: SE(t=0) = 0.091
- **Geo-Year**: SE(t=0) 略有变化，但显著性水平维持不变。
- **Geo-Coicop**: 标准误总体更小，显著性更强。

### 2.2 替代时间窗口
- **Window +/- 24 Months**:
    - 扩展窗口后，短期系数保持稳定。
    - 长期（t=24）系数进一步确认了价格调整的持续性。

### 2.3 Placebo 检验
- **结果文件**：`output/tables/placebo_summary.csv`\n- **图形**：`output/figures/placebo_distribution.png`\n- **解释**：Placebo 的 p-value 分布应接近均匀，说明识别不由虚假事件驱动。

## 索引
- 表格：`output/tables/robustness_crisis.tex` (危机剔除检验)
- 表格：`output/tables/robustness_clustering.tex` (聚类稳健性)
- 数据：`output/tables/robustness_summary.csv` (所有检验汇总)
