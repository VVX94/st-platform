"""Worker that polls the database for queued runs and executes them."""

from __future__ import annotations

import json
import logging
import tracemalloc
from pathlib import Path
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from st_platform.core.registry import AlgorithmRegistry
from st_platform.core.runner import LocalRunner
from st_platform.data import DataAsset, DatasetRef, SpatialDataBundle
from st_platform.storage.models import ArtifactModel, RunModel
from st_platform.storage.repositories import ExperimentRepo, RunRepo
from st_platform.tasks import TaskType

logger = logging.getLogger(__name__)


def _run_to_bundle_params(run: RunModel) -> dict:
    """Extract parameters dict from a RunModel."""
    try:
        return json.loads(run.parameters_json)
    except (json.JSONDecodeError, TypeError):
        return {}


def _relative_uri(absolute_path: str) -> str:
    """Convert an absolute path under the project root to a relative path."""
    abs_p = Path(absolute_path).resolve()
    # runner.py is at src/st_platform/worker/runner.py (depth 5),
    # so parents[3] = st-platform/ (the project root).
    # This matches artifacts.py's parents[4] because artifacts.py
    # is one level deeper at src/st_platform/api/routes/artifacts.py.
    project_root = Path(__file__).resolve().parents[3]
    try:
        return str(abs_p.relative_to(project_root))
    except ValueError:
        # Path is outside project root; return as-is (shouldn't happen)
        return absolute_path


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
            uri=_relative_uri(csv_path),
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
            uri=_relative_uri(bar_path),
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
                uri=_relative_uri(dom_csv_path),
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
                uri=_relative_uri(grid_path),
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


def _compute_clustering_metrics(
    metrics: Dict[str, float],
    result: Any,
    ground_truth_labels: list,
    features: Any = None,
) -> Dict[str, float]:
    """Compute all applicable metrics from domain assignments.

    Extracts predicted domain labels and coordinates from the run's
    domain_assignments artifact and computes label-dependent, spatial,
    and feature-based metrics.
    """
    import numpy as np

    from st_platform.benchmark.metrics import compute_all_metrics

    artifacts = result.artifacts or []
    domain_artifact = None
    for art in artifacts:
        if art.get("kind") == "domain_assignments":
            domain_artifact = art
            break

    if domain_artifact is None:
        logger.warning("No domain_assignments artifact found; skipping metrics.")
        return metrics

    try:
        uri = domain_artifact.get("uri", "")
        domain_data = json.loads(Path(uri).read_text(encoding="utf-8"))
        domains = domain_data.get("domains", [])
        if not domains:
            logger.warning("Empty domains list in artifact; skipping metrics.")
            return metrics

        pred_labels = np.array([d["domain"] for d in domains])
        true_labels = np.array(ground_truth_labels)
        coordinates = np.array([[d.get("x", 0), d.get("y", 0)] for d in domains], dtype=float)

        if len(pred_labels) != len(true_labels):
            logger.warning(
                "Label count mismatch: predicted=%d, truth=%d; skipping metrics.",
                len(pred_labels),
                len(true_labels),
            )
            return metrics

        all_metrics = compute_all_metrics(
            pred_labels=pred_labels,
            coordinates=coordinates,
            features=features,
            true_labels=true_labels,
        )
        metrics.update(all_metrics)
        logger.info(
            "Computed metrics: ARI=%.4f, NMI=%.4f, HOM=%.4f, COM=%.4f",
            metrics.get("ari", 0),
            metrics.get("nmi", 0),
            metrics.get("homogeneity", 0),
            metrics.get("completeness", 0),
        )
    except Exception:
        logger.warning("Failed to compute metrics", exc_info=True)

    return metrics


def _update_experiment_status(db: Session, experiment_id: Optional[str]) -> None:
    """Check if all runs for an experiment are done and update its status."""
    if not experiment_id:
        return
    run_repo = RunRepo(db)
    all_runs = run_repo.list_all()
    exp_runs = [r for r in all_runs if r.experiment_id == experiment_id]
    if not exp_runs:
        return
    statuses = {r.status for r in exp_runs}
    if statuses <= {"succeeded", "failed"}:
        final_status = "succeeded" if statuses == {"succeeded"} else "failed"
        exp_repo = ExperimentRepo(db)
        exp_repo.update_status(experiment_id, final_status)
        logger.info("Experiment %s -> %s", experiment_id, final_status)


def poll_runs(
    db: Session,
    runner: LocalRunner,
    registry: AlgorithmRegistry,
    build_demo_bundle: Optional[callable] = None,
    limit: int = 0,
) -> int:
    """Poll queued runs, execute them, and write results back.

    Returns the number of runs processed.
    """
    repo = RunRepo(db)
    queued = repo.list_queued()
    if limit > 0:
        queued = queued[:limit]

    if not queued:
        return 0

    # Track which experiments are affected
    affected_experiments: set = set()

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
        ds_platform = dataset_info.get("platform", "")
        ds_uri = dataset_info.get("uri", "")
        ds_metadata = dataset_info.get("metadata", {})

        if is_demo and build_demo_bundle is not None:
            data = build_demo_bundle()
        elif build_demo_bundle is not None and not ds_uri:
            # No real URI and demo builder available: use demo
            data = build_demo_bundle()
        elif ds_uri and ds_platform == "h5ad":
            # Real h5ad dataset - load from file
            try:
                from st_platform.io.h5ad_reader import read_h5ad_to_bundle

                data = read_h5ad_to_bundle(
                    path=ds_uri,
                    spatial_key=ds_metadata.get("spatial_key", "spatial"),
                    label_column=ds_metadata.get("label_column"),
                )
            except Exception as exc:
                repo.mark_failed(
                    run.run_id,
                    f"Failed to load h5ad dataset from {ds_uri}: {exc}",
                )
                processed += 1
                continue
        elif ds_uri and not is_demo:
            # Other real dataset types not yet supported
            repo.mark_failed(
                run.run_id,
                f"Real dataset loading not yet implemented for platform '{ds_platform}'. Dataset URI: {ds_uri}",
            )
            processed += 1
            continue
        else:
            repo.mark_failed(
                run.run_id,
                "No dataset URI provided and no demo data builder available. "
                "Please register a dataset or ensure the worker has demo data support.",
            )
            processed += 1
            continue

        params = _run_to_bundle_params(run)

        # Execute with memory tracking
        tracemalloc.start()
        try:
            result = runner.execute(
                task_type=task_type,
                algorithm_id=algo_id,
                data=data,
                parameters=params,
            )
        except Exception as exc:
            _, peak_bytes = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            repo.mark_failed(run.run_id, str(exc))
            logger.exception("Run %s failed with exception", run.run_id)
            processed += 1
            continue
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Write results back
        if result.status.value == "succeeded":
            # Add memory peak metric
            result_metrics = dict(result.metrics) if result.metrics else {}
            result_metrics["memory_peak_mb"] = peak_bytes / (1024 * 1024)

            # Compute all applicable metrics if ground-truth labels are available
            ground_truth_labels = data.metadata.get("labels")
            # Get features (expression matrix) from the data bundle
            features_array = None
            try:
                for asset in data.assets:
                    if asset.kind == "counts_table":
                        matrix = asset.metadata.get("matrix")
                        if matrix is not None:
                            import numpy as np
                            features_array = np.array(matrix, dtype=float)
                            break
            except Exception:
                logger.debug("Could not extract expression matrix for ASW computation")

            if ground_truth_labels is not None:
                result_metrics = _compute_clustering_metrics(
                    result_metrics, result, ground_truth_labels, features=features_array
                )

            # Normalize algorithm artifact URIs to relative paths
            normalized_artifacts = []
            for art in (result.artifacts or []):
                art_copy = dict(art)
                if "uri" in art_copy and art_copy["uri"]:
                    art_copy["uri"] = _relative_uri(art_copy["uri"])
                normalized_artifacts.append(art_copy)

            repo.mark_succeeded(
                run.run_id,
                summary=result.summary,
                metrics=result_metrics,
                artifacts=normalized_artifacts,
            )
            # Generate report artifacts (non-fatal)
            try:
                _generate_run_reports(run.run_id, result, db)
            except Exception:
                logger.warning("Report generation failed for run %s", run.run_id, exc_info=True)
        else:
            repo.mark_failed(run.run_id, result.error or "Unknown error")

        processed += 1
        if run.experiment_id:
            affected_experiments.add(run.experiment_id)
        logger.info("Processed run %s -> %s", run.run_id, result.status.value)

    # Update experiment statuses after all runs processed
    for exp_id in affected_experiments:
        try:
            _update_experiment_status(db, exp_id)
        except Exception:
            logger.warning("Failed to update experiment %s status", exp_id, exc_info=True)

    return processed
