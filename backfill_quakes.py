"""Backfill historical USGS earthquakes into dbo.bronze_earthquakes, one month at a time.

Why: one big request (e.g. 2020 to 2026, all magnitudes) overloads the USGS server
(503 "table is full") and can exceed the 20,000-events-per-query cap. Monthly windows
with a minimum magnitude stay well below both.

Safe to re-run: IDs already in the table are skipped, so it resumes where it stopped.
Reuses fetch_quakes() from load_quakes.py (earthquakes only, raw epoch ms times).
"""
import time
from datetime import date

import pandas as pd
import requests

from db import get_engine
from NasaEarthquakes import TABLE, fetch_quakes

BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
START = date(2020, 1, 1)
END = date.today()
MIN_MAGNITUDE = 4.5       # lower to 2.5 for more detail (watch the 20,000-per-query cap)
RETRIES = 4


def month_windows(start: date, end: date):
    """Yield (first day of month, first day of next month) up to `end`."""
    cur = date(start.year, start.month, 1)
    while cur <= end:
        nxt = date(cur.year + (cur.month == 12), cur.month % 12 + 1, 1)
        yield cur, nxt
        cur = nxt


def fetch_window(start: date, end: date) -> pd.DataFrame:
    url = (f"{BASE_URL}?format=geojson&starttime={start}&endtime={end}"
           f"&minmagnitude={MIN_MAGNITUDE}&orderby=time-asc")
    for attempt in range(1, RETRIES + 1):
        try:
            return fetch_quakes(url)
        except requests.RequestException as exc:
            wait = 5 * attempt
            print(f"  {start}: attempt {attempt} failed ({exc}); retrying in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"Window {start} to {end} failed after {RETRIES} attempts")


def main():
    engine = get_engine()
    known = set(pd.read_sql(f"SELECT ID FROM dbo.{TABLE}", engine)["ID"])
    total = 0

    for start, end in month_windows(START, END):
        df = fetch_window(start, end)
        new_rows = df[~df["ID"].isin(known)]
        if not new_rows.empty:
            new_rows.to_sql(TABLE, engine, schema="dbo", if_exists="append", index=False)
            known.update(new_rows["ID"])
        total += len(new_rows)
        print(f"{start:%Y-%m}: {len(df)} fetched, {len(new_rows)} new")
        time.sleep(1)                      # be polite to the USGS service

    print(f"Done. {total} new earthquakes loaded.")


if __name__ == "__main__":
    main()
