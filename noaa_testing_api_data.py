import requests
import pandas as pd
from io import BytesIO
import gzip
import re

ftp_list_url = "https://www1.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles/"
print("Fetching available NOAA files...")
ftp_html = requests.get(ftp_list_url).text

# Years you want to download and merge
years_to_fetch = [2023, 2024, 2025]

combined_df = []  # list to hold dataframes

for year in years_to_fetch:
    print(f"\nLooking for Storm Events file for year {year}...")

    # Pattern for that year
    pattern = fr"StormEvents_details-ftp_v1\.0_d{year}_c\d+\.csv\.gz"
    matches = re.findall(pattern, ftp_html)

    if not matches:
        print(f"No compiled Storm Events file found for {year}")
        continue

    # If multiple files exist, take the latest one
    filename = sorted(matches)[-1]
    file_url = ftp_list_url + filename

    print(f"Downloading: {filename}")
    response = requests.get(file_url)
    if response.status_code != 200:
        print(f"Failed to download file for {year}. Status code: {response.status_code}")
        continue

    # Decompress into pandas
    with gzip.open(BytesIO(response.content), mode="rt") as f:
        df = pd.read_csv(f)

    print(f"Downloaded {len(df)} rows for {year}")

    # Add a Year column to keep track
    df["EventYear"] = year
    
    combined_df.append(df)

# Combine all available years
if combined_df:
    final_df = pd.concat(combined_df, ignore_index=True)
    output_name = "noaa_storm_events_2023_2025_combined.csv"
    final_df.to_csv(output_name, index=False)
    print(f"\nMerged file created: {output_name}")
    print(f"Total rows: {len(final_df)}")
else:
    print("No data downloaded for any of the years listed.")
