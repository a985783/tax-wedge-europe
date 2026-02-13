# 主回归结果解读

## 1. 核心发现 (Baseline Results)

基于修正后的规格（单位：百分点，排他窗口：+/- 6个月），我们在 1895 个清洁税收冲击事件中发现了显著的税收传递效应。

### 传递率 (Pass-through Rate)
- **冲击当期 (t=0)**: 传递系数为 **0.4329** (p < 0.001)。这意味着 1 个百分点的增值税变动会导致价格在当月变动约 0.43%。
- **一年后 (t=12)**: 传递系数上升至 **0.6584** (p < 0.001)。这意味着长期来看，约 66% 的税收变动被传递给了消费者。
- **统计显著性**: 无论是在冲击当期还是长期，结果都在 1% 水平上显著，表明增值税传递是一个稳健的经济现象。

参见图表：
- **图**: `output/figures/main_event_study.png` (展示了动态传递路径)
- **表**: `output/tables/main_regression_results.tex` (详细回归系数)

## 2. 异质性与不对称性 (Heterogeneity & Asymmetry)

### 上调 vs 下调 (Asymmetry)
- 我们检验了税收上调 (Hikes) 与下调 (Cuts) 是否具有不同的传递效应。
- **结论**: 未发现显著的不对称性。
    - t=0 差异检验 p-value: 0.8343
    - t=12 差异检验 p-value: 0.8196
- 这表明价格对税收变动的反应是对称的，无论是增税还是减税，传递率在统计上无显著差异。

参见：`output/tables/asymmetry_results.tex`

### 部门异质性 (Sectoral Heterogeneity)
- **食品 (Food)**: 样本量 3700，显示出显著的传递效应。
- **能源 (Energy)**: 样本量 2559，通常具有较高的传递率。
- **服务 (Services)**: 样本量 1597，传递相对较慢或较低。

参见：`output/figures/heterogeneity_sector.png`
