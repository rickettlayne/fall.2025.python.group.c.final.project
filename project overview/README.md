# fall.2025.python.group.c.final.project

Interactive Django dashboard visualizing the relationship between historical weather events, disaster declarations, and home and auto insurance rates across U.S. states. Integrates data from NOAA, FEMA, Visual Crossing, Open-Meteo, and public insurance datasets.

## Running the project locally
1. Create and activate a virtual environment (macOS/Linux):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   On Windows use `python -m venv .venv` then activate with `.venv\Scripts\activate`.
2. Install dependencies (the `requirements.txt` file lives in the repo root):
   ```bash
   pip install -r requirements.txt
   ```
3. Apply migrations:
   ```bash
   python manage.py migrate
   ```
4. Start the development server:
   ```bash
   python manage.py runserver
   ```
5. Visit http://127.0.0.1:8000/ to view the dashboard.

### Troubleshooting
- **NameError: name 'New' is not defined** when running `manage.py`: this usually means the file has stray text (e.g., a line that just says `New`) above the shebang. Open `manage.py` in the repo root and ensure it matches the standard Django stub that starts with `#!/usr/bin/env python3` followed by the module docstring.
- **Django import errors**: verify your virtual environment is active and that `pip install -r requirements.txt` completed successfully.