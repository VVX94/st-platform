"""Worker that polls the database for queued runs and executes them."""

from __future__ import annotations

import json
import logging
from typing import Optional

from sqlalchemy.orm import Session

from st_platform.core.registry import AlgorithmRegistry
from st_platform.core.runner import LocalRunner
from st_platform.storage.models import RunModel
from st_platform.storage.repositories import RunRepo
from st_platform.tasks import TaskType

logger = logging.getLogger(__name__)


def _run_to_bundle_params(run: RunModel) -> dict:
    """Extract parameters dict from a RunModel."""
    try:
        return json.loads(run.parameters_json)
    except (json.JSONDecodeError, TypeError):
        return {}


def poll_runs(
    db: Session,
    runner: LocalRunner,
    registry: AlgorithmRegistry,
    build_demo_bundle: Optional[callable] = None,
    limit: int = 10,
) -> int:
    """Poll queued runs, execute them, and write results back.

    Returns the number of runs processed.
    """
    repo = RunRepo(db)
    queued = repo.list_queued()[:limit]

    if not queued:
        return 0

    processed = 0
    for run in queued:
        algo_id = run.algorithm_id
        task_type_str = run.task_type

        # Resolve TaskType enum
        try:
            task_type = TaskType(task_type_str)
        except ValueError:
            repo.mark_failed(run.run_id, f"Unknown task type: {task_type_str}")
            processed += 1
            continue

        # Check algorithm exists
        try:
            registry.get(algo_id)
        except KeyError:
            repo.mark_failed(run.run_id, f"Unknown algorithm: {algo_id}")
            processed += 1
            continue

        # Mark running
        repo.mark_running(run.run_id)

        # Build data bundle - use demo if no real data source
        if build_demo_bundle is not None:
            data = build_demo_bundle()
        else:
            from st_platform.data import DataAsset, DatasetRef, SpatialDataBundle

            dataset_info = json.loads(run.dataset_json) if run.dataset_json else {}
            data = SpatialDataBundle(
                dataset=DatasetRef(
                    dataset_id=dataset_info.get("dataset_id", "unknown"),
                    platform=dataset_info.get("platform", "visium"),
                    sample_id=dataset_info.get("sample_id", "unknown"),
                ),
                assets=[
                    DataAsset(kind="counts_table", key="counts", description="demo counts"),
                    DataAsset(kind="spatial_coordinates", key="coordinates", description="demo coords"),
                ],
            )

        params = _run_to_bundle_params(run)

        # Execute
        try:
            result = runner.execute(
                task_type=task_type,
                algorithm_id=algo_id,
                data=data,
                parameters=params,
            )
        except Exception as exc:
            repo.mark_failed(run.run_id, str(exc))
            logger.exception("Run %s failed with exception", run.run_id)
            processed += 1
            continue

        # Write results back
        if result.status.value == "succeeded":
            repo.mark_succeeded(
                run.run_id,
                summary=result.summary,
                metrics=result.metrics,
                artifacts=result.artifacts,
            )
        else:
            repo.mark_failed(run.run_id, result.error or "Unknown error")

        processed += 1
        logger.info("Processed run %s -> %s", run.run_id, result.status.value)

    return processed
