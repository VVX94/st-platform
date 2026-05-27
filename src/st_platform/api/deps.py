"""Dependency injection helpers for FastAPI routes."""

from __future__ import annotations

from pathlib import Path
from typing import Generator

from sqlalchemy.orm import Session

from st_platform.storage.database import SessionLocal
from st_platform.workflows.service import PlatformService, create_platform_service

# Lazy singleton for the platform service
_service: PlatformService | None = None


def get_db_session() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session; auto-closes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_platform_service() -> PlatformService:
    """Return (and cache) the PlatformService singleton."""
    global _service
    if _service is None:
        _service = create_platform_service(project_root=str(Path.cwd()))
    return _service
