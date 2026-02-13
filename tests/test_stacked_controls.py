import pandas as pd
from src.analysis.models import build_stacked_with_controls

def test_build_stacked_with_controls_has_controls():
    df = pd.DataFrame({
        "geo": ["A", "A", "B", "B"],
        "coicop": ["CP01", "CP01", "CP01", "CP01"],
        "time": ["2019-12", "2020-01", "2019-12", "2020-01"],
        "log_hicp": [4.5, 4.6, 4.4, 4.5],
        "weight": [1.0, 1.0, 1.0, 1.0]
    })
    events = pd.DataFrame({
        "geo": ["A"], "coicop": ["CP01"], "time": ["2020-01"], "delta_tw": [0.02]
    })
    stacked = build_stacked_with_controls(df, events, half_window=1)
    assert (stacked["treated"] == 0).any()
