import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import requests

# Basic logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("openf1_ingestion")


def _snake_case(s: str) -> str:
    s = s.replace(" ", "_").replace("-", "_")
    s = re.sub(r"(?<!^)(?=[A-Z])", "_", s)
    s = re.sub("_+", "_", s)
    return s.lower()


def _normalize_records(records: list[dict]) -> list[dict]:
    return [{_snake_case(k): v for k, v in rec.items()} for rec in records]


def _normalize_team_name(name: Optional[str]) -> Optional[str]:
    if not name:
        return name
    return "Visa Cash App Racing Bulls" if name.strip().upper() == "RB" else name


def _sanitize_df_for_parquet(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure columns have Arrow-friendly types.
    - If an object column has mixed types or list/dict values, cast whole column to string.
    This keeps bronze close to raw while avoiding ArrowInvalid errors (e.g. '+1 LAP' vs float).
    """
    for col in df.columns:
        series = df[col]
        if not isinstance(series.dtype, pd.api.types.CategoricalDtype) and not pd.api.types.is_object_dtype(series):
            # Non-object dtypes (numeric, datetime, bool) are fine.
            continue
        non_null = series.dropna()
        if non_null.empty:
            continue
        types_in_col = {type(x) for x in non_null}
        if len(types_in_col) > 1 or any(isinstance(x, (list, dict)) for x in non_null):
            df[col] = series.astype(str)
    return df


def _parse_int_list(value: str) -> list[int]:
    return [int(v.strip()) for v in value.split(",") if v.strip()]


def _parse_str_list(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def _slugify(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    return name or "unknown"


def _derive_session_code(session_name: Optional[str], session_type: Optional[str]) -> Optional[str]:
    name = (session_name or "").lower()
    stype = (session_type or "").lower()

    def match(val: str) -> Optional[str]:
        if "practice 1" in val:
            return "FP1"
        if "practice 2" in val:
            return "FP2"
        if "practice 3" in val:
            return "FP3"
        if val in {"practice", "fp", "free practice"}:
            return "FP"
        if "sprint shootout" in val or "sprint qualifying" in val:
            return "SQ"
        if val == "sprint":
            return "S"
        if "sprint" in val:
            return "S"
        if val == "qualifying" or "qualifying" in val:
            return "Q"
        if val == "race" or "race" in val:
            return "R"
        return None

    return match(name) or match(stype)


@dataclass
class IngestConfig:
    base_url: str
    seasons: list[int]
    session_codes: set[str]
    data_root: Path
    force_reingest: bool
    enable_car_data: bool
    enable_intervals: bool
    enable_overtakes: bool
    force_reingest_laps: bool
    driver_sleep_seconds: float
    max_meeting_key: int
    request_timeout: int = 30
    page_limit: int = 1000
    max_retries: int = 4
    backoff_seconds: float = 1.0


class OpenF1Client:
    def __init__(self, config: IngestConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "f1-openf1-backend/ingestion"})

    def _request(self, endpoint: str, params: list[tuple[str, Any]]) -> list[dict]:
        url = f"{self.config.base_url}/v1/{endpoint.lstrip('/')}"
        attempt = 0
        while True:
            try:
                resp = self.session.get(url, params=params, timeout=self.config.request_timeout)
                if resp.status_code in {429} or resp.status_code >= 500:
                    attempt += 1
                    if attempt > self.config.max_retries:
                        resp.raise_for_status()
                    sleep_s = self.config.backoff_seconds * (2 ** (attempt - 1))
                    logger.warning(
                        "Retrying %s (status=%s attempt=%s) in %.1fs",
                        url,
                        resp.status_code,
                        attempt,
                        sleep_s,
                    )
                    time.sleep(sleep_s)
                    continue
                resp.raise_for_status()
                data = resp.json()
                if not isinstance(data, list):
                    logger.error(
                        "Unexpected response for %s params=%s status=%s body=%s",
                        endpoint,
                        params,
                        resp.status_code,
                        resp.text[:500],
                    )
                    raise ValueError(f"Unexpected response type for {endpoint}: {type(data)}")
                return data
            except Exception as exc:
                attempt += 1
                if attempt > self.config.max_retries:
                    logger.error("Failed request %s params=%s error=%s", url, params, exc)
                    raise
                sleep_s = self.config.backoff_seconds * (2 ** (attempt - 1))
                logger.warning("Error on request %s (attempt %s): %s. Sleeping %.1fs", url, attempt, exc, sleep_s)
                time.sleep(sleep_s)

    def fetch_all(
        self,
        endpoint: str,
        base_params: dict | list[tuple[str, Any]],
        allow_pagination: bool = True,
    ) -> list[dict]:
        """
        Fetches all records for an endpoint.
        - If allow_pagination is False, sends a single request with provided params.
        - Some OpenF1 endpoints return empty when limit/offset are present, so we skip pagination there.
        """
        records: list[dict] = []

        def to_param_list(obj: dict | list[tuple[str, Any]]) -> list[tuple[str, Any]]:
            if isinstance(obj, dict):
                out: list[tuple[str, Any]] = []
                for k, v in obj.items():
                    if isinstance(v, (list, tuple)):
                        out.extend((k, item) for item in v)
                    else:
                        out.append((k, v))
                return out
            return list(obj)

        base_param_list = to_param_list(base_params)

        if not allow_pagination:
            return self._request(endpoint, params=base_param_list)

        offset = 0
        while True:
            params = base_param_list + [("limit", self.config.page_limit), ("offset", offset)]
            batch = self._request(endpoint, params=params)
            if not batch:
                break
            records.extend(batch)
            if len(batch) < self.config.page_limit:
                break
            offset += self.config.page_limit
        return records


class OpenF1Ingestor:
    def __init__(self, config: IngestConfig):
        self.config = config
        self.client = OpenF1Client(config)
        self.bronze_root = self.config.data_root / "bronze"
        self.ingested_at = datetime.utcnow().isoformat()
        self.lap_rows_written = 0

    def run(self) -> None:
        logger.info("Starting ingestion for seasons=%s session_codes=%s", self.config.seasons, self.config.session_codes)
        min_season = min(self.config.seasons)
        max_season = max(self.config.seasons)
        meetings = self._discover_meetings(min_season=min_season, max_season=max_season)
        if not meetings:
            logger.warning("No meetings discovered for seasons %s-%s", min_season, max_season)
            return

        meetings_sorted = sorted(meetings, key=lambda m: (m.get("date_start") or "", m.get("meeting_key")))
        meetings_by_season: dict[int, list[dict]] = {}
        for m in meetings_sorted:
            meetings_by_season.setdefault(m.get("year"), []).append(m)

        for season, season_meetings in meetings_by_season.items():
            self._ingest_season_meetings(season=int(season), meetings=season_meetings)
        logger.info("Ingestion completed. lap_rows_written=%s", self.lap_rows_written)

    def _discover_meetings(self, min_season: int, max_season: int) -> list[dict]:
        latest_key: Optional[int] = None
        try:
            latest = self.client.fetch_all("meetings", {"meeting_key": "latest"}, allow_pagination=False)
            if latest:
                latest_meeting = _normalize_records(latest)[0]
                latest_key = latest_meeting.get("meeting_key")
                logger.info("Latest meeting_key=%s year=%s", latest_key, latest_meeting.get("year"))
        except Exception as exc:
            logger.warning("Fetching latest meeting failed; will fall back to descending scan. Error: %s", exc)

        start_key = latest_key if latest_key is not None else self.config.max_meeting_key
        if start_key is None:
            logger.error("No start_key for meetings discovery; aborting.")
            return []

        meetings: list[dict] = []
        consecutive_misses = 0
        miss_threshold_after_found = 200
        found_any = False

        for meeting_key in range(start_key, 0, -1):
            try:
                batch = self.client.fetch_all(
                    "meetings", {"meeting_key": meeting_key}, allow_pagination=False
                )
            except Exception as exc:
                logger.warning("Fetch failed for meeting_key=%s: %s", meeting_key, exc)
                continue

            if not batch:
                consecutive_misses += 1
                if found_any and consecutive_misses >= miss_threshold_after_found:
                    break
                continue

            found_any = True
            consecutive_misses = 0
            norm = _normalize_records(batch)
            for m in norm:
                year = m.get("year")
                if year is None:
                    continue
                if year < min_season:
                    return meetings
                if year > max_season:
                    continue
                meetings.append(m)

            time.sleep(0.05)

        logger.info("Discovered %s meetings in seasons %s-%s", len(meetings), min_season, max_season)
        return meetings

    def _ingest_season_meetings(self, season: int, meetings: list[dict]) -> None:
        if not meetings:
            logger.warning("No meetings to ingest for season %s", season)
            return

        meetings_sorted = sorted(meetings, key=lambda m: m.get("date_start") or "")
        round_lookup = {m["meeting_key"]: idx + 1 for idx, m in enumerate(meetings_sorted)}
        meeting_meta: dict[int, dict[str, Any]] = {}

        meeting_records: list[dict] = []
        for meeting in meetings_sorted:
            meeting_key = meeting.get("meeting_key")
            grand_prix_slug = _slugify(meeting.get("meeting_name") or str(meeting_key))
            round_number = round_lookup.get(meeting_key, 0)
            meeting_row = {
                **meeting,
                "season": season,
                "round": round_number,
                "grand_prix_slug": grand_prix_slug,
                "session_code": None,
                "meeting_key": meeting_key,
                "session_key": None,
                "ingested_at": self.ingested_at,
            }
            meeting_records.append(meeting_row)
            meeting_meta[meeting_key] = {
                "season": season,
                "round": round_number,
                "grand_prix_slug": grand_prix_slug,
                "meeting_key": meeting_key,
            }

        self._write_partitioned(
            table="meetings",
            records=meeting_records,
            partition_keys=["season", "round", "grand_prix_slug"],
            include_session=False,
        )

        for meeting_key, meta in meeting_meta.items():
            self._ingest_meeting(meta)

    def _ingest_meeting(self, meta: dict) -> None:
        meeting_key = meta["meeting_key"]
        season = meta["season"]
        round_number = meta["round"]
        grand_prix_slug = meta["grand_prix_slug"]

        sessions_raw = self.client.fetch_all("sessions", {"meeting_key": meeting_key}, allow_pagination=False)
        sessions = _normalize_records(sessions_raw)
        if not sessions:
            logger.warning("No sessions for meeting_key=%s", meeting_key)
            return

        session_records: list[dict] = []
        for session in sessions:
            session_key = session.get("session_key")
            session_code = _derive_session_code(session.get("session_name"), session.get("session_type"))
            if session_code is None or session_code not in self.config.session_codes:
                logger.info(
                    "Skipping session_key=%s session_name=%s session_type=%s (code=%s not in allowed set)",
                    session_key,
                    session.get("session_name"),
                    session.get("session_type"),
                    session_code,
                )
                continue

            session_row = self._add_common_columns(
                record=session,
                season=season,
                round_number=round_number,
                grand_prix_slug=grand_prix_slug,
                session_code=session_code,
                meeting_key=meeting_key,
                session_key=session_key,
            )
            session_records.append(session_row)

            self._ingest_session_tables(
                season=season,
                round_number=round_number,
                grand_prix_slug=grand_prix_slug,
                meeting_key=meeting_key,
                session_key=session_key,
                session_code=session_code,
            )

        self._write_partitioned(
            table="sessions",
            records=session_records,
            partition_keys=["season", "round", "grand_prix_slug", "session_code"],
            include_session=True,
        )

    def _ingest_session_tables(
        self,
        season: int,
        round_number: int,
        grand_prix_slug: str,
        meeting_key: int,
        session_key: int,
        session_code: str,
    ) -> None:
        common_kwargs = dict(
            season=season,
            round_number=round_number,
            grand_prix_slug=grand_prix_slug,
            session_code=session_code,
            meeting_key=meeting_key,
            session_key=session_key,
        )

        # Drivers (session_key only)
        drivers_raw = self.client.fetch_all("drivers", {"session_key": session_key}, allow_pagination=False)
        drivers = _normalize_records(drivers_raw)
        driver_numbers = [d.get("driver_number") for d in drivers if d.get("driver_number") is not None]

        if drivers:
            driver_aug = []
            for rec in drivers:
                rec_norm = dict(rec)
                rec_norm["team_name"] = _normalize_team_name(rec_norm.get("team_name"))
                driver_aug.append(
                    self._add_common_columns(
                        record=rec_norm,
                        season=season,
                        round_number=round_number,
                        grand_prix_slug=grand_prix_slug,
                        session_code=session_code,
                        meeting_key=meeting_key,
                        session_key=session_key,
                    )
                )
            self._write_partitioned(
                table="drivers",
                records=driver_aug,
                partition_keys=["season", "round", "grand_prix_slug", "session_code"],
                include_session=True,
            )
        else:
            logger.info("No rows for drivers session_key=%s", session_key)

        # Laps: requires session_key + driver_number
        if driver_numbers:
            laps_all: list[dict] = []
            for dn in driver_numbers:
                try:
                    laps_raw = self.client.fetch_all(
                        "laps",
                        {"session_key": session_key, "driver_number": dn},
                        allow_pagination=False,
                    )
                except Exception as exc:
                    logger.warning("Failed laps fetch for session_key=%s driver_number=%s: %s", session_key, dn, exc)
                    continue
                if laps_raw:
                    laps_all.extend(laps_raw)
                time.sleep(self.config.driver_sleep_seconds)

            if laps_all:
                laps_norm = _normalize_records(laps_all)
                laps_aug = [
                    self._add_common_columns(
                        record=rec,
                        season=season,
                        round_number=round_number,
                        grand_prix_slug=grand_prix_slug,
                        session_code=session_code,
                        meeting_key=meeting_key,
                        session_key=session_key,
                    )
                    for rec in laps_norm
                ]
                self._write_partitioned(
                    table="laps",
                    records=laps_aug,
                    partition_keys=["season", "round", "grand_prix_slug", "session_code"],
                    include_session=True,
                    force_override=self.config.force_reingest_laps,
                )
                self.lap_rows_written += len(laps_aug)
                logger.info(
                    "[laps] season=%s round=%s session_code=%s meeting_key=%s session_key=%s drivers=%s laps_rows=%s",
                    season,
                    round_number,
                    session_code,
                    meeting_key,
                    session_key,
                    len(driver_numbers),
                    len(laps_aug),
                )
            else:
                logger.info(
                    "[laps] no laps for season=%s round=%s session_code=%s meeting_key=%s session_key=%s",
                    season,
                    round_number,
                    session_code,
                    meeting_key,
                    session_key,
                )
        else:
            logger.info("Skipping laps; no drivers for session_key=%s", session_key)

        # Tables that work with session_key only
        simple_tables = [
            ("stints", False),
            ("pit", False),
            ("session_result", False),
            ("starting_grid", False),
        ]
        for table_name, allow_pagination in simple_tables:
            self._ingest_simple_table(
                table_name=table_name,
                allow_pagination=allow_pagination,
                **common_kwargs,
            )

        # Weather, position, race_control can be sparse
        sparse_tables = [
            ("weather", False),
            ("position", False),
            ("race_control", False),
        ]
        for table_name, allow_pagination in sparse_tables:
            self._ingest_simple_table(
                table_name=table_name,
                allow_pagination=allow_pagination,
                quiet_if_empty=True,
                **common_kwargs,
            )

        # Optional heavy tables
        optional_tables = [
            ("car_data", self.config.enable_car_data, True),
            ("intervals", self.config.enable_intervals, True),
            ("overtakes", self.config.enable_overtakes, True),
        ]
        for table_name, enabled, allow_pagination in optional_tables:
            if not enabled:
                continue
            self._ingest_simple_table(
                table_name=table_name,
                allow_pagination=allow_pagination,
                **common_kwargs,
            )

    def _ingest_simple_table(
        self,
        table_name: str,
        season: int,
        round_number: int,
        grand_prix_slug: str,
        session_code: str,
        meeting_key: int,
        session_key: int,
        allow_pagination: bool,
        quiet_if_empty: bool = False,
    ) -> None:
        try:
            records_raw = self.client.fetch_all(
                table_name, {"session_key": session_key}, allow_pagination=allow_pagination
            )
        except Exception as exc:
            logger.warning("Failed fetch for %s session_key=%s: %s", table_name, session_key, exc)
            return

        records = _normalize_records(records_raw)
        if not records:
            if not quiet_if_empty:
                logger.info("No rows for %s session_key=%s", table_name, session_key)
            return

        augmented = [
            self._add_common_columns(
                record=rec,
                season=season,
                round_number=round_number,
                grand_prix_slug=grand_prix_slug,
                session_code=session_code,
                meeting_key=meeting_key,
                session_key=session_key,
            )
            for rec in records
        ]

        self._write_partitioned(
            table=table_name,
            records=augmented,
            partition_keys=["season", "round", "grand_prix_slug", "session_code"],
            include_session=True,
        )

    def _add_common_columns(
        self,
        record: dict,
        season: int,
        round_number: int,
        grand_prix_slug: str,
        session_code: Optional[str],
        meeting_key: Optional[int],
        session_key: Optional[int],
    ) -> dict:
        return {
            **record,
            "season": season,
            "round": round_number,
            "grand_prix_slug": grand_prix_slug,
            "session_code": session_code,
            "meeting_key": meeting_key,
            "session_key": session_key,
            "ingested_at": self.ingested_at,
        }

    def _write_partitioned(
        self,
        table: str,
        records: list[dict],
        partition_keys: list[str],
        include_session: bool,
        force_override: Optional[bool] = None,
    ) -> None:
        if not records:
            return
        df = pd.DataFrame(records)
        df = _sanitize_df_for_parquet(df)

        partition_values = {key: records[0].get(key) for key in partition_keys}
        partition_dir = self._build_partition_path(
            table=table,
            season=partition_values.get("season"),
            round_number=partition_values.get("round"),
            grand_prix_slug=partition_values.get("grand_prix_slug"),
            session_code=partition_values.get("session_code") if include_session else None,
        )

        existing = list(partition_dir.glob("*.parquet"))
        force = self.config.force_reingest if force_override is None else force_override
        if existing and not force:
            logger.info("Skipping %s partition %s (files already exist)", table, partition_dir)
            return

        partition_dir.mkdir(parents=True, exist_ok=True)
        if existing and force:
            for f in existing:
                f.unlink()

        target_file = partition_dir / "part-00000.parquet"
        df.to_parquet(target_file, index=False)
        logger.info("Wrote %s rows to %s", len(df), target_file)

    def _build_partition_path(
        self,
        table: str,
        season: Optional[int],
        round_number: Optional[int],
        grand_prix_slug: Optional[str],
        session_code: Optional[str],
    ) -> Path:
        parts = [
            self.bronze_root,
            table,
            f"season={season}" if season is not None else "season=unknown",
            f"round={round_number:02d}" if round_number is not None else "round=00",
            f"grand_prix={grand_prix_slug}" if grand_prix_slug else "grand_prix=unknown",
        ]
        if session_code is not None:
            parts.append(f"session={session_code}")
        return Path(*parts)


def load_config() -> IngestConfig:
    base_url = os.getenv("OPENF1_BASE_URL", "https://api.openf1.org").rstrip("/")
    seasons_default = ",".join(str(year) for year in range(2018, 2025))
    seasons = _parse_int_list(os.getenv("OPENF1_SEASONS", seasons_default))
    session_codes = set(_parse_str_list(os.getenv("OPENF1_SESSION_CODES", "FP1,FP2,FP3,SQ,S,Q,R")))
    data_root = Path(
        os.getenv(
            "DATA_ROOT",
            "/opt/data" if Path("/opt/data").exists() else os.getenv("EXTERNAL_DATA_ROOT", "/opt/data"),
        )
    )
    force_reingest = os.getenv("FORCE_REINGEST", "0") == "1"
    enable_car_data = os.getenv("OPENF1_ENABLE_CAR_DATA", "0") == "1"
    enable_intervals = os.getenv("OPENF1_ENABLE_INTERVALS", "0") == "1"
    enable_overtakes = os.getenv("OPENF1_ENABLE_OVERTAKES", "0") == "1"
    force_reingest_laps = os.getenv("OPENF1_FORCE_REINGEST_LAPS", "0") == "1"
    driver_sleep_seconds = float(os.getenv("OPENF1_DRIVER_SLEEP_SECONDS", "0.1"))
    max_meeting_key = int(os.getenv("OPENF1_MAX_MEETING_KEY", "1400"))

    return IngestConfig(
        base_url=base_url,
        seasons=seasons,
        session_codes=session_codes,
        data_root=data_root,
        force_reingest=force_reingest,
        enable_car_data=enable_car_data,
        enable_intervals=enable_intervals,
        enable_overtakes=enable_overtakes,
        force_reingest_laps=force_reingest_laps,
        driver_sleep_seconds=driver_sleep_seconds,
        max_meeting_key=max_meeting_key,
    )


def main() -> None:
    config = load_config()
    logger.info("Seasons to ingest: %s", config.seasons)
    logger.info("Config: %s", config)
    ingestor = OpenF1Ingestor(config)
    ingestor.run()


if __name__ == "__main__":
    main()
