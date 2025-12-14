# utils/state_mapping.py

STATE_MAP = {
    "ALABAMA": "AL", "AL": "AL",
    "ALASKA": "AK", "AK": "AK",
    "ARIZONA": "AZ", "AZ": "AZ",
    "ARKANSAS": "AR", "AR": "AR",
    "CALIFORNIA": "CA", "CA": "CA",
    "COLORADO": "CO", "CO": "CO",
    "CONNECTICUT": "CT", "CT": "CT",
    "DELAWARE": "DE", "DE": "DE",
    "DISTRICT OF COLUMBIA": "DC", "DC": "DC",
    "FLORIDA": "FL", "FL": "FL",
    "GEORGIA": "GA", "GA": "GA",
    "HAWAII": "HI", "HI": "HI",
    "IDAHO": "ID", "ID": "ID",
    "ILLINOIS": "IL", "IL": "IL",
    "INDIANA": "IN", "IN": "IN",
    "IOWA": "IA", "IA": "IA",
    "KANSAS": "KS", "KS": "KS",
    "KENTUCKY": "KY", "KY": "KY",
    "LOUISIANA": "LA", "LA": "LA",
    "MAINE": "ME", "ME": "ME",
    "MARYLAND": "MD", "MD": "MD",
    "MASSACHUSETTS": "MA", "MA": "MA",
    "MICHIGAN": "MI", "MI": "MI",
    "MINNESOTA": "MN", "MN": "MN",
    "MISSISSIPPI": "MS", "MS": "MS",
    "MISSOURI": "MO", "MO": "MO",
    "MONTANA": "MT", "MT": "MT",
    "NEBRASKA": "NE", "NE": "NE",
    "NEVADA": "NV", "NV": "NV",
    "NEW HAMPSHIRE": "NH", "NH": "NH",
    "NEW JERSEY": "NJ", "NJ": "NJ",
    "NEW MEXICO": "NM", "NM": "NM",
    "NEW YORK": "NY", "NY": "NY",
    "NORTH CAROLINA": "NC", "NC": "NC",
    "NORTH DAKOTA": "ND", "ND": "ND",
    "OHIO": "OH", "OH": "OH",
    "OKLAHOMA": "OK", "OK": "OK",
    "OREGON": "OR", "OR": "OR",
    "PENNSYLVANIA": "PA", "PA": "PA",
    "RHODE ISLAND": "RI", "RI": "RI",
    "SOUTH CAROLINA": "SC", "SC": "SC",
    "SOUTH DAKOTA": "SD", "SD": "SD",
    "TENNESSEE": "TN", "TN": "TN",
    "TEXAS": "TX", "TX": "TX",
    "UTAH": "UT", "UT": "UT",
    "VERMONT": "VT", "VT": "VT",
    "VIRGINIA": "VA", "VA": "VA",
    "WASHINGTON": "WA", "WA": "WA",
    "WEST VIRGINIA": "WV", "WV": "WV",
    "WISCONSIN": "WI", "WI": "WI",
    "WYOMING": "WY", "WY": "WY",
    # anything like Countrywide will map to None
}

def normalize_state(value):
    """
    Convert messy state text to two letter codes.
    Examples:
        Alabama → AL
        texas → TX
        TX → TX
        Countrywide → None
    """
    if value is None:
        return None

    key = str(value).strip().upper().replace(".", "")
    # special case for Countrywide style rows
    if "COUNTRYWIDE" in key:
        return None

    return STATE_MAP.get(key)
