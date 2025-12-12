from fastapi import APIRouter

router = APIRouter()


@router.get("/drivers")
def compare_drivers_stub():
    # TODO: Implement driver comparisons using gold.driver_session_summary.
    return {"status": "not_implemented", "detail": "Driver comparison coming soon."}


@router.get("/teams")
def compare_teams_stub():
    # TODO: Implement team comparisons using gold.team_session_summary.
    return {"status": "not_implemented", "detail": "Team comparison coming soon."}
