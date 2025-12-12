import os

import fastf1
import pandas as pd


def main() -> None:
    cache_path = "/Volumes/SAMSUNG/apps/f1-dash/fastf1_cache"
    os.makedirs(cache_path, exist_ok=True)
    fastf1.Cache.enable_cache(cache_path)

    year = 2023
    event_name = "Bahrain"
    session_type = "R"

    print(f"[info] Requesting session year={year}, event='{event_name}', session_type='{session_type}'")
    session = fastf1.get_session(year, event_name, session_type)
    print(f"[info] Retrieved session object: event='{session.event['EventName']}', session_name='{session.name}'")
    print("[info] Loading session data (telemetry=False, weather=False). First run may be slow due to downloads...")
    session.load(telemetry=False, weather=False)

    laps: pd.DataFrame = session.laps
    print(f"[info] Laps DataFrame shape: {laps.shape}")
    preview_cols = [c for c in ["DriverNumber", "Driver", "LapNumber", "LapTime"] if c in laps.columns]
    if preview_cols:
        print(f"[info] Preview of laps[{preview_cols}]:")
        print(laps[preview_cols].head())
    else:
        print("[info] Requested preview columns not present in laps DataFrame.")


if __name__ == "__main__":
    main()
