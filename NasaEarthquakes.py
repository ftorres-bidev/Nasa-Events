"""Load USGS earthquakes (GeoJSON summary feed) into dbo.bronze_earthquakes.

Design notes
------------
* Raw epoch milliseconds are loaded as-is (EventTime / UpdateTime are BIGINT);
  convert them to real dates in SQL via the dbo.silver_earthquakes view.
* Only IDs not already in the table are inserted, so re-running is safe.
* USGS revises events after publishing them, so existing rows are NOT
  updated by this script (that would need a MERGE / upsert).
"""
import pandas as pd
import requests

from db import get_engine

# --- Configuration -----------------------------------------------------------
# Other feeds: all_hour, all_day, all_week (same URL pattern).
FEED_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
TABLE = "bronze_earthquakes"


def fetch_quakes(url: str = FEED_URL) -> pd.DataFrame:
    """Download the USGS feed and return one cleaned row per earthquake."""
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()  # stop early on HTTP errors

    # Flatten each GeoJSON feature into a plain dict.
    rows = []
    for feature in resp.json()["features"]:
        props = feature["properties"]
        # GeoJSON coordinate order is [longitude, latitude, depth_km].
        lon, lat, depth = feature["geometry"]["coordinates"]
        rows.append({
            "ID": feature["id"],              # the id lives on the feature, not in properties
            "Magnitude": props.get("mag"),
            "MagType": props.get("magType"),
            "Place": props.get("place"),      # free text, e.g. "10 km SW of Ridgecrest, CA"
            "EventTime": props.get("time"),   # epoch milliseconds (UTC)
            "UpdatedTime": props.get("updated"),
            "Felt": props.get("felt"),        # number of "felt" reports
            "Cdi": props.get("cdi"),          # community-reported intensity
            "Mmi": props.get("mmi"),          # instrumental intensity
            "Alert": props.get("alert"),      # PAGER alert level
            "Tsunami": props.get("tsunami", 0),
            "Sig": props.get("sig"),          # significance score
            "Nst": props.get("nst"),          # stations used
            "Dmin": props.get("dmin"),
            "Rms": props.get("rms"),
            "Gap": props.get("gap"),
            "EventType": props.get("type"),
            "Lon": lon,
            "Lat": lat,
            "DepthKm": depth,
        })

    df = pd.DataFrame(rows)

    # --- Cleaning ---
    df = df[df["EventType"] == "earthquake"]                       # drop quarry blasts etc.
    df = df.dropna(subset=["EventTime"]).drop_duplicates(subset="ID")

    # Nullable integer type keeps missing values as NULL instead of floats/NaN.
    for col in ["Felt", "Nst", "Sig"]:
        df[col] = df[col].astype("Int64")
    df["Tsunami"] = df["Tsunami"].fillna(0).astype(int)

    # Rename to match the column names in the SQL table.
    df = df.rename(columns={"UpdatedTime": "UpdateTime", "EventType": "Type"})
    return df


def main():
    engine = get_engine()
    df = fetch_quakes()

    # Skip IDs that are already loaded (keeps the script idempotent).
    existing = pd.read_sql(f"SELECT ID FROM dbo.{TABLE}", engine)["ID"]
    new_rows = df[~df["ID"].isin(existing)]

    if new_rows.empty:
        print("No new earthquakes to load.")
        return

    new_rows.to_sql(TABLE, engine, schema="dbo", if_exists="append", index=False)
    print(f"Loaded {len(new_rows)} new earthquakes "
          f"({len(df) - len(new_rows)} already present).")


if __name__ == "__main__":
    main()
