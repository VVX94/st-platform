from __future__ import annotations

import json
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from st_platform.api.deps import get_db_session
from st_platform.api.schemas import ArtifactOut, MetricOut, RunOut
from st_platform.storage.repositories import ArtifactRepo, MetricRepo, RunRepo

router = APIRouter()


def _model_to_out(run) -> RunOut:  # type: ignore[no-untyped-def]
    try:
        params = json.loads(run.parameters_json)
    except (json.JSONDecodeError, TypeError):
        params = {}
    try:
        dataset = json.loads(run.dataset_json)
    except (json.JSONDecodeError, TypeError):
        dataset = {}
    try:
        summary = json.loads(run.summary_json)
    except (json.JSONDecodeError, TypeError):
        summary = {}

    metrics: Dict[str, float] = {}
    for m in run.metrics:
        metrics[m.name] = m.value

    artifacts: List[Dict[str, Any]] = []
    for a in run.artifacts:
        try:
            meta = json.loads(a.metadata_json)
        except (json.JSONDecodeError, TypeError):
            meta = {}
        artifacts.append(
            {
                "artifact_id": a.artifact_id,
                "kind": a.kind,
                "uri": a.uri,
                "description": a.description,
                "metadata": meta,
            }
        )

    return RunOut(
        run_id=run.run_id,
        experiment_id=run.experiment_id,
        algorithm_id=run.algorithm_id,
        task_type=run.task_type,
        status=run.status,
        parameters=params,
        dataset=dataset,
        summary=summary,
        metrics=metrics,
        artifacts=artifacts,
        error=run.error,
        run_root=run.run_root,
        created_at=run.created_at,
        started_at=run.started_at,
        finished_at=run.finished_at,
    )


@router.get("/api/runs", response_model=List[RunOut])
async def list_runs(db: Session = Depends(get_db_session)) -> List[RunOut]:
    repo = RunRepo(db)
    return [_model_to_out(r) for r in repo.list_all()]


@router.get("/api/runs/{run_id}", response_model=RunOut)
async def get_run(
    run_id: str,
    db: Session = Depends(get_db_session),
) -> RunOut:
    repo = RunRepo(db)
    run = repo.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return _model_to_out(run)


@router.get("/api/runs/{run_id}/metrics", response_model=List[MetricOut])
async def get_run_metrics(
    run_id: str,
    db: Session = Depends(get_db_session),
) -> List[MetricOut]:
    """Return all metrics for a specific run."""
    run_repo = RunRepo(db)
    run = run_repo.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    metric_repo = MetricRepo(db)
    return [
        MetricOut(
            metric_id=m.metric_id,
            run_id=m.run_id,
            name=m.name,
            value=m.value,
            created_at=m.created_at,
        )
        for m in metric_repo.list_for_run(run_id)
    ]


@router.get("/api/runs/{run_id}/artifacts", response_model=List[ArtifactOut])
async def get_run_artifacts(
    run_id: str,
    db: Session = Depends(get_db_session),
) -> List[ArtifactOut]:
    """Return all artifacts for a specific run."""
    run_repo = RunRepo(db)
    run = run_repo.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    artifact_repo = ArtifactRepo(db)
    result: List[ArtifactOut] = []
    for a in artifact_repo.list_for_run(run_id):
        try:
            meta = json.loads(a.metadata_json)
        except (json.JSONDecodeError, TypeError):
            meta = {}
        result.append(
            ArtifactOut(
                artifact_id=a.artifact_id,
                run_id=a.run_id,
                kind=a.kind,
                uri=a.uri,
                description=a.description,
                metadata=meta,
                created_at=a.created_at,
            )
        )
    return result
