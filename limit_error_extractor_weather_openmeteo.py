"""
extractor_weather_openweather_counts.py

Use OpenWeather One Call 3.0 day_summary endpoint for each US state
for every day in 2025.

Instead of saving daily rows, this script counts the number of
bad weather days per state per year, broken into slices:
    - precip_bad_days
    - wind_bad_days
    - both_precip_and_wind_days
    - bad_days_total

Output:
    CSV saved in the same folder as this script
    one row per state per year with counts.
"""

import os
import time
from datetime import date, timedelta

import requests
import certifi
import pandas as pd

# ====================================================
# Configuration
# ====================================================

API_KEY = "00dfda3b7018f77e51ee74b2a4805abc"

BASE_URL = "https://api.openweathermap.org/data/3.0/onecall/day_summary"

YEAR = 2025
START_DATE = date(YEAR, 1, 1)
END_DATE = date(YEAR, 12, 31)

# Thresholds for bad weather
PRECIP_THRESHOLD_MM = 0.1        # any measurable precip
WIND_MAX_THRESHOLD_MS = 13.4     # about 30 mph

# Representative coordinates for each state
US_STATE_COORDS = {
    "AL": {"name": "Alabama", "lat": 32.3182, "lon": -86.9023},
    "AK": {"name": "Alaska", "lat": 66.1605, "lon": -153.3691},
    "AZ": {"name": "Arizona", "lat": 34.0489, "lon": -111.0937},
    "AR": {"name": "Arkansas", "lat": 34.7999, "lon": -92.1999},
    "CA": {"name": "California", "lat": 36.7783, "lon": -119.4179},
    "CO": {"name": "Colorado", "lat": 39.1130, "lon": -105.3589},
    "CT": {"name": "Connecticut", "lat": 41.6032, "lon": -73.0877},
    "DE": {"name": "Delaware", "lat": 38.9108, "lon": -75.5277},
    "FL": {"name": "Florida", "lat": 27.6648, "lon": -81.5158},
    "GA": {"name": "Georgia", "lat": 32.1656, "lon": -82.9001},
    "HI": {"name": "Hawaii", "lat": 19.7418, "lon": -155.8444},
    "ID": {"name": "Idaho", "lat": 44.0682, "lon": -114.7420},
    "IL": {"name": "Illinois", "lat": 40.0, "lon": -89.0},
    "IN": {"name": "Indiana", "lat": 39.8494, "lon": -86.2583},
    "IA": {"name": "Iowa", "lat": 41.8780, "lon": -93.0977},
    "KS": {"name": "Kansas", "lat": 39.0119, "lon": -98.4842},
    "KY": {"name": "Kentucky", "lat": 37.8393, "lon": -84.2700},
    "LA": {"name": "Louisiana", "lat": 30.9843, "lon": -91.9623},
    "ME": {"name": "Maine", "lat": 45.2538, "lon": -69.4455},
    "MD": {"name": "Maryland", "lat": 39.0458, "lon": -76.6413},
    "MA": {"name": "Massachusetts", "lat": 42.4072, "lon": -71.3824},
    "MI": {"name": "Michigan", "lat": 44.3148, "lon": -85.6024},
    "MN": {"name": "Minnesota", "lat": 46.7296, "lon": -94.6859},
    "MS": {"name": "Mississippi", "lat": 32.3547, "lon": -89.3985},
    "MO": {"name": "Missouri", "lat": 37.9643, "lon": -91.8318},
    "MT": {"name": "Montana", "lat": 46.8797, "lon": -110.3626},
    "NE": {"name": "Nebraska", "lat": 41.4925, "lon": -99.9018},
    "NV": {"name": "Nevada", "lat": 38.8026, "lon": -116.4194},
    "NH": {"name": "New Hampshire", "lat": 43.1939, "lon": -71.5724},
    "NJ": {"name": "New Jersey", "lat": 40.0583, "lon": -74.4057},
    "NM": {"name": "New Mexico", "lat": 34.5199, "lon": -105.8701},
    "NY": {"name": "New York", "lat": 43.0, "lon": -75.0},
    "NC": {"name": "North Carolina", "lat": 35.7596, "lon": -79.0193},
    "ND": {"name": "North Dakota", "lat": 47.5515, "lon": -101.0020},
    "OH": {"name": "Ohio", "lat": 40.4173, "lon": -82.9071},
    "OK": {"name": "Oklahoma", "lat": 35.4676, "lon": -97.5164},
    "OR": {"name": "Oregon", "lat": 43.8041, "lon": -120.5542},
    "PA": {"name": "Pennsylvania", "lat": 41.2033, "lon": -77.1945},
    "RI": {"name": "Rhode Island", "lat": 41.5801, "lon": -71.4774},
    "SC": {"name": "South Carolina", "lat": 33.8361, "lon": -81.1637},
    "SD": {"name": "South Dakota", "lat": 43.9695, "lon": -99.9018},
    "TN": {"name": "Tennessee", "lat": 35.5175, "lon": -86.5804},
    "TX": {"name": "Texas", "lat": 31.0, "lon": -100.0},
    "UT": {"name": "Utah", "lat": 39.3200, "lon": -111.0937},
    "VT": {"name": "Vermont", "lat": 44.5588, "lon": -72.5778},
    "VA": {"name": "Virginia", "lat": 37.4316, "lon": -78.6569},
    "WA": {"name": "Washington", "lat": 47.7511, "lon": -120.7401},
    "WV": {"name": "West Virginia", "lat": 38.5976, "lon": -80.4549},
    "WI": {"name": "Wisconsin", "lat": 44.5, "lon": -89.5},
    "WY": {"name": "Wyoming", "lat": 43.0759, "lon": -107.2903},
}

# Script directory and output file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_CSV = os.path.join(
    SCRIPT_DIR, f"openweather_bad_weather_counts_{YEAR}_all_states.csv"
)

# ====================================================
# Helper functions
# ====================================================

def daterange(start: date, end: date):
    """Yield each date from start through end inclusive."""
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def get_numeric(value) -> float:
    """
    Safely extract a numeric value.

    Handles:
      - None
      - int or float
      - dict with 'speed' or any numeric value
      - strings that can be parsed to float
    """
    if value is None:
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, dict):
        if "speed" in value and isinstance(value["speed"], (int, float)):
            return float(value["speed"])
        for v in value.values():
            if isinstance(v, (int, float)):
                return float(v)
        return 0.0

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def classify_weather(summary: dict) -> tuple[bool, bool, bool]:
    """
    Classify one day as:
      precip_bad: precip total ≥ PRECIP_THRESHOLD_MM
      wind_bad: wind max ≥ WIND_MAX_THRESHOLD_MS
      bad_weather: precip_bad or wind_bad
    """
    precip = summary.get("precipitation") or {}
    wind = summary.get("wind") or {}

    precip_total = get_numeric(precip.get("total"))
    wind_max = get_numeric(wind.get("max"))

    precip_bad = precip_total >= PRECIP_THRESHOLD_MM
    wind_bad = wind_max >= WIND_MAX_THRESHOLD_MS
    bad_weather = precip_bad or wind_bad

    return precip_bad, wind_bad, bad_weather


def fetch_day_summary(lat: float, lon: float, d: date) -> dict | None:
    """Call OpenWeather day_summary endpoint for one date and location."""
    params = {
        "lat": lat,
        "lon": lon,
        "date": d.isoformat(),
        "appid": API_KEY,
        "units": "metric",
    }

    resp = requests.get(BASE_URL, params=params, timeout=30, verify=certifi.where())

    if resp.status_code == 429:
        raise RuntimeError("Received 429 rate limit from OpenWeather.")

    if resp.status_code == 401:
        raise RuntimeError("Unauthorized; check key or One Call subscription.")

    if resp.status_code != 200:
        print(f"Warning {d} status {resp.status_code}, body: {resp.text[:200]}")
        return None

    return resp.json()


def fetch_state_year_counts(state_code: str, info: dict, year: int) -> dict:
    """
    For one state, loop over all days in the year, classify weather,
    and return a dict with counts of each bad weather slice.
    """
    lat = info["lat"]
    lon = info["lon"]
    state_name = info["name"]

    print(f"\nFetching {year} summaries for {state_code} ({state_name})")

    total_days = 0
    bad_days_total = 0
    precip_bad_days = 0
    wind_bad_days = 0
    both_precip_and_wind_days = 0

    for d in daterange(START_DATE, END_DATE):
        try:
            data = fetch_day_summary(lat, lon, d)
        except RuntimeError as e:
            print(f"Stopping for {state_code} on {d}: {e}")
            break
        except Exception as e:
            print(f"Error {state_code} {d}: {e}")
            continue

        if not data:
            continue

        total_days += 1

        precip_bad, wind_bad, bad_weather = classify_weather(data)

        if bad_weather:
            bad_days_total += 1

        if precip_bad:
            precip_bad_days += 1

        if wind_bad:
            wind_bad_days += 1

        if precip_bad and wind_bad:
            both_precip_and_wind_days += 1

        # Small sleep to avoid hammering API
        time.sleep(0.2)

    print(
        f"{state_code} {year}: total_days={total_days}, "
        f"bad_days_total={bad_days_total}"
    )

    return {
        "state_code": state_code,
        "state_name": state_name,
        "year": year,
        "total_days": total_days,
        "bad_days_total": bad_days_total,
        "precip_bad_days": precip_bad_days,
        "wind_bad_days": wind_bad_days,
        "both_precip_and_wind_days": both_precip_and_wind_days,
    }


# ====================================================
# Main
# ====================================================

def main():
    rows: list[dict] = []

    # For testing you can slice the states:
    # for code in ["TX", "OK", "LA", "AR"]:
    #     info = US_STATE_COORDS[code]
    #     rows.append(fetch_state_year_counts(code, info, YEAR))
    #     continue

    for state_code, info in US_STATE_COORDS.items():
        summary_row = fetch_state_year_counts(state_code, info, YEAR)
        rows.append(summary_row)

    if not rows:
        print("No data collected; check key and configuration.")
        return

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nWrote {len(df)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
