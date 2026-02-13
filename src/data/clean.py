import pandas as pd
import os
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.time_parse import normalize_time

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
METADATA_DIR = "output/metadata"

def load_and_clean(file_name, value_col_name, filter_unit=None):
    print(f"Processing {file_name}...")
    path = os.path.join(RAW_DIR, f"{file_name}.parquet")
    df = pd.read_parquet(path)
    
    # Rename weird column if exists
    if 'geo\\time_period' in df.columns:
        df = df.rename(columns={'geo\\time_period': 'geo'})
    
    # Filter unit if specified
    if filter_unit and 'unit' in df.columns:
        df = df[df['unit'] == filter_unit]
    
    # Keep only necessary columns
    cols_to_keep = ['geo', 'coicop', 'time', 'value']
    df = df[cols_to_keep]
    
    # Rename value column
    df = df.rename(columns={'value': value_col_name})

    # Normalize time format
    df['time'] = df['time'].map(normalize_time)
    
    return df

def main():
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)
    if not os.path.exists(METADATA_DIR):
        os.makedirs(METADATA_DIR)

    # 1. Load HICP (I15)
    # Ensure we use Index 2015=100
    hicp = load_and_clean("prc_hicp_midx", "hicp", filter_unit="I15")
    
    # 2. Load HICP-CT (I15)
    hicp_ct = load_and_clean("prc_hicp_cind", "hicp_ct", filter_unit="I15")
    
    # Validation: Check overlap
    common_ids = pd.merge(hicp[['geo', 'coicop', 'time']], hicp_ct[['geo', 'coicop', 'time']], on=['geo', 'coicop', 'time'], how='inner')
    overlap_ratio = len(common_ids) / max(len(hicp), 1)
    if overlap_ratio < 0.5:
        print("Warning: Low overlap between HICP and HICP-CT. Check data integrity.")

    # 3. Merge HICP and HICP-CT
    print("Merging HICP and HICP-CT...")
    merged = pd.merge(hicp, hicp_ct, on=['geo', 'coicop', 'time'], how='inner')
    
    # 4. Load Weights
    # Weights are annual. Time format might be "2015".
    weights = load_and_clean("prc_hicp_inw", "weight")
    
    # Create 'year' column for merging
    # HICP time is YYYY-MM
    merged['year'] = merged['time'].str[:4].astype(int)
    
    # Weights time is usually YYYY (int or str)
    # Let's inspect weights time format. Assuming it is string "YYYY" from fetch.py
    # If fetch.py treated "2015" as "2015", it is fine.
    # But sometimes Eurostat annual data might be "2015" or "2015A00" etc.
    # Let's try to convert to int.
    try:
        weights['year'] = weights['time'].astype(str).str[:4].astype(int)
    except:
        print("Warning: Could not parse year from weights time column. Check data.")
        print(weights['time'].unique()[:5])
    
    # Drop time column from weights to avoid conflict
    weights = weights.drop(columns=['time'])
    
    # Merge Weights
    print("Merging Weights...")
    final_df = pd.merge(merged, weights, on=['geo', 'coicop', 'year'], how='left')
    
    # Save
    output_path = os.path.join(PROCESSED_DIR, "merged_indices.parquet")
    final_df.to_parquet(output_path, index=False)
    print(f"Saved merged data to {output_path} ({len(final_df)} rows)")

    # Data quality report
    time_vals = merged['time'].dropna().astype(str)
    time_min = time_vals.min() if not time_vals.empty else None
    time_max = time_vals.max() if not time_vals.empty else None

    quality = {
        "hicp_rows": int(len(hicp)),
        "hicp_ct_rows": int(len(hicp_ct)),
        "merged_rows": int(len(merged)),
        "overlap_ratio": float(overlap_ratio),
        "time_min": time_min,
        "time_max": time_max,
        "missing_hicp_rate": float(hicp['hicp'].isna().mean()),
        "missing_hicp_ct_rate": float(hicp_ct['hicp_ct'].isna().mean()),
        "missing_weight_rate": float(final_df['weight'].isna().mean()),
    }

    quality_path = os.path.join(METADATA_DIR, "data_quality.json")
    with open(quality_path, "w") as f:
        json.dump(quality, f, indent=2)

if __name__ == "__main__":
    main()
