# 机制检验计划 (Test Plan)

## 检验 1：不对称传导检验 (Asymmetry Test)

*   **假设 (Hypothesis)**: 加税 (Tax Hike) 的传导率显著高于减税 (Tax Cut) 的传导率（绝对值）。
*   **回归模型**:
    $$ P_{it} = \sum_{k \neq -1} \beta_k^{hike} \cdot \mathbb{1}(Hike) \cdot Shock_{i} + \sum_{k \neq -1} \beta_k^{cut} \cdot \mathbb{1}(Cut) \cdot Shock_{i} + \gamma_k + \epsilon_{it} $$
*   **检验统计量**: $H_0: \beta_k^{hike} = \beta_k^{cut}$ (For $k=0, 6, 12$)
*   **预期结果**: 如果存在不对称性，预计 $\beta^{hike} > \beta^{cut}$。
*   **实际结果**: $p > 0.6$，无法拒绝原假设。传导表现为对称。

## 检验 2：行业异质性检验 (Sectoral Heterogeneity)

*   **假设 (Hypothesis)**: 能源和食品（必需品）的传导率高于服务业。
*   **分组方法**: 基于 COICOP 代码。
    -   Energy: `CP045` (Electricity, Gas)
    -   Food: `CP01`
    -   Services: `CP11` (Restaurants & Hotels)
*   **模型**: 分样本回归 (Sub-sample Regression)。
*   **检验**: 比较各组 $\beta_{12}$ 的置信区间。

## 检验 3：显著性/权重渠道检验 (Salience/Weight Channel)

*   **假设 (Hypothesis)**: 在消费篮子中权重较高的商品（High Weight），其价格调整更受关注，传导模式可能不同。
*   **分组方法**: 按事件发生时的权重中位数 (Median Split) 分为 `High Weight` 和 `Low Weight` 组。
*   **模型**: 交互项回归或分样本回归。
    $$ P_{it} = \sum \beta_k^{high} \cdot Shock \cdot \mathbb{1}(High) + \sum \beta_k^{low} \cdot Shock \cdot \mathbb{1}(Low) + \dots $$
*   **检验**: $H_0: \beta_{12}^{high} = \beta_{12}^{low}$
*   **实际结果**: $p \approx 0.17$，差异在统计上不显著，但图形上显示出一定分离趋势。

## 所需变量清单

| 变量名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `norm_log_hicp` | Dependent | 归一化对数价格指数 |
| `shock_size` | Independent | 税楔变化量 (Delta Tax Wedge) |
| `rel_time` | Time | 相对事件发生的时间 (Event Time) |
| `event_type` | Categorical | 'hike' or 'cut' |
| `coicop` | Categorical | 商品类别代码 |
| `weight` | Continuous | 消费权重 |
