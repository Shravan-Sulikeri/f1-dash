import duckdb
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    db_path = repo_root / "warehouse" / "f1_openf1.duckdb"
    print(f"[info] Connecting to DuckDB warehouse at {db_path}")
    con = duckdb.connect(str(db_path))

    con.execute("CREATE SCHEMA IF NOT EXISTS features;")

    sql = """
    CREATE OR REPLACE VIEW features.race_win_training_enriched AS
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
            COALESCE(track_temp_c, 0) AS track_temp_c,
            COALESCE(rain_probability, 0) AS rain_probability,
            event_date,
            target_win_race,
            target_top3
        FROM gold.race_winner_top3
    ),
    form AS (
        SELECT
            season,
            driver_code,
            round,
            AVG(finish_position) OVER (
                PARTITION BY season, driver_code
                ORDER BY round
                ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
            ) AS driver_avg_finish_last_3,
            SUM(points_race) OVER (
                PARTITION BY season, driver_code
                ORDER BY round
                ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
            ) AS driver_points_last_3,
            SUM(points_race) OVER (
                PARTITION BY season, driver_code
                ORDER BY round
                ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
            ) AS driver_points_to_date
        FROM base
    ),
    team_form AS (
        SELECT
            season,
            team_name,
            round,
            SUM(points_race) OVER (
                PARTITION BY season, team_name
                ORDER BY round
                ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
            ) AS team_points_last_3,
            SUM(points_race) OVER (
                PARTITION BY season, team_name
                ORDER BY round
                ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
            ) AS team_points_to_date
        FROM base
    ),
    track_form AS (
        SELECT
            season,
            grand_prix_slug,
            driver_code,
            team_name,
            round,
            AVG(finish_position) OVER (
                PARTITION BY grand_prix_slug, driver_code
                ORDER BY season, round
                ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
            ) AS driver_track_avg_finish_last_3_at_gp,
            SUM(points_race) OVER (
                PARTITION BY grand_prix_slug, driver_code
                ORDER BY season, round
                ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
            ) AS driver_track_points_last_3_at_gp,
            SUM(points_race) OVER (
                PARTITION BY grand_prix_slug, team_name
                ORDER BY season, round
                ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
            ) AS team_track_points_last_3_at_gp
        FROM base
    ),
    raw_enriched AS (
        SELECT
            b.season,
            b.round,
            b.grand_prix_slug,
            b.driver_code,
            b.driver_name,
            b.team_name,
            b.grid_position,
            b.finish_position,
            b.points_race,
            b.track_temp_c,
            b.rain_probability,
            b.target_win_race,
            b.target_top3,
            f.driver_avg_finish_last_3,
            f.driver_points_last_3,
            f.driver_points_to_date,
            tf.team_points_last_3,
            tf.team_points_to_date,
            tfm.driver_track_avg_finish_last_3_at_gp,
            tfm.driver_track_points_last_3_at_gp,
            tfm.team_track_points_last_3_at_gp,
            MAX(b.grid_position) OVER (
                PARTITION BY b.season, b.round, b.grand_prix_slug
            ) AS max_grid_position,
            ROW_NUMBER() OVER (
                PARTITION BY b.season, b.round, b.grand_prix_slug, b.driver_code
                ORDER BY b.event_date
            ) AS rn
        FROM base b
        LEFT JOIN form f
          ON b.season = f.season
         AND b.round = f.round
         AND b.driver_code = f.driver_code
        LEFT JOIN team_form tf
          ON b.season = tf.season
         AND b.round = tf.round
         AND b.team_name = tf.team_name
        LEFT JOIN track_form tfm
          ON b.season = tfm.season
         AND b.round = tfm.round
         AND b.grand_prix_slug = tfm.grand_prix_slug
         AND b.driver_code = tfm.driver_code
         AND b.team_name = tfm.team_name
    )
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
        driver_avg_finish_last_3,
        driver_points_last_3,
        driver_points_to_date,
        team_points_last_3,
        team_points_to_date,
        driver_track_avg_finish_last_3_at_gp,
        driver_track_points_last_3_at_gp,
        team_track_points_last_3_at_gp,
        CASE
            WHEN max_grid_position IS NULL OR max_grid_position = 0 THEN NULL
            ELSE grid_position::DOUBLE / max_grid_position::DOUBLE
        END AS grid_position_norm,
        target_win_race,
        target_top3
    FROM raw_enriched
    WHERE rn = 1;
    """

    con.execute(sql)

    count = con.execute("SELECT COUNT(*) FROM features.race_win_training_enriched").fetchone()[0]
    print(f"[info] features.race_win_training_enriched row count: {count}")
    preview = con.execute(
        "SELECT season, round, grand_prix_slug, driver_code, grid_position, "
        "track_temp_c, rain_probability, driver_avg_finish_last_3, driver_points_last_3, "
        "team_points_last_3, driver_track_avg_finish_last_3_at_gp, "
        "driver_track_points_last_3_at_gp, team_track_points_last_3_at_gp, grid_position_norm, "
        "target_win_race, target_top3 "
        "FROM features.race_win_training_enriched "
        "ORDER BY season, round, driver_code "
        "LIMIT 5"
    ).fetchdf()
    print("[info] features.race_win_training_enriched preview:")
    print(preview)

    # Validate uniqueness for season >= 2018
    row_count = con.execute(
        "SELECT COUNT(*) FROM features.race_win_training_enriched WHERE season >= 2018"
    ).fetchone()[0]
    distinct_count = con.execute(
        """
        SELECT COUNT(*) FROM (
          SELECT season, round, grand_prix_slug, driver_code
          FROM features.race_win_training_enriched
          WHERE season >= 2018
          GROUP BY season, round, grand_prix_slug, driver_code
        )
        """
    ).fetchone()[0]
    print(f"[info] season>=2018 row_count={row_count}, distinct_key_count={distinct_count}")
    if row_count != distinct_count:
        print("[warn] race_win_training_enriched has duplicate keys for season>=2018")


if __name__ == "__main__":
    main()
