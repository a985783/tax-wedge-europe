# Figures and Tables

## Figure 1: Aggregate Pass-through of Indirect Tax Shocks
**File**: `main_event_study.png`
**Note**: The figure plots the coefficients $\beta_\tau$ from the stacked event study regression (Eq. 1) for the full sample of over 20,000 tax events. The dependent variable is the cumulative log change in consumer prices relative to $t-1$. Shaded areas represent 95% confidence intervals clustered at the country-sector level. The vertical line at $t=0$ marks the implementation month of the tax change. The results show a sharp, immediate price adjustment with partial pass-through stabilizing around 0.5.

## Figure 2: Sectoral Heterogeneity in Pass-through
**File**: `heterogeneity_sector.png`
**Note**: This figure displays the dynamic pass-through estimates disaggregated by major product groups: Food (green), Energy (red), and Services (blue). Energy exhibits the highest and most volatile pass-through, while Services show a more gradual and muted response. Food prices show high initial pass-through.

## Figure 3: Testing for Asymmetry: Tax Hikes vs. Tax Cuts
**File**: `asymmetry_hike_vs_cut.png`
**Note**: The left panel shows the estimated response to Tax Hikes (blue line), and the right panel shows the response to Tax Cuts (inverted, red line). The bottom panel plots the difference between the absolute magnitudes of the two coefficients. Dotted lines indicate 95% confidence intervals. The difference is statistically indistinguishable from zero at all horizons, indicating symmetric pass-through.

## Table 1: Descriptive Statistics of the Tax Wedge Database
**Note**: Summary statistics for the Tax Wedge dataset covering 30 European countries from 1996 to 2024. The table reports the number of identified tax events, the mean and standard deviation of the Tax Wedge shocks, and the distribution of events across major product categories (COICOP).

## Table 2: Formal Tests of Asymmetry
**Note**: The table reports p-values from Wald tests comparing the pass-through coefficients of tax hikes ($\beta^{Hike}_\tau$) and tax cuts ($\beta^{Cut}_\tau$) at horizons $\tau = 0, 6, 12$.
*   **Hypothesis**: $H_0: \beta^{Hike}_\tau = |\beta^{Cut}_\tau|$
*   **Result**: We fail to reject the null hypothesis in all specifications (p-values > 0.6), confirming symmetric price adjustment.
