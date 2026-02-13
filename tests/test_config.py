from src.utils.config import load_config

def test_load_config_has_required_keys():
    cfg = load_config("analysis_config.yaml")
    assert "identification" in cfg
    assert "event_threshold" in cfg["identification"]
    assert "clean_window_months" in cfg["identification"]
