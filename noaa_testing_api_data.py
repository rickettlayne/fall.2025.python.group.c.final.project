import requests
import pandas as pd
from io import BytesIO
import gzip
import re

# Step 1: Get file list from NOAA FTP directory
ftp_list_url = "https://www1.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles/"
print("Fetching available NOAA files...")
ftp_html = requests.get(ftp_list_url).text

# Step 2: Find the latest compiled 2022 file
pattern = r"StormEvents_details-ftp_v1\.0_d2022_c\d+\.csv\.gz"
matches = re.findall(pattern, ftp_html)

if not matches:
    print("Could not find the 2022 storm events file in NOAA archive.")
else:
    filename = matches[0]
    file_url = ftp_list_url + filename
    print(f"Downloading: {filename}")

    # Step 3: Download and decompress the .gz file
    response = requests.get(file_url)
    if response.status_code == 200:
        with gzip.open(BytesIO(response.content), mode='rt') as f:
            df = pd.read_csv(f)

        # Step 4: Print column names and first 10 rows
        print("\nColumn Names:")
        for col in df.columns:
            print(col)

        print("\nFirst 10 Rows:")
        print(df.head(10))

        # Step 5: Save to CSV
        df.to_csv("noaa_storm_events_2022_full.csv", index=False)
        print("\nData saved to 'noaa_storm_events_2022_full.csv'")

    else:
        print(f"Failed to download file. Status code: {response.status_code}")
