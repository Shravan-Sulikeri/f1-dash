import duckdb
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    warehouse_path = repo_root / "warehouse" / "f1_openf1.duckdb"
    con = duckdb.connect(str(warehouse_path))
    con.execute("CREATE SCHEMA IF NOT EXISTS silver;")

    con.execute(
        """
        CREATE OR REPLACE TABLE silver.driver_race_clean AS
        WITH base AS (
          SELECT
            season::INT AS season,
            COALESCE(round::INT,
                     DENSE_RANK() OVER (PARTITION BY season ORDER BY grand_prix_slug)) AS round,
            grand_prix_slug,
            driver_code,
            driver_name,
            team_name,
            grid_position,
            finish_position,
            points AS points_race,
            NULL::DOUBLE AS track_temp_c,
            NULL::DOUBLE AS rain_probability,
            ingested_at AS event_date
          FROM bronze.session_result
          WHERE session_code = 'R'
            AND season BETWEEN 2018 AND 2025
        ),
        ordered AS (
          SELECT
            *,
            ROW_NUMBER() OVER (
              PARTITION BY season, round, driver_code
              ORDER BY event_date
            ) AS rn
          FROM base
        )
        SELECT * FROM ordered WHERE rn = 1;
        """
    )

    res = con.execute(
        """
        SELECT
          COUNT(*) AS n,
          MIN(season) AS min_season,
          MAX(season) AS max_season,
          SUM(CASE WHEN (grid_position IS NULL) OR (finish_position IS NULL) THEN 1 ELSE 0 END) AS null_core
        FROM silver.driver_race_clean;
        """
    ).fetchone()
    print("[silver] rows=%s seasons=%s-%s null_core=%s" % res)


if __name__ == "__main__":
    main()
