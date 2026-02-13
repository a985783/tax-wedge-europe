# Wild Cluster Bootstrap Implementation

## 概述

本文档描述了为解决小聚类数问题（G < 50）而实施的Wild Cluster Bootstrap方法。基于Cameron, Gelbach & Miller (2008)的经典论文，该方法通过Bootstrap重采样来修正聚类标准误的size distortion问题。

## 问题背景

您的论文使用30个国家的数据（G = 30 < 50），标准的聚类稳健标准误可能存在以下问题：
- **Size distortion**：检验的实际size可能偏离名义size
- **置信区间覆盖不足**：真实参数可能不在置信区间内
- **过度拒绝原假设**：第一类错误率可能高于设定水平

## 解决方案

Wild Cluster Bootstrap通过以下方式解决上述问题：
1. 在聚类层面进行重采样
2. 使用wild weights扰动残差
3. 构建bootstrap分布进行推断

## 实现功能

### 1. 支持的分布类型

- **Rademacher分布**（默认）：`{-1, 1}`等概率
  - 适用于 G >= 10
  - 计算简单，最常用

- **Mammen分布**：两点不对称分布
  - 适用于 G < 10
  - 高阶性质更好

- **Webb六点分布**：六点对称分布
  - 适用于 G < 10
  - 小样本表现最优

### 2. 主要类和方法

#### BootstrapConfig
配置Bootstrap参数的数据类：
```python
from src.analysis.models import BootstrapConfig

config = BootstrapConfig(
    n_bootstrap=9999,        # Bootstrap重采样次数
    distribution="rademacher",  # 权重分布类型
    confidence_level=0.95,   # 置信水平
    seed=42,                 # 随机种子
    small_cluster_correction=True  # 小样本校正
)
```

#### WildClusterBootstrap
核心Bootstrap类：
```python
from src.analysis.models import WildClusterBootstrap

bootstrap = WildClusterBootstrap(config)
bootstrap.fit(y, X, cluster_col, absorb, weights, param_idx)
results = bootstrap.summary()
```

#### 便捷函数
```python
from src.analysis.models import (
    run_wild_bootstrap_inference,
    load_bootstrap_config_from_yaml,
    run_main_analysis_with_bootstrap
)

# 方法1: 直接运行
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

# 方法2: 从YAML配置加载
config = load_bootstrap_config_from_yaml()

# 方法3: 完整分析流程
results = run_main_analysis_with_bootstrap(
    df=df,
    events=events,
    use_bootstrap=True
)
```

## 配置文件

在 `analysis_config.yaml` 中已添加Bootstrap配置：

```yaml
analysis:
  bootstrap:
    enabled: true              # 启用Bootstrap
    n_bootstrap: 9999          # 重采样次数
    distribution: rademacher   # 分布类型
    confidence_level: 0.95     # 置信水平
    seed: 42                   # 随机种子
    small_cluster_correction: true  # 小样本校正
```

## 使用示例

### 基本使用

```python
from src.analysis.models import (
    load_and_prep_data,
    build_stacked_with_controls,
    BootstrapConfig,
    run_wild_bootstrap_inference
)

# 加载数据
df, events = load_and_prep_data()
stacked_df = build_stacked_with_controls(df, events, half_window=12)

# 配置Bootstrap
config = BootstrapConfig(
    n_bootstrap=9999,
    distribution="rademacher",
    confidence_level=0.95,
    seed=42
)

# 运行Bootstrap推断
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

# 查看结果
print(results[['rel_time', 'coef', 'se', 'pval_bootstrap', 'ci_lower', 'ci_upper']])
```

### 完整分析流程

```python
from src.analysis.models import run_main_analysis_with_bootstrap

# 运行包含Bootstrap的完整分析
results = run_main_analysis_with_bootstrap(
    df=df,
    events=events,
    use_bootstrap=True
)

# 结果包含标准推断和Bootstrap推断
standard_results = results['standard']
bootstrap_results = results['bootstrap']
```

## 输出结果

### 控制台输出
```
Wild Cluster Bootstrap: G=30 clusters, B=9999 replications
Distribution: rademacher

Bootstrap for t=0
  Bootstrap iteration 1000/9999
  Bootstrap iteration 2000/9999
  ...

Time   Coef       SE         p-value      CI Lower   CI Upper
----------------------------------------------------------------
-12    0.0234     0.0456     0.6123      -0.0891     0.1359
0      0.8234***  0.0678     0.0000       0.6905     0.9563
12     0.9456***  0.0745     0.0000       0.7996     1.0916
```

### CSV输出
结果保存至：`output/tables/main_results_bootstrap.csv`

| rel_time | coef | se | t_stat | pval_bootstrap | ci_lower | ci_upper |
|----------|------|-----|--------|----------------|----------|----------|
| 0 | 0.8234 | 0.0678 | 12.1456 | 0.0000 | 0.6905 | 0.9563 |
| 12 | 0.9456 | 0.0745 | 12.6934 | 0.0000 | 0.7996 | 1.0916 |

### LaTeX表格
结果保存至：`output/tables/main_results_bootstrap.tex`

## 推荐配置

根据聚类数G选择分布：

| 聚类数 G | 推荐分布 | 说明 |
|---------|---------|------|
| G < 10 | webb_6pt | Webb六点分布，小样本最优 |
| 10 <= G < 30 | mammen | Mammen两点分布 |
| G >= 30 | rademacher | Rademacher分布（默认） |

您的数据：G = 30个国家
推荐：**rademacher**（默认）或 **mammen**

## 参考文献

1. Cameron, A.C., Gelbach, J.B., & Miller, D.L. (2008). "Bootstrap-Based Improvements for Inference with Clustered Errors." *Review of Economics and Statistics*, 90(3), 414-427.

2. Webb, M.D. (2013). "Reworking Wild Bootstrap Based Inference for Clustered Errors." Working Paper.

3. Mammen, E. (1993). "Bootstrap and Wild Bootstrap for High Dimensional Linear Models." *Annals of Statistics*, 21(1), 255-285.

## 文件位置

- 实现代码：`/Users/cuiqingsong/Documents/论文 3/src/analysis/models.py`
- 配置文件：`/Users/cuiqingsong/Documents/论文 3/analysis_config.yaml`
- 使用示例：`/Users/cuiqingsong/Documents/论文 3/examples/bootstrap_example.py`
- 输出示例：`/Users/cuiqingsong/Documents/论文 3/examples/bootstrap_output_example.md`

## 注意事项

1. **计算时间**：9999次Bootstrap可能需要几分钟到几十分钟，取决于数据大小
2. **内存使用**：Bootstrap需要存储大量中间结果，确保有足够的内存
3. **随机种子**：设置seed以确保结果可重复
4. **并行计算**：当前实现为单线程，可考虑使用joblib进行并行化

## 更新日志

- 2024-XX-XX: 初始实现Wild Cluster Bootstrap
- 支持Rademacher、Mammen和Webb六点分布
- 集成到现有分析流程
- 添加LaTeX表格输出
