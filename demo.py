import argparse
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

RAW_FILES = [
    "noaa_weather.csv",
    "fema_weather.csv",
    "nerdwallet_home.csv",
    "naic_auto_insurance.csv",
]

CLEAN_FILES = [
    "clean_noaa_weather.csv",
    "clean_fema_weather.csv",
    "clean_nerdwallet_home.csv",
    "clean_naic_auto_insurance.csv",
]

def run(cmd):
    print(f"\n>>> {' '.join(cmd)}")
    subprocess.check_call(cmd)

def files_exist(filenames):
    return all(os.path.exists(os.path.join(DATA_DIR, f)) for f in filenames)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the dashboard demo end-to-end.")
    parser.add_argument("--refresh", action="store_true", help="Force re-download/re-scrape datasets.")
    parser.add_argument("--offline", action="store_true", help="Do not run extractors; use local files only.")
    args = parser.parse_args()

    has_clean = files_exist(CLEAN_FILES)
    has_raw = files_exist(RAW_FILES)

    # Decide extraction/cleaning path
    if args.refresh:
        print("\n[Demo] --refresh: running extractors and cleaning.")
        run([sys.executable, "run_all_extractors.py", "--timeout", "600", "--continue-on-error"])
        run([sys.executable, "clean_all_data.py"])

    else:
        if has_clean:
            print("\n[Demo] Clean datasets already exist: skipping extractors + cleaning (fast mode).")
        elif has_raw:
            print("\n[Demo] Raw datasets exist but clean datasets missing: running cleaning step.")
            run([sys.executable, "clean_all_data.py"])
        else:
            if args.offline:
                raise SystemExit(
                    "\n[Demo] Offline mode enabled but no local data found.\n"
                    "Run once with internet access:\n"
                    "  python demo.py --refresh\n"
                )
            print("\n[Demo] No local datasets found: running extractors and cleaning.")
            run([sys.executable, "run_all_extractors.py", "--timeout", "600", "--continue-on-error"])
            run([sys.executable, "clean_all_data.py"])

    # Migrate + run server
    print("\n[Demo] Running migrations...")
    run([sys.executable, "manage.py", "migrate"])

    print("\n[Demo] Starting Django server (CTRL+C to stop)...")
    run([sys.executable, "manage.py", "runserver"])
