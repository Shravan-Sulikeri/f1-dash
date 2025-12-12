try:
    # When imported as a package (uvicorn api.main:app)
    from .app import app
except ImportError:
    # When running from within the api directory (uvicorn main:app)
    from app import app  # type: ignore
