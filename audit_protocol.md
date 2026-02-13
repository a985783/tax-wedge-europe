# Data Audit Protocol: Narration Verification

## 1. Objective
To assess the accuracy and reliability of the identified narrative events by cross-referencing a stratified sample of events with official Eurostat metadata and qualitative reports.

## 2. Sampling Strategy
We employ a **Stratified Random Sampling** method to ensure representativeness across two key dimensions: Geography and Sector.

- **Total Sample Size**: $N = 500$ events.
- **Strata**:
  1.  **Country Group**: Core vs. Periphery (to capture different reporting standards and economic structures).
  2.  **COICOP Sector**: Food (01), Energy (04.5), Services (07-12) (to capture sector-specific shocks).

### Allocation
The sample is allocated proportionally to the volume of events identified in the full dataset, with a minimum quota of 30 events per stratum to ensure statistical validity for sub-group analysis.

## 3. Verification Source: Eurostat Metadata
Each sampled event is audited against **Eurostat HICP Metadata (prc_hicp_manr)** and national statistical office press releases. The metadata matching is automated and summarized in `output/tables/audit_summary.csv` and `output/tables/audit_summary.tex`.

### Verification Criteria
An event is classified as **Confirmed (True Positive)** if:
1.  **Timing Match**: The narrative event date aligns with a flagged structural break or revision in Eurostat data within a $\pm 1$ month window.
2.  **Content Match**: The text description of the event (e.g., "VAT change," "Methodology update") matches the metadata description.

An event is classified as a **False Positive** if:
1.  No corresponding official record exists in Eurostat metadata.
2.  The event refers to a prospect that was never implemented (e.g., a proposed tax hike that was cancelled).

## 4. Audit Procedure
1.  **Extraction**: Extract 500 events using the seed `12345` for reproducibility.
2.  **Automated Match**: Match by geo×coicop and time within ±1 month using `prc_hicp_manr`.
3.  **Manual Review**: A human annotator reviews each event against the Eurostat `FLAGS` domain and `COMMENTS` field.
3.  **Classification**: Tag each event as `Confirmed`, `False Positive`, or `Ambiguous` (Ambiguous treated as Error for conservative estimation).
4.  **Reporting**: Calculate Precision, Recall (estimated), and False Discovery Rate (FDR). Automated precision is reported in `output/tables/audit_summary.tex`.

## 5. Output
The results are compiled into `output/tables/audit_summary.tex` presenting the error rates broken down by region and sector.
