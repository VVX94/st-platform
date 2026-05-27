from __future__ import annotations

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from st_platform.api.deps import get_db_session
from st_platform.api.schemas import ExperimentCreate, ExperimentOut
from st_platform.storage.repositories import ExperimentRepo, RunRepo

router = APIRouter()


def _model_to_out(exp, run_count: int = 0) -> ExperimentOut:  # type: ignore[no-untyped-def]
    try:
        params = json.loads(exp.parameters_json)
    except (json.JSONDecodeError, TypeError):
        params = {}
    return ExperimentOut(
        experiment_id=exp.experiment_id,
        name=exp.name,
        task_type=exp.task_type,
        dataset_id=exp.dataset_id,
        parameters=params,
        status=exp.status,
        run_count=run_count,
        created_at=exp.created_at,
    )


@router.post("/api/experiments", response_model=ExperimentOut, status_code=201)
async def create_experiment(
    payload: ExperimentCreate,
    db: Session = Depends(get_db_session),
) -> ExperimentOut:
    repo = ExperimentRepo(db)
    exp = repo.create(
        name=payload.name,
        task_type=payload.task_type,
        dataset_id=payload.dataset_id,
        parameters={
            **payload.parameters,
            "algorithm_ids": payload.algorithm_ids,
        },
    )
    # Create queued runs for each algorithm
    run_repo = RunRepo(db)
    for algo_id in payload.algorithm_ids:
        run_repo.create(
            algorithm_id=algo_id,
            task_type=payload.task_type,
            experiment_id=exp.experiment_id,
            parameters=payload.parameters,
        )
    return _model_to_out(exp, run_count=len(payload.algorithm_ids))


@router.get("/api/experiments", response_model=List[ExperimentOut])
async def list_experiments(db: Session = Depends(get_db_session)) -> List[ExperimentOut]:
    repo = ExperimentRepo(db)
    exps = repo.list_all()
    return [_model_to_out(exp) for exp in exps]


@router.get("/api/experiments/{experiment_id}", response_model=ExperimentOut)
async def get_experiment(
    experiment_id: str,
    db: Session = Depends(get_db_session),
) -> ExperimentOut:
    repo = ExperimentRepo(db)
    exp = repo.get(experiment_id)
    if exp is None:
        raise HTTPException(status_code=404, detail=f"Experiment '{experiment_id}' not found")
    run_count = len(exp.runs) if exp.runs else 0
    return _model_to_out(exp, run_count=run_count)
