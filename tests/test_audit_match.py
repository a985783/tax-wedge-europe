from src.audit.metadata_match import match_events

def test_match_events_runs():
    out = match_events(sample_n=5, seed=1)
    assert "precision" in out
