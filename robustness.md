# Robustness Checks (Executed)

## Core Checks
1.  **Parallel Trends Test**: Joint significance of pre-treatment coefficients ($\sum_{\tau=-12}^{-2} \beta_\tau = 0$).
2.  **Placebo Dates**: Randomly assign event dates (1,000 simulations); distribution of placebo $p$-values should be uniform.
3.  **Alternative Event Windows**: Re-estimate with $\tau \in [-6, 6]$ and $\tau \in [-24, 24]$.

## Sample Sensitivity
4.  **Exclude January**: Drop all events starting in Month 1 to rule out base-period/chain-linking artifacts.
5.  **Exclude Energy**: Drop COICOP 04.5 to test sensitivity to energy volatility.
6.  **Exclude "Tiny" Countries**: Drop Luxembourg, Malta, Cyprus.
7.  **Balanced Panel**: Keep only events with full $\pm 12$ month coverage.

## Specification Sensitivity
8.  **Alternative Thresholds**: $|\Delta Wedge| > 0.5\%$ and $>2.0\%$.
9.  **Log-Log vs Log-Level**: Replace log outcomes with levels.
10. **Standard Errors**: Cluster at geo, geo×coicop, geo×year.
11. **Lagged Dependent Variable**: Include LDV as robustness.
12. **Donut Design**: Drop $t=0$ and $t=1$.

## Heterogeneity (Sub-sample Analysis)
13. **VAT Rate Type**: Split sample into "Standard Rate" changes vs "Reduced Rate" changes.
14. **Euro Area vs Non-Euro**: Check if monetary union membership affects transmission.
