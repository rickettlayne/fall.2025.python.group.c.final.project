# utils/time_normalization.py

def normalize_year(value):
    """
    Convert various year formats to int year.
    Examples:
        2019 → 2019
        2019.0 → 2019
        "2019 " → 2019
        "2019 01 01" → 2019
    """
    if value is None:
        return None

    s = str(value).strip()
    if len(s) < 4:
        return None

    try:
        return int(s[:4])
    except ValueError:
        return None
