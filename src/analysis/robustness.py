import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analysis.models import (
    load_and_prep_data,
    build_stacked_with_controls,
    run_regression_base,
    extract_coefficients,
    CONFIG,
)

OUTPUT_DIR = "output"
FIGURES_DIR = os.path.join(OUTPUT_DIR, "figures")
TABLES_DIR = os.path.join(OUTPUT_DIR, "tables")

os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(TABLES_DIR, exist_ok=True)

def _randomize_event_times(events, coicop_time_map, rng):
    placebo = events.copy()
    new_times = []
    for _, row in placebo.iterrows():
        options = coicop_time_map.get(row['coicop'], [])
        if len(options) == 0:
            new_times.append(row['time'])
        else:
            new_times.append(rng.choice(options))
    placebo['time'] = new_times
    return placebo

def run_placebo(seed=1, n_sim=1000, sample_events=200):
    try:
        df, events = load_and_prep_data()
    except Exception as e:
        return {"pvals": [], "n_sim": 0, "seed": seed, "error": str(e)}
    if events.empty:
        return {"pvals": [], "n_sim": 0, "seed": seed}

    rng = np.random.default_rng(seed)

    if sample_events and len(events) > sample_events:
        events = events.sample(sample_events, random_state=seed)

    coicop_time_map = (
        df[['coicop', 'time']]
        .dropna()
        .groupby('coicop')['time']
        .unique()
        .to_dict()
    )

    half_window = CONFIG.get("analysis", {}).get("event_window", 12)
    weights_col = CONFIG.get("analysis", {}).get("weight_column", None)

    formula_main = "norm_log_hicp ~ C(rel_time):treat_shock + C(rel_time) + C(cal_time) + C(event_id) - 1"

    pvals = []
    coefs = []
    for i in range(n_sim):
        placebo_events = _randomize_event_times(events, coicop_time_map, rng)
        stacked = build_stacked_with_controls(df, placebo_events, half_window=half_window)
        if stacked.empty:
            continue
        res = run_regression_base(stacked, formula_main, cluster_col='geo', weights_col=weights_col)
        coeffs = extract_coefficients(res, interaction_var='treat_shock', half_window=half_window)
        t0 = coeffs[coeffs['rel_time'] == 0]
        if not t0.empty:
            pvals.append(float(t0['pval'].values[0]))
            coefs.append(float(t0['coef'].values[0]))

    summary = pd.DataFrame({
        "pval": pvals,
        "coef_t0": coefs,
    })
    summary_path = os.path.join(TABLES_DIR, "placebo_summary.csv")
    summary.to_csv(summary_path, index=False)

    valid_pvals = [p for p in pvals if np.isfinite(p)]

    if len(valid_pvals) > 0:
        plt.figure(figsize=(8, 4))
        plt.hist(valid_pvals, bins=20, color='steelblue', alpha=0.8)
        plt.axvline(0.05, color='red', linestyle='--', linewidth=1)
        plt.title("Placebo p-value distribution (t=0)")
        plt.xlabel("p-value")
        plt.ylabel("count")
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "placebo_distribution.png"), dpi=300)
        plt.close()

    return {"pvals": pvals, "n_sim": len(pvals), "seed": seed}

if __name__ == "__main__":
    run_placebo()
