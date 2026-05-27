"""Report generation: CSV, PNG plots, Markdown summaries."""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sqlalchemy.orm import Session

from st_platform.storage.repositories import ArtifactRepo, MetricRepo, RunRepo

logger = logging.getLogger(__name__)


def generate_run_metrics_csv(run_data: dict, output_path: str) -> str:
    """Generate CSV with run metrics.

    Parameters
    ----------
    run_data : dict
        Must contain ``run_id``, ``algorithm_id``, ``metrics`` (dict of float).
    output_path : str
        Destination file path.

    Returns
    -------
    str
        The *output_path* written.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    metrics: Dict[str, float] = run_data.get("metrics", {})
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["run_id", "algorithm_id", "metric_name", "metric_value"])
        for name, value in sorted(metrics.items()):
            writer.writerow([run_data.get("run_id", ""), run_data.get("algorithm_id", ""), name, value])

    return str(path)


def generate_domain_predictions_csv(domain_assignments: dict, output_path: str) -> str:
    """Generate CSV with spot_id, domain, x, y.

    Parameters
    ----------
    domain_assignments : dict
        Must contain ``domains`` key with a list of dicts having
        ``spot_id``, ``domain``, ``x``, ``y``.
    output_path : str
        Destination file path.

    Returns
    -------
    str
        The *output_path* written.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    domains: List[dict] = domain_assignments.get("domains", [])
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["spot_id", "domain", "x", "y"])
        for d in domains:
            writer.writerow([d.get("spot_id", ""), d.get("domain", ""), d.get("x", ""), d.get("y", "")])

    return str(path)


def generate_domain_grid_plot(domain_assignments: dict, output_path: str) -> str:
    """Generate scatter plot of spatial domains colored by label.

    Parameters
    ----------
    domain_assignments : dict
        Must contain ``domains`` key.
    output_path : str
        Destination file path (PNG).

    Returns
    -------
    str
        The *output_path* written.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    domains: List[dict] = domain_assignments.get("domains", [])
    if not domains:
        # Create an empty placeholder image
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.text(0.5, 0.5, "No domain data", ha="center", va="center", transform=ax.transAxes)
        fig.savefig(str(path), dpi=100, bbox_inches="tight")
        plt.close(fig)
        return str(path)

    x = [d.get("x", 0) for d in domains]
    y = [d.get("y", 0) for d in domains]
    labels = [d.get("domain", 0) for d in domains]

    fig, ax = plt.subplots(figsize=(8, 8))
    scatter = ax.scatter(x, y, c=labels, cmap="tab10", s=12, edgecolors="none")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Spatial Domain Predictions")
    ax.invert_yaxis()
    fig.colorbar(scatter, ax=ax, label="Domain")
    fig.savefig(str(path), dpi=100, bbox_inches="tight")
    plt.close(fig)

    return str(path)


def generate_metrics_bar_plot(metrics: dict, output_path: str) -> str:
    """Generate bar chart of metric values.

    Parameters
    ----------
    metrics : dict
        Mapping of metric name to float value.
    output_path : str
        Destination file path (PNG).

    Returns
    -------
    str
        The *output_path* written.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not metrics:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, "No metrics data", ha="center", va="center", transform=ax.transAxes)
        fig.savefig(str(path), dpi=100, bbox_inches="tight")
        plt.close(fig)
        return str(path)

    names = list(metrics.keys())
    values = [metrics[k] for k in names]

    fig, ax = plt.subplots(figsize=(max(6, len(names) * 1.2), 4))
    bars = ax.bar(names, values, color="#4e79a7")
    ax.set_ylabel("Value")
    ax.set_title("Run Metrics")
    ax.tick_params(axis="x", rotation=30)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{val:.2f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    fig.tight_layout()
    fig.savefig(str(path), dpi=100, bbox_inches="tight")
    plt.close(fig)

    return str(path)


def generate_markdown_report(
    experiment_info: dict, runs_data: list[dict], output_path: str
) -> str:
    """Generate Markdown report with summary table and per-run details.

    Parameters
    ----------
    experiment_info : dict
        Experiment metadata (name, status, etc.).
    runs_data : list[dict]
        Each dict has ``run_id``, ``algorithm_id``, ``status``, ``metrics``, ``artifacts``.
    output_path : str
        Destination file path.

    Returns
    -------
    str
        The *output_path* written.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    lines.append(f"# Experiment Report: {experiment_info.get('name', 'Unknown')}")
    lines.append("")
    lines.append(f"- **Experiment ID**: `{experiment_info.get('experiment_id', '')}`")
    lines.append(f"- **Status**: {experiment_info.get('status', '')}")
    lines.append(f"- **Task Type**: {experiment_info.get('task_type', '')}")
    lines.append(f"- **Run Count**: {len(runs_data)}")
    lines.append("")

    # Summary table
    if runs_data:
        lines.append("## Summary Table")
        lines.append("")
        lines.append("| Run ID | Algorithm | Status | Metrics |")
        lines.append("|--------|-----------|--------|---------|")
        for run in runs_data:
            metrics = run.get("metrics", {})
            metrics_str = ", ".join(f"{k}={v:.3f}" for k, v in sorted(metrics.items()))
            lines.append(
                f"| `{run.get('run_id', '')[:12]}` "
                f"| {run.get('algorithm_id', '')} "
                f"| {run.get('status', '')} "
                f"| {metrics_str} |"
            )
        lines.append("")

    # Per-run details
    for run in runs_data:
        lines.append(f"## Run: {run.get('algorithm_id', '')} (`{run.get('run_id', '')}`)")
        lines.append("")
        lines.append(f"- **Status**: {run.get('status', '')}")
        if run.get("error"):
            lines.append(f"- **Error**: {run['error']}")
        lines.append("")

        metrics = run.get("metrics", {})
        if metrics:
            lines.append("### Metrics")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")
            for name, value in sorted(metrics.items()):
                lines.append(f"| {name} | {value:.4f} |")
            lines.append("")

        artifacts = run.get("artifacts", [])
        if artifacts:
            lines.append("### Artifacts")
            lines.append("")
            lines.append("| Kind | URI | Description |")
            lines.append("|------|-----|-------------|")
            for a in artifacts:
                lines.append(f"| {a.get('kind', '')} | `{a.get('uri', '')}` | {a.get('description', '')} |")
            lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


def generate_experiment_report(
    experiment_id: str, db: Session, output_dir: str
) -> dict:
    """Generate all reports for an experiment.

    Returns
    -------
    dict
        Keys are artifact names, values are file paths.
    """
    from st_platform.storage.models import ExperimentModel, RunModel

    exp = db.query(ExperimentModel).filter(ExperimentModel.experiment_id == experiment_id).first()
    if exp is None:
        raise ValueError(f"Experiment '{experiment_id}' not found")

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    experiment_info = {
        "experiment_id": exp.experiment_id,
        "name": exp.name,
        "status": exp.status,
        "task_type": exp.task_type,
    }

    runs = db.query(RunModel).filter(RunModel.experiment_id == experiment_id).all()
    metric_repo = MetricRepo(db)
    artifact_repo = ArtifactRepo(db)

    runs_data: List[dict] = []
    for run in runs:
        metrics = {m.name: m.value for m in metric_repo.list_for_run(run.run_id)}
        artifacts_list: List[dict] = []
        for a in artifact_repo.list_for_run(run.run_id):
            try:
                meta = json.loads(a.metadata_json)
            except (json.JSONDecodeError, TypeError):
                meta = {}
            artifacts_list.append({
                "kind": a.kind,
                "uri": a.uri,
                "description": a.description,
                "metadata": meta,
            })
        runs_data.append({
            "run_id": run.run_id,
            "algorithm_id": run.algorithm_id,
            "status": run.status,
            "metrics": metrics,
            "artifacts": artifacts_list,
            "error": run.error,
        })

    paths: Dict[str, str] = {}

    # Aggregate metrics CSV
    try:
        all_metrics_path = str(out_dir / "all_metrics.csv")
        with open(all_metrics_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["run_id", "algorithm_id", "metric_name", "metric_value"])
            for run in runs_data:
                for name, value in sorted(run.get("metrics", {}).items()):
                    writer.writerow([run["run_id"], run["algorithm_id"], name, value])
        paths["all_metrics_csv"] = all_metrics_path
    except Exception:
        logger.warning("Failed to generate aggregate metrics CSV", exc_info=True)

    # Per-run CSVs and plots
    for run in runs_data:
        rid = run["run_id"]

        # Run metrics CSV
        try:
            csv_path = str(out_dir / f"{rid}_metrics.csv")
            generate_run_metrics_csv(run, csv_path)
            paths[f"{rid}_metrics_csv"] = csv_path
        except Exception:
            logger.warning("Failed to generate metrics CSV for run %s", rid, exc_info=True)

        # Metrics bar plot
        try:
            bar_path = str(out_dir / f"{rid}_metrics_bar.png")
            generate_metrics_bar_plot(run.get("metrics", {}), bar_path)
            paths[f"{rid}_metrics_bar_png"] = bar_path
        except Exception:
            logger.warning("Failed to generate metrics bar plot for run %s", rid, exc_info=True)

        # Domain predictions from artifacts
        for art in run.get("artifacts", []):
            if art.get("kind") == "domain_assignments":
                try:
                    uri = art.get("uri", "")
                    if uri and Path(uri).exists():
                        domain_data = json.loads(Path(uri).read_text(encoding="utf-8"))
                        # Domain CSV
                        dom_csv_path = str(out_dir / f"{rid}_domain_predictions.csv")
                        generate_domain_predictions_csv(domain_data, dom_csv_path)
                        paths[f"{rid}_domain_predictions_csv"] = dom_csv_path
                        # Domain grid plot
                        grid_path = str(out_dir / f"{rid}_domain_grid.png")
                        generate_domain_grid_plot(domain_data, grid_path)
                        paths[f"{rid}_domain_grid_png"] = grid_path
                except Exception:
                    logger.warning("Failed to generate domain reports for run %s", rid, exc_info=True)

    # Markdown report
    try:
        md_path = str(out_dir / "report.md")
        generate_markdown_report(experiment_info, runs_data, md_path)
        paths["markdown_report"] = md_path
    except Exception:
        logger.warning("Failed to generate markdown report", exc_info=True)

    return paths
