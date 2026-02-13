import pandas as pd
import numpy as np
import os
import statsmodels.formula.api as smf
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Paths
PROCESSED_DIR = "data/processed"
OUTPUT_DIR = "output"
TABLES_DIR = os.path.join(OUTPUT_DIR, "tables")
FIGURES_DIR = os.path.join(OUTPUT_DIR, "figures")

os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# --- Helper Functions ---

def filter_clean_events(events, window_months=6):
    if not np.issubdtype(events['time'].dtype, np.datetime64):
        events['time'] = pd.to_datetime(events['time'])
    all_shocks = events[np.abs(events['delta_tw']) > 0.01].copy()
    clean_indices = []
    for geo, group in all_shocks.groupby('geo'):
        unique_dates = np.sort(group['time'].unique())
        valid_dates = set()
        for t in unique_dates:
            is_clean = True
            ts = pd.Timestamp(t)
            for t_other in unique_dates:
                if t == t_other: continue
                ts_o = pd.Timestamp(t_other)
                diff = abs((ts.year - ts_o.year)*12 + (ts.month - ts_o.month))
                if diff <= window_months:
                    is_clean = False
                    break
            if is_clean:
                valid_dates.add(t)
        if valid_dates:
            clean_indices.extend(group[group['time'].isin(valid_dates)].index.tolist())
    filtered = all_shocks.loc[clean_indices].copy()
    return filtered

def load_and_prep_data():
    print("Loading data...")
    try:
        df = pd.read_parquet(os.path.join(PROCESSED_DIR, "panel_with_wedge.parquet"))
        events = pd.read_parquet(os.path.join(PROCESSED_DIR, "events_list.parquet"))
    except FileNotFoundError:
        print("Error: Data files not found.")
        return pd.DataFrame(), pd.DataFrame()

    df['time'] = pd.to_datetime(df['time'])
    if 'time' in events.columns:
        events['time'] = pd.to_datetime(events['time'])
    
    clean_events = filter_clean_events(events, window_months=6)
    if len(clean_events) > 5000:
        clean_events = clean_events.reindex(clean_events.delta_tw.abs().sort_values(ascending=False).index).head(5000)
    
    return df, clean_events

def create_stacked_dataset(df, events, half_window=12):
    print(f"Creating stacked dataset (window +/- {half_window})...")
    df_indexed = df.set_index(['geo', 'coicop', 'time'])
    datasets = []
    event_list = events.to_dict('records')
    
    for i, row in enumerate(event_list):
        geo = row['geo']
        coicop = row['coicop']
        event_time = row['time']
        shock_size = row['delta_tw']
        
        try:
            subset = df_indexed.loc[(geo, coicop)].reset_index()
        except KeyError:
            continue
            
        event_indices = subset.index[subset['time'] == event_time]
        if len(event_indices) == 0: continue
        event_idx = event_indices[0]
        
        subset['rel_time'] = subset.index - event_idx
        window = subset[(subset['rel_time'] >= -half_window) & (subset['rel_time'] <= half_window)].copy()
        
        base_row = window[window['rel_time'] == -1]
        if base_row.empty: continue
        base_log_hicp = base_row['log_hicp'].values[0]
        
        window['norm_log_hicp'] = (window['log_hicp'] - base_log_hicp) * 100
        window['event_id'] = i
        window['shock_size'] = shock_size * 100
        window['geo'] = geo
        window['coicop'] = coicop
        datasets.append(window)
        
    if not datasets: return pd.DataFrame()
    return pd.concat(datasets, ignore_index=True)

# --- Mechanism Testing Logic ---

def get_core_dummy(coicop):
    # Core Inflation usually excludes:
    # - Energy (CP045)
    # - Unprocessed Food (Part of CP01)
    # Since we might not have perfect granularity, we can approximate.
    # Non-Core: Food (CP01) and Energy (CP045)
    if coicop.startswith('CP01') or coicop.startswith('CP045'):
        return 0 # Non-Core
    return 1 # Core

def get_nondurable_dummy(coicop):
    # Non-Durable: Food, Energy, Services (consumed immediately)
    # Durable: Furniture, Appliances, Cars
    # Semi-Durable: Clothing
    
    # Approximation:
    # CP01 (Food): Non-Durable
    # CP03 (Clothing): Semi-Durable
    # CP04 (Housing/Energy): Mixed, Energy is Non-Durable
    # CP05 (Furniture): Durable
    # CP06 (Health): Service/Non-Durable
    # CP07 (Transport): Cars (Durable), Fuel (Non-Durable), Services
    
    # Simplification for this test:
    if coicop.startswith('CP05') or coicop.startswith('CP08') or coicop.startswith('CP09'):
        return 0 # Durable/Semi
    if coicop.startswith('CP01') or coicop.startswith('CP045') or coicop.startswith('CP072'):
        return 1 # Non-Durable
        
    return 0 # Default to 0 if unsure, or exclude

def run_mechanism_regression(stacked_df, dummy_col, label):
    print(f"Running Mechanism Test: {label}")
    
    # Interaction: Shock * Dummy
    # We want to estimate: norm_log_hicp ~ C(rel_time)*shock_size + C(rel_time)*shock_size*dummy
    
    # Create explicit interaction terms for clearer formula
    # We must drop NaNs first to ensure groups align with regression data
    cols_to_use = ['norm_log_hicp', 'rel_time', 'shock_size', dummy_col, 'geo']
    df_clean = stacked_df.dropna(subset=cols_to_use).copy()
    
    df_clean['shock_x_dummy'] = df_clean['shock_size'] * df_clean[dummy_col]
    
    # Formula:
    # Baseline path (no shock): C(rel_time)
    # Baseline pass-through (dummy=0): C(rel_time):shock_size
    # Additional pass-through (dummy=1): C(rel_time):shock_x_dummy
    # Note: We should also control for Dummy main effect if it varies by time, 
    # but here Dummy is time-invariant per event (sector characteristic).
    # However, we should interact dummy with time fixed effects to allow different trend: C(rel_time):dummy
    
    formula = "norm_log_hicp ~ C(rel_time) + C(rel_time):shock_size + C(rel_time):shock_x_dummy + C(rel_time):" + dummy_col + " - 1"
    
    # Simplify for robustness/speed if needed, but full interaction is best.
    
    res = smf.ols(formula, data=df_clean).fit(cov_type='cluster', cov_kwds={'groups': df_clean['geo']})
    
    # Extract coefficients for t=0, 6, 12
    results = []
    for t in [0, 6, 12]:
        # Param names
        def get_name(term, time):
            candidates = [
                f"C(rel_time)[T.{time}]:{term}", f"C(rel_time)[{time}]:{term}",
                f"{term}:C(rel_time)[T.{time}]", f"{term}:C(rel_time)[{time}]"
            ]
            for n in candidates:
                if n in res.params: return n
            return None
            
        base_shock_name = get_name('shock_size', t)
        inter_shock_name = get_name('shock_x_dummy', t)
        
        if base_shock_name and inter_shock_name:
            base_coef = res.params[base_shock_name]
            inter_coef = res.params[inter_shock_name]
            p_val = res.pvalues[inter_shock_name]
            se = res.bse[inter_shock_name]
            
            results.append({
                'Mechanism': label,
                'Time': t,
                'Base_PassThrough': base_coef,
                'Interaction_Coef': inter_coef, # This is the difference
                'SE': se,
                'P-val': p_val
            })
            
    return pd.DataFrame(results)

def main():
    print("--- Starting Mechanism Testing ---")
    
    # 1. Load
    df, events = load_and_prep_data()
    if df.empty: return
    
    # 2. Stack
    stacked_df = create_stacked_dataset(df, events, half_window=12)
    if stacked_df.empty: return
    
    # 3. Define Dummies
    stacked_df['is_core'] = stacked_df['coicop'].apply(get_core_dummy)
    stacked_df['is_nondurable'] = stacked_df['coicop'].apply(get_nondurable_dummy)
    
    all_results = []
    
    # 4. Run Regressions
    # Test 1: Core vs Non-Core
    res_core = run_mechanism_regression(stacked_df, 'is_core', 'Core Inflation (Dummy=1)')
    if not res_core.empty: all_results.append(res_core)
    
    # Test 2: Non-Durable vs Durable
    res_dur = run_mechanism_regression(stacked_df, 'is_nondurable', 'Non-Durable (Dummy=1)')
    if not res_dur.empty: all_results.append(res_dur)
    
    # 5. Output
    if not all_results:
        print("No results.")
        return
        
    final_df = pd.concat(all_results)
    print("\nMechanism Results:")
    print(final_df)
    
    # Latex
    lines = []
    lines.append("\\begin{table}[htbp]")
    lines.append("\\centering")
    lines.append("\\caption{Mechanism Testing: Heterogeneity by Product Characteristics}")
    lines.append("\\label{tab:mechanism}")
    lines.append("\\begin{tabular}{lccccc}")
    lines.append("\\toprule")
    lines.append("Mechanism & Time & Base PT & Interaction (Diff) & SE & p-value \\\\")
    lines.append("\\midrule")
    
    current_mech = ""
    for _, row in final_df.iterrows():
        mech = row['Mechanism']
        if mech != current_mech:
            lines.append(f"\\multicolumn{{6}}{{l}}{{\\textbf{{{mech}}}}} \\\\")
            current_mech = mech
            
        t = row['Time']
        base = row['Base_PassThrough']
        diff = row['Interaction_Coef']
        se = row['SE']
        p = row['P-val']
        
        stars = ""
        if p < 0.01: stars = "***"
        elif p < 0.05: stars = "**"
        elif p < 0.1: stars = "*"
        
        lines.append(f"t={t} & {base:.3f} & {diff:.3f}{stars} & ({se:.3f}) & {p:.3f} \\\\")
        
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")
    
    with open(os.path.join(TABLES_DIR, "heterogeneity_mechanism.tex"), "w") as f:
        f.write("\n".join(lines))
    print(f"Saved table to {os.path.join(TABLES_DIR, 'heterogeneity_mechanism.tex')}")

if __name__ == "__main__":
    main()
