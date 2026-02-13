# The Tax Wedge: High-Frequency Identification of Indirect Tax Shocks and Price Rigidity in Europe

## 1. Motivation
Indirect taxes (VAT, excise duties) account for ~30% of EU tax revenue. Understanding their pass-through to consumer prices is critical for inflation dynamics and welfare analysis. However, identifying causal effects is challenged by the endogeneity of tax reforms (often responding to business cycles) and the difficulty in pinpointing precise timing in low-frequency data ("macro-micro" disconnect).

## 2. The Gap
*   **Macro studies**: Aggregate data masks granular heterogeneity.
*   **Micro studies**: Often lack external validity or rely on labor-intensive manual data collection (narrative approach).
*   **Existing Theory**: Predicts asymmetric "rockets and feathers" adjustment, but empirical evidence is mixed and often limited to single countries.

## 3. Contribution
We introduce a scalable, automated identification strategy leveraging the **Tax Wedge**—the mechanical divergence between HICP and HICP-CT (Constant Tax Rates).
*   **Data**: 30 European countries, 100+ product categories, 1996–2024.
*   **Scale**: Automated detection of >20,000 idiosyncratic tax shocks.
*   **Method**: High-frequency identification (HFI) applied to fiscal policy.

## 4. Methodology
*   **Identification**: $\text{Tax Wedge}_{c,k,t} = \ln(\text{HICP}_{c,k,t}) - \ln(\text{HICP-CT}_{c,k,t})$.
*   **Estimation**: Stacked Event Study design with "Clean Window" filtering (no confounding shocks in $\pm 12$ months).
*   **Specification**: Controls for unit and time fixed effects to isolate the dynamic response to tax shocks.

## 5. Key Results
*   **Pass-through**: Substantial but incomplete (0.4–0.6) in the medium term. Immediate adjustment at $t=0$.
*   **Heterogeneity**: High in Energy/Food, lower in Services.
*   **Symmetry (Counter-intuitive)**: We find **no evidence of asymmetric pass-through**.
    *   Tax Hikes vs. Tax Cuts: Coefficients are statistically indistinguishable (p-value > 0.6).
    *   Challenges the "rockets and feathers" hypothesis; suggests high competition in European retail markets.

## 6. Implications
*   **Fiscal Surveillance**: The Tax Wedge provides a real-time tool for monitoring fiscal stance.
*   **Policy**: The symmetric response implies that temporary VAT cuts are effective stimulus tools (passed through to consumers), contrary to concerns that firms capture the benefits.
*   **Theory**: Downward price rigidity may be less pervasive in competitive goods markets than previously thought.
