import pandas as pd

from utils.state_mapping import normalize_state
from utils.time_normalization import normalize_year
from utils.value_normalization import normalize_dollar


# ---------------------------------------------------
# NAIC AUTO INSURANCE
# ---------------------------------------------------
naic_raw = "data/naic_auto_insurance.csv"
naic_clean = "data/clean_naic_auto_insurance.csv"

df_naic = pd.read_csv(naic_raw)

df_naic["state"] = df_naic["state"].apply(normalize_state)

for col in ["avg_2022", "avg_2021", "avg_2020", "avg_2019", "avg_2018"]:
    df_naic[col] = df_naic[col].apply(normalize_dollar)

df_naic.to_csv(naic_clean, index=False)
print("Cleaned NAIC auto insurance data written")


# ---------------------------------------------------
# NERDWALLET HOME INSURANCE
# ---------------------------------------------------
nerd_raw = "data/nerdwallet_home.csv"
nerd_clean = "data/clean_nerdwallet_home.csv"

df_nerd = pd.read_csv(nerd_raw)

df_nerd["state"] = df_nerd["state"].apply(normalize_state)

if "year" in df_nerd.columns:
    df_nerd["year"] = df_nerd["year"].apply(normalize_year)

if "avg_home_premium" in df_nerd.columns:
    df_nerd["avg_home_premium"] = df_nerd["avg_home_premium"].apply(normalize_dollar)

df_nerd.to_csv(nerd_clean, index=False)
print("Cleaned NerdWallet home insurance data written")


# ---------------------------------------------------
# FEMA WEATHER DISASTERS
# ---------------------------------------------------
fema_raw = "data/fema_weather.csv"
fema_clean = "data/clean_fema_weather.csv"

df_fema = pd.read_csv(fema_raw)

if "state" in df_fema.columns:
    df_fema["state"] = df_fema["state"].apply(normalize_state)

if "year" in df_fema.columns:
    df_fema["year"] = df_fema["year"].apply(normalize_year)

df_fema.to_csv(fema_clean, index=False)
print("Cleaned FEMA weather data written")


# ---------------------------------------------------
# NOAA WEATHER
# ---------------------------------------------------
noaa_raw = "data/noaa_weather.csv"
noaa_clean = "data/clean_noaa_weather.csv"

df_noaa = pd.read_csv(noaa_raw)

if "state" in df_noaa.columns:
    df_noaa["state"] = df_noaa["state"].apply(normalize_state)

if "year" in df_noaa.columns:
    df_noaa["year"] = df_noaa["year"].apply(normalize_year)

# normalize numeric weather columns if present
for col in df_noaa.columns:
    if col.lower().endswith(("temp", "temperature", "precip", "rain", "snow")):
        df_noaa[col] = pd.to_numeric(df_noaa[col], errors="coerce")

df_noaa.to_csv(noaa_clean, index=False)
print("Cleaned NOAA weather data written")


print("All datasets cleaned successfully")
