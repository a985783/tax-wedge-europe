# 机制图谱与变量映射 (Mechanism Map)

## 核心机制路径 (Core Mechanism Path)

```mermaid
graph TD
    A[VAT Rate Change (Tax Shock)] -->|Cost Shock| B(Marginal Cost Change)
    B -->|Pricing Decision| C{Firms Set Prices}
    
    C -->|Full Pass-through| D[Consumer Prices Change 1:1]
    C -->|Partial Pass-through| E[Consumer Prices Change < 1:1]
    
    subgraph "调节效应 (Moderators)"
    M1[不对称性 Asymmetry] -.->|Direction| C
    M2[行业异质性 Heterogeneity] -.->|Market Structure| C
    M3[商品显著性 Salience] -.->|Weight in Basket| C
    end
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#9f9,stroke:#333,stroke-width:2px
    style E fill:#ff9,stroke:#333,stroke-width:2px
```

## 关键变量映射 (Variable Mapping)

| 概念 (Concept) | 代理变量 (Proxy Variable) | 数据来源/构造 |
| :--- | :--- | :--- |
| **政策冲击 (Policy Shock)** | `delta_tw` (Tax Wedge Change) | VAT rate changes from database |
| **价格响应 (Price Response)** | `norm_log_hicp` | Log HICP normalized to t=-1 |
| **不对称性 (Asymmetry)** | `is_hike` (Dummy), `pos_shock`, `neg_shock` | Sign of `delta_tw` |
| **行业类型 (Sector)** | `coicop` (CP01, CP045, CP11...) | COICOP 2-4 digit codes |
| **显著性/权重 (Salience)** | `weight`, `weight_group` | HICP weights (expenditure share) |
| **时间动态 (Dynamics)** | `rel_time` (Month relative to event) | Event Study Time Window [-12, +12] |

## 理论逻辑 (Theoretical Logic)

1.  **基准传导 (Baseline)**: 在完全竞争市场中，供给弹性无穷大时，税收完全传导给消费者 (Pass-through = 1)。
2.  **不对称性 (Asymmetry)**: 
    -   *假设*: "Rocket and Feathers" —— 价格涨得快（加税），跌得慢（减税）。
    -   *机制*: 菜单成本、消费者搜索成本、企业利润最大化动机。
3.  **异质性 (Heterogeneity)**:
    -   *必需品 vs 服务*: 必需品（能源、食品）需求弹性低，传导率应更高；服务业市场势力大或粘性大，传导率可能较低。
    -   *高权重 vs 低权重*: 高权重商品更受消费者关注（Salience），企业调整价格可能更谨慎（传导率低？）或者因为竞争激烈而更接近完全传导？需实证检验。
