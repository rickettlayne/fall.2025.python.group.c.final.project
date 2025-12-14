Weather and Insurance Risk Dashboard
===================================

This project is a Django based interactive dashboard that analyzes the relationship between
U.S. insurance premiums and federally declared disaster activity. The application supports
both Auto and Home insurance views and integrates FEMA disaster data to compute a composite
risk score by state.

The dashboard is designed to help users understand how insurance costs vary by geography,
time, and disaster exposure.

--------------------------------------------------
Key Features
--------------------------------------------------

• Auto insurance analysis with multi year trends from 2018 through 2022  
• Home insurance analysis as a single year national snapshot  
• FEMA disaster integration by state and year  
• Composite risk score combining premium pressure and disaster frequency  
• Interactive filters for insurance type, state, and year  
• Choropleth map visualizing relative risk by state  
• Indexed trend charts for fair comparison over time  

--------------------------------------------------
Project Structure
--------------------------------------------------

fall.2025.python.group.c.final.project/
│
├── manage.py
├── requirements.txt
├── run_all_extractors.py
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── dashboard/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── tests.py
│   └── home.html
│
├── extractors/
│   ├── extractor_weather_noaa.py
│   ├── extractor_weather_fema.py
│   ├── extractor_insurance_car_naic.py
│   └── extractor_insurance_home_nerd_wallet.py
│
├── utils/
│   ├── clean_home_insurance.py
│   ├── state_mapping.py
│   ├── time_normalization.py
│   └── value_normalization.py
│
├── data/
│   ├── clean_naic_auto_insurance.csv
│   ├── clean_nerdwallet_home.csv
│   ├── clean_fema_weather.csv
│   ├── clean_noaa_weather.csv
│   ├── naic_auto_insurance.csv
│   ├── nerdwallet_home.csv
│   ├── fema_weather.csv
│   └── noaa_weather.csv
│
├── archive_files/
│
└── project overview/

--------------------------------------------------
Data Overview
--------------------------------------------------

Auto Insurance
• Source: NAIC
• Coverage: 2018 through 2022
• Used for trend analysis and premium indexing

Home Insurance
• Source: NerdWallet
• Coverage: Single year national snapshot
• Displayed as current year reference only

FEMA Disaster Data
• Source: FEMA Disaster Declarations
• Used to compute annual disaster frequency by state
• Combined with premium index to calculate composite risk score

--------------------------------------------------
Risk Score Methodology
--------------------------------------------------

Risk Score = 0.6 × Premium Index + 0.4 × Disaster Index

• Premium Index compares a state's average premium to the national average
• Disaster Index compares a state's disaster frequency to the national average
• A score above 1.00 indicates above average risk

--------------------------------------------------
Quickstart Demo (Recommended)
--------------------------------------------------

This project is a Django-based interactive dashboard that analyzes U.S. insurance premiums
and federally declared disaster activity.

The demo script runs the full flow:
A) (If needed) Download/refresh raw datasets (extractors)
B) (If needed) Generate cleaned datasets (clean_all_data.py) used by the dashboard
C) Run Django migrations
D) Start the Django server

Then open:
http://127.0.0.1:8000

--------------------------------------------------
QuickStart Demo Setup (Cross-Platform, No Activation Required)
--------------------------------------------------

Recommended: use the "no activation" commands below to avoid OS/shell differences.

Windows note: If `py` is not available, use `python` instead.

1) Create a virtual environment

macOS / Linux
python3 -m venv .venv

Windows (PowerShell)
py -m venv .venv

2) Install dependencies (no activation required)

macOS / Linux
./.venv/bin/python -m pip install -r requirements.txt

Windows (PowerShell)
.\.venv\Scripts\python -m pip install -r requirements.txt

3) Run the demo (no activation required)

macOS / Linux
./.venv/bin/python demo.py

Windows (PowerShell)
.\.venv\Scripts\python demo.py

Then open:
http://127.0.0.1:8000
--------------------------------------------------
Demo Options
--------------------------------------------------

Fast mode (default)
- If cleaned files already exist in /data (clean_*.csv), demo.py will skip re-scraping and run quickly.

Force refresh (slow, downloads data again)
- Use this if you want the newest datasets or if you are running for the first time.

macOS / Linux
./.venv/bin/python demo.py --refresh

Windows (PowerShell)
.\.venv\Scripts\python demo.py --refresh

Offline mode (no downloads)
- Use this if you are offline or the data sources are unavailable.
- Requires local data to already exist:
  - either clean_*.csv (preferred), or raw *.csv so clean_all_data.py can generate clean files.

macOS / Linux
./.venv/bin/python demo.py --offline

Windows (PowerShell)
.\.venv\Scripts\python demo.py --offline

--------------------------------------------------
Running Manually (Step-by-Step, No Activation)
--------------------------------------------------

1) Run all extractors (downloads raw datasets into /data)

macOS / Linux
./.venv/bin/python run_all_extractors.py

Windows (PowerShell)
.\.venv\Scripts\python run_all_extractors.py

2) Generate cleaned datasets (creates clean_*.csv in /data)

macOS / Linux
./.venv/bin/python clean_all_data.py

Windows (PowerShell)
.\.venv\Scripts\python clean_all_data.py

3) Run database migrations

macOS / Linux
./.venv/bin/python manage.py migrate

Windows (PowerShell)
.\.venv\Scripts\python manage.py migrate

4) Start the server

macOS / Linux
./.venv/bin/python manage.py runserver

Windows (PowerShell)
.\.venv\Scripts\python manage.py runserver

5) Open:
http://127.0.0.1:8000

--------------------------------------------------
Running in VS Code
--------------------------------------------------

1) Open the project folder in VS Code
2) Select interpreter:
   - Press Ctrl+Shift+P (Mac: Cmd+Shift+P)
   - Type: Python: Select Interpreter
   - Choose:
       Windows: .venv\Scripts\python.exe
       Mac/Linux: .venv/bin/python

3) Open the VS Code terminal and run:

python -m pip install -r requirements.txt
python demo.py

--------------------------------------------------
Troubleshooting (Common)
--------------------------------------------------

Port 8000 already in use
- Start on a different port:

macOS / Linux
./.venv/bin/python manage.py runserver 8001

Windows (PowerShell)
.\.venv\Scripts\python manage.py runserver 8001

Then open:
http://127.0.0.1:8001


VS Code says "ModuleNotFoundError" or imports fail
- Ensure VS Code is using the workspace virtual environment:
  Python: Select Interpreter -> .venv
- Then re-install deps into that environment:

Windows (PowerShell)
.\.venv\Scripts\python -m pip install -r requirements.txt

macOS / Linux
./.venv/bin/python -m pip install -r requirements.txt

--------------------------------------------------
Notes
--------------------------------------------------

• Auto insurance supports multi year trend analysis
• Home insurance data represents a single year snapshot
• Year selection is disabled when Home insurance is selected
• The application uses indexed values to avoid misleading scale effects
