import requests
import certifi
import time
import pandas as pd
import os
from calendar import monthrange, month_name

API_KEY = "MR9KG27BBP586WVSA4M5BV5U6"
BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"

STATE_CODE = "TX"
STATE_NAME = "Texas"

# We want 2018 through 2022 in the end
START_YEAR = 2018
END_YEAR = 2022

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "visualcrossing_bad_weather_TX_2018_2022_simple.csv")

PRECIP_THRESHOLD_IN = 1.0
WIND_THRESHOLD_MPH = 30.0
INCLUDE_CONDITION_WORDS = ("Rain", "Snow", "Storm", "Sleet")


def is_bad_weather(day: dict) -> bool:
    precip = float(day.get("precip", 0.0) or 0.0)
    snow = float(day.get("snow", 0.0) or 0.0)
    windspeed = float(day.get("windspeed", 0.0) or 0.0)
    conditions = str(day.get("conditions", "") or "")

    if precip >= PRECIP_THRESHOLD_IN:
        return True
    if snow > 0:
        return True
    if windspeed >= WIND_THRESHOLD_MPH:
        return True
    if any(word in conditions for word in INCLUDE_CONDITION_WORDS):
        return True

    return False


def load_processed_months() -> set[tuple[int, str]]:
    """Read existing CSV and return set of (year, month_name) that already exist."""
    processed = set()

    if not os.path.exists(OUTPUT_FILE):
        print("No existing CSV found, starting fresh")
        return processed

    print(f"Loading existing data from {OUTPUT_FILE}")
    df = pd.read_csv(OUTPUT_FILE)
    if "year" not in df.columns or "month" not in df.columns:
        print("Existing CSV does not have expected columns year and month, ignoring it")
        return processed

    for _, row in df.iterrows():
        try:
            y = int(row["year"])
            m = str(row["month"])
            processed.add((y, m))
        except Exception:
            continue

    print(f"Already have {len(processed)} year month combinations")
    return processed


def fetch_state_month(year: int, month: int) -> list[dict]:
    _, last_day = monthrange(year, month)
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{last_day:02d}"

    location = f"{STATE_NAME},US"

    params = {
        "unitGroup": "us",
        "key": API_KEY,
        "include": "days",
        "contentType": "json",
        "elements": "datetime,precip,snow,windspeed,conditions",
    }

    url = f"{BASE_URL}/{location}/{start_date}/{end_date}"

    print(f"Calling API for year {year}, month {month} ({start_date} to {end_date})")
    resp = requests.get(url, params=params, timeout=60, verify=certifi.where())

    if resp.status_code == 429:
        print(f"API limit reached for year {year}, month {month}, status 429")
        return []
    if resp.status_code != 200:
        print(f"API error {resp.status_code} for year {year}, month {month}")
        print(resp.text[:300])
        return []

    data = resp.json()
    days = data.get("days", [])

    rows: list[dict] = []
    for day in days:
        if not is_bad_weather(day):
            continue

        date_str = day.get("datetime")
        if not date_str:
            continue

        year_val = int(date_str[0:4])
        month_num = int(date_str[5:7])
        month_str = month_name[month_num]

        rows.append(
            {
                "year": year_val,
                "month": month_str,
                "state": STATE_CODE,
                "weather_type": day.get("conditions"),
            }
        )

    print(f"Year {year}, month {month}: {len(rows)} bad weather days")
    return rows


def write_rows_to_csv(rows: list[dict]) -> None:
    if not rows:
        return

    df = pd.DataFrame(rows)
    file_exists = os.path.exists(OUTPUT_FILE)

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        mode="a" if file_exists else "w",
        header=not file_exists,
    )
    print(f"Wrote {len(rows)} rows to {OUTPUT_FILE}")


def main():
    print("Starting Visual Crossing run for Texas")
    processed = load_processed_months()

    for year in range(START_YEAR, END_YEAR + 1):
        for month in range(1, 13):
            month_str = month_name[month]
            key = (year, month_str)

            if key in processed:
                print(f"Skipping {year} {month_str}, already in CSV")
                continue

            rows = fetch_state_month(year, month)

            if not rows:
                print(f"Stopping after year {year}, month {month_str} because there were no rows")
                print("Most likely hit API daily cost limit")
                return

            write_rows_to_csv(rows)
            processed.add(key)

            time.sleep(1)

    print("Finished script successfully, all months processed")


if __name__ == "__main__":
    main()
