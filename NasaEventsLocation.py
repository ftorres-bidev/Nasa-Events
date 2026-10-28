"""Geocode earthquakes to their nearest place and link them via PlaceID.

Steps
-----
1. Read earthquake coordinates from dbo.bronze_earthquakes.
2. Reverse-geocode every point to the nearest GeoNames city (offline).
3. Insert any new places into dbo.bronze_places.
4. Write the resulting PlaceID back onto each earthquake row.

Caveat: reverse_geocoder returns the NEAREST CITY, not a boundary match, so
offshore or border-area quakes may get an approximate (or wrong-country) place.
"""
import pandas as pd
import pycountry
import reverse_geocoder as rg
from sqlalchemy import text, types as T

from db import get_engine

# --- Configuration -----------------------------------------------------------
QUAKES_TABLE = "bronze_earthquakes"
PLACES_TABLE = "bronze_places"
STAGING_TABLE = "stg_place_map"

# A place is uniquely identified by these three columns.
PLACE_KEY = ["PlaceName", "State", "CountryCode"]


def geocode_earthquakes(engine) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (earthquakes with place columns, distinct places)."""
    df = pd.read_sql(f"SELECT ID, Lat, Lon FROM dbo.{QUAKES_TABLE}", engine)
    df["Source"] = "usgs"
    print(df.head(5))

    # Find the nearest place for every event in one batch.
    # mode=1 runs single-process (mode 2 breaks on Windows); coords are (lat, lon).
    coords = list(zip(df["Lat"], df["Lon"]))
    results = rg.search(coords, mode=1)

    df["PlaceName"] = [r["name"] for r in results]
    df["State"] = [r["admin1"] or "" for r in results]        # '' keeps the unique key NOT NULL
    df["CountryCode"] = [r["cc"] for r in results]
    place_lat = [float(r["lat"]) for r in results]            # coordinates of the city itself
    place_lon = [float(r["lon"]) for r in results]

    # One row per distinct place, using the city's own coordinates.
    places = (
        df[PLACE_KEY]
        .assign(PlaceLat=place_lat, PlaceLon=place_lon)
        .drop_duplicates(subset=PLACE_KEY)
        .rename(columns={"PlaceLat": "Lat", "PlaceLon": "Lon"})
    )

    # Convert ISO country code (e.g. "US") to a name; fall back to the code.
    places["Country"] = places["CountryCode"].map(country_name)
    print(places.head(5))

    return df, places


def country_name(code: str) -> str:
    """Look up a country name from its ISO alpha-2 code."""
    country = pycountry.countries.get(alpha_2=code)
    return country.name if country else code


def load_new_places(engine, places: pd.DataFrame) -> None:
    """Insert only the places that are not already in dbo.bronze_places."""
    existing = pd.read_sql(
        f"SELECT PlaceName, State, CountryCode FROM dbo.{PLACES_TABLE}", engine
    )
    # Left anti-join: keep rows that exist only in `places`.
    new_places = (
        places.merge(existing, on=PLACE_KEY, how="left", indicator=True)
        .query("_merge == 'left_only'")
        .drop(columns="_merge")
    )
    new_places.to_sql(PLACES_TABLE, engine, schema="dbo", if_exists="append", index=False)
    print(f"Inserted {len(new_places)} new places.")


def attach_place_ids(engine, df: pd.DataFrame) -> pd.DataFrame:
    """Read generated PlaceIDs back and merge them onto every earthquake row."""
    place_ids = pd.read_sql(
        f"SELECT PlaceID, PlaceName, State, CountryCode FROM dbo.{PLACES_TABLE}", engine
    )
    # validate guards against duplicate places silently multiplying rows.
    return df.merge(place_ids, on=PLACE_KEY, how="left", validate="many_to_one")


def write_place_ids(engine, df: pd.DataFrame) -> None:
    """Update PlaceID on dbo.bronze_earthquakes via a temporary staging table."""
    mapping = df[["ID", "Source", "PlaceID"]].dropna(subset=["PlaceID"]).copy()
    mapping["PlaceID"] = mapping["PlaceID"].astype(int)

    # Stage the ID -> PlaceID mapping, then do one set-based UPDATE.
    mapping.to_sql(
        STAGING_TABLE, engine, schema="dbo", if_exists="replace", index=False,
        dtype={"ID": T.NVARCHAR(50), "Source": T.NVARCHAR(10)},
    )

    # engine.begin() commits on success and rolls back on error.
    with engine.begin() as conn:
        conn.execute(text(f"""
            UPDATE q
            SET q.PlaceID = m.PlaceID
            FROM dbo.{QUAKES_TABLE} AS q
            JOIN dbo.{STAGING_TABLE} AS m
              ON m.Source = 'usgs' AND m.ID = q.ID;
        """))
        conn.execute(text(f"DROP TABLE dbo.{STAGING_TABLE}"))


def main():
    engine = get_engine()

    df_earthquakes, places = geocode_earthquakes(engine)
    load_new_places(engine, places)
    df_earthquakes = attach_place_ids(engine, df_earthquakes)
    write_place_ids(engine, df_earthquakes)
    print("PlaceIDs written to earthquakes.")


if __name__ == "__main__":
    main()
