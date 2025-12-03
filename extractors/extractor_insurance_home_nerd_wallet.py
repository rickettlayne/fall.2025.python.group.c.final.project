# extractor_insurance_home_nerd.py
# Scrapes NerdWallet's home insurance table, cleans the data,
# generates year panels (2018-2022), and saves output to /data folder.

import os
import requests
import certifi
import pandas as pd

# ---------------------------------------------------
# Locate project root and /data folder
# ---------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# Ensure /data exists
os.makedirs(DATA_DIR, exist_ok=True)

# Output CSV file
OUTPUT_FILE = os.path.join(DATA_DIR, "nerdwallet_home.csv")

# NerdWallet article URL
NERDWALLET_URL = (
    "https://www.nerdwallet.com/insurance/homeowners/learn/average-homeowners-insurance-cost"
)

# ---------------------------------------------------
# Download HTML from NerdWallet
# ---------------------------------------------------
def fetch_nerdwallet_html() -> str:
    """Download the NerdWallet HTML article as text."""

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    print(f"Requesting NerdWallet page: {NERDWALLET_URL}")
    resp = requests.get(
        NERDWALLET_URL,
        headers=headers,
        timeout=60,
        verify=certifi.where(),
    )
    resp.raise_for_status()

    print(f"Got response: status {resp.status_code}, HTML size {len(resp.text)} bytes")
    return resp.text

# ---------------------------------------------------
# Extract the state-level table from the HTML
# ---------------------------------------------------
def extract_state_table(html: str) -> pd.DataFrame:
    """Extract state cost table using pandas.read_html."""
    print("Parsing HTML tables with pandas.read_html()...")
    tables = pd.read_html(html)
    print(f"Found {len(tables)} tables in the article")

    target_df = None

    for idx, df in enumerate(tables):
        cols = [str(c).strip().lower() for c in df.columns]
        print(f"Table {idx} columns: {cols}")

        if (
            "state" in cols
            and "average annual cost" in cols
            and "average monthly cost" in cols
        ):
            target_df = df
            print(f"Identified table {idx} as the state-level cost table")
            break

    if target_df is None:
        raise RuntimeError("Could not locate NerdWallet state table")

    return target_df

# ---------------------------------------------------
# Clean the extracted table into uniform column names
# ---------------------------------------------------
def clean_state_table(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize the state table columns."""

    rename_map = {}
    for col in df.columns:
        col_lower = str(col).strip().lower()

        if col_lower == "state":
            rename_map[col] = "state"
        elif "average annual" in col_lower:
            rename_map[col] = "avg_annual_usd"
        elif "average monthly" in col_lower:
            rename_map[col] = "avg_monthly_usd"

    df = df.rename(columns=rename_map)

    needed = ["state", "avg_annual_usd", "avg_monthly_usd"]
    df = df[[c for c in needed if c in df.columns]]

    # Remove nationwide averages
    df = df[df["state"].astype(str).str.lower() != "national average"]

    # Clean numeric fields
    for col in ["avg_annual_usd", "avg_monthly_usd"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r"[\$,]", "", regex=True)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["state"]).reset_index(drop=True)
    print(f"Cleaned table contains {len(df)} rows")

    return df

# ---------------------------------------------------
# Main logic
# ---------------------------------------------------
def main():
    try:
        html = fetch_nerdwallet_html()
        base_table = clean_state_table(extract_state_table(html))

        all_years = []
        for year in range(2018, 2023):  # 2018 through 2022
            df_year = base_table.copy()
            df_year["source_year"] = year
            all_years.append(df_year)

        combined = pd.concat(all_years, ignore_index=True)

        combined.to_csv(OUTPUT_FILE, index=False)
        print(f"\nSaved NerdWallet home insurance data to: {OUTPUT_FILE}")
        print(combined.head())

    except Exception as e:
        print("\nError while processing NerdWallet data:")
        print(e)

# ---------------------------------------------------
# Execute
# ---------------------------------------------------
if __name__ == "__main__":
    main()
