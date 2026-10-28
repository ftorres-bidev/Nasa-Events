import requests
import json
import pandas as pd
import reverse_geocoder as rg
import pycountry
from sqlalchemy import text
from db import get_engine
from sqlalchemy import create_engine, types as T
from sqlalchemy.engine import URL
from sqlalchemy.dialects.mssql import DATETIME2


#Getting the data from database

table1 = "bronze_earthquakes"
engine = get_engine()

df_earthquakes = pd.read_sql(f"SELECT ID, Lat, Lon FROM dbo.{table1}", engine)
df_earthquakes['Source'] = 'usgs'
print(df_earthquakes.head(5))

# Find the nearest place for every event
coords = list(zip(df_earthquakes['Lat'], df_earthquakes['Lon']))
results = rg.search(coords, mode=1)

df_earthquakes['PlaceName']   = [r['name'] for r in results]
df_earthquakes['State']       = [r['admin1'] or '' for r in results]
df_earthquakes['CountryCode'] = [r['cc'] for r in results]
place_lat = [float(r['lat']) for r in results]
place_lon = [float(r['lon']) for r in results]

# Distinct places only
places = (
    df_earthquakes[['PlaceName', 'State', 'CountryCode']]
    .assign(PlaceLat=place_lat, PlaceLon=place_lon)
    .drop_duplicates(subset=['PlaceName', 'State', 'CountryCode'])
    .rename(columns={'PlaceLat': 'Lat', 'PlaceLon': 'Lon'})
)
places['Country'] = places['CountryCode'].map(
    lambda c: pycountry.countries.get(alpha_2=c).name if pycountry.countries.get(alpha_2=c) else c
)

print(places.head(5))



key = ['PlaceName', 'State', 'CountryCode']

# 1. Load only places that aren't in bronze_places yet
existing = pd.read_sql("SELECT PlaceName, State, CountryCode FROM dbo.bronze_places", engine)
new_places = (places.merge(existing, on=key, how='left', indicator=True)
                    .query("_merge == 'left_only'").drop(columns='_merge'))
new_places.to_sql("bronze_places", engine, schema="dbo", if_exists="append", index=False)

# 2. Read the generated PlaceIDs back and attach them to every row
place_ids = pd.read_sql("SELECT PlaceID, PlaceName, State, CountryCode FROM dbo.bronze_places", engine)
df_earthquakes = df_earthquakes.merge(place_ids, on=key, how='left', validate='many_to_one')

# 3. Write PlaceID onto the existing rows through a temporary staging table
mapping = df_earthquakes[['ID', 'Source', 'PlaceID']].dropna(subset=['PlaceID'])
mapping['PlaceID'] = mapping['PlaceID'].astype(int)
mapping.to_sql("stg_place_map", engine, schema="dbo", if_exists="replace", index=False,
               dtype={'ID': T.NVARCHAR(50), 'Source': T.NVARCHAR(10)})

with engine.begin() as conn: 
    conn.execute(text("""
        UPDATE q SET q.PlaceID = m.PlaceID
        FROM dbo.bronze_earthquakes q
        JOIN dbo.stg_place_map m
          ON m.Source = 'usgs' AND m.ID = q.ID;
    """))
    conn.execute(text("DROP TABLE dbo.stg_place_map"))




