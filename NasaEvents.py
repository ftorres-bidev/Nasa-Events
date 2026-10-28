"""Fetch NASA EONET natural events and prepare them for dbo.bronze_events.

Design notes
------------
* The GeoJSON feed has one row per point on an event's track, so `ID` is NOT
  unique on its own. The natural key is (ID, EventDate).
* Only `Point` geometries are kept; polygons have nested coordinate lists.
* Only the first category of each event is kept.
* By default the script just previews the data. Set LOAD_TO_DB = True to
  append it to SQL Server (the table must already exist, with DATETIME2
  for EventDate; re-running will fail on the primary key unless you
  truncate first).
"""
import pandas as pd
import requests

from db import get_engine

# --- Configuration -----------------------------------------------------------
URL = "https://eonet.gsfc.nasa.gov/api/v3/events/geojson"
TABLE = "bronze_events"
LOAD_TO_DB = False   # flip to True to write to SQL Server

# Columns to pull from the flattened GeoJSON, and the names we give them.
COLUMN_MAP = {
    "properties.id": "ID",
    "properties.title": "Title",
    "properties.closed": "Status",              # actually a close date (null while open)
    "properties.date": "EventDate",
    "properties.categories": "CategoryList",    # list of {'id': ..., 'title': ...}
    "properties.magnitudeValue": "MagnitudeValue",
    "properties.magnitudeUnit": "MagnitudeUnit",
    "geometry.type": "GeometryType",
    "geometry.coordinates": "Coordinates",      # [lon, lat] for points
}


def fetch_events(url: str = URL) -> pd.DataFrame:
    """Download the EONET feed and return one cleaned row per event point."""
    response = requests.get(url, timeout=30, headers={"accept": "application/json"})
    response.raise_for_status()  # stop early on HTTP errors

    # Flatten the nested GeoJSON, keep only the columns we need, and rename them.
    df = pd.json_normalize(response.json()["features"])
    df = df[list(COLUMN_MAP)].rename(columns=COLUMN_MAP)

    # Keep points only (polygons have nested coordinates that break numeric casts).
    df = df[df["GeometryType"] == "Point"].copy()

    # Use the first category of each event as its category.
    df["categoryId"] = df["CategoryList"].apply(lambda c: c[0]["id"])

    # Split [lon, lat] into two numeric columns.
    df["Lon"] = pd.to_numeric(df["Coordinates"].str[0])
    df["Lat"] = pd.to_numeric(df["Coordinates"].str[1])

    # Dates arrive timezone-aware (UTC); SQL Server DATETIME2 needs them naive.
    df["EventDate"] = pd.to_datetime(df["EventDate"]).dt.tz_localize(None)

    # Helper columns are no longer needed.
    df = df.drop(columns=["CategoryList", "Coordinates"])

    # Enforce the (ID, EventDate) primary key.
    return df.drop_duplicates(subset=["ID", "EventDate"])


def load_events(df: pd.DataFrame) -> None:
    """Append the events to SQL Server (never use if_exists='replace' here,
    it would recreate the table with pandas' default column types)."""
    engine = get_engine()
    df.to_sql(TABLE, engine, schema="dbo", if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into dbo.{TABLE}.")


def main():
    df_events = fetch_events()
    print(df_events.head(5))

    if LOAD_TO_DB:
        load_events(df_events)


if __name__ == "__main__":
    main()
