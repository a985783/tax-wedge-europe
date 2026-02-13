import os
import json
import pandas as pd
import numpy as np
import eurostat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.time_parse import normalize_time

OUTPUT_DIR = "output"
TABLES_DIR = os.path.join(OUTPUT_DIR, "tables")

os.makedirs(TABLES_DIR, exist_ok=True)

def _load_metadata():
    local_path = "data/raw/prc_hicp_manr.parquet"
    if os.path.exists(local_path):
        return pd.read_parquet(local_path)
    return eurostat.get_data_df("prc_hicp_manr")

def _to_abs_month(val):
    if pd.isna(val):
        return np.nan
    s = normalize_time(val)
    if isinstance(s, str) and "-" in s:
        parts = s.split("-")
        if len(parts) >= 2:
            try:
                return int(parts[0]) * 12 + int(parts[1])
            except ValueError:
                pass
    try:
        dt = pd.to_datetime(s)
        return int(dt.year) * 12 + int(dt.month)
    except Exception:
        return np.nan


def match_events(sample_n=500, seed=12345):
    try:
        events = pd.read_parquet("data/processed/events_list.parquet")
    except Exception as e:
        return {"precision": 0.0, "error": str(e)}

    if events.empty:
        return {"precision": 0.0, "error": "events_list empty"}

    events = events.copy()
    events['time'] = events['time'].map(normalize_time)
    events['abs_month'] = events['time'].map(_to_abs_month)

    if len(events) > sample_n:
        events = events.sample(sample_n, random_state=seed)

    try:
        meta = _load_metadata()
    except Exception as e:
        return {"precision": 0.0, "error": str(e)}

    if meta is None or meta.empty:
        return {"precision": 0.0, "error": "metadata empty"}

    meta.columns = [c.lower() for c in meta.columns]
    if 'geo\\time_period' in meta.columns:
        meta = meta.rename(columns={'geo\\time_period': 'geo'})

    # Melt to long if needed (time columns)
    if 'time' in meta.columns and 'value' in meta.columns:
        meta_long = meta.copy()
    else:
        id_vars = [c for c in meta.columns if not c[0].isdigit() and not c.startswith('19') and not c.startswith('20')]
        value_vars = [c for c in meta.columns if c not in id_vars]
        meta_long = meta.melt(id_vars=id_vars, value_vars=value_vars, var_name='time', value_name='value')

    meta_long['time'] = meta_long['time'].map(normalize_time)
    meta_long['abs_month'] = meta_long['time'].map(_to_abs_month)

    # Keep only relevant columns if available
    keep_cols = [c for c in ['geo', 'coicop', 'time', 'abs_month', 'value'] if c in meta_long.columns]
    meta_long = meta_long[keep_cols]

    # Match by geo, coicop, and time within +/- 1 month
    merged = events.merge(meta_long, on=['geo', 'coicop'], how='left', suffixes=('', '_meta'))
    merged['month_diff'] = (merged['abs_month'] - merged['abs_month_meta']).abs()
    matched = merged[merged['month_diff'] <= 1]

    matched_events = matched[['geo', 'coicop', 'time']].drop_duplicates()
    precision = len(matched_events) / max(len(events), 1)

    summary = pd.DataFrame({
        'sample_n': [len(events)],
        'matched_n': [len(matched_events)],
        'precision': [precision]
    })

    summary.to_csv(os.path.join(TABLES_DIR, 'audit_summary.csv'), index=False)

    # Simple LaTeX table
    with open(os.path.join(TABLES_DIR, 'audit_summary.tex'), 'w') as f:
        f.write("\\begin{table}[htbp]\n")
        f.write("\\centering\n")
        f.write("\\caption{Audit Summary (Metadata Match)}\n")
        f.write("\\label{tab:audit_summary}\n")
        f.write("\\begin{tabular}{lccc}\n\\toprule\n")
        f.write("Sample N & Matched N & Precision \\\\\n")
        f.write("\\midrule\n")
        f.write(f"{len(events)} & {len(matched_events)} & {precision:.3f} \\\\\n")
        f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")

    return {"precision": precision, "sample_n": len(events), "matched_n": len(matched_events)}


if __name__ == "__main__":
    match_events()
