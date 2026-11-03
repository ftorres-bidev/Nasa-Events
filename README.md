## Earth Events & Earthquakes Data Warehouse

A hands-on data engineering project that uses **Python as an ETL tool** to extract public natural-event data, transform it, and load it into **SQL Server** using a **medallion (bronze / silver / gold) architecture**.

### Objective

Practice the full ETL cycle end to end: calling REST APIs, flattening nested GeoJSON, geocoding coordinates, loading into SQL Server, and building cleaned and reporting-ready layers with T-SQL. The project is a one-off run, so it focuses on design and transformation quality rather than scheduling or orchestration.

### Data sources

| Source | Content | Endpoint |
| --- | --- | --- |
| NASA EONET | Natural events (wildfires, storms, volcanoes, floods, ...) with categories and dated observations | `https://eonet.gsfc.nasa.gov/api/v3/events/geojson` |
| USGS | Earthquakes with magnitude, depth, time, coordinates, tsunami flag and significance | `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/{feed}.geojson` |

Both sources are linked through a shared **places** table (nearest GeoNames city, state and country) so events and earthquakes can be analysed by country.

### Architecture

```
NASA EONET + USGS APIs
        |
   Python (extract, flatten, geocode, load)
        |
   bronze_*  tables   raw data as loaded
        |
   T-SQL scripts (INSERT ... SELECT)
        |
   silver_*  tables   cleaned, keyed, readable
        |
   T-SQL views
        |
   Gold_*    views    reporting layer
```

| Layer | Objects | Purpose |
| --- | --- | --- |
| Bronze | `bronze_events`, `bronze_earthquakes`, `bronze_categories`, `bronze_places` | Receives the full source data |
| Silver | `silver_places`, `silver_categories`, `silver_earthquakes`, `silver_events` | Cleansing, type conversion, primary keys and foreign keys |
| Gold | `Gold_dim_places`, `Gold_dim_categories`, `Gold_fact_earthquakes`, `Gold_fact_natural_event`, `Gold_fact_topHighest_earthquakes` | Dimensions and facts exposed as views |

All objects live in the `NasaEvents` database, `dbo` schema, separated by name prefix.

### Key points

- **Python handles extract and load.** Requests, pandas flattening, timezone removal, geocoding (`reverse_geocoder`, `pycountry`) and loading through SQLAlchemy + pyodbc.
- **T-SQL handles silver and gold.** Silver is filled with `INSERT ... SELECT` scripts; gold is a set of views over silver with explicit column lists.
- **EONET observations.** Each EONET event can have several observations, so `EventID` is not unique. Silver adds a deterministic `ObservationGuid` (first 16 bytes of SHA-256 over `EventID | EventDate`).
- **USGS cleaning.** Epoch milliseconds converted to UTC datetimes, magnitude rounded to 2 decimals, missing alert set to `n/a`, magnitude type codes expanded to readable descriptions.
- **Gold facts.** Earthquakes per row, EONET observations aggregated by category, country, year and month, and the top 10 countries per year by strongest earthquake.

### Run order

1. Silver DDL: `Create_silver_places.sql`, then `Create_silver_categories.sql` and `Create_silver_earthquakes.sql`, then `Create_silver_events.sql`
2. Silver loads: `silver_places.sql`, then `silver_categories.sql` and `silver_earthquakes.sql`, then `silver_events.sql`
3. Gold views: the two dimensions, `Gold_fact_earthquakes` and `Gold_fact_natural_event`, then `Gold_fact_topHighest_earthquakes`

### Tech stack

Python 3.12/3.13, requests, pandas, SQLAlchemy, pyodbc, reverse_geocoder, pycountry, SQL Server 2019, T-SQL, SSMS, VS Code.

### Known limitations

- Places come from the nearest GeoNames city, so offshore or border-area events can be assigned to a nearby country.
- `Gold_fact_natural_event` counts observations, not distinct events.
- Silver loads are plain inserts into empty tables (run once).

### Documentation

Full process documentation (design, transformations, decisions): `Earth_Events_Documentation_Structure.docx`.
