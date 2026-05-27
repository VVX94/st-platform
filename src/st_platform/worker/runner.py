"""Worker that polls the database for queued runs and executes them."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from st_platform.core.registry import AlgorithmRegistry
from st_platform.core.runner import LocalRunner
from st_platform.storage.models import ArtifactModel, RunModel
from st_platform.storage.repositories import RunRepo
from st_platform.tasks import TaskType

logger = logging.getLogger(__name__)


def _run_to_bundle_params(run: RunModel) -> dict:
    """Extract parameters dict from a RunModel."""
    try:
        return json.loads(run.parameters_json)
    except (json.JSONDecodeError, TypeError):
        return {}


def _generate_run_reports(run_id: str, result, db: Session) -> None:
    """Generate CSV/PNG report artifacts after a successful run.

    Failures here are logged as warnings and do NOT fail the run.
    """
    from st_platform.benchmark.reports import (
        generate_domain_grid_plot,
        generate_domain_predictions_csv,
        generate_metrics_bar_plot,
        generate_run_metrics_csv,
    )

    run_root = Path(result.run_root) if result.run_root else None
    if run_root is None:
        logger.warning("No run_root for run %s; skipping report generation", run_id)
        return

    metrics = result.metrics or {}
    artifacts = result.artifacts or []

    # -- Metrics CSV --
    try:
        csv_path = str(run_root / f"{run_id}_metrics.csv")
        generate_run_metrics_csv(
            {"run_id": run_id, "algorithm_id": result.algorithm_id, "metrics": metrics},
            csv_path,
        )
        art = ArtifactModel(
            run_id=run_id,
            kind="metrics_csv",
            uri=csv_path,
            description="Run metrics as CSV.",
        )
        db.add(art)
    except Exception:
        logger.warning("Failed to generate metrics CSV for run %s", run_id, exc_info=True)

    # -- Metrics bar plot --
    try:
        bar_path = str(run_root / f"{run_id}_metrics_bar.png")
        generate_metrics_bar_plot(metrics, bar_path)
        art = ArtifactModel(
            run_id=run_id,
            kind="metrics_bar_plot",
            uri=bar_path,
            description="Bar chart of run metrics.",
        )
        db.add(art)
    except Exception:
        logger.warning("Failed to generate metrics bar plot for run %s", run_id, exc_info=True)

    # -- Domain predictions from domain_assignments artifacts --
    for orig_art in artifacts:
        if orig_art.get("kind") != "domain_assignments":
            continue
        uri = orig_art.get("uri", "")
        if not uri or not Path(uri).exists():
            continue

        try:
            domain_data = json.loads(Path(uri).read_text(encoding="utf-8"))
        except Exception:
            logger.warning("Failed to read domain assignments from %s", uri, exc_info=True)
            continue

        # Domain CSV
        try:
            dom_csv_path = str(run_root / f"{run_id}_domain_predictions.csv")
            generate_domain_predictions_csv(domain_data, dom_csv_path)
            art = ArtifactModel(
                run_id=run_id,
                kind="domain_predictions_csv",
                uri=dom_csv_path,
                description="Domain predictions as CSV.",
            )
            db.add(art)
        except Exception:
            logger.warning("Failed to generate domain CSV for run %s", run_id, exc_info=True)

        # Domain grid plot
        try:
            grid_path = str(run_root / f"{run_id}_domain_grid.png")
            generate_domain_grid_plot(domain_data, grid_path)
            art = ArtifactModel(
                run_id=run_id,
                kind="domain_grid_plot",
                uri=grid_path,
                description="Scatter plot of spatial domain predictions.",
            )
            db.add(art)
        except Exception:
            logger.warning("Failed to generate domain grid plot for run %s", run_id, exc_info=True)

    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.warning("Failed to commit report artifacts for run %s", run_id, exc_info=True)


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

        # Determine dataset info from the run's dataset_json
        dataset_info = {}
        try:
            dataset_info = json.loads(run.dataset_json) if run.dataset_json else {}
        except (json.JSONDecodeError, TypeError):
            dataset_info = {}

        is_demo = dataset_info.get("metadata", {}).get("demo", False)

        # Build data bundle - use demo if dataset is flagged as demo or no real URI
        if is_demo and build_demo_bundle is not None:
            data = build_demo_bundle()
        elif build_demo_bundle is not None and not dataset_info.get("uri"):
            # No real URI and demo builder available: use demo
            data = build_demo_bundle()
        elif dataset_info.get("uri") and not is_demo:
            # Real dataset URI - for now fail gracefully with a clear message
            uri = dataset_info.get("uri", "")
            repo.mark_failed(
                run.run_id,
                f"Real dataset loading not yet implemented. Dataset URI: {uri}",
            )
            processed += 1
            continue
        else:
            # Fallback: build a minimal bundle from dataset_info
            from st_platform.data import DataAsset, DatasetRef, SpatialDataBundle

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
            # Generate report artifacts (non-fatal)
            try:
                _generate_run_reports(run.run_id, result, db)
            except Exception:
                logger.warning("Report generation failed for run %s", run.run_id, exc_info=True)
        else:
            repo.mark_failed(run.run_id, result.error or "Unknown error")

        processed += 1
        logger.info("Processed run %s -> %s", run.run_id, result.status.value)

    return processed
