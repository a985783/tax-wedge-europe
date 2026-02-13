import pandas as pd
import numpy as np
import os
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.config import load_config
from src.utils.time_parse import normalize_time

PROCESSED_DIR = "data/processed"
METADATA_DIR = "output/metadata"

CONFIG = load_config()

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

def apply_clean_window(events, window_months):
    events = events.copy()
    events['time'] = events['time'].map(normalize_time)
    events['abs_month'] = events['time'].map(_to_abs_month)
    events = events.sort_values(['geo', 'coicop', 'abs_month'])

    events['prev_event_time'] = events.groupby(['geo', 'coicop'])['abs_month'].shift(1)
    events['next_event_time'] = events.groupby(['geo', 'coicop'])['abs_month'].shift(-1)
    events['dist_prev'] = events['abs_month'] - events['prev_event_time']
    events['dist_next'] = events['next_event_time'] - events['abs_month']

    is_clean_prev = events['dist_prev'].isna() | (events['dist_prev'] > window_months)
    is_clean_next = events['dist_next'].isna() | (events['dist_next'] > window_months)
    events['is_clean'] = is_clean_prev & is_clean_next
    return events

def main():
    print("Loading merged data...")
    df = pd.read_parquet(os.path.join(PROCESSED_DIR, "merged_indices.parquet"))

    # Ensure sorted
    df['time'] = df['time'].map(normalize_time)
    df = df.sort_values(['geo', 'coicop', 'time'])
    
    # Calculate Tax Wedge (TW)
    # Use log difference approximation
    # TW = ln(HICP) - ln(HICP_CT)
    # Note: HICP and HICP_CT are indices.
    
    print("Calculating Tax Wedge...")
    df.loc[df['hicp'] <= 0, 'hicp'] = np.nan
    df.loc[df['hicp_ct'] <= 0, 'hicp_ct'] = np.nan
    df['log_hicp'] = np.log(df['hicp'])
    df['log_hicp_ct'] = np.log(df['hicp_ct'])
    df['tax_wedge'] = df['log_hicp'] - df['log_hicp_ct']
    
    # Calculate Monthly Change in Wedge (Delta TW)
    # We need to group by geo and coicop to shift safely
    df['delta_tw'] = df.groupby(['geo', 'coicop'])['tax_wedge'].diff()
    
    # Define Event Threshold
    THRESHOLD = CONFIG.get("identification", {}).get("event_threshold", 0.01)
    
    # Identify Events
    # Tax Hike: Wedge increases (HICP grows faster than HICP-CT, or drops slower) -> Positive Delta TW
    # Tax Cut: Wedge decreases -> Negative Delta TW
    
    events = df[np.abs(df['delta_tw']) > THRESHOLD].copy()
    
    conditions = [
        events['delta_tw'] > THRESHOLD,
        events['delta_tw'] < -THRESHOLD
    ]
    choices = ['hike', 'cut']
    events['event_type'] = np.select(conditions, choices, default='none')
    
    # --- Clean Window Logic ---
    print("Applying Clean Window Logic...")
    window_months = CONFIG.get("identification", {}).get("clean_window_months", 12)
    events = apply_clean_window(events, window_months=window_months)
    
    print(f"Total events: {len(events)}")
    print(f"Clean events (isolated +/- {window_months}m): {events['is_clean'].sum()}")
    print(events['event_type'].value_counts())
    
    # Save panel with wedge
    df.to_parquet(os.path.join(PROCESSED_DIR, "panel_with_wedge.parquet"), index=False)
    
    # Save events list
    events_list = events[['geo', 'coicop', 'time', 'event_type', 'delta_tw', 'is_clean']]
    events_list.to_parquet(os.path.join(PROCESSED_DIR, "events_list.parquet"), index=False)
    print("Saved events list and panel.")

    if not os.path.exists(METADATA_DIR):
        os.makedirs(METADATA_DIR)
    summary_path = os.path.join(METADATA_DIR, "events_summary.json")
    with open(summary_path, "w") as f:
        json.dump({
            "event_threshold": THRESHOLD,
            "clean_window_months": window_months,
            "total_events": int(len(events)),
            "clean_events": int(events['is_clean'].sum())
        }, f, indent=2)

if __name__ == "__main__":
    main()
