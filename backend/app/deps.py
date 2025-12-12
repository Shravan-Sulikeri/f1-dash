from typing import Generator

import duckdb

from .db import connect_ro


def get_db() -> Generator[duckdb.DuckDBPyConnection, None, None]:
    con = connect_ro()
    try:
        yield con
    finally:
        con.close()
