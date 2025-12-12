from fastapi import FastAPI

from .routers import (
    analytics_pace,
    analytics_racecraft_stub,
    analytics_strategy_stub,
    analytics_track_stub,
    catalog,
    compare_stub,
    frontend_stub,
    meta,
    pace,
    predict,
    predict_stub,
    results,
    standings,
)
from .db import get_warehouse_path

app = FastAPI(
    title="F1 OpenF1 Backend",
    version="0.1.0",
    description="Read-only analytics API over DuckDB for F1 data (OpenF1).",
)

# Optional startup log for warehouse path
try:
    path = get_warehouse_path()
    print(f"[info] backend using warehouse {path}, serving on port 8001")
except Exception:
    # Avoid crashing app init; health endpoint will surface the issue.
    print("[warn] backend could not resolve warehouse path at startup.")

@app.get("/")
def root():
    return {"service": "f1-backend", "ok": True}


app.include_router(catalog.router, prefix="/catalog", tags=["catalog"])
app.include_router(standings.router)
app.include_router(results.router, prefix="/results", tags=["results"])
app.include_router(pace.router, prefix="/pace", tags=["pace"])
app.include_router(analytics_pace.router, prefix="/analytics/pace", tags=["analytics:pace"])
app.include_router(analytics_strategy_stub.router, prefix="/analytics/strategy", tags=["analytics:strategy"])
app.include_router(analytics_racecraft_stub.router, prefix="/analytics/racecraft", tags=["analytics:racecraft"])
app.include_router(analytics_track_stub.router, prefix="/analytics/track", tags=["analytics:track"])
app.include_router(compare_stub.router, prefix="/compare", tags=["compare"])
app.include_router(predict_stub.router, prefix="/predict", tags=["predict"])
app.include_router(predict.router, prefix="/api", tags=["predictions"])
app.include_router(meta.router, prefix="/meta", tags=["meta"])
# Stub endpoints to satisfy frontend calls while data pipes are offline
app.include_router(frontend_stub.router)
