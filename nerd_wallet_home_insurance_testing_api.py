import requests
import pandas as pd
from bs4 import BeautifulSoup

url = "https://www.nerdwallet.com/best/insurance/homeowners/home-insurance-rates"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/16.4 Safari/605.1.15"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com"
}

response = requests.get(url, headers=headers)

print("Status code:", response.status_code)
print("Final URL:", response.url)

if response.status_code != 200:
    print(response.text[:1000])
    raise SystemExit("Server did not return 200, scraping blocked")
