Weather and Insurance Risk Dashboard
===================================

This project is a Django based interactive dashboard that analyzes the relationship between U.S. insurance premiums and federally declared disaster activity. The application supports both Auto and Home insurance views and integrates FEMA disaster data to compute a composite risk score by state.

The dashboard is designed to help users understand how insurance costs vary by geography,time, and disaster exposure.

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

• Auto insurance analysis with multi year trends from 2018 through 2022
• Home insurance analysis presented as a current year national snapshot
• FEMA disaster integration by state
• Composite risk score combining premium pressure and disaster exposure
• Interactive filters for insurance type, state, and year
• Choropleth map visualizing relative risk by state
• Indexed trend charts for fair comparison over time

---

## Project Structure

fall.2025.python.group.c.final.project/
│
├── manage.py
├── requirements.txt
├── run_all_extractors.py
│
├── config/
│   ├── init.py
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

---

## Data Overview

### Auto Insurance

• Source: NAIC
• Coverage: 2018 through 2022
• Used for trend analysis and premium indexing

### Home Insurance

• Source: NerdWallet
• Coverage: Single year national snapshot
• Displayed as a current year reference only

### FEMA Disaster Data

• Source: FEMA Disaster Declarations
• Used to compute disaster frequency by state
• Combined with premium index to calculate composite risk score

---

## Risk Score Methodology

Risk Score = 0.6 × Premium Index + 0.4 × Disaster Index

• Premium Index compares a state's average premium to the national average
• Disaster Index compares a state's disaster frequency to the national average
• A score above 1.00 indicates above average risk

---

Running the Project Locally

1. Create and activate a virtual environment

macOS or Linux

```
python3 -m venv .venv
source .venv/bin/activate
```

Windows

```
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies

```
pip install -r requirements.txt
```

3. Optional: Refresh all datasets

```
python run_all_extractors.py
```

4. Start the development server

```
python manage.py runserver
```

5. Open the application

```
http://127.0.0.1:8000
```

---

## Notes

• The application does not use a database or Django ORM models
• All analytics are performed using Pandas and CSV based datasets
• Auto insurance supports multi year trend analysis
• Home insurance data represents a current year snapshot
• Year selection is disabled when Home insurance is selected
• Indexed values are used to avoid misleading scale effects

