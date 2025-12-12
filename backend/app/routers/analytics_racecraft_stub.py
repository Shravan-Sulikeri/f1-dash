from fastapi import APIRouter

router = APIRouter()


@router.get("/session")
def racecraft_session_stub():
    # TODO: Implement racecraft analytics (overtakes/defense) using position/intervals when available.
    return {"status": "not_implemented", "detail": "Racecraft analytics coming soon."}
