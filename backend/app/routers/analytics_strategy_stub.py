from fastapi import APIRouter

router = APIRouter()


@router.get("/session")
def strategy_session_stub():
    # TODO: Implement strategy analytics using gold.driver_session_summary and pit/stints from silver.
    return {"status": "not_implemented", "detail": "Strategy analytics coming soon."}
