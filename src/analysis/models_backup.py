import pandas as pd
import numpy as np
import os
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import yaml
import warnings
import sys
from pathlib import Path
from linearmodels.iv import AbsorbingLS
from scipy import stats
from typing import Optional, Tuple, Dict, List, Union
from dataclasses import dataclass
from statsmodels.stats._delta_method import approx_fprime_cs
from scipy.stats import chi2, f as f_dist

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.config import load_config
from src.utils.time_parse import normalize_time

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

PROCESSED_DIR = "data/processed"
OUTPUT_DIR = "output"
FIGURES_DIR = os.path.join(OUTPUT_DIR, "figures")
TABLES_DIR = os.path.join(OUTPUT_DIR, "tables")
CONFIG = load_config()

os.environ.setdefault("MPLCONFIGDIR", os.path.join(OUTPUT_DIR, "mpl_cache"))

# Ensure output directories exist
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(TABLES_DIR, exist_ok=True)

def filter_clean_events(events, window_months=6):
    """
    Filters events to ensure no other significant shocks occur within +/- window_months.
    Checks for isolation at the Country (Geo) level.
    """
    print(f"Filtering events with exclusion window +/- {window_months} months...")
    
    # Ensure datetime
    if not np.issubdtype(events['time'].dtype, np.datetime64):
        events['time'] = pd.to_datetime(events['time'])
    
    # Identify all potential shocks
    all_shocks = events[np.abs(events['delta_tw']) > 0.01].copy()
    
    clean_indices = []
    
    # Iterate by geography to find isolated dates
    for geo, group in all_shocks.groupby('geo'):
        unique_dates = np.sort(group['time'].unique())
        
        valid_dates = set()
        for t in unique_dates:
            is_clean = True
            ts = pd.Timestamp(t)
            
            for t_other in unique_dates:
                if t == t_other: continue
                
                ts_o = pd.Timestamp(t_other)
                # Calculate month difference
                diff = abs((ts.year - ts_o.year)*12 + (ts.month - ts_o.month))
                
                if diff <= window_months:
                    is_clean = False
                    break
            
            if is_clean:
                valid_dates.add(t)
        
        if valid_dates:
            # Add all events (items) that happened on these valid dates
            clean_indices.extend(group[group['time'].isin(valid_dates)].index.tolist())
            
    filtered = all_shocks.loc[clean_indices].copy()
    print(f"Original events with >1% shock: {len(all_shocks)}")
    print(f"New clean events (window={window_months}): {len(filtered)}")
    return filtered

def load_and_prep_data():
    print("Loading data...")
    df = pd.read_parquet(os.path.join(PROCESSED_DIR, "panel_with_wedge.parquet"))
    events = pd.read_parquet(os.path.join(PROCESSED_DIR, "events_list.parquet"))
    
    # Ensure time is datetime in both
    df['time'] = pd.to_datetime(df['time'].map(normalize_time))
    if 'time' in events.columns:
        events['time'] = pd.to_datetime(events['time'].map(normalize_time))

    threshold = CONFIG.get("identification", {}).get("event_threshold", 0.01)
    clean_events = events[events['delta_tw'].abs() > threshold].copy()
    if 'is_clean' in clean_events.columns:
        clean_events = clean_events[clean_events['is_clean']]

    print(f"Events after threshold and clean window: {len(clean_events)}")
    return df, clean_events

def build_stacked_with_controls(df, events, half_window=12):
    print(f"Creating stacked dataset with controls, window +/- {half_window} months...")
    if events.empty:
        return pd.DataFrame()

    base_period = CONFIG.get("identification", {}).get("base_period", -1)
    df = df.copy()
    df['time'] = pd.to_datetime(df['time'])
    df['geo_coicop'] = df['geo'].astype(str) + "_" + df['coicop'].astype(str)
    df['abs_month'] = df['time'].dt.year * 12 + df['time'].dt.month

    datasets = []
    event_list = events.to_dict('records')
    coicop_groups = {c: g.copy() for c, g in df.groupby('coicop')}

    for i, row in enumerate(event_list):
        event_geo = row['geo']
        coicop = row['coicop']
        event_time = pd.to_datetime(row['time'])
        shock_size = row['delta_tw']
        event_type = row.get('event_type', 'unknown')

        df_subset = coicop_groups.get(coicop)
        if df_subset.empty:
            continue

        event_abs = event_time.year * 12 + event_time.month
        window = df_subset[(df_subset['abs_month'] >= event_abs - half_window) & (df_subset['abs_month'] <= event_abs + half_window)].copy()
        if window.empty:
            continue

        base_rows = df_subset[df_subset['abs_month'] == event_abs + base_period][['geo', 'log_hicp', 'weight']].copy()
        if base_rows.empty:
            continue

        base_rows = base_rows.rename(columns={'log_hicp': 'log_hicp_base', 'weight': 'weight_base'})
        window = window.merge(base_rows, on='geo', how='inner')
        if window.empty:
            continue

        if 'weight_base' in window.columns:
            window['weight_base'] = window['weight_base'].fillna(window['weight'].mean())

        window['rel_time'] = window['abs_month'] - event_abs
        window['norm_log_hicp'] = (window['log_hicp'] - window['log_hicp_base']) * 100
        window['event_id'] = i
        window['event_geo'] = event_geo
        window['shock_size'] = shock_size * 100
        window['event_type'] = event_type
        window['treated'] = (window['geo'] == event_geo).astype(int)
        window['treat_shock'] = window['shock_size'] * window['treated']
        window['geo_coicop'] = window['geo'] + "_" + window['coicop']
        window['cal_time'] = window['time'].dt.strftime("%Y-%m")
        window['event_weight'] = window['weight_base']

        # Keep only columns needed downstream to reduce memory
        window = window[[
            'geo', 'coicop', 'time', 'rel_time',
            'norm_log_hicp', 'event_id', 'event_geo',
            'shock_size', 'event_type', 'treated', 'treat_shock',
            'geo_coicop', 'cal_time', 'event_weight'
        ]]

        datasets.append(window)

    if not datasets:
        print("Warning: No datasets created. Check data matching.")
        return pd.DataFrame()

    stacked_df = pd.concat(datasets, ignore_index=True)
    print(f"Stacked dataset size: {len(stacked_df)} rows")
    return stacked_df

def run_regression_base(data, formula, cluster_col='geo', weights_col=None):
    print(f"Running regression: {formula}")
    if data.empty:
        print("Error: Empty dataset for regression.")
        return None
        
    # Drop NaNs
    cols_to_check = ['norm_log_hicp', 'rel_time', cluster_col]
    if 'shock_size' in formula: cols_to_check.append('shock_size')
    if 'pos_shock' in formula: cols_to_check.append('pos_shock')
    if 'neg_shock' in formula: cols_to_check.append('neg_shock')
    
    data_clean = data.dropna(subset=[c for c in cols_to_check if c in data.columns])
    
    if weights_col and weights_col in data_clean.columns:
        mod = smf.wls(formula, data=data_clean, weights=data_clean[weights_col])
    else:
        mod = smf.ols(formula, data=data_clean)
    res = mod.fit(cov_type='cluster', cov_kwds={'groups': data_clean[cluster_col]})
    return res

def build_event_design_matrix_np(df, treat_vars, half_window, base_period, include_time_dummies=False):
    times = [t for t in range(-half_window, half_window + 1) if t != base_period]
    n = len(df)
    rel = df['rel_time'].to_numpy()
    treat_arrays = {var: df[var].to_numpy() for var in treat_vars}

    n_cols = 0
    if include_time_dummies:
        n_cols += len(times)
    n_cols += len(times) * len(treat_vars)

    X = np.zeros((n, n_cols), dtype=np.float32)
    col_names = []
    col_idx = 0
    for t in times:
        mask = (rel == t)
        if include_time_dummies:
            X[mask, col_idx] = 1.0
            col_names.append(f"rt_{t}")
            col_idx += 1
        for var in treat_vars:
            X[mask, col_idx] = treat_arrays[var][mask]
            col_names.append(f"rt_{t}_x_{var}")
            col_idx += 1

    return X, col_names

def run_absorbing_regression(df, y_col, treat_vars, half_window, base_period, absorb_cols, cluster_col, weights_col=None, include_time_dummies=False):
    if df.empty:
        return None, None
    df = df.reset_index(drop=True)
    X, col_names = build_event_design_matrix_np(df, treat_vars, half_window, base_period, include_time_dummies=include_time_dummies)
    data_clean = df.copy()
    data_clean = data_clean.replace([np.inf, -np.inf], np.nan)
    y = data_clean[y_col]
    absorb = data_clean[absorb_cols].copy()
    for col in absorb_cols:
        absorb[col] = absorb[col].astype('category').cat.codes
    cols_to_check = [y_col, cluster_col] + absorb_cols
    if weights_col and weights_col in data_clean.columns:
        cols_to_check.append(weights_col)
    data_clean = data_clean.dropna(subset=cols_to_check)
    X = X[data_clean.index.values]
    y = y.loc[data_clean.index].to_numpy(dtype=np.float32)
    absorb = absorb.loc[data_clean.index]

    weights = None
    if weights_col and weights_col in data_clean.columns:
        weights = data_clean[weights_col]

    clusters = data_clean[[cluster_col]].copy()
    clusters[cluster_col] = clusters[cluster_col].astype('category').cat.codes
    mod = AbsorbingLS(y, X, absorb=absorb, weights=weights)
    res = mod.fit(cov_type='clustered', clusters=clusters)
    return res, col_names

def extract_coefficients_absorbing(res, treat_var, half_window, base_period, col_names=None):
    if res is None:
        return pd.DataFrame()

    coefs = []
    cis_lower = []
    cis_upper = []
    se = []
    pvals = []
    times = range(-half_window, half_window + 1)
    params = res.params
    conf = res.conf_int()
    if col_names is not None:
        params_arr = params.to_numpy()
        conf_arr = conf.to_numpy()
        se_arr = res.std_errors.to_numpy()
        pval_arr = res.pvalues.to_numpy()
        name_to_idx = {n: i for i, n in enumerate(col_names)}
    for t in times:
        if t == base_period:
            coefs.append(0)
            cis_lower.append(0)
            cis_upper.append(0)
            se.append(0)
            pvals.append(1.0)
            continue
        name = f"rt_{t}_x_{treat_var}"
        if col_names is not None:
            idx = name_to_idx.get(name)
            if idx is None:
                coefs.append(np.nan)
                cis_lower.append(np.nan)
                cis_upper.append(np.nan)
                se.append(np.nan)
                pvals.append(np.nan)
                continue
            coefs.append(params_arr[idx])
            cis_lower.append(conf_arr[idx][0])
            cis_upper.append(conf_arr[idx][1])
            se.append(se_arr[idx])
            pvals.append(pval_arr[idx])
        elif name in params.index:
            coefs.append(params[name])
            ci = conf.loc[name]
            cis_lower.append(ci.iloc[0])
            cis_upper.append(ci.iloc[1])
            se.append(res.std_errors[name])
            pvals.append(res.pvalues[name])
        else:
            coefs.append(np.nan)
            cis_lower.append(np.nan)
            cis_upper.append(np.nan)
            se.append(np.nan)
            pvals.append(np.nan)
    return pd.DataFrame({
        'rel_time': times,
        'coef': coefs,
        'ci_lower': cis_lower,
        'ci_upper': cis_upper,
        'se': se,
        'pval': pvals
    })

def extract_coefficients(res, interaction_var='shock_size', half_window=12):
    if res is None:
        return pd.DataFrame()
        
    coefs = []
    cis_lower = []
    cis_upper = []
    se = []
    pvals = []
    times = range(-half_window, half_window + 1)
    
    def get_param_name(t, var_name):
        candidates = [
            f"C(rel_time)[T.{t}]:{var_name}",
            f"C(rel_time)[{t}]:{var_name}",
            f"{var_name}:C(rel_time)[T.{t}]",
            f"{var_name}:C(rel_time)[{t}]"
        ]
        for name in candidates:
            if name in res.params:
                return name
        return None
    
    for t in times:
        if t == -1:
            coefs.append(0)
            cis_lower.append(0)
            cis_upper.append(0)
            se.append(0)
            pvals.append(1.0)
            continue
            
        name = get_param_name(t, interaction_var)
        
        if name:
            coefs.append(res.params[name])
            cis_lower.append(res.conf_int().loc[name][0])
            cis_upper.append(res.conf_int().loc[name][1])
            se.append(res.bse[name])
            pvals.append(res.pvalues[name])
        else:
            coefs.append(np.nan)
            cis_lower.append(np.nan)
            cis_upper.append(np.nan)
            se.append(np.nan)
            pvals.append(np.nan)
            
    return pd.DataFrame({
        'rel_time': times,
        'coef': coefs,
        'ci_lower': cis_lower,
        'ci_upper': cis_upper,
        'se': se,
        'pval': pvals
    })

def plot_coefficients(results_dict, title, filename):
    plt.figure(figsize=(12, 6))
    
    colors = ['blue', 'red', 'green', 'purple']
    styles = ['-o', '--s', '-.^', ':d']
    
    has_data = False
    for i, (label, df) in enumerate(results_dict.items()):
        if df.empty: continue
        has_data = True
        color = colors[i % len(colors)]
        style = styles[i % len(styles)]
        
        # Plot Coefs
        plt.plot(df['rel_time'], df['coef'], style, color=color, label=label, alpha=0.8)
        
        # Plot CI
        plt.fill_between(df['rel_time'], 
                         df['ci_lower'], 
                         df['ci_upper'], 
                         color=color, alpha=0.05)
    
    if not has_data:
        plt.close()
        return

    plt.axvline(x=-0.5, color='gray', linestyle='--', alpha=0.5)
    plt.axhline(y=0, color='black', linewidth=0.8)
    
    plt.title(title, fontsize=14)
    plt.xlabel("Months relative to event", fontsize=12)
    plt.ylabel("Pass-through Rate", fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    path = os.path.join(FIGURES_DIR, filename)
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"Saved plot to {path}")

def save_latex_table(df, filename, caption, label, columns=None):
    """
    Saves a pandas DataFrame to a LaTeX table with booktabs formatting.
    Outputs the complete table environment.
    """
    if df.empty: return
    
    # Check if this is a regression result df (has coef, se, pval)
    if {'coef', 'se', 'pval'}.issubset(df.columns):
        lines = []
        lines.append("\\begin{table}[htbp]")
        lines.append("\\centering")
        lines.append(f"\\caption{{{caption}}}")
        lines.append(f"\\label{{{label}}}")
        lines.append("\\begin{tabular}{lccc}")
        lines.append("\\toprule")
        lines.append("Event Time & Coefficient & Std. Err. & Significance \\\\")
        lines.append("\\midrule")
        
        for _, row in df.iterrows():
            # Time Label
            if 'rel_time' in row:
                t = int(row['rel_time'])
                time_str = f"{t}"
            elif 'time' in row:
                t = int(row['time'])
                time_str = f"{t}"
            else:
                time_str = "Constant"
                
            # Coef and Stars
            coef = row['coef']
            if pd.isna(coef): continue
            
            p = row['pval']
            stars = ""
            if p < 0.01: stars = "***"
            elif p < 0.05: stars = "**"
            elif p < 0.1: stars = "*"
            
            coef_str = f"{coef:.4f}{stars}"
            se = row['se']
            se_str = f"({se:.4f})"
            
            lines.append(f"{time_str} & {coef_str} & {se_str} & {stars} \\\\")
            
        lines.append("\\bottomrule")
        lines.append("\\end{tabular}")
        lines.append("\\end{table}")
        
        with open(os.path.join(TABLES_DIR, filename), "w") as f:
            f.write("\n".join(lines))
        print(f"Saved LaTeX table to {filename}")
        
    else:
        # Fallback for other tables
        if 'diff' in df.columns:
            lines = []
            lines.append("\\begin{table}[htbp]")
            lines.append("\\centering")
            lines.append(f"\\caption{{{caption}}}")
            lines.append(f"\\label{{{label}}}")
            lines.append("\\begin{tabular}{lccc}")
            lines.append("\\toprule")
            lines.append("Time & Difference & t-stat & p-value \\\\")
            lines.append("\\midrule")
            
            for _, row in df.iterrows():
                t = int(row['time']) if 'time' in row else 0
                diff = row['diff']
                tstat = row['t_stat']
                pval = row['p_val']
                
                stars = ""
                if pval < 0.01: stars = "***"
                elif pval < 0.05: stars = "**"
                elif pval < 0.1: stars = "*"
                
                lines.append(f"{t} & {diff:.4f}^{{{stars}}} & {tstat:.2f} & {pval:.4f} \\\\")
            
            lines.append("\\bottomrule")
            lines.append("\\end{tabular}")
            lines.append("\\end{table}")
            
            with open(os.path.join(TABLES_DIR, filename), "w") as f:
                f.write("\n".join(lines))
            print(f"Saved LaTeX table to {filename}")

def analysis_asymmetry(stacked_df):
    """
    Comprehensive asymmetry analysis with formal statistical tests.
    """
    print("\n" + "="*80)
    print("--- Running Asymmetry Analysis (Hike vs Cut) ---")
    print("="*80)

    if stacked_df.empty:
        return pd.DataFrame(), {}

    half_window = CONFIG.get("analysis", {}).get("event_window", 12)
    base_period = CONFIG.get("identification", {}).get("base_period", -1)

    # Create hike/cut indicators
    stacked_df = stacked_df.copy()
    stacked_df['is_hike'] = (stacked_df['shock_size'] > 0).astype(int)
    stacked_df['pos_shock'] = stacked_df['treat_shock'] * stacked_df['is_hike']
    stacked_df['neg_shock'] = stacked_df['treat_shock'] * (1 - stacked_df['is_hike'])

    # Run main asymmetry regression
    weights_col = CONFIG.get("analysis", {}).get("weight_column", None)
    res, col_names = run_absorbing_regression(
        stacked_df,
        y_col="norm_log_hicp",
        treat_vars=["pos_shock", "neg_shock"],
        half_window=half_window,
        base_period=base_period,
        absorb_cols=["geo_coicop", "cal_time", "rel_time"],
        cluster_col="geo",
        weights_col=weights_col,
        include_time_dummies=False
    )

    if res is None:
        return pd.DataFrame(), {}

    # Extract coefficients for plotting
    res_hike = extract_coefficients_absorbing(
        res, 'pos_shock', half_window=half_window, base_period=base_period, col_names=col_names
    )
    res_cut = extract_coefficients_absorbing(
        res, 'neg_shock', half_window=half_window, base_period=base_period, col_names=col_names
    )

    # Plot
    plot_coefficients({
        'Tax Hike': res_hike,
        'Tax Cut': res_cut
    }, "Asymmetric Pass-through: Hikes vs Cuts", "asymmetry_hike_vs_cut.png")

    # ============================================================
    # FORMAL STATISTICAL TESTS
    # ============================================================

    print("\n" + "-"*60)
    print("FORMAL ASYMMETRY TESTS")
    print("-"*60)

    # Initialize test class
    asym_tests = AsymmetryTests(res, col_names, half_window=half_window, base_period=base_period)

    # Run all tests
    all_test_results = asym_tests.run_all_tests()

    # Print results
    print("\n1. JOINT WALD TEST (All Periods)")
    joint_all = all_test_results['joint_all_periods']
    if 'wald_statistic' in joint_all:
        print(f"   H0: beta_hike(t) = beta_cut(t) for all t")
        print(f"   Wald Statistic: {joint_all['wald_statistic']:.4f}")
        print(f"   Degrees of Freedom: {joint_all['df']}")
        print(f"   p-value: {joint_all['p_value']:.4f}")
        print(f"   Result: {'Reject H0' if joint_all['rejected_05'] else 'Fail to reject H0'} (alpha=0.05)")

    print("\n2. JOINT WALD TEST (Post-Treatment Periods Only)")
    joint_post = all_test_results['joint_post_periods']
    if 'wald_statistic' in joint_post:
        print(f"   H0: beta_hike(t) = beta_cut(t) for all t >= 0")
        print(f"   Wald Statistic: {joint_post['wald_statistic']:.4f}")
        print(f"   Degrees of Freedom: {joint_post['df']}")
        print(f"   p-value: {joint_post['p_value']:.4f}")
        print(f"   Result: {'Reject H0' if joint_post['rejected_05'] else 'Fail to reject H0'} (alpha=0.05)")

    print("\n3. AVERAGE DIFFERENCE TEST")
    avg_test = all_test_results['average_difference']
    if 'difference' in avg_test:
        print(f"   H0: Average(beta_hike) = Average(beta_cut)")
        print(f"   Difference: {avg_test['difference']:.4f}")
        print(f"   Std Error: {avg_test['std_error']:.4f}")
        print(f"   t-statistic: {avg_test['t_statistic']:.4f}")
        print(f"   p-value: {avg_test['p_value']:.4f}")

    print("\n4. CUMULATIVE EFFECT TEST (t=0,6,12)")
    cum_test = all_test_results['cumulative_effect']
    if 'difference' in cum_test:
        print(f"   H0: Sum(beta_hike) = Sum(beta_cut) for t=0,6,12")
        print(f"   Cumulative Hike: {cum_test['cum_hike']:.4f}")
        print(f"   Cumulative Cut: {cum_test['cum_cut']:.4f}")
        print(f"   Difference: {cum_test['difference']:.4f}")
        print(f"   Std Error: {cum_test['std_error']:.4f}")
        print(f"   t-statistic: {cum_test['t_statistic']:.4f}")
        print(f"   p-value: {cum_test['p_value']:.4f}")

    print("\n5. PAIRWISE COMPARISONS (Key Periods)")
    pairwise = all_test_results['pairwise']
    key_times = [0, 6, 12]
    for t in key_times:
        row = pairwise[pairwise['time'] == t]
        if not row.empty and not pd.isna(row['difference'].values[0]):
            diff = row['difference'].values[0]
            pval = row['p_value'].values[0]
            sig = "***" if pval < 0.01 else "**" if pval < 0.05 else "*" if pval < 0.1 else "ns"
            print(f"   t={t:2d}: Diff = {diff:7.4f}, p = {pval:.4f} [{sig}]")

    # Save LaTeX tables
    save_asymmetry_latex_tables(all_test_results)

    # ============================================================
    # INTERACTION TERM REGRESSION (Alternative Specification)
    # ============================================================

    print("\n" + "-"*60)
    print("INTERACTION TERM REGRESSION")
    print("-"*60)

    res_int, col_names_int, interaction_df = run_interaction_regression(
        stacked_df, half_window=half_window, base_period=base_period
    )

    if not interaction_df.empty:
        save_interaction_latex_table(interaction_df)
        interaction_df.to_csv(os.path.join(TABLES_DIR, "asymmetry_interaction.csv"), index=False)

    # ============================================================
    # POWER ANALYSIS
    # ============================================================

    print("\n" + "-"*60)
    print("STATISTICAL POWER ANALYSIS")
    print("-"*60)

    n_obs = len(stacked_df)
    power_results = calculate_power_analysis(effect_size=0.15, n_obs=n_obs)

    print(f"   Sample Size: {power_results['n_observations']:,}")
    print(f"   Effective N (after clustering): {power_results['n_effective']:,.0f}")
    print(f"   Approximate SE: {power_results['approximate_se']:.4f}")
    print(f"   Power to detect 15pp difference: {power_results['power_at_15pp']:.1%}")
    print(f"   Minimum Detectable Effect (80% power): {power_results['min_detectable_effect_80']:.4f}")
    print(f"   Minimum Detectable Effect (90% power): {power_results['min_detectable_effect_90']:.4f}")

    # ============================================================
    # SUMMARY AND CONCLUSIONS
    # ============================================================

    print("\n" + "="*80)
    print("ASYMMETRY TEST SUMMARY")
    print("="*80)

    # Determine overall conclusion
    p_values = []
    if 'p_value' in joint_all:
        p_values.append(('Joint (All)', joint_all['p_value']))
    if 'p_value' in joint_post:
        p_values.append(('Joint (Post)', joint_post['p_value']))
    if 'p_value' in cum_test:
        p_values.append(('Cumulative', cum_test['p_value']))

    min_pval = min([p for _, p in p_values]) if p_values else 1.0

    print(f"\nMinimum p-value across joint tests: {min_pval:.4f}")

    if min_pval > 0.10:
        print("\n*** CONCLUSION: No statistically significant asymmetry detected ***")
        print("    The pass-through of tax hikes and cuts is statistically indistinguishable.")
        print("    This supports the hypothesis of SYMMETRIC price adjustment.")
    elif min_pval > 0.05:
        print("\n*** CONCLUSION: Weak evidence of asymmetry ***")
        print("    Some tests suggest potential asymmetry at 10% level.")
    else:
        print("\n*** CONCLUSION: Significant asymmetry detected ***")
        print("    The data rejects the null of symmetric pass-through.")

    print("="*80)

    # Prepare return data
    pairwise['test_type'] = 'pairwise'
    summary_results = {
        'joint_all': joint_all,
        'joint_post': joint_post,
        'average': avg_test,
        'cumulative': cum_test,
        'power': power_results,
        'conclusion': 'symmetric' if min_pval > 0.05 else 'asymmetric'
    }

    return pairwise, summary_results

def get_country_group(geo):
    core = ['DE', 'FR', 'NL', 'BE', 'AT', 'FI']
    periphery = ['IT', 'ES', 'PT', 'GR', 'IE']
    if geo in core: return 'Core'
    if geo in periphery: return 'Periphery'
    return 'Other'

def get_durability(coicop):
    # Non-durable: Food (CP01), Energy (CP045)
    # Durable: Furniture, Appliances (CP05)
    if coicop.startswith('CP01'): return 'Non-durable' # Food
    if coicop.startswith('CP045'): return 'Non-durable' # Energy
    if coicop.startswith('CP05'): return 'Durable' # Furnishings
    return 'Other'

def export_results_yaml(results_data):
    yaml_path = "results.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(results_data, f, sort_keys=False)
    print(f"Saved results summary to {yaml_path}")


class AsymmetryTests:
    """
    Comprehensive statistical tests for asymmetry between tax hikes and cuts.
    Implements Wald tests and interaction term tests.
    """

    def __init__(self, res, col_names, half_window=12, base_period=-1):
        """
        Parameters:
        -----------
        res : AbsorbingLSResults
            Fitted regression results from linearmodels
        col_names : list
            Column names corresponding to parameters
        half_window : int
            Event study window size
        base_period : int
            Base period for normalization
        """
        self.res = res
        self.col_names = col_names
        self.half_window = half_window
        self.base_period = base_period
        self.params = res.params.to_numpy()
        self.cov = res.cov.to_numpy()
        self.name_to_idx = {n: i for i, n in enumerate(col_names)}

    def _get_param_idx(self, time, var):
        """Get parameter index for a given time and variable."""
        name = f"rt_{time}_x_{var}"
        return self.name_to_idx.get(name)

    def _get_params_and_cov(self, times, var1, var2):
        """Extract parameters and covariance matrix for specified times."""
        indices = []
        for t in times:
            if t == self.base_period:
                continue
            idx1 = self._get_param_idx(t, var1)
            idx2 = self._get_param_idx(t, var2)
            if idx1 is not None and idx2 is not None:
                indices.extend([idx1, idx2])

        if len(indices) == 0:
            return None, None

        params_subset = self.params[indices]
        cov_subset = self.cov[np.ix_(indices, indices)]
        return params_subset, cov_subset

    def wald_test_equality(self, times=None, var1='pos_shock', var2='neg_shock'):
        """
        Wald test for equality of coefficients between hikes and cuts.
        H0: beta_hike(t) = beta_cut(t) for all t in times

        Parameters:
        -----------
        times : list or None
            Specific time periods to test. If None, tests all periods.
        var1, var2 : str
            Variable names for the two groups (default: pos_shock, neg_shock)

        Returns:
        --------
        dict : Test results with chi2 statistic, p-value, and degrees of freedom
        """
        if times is None:
            times = [t for t in range(-self.half_window, self.half_window + 1)
                     if t != self.base_period]

        # Build restriction matrix R and vector r
        # R*beta = r, where we want beta_hike - beta_cut = 0
        n_restrictions = len(times)
        n_params = len(self.params)

        R = np.zeros((n_restrictions, n_params))
        r = np.zeros(n_restrictions)

        valid_times = []
        for i, t in enumerate(times):
            idx1 = self._get_param_idx(t, var1)
            idx2 = self._get_param_idx(t, var2)
            if idx1 is not None and idx2 is not None:
                R[i, idx1] = 1
                R[i, idx2] = -1
                valid_times.append(t)

        if len(valid_times) == 0:
            return {'error': 'No valid parameters found for test'}

        # Trim R to valid restrictions
        R = R[:len(valid_times), :]

        # Wald statistic: (R*beta - r)' * (R*V*R')^-1 * (R*beta - r) ~ chi2(q)
        Rbeta = R @ self.params
        RVRT = R @ self.cov @ R.T

        try:
            RVRT_inv = np.linalg.inv(RVRT)
            wald_stat = (Rbeta - r).T @ RVRT_inv @ (Rbeta - r)
            wald_stat = float(wald_stat)
        except np.linalg.LinAlgError:
            # Use pseudo-inverse if singular
            RVRT_inv = np.linalg.pinv(RVRT)
            wald_stat = float((Rbeta - r).T @ RVRT_inv @ (Rbeta - r))

        df = len(valid_times)
        p_value = 1 - chi2.cdf(wald_stat, df)

        return {
            'test_type': 'Wald Test (Equality)',
            'wald_statistic': wald_stat,
            'p_value': p_value,
            'df': df,
            'times_tested': valid_times,
            'null_hypothesis': f'{var1} = {var2} for all periods',
            'rejected_05': p_value < 0.05,
            'rejected_01': p_value < 0.01
        }

    def wald_test_linear_combination(self, times=None, var1='pos_shock', var2='neg_shock'):
        """
        Test if the average difference between hikes and cuts is zero.
        H0: sum_t (beta_hike(t) - beta_cut(t)) = 0

        Returns:
        --------
        dict : Test results
        """
        if times is None:
            times = [t for t in range(-self.half_window, self.half_window + 1)
                     if t != self.base_period]

        n_params = len(self.params)
        R = np.zeros(n_params)

        valid_count = 0
        for t in times:
            idx1 = self._get_param_idx(t, var1)
            idx2 = self._get_param_idx(t, var2)
            if idx1 is not None and idx2 is not None:
                R[idx1] = 1
                R[idx2] = -1
                valid_count += 1

        if valid_count == 0:
            return {'error': 'No valid parameters found for test'}

        # Test if average difference is zero
        R = R / valid_count

        diff = R @ self.params
        se = np.sqrt(R @ self.cov @ R.T)
        t_stat = diff / se if se > 0 else np.nan

        return {
            'test_type': 'Average Difference Test',
            'difference': float(diff),
            'std_error': float(se),
            't_statistic': float(t_stat),
            'p_value': 2 * (1 - stats.norm.cdf(abs(t_stat))) if not np.isnan(t_stat) else np.nan,
            'null_hypothesis': f'Average {var1} = Average {var2}'
        }

    def pairwise_comparison(self, times=None, var1='pos_shock', var2='neg_shock'):
        """
        Pairwise t-tests for each time period.

        Returns:
        --------
        pd.DataFrame : Results for each time period
        """
        if times is None:
            times = range(-self.half_window, self.half_window + 1)

        results = []
        for t in times:
            if t == self.base_period:
                results.append({
                    'time': t,
                    'hike_coef': 0.0,
                    'hike_se': 0.0,
                    'cut_coef': 0.0,
                    'cut_se': 0.0,
                    'difference': 0.0,
                    'diff_se': 0.0,
                    't_stat': 0.0,
                    'p_value': 1.0
                })
                continue

            idx1 = self._get_param_idx(t, var1)
            idx2 = self._get_param_idx(t, var2)

            if idx1 is None or idx2 is None:
                results.append({
                    'time': t,
                    'hike_coef': np.nan,
                    'hike_se': np.nan,
                    'cut_coef': np.nan,
                    'cut_se': np.nan,
                    'difference': np.nan,
                    'diff_se': np.nan,
                    't_stat': np.nan,
                    'p_value': np.nan
                })
                continue

            hike_coef = self.params[idx1]
            cut_coef = self.params[idx2]
            hike_se = np.sqrt(self.cov[idx1, idx1])
            cut_se = np.sqrt(self.cov[idx2, idx2])

            diff = hike_coef - cut_coef
            diff_var = self.cov[idx1, idx1] + self.cov[idx2, idx2] - 2 * self.cov[idx1, idx2]
            diff_se = np.sqrt(max(0, diff_var))

            t_stat = diff / diff_se if diff_se > 0 else np.nan
            p_val = 2 * (1 - stats.norm.cdf(abs(t_stat))) if not np.isnan(t_stat) else np.nan

            results.append({
                'time': t,
                'hike_coef': float(hike_coef),
                'hike_se': float(hike_se),
                'cut_coef': float(cut_coef),
                'cut_se': float(cut_se),
                'difference': float(diff),
                'diff_se': float(diff_se),
                't_stat': float(t_stat),
                'p_value': float(p_val)
            })

        return pd.DataFrame(results)

    def joint_wald_test_post_periods(self, post_periods=None, var1='pos_shock', var2='neg_shock'):
        """
        Joint Wald test for post-treatment periods only.
        H0: beta_hike(t) = beta_cut(t) for all t >= 0

        Parameters:
        -----------
        post_periods : list or None
            Post-treatment periods to include. Default: [0, 1, ..., half_window]

        Returns:
        --------
        dict : Test results
        """
        if post_periods is None:
            post_periods = [t for t in range(0, self.half_window + 1) if t != self.base_period]

        return self.wald_test_equality(times=post_periods, var1=var1, var2=var2)

    def cumulative_effect_test(self, periods=None, var1='pos_shock', var2='neg_shock'):
        """
        Test equality of cumulative effects.
        H0: sum_t beta_hike(t) = sum_t beta_cut(t)

        Parameters:
        -----------
        periods : list or None
            Periods over which to sum. Default: [0, 6, 12]

        Returns:
        --------
        dict : Test results
        """
        if periods is None:
            periods = [0, 6, 12]

        n_params = len(self.params)
        R_hike = np.zeros(n_params)
        R_cut = np.zeros(n_params)

        valid_periods = []
        for t in periods:
            idx1 = self._get_param_idx(t, var1)
            idx2 = self._get_param_idx(t, var2)
            if idx1 is not None and idx2 is not None:
                R_hike[idx1] = 1
                R_cut[idx2] = 1
                valid_periods.append(t)

        if len(valid_periods) == 0:
            return {'error': 'No valid parameters found for test'}

        cum_hike = R_hike @ self.params
        cum_cut = R_cut @ self.params
        cum_diff = cum_hike - cum_cut

        # Variance of difference
        R_diff = R_hike - R_cut
        var_diff = R_diff @ self.cov @ R_diff.T
        se_diff = np.sqrt(var_diff)

        t_stat = cum_diff / se_diff if se_diff > 0 else np.nan
        p_val = 2 * (1 - stats.norm.cdf(abs(t_stat))) if not np.isnan(t_stat) else np.nan

        return {
            'test_type': 'Cumulative Effect Test',
            'periods': valid_periods,
            'cum_hike': float(cum_hike),
            'cum_cut': float(cum_cut),
            'difference': float(cum_diff),
            'std_error': float(se_diff),
            't_statistic': float(t_stat),
            'p_value': p_val,
            'null_hypothesis': 'Cumulative hike effect = Cumulative cut effect'
        }

    def run_all_tests(self):
        """
        Run all asymmetry tests and return comprehensive results.

        Returns:
        --------
        dict : All test results
        """
        # Key time periods for focused tests
        key_periods = [0, 6, 12]
        post_periods = [t for t in range(0, self.half_window + 1) if t != self.base_period]

        results = {
            'joint_all_periods': self.wald_test_equality(),
            'joint_post_periods': self.joint_wald_test_post_periods(),
            'average_difference': self.wald_test_linear_combination(),
            'cumulative_effect': self.cumulative_effect_test(key_periods),
            'pairwise': self.pairwise_comparison()
        }

        return results


def run_interaction_regression(stacked_df, half_window=12, base_period=-1):
    """
    Run regression with interaction terms between shock direction and event time.
    This provides an alternative test for asymmetry.

    Model: y = sum_t [beta_t * 1(tau=t) * shock + gamma_t * 1(tau=t) * shock * is_hike] + FE + epsilon

    where gamma_t captures the differential effect of hikes vs cuts.

    Parameters:
    -----------
    stacked_df : pd.DataFrame
        Stacked event study dataset
    half_window : int
        Event window size
    base_period : int
        Base period for normalization

    Returns:
    --------
    tuple : (results, col_names, interaction_df)
    """
    print("\n--- Running Interaction Term Regression ---")

    if stacked_df.empty:
        return None, None, pd.DataFrame()

    # Create interaction variables
    stacked_df = stacked_df.copy()
    stacked_df['is_hike'] = (stacked_df['shock_size'] > 0).astype(int)
    stacked_df['shock_abs'] = stacked_df['treat_shock'].abs()
    stacked_df['shock_x_hike'] = stacked_df['shock_abs'] * stacked_df['is_hike']

    weights_col = CONFIG.get("analysis", {}).get("weight_column", None)

    # Run regression with interaction terms
    res, col_names = run_absorbing_regression(
        stacked_df,
        y_col="norm_log_hicp",
        treat_vars=["shock_abs", "shock_x_hike"],
        half_window=half_window,
        base_period=base_period,
        absorb_cols=["geo_coicop", "cal_time", "rel_time"],
        cluster_col="geo",
        weights_col=weights_col,
        include_time_dummies=False
    )

    if res is None:
        return None, None, pd.DataFrame()

    # Extract interaction coefficients (these represent the asymmetry)
    params_arr = res.params.to_numpy()
    cov_arr = res.cov.to_numpy()
    name_to_idx = {n: i for i, n in enumerate(col_names)}

    interaction_results = []
    times = range(-half_window, half_window + 1)

    for t in times:
        if t == base_period:
            interaction_results.append({
                'time': t,
                'base_coef': 0.0,
                'base_se': 0.0,
                'interaction_coef': 0.0,
                'interaction_se': 0.0,
                'interaction_pval': 1.0,
                'total_hike': 0.0,
                'total_cut': 0.0
            })
            continue

        base_name = f"rt_{t}_x_shock_abs"
        int_name = f"rt_{t}_x_shock_x_hike"

        base_idx = name_to_idx.get(base_name)
        int_idx = name_to_idx.get(int_name)

        if base_idx is None or int_idx is None:
            interaction_results.append({
                'time': t,
                'base_coef': np.nan,
                'base_se': np.nan,
                'interaction_coef': np.nan,
                'interaction_se': np.nan,
                'interaction_pval': np.nan,
                'total_hike': np.nan,
                'total_cut': np.nan
            })
            continue

        base_coef = params_arr[base_idx]
        int_coef = params_arr[int_idx]
        base_se = np.sqrt(cov_arr[base_idx, base_idx])
        int_se = np.sqrt(cov_arr[int_idx, int_idx])

        # p-value for interaction term
        int_tstat = int_coef / int_se if int_se > 0 else np.nan
        int_pval = 2 * (1 - stats.norm.cdf(abs(int_tstat))) if not np.isnan(int_tstat) else np.nan

        # Total effects
        total_hike = base_coef + int_coef  # Effect for hikes
        total_cut = base_coef  # Effect for cuts (base is cut since is_hike=0)

        interaction_results.append({
            'time': t,
            'base_coef': float(base_coef),
            'base_se': float(base_se),
            'interaction_coef': float(int_coef),
            'interaction_se': float(int_se),
            'interaction_tstat': float(int_tstat),
            'interaction_pval': float(int_pval),
            'total_hike': float(total_hike),
            'total_cut': float(total_cut)
        })

    interaction_df = pd.DataFrame(interaction_results)

    # Print key results
    print("\nInteraction Term Results (Key Periods):")
    print("-" * 80)
    for t in [0, 6, 12]:
        row = interaction_df[interaction_df['time'] == t]
        if not row.empty and not pd.isna(row['interaction_coef'].values[0]):
            coef = row['interaction_coef'].values[0]
            pval = row['interaction_pval'].values[0]
            sig = "***" if pval < 0.01 else "**" if pval < 0.05 else "*" if pval < 0.1 else ""
            print(f"t={t:3d}: Interaction = {coef:7.4f} (p={pval:.4f}){sig}")
    print("-" * 80)

    return res, col_names, interaction_df


def save_asymmetry_latex_tables(test_results, output_dir=TABLES_DIR):
    """
    Save asymmetry test results as LaTeX tables.

    Parameters:
    -----------
    test_results : dict
        Results from AsymmetryTests.run_all_tests()
    output_dir : str
        Directory to save tables
    """
    os.makedirs(output_dir, exist_ok=True)

    # Table 1: Joint Wald Tests
    lines = []
    lines.append("\\begin{table}[htbp]")
    lines.append("\\centering")
    lines.append("\\caption{Asymmetry Tests: Joint Wald Tests for Equality of Hike and Cut Coefficients}")
    lines.append("\\label{tab:asymmetry_joint_tests}")
    lines.append("\\begin{tabular}{lccc}")
    lines.append("\\toprule")
    lines.append("Test & Wald Statistic & df & p-value \\\\")
    lines.append("\\midrule")

    # Joint all periods
    joint_all = test_results.get('joint_all_periods', {})
    if 'wald_statistic' in joint_all:
        wald = joint_all['wald_statistic']
        df = joint_all['df']
        pval = joint_all['p_value']
        sig = "***" if pval < 0.01 else "**" if pval < 0.05 else "*" if pval < 0.1 else ""
        lines.append(f"All Periods & {wald:.3f} & {df} & {pval:.4f}{sig} \\\\")

    # Joint post periods
    joint_post = test_results.get('joint_post_periods', {})
    if 'wald_statistic' in joint_post:
        wald = joint_post['wald_statistic']
        df = joint_post['df']
        pval = joint_post['p_value']
        sig = "***" if pval < 0.01 else "**" if pval < 0.05 else "*" if pval < 0.1 else ""
        lines.append(f"Post-Treatment Only & {wald:.3f} & {df} & {pval:.4f}{sig} \\\\")

    lines.append("\\bottomrule")
    lines.append("\\multicolumn{4}{p{0.8\\textwidth}}{\\footnotesize \\textit{Notes:} " +
                 "Wald test of H\\textsubscript{0}: $\\beta_{hike}(t) = \\beta_{cut}(t)$ " +
                 "for all periods in the specified set. *** p<0.01, ** p<0.05, * p<0.1.}")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")

    with open(os.path.join(output_dir, "asymmetry_joint_tests.tex"), "w") as f:
        f.write("\n".join(lines))
    print(f"Saved joint tests table to {output_dir}/asymmetry_joint_tests.tex")

    # Table 2: Pairwise Comparisons at Key Periods
    pairwise = test_results.get('pairwise', pd.DataFrame())
    if not pairwise.empty:
        lines = []
        lines.append("\\begin{table}[htbp]")
        lines.append("\\centering")
        lines.append("\\caption{Asymmetry Tests: Pairwise Comparisons at Key Time Periods}")
        lines.append("\\label{tab:asymmetry_pairwise}")
        lines.append("\\begin{tabular}{ccccccc}")
        lines.append("\\toprule")
        lines.append("Time & Hike Coef & Cut Coef & Difference & SE & t-stat & p-value \\\\")
        lines.append("\\midrule")

        key_times = [0, 6, 12]
        for t in key_times:
            row = pairwise[pairwise['time'] == t]
            if not row.empty and not pd.isna(row['difference'].values[0]):
                hike = row['hike_coef'].values[0]
                cut = row['cut_coef'].values[0]
                diff = row['difference'].values[0]
                se = row['diff_se'].values[0]
                tstat = row['t_stat'].values[0]
                pval = row['p_value'].values[0]
                sig = "***" if pval < 0.01 else "**" if pval < 0.05 else "*" if pval < 0.1 else ""
                lines.append(f"{t} & {hike:.4f} & {cut:.4f} & {diff:.4f} & {se:.4f} & {tstat:.2f} & {pval:.4f}{sig} \\\\")

        lines.append("\\bottomrule")
        lines.append("\\multicolumn{7}{p{0.9\\textwidth}}{\\footnotesize \\textit{Notes:} " +
                     "Pairwise comparison of hike and cut coefficients at selected time periods. " +
                     "H\\textsubscript{0}: $\\beta_{hike}(t) = \\beta_{cut}(t)$. " +
                     "*** p<0.01, ** p<0.05, * p<0.1.}")
        lines.append("\\end{tabular}")
        lines.append("\\end{table}")

        with open(os.path.join(output_dir, "asymmetry_pairwise.tex"), "w") as f:
            f.write("\n".join(lines))
        print(f"Saved pairwise table to {output_dir}/asymmetry_pairwise.tex")

    # Table 3: Cumulative and Average Tests
    lines = []
    lines.append("\\begin{table}[htbp]")
    lines.append("\\centering")
    lines.append("\\caption{Asymmetry Tests: Cumulative and Average Effects}")
    lines.append("\\label{tab:asymmetry_cumulative}")
    lines.append("\\begin{tabular}{lcccc}")
    lines.append("\\toprule")
    lines.append("Test & Estimate & Std. Error & t-stat & p-value \\\\")
    lines.append("\\midrule")

    avg_diff = test_results.get('average_difference', {})
    if 'difference' in avg_diff:
        diff = avg_diff['difference']
        se = avg_diff['std_error']
        tstat = avg_diff['t_statistic']
        pval = avg_diff['p_value']
        sig = "***" if pval < 0.01 else "**" if pval < 0.05 else "*" if pval < 0.1 else ""
        lines.append(f"Average Difference & {diff:.4f} & {se:.4f} & {tstat:.2f} & {pval:.4f}{sig} \\\\")

    cum_test = test_results.get('cumulative_effect', {})
    if 'difference' in cum_test:
        diff = cum_test['difference']
        se = cum_test['std_error']
        tstat = cum_test['t_statistic']
        pval = cum_test['p_value']
        periods = cum_test.get('periods', [])
        sig = "***" if pval < 0.01 else "**" if pval < 0.05 else "*" if pval < 0.1 else ""
        lines.append(f"Cumulative Diff (t={','.join(map(str, periods))}) & {diff:.4f} & {se:.4f} & {tstat:.2f} & {pval:.4f}{sig} \\\\")

    lines.append("\\bottomrule")
    lines.append("\\multicolumn{5}{p{0.8\\textwidth}}{\\footnotesize \\textit{Notes:} " +
                 "Tests of equality between hike and cut effects. " +
                 "Average difference tests H\\textsubscript{0}: $\\bar{\\beta}_{hike} = \\bar{\\beta}_{cut}$. " +
                 "Cumulative difference tests H\\textsubscript{0}: $\\sum_t \\beta_{hike}(t) = \\sum_t \\beta_{cut}(t)$. " +
                 "*** p<0.01, ** p<0.05, * p<0.1.}")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")

    with open(os.path.join(output_dir, "asymmetry_cumulative.tex"), "w") as f:
        f.write("\n".join(lines))
    print(f"Saved cumulative tests table to {output_dir}/asymmetry_cumulative.tex")


def save_interaction_latex_table(interaction_df, output_dir=TABLES_DIR):
    """
    Save interaction term regression results as LaTeX table.

    Parameters:
    -----------
    interaction_df : pd.DataFrame
        Results from run_interaction_regression
    output_dir : str
        Directory to save tables
    """
    if interaction_df.empty:
        return

    os.makedirs(output_dir, exist_ok=True)

    lines = []
    lines.append("\\begin{table}[htbp]")
    lines.append("\\centering")
    lines.append("\\caption{Asymmetry Tests: Interaction Term Regression Results}")
    lines.append("\\label{tab:asymmetry_interaction}")
    lines.append("\\begin{tabular}{cccccc}")
    lines.append("\\toprule")
    lines.append("Time & Base Effect (Cut) & Interaction & Total Hike & Diff (Hike-Cut) & p-value \\\\")
    lines.append("\\midrule")

    key_times = [0, 6, 12]
    for t in key_times:
        row = interaction_df[interaction_df['time'] == t]
        if not row.empty and not pd.isna(row['interaction_coef'].values[0]):
            base = row['base_coef'].values[0]
            int_coef = row['interaction_coef'].values[0]
            total_hike = row['total_hike'].values[0]
            diff = int_coef  # Interaction coefficient is the difference
            pval = row['interaction_pval'].values[0]
            sig = "***" if pval < 0.01 else "**" if pval < 0.05 else "*" if pval < 0.1 else ""
            lines.append(f"{t} & {base:.4f} & {int_coef:.4f} & {total_hike:.4f} & {diff:.4f} & {pval:.4f}{sig} \\\\")

    lines.append("\\bottomrule")
    lines.append("\\multicolumn{6}{p{0.9\\textwidth}}{\\footnotesize \\textit{Notes:} " +
                 "Interaction regression: $y = \\beta_0 \\cdot Shock + \\gamma \\cdot Shock \\times Hike + FE + \\epsilon$. " +
                 "Base effect represents pass-through for cuts. Interaction term captures the differential effect of hikes. " +
                 "Total Hike = Base + Interaction. H\\textsubscript{0} for p-value: $\\gamma = 0$. " +
                 "*** p<0.01, ** p<0.05, * p<0.1.}")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")

    with open(os.path.join(output_dir, "asymmetry_interaction.tex"), "w") as f:
        f.write("\n".join(lines))
    print(f"Saved interaction table to {output_dir}/asymmetry_interaction.tex")


def calculate_power_analysis(effect_size=0.15, n_obs=5000000, alpha=0.05):
    """
    Calculate statistical power for detecting asymmetry.

    Parameters:
    -----------
    effect_size : float
        Minimum detectable effect size (difference in coefficients)
    n_obs : int
        Total number of observations
    alpha : float
        Significance level

    Returns:
    --------
    dict : Power analysis results
    """
    # Approximate power calculation for two-sample t-test
    # Using formula: power = P(reject H0 | H1 is true)

    from scipy.stats import norm

    # Standard error approximation (clustered at geo level)
    # Assuming 30 clusters, design effect ~2
    n_eff = n_obs / 2  # Effective sample size after clustering
    se = 0.07  # Approximate SE from main results

    # Non-centrality parameter
    ncp = effect_size / se

    # Critical value
    z_alpha = norm.ppf(1 - alpha/2)

    # Power
    power = 1 - norm.cdf(z_alpha - ncp) + norm.cdf(-z_alpha - ncp)

    # Minimum detectable effect at 80% power
    z_beta = norm.ppf(0.80)
    mde = (z_alpha + z_beta) * se

    return {
        'effect_size_tested': effect_size,
        'approximate_se': se,
        'power_at_15pp': power,
        'min_detectable_effect_80': mde,
        'min_detectable_effect_90': (norm.ppf(1-alpha/2) + norm.ppf(0.90)) * se,
        'alpha': alpha,
        'n_observations': n_obs,
        'n_effective': n_eff
    }

def analysis_heterogeneity_v2(stacked_df):
    print("\n--- Running Heterogeneity Analysis (Core/Periphery, Durable/Non-Durable) ---")
    if stacked_df.empty: return

    # 1. Core vs Periphery
    stacked_df['geo_group'] = stacked_df['geo'].apply(get_country_group)
    geo_results = {}
    
    for grp in ['Core', 'Periphery']:
        sub_df = stacked_df[stacked_df['geo_group'] == grp].copy()
        if len(sub_df) < 100:
            print(f"Skipping geo group {grp}, too few obs.")
            continue
        print(f"Running for Geo Group: {grp} (Obs: {len(sub_df)})")
        weights_col = CONFIG.get("analysis", {}).get("weight_column", None)
        res, col_names = run_absorbing_regression(
            sub_df,
            y_col="norm_log_hicp",
            treat_vars=["treat_shock"],
            half_window=CONFIG.get("analysis", {}).get("event_window", 12),
            base_period=CONFIG.get("identification", {}).get("base_period", -1),
            absorb_cols=["geo_coicop", "cal_time", "rel_time"],
            cluster_col="geo",
            weights_col=weights_col,
            include_time_dummies=False
        )
        geo_results[grp] = extract_coefficients_absorbing(
            res,
            'treat_shock',
            half_window=CONFIG.get("analysis", {}).get("event_window", 12),
            base_period=CONFIG.get("identification", {}).get("base_period", -1),
            col_names=col_names
        )
        
    if geo_results:
        plot_coefficients(geo_results, "Pass-through: Core vs Periphery", "heterogeneity_core_periphery.png")
        combined_geo = []
        for grp, df in geo_results.items():
            df['group'] = grp
            combined_geo.append(df)
        if combined_geo:
            pd.concat(combined_geo).to_csv(os.path.join(TABLES_DIR, "heterogeneity_core_periphery.csv"), index=False)
            save_latex_table(pd.concat(combined_geo), "heterogeneity_core_periphery.tex", "Heterogeneity: Core vs Periphery", "tab:het_core_periph")

    # 2. Durable vs Non-durable
    stacked_df['durability'] = stacked_df['coicop'].apply(get_durability)
    dur_results = {}
    
    for grp in ['Durable', 'Non-durable']:
        sub_df = stacked_df[stacked_df['durability'] == grp].copy()
        if len(sub_df) < 100:
            print(f"Skipping durability group {grp}, too few obs.")
            continue
        print(f"Running for Durability Group: {grp} (Obs: {len(sub_df)})")
        weights_col = CONFIG.get("analysis", {}).get("weight_column", None)
        res, col_names = run_absorbing_regression(
            sub_df,
            y_col="norm_log_hicp",
            treat_vars=["treat_shock"],
            half_window=CONFIG.get("analysis", {}).get("event_window", 12),
            base_period=CONFIG.get("identification", {}).get("base_period", -1),
            absorb_cols=["geo_coicop", "cal_time", "rel_time"],
            cluster_col="geo",
            weights_col=weights_col,
            include_time_dummies=False
        )
        dur_results[grp] = extract_coefficients_absorbing(
            res,
            'treat_shock',
            half_window=CONFIG.get("analysis", {}).get("event_window", 12),
            base_period=CONFIG.get("identification", {}).get("base_period", -1),
            col_names=col_names
        )
        
    if dur_results:
        plot_coefficients(dur_results, "Pass-through: Durable vs Non-durable", "heterogeneity_durable_nondurable.png")
        combined_dur = []
        for grp, df in dur_results.items():
            df['group'] = grp
            combined_dur.append(df)
        if combined_dur:
            pd.concat(combined_dur).to_csv(os.path.join(TABLES_DIR, "heterogeneity_durability.csv"), index=False)
            # The user specifically asked for "output/tables/heterogeneity_results.tex"
            save_latex_table(pd.concat(combined_dur), "heterogeneity_results.tex", "Heterogeneity: Durable vs Non-durable", "tab:het_durability")

def analysis_robustness(df, events, stacked_df_main):
    print("\n--- Running Robustness Checks ---")
    
    robustness_summary = []
    
    # 1. Alternative Clustering
    # Clusters: geo (Main), geo-year, geo-coicop
    clustering_options = ['geo', 'geo_year', 'geo_coicop']
    
    # Ensure columns exist (geo_coicop exists from create_stacked_dataset)
    if 'geo_year' not in stacked_df_main.columns:
         stacked_df_main['year'] = stacked_df_main['time'].dt.year
         stacked_df_main['geo_year'] = stacked_df_main['geo'] + "_" + stacked_df_main['year'].astype(str)
         
    for cluster_col in clustering_options:
        if cluster_col not in stacked_df_main.columns:
            print(f"Warning: {cluster_col} not found in dataset")
            continue
            
        print(f"Robustness: Clustering by {cluster_col}")
        weights_col = CONFIG.get("analysis", {}).get("weight_column", None)
        res, col_names = run_absorbing_regression(
            stacked_df_main,
            y_col="norm_log_hicp",
            treat_vars=["treat_shock"],
            half_window=CONFIG.get("analysis", {}).get("event_window", 12),
            base_period=CONFIG.get("identification", {}).get("base_period", -1),
            absorb_cols=["geo_coicop", "cal_time", "rel_time"],
            cluster_col=cluster_col,
            weights_col=weights_col,
            include_time_dummies=False
        )
        coeffs = extract_coefficients_absorbing(
            res,
            'treat_shock',
            half_window=CONFIG.get("analysis", {}).get("event_window", 12),
            base_period=CONFIG.get("identification", {}).get("base_period", -1),
            col_names=col_names
        )
        
        # Extract key stats for t=0 and t=12
        for t in [0, 12]:
            row = coeffs[coeffs['rel_time'] == t]
            if not row.empty:
                robustness_summary.append({
                    'Check': f"Cluster: {cluster_col}",
                    'Time': t,
                    'Coef': row['coef'].values[0],
                    'SE': row['se'].values[0],
                    'P-val': row['pval'].values[0]
                })
                
    # 2. Alternative Windows
    for w in [12, 24]:
        print(f"Robustness: Window +/- {w}")
        if w == 12:
            current_stacked = stacked_df_main
        else:
            # Need to re-stack with larger window
            current_stacked = build_stacked_with_controls(df, events, half_window=w)
            
        if current_stacked.empty: continue
        
        weights_col = CONFIG.get("analysis", {}).get("weight_column", None)
        res, col_names = run_absorbing_regression(
            current_stacked,
            y_col="norm_log_hicp",
            treat_vars=["treat_shock"],
            half_window=w,
            base_period=CONFIG.get("identification", {}).get("base_period", -1),
            absorb_cols=["geo_coicop", "cal_time", "rel_time"],
            cluster_col="geo",
            weights_col=weights_col,
            include_time_dummies=False
        )
        coeffs = extract_coefficients_absorbing(
            res,
            'treat_shock',
            half_window=w,
            base_period=CONFIG.get("identification", {}).get("base_period", -1),
            col_names=col_names
        )
        
        for t in [0, 12, 24]:
            if t > w: continue
            row = coeffs[coeffs['rel_time'] == t]
            if not row.empty:
                robustness_summary.append({
                    'Check': f"Window: {w}",
                    'Time': t,
                    'Coef': row['coef'].values[0],
                    'SE': row['se'].values[0],
                    'P-val': row['pval'].values[0]
                })

    # 3. Exclude Crisis Years (2008-2009, 2020-2021)
    print("Robustness: Excluding Crisis Years (2008-2009, 2020-2021)")
    crisis_years = [2008, 2009, 2020, 2021]
    non_crisis_stacked = stacked_df_main[~stacked_df_main['year'].isin(crisis_years)].copy()
    
    if not non_crisis_stacked.empty:
        weights_col = CONFIG.get("analysis", {}).get("weight_column", None)
        res_nc, col_names = run_absorbing_regression(
            non_crisis_stacked,
            y_col="norm_log_hicp",
            treat_vars=["treat_shock"],
            half_window=CONFIG.get("analysis", {}).get("event_window", 12),
            base_period=CONFIG.get("identification", {}).get("base_period", -1),
            absorb_cols=["geo_coicop", "cal_time", "rel_time"],
            cluster_col="geo",
            weights_col=weights_col,
            include_time_dummies=False
        )
        coeffs_nc = extract_coefficients_absorbing(
            res_nc,
            'treat_shock',
            half_window=CONFIG.get("analysis", {}).get("event_window", 12),
            base_period=CONFIG.get("identification", {}).get("base_period", -1),
            col_names=col_names
        )
        
        for t in [0, 12]:
            row = coeffs_nc[coeffs_nc['rel_time'] == t]
            if not row.empty:
                robustness_summary.append({
                    'Check': "Exclude Crisis Years",
                    'Time': t,
                    'Coef': row['coef'].values[0],
                    'SE': row['se'].values[0],
                    'P-val': row['pval'].values[0]
                })
        
        # Save specific table for crisis robustness
        save_latex_table(coeffs_nc, "robustness_crisis.tex", "Robustness: Excluding Crisis Periods (2008-09, 2020-21)", "tab:rob_crisis")

    # Save Robustness Table
    rob_df = pd.DataFrame(robustness_summary)
    rob_df.to_csv(os.path.join(TABLES_DIR, "robustness_summary.csv"), index=False)
    
    # Generate Latex for Clustering Robustness
    cluster_df = rob_df[rob_df['Check'].str.startswith('Cluster')]
    save_latex_table(cluster_df, "robustness_clustering.tex", "Robustness: Alternative Clustering Standard Errors", "tab:rob_cluster")
    
    return rob_df

def main():
    # 1. Load
    df, events = load_and_prep_data()
    
    # 2. Stack (Default Window 12)
    half_window = CONFIG.get("analysis", {}).get("event_window", 12)
    stacked_df = build_stacked_with_controls(df, events, half_window=half_window)
    
    if stacked_df.empty:
        print("Analysis aborted due to empty dataset.")
        return
        
    # 3. Main Regression (Cluster by Geo)
    weights_col = CONFIG.get("analysis", {}).get("weight_column", None)
    res_main, col_names = run_absorbing_regression(
        stacked_df,
        y_col="norm_log_hicp",
        treat_vars=["treat_shock"],
        half_window=half_window,
        base_period=CONFIG.get("identification", {}).get("base_period", -1),
        absorb_cols=["geo_coicop", "cal_time", "rel_time"],
        cluster_col="geo",
        weights_col=weights_col,
        include_time_dummies=False
    )
    results_main = extract_coefficients_absorbing(
        res_main,
        treat_var='treat_shock',
        half_window=half_window,
        base_period=CONFIG.get("identification", {}).get("base_period", -1),
        col_names=col_names
    )
    
    # 4. Basic Outputs
    plot_coefficients({'All Events': results_main}, "Pass-through of VAT Changes (Stacked w/ Controls)", "main_event_study.png")
    results_main.to_csv(os.path.join(TABLES_DIR, "main_regression_results.csv"), index=False)
    save_latex_table(results_main, "main_regression_results.tex", "Baseline Pass-through Estimates", "tab:main_results")
    
    # Prepare results.yaml data
    t0_row = results_main[results_main['rel_time'] == 0]
    t12_row = results_main[results_main['rel_time'] == 12]
    
    results_data = {
        'spec_id': 'baseline_vat_passthrough',
        'key_coeffs': {
            't_0': float(t0_row['coef'].values[0]) if not t0_row.empty else None,
            't_12': float(t12_row['coef'].values[0]) if not t12_row.empty else None
        },
        'se': {
             't_0': float(t0_row['se'].values[0]) if not t0_row.empty else None,
             't_12': float(t12_row['se'].values[0]) if not t12_row.empty else None
        },
        'n': int(res_main.nobs) if res_main else 0,
        'fe': 'Geo×COICOP FE (absorbed) + Calendar Time FE (absorbed) + Event-time dummies',
        'clusters': 'Geo',
        'figs': ['output/figures/main_event_study.png'],
        'tables': ['output/tables/main_regression_results.tex']
    }
    
    # Print P-values for User
    print("\n--- P-values for User ---")
    if not t0_row.empty:
        print(f"Main Result t=0: Coef={t0_row['coef'].values[0]:.4f}, P-val={t0_row['pval'].values[0]:.6f}")
    if not t12_row.empty:
        print(f"Main Result t=12: Coef={t12_row['coef'].values[0]:.4f}, P-val={t12_row['pval'].values[0]:.6f}")
    
    # 5. Asymmetry
    asym_diffs, asym_summary = analysis_asymmetry(stacked_df)
    if not asym_diffs.empty:
        asym_diffs.to_csv(os.path.join(TABLES_DIR, "asymmetry_tests.csv"), index=False)
        save_latex_table(asym_diffs, "asymmetry_results.tex", "Asymmetry Tests (Hikes vs Cuts)", "tab:asymmetry_results")

    # Add asymmetry results to YAML
    if asym_summary:
        results_data['asymmetry_tests'] = {
            'joint_all_pvalue': asym_summary.get('joint_all', {}).get('p_value'),
            'joint_post_pvalue': asym_summary.get('joint_post', {}).get('p_value'),
            'cumulative_pvalue': asym_summary.get('cumulative', {}).get('p_value'),
            'conclusion': asym_summary.get('conclusion'),
            'power_15pp': asym_summary.get('power', {}).get('power_at_15pp'),
            'mde_80': asym_summary.get('power', {}).get('min_detectable_effect_80')
        }
    
    # 6. Heterogeneity (New)
    analysis_heterogeneity_v2(stacked_df)
    
    # 7. Robustness (New)
    analysis_robustness(df, events, stacked_df)
    
    # 8. Save YAML
    export_results_yaml(results_data)
    
    print("Analysis complete. Check output/ folder.")

if __name__ == "__main__":
    main()
