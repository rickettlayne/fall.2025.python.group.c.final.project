"""
NAIC Auto Insurance Data Summary (2018 to 2022)

This dataset provides state-level averages for private passenger auto insurance.
It includes the voluntary and residual markets and focuses on three major coverage types:
liability, collision, and comprehensive.

Liability Coverage:
    Source: Table 1
    Includes Bodily Injury, Property Damage, Uninsured or Underinsured Motorist,
    Medical Payments, PIP, and similar coverages.
    Liability Average Premium = Liability Written Premiums / Liability Written Exposures
    Exposures represent car-years of risk.

Collision Coverage:
    Source: Table 2
    Collision Average Premium = Collision Written Premiums / Collision Written Exposures

Comprehensive Coverage:
    Source: Table 3
    Comprehensive Average Premium = Comprehensive Written Premiums / Comprehensive Written Exposures

Combined Average Premium:
    Source: Table 5
    Represents the total average cost of a full auto policy.
    Combined Premium = Liability Avg + Collision Avg + Comprehensive Avg
    Example: 2022 countrywide combined average was 1258 dollars.

Average Expenditure:
    Source: Table 4
    Measures what consumers actually spent on average in each state.
    Average Expenditure = (Liability + Collision + Comprehensive Written Premiums) 
                          / Liability Written Exposures
    Example: 2022 countrywide average expenditure was 1126 dollars.

Notes:
    Premiums and expenditures are based on aggregate written premiums and exposures.
    The values do not account for policyholder differences, vehicle type, selected limits,
    deductibles, or individual risk factors. Differences in state laws, accident rates,
    traffic density, repair costs, and legal environments strongly influence results.
"""


import requests
import io
import csv
import re
from pypdf import PdfReader

def extract_text_from_pdf_url(url):
    try:
        print(f"Downloading PDF from: {url}")
        response = requests.get(url)
        response.raise_for_status()
        
        print("Download complete. Extracting text...")
        
        # Create a file-like object from the response content
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

def parse_and_save_tables(text):
    print("Parsing text for tables...")
    
    # Regex for table start, e.g., "Table 1", "Table 3C"
    table_start_pattern = re.compile(r"^Table\s+\d+[A-Z]*$")
    # Regex for data rows (State + 5 numbers with optional decimals)
    data_pattern = re.compile(r"^([A-Za-z\s\.]+?)\s+([\d,]+(?:\.\d{2})?)\s+([\d,]+(?:\.\d{2})?)\s+([\d,]+(?:\.\d{2})?)\s+([\d,]+(?:\.\d{2})?)\s+([\d,]+(?:\.\d{2})?)$")
    
    lines = text.split('\n')
    
    current_table_name = None
    current_rows = []
    # Buffer for data rows that appear before a table header
    buffered_rows = []
    # We'll use a simple state machine
    # 0: Looking for Table start or data
    # 1: Found Table start, looking for Name
    # 2: Found Name, reading rows
    state = 0
    
    # Buffer to help find the table name (it's usually 1-2 lines after Table X)
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
            
            # Check if we have buffered rows (data that appeared before this table header)
            if buffered_rows:
                current_rows = buffered_rows
                buffered_rows = []
            else:
                current_rows = []
            
            # Reset for new table
            current_table_name = None
            state = 1
            lines_since_table_start = 0
            continue
            
        if state == 0:
            # In state 0, we're looking for either a table start or data rows
            # If we find data rows before a table header, buffer them
            match = data_pattern.match(line)
            if match:
                state_name = match.group(1).strip()
                # Skip if this is actually a STATE header row (e.g., "STATE 2022 2021 2020...")
                if state_name.upper() == "STATE":
                    buffered_rows = []
                    continue
                row = [state_name] + list(match.groups()[1:])
                buffered_rows.append(row)
            elif line.startswith("STATE"):
                # Clear buffer when we see a STATE header (start of a new data section)
                buffered_rows = []
            continue
            
        if state == 1:
            lines_since_table_start += 1
            # usually the line after "Table X" is "Average Premiums..."
            # and the line after THAT is the table name.
            # But sometimes it might be different. 
            # Let's assume the table name is the line that is NOT "Average Premiums..." and NOT "STATE ..."
            
            if "Average Premiums" in line:
                continue
            if line.startswith("STATE"):
                # We missed the name or it wasn't there, start reading rows
                state = 2
                continue
            
            # This line is likely the table name
            current_table_name = line
            state = 2
            continue
            
        if state == 2:
            # Check if we hit a new STATE header - this might indicate a new table section
            if line.startswith("STATE") and current_rows:
                # We already have data, so this STATE header might be for a new table
                # Save current table and go back to state 0 to buffer the new data
                if current_table_name:
                    save_table(current_table_name, current_rows)
                current_table_name = None
                current_rows = []
                buffered_rows = []
                state = 0
                continue
            
            # Check for data row
            match = data_pattern.match(line)
            if match:
                state_name = match.group(1).strip()
                # Skip if this is actually a STATE header row (e.g., "STATE 2022 2021 2020...")
                if state_name.upper() == "STATE":
                    continue
                # Filter out "Countrywide" if it's not desired, but user didn't say to remove it.
                # The user said "Only extract the datatables".
                row = [state_name] + list(match.groups()[1:])
                current_rows.append(row)
            elif line.startswith("STATE"):
                # Just a header repetition at the start, ignore
                continue
            elif "©" in line:
                # Footer, ignore
                continue
            # If we hit something that looks like a table start, the loop top will catch it.

    # Save the last table if exists
    if current_table_name and current_rows:
        save_table(current_table_name, current_rows)

def save_table(table_name, rows):
    # Clean filename
    safe_name = re.sub(r'[^\w\s-]', '', table_name).strip().replace(' ', '_')
    filename = f"{safe_name}.csv"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['State', '2022', '2021', '2020', '2019', '2018'])
            writer.writerows(rows)
        print(f"Saved {len(rows)} rows to '{filename}' (Table: {table_name})")
    except Exception as e:
        print(f"Error saving {filename}: {e}")

if __name__ == "__main__":
    pdf_url = "https://content.naic.org/sites/default/files/aut-db.pdf"
    text = extract_text_from_pdf_url(pdf_url)
    if text:
        parse_and_save_tables(text)
