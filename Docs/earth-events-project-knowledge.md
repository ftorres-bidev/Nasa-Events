# Earth Events & Earthquakes: Project Knowledge

## 1. Project overview
ETL project (Python + SQL Server, bronze layer) that loads:
- **NASA EONET events** (`https://eonet.gsfc.nasa.gov/api/v3/events/geojson`) into `dbo.events`
- **USGS earthquakes** (GeoJSON summary feeds) into `bronze.earthquakes`
- A shared **places** table (`bronze.places`) that both datasets link to via `PlaceID`

Environment: Windows, local SQL Server 2019 (`localhost`, database `NasaEvents`), VS Code, SSMS.

## 2. Python environment
- Python 3.15 is too new: pyyaml/pywinpty have no prebuilt wheels, so `pip install notebook` fails. Use **Python 3.12 or 3.13**.
- Create a venv per project:
  ```
  py -3.12 -m venv .venv
  .venv\Scripts\activate
  python -m pip install --upgrade pip
  pip install requests pandas sqlalchemy pyodbc notebook ipykernel reverse_geocoder pycountry
  ```
- An old `.venv` pointed to a deleted Anaconda Python ("No Python at ...anaconda3\python.exe"). Delete and recreate the venv when this happens.
- In VS Code: Ctrl+Shift+P > Python: Select Interpreter > pick `.venv`.
- Jupyter is installed once per venv; each session just activate the venv and run `jupyter notebook` (or use `.ipynb` in VS Code with ipykernel).
- Comment lines in VS Code: Ctrl + /

## 3. SQL Server connection (SQLAlchemy + pyodbc)
```python
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

connection_url = URL.create(
    "mssql+pyodbc",
    host="localhost",                      # or r"localhost\SQLEXPRESS"
    database="NasaEvents",
    query={
        "driver": "ODBC Driver 17 for SQL Server",
        "trusted_connection": "yes",
        "TrustServerCertificate": "yes",
    },
)
engine = create_engine(connection_url, fast_executemany=True)
```
Errors seen and meaning:
- `IM002 Data source name not found`: driver name doesn't match `pyodbc.drivers()`.
- `08001 Error Locating Server/Instance`: wrong server name or service stopped; check name in SSMS.

## 4. EONET data shape
- Each row in the GeoJSON is one **point on an event's track**, so `ID` is NOT unique. Primary key is `(ID, EventDate)`.
- `properties.closed` is a close date (null while open), not a status. Consider renaming to `ClosedDate` (DATETIME2).
- `properties.categories` is a list of dicts: `[{'id': 'wildfires', 'title': 'Wildfires'}]`.
  ```python
  df['categoryId'] = df['CategoryId'].str[0].str['id']
  df['categoryTitle'] = df['CategoryId'].str[0].str['title']
  ```
- Geometry can be `Point` or `Polygon`. For Polygons, `Coordinates` is a nested list, which broke `pd.to_numeric` (TypeError at position 619). Either keep only Points, or compute an approximate centroid from the outer ring.
- Dates come back timezone-aware (UTC). Before loading: `df['EventDate'] = df['EventDate'].dt.tz_localize(None)`.

## 5. Table design and gotchas
- SQL Server `TIMESTAMP` is a row-version counter, not a date. pandas auto-created `EventDate` as `timestamp`, causing "Cannot insert an explicit value into a timestamp column". Fix: create the table yourself with `DATETIME2`, and load with `if_exists="append"` (never `"replace"`, which recreates the table with pandas' types).
- pandas defaults text to `VARCHAR(max)`; define types explicitly.

```sql
CREATE TABLE dbo.events (
    ID             NVARCHAR(50)  NOT NULL,
    Title          NVARCHAR(500) NULL,
    Status         NVARCHAR(50)  NULL,
    EventDate      DATETIME2     NOT NULL,
    MagnitudeValue FLOAT         NULL,
    MagnitudeUnit  NVARCHAR(50)  NULL,
    GeometryType   NVARCHAR(50)  NULL,
    categoryId     NVARCHAR(50)  NULL,
    Lon            FLOAT         NULL,
    Lat            FLOAT         NULL,
    CONSTRAINT PK_events PRIMARY KEY (ID, EventDate)
);

CREATE SCHEMA bronze;  -- must be in its own batch (use EXEC('CREATE SCHEMA bronze'))

CREATE TABLE bronze.categories (
    CategoryID  NVARCHAR(50)  NOT NULL,
    Description NVARCHAR(200) NULL,
    CONSTRAINT PK_bronze_categories PRIMARY KEY (CategoryID)
);
```
- Categories lookup from the dataframe:
  ```python
  categories = (pd.json_normalize(df_events['CategoryId'].explode())
                .drop_duplicates()
                .rename(columns={'id': 'CategoryID', 'title': 'Description'}))
  categories.to_sql("categories", engine, schema="bronze", if_exists="append", index=False)
  ```
- Re-running with a primary key fails on existing rows: TRUNCATE first, or stage + MERGE.

## 6. Places table (shared by events and earthquakes)
```sql
CREATE TABLE bronze.places (
    PlaceID      INT IDENTITY(1,1) NOT NULL,
    PlaceName    NVARCHAR(200) NOT NULL,
    State        NVARCHAR(100) NOT NULL DEFAULT '',
    CountryCode  NCHAR(2)      NOT NULL,
    Country      NVARCHAR(100) NULL,
    Lat          FLOAT NULL,
    Lon          FLOAT NULL,
    CONSTRAINT PK_bronze_places PRIMARY KEY (PlaceID),
    CONSTRAINT UQ_bronze_places UNIQUE (PlaceName, State, CountryCode)
);

ALTER TABLE dbo.events ADD PlaceID INT NULL;
ALTER TABLE dbo.events ADD CONSTRAINT FK_events_places
    FOREIGN KEY (PlaceID) REFERENCES bronze.places(PlaceID);

ALTER TABLE bronze.earthquakes ADD PlaceID INT NULL;
ALTER TABLE bronze.earthquakes ADD CONSTRAINT FK_quakes_places
    FOREIGN KEY (PlaceID) REFERENCES bronze.places(PlaceID);
```
Workflow:
1. Standardize both sources to `Lat`, `Lon`; concat and geocode in one batch with `reverse_geocoder.search(coords, mode=1)` (mode=1 avoids Windows multiprocessing problems; coords are `(lat, lon)`).
2. Build distinct places (PlaceName, State, CountryCode), map country code to name with `pycountry`, load only new places.
3. Read back `PlaceID`s and merge onto each dataframe, drop the helper columns, then load events and earthquakes.

Caveats:
- `reverse_geocoder` returns the **nearest GeoNames city**, not a boundary match; rural/ocean events get the closest town, possibly the wrong country near borders.
- More accurate: point-in-polygon with Natural Earth Admin 1 shapefile via geopandas (`sjoin`, predicate `within`); unmatched points = ocean.
- Other place datasets: GeoNames (`cities1000.zip`), Natural Earth, Simplemaps World Cities, US Census Gazetteer / USGS GNIS.

## 7. USGS earthquake data
Feeds: `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/{all_hour|all_day|all_week|all_month}.geojson`
Docs: GeoJSON Summary format (`.../earthquakes/feed/v1.0/geojson.php`), event terms (`.../data/comcat/data-eventterms.php`), FDSN Event API (`.../fdsnws/event/1/`).

Key fields: `id` (on the feature, not in properties; use as PK), `mag`, `magType`, `place` (text like "10 km SW of Ridgecrest, CA"), `time` and `updated` (ms since 1970 UTC), `status` (automatic/reviewed), `tsunami`, `sig`, `felt`/`cdi`/`mmi`/`alert` (often null), `nst`/`gap`/`dmin`/`rms`, `type`, `title`.

Notes:
- Geometry is `[longitude, latitude, depth_km]`.
- Convert time: `pd.to_datetime(df['time'], unit='ms')` (already timezone-naive).
- Filter `type == "earthquake"` to exclude quarry blasts/explosions.
- Events get revised by USGS, so re-loading the same `id` can change values.
- Many quakes are at sea, so nearest-city places are approximate.

## 8. Pandas snippets
- DataFrame from a list of tuples: `pd.DataFrame(rows, columns=[...])`; single tuple needs wrapping: `pd.DataFrame([t], columns=[...])`.
- Read SQL: `pd.read_sql("SELECT * FROM dbo.events", engine)`.

## 9. Dashboard options (not built yet)
- Static: export tables to CSV and have Claude build an HTML dashboard.
- Live: Streamlit + Plotly app querying SQL Server with the same `engine`.
- Power BI Desktop connecting directly to SQL Server.
Claude cannot connect to a local database; share exported CSVs instead.

## 10. Open items
- Create `bronze.earthquakes` table (need `df_quakes.columns` to define types).
- Build combined geocoding + places load for both sources.
- Decide refresh strategy (truncate and reload vs. merge/upsert).
- Optional: rename EONET `Status` to `ClosedDate`; add `categoryTitle`; move `events` into `bronze` schema.
