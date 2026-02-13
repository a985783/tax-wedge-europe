# Replication Guide

This directory contains the necessary scripts to reproduce all tables and figures in the paper.

## Quick Start

You can reproduce the entire analysis pipeline by running the `run_all.sh` script.

### Prerequisites
- Python 3.8+
- Dependencies installed (see `../requirements.txt`)
  ```bash
  pip install -r ../requirements.txt
  ```

### Run Instructions

1. Navigate to the `replication` directory (if you are not already there):
   ```bash
   cd replication
   ```

2. Execute the runner script:
   ```bash
   ./run_all.sh
   ```

   *Note: The script automatically sets the working directory to the project root.*

### Pipeline Steps

The `run_all.sh` script executes the following steps in order:

1.  **Data Fetching** (`src/data/fetch.py`): Loads raw data.
2.  **Data Cleaning** (`src/data/clean.py`): Processes and merges datasets.
3.  **Event Identification** (`src/identification/detect_events.py`): Identifies VAT change events.
4.  **Model Estimation** (`src/analysis/models.py`): Runs the main event study and regression models.
5.  **Benchmarking** (`src/analysis/benchmark_benzarti.py`): Compares results with Benzarti et al. (2020).
6.  **Mechanism Testing** (`src/analysis/mechanism_testing.py`): Performs heterogeneity analysis and mechanism tests.

### Output

- **Tables**: Generated LaTeX and CSV tables are saved in `output/tables/`.
- **Figures**: Generated plots are saved in `output/figures/`.
