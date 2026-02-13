# Identification Threats and Mitigation Strategies

## 1. Endogeneity of Tax Reforms
*   **Threat**: Governments may cut taxes during recessions (counter-cyclical) or raise them during overheating. Estimates would be biased by the correlation between $\varepsilon_{c,k,t}$ (demand shock) and $\text{Size}_e$.
*   **Mitigation**:
    *   **Pre-trend Testing**: Explicitly test $\beta_\tau = 0$ for $\tau < 0$. Flat pre-trends indicate shocks are not anticipated/endogenous to immediate price paths.
    *   **High-Frequency**: Monthly timing is often determined by legislative calendars, exogenous to monthly demand fluctuations.

## 2. Anticipation Effects
*   **Threat**: Firms may raise prices *before* a known VAT hike to smooth the transition, leading to $\beta_{-1} > 0$ and underestimating the jump at $t=0$.
*   **Mitigation**:
    *   Visual inspection of $\tau = -1, -2$.
    *   Robustness check: Re-center reference period to $t=-3$ or $t=-6$.

## 3. Base Period Artifacts (January Effect)
*   **Threat**: HICP-CT base tax rates ($\tau_0$) reset every December. A tax change in January might be confounded by chain-linking adjustments.
*   **Mitigation**:
    *   **Difference-in-Differences**: The differencing operator cancels out level shifts.
    *   **Robustness**: Exclude all shocks occurring in January ($Month \neq 1$).

## 4. Weight Composition Changes
*   **Threat**: HICP weights update annually. If a tax hike causes massive substitution away from a good, the aggregate index might skew.
*   **Mitigation**:
    *   **Granularity**: Analysis at COICOP-5 (very narrow) level reduces within-category substitution.
    *   **Frequency**: Weights are constant *within* the calendar year.

## 5. Concurrent Supply Shocks
*   **Threat**: An energy tax hike often coincides with rising global oil prices.
*   **Mitigation**:
    *   **Control Group**: The control group (other countries/sectors) experiences the same global oil shock.
    *   **Time FE**: $\lambda_{t,e}$ absorbs common global/European price movements.

## 6. Measurement Error in HICP-CT
*   **Threat**: Eurostat might miscalculate HICP-CT for complex bundles, creating "fake" shocks.
*   **Mitigation**:
    *   **Threshold**: Ignore small shocks ($<1\%$) which are noise-prone.
    *   **Validation**: Manual audit of 500 events; cross-check with 'i' flags.

## 7. Confounding Overlapping Shocks
*   **Threat**: Two tax changes happen in close succession (e.g., +2% in Jan, -1% in March).
*   **Mitigation**:
    *   **Clean Window Filter**: Drop any event if another shock occurs within $\pm 3$ months.

## 8. Asymmetric Sample Selection
*   **Threat**: Tax changes might be concentrated in specific volatile sectors (Energy) or countries.
*   **Mitigation**:
    *   **Heterogeneity Analysis**: Report results separately for Food, Energy, Services, Goods.
    *   **Weighted Regressions**: Re-weight to match EU aggregate consumption basket.

## 9. Seasonality
*   **Threat**: Prices and taxes might both follow seasonal patterns (e.g., January adjustments).
*   **Mitigation**:
    *   **Month FE**: Included in some specifications.
    *   **Comparison**: Controls have same seasonality but no tax shock.

## 10. Cross-Border Leakage
*   **Threat**: For small countries, tax hikes might drive consumers across borders, dampening local price response (attenuation bias).
*   **Mitigation**:
    *   Acknowledge as a mechanism for incomplete pass-through.
    *   Robustness: Exclude small border-heavy countries (e.g., Luxembourg).
