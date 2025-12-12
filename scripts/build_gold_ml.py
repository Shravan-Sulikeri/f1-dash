import duckdb
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    warehouse_path = repo_root / "warehouse" / "f1_openf1.duckdb"
    con = duckdb.connect(str(warehouse_path))
    con.execute("CREATE SCHEMA IF NOT EXISTS gold;")

    con.execute(
        """
        CREATE OR REPLACE TABLE gold.race_winner_top3 AS
        WITH base AS (
          SELECT
            season,
            round,
            grand_prix_slug,
            driver_code,
            driver_name,
            team_name,
            grid_position,
            finish_position,
            points_race,
            track_temp_c,
            rain_probability,
            event_date
          FROM silver.driver_race_clean
        ),
        features AS (
          SELECT
            *,
            CASE WHEN finish_position = 1 THEN 1 ELSE 0 END AS target_win_race,
            CASE WHEN finish_position <= 3 THEN 1 ELSE 0 END AS target_top3
          FROM base
        )
        SELECT * FROM features;
        """
    )

    rows = con.execute("SELECT COUNT(*) FROM gold.race_winner_top3;").fetchone()[0]
    print("[gold] rows=", rows)


if __name__ == "__main__":
    main()
