import os
import sys
from pathlib import Path

import duckdb


def main() -> None:
    data_root = os.getenv("EXTERNAL_DATA_ROOT")

    # Fallback based on user-provided path (bronze lives here under /bronze).
    if not data_root:
        data_root = "/Volumes/SAMSUNG/apps/f1-dash"

    bronze_root = Path(data_root) / "bronze"
    laps_glob = bronze_root / "laps" / "**" / "*.parquet"

    if not bronze_root.exists():
        print(f"[error] Bronze root does not exist: {bronze_root}")
        print("Set EXTERNAL_DATA_ROOT or adjust the fallback path in this script.")
        sys.exit(1)

    matching_files = list(bronze_root.glob("laps/**/*.parquet"))
    if not matching_files:
        print(f"[info] No Parquet files found at {laps_glob}. Nothing to sample.")
        return

    con = duckdb.connect(database=":memory:")

    # Sample rows
    try:
        sample_df = con.execute(
            f"select * from read_parquet('{laps_glob}', hive_partitioning=1) limit 5"
        ).fetchdf()
    except Exception as exc:
        print(f"[error] Failed to read sample from {laps_glob}: {exc}")
        return

    print(f"[sample] rows: {len(sample_df)}")
    print(f"[sample] columns: {list(sample_df.columns)}")
    if not sample_df.empty:
        print("[sample] data:")
        print(sample_df)

    # Distinct session identifiers
    try:
        combos_df = con.execute(
            f"""
            select distinct season, round, grand_prix_slug, session_code
            from read_parquet('{laps_glob}', hive_partitioning=1)
            limit 20
            """
        ).fetchdf()
    except Exception as exc:
        print(f"[error] Failed to read distinct combos from {laps_glob}: {exc}")
        return

    print("[distinct] first 20 (season, round, grand_prix_slug, session_code):")
    if combos_df.empty:
        print("  (none)")
    else:
        for _, row in combos_df.iterrows():
            print(
                f"  season={row['season']}, round={row['round']}, "
                f"grand_prix_slug={row['grand_prix_slug']}, session_code={row['session_code']}"
            )


if __name__ == "__main__":
    main()
