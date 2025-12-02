# extractor_weather_noaa.py
# This script downloads the compiled NOAA Storm Events "details" file
# for each year from 2018 through 2022, combines them into one DataFrame,
# and saves a single CSV file in the same folder as this script.

import os
import requests
import pandas as pd
from io import BytesIO
import gzip
import re

# Determine the folder where this script lives
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Name of the combined output CSV file
OUTPUT_FILENAME = "noaa_storm_events_2018_2022_full.csv"
OUTPUT_PATH = os.path.join(SCRIPT_DIR, OUTPUT_FILENAME)

# Base URL that lists all StormEvents CSV and gzip files
FTP_LIST_URL = "https://www1.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles/"

# List of years we want to pull
YEARS = [2018, 2019, 2020, 2021, 2022]

print("Fetching available NOAA files from:")
print(FTP_LIST_URL)

# Request the HTML file listing from the NOAA directory
response_list = requests.get(FTP_LIST_URL)
if response_list.status_code != 200:
    print(f"Failed to access NOAA list page, status code: {response_list.status_code}")
    raise SystemExit(1)

ftp_html = response_list.text

all_dfs = []

# Loop through each target year and download the corresponding compiled file
for year in YEARS:
    print(f"\nLooking for compiled StormEvents details file for year {year}")

    # Pattern for the compiled "details" file for this year
    # Example file name:
    # StormEvents_details-ftp_v1.0_d2018_c20230119.csv.gz
    pattern = rf"StormEvents_details-ftp_v1\.0_d{year}_c\d+\.csv\.gz"

    matches = re.findall(pattern, ftp_html)
    if not matches:
        print(f"Could not find the compiled file for {year} in NOAA archive, skipping this year.")
        continue

    # It is safer to take the last match which is usually the latest compiled file
    filename = matches[-1]
    file_url = FTP_LIST_URL + filename

    print(f"Found file: {filename}")
    print(f"Downloading from: {file_url}")

    response_data = requests.get(file_url)
    if response_data.status_code != 200:
        print(f"Failed to download file for {year}. Status code: {response_data.status_code}")
        continue

    # Decompress the gzip content and read into a DataFrame
    with gzip.open(BytesIO(response_data.content), mode="rt") as f:
        df_year = pd.read_csv(f)

    # Add a Year column so you can keep track of which year each row belongs to
    df_year["YEAR"] = year

    print(f"Loaded {len(df_year)} rows for year {year}")
    all_dfs.append(df_year)

# After the loop, check if we collected any data
if not all_dfs:
    print("No data frames were created for any year. Exiting.")
    raise SystemExit(1)

# Concatenate all yearly DataFrames into one combined DataFrame
combined_df = pd.concat(all_dfs, ignore_index=True)

# Print column names and a sample of rows for a quick check
print("\nColumn Names:")
for col in combined_df.columns:
    print(col)

print("\nFirst 10 rows of combined data:")
print(combined_df.head(10))

# Save the combined DataFrame to a CSV in the same folder as this script
combined_df.to_csv(OUTPUT_PATH, index=False)
print(f"\nCombined data for years {YEARS} saved to '{OUTPUT_PATH}'")
