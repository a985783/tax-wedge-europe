"""
Wild Cluster Bootstrap Usage Example
=====================================

This script demonstrates how to use the Wild Cluster Bootstrap functionality
to address small cluster number issues (G < 50) in your econometric analysis.

Based on: Cameron, Gelbach & Miller (2008)
"""

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analysis.models import (
    load_and_prep_data,
    build_stacked_with_controls,
    BootstrapConfig,
    WildClusterBootstrap,
    run_wild_bootstrap_inference,
    load_bootstrap_config_from_yaml,
    run_main_analysis_with_bootstrap
)


def example_1_basic_usage():
    """
    Example 1: Basic Wild Cluster Bootstrap Usage

    This example shows the simplest way to run bootstrap inference
    on your event study coefficients.
    """
    print("="*80)
    print("Example 1: Basic Wild Cluster Bootstrap Usage")
    print("="*80)

    # Load data
    df, events = load_and_prep_data()

    # Build stacked dataset
    stacked_df = build_stacked_with_controls(df, events, half_window=12)

    # Configure bootstrap
    config = BootstrapConfig(
        n_bootstrap=9999,        # Number of replications
        distribution="rademacher",  # Weight distribution
        confidence_level=0.95,   # 95% confidence intervals
        seed=42,                 # For reproducibility
        small_cluster_correction=True  # Apply small G correction
    )

    # Run bootstrap inference
    results = run_wild_bootstrap_inference(
        df=stacked_df,
        y_col="norm_log_hicp",
        treat_var="treat_shock",
        half_window=12,
        base_period=-1,
        absorb_cols=["geo_coicop", "cal_time", "rel_time"],
        cluster_col="geo",
        weights_col="event_weight",
        config=config
    )

    print("\nBootstrap Results (Key Periods):")
    print("-" * 80)
    print(f"{'Time':<6} {'Coef':<10} {'SE':<10} {'p-value':<12} {'CI Lower':<10} {'CI Upper':<10}")
    print("-" * 80)

    for t in [-12, -6, -1, 0, 6, 12]:
        row = results[results['rel_time'] == t]
        if not row.empty:
            print(f"{t:<6} {row['coef'].values[0]:<10.4f} {row['se'].values[0]:<10.4f} "
                  f"{row['pval_bootstrap'].values[0]:<12.4f} {row['ci_lower'].values[0]:<10.4f} "
                  f"{row['ci_upper'].values[0]:<10.4f}")

    return results


def example_2_different_distributions():
    """
    Example 2: Comparing Different Weight Distributions

    This example compares the three available weight distributions
    for the wild bootstrap.
    """
    print("\n" + "="*80)
    print("Example 2: Comparing Different Weight Distributions")
    print("="*80)

    # Load data
    df, events = load_and_prep_data()
    stacked_df = build_stacked_with_controls(df, events, half_window=12)

    distributions = ["rademacher", "mammen", "webb_6pt"]
    all_results = {}

    for dist in distributions:
        print(f"\nRunning with {dist} distribution...")

        config = BootstrapConfig(
            n_bootstrap=9999,
            distribution=dist,
            confidence_level=0.95,
            seed=42
        )

        results = run_wild_bootstrap_inference(
            df=stacked_df,
            y_col="norm_log_hicp",
            treat_var="treat_shock",
            half_window=12,
            base_period=-1,
            absorb_cols=["geo_coicop", "cal_time", "rel_time"],
            cluster_col="geo",
            weights_col="event_weight",
            config=config
        )

        all_results[dist] = results

    # Compare results at t=0
    print("\nComparison at t=0:")
    print("-" * 80)
    print(f"{'Distribution':<15} {'Coef':<10} {'p-value':<12} {'CI Lower':<10} {'CI Upper':<10}")
    print("-" * 80)

    for dist, results in all_results.items():
        row = results[results['rel_time'] == 0]
        if not row.empty:
            print(f"{dist:<15} {row['coef'].values[0]:<10.4f} "
                  f"{row['pval_bootstrap'].values[0]:<12.4f} "
                  f"{row['ci_lower'].values[0]:<10.4f} "
                  f"{row['ci_upper'].values[0]:<10.4f}")

    return all_results


def example_3_using_yaml_config():
    """
    Example 3: Using Configuration from YAML File

    This example shows how to load bootstrap configuration
    from the analysis_config.yaml file.
    """
    print("\n" + "="*80)
    print("Example 3: Using Configuration from YAML File")
    print("="*80)

    # Load bootstrap configuration from YAML
    config = load_bootstrap_config_from_yaml()

    if config is None:
        print("Bootstrap is disabled in configuration.")
        print("To enable, set analysis.bootstrap.enabled: true in analysis_config.yaml")
        return None

    print(f"Loaded configuration:")
    print(f"  - Bootstrap replications: {config.n_bootstrap}")
    print(f"  - Distribution: {config.distribution}")
    print(f"  - Confidence level: {config.confidence_level}")
    print(f"  - Seed: {config.seed}")
    print(f"  - Small cluster correction: {config.small_cluster_correction}")

    # Load data and run analysis
    df, events = load_and_prep_data()

    results = run_main_analysis_with_bootstrap(
        df=df,
        events=events,
        use_bootstrap=True
    )

    return results


def example_4_direct_class_usage():
    """
    Example 4: Direct WildClusterBootstrap Class Usage

    This example shows how to use the WildClusterBootstrap class
    directly for more control over the bootstrap procedure.
    """
    print("\n" + "="*80)
    print("Example 4: Direct WildClusterBootstrap Class Usage")
    print("="*80)

    import pandas as pd
    import numpy as np

    # Load data
    df, events = load_and_prep_data()
    stacked_df = build_stacked_with_controls(df, events, half_window=12)

    # Subset to a specific time period for demonstration
    t = 0
    df_t = stacked_df[stacked_df['rel_time'] == t].copy()
    df_t = df_t.reset_index(drop=True)
    df_t = df_t.replace([np.inf, -np.inf], np.nan)

    # Prepare data
    y = df_t["norm_log_hicp"].to_numpy(dtype=np.float64)
    X = df_t[["treat_shock"]].to_numpy(dtype=np.float64)
    X = np.column_stack([np.ones(len(X)), X])  # Add constant

    clusters = df_t["geo"].to_numpy()
    clusters_numeric = pd.Categorical(clusters).codes

    # Create bootstrap instance
    config = BootstrapConfig(
        n_bootstrap=9999,
        distribution="rademacher",
        confidence_level=0.95,
        seed=42
    )

    bootstrap = WildClusterBootstrap(config)

    # Run bootstrap (param_idx=1 for the treatment coefficient)
    print(f"\nRunning bootstrap for t={t}...")
    bootstrap.fit(y, X, clusters_numeric, param_idx=1)

    # Get summary
    summary = bootstrap.summary()
    print("\nBootstrap Summary:")
    print(summary.to_string(index=False))

    # Access detailed results
    print("\nDetailed Results:")
    print(f"  Estimate: {bootstrap.results_['estimate']:.4f}")
    print(f"  Std Error: {bootstrap.results_['std_error']:.4f}")
    print(f"  t-statistic: {bootstrap.results_['t_stat']:.4f}")
    print(f"  p-value: {bootstrap.results_['p_value']:.4f}")
    print(f"  95% CI: [{bootstrap.results_['ci_lower']:.4f}, {bootstrap.results_['ci_upper']:.4f}]")
    print(f"  Number of clusters: {bootstrap.results_['n_clusters']}")

    return bootstrap


def example_5_small_cluster_recommendations():
    """
    Example 5: Recommendations for Small Cluster Numbers

    This example provides recommendations for different cluster sizes
    based on Cameron, Gelbach & Miller (2008).
    """
    print("\n" + "="*80)
    print("Example 5: Recommendations for Small Cluster Numbers")
    print("="*80)

    print("""
    Recommendations based on Cameron, Gelbach & Miller (2008):

    1. Number of Clusters (G):
       - G < 10:  Use Webb's six-point distribution (webb_6pt)
       - 10 <= G < 30: Use Mammen's two-point distribution (mammen)
       - G >= 30: Use Rademacher distribution (rademacher)

    2. Bootstrap Replications (B):
       - Minimum: 999 replications
       - Recommended: 9,999 replications
       - For publication: 99,999 replications

    3. Confidence Level:
       - Standard: 95%
       - For robustness: 90% and 99%

    4. Small Sample Corrections:
       - Always apply for G < 50
       - Uses G/(G-1) correction factor

    Your current setup:
    - Countries: 30 (G = 30)
    - Recommended distribution: rademacher or mammen
    - Recommended replications: 9999
    """)

    # Load data and check number of clusters
    df, events = load_and_prep_data()
    stacked_df = build_stacked_with_controls(df, events, half_window=12)

    n_clusters = stacked_df['geo'].nunique()
    print(f"\nActual number of clusters in your data: {n_clusters}")

    if n_clusters < 10:
        print("Recommendation: Use 'webb_6pt' distribution")
    elif n_clusters < 30:
        print("Recommendation: Use 'mammen' distribution")
    else:
        print("Recommendation: Use 'rademacher' distribution (default)")


if __name__ == "__main__":
    print("\n")
    print("*" * 80)
    print("Wild Cluster Bootstrap Examples")
    print("Cameron, Gelbach & Miller (2008) Implementation")
    print("*" * 80)

    # Run examples
    # Uncomment the examples you want to run:

    # example_1_basic_usage()
    # example_2_different_distributions()
    # example_3_using_yaml_config()
    # example_4_direct_class_usage()
    example_5_small_cluster_recommendations()

    print("\n" + "*" * 80)
    print("Examples completed!")
    print("*" * 80)
