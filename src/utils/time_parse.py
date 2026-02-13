import re

def normalize_time(t):
    if t is None:
        return t
    s = str(t)
    match = re.match(r"^(\d{4})M(\d{2})$", s)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    return s
