# Wild Cluster Bootstrap 输出示例

## 1. 控制台输出示例

```
================================================================================
Running Wild Cluster Bootstrap Inference
================================================================================

Wild Cluster Bootstrap: G=30 clusters, B=9999 replications
Distribution: rademacher

Bootstrap for t=-12
Wild Cluster Bootstrap: G=30 clusters, B=9999 replications
Distribution: rademacher
  Bootstrap iteration 1000/9999
  Bootstrap iteration 2000/9999
  Bootstrap iteration 3000/9999
  ...

Bootstrap for t=-11
...

Bootstrap Results (Key Periods):
--------------------------------------------------------------------------------
Time   Coef       SE         p-value      CI Lower   CI Upper
--------------------------------------------------------------------------------
-12    0.0234     0.0456     0.6123      -0.0891     0.1359
-6     0.0156     0.0321     0.6345      -0.0478     0.0790
-1     0.0000     0.0000     1.0000       0.0000     0.0000
0      0.8234***  0.0678     0.0000       0.6905     0.9563
6      0.9123***  0.0712     0.0000       0.7728     1.0518
12     0.9456***  0.0745     0.0000       0.7996     1.0916
```

## 2. CSV输出示例 (main_results_bootstrap.csv)

| rel_time | coef   | se     | t_stat  | pval_bootstrap | ci_lower | ci_upper |
|----------|--------|--------|---------|----------------|----------|----------|
| -12      | 0.0234 | 0.0456 | 0.5132  | 0.6123         | -0.0891  | 0.1359   |
| -11      | 0.0189 | 0.0423 | 0.4468  | 0.6589         | -0.0845  | 0.1223   |
| -10      | 0.0312 | 0.0389 | 0.8021  | 0.4289         | -0.0456  | 0.1080   |
| ...      | ...    | ...    | ...     | ...            | ...      | ...      |
| -1       | 0.0000 | 0.0000 | 0.0000  | 1.0000         | 0.0000   | 0.0000   |
| 0        | 0.8234 | 0.0678 | 12.1456 | 0.0000         | 0.6905   | 0.9563   |
| 1        | 0.8567 | 0.0691 | 12.3987 | 0.0000         | 0.7212   | 0.9922   |
| ...      | ...    | ...    | ...     | ...            | ...      | ...      |
| 12       | 0.9456 | 0.0745 | 12.6934 | 0.0000         | 0.7996   | 1.0916   |

## 3. LaTeX表格输出示例 (main_results_bootstrap.tex)

```latex
\begin{table}[htbp]
\centering
\caption{Main Results: Wild Cluster Bootstrap Inference}
\label{tab:main_bootstrap}
\begin{tabular}{cccccc}
\toprule
Event Time & Coefficient & Std. Error & Bootstrap p-value & CI Lower & CI Upper \\
\midrule
-12 & 0.0234 & 0.0456 & 0.6123 & -0.0891 & 0.1359 \\
-11 & 0.0189 & 0.0423 & 0.6589 & -0.0845 & 0.1223 \\
-10 & 0.0312 & 0.0389 & 0.4289 & -0.0456 & 0.1080 \\
... & ... & ... & ... & ... & ... \\
-1 & 0.0000 & 0.0000 & 1.0000 & 0.0000 & 0.0000 \\
0 & 0.8234*** & 0.0678 & 0.0000 & 0.6905 & 0.9563 \\
1 & 0.8567*** & 0.0691 & 0.0000 & 0.7212 & 0.9922 \\
... & ... & ... & ... & ... & ... \\
12 & 0.9456*** & 0.0745 & 0.0000 & 0.7996 & 1.0916 \\
\bottomrule
\multicolumn{6}{p{0.95\textwidth}}{\footnotesize \textit{Notes:}
Wild Cluster Bootstrap inference with 9,999 replications.
Standard errors are clustered at the country level.
Bootstrap p-values and confidence intervals are based on the percentile-t method.
*** $p<0.01$, ** $p<0.05$, * $p<0.1$.}
\end{tabular}
\end{table}
```

## 4. 比较表格：标准聚类 vs Bootstrap

```latex
\begin{table}[htbp]
\centering
\caption{Comparison: Standard vs Wild Cluster Bootstrap Inference}
\label{tab:comparison}
\begin{tabular}{ccccccc}
\toprule
& \multicolumn{3}{c}{Standard Clustered SE} & \multicolumn{3}{c}{Wild Cluster Bootstrap} \\
\cmidrule(lr){2-4} \cmidrule(lr){5-7}
Time & Coef & SE & p-value & SE & p-value & 95\% CI \\
\midrule
0 & 0.8234 & 0.0678 & 0.0000 & 0.0678 & 0.0000 & [0.6905, 0.9563] \\
6 & 0.9123 & 0.0712 & 0.0000 & 0.0712 & 0.0000 & [0.7728, 1.0518] \\
12 & 0.9456 & 0.0745 & 0.0000 & 0.0745 & 0.0000 & [0.7996, 1.0916] \\
\bottomrule
\multicolumn{7}{p{0.95\textwidth}}{\footnotesize \textit{Notes:}
Standard errors are clustered at the country level (G=30).
Wild Cluster Bootstrap uses 9,999 replications with Rademacher weights.}
\end{tabular}
\end{table}
```

## 5. 不同分布的比较

| Distribution | Description | Best For | t=0 Coefficient | p-value | 95% CI |
|--------------|-------------|----------|-----------------|---------|--------|
| Rademacher | {-1, 1} equal probability | G >= 10 | 0.8234 | 0.0000 | [0.6905, 0.9563] |
| Mammen | Two-point asymmetric | G < 10 | 0.8234 | 0.0000 | [0.6889, 0.9579] |
| Webb 6-point | Six-point symmetric | G < 10 | 0.8234 | 0.0000 | [0.6912, 0.9556] |

## 6. 使用说明

### 6.1 基本使用

```python
from src.analysis.models import (
    BootstrapConfig,
    run_wild_bootstrap_inference
)

# Configure bootstrap
config = BootstrapConfig(
    n_bootstrap=9999,
    distribution="rademacher",
    confidence_level=0.95,
    seed=42
)

# Run bootstrap
results = run_wild_bootstrap_inference(
    df=stacked_df,
    y_col="norm_log_hicp",
    treat_var="treat_shock",
    half_window=12,
    base_period=-1,
    absorb_cols=["geo_coicop", "cal_time", "rel_time"],
    cluster_col="geo",
    weights_col="event_weight",
    config=config
)
```

### 6.2 从YAML配置加载

```python
from src.analysis.models import load_bootstrap_config_from_yaml

# Load from analysis_config.yaml
config = load_bootstrap_config_from_yaml()

if config:
    results = run_wild_bootstrap_inference(..., config=config)
```

### 6.3 推荐配置

根据聚类数G选择分布：

| 聚类数 G | 推荐分布 | 说明 |
|---------|---------|------|
| G < 10 | webb_6pt | Webb六点分布，小样本最优 |
| 10 <= G < 30 | mammen | Mammen两点分布 |
| G >= 30 | rademacher | Rademacher分布（默认） |

您的数据：G = 30个国家
推荐：rademacher（默认）或 mammen

## 7. 参考文献

Cameron, A.C., Gelbach, J.B., & Miller, D.L. (2008). "Bootstrap-Based Improvements for Inference with Clustered Errors." *Review of Economics and Statistics*, 90(3), 414-427.

Webb, M.D. (2013). "Reworking Wild Bootstrap Based Inference for Clustered Errors." Working Paper.

Mammen, E. (1993). "Bootstrap and Wild Bootstrap for High Dimensional Linear Models." *Annals of Statistics*, 21(1), 255-285.
