from src.utils.time_parse import normalize_time

def test_normalize_time():
    assert normalize_time("2020M01") == "2020-01"
    assert normalize_time("1999M12") == "1999-12"
