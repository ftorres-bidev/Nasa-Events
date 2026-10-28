"""Build the EONET categories lookup table (dbo.bronze_categories).

The table is small and fully derived from the feed, so it is rebuilt on every
run (if_exists="replace"). Only the first category of each event is used,
matching NasaEvents.py.
"""
import pandas as pd
import requests

from db import get_engine

# --- Configuration -----------------------------------------------------------
URL = "https://eonet.gsfc.nasa.gov/api/v3/events/geojson"
TABLE = "bronze_categories"


def fetch_categories(url: str = URL) -> pd.DataFrame:
    """Return the distinct (CategoryID, Title) pairs found in the feed."""
    response = requests.get(url, timeout=30, headers={"accept": "application/json"})
    response.raise_for_status()  # stop early on HTTP errors

    df = pd.json_normalize(response.json()["features"])

    # Each cell looks like [{'id': 'wildfires', 'title': 'Wildfires'}].
    # Take the first category and split it into two columns.
    first_category = df["properties.categories"].str[0]
    categories = pd.DataFrame({
        "CategoryID": first_category.str["id"],
        "Title": first_category.str["title"],
    })

    return categories.drop_duplicates().reset_index(drop=True)


def main():
    df_categories = fetch_categories()
    engine = get_engine()

    # Sanity check that the connection works before writing.
    with engine.connect():
        print("Connected!")

    df_categories.to_sql(TABLE, engine, schema="dbo", if_exists="replace", index=False)
    print(f"Loaded {len(df_categories)} categories into dbo.{TABLE}.")


if __name__ == "__main__":
    main()
