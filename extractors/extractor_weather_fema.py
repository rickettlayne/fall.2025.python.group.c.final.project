# extractor_weather_fema.py
# This script fetches weather disaster data from the FEMA API,
# processes it into a pandas DataFrame, and saves it as a CSV file.
# The script also prints the column names and the first 10 rows of the dataset.
# The FEMA API provides open access to disaster declaration summaries.
# The output CSV file is named 'fema_disaster_declarations.csv'.

import requests
import pandas as pd

# FEMA API endpoint (open access)
url = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"

# Parameters: limit to first 100000 records and request JSON format
params = {
    "$top": 100000,
    "$format": "json"
}

# Fetch data from FEMA API
# Process the JSON response into a pandas DataFrame
# Print column names and first 10 rows
# Save the full dataset to a CSV file

try:
    print("Fetching FEMA Disaster Declarations Summary data...")
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data["DisasterDeclarationsSummaries"])

        # Print column names
        print("\nColumn Names:")
        for col in df.columns:
            print(col)

        # Print first 10 rows
        print("\nFirst 10 Rows:")
        print(df.head(10))

        # Save full dataset to CSV
        df.to_csv("fema_disaster_declarations.csv", index=False)
        print("\nData saved to 'fema_disaster_declarations.csv'")

    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

# Handle exceptions during the request
# Print error message on failure
# Save the dataset only on successful fetch
# Catch any other exceptions and print error message
# This ensures robust error handling during data extraction


except Exception as e:
    print(f"An error occurred: {e}")
