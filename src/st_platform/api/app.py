"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from st_platform.api.routes import api_router
from st_platform.storage.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="ST Platform API",
        version="0.1.0",
        description="Spatial Transcriptomics Algorithm Benchmark Platform",
        lifespan=lifespan,
    )
    app.include_router(api_router)
    return app
