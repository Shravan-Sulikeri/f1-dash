
import duckdb
import pandas as pd

BRONZE_DIR = '/Volumes/SAMSUNG/apps/f1-dash/bronze'

def read_bronze(sql: str, params=None):
    params = params or []
    if not BRONZE_DIR:
        raise Exception(f"Bronze directory not found")
    con = duckdb.connect(":memory:")
    try:
        cur = con.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    except duckdb.Error as exc:
        raise Exception(str(exc))
    finally:
        con.close()

sql = f"""
SELECT DISTINCT season, round, grand_prix_slug, session_code, session_name
FROM read_parquet('{BRONZE_DIR}/sessions/season=*/round=*/grand_prix=*/session=*/part-*.parquet')
WHERE season = 2024 AND round = 1
"""

rows = read_bronze(sql)
print(pd.DataFrame(rows))
