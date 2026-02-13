import pandas as pd
import numpy as np
import os
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
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

# --- Helper Functions (Copied for Self-Containment) ---

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
        print("Error: Data files not found in data/processed/")
        return pd.DataFrame(), pd.DataFrame()

    df['time'] = pd.to_datetime(df['time'])
    if 'time' in events.columns:
        events['time'] = pd.to_datetime(events['time'])
    
    clean_events = filter_clean_events(events, window_months=6)
    # Subsample if too many (consistency with main results)
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

def run_regression_base(data, formula, cluster_col='geo'):
    if data.empty: return None
    # Quick dropna based on formula vars
    # Heuristic: just drop if outcome or shock is missing
    data_clean = data.dropna(subset=['norm_log_hicp', 'shock_size'])
    mod = smf.ols(formula, data=data_clean)
    res = mod.fit(cov_type='cluster', cov_kwds={'groups': data_clean[cluster_col]})
    return res

# --- Benzarti Specific Logic ---

def identify_sector(coicop):
    # Proxy for Benzarti sample: Services
    # Benzarti et al. (2020) focus heavily on Restaurants, Hairdressers, etc.
    # CP07: Transport Services
    # CP11: Restaurants & Hotels
    # CP12: Misc (Hairdressing is here)
    if coicop.startswith('CP07') or coicop.startswith('CP11') or coicop.startswith('CP12'):
        return 'Services'
    # Proxy for Goods (High Competition / Standard)
    # CP01: Food
    # CP05: Furnishings
    # GD: Industrial Goods
    if coicop.startswith('CP01') or coicop.startswith('CP05') or coicop == 'GD' or coicop == 'IGD':
        return 'Goods'
    return 'Other'

def analyze_asymmetry(df, label):
    print(f"Running Asymmetry Analysis for: {label}")
    # Define Hikes vs Cuts
    df['is_hike'] = (df['shock_size'] > 0).astype(int)
    df['pos_shock'] = df['shock_size'] * df['is_hike']
    df['neg_shock'] = df['shock_size'] * (1 - df['is_hike'])
    
    # Regression: Allow different coefficients for Hike and Cut at each horizon
    # formula = "norm_log_hicp ~ C(rel_time):pos_shock + C(rel_time):neg_shock + C(rel_time) - 1"
    # We include C(rel_time) fixed effects to control for average path
    formula = "norm_log_hicp ~ C(rel_time):pos_shock + C(rel_time):neg_shock + C(rel_time) - 1"
    
    res = run_regression_base(df, formula)
    if res is None: return None
    
    # Extract results for t=0, 6, 12, 24
    results = []
    for t in [0, 6, 12, 24]:
        # Construct parameter names
        # Statsmodels naming can vary (T.t or just t)
        def get_param(var, time):
            names = [f"C(rel_time)[T.{time}]:{var}", f"C(rel_time)[{time}]:{var}", 
                     f"{var}:C(rel_time)[T.{time}]", f"{var}:C(rel_time)[{time}]"]
            for n in names:
                if n in res.params: return n
            return None

        p_hike = get_param('pos_shock', t)
        p_cut = get_param('neg_shock', t)
        
        if p_hike and p_cut:
            coef_hike = res.params[p_hike]
            coef_cut = res.params[p_cut]
            
            # Test Difference
            hyp = f"{p_hike} = {p_cut}"
            wald = res.t_test(hyp)
            diff = coef_hike - coef_cut
            pval = wald.pvalue
            
            results.append({
                'Sample': label,
                'Time': t,
                'Hike': coef_hike,
                'Cut': coef_cut,
                'Diff': diff,
                'P-val': float(pval),
                'Obs': int(res.nobs)
            })
            
    return pd.DataFrame(results)

def main():
    print("--- Starting Benzarti Benchmark Analysis ---")
    
    # 1. Load Data
    df, events = load_and_prep_data()
    if df.empty: return

    # 2. Stack Data
    stacked_df = create_stacked_dataset(df, events, half_window=24) # Use 24 months to match Benzarti long horizons
    if stacked_df.empty: return
    
    # 3. Define Sectors
    stacked_df['sector'] = stacked_df['coicop'].apply(identify_sector)
    
    # 4. Run Analysis by Sector
    results = []
    
    # Services (Benzarti Proxy)
    df_serv = stacked_df[stacked_df['sector'] == 'Services'].copy()
    if len(df_serv) > 500:
        res_serv = analyze_asymmetry(df_serv, "Services (Benzarti Proxy)")
        if res_serv is not None: results.append(res_serv)
    
    # Goods (Control)
    df_goods = stacked_df[stacked_df['sector'] == 'Goods'].copy()
    if len(df_goods) > 500:
        res_goods = analyze_asymmetry(df_goods, "Goods (Standard)")
        if res_goods is not None: results.append(res_goods)
        
    # All
    res_all = analyze_asymmetry(stacked_df, "Full Sample")
    if res_all is not None: results.append(res_all)
    
    # 5. Output Table
    if not results:
        print("No results generated.")
        return
        
    final_df = pd.concat(results)
    print("\nBenzarti Replication Results:")
    print(final_df)
    
    # Generate LaTeX
    lines = []
    lines.append("\\begin{table}[htbp]")
    lines.append("\\centering")
    lines.append("\\caption{Asymmetry by Sector: Replicating Benzarti et al. (2020)}")
    lines.append("\\label{tab:benzarti_benchmark}")
    lines.append("\\begin{tabular}{lccccc}")
    lines.append("\\toprule")
    lines.append("Sample & Horizon & Hike Pass-through & Cut Pass-through & Difference & p-value \\\\")
    lines.append("\\midrule")
    
    current_sample = ""
    for _, row in final_df.iterrows():
        sample = row['Sample']
        if sample != current_sample:
            lines.append(f"\\multicolumn{{6}}{{l}}{{\\textit{{{sample}}}}} \\\\")
            current_sample = sample
            
        t = row['Time']
        h = row['Hike']
        c = row['Cut']
        d = row['Diff']
        p = row['P-val']
        
        stars = ""
        if p < 0.01: stars = "***"
        elif p < 0.05: stars = "**"
        elif p < 0.1: stars = "*"
        
        lines.append(f"t={t} & {h:.3f} & {c:.3f} & {d:.3f} & {p:.3f}{stars} \\\\")
        
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\begin{minipage}{0.9\\textwidth}")
    lines.append("\\footnotesize \\textit{Notes:} Dependent variable is cumulative price change. Difference = Hike - Cut. Services include Restaurants, Transport, etc. Goods include Food and Industrial Goods.")
    lines.append("\\end{minipage}")
    lines.append("\\end{table}")
    
    with open(os.path.join(TABLES_DIR, "benchmark_benzarti.tex"), "w") as f:
        f.write("\n".join(lines))
    print(f"Saved table to {os.path.join(TABLES_DIR, 'benchmark_benzarti.tex')}")

if __name__ == "__main__":
    main()
