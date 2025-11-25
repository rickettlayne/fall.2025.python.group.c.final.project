

import requests
import pandas as pd
from bs4 import BeautifulSoup

url = "https://www.nerdwallet.com/best/insurance/homeowners/home-insurance-rates"

# Spoof a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# Find all tables
tables = pd.read_html(str(soup))

print(f"✅ Found {len(tables)} tables.")

# Preview and save the likely correct one
for i, table in enumerate(tables):
    print(f"\nTable {i} preview:")
    print(table.head())

# Save the first (or appropriate) table
if tables:
    df = tables[0]
    df.to_csv("nerdwallet_home_insurance.csv", index=False)
    print("\n✅ Table saved as 'nerdwallet_home_insurance.csv'")
else:
    print("❌ No tables found.")
