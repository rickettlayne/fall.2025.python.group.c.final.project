# extractor_weather_fema.py
# Fetches disaster declaration data from FEMA API and saves the
# full dataset into the project's /data folder for use in Django.

import os
import requests
import pandas as pd

# ---------------------------------------------------
# Locate the project root and /data folder
# ---------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)        # one level up
DATA_DIR = os.path.join(PROJECT_ROOT, "data")      # project_root/data

# Make sure /data exists
os.makedirs(DATA_DIR, exist_ok=True)

# Output filename
OUTPUT_FILENAME = "fema_weather.csv"
OUTPUT_PATH = os.path.join(DATA_DIR, OUTPUT_FILENAME)

# ---------------------------------------------------
# FEMA API endpoint
# ---------------------------------------------------
url = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"

params = {
    "$top": 100000,
    "$format": "json"
}

print("Fetching FEMA Disaster Declarations Summary data...")

try:
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        raise SystemExit(1)

    # Parse JSON
    data = response.json()
    df = pd.DataFrame(data["DisasterDeclarationsSummaries"])

    # Print columns for debugging
    print("\nColumn Names:")
    for col in df.columns:
        print(col)

    # Print sample rows
    print("\nFirst 10 Rows:")
    print(df.head(10))

    # Save dataset to /data folder
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"\nFEMA data saved to '{OUTPUT_PATH}'")

except Exception as e:
    print(f"An error occurred: {e}")
