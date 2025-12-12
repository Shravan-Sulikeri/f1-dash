from fastapi import APIRouter

router = APIRouter()


@router.get("/profile")
def track_profile_stub():
    # TODO: Implement track profiles using location/telemetry data when available.
    return {"status": "not_implemented", "detail": "Track analytics coming soon."}
