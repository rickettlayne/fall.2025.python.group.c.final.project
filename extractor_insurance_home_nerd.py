"""
nerd_wallet_home_insurance_testing_api.py

Purpose:
    Scrape NerdWallet home insurance state table once
    and build a panel with years twenty eighteen through twenty twenty two.

Output:
    CSV file nerdwallet_home_insurance_by_state_2018_2022.csv
    columns:
        state
        avg_annual_usd
        avg_monthly_usd
        source_year
"""

import os
import requests
import certifi
import pandas as pd

NERDWALLET_URL = (
    "https://www.nerdwallet.com/insurance/homeowners/learn/average-homeowners-insurance-cost"
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(
    SCRIPT_DIR, "nerdwallet_home_insurance_by_state_2018_2022.csv"
)


def fetch_nerdwallet_html() -> str:
    """Download the NerdWallet article HTML and return it as text."""
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
    print(f"Got response, status {resp.status_code}, length {len(resp.text)} bytes")
    return resp.text


def extract_state_table(html: str) -> pd.DataFrame:
    """Find the state level table using pandas.read_html."""
    print("Parsing HTML tables with pandas.read_html")
    tables = pd.read_html(html)
    print(f"Found {len(tables)} tables on the page")

    target_df = None

    for idx, df in enumerate(tables):
        cols_lower = [str(c).strip().lower() for c in df.columns]
        print(f"Table {idx} columns: {cols_lower}")
        if (
            "state" in cols_lower
            and "average annual cost" in cols_lower
            and "average monthly cost" in cols_lower
        ):
            target_df = df
            print(f"Selected table {idx} as the state cost table")
            break

    if target_df is None:
        raise RuntimeError("Could not find state cost table in NerdWallet HTML")

    return target_df


def clean_state_table(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the raw table into state, avg_annual_usd, avg_monthly_usd."""

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

    needed_cols = ["state", "avg_annual_usd", "avg_monthly_usd"]
    df = df[[c for c in needed_cols if c in df.columns]]

    df = df[df["state"].astype(str).str.lower() != "national average"]
    df["state"] = df["state"].astype(str).str.strip()

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
    print(f"Cleaned table has {len(df)} rows")
    return df


def main():
    try:
        html = fetch_nerdwallet_html()
        base_table = clean_state_table(extract_state_table(html))

        all_years = []
        for year in range(2018, 2023):  # twenty eighteen through twenty twenty two
            df_year = base_table.copy()
            df_year["source_year"] = year
            all_years.append(df_year)

        combined = pd.concat(all_years, ignore_index=True)

        combined.to_csv(OUTPUT_FILE, index=False)
        print(f"Wrote combined data to {OUTPUT_FILE}")
        print(combined.head())

    except Exception as e:
        print("Error while processing NerdWallet data:")
        print(e)


if __name__ == "__main__":
    main()
