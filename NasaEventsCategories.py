import requests
import json
import pandas as pd
from db import get_engine 

URL = 'https://eonet.gsfc.nasa.gov/api/v3/events/geojson'

response = requests.get(URL,timeout=30, headers={'accept':'application/json'})

data = response.json()
events = data['features']
df_events = pd.json_normalize(events)
categories = df_events[[ 'properties.categories']]
categories.rename(columns={
    'properties.categories': 'CategoryId',
    }, inplace=True)

categories['CategoryID'] = categories['CategoryId'].apply(lambda row: row[0]['id'])
categories['Title'] = categories['CategoryId'].apply(lambda row: row[0]['title'])
categories = categories.drop(columns=['CategoryId'])
#print(df_categories.head(5))

df_categories = categories.drop_duplicates(subset=['CategoryID', 'Title']).reset_index(drop=True)

engine = get_engine()

with engine.connect() as conn:
    print("Connected!")

df_categories.to_sql(
    'bronze_categories', 
    engine, if_exists='replace', index=False)