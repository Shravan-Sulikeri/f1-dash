from fastapi import APIRouter

router = APIRouter()


@router.post("/race")
def predict_race_stub():
    # TODO: Implement race win probability using ML models once available.
    return {"status": "not_implemented", "detail": "Race prediction coming soon."}


@router.post("/quali")
def predict_quali_stub():
    # TODO: Implement quali pole probability using ML models once available.
    return {"status": "not_implemented", "detail": "Qualifying prediction coming soon."}


@router.get("/championship")
def predict_championship_stub():
    # TODO: Implement championship projections.
    return {"status": "not_implemented", "detail": "Championship prediction coming soon."}
