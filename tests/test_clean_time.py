from src.utils.time_parse import normalize_time

def test_clean_time_format():
    assert normalize_time("2015M03") == "2015-03"
