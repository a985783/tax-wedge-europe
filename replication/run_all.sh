#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status.

# Get the project root directory (parent of replication/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Starting reproduction pipeline..."
echo "Working directory: $PROJECT_ROOT"

echo "[1/6] Fetching data..."
python src/data/fetch.py

echo "[2/6] Cleaning data..."
python src/data/clean.py

echo "[3/6] Detecting events..."
python src/identification/detect_events.py

echo "[4/6] Running main analysis models..."
python src/analysis/models.py

echo "[5/6] Running Benzarti benchmark..."
python src/analysis/benchmark_benzarti.py

echo "[6/8] Testing mechanisms..."
python src/analysis/mechanism_testing.py

echo "[7/8] Running robustness tests..."
python src/analysis/robustness.py

echo "[8/8] Running audit..."
python src/audit/metadata_match.py

echo "Replication complete. Results are in output/tables/ and output/figures/."
