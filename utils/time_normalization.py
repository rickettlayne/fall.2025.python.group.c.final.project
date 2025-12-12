import re

def normalize_year(value):
    if value is None:
        return None
    if isinstance(value, int):
        return value
    match = re.search(r"(19|20)\d{2}", str(value))
    return int(match.group()) if match else None
