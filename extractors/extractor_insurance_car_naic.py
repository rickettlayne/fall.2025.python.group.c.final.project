# extractor_insurance_car_naic.py
# This script downloads a PDF from the NAIC website, extracts text,
# parses tables of average car insurance premiums by state and year,
# and saves each table as a separate CSV file.
# Each table is saved in the same folder as this script.


import requests
import io
import csv
import re
import os
from pypdf import PdfReader

# Folder where this script lives

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Function to download PDF and extract text
# from a given URL
# Returns the extracted text as a string
# or None on failure

def extract_text_from_pdf_url(url):
    try:
        print(f"Downloading PDF from: {url}")
        response = requests.get(url)
        response.raise_for_status()
        
        print("Download complete. Extracting text...")
        
        # Create a file like object from the response content
        pdf_file = io.BytesIO(response.content)
        
        # Create a PDF reader object
        reader = PdfReader(pdf_file)
        
        print(f"Number of pages: {len(reader.pages)}")
        
        full_text = ""
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            print(f"--- Page {i+1} ---")
            print(text)
            full_text += text + "\n"
            
        return full_text

    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF: {e}")
        return None
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None

# Function to parse extracted text and save tables as CSV files
# Each table is saved in the same folder as this script
# The CSV filename is derived from the table name
# The function handles multiple tables in the text
# Each table contains state names and average premiums for years 2018-2022


def parse_and_save_tables(text):
    print("Parsing text for tables...")
    
    # Regex for table start, for example "Table 1", "Table 3C"
    table_start_pattern = re.compile(r"^Table\s+\d+[A-Z]*$")
    # Regex for data rows (State plus five numbers with optional decimals)
    data_pattern = re.compile(
        r"^([A-Za-z\s\.]+?)\s+([\d,]+(?:\.\d{2})?)\s+([\d,]+(?:\.\d{2})?)\s+"
        r"([\d,]+(?:\.\d{2})?)\s+([\d,]+(?:\.\d{2})?)\s+([\d,]+(?:\.\d{2})?)$"
    )
    
    lines = text.split('\n')
    
    current_table_name = None
    current_rows = []
    buffered_rows = []
    state = 0  # 0 looking, 1 just saw "Table X", 2 reading rows
    lines_since_table_start = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for new table start
        if table_start_pattern.match(line):
            # If we were already reading a table, save it
            if current_table_name and current_rows:
                save_table(current_table_name, current_rows)
            
            # Check if we have buffered rows
            if buffered_rows:
                current_rows = buffered_rows
                buffered_rows = []
            else:
                current_rows = []
            
            current_table_name = None
            state = 1
            lines_since_table_start = 0
            continue
            
        if state == 0:
            # Looking for table start or data rows
            match = data_pattern.match(line)
            if match:
                state_name = match.group(1).strip()
                # Skip header row
                if state_name.upper() == "STATE":
                    buffered_rows = []
                    continue
                row = [state_name] + list(match.groups()[1:])
                buffered_rows.append(row)
            elif line.startswith("STATE"):
                buffered_rows = []
            continue
            
        if state == 1:
            lines_since_table_start += 1
            
            if "Average Premiums" in line:
                continue
            if line.startswith("STATE"):
                state = 2
                continue
            
            # This line is likely the table name
            current_table_name = line
            state = 2
            continue
            
        if state == 2:
            if line.startswith("STATE") and current_rows:
                # New section; save current table
                if current_table_name:
                    save_table(current_table_name, current_rows)
                current_table_name = None
                current_rows = []
                buffered_rows = []
                state = 0
                continue
            
            match = data_pattern.match(line)
            if match:
                state_name = match.group(1).strip()
                if state_name.upper() == "STATE":
                    continue
                row = [state_name] + list(match.groups()[1:])
                current_rows.append(row)
            elif line.startswith("STATE"):
                continue
            elif "©" in line:
                continue

    # Save the last table if it exists
    if current_table_name and current_rows:
        save_table(current_table_name, current_rows)

# Function to save a table to CSV
# The CSV file is saved in the same folder as this script
# The filename is derived from the table name

def save_table(table_name, rows):
    # Clean filename
    safe_name = re.sub(r'[^\w\s-]', '', table_name).strip().replace(' ', '_')
    filename_only = f"{safe_name}.csv"
    
    # Build full path in same folder as this script
    full_path = os.path.join(SCRIPT_DIR, filename_only)
    
    try:
        with open(full_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['State', '2022', '2021', '2020', '2019', '2018'])
            writer.writerows(rows)
        print(f"Saved {len(rows)} rows to '{full_path}' (Table: {table_name})")
    except Exception as e:
        print(f"Error saving {full_path}: {e}")

# Main execution
# Download PDF, extract text, parse tables, and save as CSV
# Each table is saved in the same folder as this script
# The CSV filename is derived from the table name
# The function handles multiple tables in the text
# Each table contains state names and average premiums for years 2018-2022
# Run this script directly to perform the extraction and saving

if __name__ == "__main__":
    pdf_url = "https://content.naic.org/sites/default/files/aut-db.pdf"
    text = extract_text_from_pdf_url(pdf_url)
    if text:
        parse_and_save_tables(text)
