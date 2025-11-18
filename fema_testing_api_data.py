import requests
import pandas as pd

# FEMA API endpoint (open access)
url = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"

# Parameters: limit to first 1000 records and request JSON format
params = {
    "$top": 1000,
    "$format": "json"
}

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
        df.to_csv("fema_disaster_declarations_sample.csv", index=False)
        print("\nData saved to 'fema_disaster_declarations_sample.csv'")

    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

except Exception as e:
    print(f"An error occurred: {e}")
