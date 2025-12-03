# extractor_insurance_car_naic.py
# Extracts auto insurance average premiums by state from the NAIC PDF
# Parses all tables and saves a single clean CSV into /data folder
# Format:
#   state, avg_2022, avg_2021, avg_2020, avg_2019, avg_2018

import requests
import io
import csv
import re
import os
from pypdf import PdfReader
import pandas as pd

# ---------------------------------------------------
# Locate project root and /data folder
# ---------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

os.makedirs(DATA_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(DATA_DIR, "naic_auto_insurance.csv")

# ---------------------------------------------------
# Download PDF and extract text
# ---------------------------------------------------
def extract_text_from_pdf_url(url):
    try:
        print(f"Downloading NAIC PDF from: {url}")
        response = requests.get(url)
        response.raise_for_status()

        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)

        print(f"PDF pages: {len(reader.pages)}")

        full_text = ""
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            print(f"Extracting Page {i+1}")
            full_text += text + "\n"

        return full_text

    except Exception as e:
        print(f"PDF extraction error: {e}")
        return None

# ---------------------------------------------------
# Parse all NAIC tables into rows
# Returns a list of dictionaries
# ---------------------------------------------------
def parse_naic_tables(text):
    print("Parsing NAIC tables...")

    # Match lines like:
    # Alabama 1123.45 1100.11 1023.22 999.00 876.12
    row_pattern = re.compile(
        r"^([A-Za-z\s\.]+?)\s+([\d,]+(?:\.\d+)?)\s+([\d,]+(?:\.\d+)?)\s+"
        r"([\d,]+(?:\.\d+)?)\s+([\d,]+(?:\.\d+)?)\s+([\d,]+(?:\.\d+)?)$"
    )

    rows = []

    for line in text.splitlines():
        line = line.strip()
        match = row_pattern.match(line)

        if match:
            state = match.group(1).strip()
            # Skip header rows
            if state.lower() == "state":
                continue

            nums = list(match.groups()[1:])
            nums = [value.replace(",", "") for value in nums]

            rows.append(
                {
                    "state": state,
                    "avg_2022": nums[0],
                    "avg_2021": nums[1],
                    "avg_2020": nums[2],
                    "avg_2019": nums[3],
                    "avg_2018": nums[4],
                }
            )

    print(f"Extracted {len(rows)} state rows from NAIC PDF.")
    return rows

# ---------------------------------------------------
# Save all rows into a single CSV file
# ---------------------------------------------------
def save_naic_csv(rows):
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved NAIC auto insurance data to: {OUTPUT_FILE}")
    print(df.head())

# ---------------------------------------------------
# Main Execution
# ---------------------------------------------------
if __name__ == "__main__":
    pdf_url = "https://content.naic.org/sites/default/files/aut-db.pdf"
    text = extract_text_from_pdf_url(pdf_url)

    if text:
        rows = parse_naic_tables(text)
        save_naic_csv(rows)
