# The Tax Wedge: High-Frequency Identification of Indirect Tax Shocks and Price Rigidity in Europe

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository contains the complete replication package for the paper **"The Tax Wedge: High-Frequency Identification of Indirect Tax Shocks and Price Rigidity in Europe"**.

## Abstract

This paper introduces a novel "Tax Wedge" indicator, leveraging the mechanical divergence between the Harmonized Index of Consumer Prices (HICP) and the HICP at Constant Tax Rates (HICP-CT) to automate the identification of over 20,000 idiosyncratic tax shocks across 30 European countries and 100+ product categories from 1996 to 2024. By constructing this high-frequency panel, we provide new evidence on the dynamics of indirect tax pass-through and price rigidity in the Eurozone.

## Key Findings

1.  **Symmetric Pass-through**: We find evidence of symmetric pass-through for both tax increases and decreases, with an average elasticity of **0.35**.
2.  **Heterogeneity**: Pass-through rates are significantly higher in **core economies** and for **non-durable goods**, reflecting differences in market competition and price adjustment costs.
3.  **Methodological Innovation**: The study employs a **stacked event study design** to handle the staggered nature of tax shocks across countries and sectors, ensuring robust causal identification.

---

## Quick Start

### Prerequisites
- Python 3.8 or higher
- `pip` or `conda` package manager
- Internet connection (to fetch data from Eurostat API)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/a985783/tax-wedge-europe.git
   cd tax-wedge-europe
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Replication Steps

To replicate the results presented in the paper, execute the following scripts in sequence:

1.  **Data Acquisition**: Fetch raw HICP and HICP-CT data from Eurostat.
    ```bash
    python src/data/fetch.py
    ```
2.  **Data Processing**: Clean and merge the raw indices into a unified panel.
    ```bash
    python src/data/clean.py
    ```
3.  **Event Identification**: Calculate the Tax Wedge and identify tax shock events.
    ```bash
    python src/identification/detect_events.py
    ```
4.  **Main Analysis**: Run the stacked event study models and generate primary results.
    ```bash
    python src/analysis/models.py
    ```
5.  **Robustness Checks**: Execute sensitivity analyses and placebo tests.
    ```bash
    python src/analysis/robustness.py
    ```
6.  **Audit & Validation**: Perform metadata matching to validate identified shocks against official records.
    ```bash
    python src/audit/metadata_match.py
    ```

---

## Project Structure

```text
.
├── src/                # Source code
│   ├── data/           # Data fetching and cleaning scripts
│   ├── identification/ # Tax Wedge calculation and event detection
│   ├── analysis/       # Econometric models and robustness tests
│   ├── audit/          # Validation and metadata matching
│   └── utils/          # Helper functions and configurations
├── data/               # Data directory
│   ├── raw/            # Raw data from Eurostat (Parquet format)
│   └── processed/      # Cleaned panels and identified events
├── docs/               # Documentation and supplementary materials
├── tests/              # Unit tests for core modules
├── examples/           # Jupyter notebooks with usage examples
├── output/             # Generated figures, tables, and logs
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## Data Description

The analysis relies on two primary datasets from Eurostat:
- **HICP (prc_hicp_midx)**: Harmonized Index of Consumer Prices.
- **HICP-CT (prc_hicp_cidx)**: HICP at Constant Tax Rates.

The "Tax Wedge" is defined as the log difference between these two indices, capturing the cumulative impact of indirect tax changes on consumer prices.

---

## Citation

If you use this code or the Tax Wedge indicator in your research, please cite:

```bibtex
@article{cui2024taxwedge,
  title={The Tax Wedge: High-Frequency Identification of Indirect Tax Shocks and Price Rigidity in Europe},
  author={Cui, Qingsong},
  year={2024},
  journal={Working Paper}
}
```

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## Contact

For questions or feedback regarding the replication package, please contact:

**Qingsong Cui**  
Email: qingsongcui9857@gmail.com
