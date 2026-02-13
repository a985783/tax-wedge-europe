# Replication Guide: The Tax Wedge

This document provides detailed instructions for replicating the results presented in the paper: **"The Tax Wedge: High-Frequency Identification of Indirect Tax Shocks and Price Rigidity in Europe"**.

## 1. Overview
This replication package contains the complete codebase and instructions required to reproduce the empirical findings, including data acquisition, shock identification, model estimation, and robustness checks. The project is structured to ensure transparency and reproducibility of the high-frequency identification of indirect tax shocks across European markets.

## 2. System Requirements
- **Operating System**: Linux, macOS, or Windows (via WSL2 recommended).
- **Python Version**: Python 3.10 or higher.
- **Hardware**: 
  - Minimum 8GB RAM (16GB recommended for large-scale Eurostat data processing).
  - Stable internet connection for initial data fetching from Eurostat API.

## 3. Installation

### 3.1 Environment Setup
It is highly recommended to use a virtual environment to avoid dependency conflicts.

```bash
# Create a virtual environment
python -m venv venv

# Activate the environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate
```

### 3.2 Install Dependencies
Ensure `pip` is up to date and install the required packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```
*(Note: Ensure a `requirements.txt` file exists with necessary libraries like `pandas`, `numpy`, `scipy`, `statsmodels`, `requests`, `pyyaml`, etc.)*

## 4. Replication Workflow

The replication process follows a sequential pipeline. Configuration parameters (sample periods, country codes, significance levels) are managed via `analysis_config.yaml`.

### Step 1: Data Fetching
Retrieve raw data directly from the Eurostat API.
```bash
python src/data/fetch.py
```
*Output: Raw data files stored in `data/raw/`.*

### Step 2: Data Cleaning
Process raw data into a structured format suitable for analysis.
```bash
python src/data/clean.py
```
*Output: Cleaned datasets in `data/processed/`.*

### Step 3: Event Identification
Identify indirect tax shock events using the high-frequency identification strategy.
```bash
python src/identification/detect_events.py
```
*Output: Identified events and shock series in `output/data/`.*

### Step 4: Estimation & Analysis
Estimate the main econometric models and price rigidity statistics.
```bash
python src/analysis/models.py
```

### Step 5: Robustness & Placebo Tests
Run sensitivity analyses and placebo tests to validate the identification strategy.
```bash
python src/analysis/robustness.py
```

### Step 6: Audit & Validation
Perform metadata matching and audit checks to ensure data integrity.
```bash
python src/audit/metadata_match.py
```

## 5. Expected Outputs
Upon successful completion, the following outputs will be generated in the `output/` directory:

- **`output/figures/`**: Visualizations of tax shocks, impulse response functions (IRFs), and price distribution plots.
- **`output/tables/`**: Regression results and summary statistics in `.tex` format for direct inclusion in LaTeX documents.
- **`output/reports/`**: Automated analysis reports summarizing key findings and audit results.

## 6. Project Structure
```text
.
├── src/                # Source code
│   ├── data/           # Data acquisition and cleaning scripts
│   ├── identification/ # Event identification logic
│   ├── analysis/       # Statistical models and robustness checks
│   ├── audit/          # Validation and metadata matching
│   └── utils/          # Shared utility functions
├── data/               # Local data storage (raw and processed)
├── docs/               # Technical documentation and codebooks
├── tests/              # Unit tests for core modules
├── examples/           # Jupyter notebooks or minimal examples
├── output/             # Final results (figures, tables, reports)
├── analysis_config.yaml # Global configuration file
└── REPLICATION.md      # This file
```

## 7. Computational Requirements
- **Execution Time**: Total execution time is approximately 30-60 minutes depending on internet speed and CPU performance.
- **Storage**: Approximately 2GB of disk space is required for the full dataset and intermediate outputs.

## 8. Troubleshooting
- **API Errors**: If Eurostat API is down, retry the `fetch.py` script or check your network proxy settings.
- **Memory Issues**: For systems with low RAM, consider processing countries individually by modifying the `countries` list in `analysis_config.yaml`.
- **Dependency Conflicts**: Ensure you are using Python 3.10+ and a clean virtual environment.

## 9. Contact Information
For questions regarding the code or data, please contact:
- **Author**: Qingsong Cui
- **Email**: qingsongcui9857@gmail.com
- **Repository**: https://github.com/a985783/tax-wedge-europe

---
*This replication package is provided for academic purposes. Please cite the original paper when using this code or data.*
