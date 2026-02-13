# Reviewer Attack List & Defense Strategy

## ⚔️ Attack 1: "Mechanical" Identification
**Critique**: "Your 'Tax Wedge' is just a mechanical calculation. How do we know it captures exogenous policy shocks and not just Eurostat accounting noise or re-weighting artifacts?"
**Defense (Pre-emptive)**:
- **Validation**: We manually audited 500 events against legislative records (Table \ref{tab:audit_summary}) and found a <2% false positive rate.
- **Thresholds**: We use a strict 1% threshold to filter out noise.
- **Controls**: We explicitly control for monthly seasonality and use differencing to remove base-year effects.
**Evidence**: Section 3.2 (Audit) and Appendix B (Robustness).

## ⚔️ Attack 2: Endogeneity of Tax Reforms
**Critique**: "Tax changes don't happen in a vacuum. Governments raise VAT when the economy is overheating (or cut it in recessions). Your estimates are biased by the cycle."
**Defense (Pre-emptive)**:
- **Stacked Event Study**: We focus on the *high-frequency* (monthly) response within a tight window (+/- 12 months). Macro conditions don't jump sharply in the exact month of the tax change.
- **Pre-trends**: We show flat pre-trends ($t < 0$), proving that prices weren't already accelerating before the tax shock.
- **Clean Controls**: Our control group includes country-sectors that *didn't* have a shock but faced the same macro environment.

## ⚔️ Attack 3: External Validity vs. Benzarti et al. (2020)
**Critique**: "Benzarti et al. (2020) found strong asymmetry. Why are your results different? Is your sample biased towards goods?"
**Defense (Pre-emptive)**:
- **Reconciliation**: We admit this explicitly. Benzarti focuses on services (hairdressers, restaurants). Our sample covers the full HICP basket (mostly goods).
- **Table**: We replicate their finding when restricting to Services (Table \ref{tab:benzarti_benchmark}), showing asymmetry there.
- **Argument**: Goods markets (tradables) are more competitive than local services, forcing symmetry. This is a *feature*, not a bug, of our comprehensive analysis.

## ⚔️ Attack 4: Anticipation Effects
**Critique**: "VAT changes are announced months in advance. Firms surely adjust prices *before* the implementation date."
**Defense (Pre-emptive)**:
- **Visual Evidence**: The event study plots show no significant movement at $t=-1, -2$.
- **Mechanism**: In Europe, tax-inclusive pricing means changing the sticker price is costly (menu costs) and salient. Firms prefer to wait until the tax actually changes to justify the new price to consumers.

## ⚔️ Attack 5: Cross-Country Heterogeneity
**Critique**: "Pooling Greece with Germany is dangerous. Institutional quality differs."
**Defense (Pre-emptive)**:
- **Heterogeneity Analysis**: We explicitly split the sample (Core vs. Periphery) and show the results hold in both, though magnitudes differ.
- **Fixed Effects**: Our model includes Country-Sector fixed effects to absorb institutional baselines.
