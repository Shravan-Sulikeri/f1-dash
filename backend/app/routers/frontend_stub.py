from typing import Any, Dict, List

from fastapi import APIRouter, Query

router = APIRouter(tags=["frontend-stub"])


# --- Helper payloads ---
_empty_results: List[Dict[str, Any]] = []
_empty_sessions: Dict[str, List[Any]] = {"sessions": []}
_empty_weather: Dict[str, Any] = {}
_empty_predictions: Dict[str, Any] = {"field": [], "top3": [], "winner": None}
_empty_monitor: Dict[str, Any] = {}
_empty_summary: Dict[str, Any] = {"hit_at_1": 0.0, "hit_at_3": 0.0, "n_races": 0, "season": None}
_empty_pace: Dict[str, Any] = {}


@router.get("/races/{season}/{round}/results")
def race_results(season: int, round: int, session_type: str = Query("R")) -> List[Dict[str, Any]]:
    return _empty_results


@router.get("/races/{season}/{round}/sessions")
def race_sessions(season: int, round: int) -> Dict[str, List[Any]]:
    return _empty_sessions


@router.get("/races/{season}/{round}/weather")
def race_weather(season: int, round: int, session_type: str = Query("R")) -> Dict[str, Any]:
    return _empty_weather


@router.get("/races/{season}/{round}/predictions")
def race_predictions(season: int, round: int) -> Dict[str, Any]:
    return _empty_predictions


@router.get("/season/{season}/driver_pace")
def driver_pace(season: int) -> Dict[str, Any]:
    return _empty_pace


@router.get("/predictions/race_win/summary")
def predictions_summary(season: int) -> Dict[str, Any]:
    data = dict(_empty_summary)
    data["season"] = season
    return data


@router.get("/monitor")
def monitor(season: int) -> Dict[str, Any]:
    return _empty_monitor


@router.get("/standings/drivers")
def standings_drivers(season: int, round: int | None = Query(None)) -> List[Dict[str, Any]]:
    return []


@router.get("/standings/constructors")
def standings_constructors(season: int, round: int | None = Query(None)) -> List[Dict[str, Any]]:
    return []


@router.get("/standings/teams")
def standings_teams(season: int, round: int | None = Query(None)) -> List[Dict[str, Any]]:
    return []
