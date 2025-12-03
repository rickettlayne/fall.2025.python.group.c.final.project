Project Structure
The repository is organized as follows:
fall.2025.python.group.c.final.project/
│
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
│
├── config/                   # Django project configuration
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── dashboard/                # Django application
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── tests.py
│   └── home.html
│
├── extractors/               # API extractors for weather and insurance data
│   ├── extractor_weather_noaa.py
│   ├── extractor_weather_fema.py
│   ├── extractor_insurance_car_naic.py
│   └── extractor_insurance_home_nerd_wallet.py
│
├── archive files/            # Older versions of extractors
└── project overview/         # Proposal and planning documents
 
Running the Project Locally (macOS and Windows)

1. Create and activate a virtual environment

macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate

Windows:
python -m venv .venv
.venv\Scripts\activate

2. Install project dependencies
Run this from the project root:
pip install -r requirements.txt

3. Run database migrations
python manage.py migrate

4. Start the development server
python manage.py runserver

5. Open the application
Visit:
http://127.0.0.1:8000

