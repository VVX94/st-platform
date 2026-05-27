"""Artifact file serving routes."""

import mimetypes
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

router = APIRouter()

_MEDIA_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".csv": "text/csv",
    ".json": "application/json",
    ".md": "text/markdown",
    ".txt": "text/plain",
    ".html": "text/html",
}


@router.get("/api/artifacts/file")
def serve_artifact_file(path: str = Query(..., description="Relative path within the artifact root")):
    """Serve an artifact file by its relative path.

    The ``path`` parameter is the relative path stored in the artifact's
    ``uri`` field (e.g. ``runs/<run_id>/report.csv``).  The server resolves
    it against the project root and returns the file with the appropriate
    content type.

    Absolute paths and path-traversal attempts are rejected.
    """
    # Reject absolute paths
    if Path(path).is_absolute():
        raise HTTPException(status_code=400, detail="Absolute paths are not allowed.")

    # Resolve against project root (two levels up from this file)
    project_root = Path(__file__).resolve().parents[4]
    full_path = (project_root / path).resolve()

    # Ensure the resolved path is still under project root
    if not str(full_path).startswith(str(project_root)):
        raise HTTPException(status_code=403, detail="Access denied.")

    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="Artifact file not found.")

    media_type = _MEDIA_MAP.get(full_path.suffix.lower())
    if media_type is None:
        media_type = mimetypes.guess_type(str(full_path))[0] or "application/octet-stream"

    return FileResponse(
        path=str(full_path),
        media_type=media_type,
        filename=full_path.name,
    )
