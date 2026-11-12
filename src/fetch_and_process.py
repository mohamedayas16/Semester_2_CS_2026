
from pathlib import Path
from datetime import datetime, timezone
import json

import requests
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# STEP 1: Locate the project folders
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

RAW.mkdir(parents=True, exist_ok=True)
PROCESSED.mkdir(parents=True, exist_ok=True)

# STEP 2: Request October 2026 Kp data
url = "https://kp.gfz.de/app/json/"

params = {
    "start": "2026-10-01T00:00:00Z",
    "end": "2026-10-31T23:59:59Z",
    "index": "Kp"
}

print("Connecting to GFZ scientific API...")

response = requests.get(url, params=params, timeout=60)
response.raise_for_status()

data = response.json()

# STEP 3: Save the original JSON
raw_file = RAW / "kp_october_2026.json"

with open(raw_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Original JSON saved successfully.")

# STEP 4: Validate the downloaded data
required = ["datetime", "Kp", "status"]

if not isinstance(data, dict):
    raise ValueError("Unexpected API response format")

if not all(k in data for k in required):
    raise ValueError(f"Missing fields: {list(data.keys())}")

if not (
    len(data["datetime"])
    == len(data["Kp"])
    == len(data["status"])
):
    raise ValueError("Data columns have unequal lengths")

df = pd.DataFrame({
    "datetime": pd.to_datetime(data["datetime"], utc=True),
    "kp": pd.to_numeric(data["Kp"], errors="coerce"),
    "status": data["status"]
})

df = df.dropna(subset=["datetime", "kp"])
df = df.sort_values("datetime").reset_index(drop=True)

if df.empty:
    raise ValueError("No valid observations received")

if df["datetime"].duplicated().any():
    raise ValueError("Duplicate timestamps detected")

if not df["kp"].between(0, 9).all():
    raise ValueError("Kp outside valid range")

start = pd.Timestamp("2026-10-01", tz="UTC")
end = pd.Timestamp("2026-11-01", tz="UTC")

if not ((df["datetime"] >= start) &
        (df["datetime"] < end)).all():
    raise ValueError("Unexpected dates in API data")

# STEP 5: Add useful analysis columns
df["date"] = df["datetime"].dt.date
df["hour"] = df["datetime"].dt.hour

# Kp >= 5 indicates storm-level geomagnetic activity
df["storm_interval"] = df["kp"] >= 5

# STEP 6: Convert to Parquet with source metadata
table = pa.Table.from_pandas(df, preserve_index=False)

metadata = dict(table.schema.metadata or {})
metadata.update({
    b"source": b"GFZ Helmholtz Centre for Geosciences",
    b"api_url": response.url.encode("utf-8"),
    b"license": b"CC BY 4.0",
    b"retrieved_utc": datetime.now(
        timezone.utc
    ).isoformat().encode("utf-8")
})

table = table.replace_schema_metadata(metadata)

parquet_file = PROCESSED / "kp_october_2026.parquet"
pq.write_table(table, parquet_file)

# STEP 7: Calculate summary statistics
summary = {
    "observations": int(len(df)),
    "average_kp": round(float(df["kp"].mean()), 3),
    "maximum_kp": float(df["kp"].max()),
    "storm_intervals": int(df["storm_interval"].sum()),
    "days": int(df["date"].nunique())
}

summary_file = PROCESSED / "kp_summary.json"

with open(summary_file, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

print("\nSUCCESS! Analysis completed.")
print("--------------------------------")

for key, value in summary.items():
    print(f"{key}: {value}")

print("\nSaved files:")
print(raw_file)
print(parquet_file)
print(summary_file)
