# extractor_weather_noaa.py
# Downloads NOAA Storm Events compiled "details" files
# for each year and saves a combined CSV into the project's /data folder.

import os
import requests
import pandas as pd
from io import BytesIO
import gzip
import re

# ---------------------------------------------------
# Locate the project root and DATA folder
# ---------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)         # one level up
DATA_DIR = os.path.join(PROJECT_ROOT, "data")       # /data folder

# Make sure the data folder exists
os.makedirs(DATA_DIR, exist_ok=True)

OUTPUT_FILENAME = "noaa_weather.csv"
OUTPUT_PATH = os.path.join(DATA_DIR, OUTPUT_FILENAME)

# ---------------------------------------------------
# NOAA Storm Events source
# ---------------------------------------------------
FTP_LIST_URL = "https://www1.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles/"
YEARS = [2018, 2019, 2020, 2021, 2022]

print("Fetching available NOAA files from:")
print(FTP_LIST_URL)

response_list = requests.get(FTP_LIST_URL)
if response_list.status_code != 200:
    print(f"Failed to access NOAA list page, status code: {response_list.status_code}")
    raise SystemExit(1)

ftp_html = response_list.text
all_dfs = []

# ---------------------------------------------------
# Download each year's compiled "details" file
# ---------------------------------------------------
for year in YEARS:
    print(f"\nLooking for compiled StormEvents file for year {year}")

    pattern = rf"StormEvents_details-ftp_v1\.0_d{year}_c\d+\.csv\.gz"
    matches = re.findall(pattern, ftp_html)

    if not matches:
        print(f"Could not find compiled file for {year}, skipping.")
        continue

    filename = matches[-1]  # latest compiled version
    file_url = FTP_LIST_URL + filename

    print(f"Downloading: {file_url}")
    response_data = requests.get(file_url)

    if response_data.status_code != 200:
        print(f"Failed to download file for {year}. Status: {response_data.status_code}")
        continue

    with gzip.open(BytesIO(response_data.content), mode="rt") as f:
        df_year = pd.read_csv(f)

    df_year["YEAR"] = year
    print(f"Loaded {len(df_year)} rows")
    all_dfs.append(df_year)

# ---------------------------------------------------
# Combine and save to /data/noaa_weather.csv
# ---------------------------------------------------
if not all_dfs:
    print("No datasets were downloaded. Exiting.")
    raise SystemExit(1)

combined_df = pd.concat(all_dfs, ignore_index=True)

print("\nSaving combined NOAA data to:")
print(OUTPUT_PATH)
combined_df.to_csv(OUTPUT_PATH, index=False)

print(f"Done. Saved {len(combined_df)} rows to {OUTPUT_PATH}")
