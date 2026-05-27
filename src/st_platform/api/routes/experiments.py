from __future__ import annotations

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from st_platform.api.deps import get_db_session
from st_platform.api.schemas import (
    ArtifactOut,
    ExperimentCreate,
    ExperimentOut,
    ExperimentReportOut,
    RunOut,
)
from st_platform.storage.repositories import ArtifactRepo, DatasetRepo, ExperimentRepo, MetricRepo, RunRepo

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

    # Look up dataset info if dataset_id provided
    dataset_info = {}
    if payload.dataset_id:
        ds_repo = DatasetRepo(db)
        ds = ds_repo.get(payload.dataset_id)
        if ds is not None:
            try:
                meta = json.loads(ds.metadata_json)
            except (json.JSONDecodeError, TypeError):
                meta = {}
            dataset_info = {
                "dataset_id": ds.dataset_id,
                "name": ds.name,
                "platform": ds.platform,
                "sample_id": ds.sample_id,
                "uri": ds.uri,
                "metadata": meta,
            }

    # Create queued runs for each algorithm
    run_repo = RunRepo(db)
    for algo_id in payload.algorithm_ids:
        run_repo.create(
            algorithm_id=algo_id,
            task_type=payload.task_type,
            experiment_id=exp.experiment_id,
            parameters=payload.parameters,
            dataset=dataset_info,
        )

    # Update experiment status to "running"
    repo.update_status(exp.experiment_id, "running")

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


@router.get("/api/experiments/{experiment_id}/runs", response_model=List[RunOut])
async def get_experiment_runs(
    experiment_id: str,
    db: Session = Depends(get_db_session),
) -> List[RunOut]:
    """Return all runs belonging to an experiment."""
    repo = ExperimentRepo(db)
    exp = repo.get(experiment_id)
    if exp is None:
        raise HTTPException(status_code=404, detail=f"Experiment '{experiment_id}' not found")
    run_repo = RunRepo(db)
    runs = run_repo.list_all()
    exp_runs = [r for r in runs if r.experiment_id == experiment_id]

    from st_platform.api.routes.runs import _model_to_out as run_model_to_out

    return [run_model_to_out(r) for r in exp_runs]


@router.get("/api/experiments/{experiment_id}/report", response_model=ExperimentReportOut)
async def get_experiment_report(
    experiment_id: str,
    db: Session = Depends(get_db_session),
) -> ExperimentReportOut:
    """Return a summary report for an experiment: info, runs, metrics, artifacts."""
    repo = ExperimentRepo(db)
    exp = repo.get(experiment_id)
    if exp is None:
        raise HTTPException(status_code=404, detail=f"Experiment '{experiment_id}' not found")

    # Gather runs
    run_repo = RunRepo(db)
    all_runs = run_repo.list_all()
    exp_runs = [r for r in all_runs if r.experiment_id == experiment_id]

    from st_platform.api.routes.runs import _model_to_out as run_model_to_out

    runs_out = [run_model_to_out(r) for r in exp_runs]

    # Aggregate metrics summary: for each metric name, collect values across runs
    metrics_summary: dict = {}
    for run in runs_out:
        for name, value in run.metrics.items():
            if name not in metrics_summary:
                metrics_summary[name] = []
            metrics_summary[name].append(value)

    # Compute avg/min/max per metric
    summary_stats: dict = {}
    for name, values in metrics_summary.items():
        summary_stats[name] = {
            "avg": sum(values) / len(values) if values else 0,
            "min": min(values) if values else 0,
            "max": max(values) if values else 0,
            "count": len(values),
        }

    # Collect all artifacts
    artifact_repo = ArtifactRepo(db)
    all_artifacts: list = []
    for r in exp_runs:
        for a in artifact_repo.list_for_run(r.run_id):
            try:
                meta = json.loads(a.metadata_json)
            except (json.JSONDecodeError, TypeError):
                meta = {}
            all_artifacts.append(
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

    # Build algorithm comparison summary for multi-algorithm experiments
    comparison_summary: dict = {}
    succeeded_runs = [r for r in runs_out if r.status == "succeeded" and r.metrics]
    algo_ids = sorted(set(r.algorithm_id for r in succeeded_runs))
    if len(algo_ids) > 1:
        for algo_id in algo_ids:
            algo_runs = [r for r in succeeded_runs if r.algorithm_id == algo_id]
            algo_metrics: dict = {}
            all_metric_names = sorted(set(name for r in algo_runs for name in r.metrics))
            for metric_name in all_metric_names:
                values = [r.metrics[metric_name] for r in algo_runs if metric_name in r.metrics]
                if values:
                    algo_metrics[metric_name] = sum(values) / len(values)
            comparison_summary[algo_id] = algo_metrics

    return ExperimentReportOut(
        experiment_id=exp.experiment_id,
        name=exp.name,
        status=exp.status,
        task_type=exp.task_type,
        runs=runs_out,
        metrics_summary=summary_stats,
        comparison_summary=comparison_summary,
        artifacts=all_artifacts,
    )
