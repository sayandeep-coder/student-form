"""FastAPI application entrypoint."""

import logging
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1.students import router as students_router
from app.core.config import get_settings
from app.db.session import get_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

is_production = settings.app_env.lower() == "production"

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 routes
app.include_router(students_router, prefix=settings.api_v1_prefix)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions safely without leaking internals, SQL, or traces."""
    logger.error("Unhandled exception processing %s %s: %s", request.method, request.url.path, type(exc).__name__)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred."},
    )


@app.get("/health", tags=["Health"], summary="Service health check")
def health_check() -> Dict[str, Any]:
    """Perform health verification without exposing sensitive internals or credentials."""
    db_status = "unconfigured"

    if settings.is_placeholder_database_url():
        db_status = "placeholder_configured"
    else:
        try:
            engine = get_engine()
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            db_status = "connected"
        except Exception:
            # Mask internal error, do not leak credentials
            db_status = "unreachable"

    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "environment": settings.app_env,
        "database": db_status,
    }
