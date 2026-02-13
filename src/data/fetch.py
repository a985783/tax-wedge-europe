import eurostat
import pandas as pd
import os
import time
import json
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.config import load_config
from src.utils.time_parse import normalize_time

DATA_DIR = "data/raw"
METADATA_DIR = "output/metadata"

CONFIG = load_config()
datasets = CONFIG.get("fetch", {}).get("datasets", [
    "prc_hicp_midx",  # HICP (2015=100) - monthly
    "prc_hicp_cind",  # HICP-CT (Constant Tax) - monthly
    "prc_hicp_inw",   # Item weights
    "prc_hicp_cmon"   # Monthly change (for validation)
])

def _hash_file(path):
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def fetch_and_save(code, manifest_records, hash_records):
    print(f"Fetching {code}...")
    try:
        # get_data_df returns a pandas dataframe
        df = eurostat.get_data_df(code)
        if df is not None and not df.empty:
            # Rename columns to lowercase for consistency
            df.columns = [c.lower() for c in df.columns]
            
            # Melt the dataframe to long format (Eurostat returns wide format with dates as columns)
            # Identifying ID columns (usually the first few columns like unit, coicop, geo)
            id_vars = [c for c in df.columns if not c[0].isdigit() and not c.startswith('19') and not c.startswith('20')]
            value_vars = [c for c in df.columns if c not in id_vars]
            
            df_long = df.melt(id_vars=id_vars, value_vars=value_vars, var_name='time', value_name='value')
            df_long['time'] = df_long['time'].map(normalize_time)
            
            # Clean time column (remove letters, keep YYYY-MM)
            # Eurostat time format in columns is often '2020M01' or just '2020M01'
            # But the column names in the dataframe from eurostat package might be just '2020M01'
            
            output_path = os.path.join(DATA_DIR, f"{code}.parquet")
            df_long.to_parquet(output_path, index=False)
            print(f"Saved {code} to {output_path} ({len(df_long)} rows)")

            time_vals = df_long['time'].dropna().astype(str)
            time_min = time_vals.min() if not time_vals.empty else None
            time_max = time_vals.max() if not time_vals.empty else None
            missing_rate = df_long['value'].isna().mean()

            manifest_records.append({
                "dataset": code,
                "rows": len(df_long),
                "time_min": time_min,
                "time_max": time_max,
                "missing_rate": float(missing_rate)
            })
            hash_records[code] = _hash_file(output_path)
        else:
            print(f"Warning: {code} returned empty data")
    except Exception as e:
        print(f"Error fetching {code}: {e}")

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(METADATA_DIR):
        os.makedirs(METADATA_DIR)

    manifest = []
    hashes = {}
    fetch_timestamp = datetime.now(timezone.utc).isoformat()
        
    for code in datasets:
        fetch_and_save(code, manifest, hashes)
        time.sleep(1) # Be nice to the API

    manifest_path = os.path.join(METADATA_DIR, "data_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump({
            "fetched_at_utc": fetch_timestamp,
            "datasets": manifest
        }, f, indent=2)

    hashes_path = os.path.join(METADATA_DIR, "data_hashes.json")
    with open(hashes_path, "w") as f:
        json.dump(hashes, f, indent=2)
