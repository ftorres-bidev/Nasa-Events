"""Load USGS earthquakes (GeoJSON summary feed) into dbo.bronze_earthquakes.

Raw epoch milliseconds are loaded as-is (EventTime / UpdatedTime are BIGINT);
convert them in SQL via the dbo.silver_earthquakes view.
Only IDs not already in the table are inserted, so re-running is safe.
Note: USGS revises events, so existing rows are NOT updated by this script.
"""
import pandas as pd
import requests

from db import get_engine

FEED_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
TABLE = "bronze_earthquakes"


def fetch_quakes(url: str = FEED_URL) -> pd.DataFrame:
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    rows = []
    for f in resp.json()["features"]:
        p = f["properties"]
        lon, lat, depth = f["geometry"]["coordinates"]
        rows.append({
            "ID": f["id"],
            "Magnitude": p.get("mag"),
            "MagType": p.get("magType"),
            "Place": p.get("place"),
            "EventTime": p.get("time"),
            "UpdatedTime": p.get("updated"),
            "Felt": p.get("felt"),
            "Cdi": p.get("cdi"),
            "Mmi": p.get("mmi"),
            "Alert": p.get("alert"),
            "Tsunami": p.get("tsunami", 0),
            "Sig": p.get("sig"),
            "Nst": p.get("nst"),
            "Dmin": p.get("dmin"),
            "Rms": p.get("rms"),
            "Gap": p.get("gap"),
            "EventType": p.get("type"),
            "Lon": lon,
            "Lat": lat,
            "DepthKm": depth,
        })

    df = pd.DataFrame(rows)
    df = df[df["EventType"] == "earthquake"]          # drop quarry blasts etc.
    df = df.dropna(subset=["EventTime"]).drop_duplicates(subset="ID")
    for col in ["Felt", "Nst", "Sig"]:
        df[col] = df[col].astype("Int64")
    df["Tsunami"] = df["Tsunami"].fillna(0).astype(int)
    df = df.rename(columns={"UpdatedTime": "UpdateTime", "EventType": "Type"})
    return df


def main():
    engine = get_engine()
    df = fetch_quakes()

    existing = pd.read_sql(f"SELECT ID FROM dbo.{TABLE}", engine)["ID"]
    new_rows = df[~df["ID"].isin(existing)]

    if new_rows.empty:
        print("No new earthquakes to load.")
        return

    new_rows.to_sql(TABLE, engine, schema="dbo", if_exists="append", index=False)
    print(f"Loaded {len(new_rows)} new earthquakes ({len(df) - len(new_rows)} already present).")


if __name__ == "__main__":
    main()
