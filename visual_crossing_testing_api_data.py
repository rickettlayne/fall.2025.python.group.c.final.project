import csv
import urllib.request
from urllib.error import URLError, HTTPError

# Set up the request parameters
base_url = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'
location = 'Washington,DC'  # Change to preferred location
api_key = 'MR9KG27BBP586WVSA4M5BV5U6'
start_date = "2022-01-01"
end_date = "2022-01-07"

unit_group = 'us'
content_type = 'csv'
include = 'days'

# Construct the full request URL
request_url = (f"{base_url}{location}/{start_date}/{end_date}"
               f"?unitGroup={unit_group}&contentType={content_type}&include={include}&key={api_key}")

try:
    # Make the API request
    response = urllib.request.urlopen(request_url)
    csv_data = response.read().decode('utf-8')
    response.close()

    # Save CSV to file
    output_file = "visualcrossing_weather_data.csv"
    with open(output_file, "w", encoding='utf-8') as f:
        f.write(csv_data)
    print(f"\n✅ CSV data saved to: {output_file}\n")

    # Optionally print a preview of the rows
    csv_reader = csv.reader(csv_data.splitlines(), delimiter=',')
    for i, row in enumerate(csv_reader):
        print(row)
        if i >= 9:
            break  # only show first 10 rows

except HTTPError as e:
    print(f'HTTP Error: {e.code} {e.reason}')
    print(e.read().decode('utf-8'))  # Read body to understand the error
except URLError as e:
    print(f'URL Error: {e.reason}')
