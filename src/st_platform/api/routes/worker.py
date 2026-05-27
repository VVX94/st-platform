"""Worker poll endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from st_platform.api.deps import get_db_session, get_platform_service
from st_platform.api.schemas import WorkerPollResponse
from st_platform.worker.runner import poll_runs

router = APIRouter()


@router.post("/api/worker/poll", response_model=WorkerPollResponse)
async def trigger_worker_poll(db: Session = Depends(get_db_session)) -> WorkerPollResponse:
    """Trigger a worker poll cycle and return the number of processed runs."""
    svc = get_platform_service()
    count = poll_runs(
        db=db,
        runner=svc.runner,
        registry=svc.algorithm_registry,
        build_demo_bundle=svc.build_demo_dataset,
    )
    return WorkerPollResponse(processed=count)
