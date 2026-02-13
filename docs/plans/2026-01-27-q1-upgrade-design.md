# Q1-Ready Upgrade Design (EER Standard)

Date: 2026-01-27
Owner: Codex + User
Target venue standard: European Economic Review (EER)
Status: **IMPLEMENTED** (See implementation plan for verification details)

## Context
Current repo delivers a Tax Wedge identification and stacked event-study estimates, but method/implementation/outputs are misaligned (thresholds, clean windows, FE structure, sampling). The goal is to upgrade the project to a near-Q1 standard with strict identification, full reproducibility, and comprehensive robustness and audit evidence.

## Goals
- Align paper, code, and outputs with one authoritative identification strategy.
- Ensure full reproducibility: data manifest, hashes, config, and one-click pipeline.
- Provide audit-grade validation of event detection using Eurostat metadata + manual sample.
- Deliver a robustness matrix consistent with EER expectations.
- Allow conclusions to update if stricter methods change results.

## Non-Goals
- Novel theoretical model development beyond current scope.
- New external datasets beyond Eurostat unless required for validation.
- Competitive journal formatting (we focus on content integrity first).

## Recommended Approach
Option A: Strict stacked event study with explicit control group, calendar time FE, unit FE, and weighted estimation, plus panel LP as robustness. This preserves the paper's narrative while meeting identification rigor.

## Data and Reproducibility
- Re-fetch Eurostat datasets with a logged timestamp and data manifest.
- Record dataset row counts, time ranges, missing rates, and hashes in `output/metadata/`.
- Normalize time parsing explicitly (YYYYMmm -> YYYY-MM) to ensure stable matching.
- Remove any undocumented subsampling (e.g., Top 5000 events).
- Store all analysis parameters in `analysis_config.yaml` and reference in the paper.

## Identification and Estimation
- Event definition: baseline threshold |delta_tax_wedge| > 0.01.
- Clean window: country x category +/- 12 months (baseline).
- Control group: same category, other countries in same calendar months, not-yet-treated + never-treated.
- Estimation: weighted OLS with HICP weights; unit FE (geo x coicop) + calendar month FE.
- Interaction structure: C(rel_time) x shock_size with tau=-1 baseline.
- Cluster SE: geo (main), geo x coicop and geo x year (robustness).

## Validation and Robustness
Validation layers:
1) Eurostat metadata match (prc_hicp_manr): automated flag/comment matching.
2) Manual audit: stratified sample of 500 events with recorded evidence.
3) Mechanical consistency checks: stable wedge when no tax change.

Robustness matrix (minimum):
- Pre-trend joint test (tau < 0).
- Placebo event months (1,000 random draws).
- Window sensitivity (+/- 6, 12, 24).
- Threshold sensitivity (0.5%, 1%, 2%).
- Donut design (drop tau = 0 and 1).
- Excluding crisis years, energy, and small countries.
- Alternative clustering levels.
- Panel LP alternative spec.

## Deliverables
- Updated paper and appendices matching code outputs.
- Full set of tables/figures in `output/` consistent with baseline and robustness.
- Audit report tables and evidence logs.
- Reproducibility README with exact pipeline steps.

## Risks and Mitigations
- API instability: caching + hashing + fetch timestamp.
- Result sensitivity: pre-commit to reporting changed findings.
- Computation time: allow optional parallelization and memoization.

## Implementation Steps (High-Level)
1) Rebuild data pipeline with manifest and strict time parsing.
2) Rewrite event detection to standardize thresholds and clean windows.
3) Rebuild event study with explicit control group and FE structure.
4) Add validation + audit tooling and outputs.
5) Implement robustness suite and update paper/appendix.

## Success Criteria
- Paper statements, code parameters, and outputs are identical by construction.
- Full pipeline rerun from raw data reproduces all main and appendix results.
- Robustness matrix complete with documented outputs.

