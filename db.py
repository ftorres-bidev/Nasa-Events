"""Shared SQL Server connection (SQLAlchemy + pyodbc, Windows authentication).

Every loader script imports `get_engine` from here so the connection
settings live in exactly one place.
"""
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# --- Connection settings -----------------------------------------------------
SERVER = "localhost"                       # or r"localhost\SQLEXPRESS"
DATABASE = "NasaEvents"
DRIVER = "ODBC Driver 17 for SQL Server"   # must match an entry in pyodbc.drivers()


def get_engine():
    """Return a SQLAlchemy engine for the NasaEvents database.

    Uses Windows (trusted) authentication, so no username or password is
    needed in the code. `fast_executemany` makes bulk inserts much faster.
    """
    connection_url = URL.create(
        "mssql+pyodbc",
        host=SERVER,
        database=DATABASE,
        query={
            "driver": DRIVER,
            "trusted_connection": "yes",        # Windows authentication
            "TrustServerCertificate": "yes",    # accept the local dev certificate
        },
    )
    return create_engine(connection_url, fast_executemany=True)
