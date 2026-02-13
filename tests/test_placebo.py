from src.analysis.robustness import run_placebo

def test_placebo_runs():
    result = run_placebo(seed=1, n_sim=1, sample_events=1)
    assert "pvals" in result
