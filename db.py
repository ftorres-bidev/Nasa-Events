"""SQL Server connection (SQLAlchemy + pyodbc, Windows authentication)."""
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

SERVER = "localhost"          # or r"localhost\SQLEXPRESS"
DATABASE = "NasaEvents"
DRIVER = "ODBC Driver 17 for SQL Server"   # must match pyodbc.drivers()


def get_engine():
    connection_url = URL.create(
        "mssql+pyodbc",
        host=SERVER,
        database=DATABASE,
        query={
            "driver": DRIVER,
            "trusted_connection": "yes",
            "TrustServerCertificate": "yes",
        },
    )
    return create_engine(connection_url, fast_executemany=True)
