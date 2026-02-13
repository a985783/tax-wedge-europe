import pandas as pd
from src.identification.detect_events import apply_clean_window

def test_clean_window_geo_coicop():
    df = pd.DataFrame({
        "geo": ["AA", "AA", "AA"],
        "coicop": ["CP01", "CP01", "CP01"],
        "time": ["2020-01", "2020-03", "2020-10"],
        "delta_tw": [0.02, 0.03, 0.02]
    })
    out = apply_clean_window(df, window_months=6)
    assert out.loc[1, "is_clean"] == False
