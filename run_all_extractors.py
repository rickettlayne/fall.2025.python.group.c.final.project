import subprocess
import os
import sys

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACTORS_DIR = os.path.join(BASE_DIR, "extractors")
DATA_DIR = os.path.join(BASE_DIR, "data")

# List of extractors to run
EXTRACTOR_SCRIPTS = [
    "extractor_weather_noaa.py",
    "extractor_weather_fema.py",
    "extractor_insurance_home_nerd_wallet.py",
    "extractor_insurance_car_naic.py",
]

def run_extractor(script_name):
    """Run a single extractor"""
    script_path = os.path.join(EXTRACTORS_DIR, script_name)
    print(f"\n--------------------------------------------------")
    print(f"Running: {script_name}")
    print(f"--------------------------------------------------")

    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ ERROR running {script_name}")
        print(result.stderr)
        sys.exit(1)

    print(result.stdout)
    print(f"✔ Finished {script_name}")

def verify_output():
    """Check that expected CSV files exist"""
    print("\nVerifying output files...")

    expected_files = [
        "noaa_weather.csv",
        "fema_weather.csv",
        "nerdwallet_home.csv",
        "naic_auto_insurance.csv",
    ]

    missing = []

    for f in expected_files:
        path = os.path.join(DATA_DIR, f)
        if not os.path.exists(path):
            missing.append(f)

    if missing:
        print("\n❌ Missing files:")
        for f in missing:
            print(f" - {f}")
        print("\nExtraction incomplete. Fix errors and re-run.")
        sys.exit(1)

    print("✔ All extractor CSV files created successfully!")
    print("\nYour dashboard is ready to load fresh data.")

if __name__ == "__main__":
    print("\n==============================================")
    print(" RUNNING ALL EXTRACTORS ")
    print("==============================================")

    for script in EXTRACTOR_SCRIPTS:
        run_extractor(script)

    verify_output()

    print("\n==============================================")
    print(" ALL EXTRACTORS COMPLETED SUCCESSFULLY ")
    print("==============================================")
