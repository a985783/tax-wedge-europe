# Project Plan: The Tax Wedge & Price Rigidity (Eurostat Replication)

This plan outlines the end-to-end implementation of your paper using Eurostat's HICP and HICP-CT data.

## Phase 1: Data Infrastructure & Pipeline
**Goal**: Establish a reproducible data pipeline from Eurostat API to structured local datasets.
1.  **Project Setup**: Initialize `data/`, `src/`, `output/` structure and `requirements.txt` (pandas, requests, statsmodels, linearmodels).
2.  **API Extraction (`src/data/fetch.py`)**:
    *   Fetch **HICP** (`prc_hicp_midx`) and **HICP-CT** (`prc_hicp_cind`) via Eurostat REST API (JSON-stat/SDMX).
    *   Fetch **Weights** (`prc_hicp_inw`) for welfare/contribution analysis.
    *   Fetch **Controls** (optional): `prc_hicp_cmon` for validation.
3.  **Data Cleaning (`src/data/clean.py`)**:
    *   Standardize country codes (Geo) and item codes (COICOP).
    *   Merge HICP and HICP-CT on `geo`, `coicop`, `time`.
    *   Save processed data as Parquet for performance.

## Phase 2: Identification Strategy (The "Tax Wedge")
**Goal**: Construct the identification instrument and isolate tax events.
1.  **Wedge Construction**:
    *   Calculate $TW_{c,k,t} = \ln(HICP_{c,k,t}) - \ln(HICP^{CT}_{c,k,t})$.
    *   Calculate $TW^{yoy}$ and monthly changes.
2.  **Event Detection Algorithm (`src/identification/detect_events.py`)**:
    *   Implement threshold/break detection on TW changes to identify "Tax Change Months".
    *   Classify events: **Tax Hike** vs. **Tax Cut**.
    *   Validate against official metadata (using `prc_hicp_cmon` notes if available) to ensure "Strong Identification".

## Phase 3: Empirical Estimation
**Goal**: Run the stacked event study and DDD models.
1.  **Stacked Dataset Construction**:
    *   Create window $\tau \in [-12, +12]$ around each event.
    *   Build the stacked panel dataset.
2.  **Estimation (`src/analysis/models.py`)**:
    *   **Baseline**: Stacked Event Study ($TW_{i,t} = \alpha + \sum \beta_\tau + \dots$).
    *   **DDD**: Introduce control groups (non-affected categories).
    *   **Asymmetry Test**: Estimate separate coefficients for Hikes vs. Cuts to test "Rocket and Feather" effects.
3.  **Mechanism Tests**:
    *   Interaction terms with **Market Power** (proxy by sector/weight) and **Inflation Regime** (High vs Low).

## Phase 4: Output & Paper Writing
**Goal**: Generate publication-ready artifacts.
1.  **Visualization**:
    *   Plot dynamic pass-through coefficients (Event Study graphs).
    *   Plot raw price vs. constant-tax price for case studies.
2.  **Tables**:
    *   Descriptive stats of tax events (Count by country/year).
    *   Regression results (Pass-through rates).
3.  **Paper Draft**:
    *   Assemble sections: Intro, Institutional Background, Strategy, Results, Mechanisms.

## Phase 5: Replication Package
*   Finalize `README.md` with one-click run instructions.
*   Export environment configuration (`environment.yml` / `requirements.txt`).
