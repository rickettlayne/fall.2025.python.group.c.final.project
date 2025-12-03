Project Structure
The repository is organized as follows:
fall.2025.python.group.c.final.project/
│
├── manage.py
├── requirements.txt
├── run_all_extractors.py
├── .venv/
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
├── data/
│   ├── noaa_weather.csv
│   ├── fema_weather.csv
│   ├── nerdwallet_home.csv
│   └── naic_auto_insurance.csv
│
├── archive_files/
│
└── project overview/

Running the Project Locally (macOS, Linux, Windows)

1. Create and activate a virtual environment

macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

Windows
python -m venv .venv
.venv\Scripts\activate
 
2. Install project dependencies
Run this in the project root:
pip install -r requirements.txt
 
3. (Optional) Run all data extractors
Refresh NOAA, FEMA, home insurance, and auto insurance datasets:
python run_all_extractors.py
 
4. Run database migrations
python manage.py migrate
 
5. Start the development server
python manage.py runserver
 
6. Open the application
Visit in your browser:
http://127.0.0.1:8000
