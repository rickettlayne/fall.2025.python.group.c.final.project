# utils/value_normalization.py

def normalize_dollar(value):
    """
    Normalize dollar like numbers to float.
    Handles strings with commas or dollar signs.
    """
    if value is None:
        return None

    s = str(value).strip()
    if s == "":
        return None

    s = s.replace("$", "").replace(",", "")

    try:
        return float(s)
    except ValueError:
        return None
