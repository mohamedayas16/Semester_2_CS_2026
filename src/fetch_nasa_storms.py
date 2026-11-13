
"""
NASA DONKI Geomagnetic Storm Events - 2024

Downloads NASA geomagnetic storm records using an API key.
Creates CSV files for Power BI.

Does not modify the existing GFZ or Aurorasaurus datasets.
"""

from pathlib import Path
import os
import json
import requests
import pandas as pd

# ----------------------------------
# 1. PROJECT FOLDERS
# ----------------------------------

ROOT = Path(__file__).resolve().parent.parent

RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

RAW.mkdir(parents=True, exist_ok=True)
PROCESSED.mkdir(parents=True, exist_ok=True)

# ----------------------------------
# 2. NASA API KEY
# ----------------------------------

API_KEY = os.getenv("NASA_API_KEY")

if not API_KEY:
    raise ValueError(
        "NASA_API_KEY not found. "
        "Set your NASA API key in PowerShell first."
    )

URL = "https://api.nasa.gov/DONKI/GST"

PARAMS = {
    "startDate": "2024-05-01",
    "endDate": "2024-05-31",
    "api_key": API_KEY
}

# ----------------------------------
# 3. DOWNLOAD NASA DATA - ALL 12 MONTHS
# ----------------------------------

import calendar

print("Connecting to NASA DONKI API...")
print("Downloading geomagnetic storm events for 2024...")

all_events = []

for month in range(1, 13):

    # Find the last day of each month
    last_day = calendar.monthrange(2024, month)[1]

    start_date = f"2024-{month:02d}-01"
    end_date = f"2024-{month:02d}-{last_day:02d}"

    print(f"\nDownloading {start_date} to {end_date}...")

    monthly_params = {
        "startDate": start_date,
        "endDate": end_date,
        "api_key": API_KEY
    }

    response = requests.get(
        URL,
        params=monthly_params,
        timeout=120
    )

    print("HTTP status:", response.status_code)

    if not response.ok:
        # Do not expose the API key in error messages
        error_text = response.text[:500].replace(
            API_KEY, "[HIDDEN]"
        )
        print("NASA error:", error_text)
        raise RuntimeError(
            f"NASA request failed for {start_date} "
            f"to {end_date} (HTTP {response.status_code})"
        )

    monthly_data = response.json()

    if not isinstance(monthly_data, list):
        raise ValueError(
            f"Unexpected NASA response for month {month}"
        )

    print(f"Events received: {len(monthly_data)}")

    all_events.extend(monthly_data)


# Remove duplicate storm IDs
unique_events = {}

for event in all_events:
    storm_id = event.get("gstID")

    if storm_id:
        unique_events[storm_id] = event

data = list(unique_events.values())

print("\n--------------------------------")
print("ALL 12 MONTHS DOWNLOADED!")
print("Total records received:", len(all_events))
print("Unique storm events:", len(data))
print("--------------------------------")

# ----------------------------------
# 4. SAVE ORIGINAL JSON
# ----------------------------------

raw_file = RAW / "nasa_storms_2024.json"

with open(raw_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Original NASA JSON saved.")

# ----------------------------------
# 5. PROCESS STORM EVENTS
# ----------------------------------

records = []

for event in data:

    storm_id = event.get("gstID")
    start_time = event.get("startTime")

    if not storm_id or not start_time:
        continue

    kp_values = []

    for observation in event.get("allKpIndex", []) or []:
        value = observation.get("kpIndex")

        if value is not None:
            kp_values.append(float(value))

    max_kp = max(kp_values) if kp_values else None

    records.append({
        "storm_id": storm_id,
        "start_time": start_time,
        "maximum_kp": max_kp
    })

columns = [
    "storm_id",
    "start_time",
    "maximum_kp"
]

df = pd.DataFrame(records, columns=columns)

if not df.empty:
    df["start_time"] = pd.to_datetime(
        df["start_time"],
        utc=True,
        errors="coerce"
    )

    df = df.dropna(subset=["start_time"])
    df = df.drop_duplicates(subset=["storm_id"])

    df = df[
        (df["start_time"] >= pd.Timestamp("2024-01-01", tz="UTC"))
        &
        (df["start_time"] < pd.Timestamp("2025-01-01", tz="UTC"))
    ].copy()

    df["date"] = df["start_time"].dt.strftime("%Y-%m-%d")
    df["month"] = df["start_time"].dt.strftime("%Y-%m")

    df = df.sort_values("start_time")

else:
    df["date"] = pd.Series(dtype="string")
    df["month"] = pd.Series(dtype="string")

# ----------------------------------
# 6. SAVE POWER BI STORM DATA
# ----------------------------------

storm_file = PROCESSED / "nasa_storms_2024.csv"

df.to_csv(storm_file, index=False)

# ----------------------------------
# 7. MONTHLY STORM COUNTS
# ----------------------------------

months = pd.period_range(
    "2024-01",
    "2024-12",
    freq="M"
).astype(str)

monthly = pd.DataFrame({"month": months})

if not df.empty:
    counts = (
        df.groupby("month")
        .size()
        .reset_index(name="storm_events")
    )

    monthly = monthly.merge(
        counts,
        on="month",
        how="left"
    )

else:
    monthly["storm_events"] = 0

monthly["storm_events"] = (
    monthly["storm_events"]
    .fillna(0)
    .astype(int)
)

monthly_file = (
    PROCESSED / "nasa_storms_monthly_2024.csv"
)

monthly.to_csv(monthly_file, index=False)

# ----------------------------------
# 8. SUMMARY
# ----------------------------------

summary = {
    "year": 2024,
    "source": "NASA DONKI GST API",
    "total_storm_events": int(len(df)),
    "months_with_storms": int(
        (monthly["storm_events"] > 0).sum()
    ),
    "maximum_reported_kp": (
        float(df["maximum_kp"].max())
        if df["maximum_kp"].notna().any()
        else None
    )
}

summary_file = (
    PROCESSED / "nasa_storm_summary_2024.json"
)

with open(summary_file, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

# ----------------------------------
# 9. OUTPUT
# ----------------------------------

print("\nSUCCESS! NASA data processed.")
print("--------------------------------")

for key, value in summary.items():
    print(f"{key}: {value}")

print("\nFiles created:")
print(raw_file)
print(storm_file)
print(monthly_file)
print(summary_file)

print("\nExisting GFZ and Aurorasaurus files are unchanged.")
