import requests
import json
import pandas as pd

URL = 'https://eonet.gsfc.nasa.gov/api/v3/events/geojson'

response = requests.get(URL,timeout=30, headers={'accept':'application/json'})

data = response.json()

events = data['features']
df_events = pd.json_normalize(events)
df_events = df_events[['properties.id', 'properties.title', 'properties.closed', 'properties.date', 'properties.categories','properties.magnitudeValue','properties.magnitudeUnit', 'geometry.type', 'geometry.coordinates']]
df_events.info()
df_events.rename(columns={
    'properties.id': 'ID',
    'properties.title': 'Title',
    'properties.closed': 'Status',
    'properties.date': 'EventDate',
    'properties.categories': 'CategoryId',
    'properties.magnitudeValue': 'MagnitudeValue',
    'properties.magnitudeUnit': 'MagnitudeUnit', 
    'geometry.type': 'GeometryType', 
    'geometry.coordinates': 'Coordinates'
    }, inplace=True)

df_events['categoryId'] = df_events['CategoryId'].apply(lambda c: c[0]['id'])
df_events['EventDate'] = pd.to_datetime(df_events['EventDate'])
df_events = df_events[df_events['GeometryType'] == 'Point'].copy()
df_events['Lon'] = df_events['Coordinates'].str[0]
df_events['Lat'] = df_events['Coordinates'].str[1]
df_events = df_events.drop(columns=['CategoryId', 'Coordinates'])
df_events['Lon'] = pd.to_numeric(df_events['Lon'])
df_events['Lat'] = pd.to_numeric(df_events['Lat'])
df_events['EventDate'] = df_events['EventDate'].dt.tz_localize(None)
df_events = df_events.drop_duplicates(subset=['ID', 'EventDate'])



print(df_events.head(5))

# from sqlalchemy import create_engine, types as T
# from sqlalchemy.engine import URL

# connection_url = URL.create(
#     "mssql+pyodbc",
#     host=r"localhost",   # or just "localhost"
#     database="NasaEvents",
#     username="felip",  # replace with your username
#     password="1990",  # replace with your password
#     query={
#         "driver": "ODBC Driver 17 for SQL Server",
#         "trusted_connection": "yes",      
#         "TrustServerCertificate": "yes",
#     },
# )

# engine = create_engine(connection_url)
# with engine.connect() as conn:
#     print("Connected!")



# df_events.to_sql(
#     "bronze_events",
#     engine,
#     if_exists="append",   # creates the table if missing, otherwise adds rows
#     index=False,
    
# )




