"""Tests for report generation functions."""

from __future__ import annotations

import csv
import json
import os
import tempfile

import pytest

from st_platform.benchmark.reports import (
    generate_domain_grid_plot,
    generate_domain_predictions_csv,
    generate_experiment_report,
    generate_markdown_report,
    generate_metrics_bar_plot,
    generate_run_metrics_csv,
)

_tmpdir = tempfile.mkdtemp()


class TestGenerateRunMetricsCsv:
    def test_creates_valid_csv(self):
        path = os.path.join(_tmpdir, "test_run_metrics.csv")
        run_data = {
            "run_id": "abc123",
            "algorithm_id": "spagcn-lite",
            "metrics": {"spot_count": 100.0, "gene_count": 50.0},
        }
        result = generate_run_metrics_csv(run_data, path)
        assert result == path
        assert os.path.exists(path)

        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            rows = list(reader)
        assert rows[0] == ["run_id", "algorithm_id", "metric_name", "metric_value"]
        assert len(rows) == 3  # header + 2 metrics

    def test_empty_metrics(self):
        path = os.path.join(_tmpdir, "test_empty_metrics.csv")
        run_data = {"run_id": "r1", "algorithm_id": "a1", "metrics": {}}
        result = generate_run_metrics_csv(run_data, path)
        assert os.path.exists(result)

        with open(path, newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        assert len(rows) == 1  # header only

    def test_creates_parent_dirs(self):
        path = os.path.join(_tmpdir, "subdir", "nested", "metrics.csv")
        generate_run_metrics_csv({"run_id": "x", "algorithm_id": "y", "metrics": {"m": 1.0}}, path)
        assert os.path.exists(path)


class TestGenerateDomainPredictionsCsv:
    def test_creates_valid_csv(self):
        path = os.path.join(_tmpdir, "test_domain_pred.csv")
        data = {
            "domains": [
                {"spot_id": "s1", "domain": 0, "x": 1.0, "y": 2.0},
                {"spot_id": "s2", "domain": 1, "x": 3.0, "y": 4.0},
            ]
        }
        result = generate_domain_predictions_csv(data, path)
        assert os.path.exists(result)

        with open(path, newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        assert rows[0] == ["spot_id", "domain", "x", "y"]
        assert len(rows) == 3

    def test_empty_domains(self):
        path = os.path.join(_tmpdir, "test_empty_domains.csv")
        generate_domain_predictions_csv({"domains": []}, path)
        assert os.path.exists(path)


class TestGenerateDomainGridPlot:
    def test_creates_png(self):
        path = os.path.join(_tmpdir, "test_domain_grid.png")
        data = {
            "domains": [
                {"spot_id": "s1", "domain": 0, "x": 1.0, "y": 2.0},
                {"spot_id": "s2", "domain": 1, "x": 3.0, "y": 4.0},
                {"spot_id": "s3", "domain": 0, "x": 2.0, "y": 3.0},
            ]
        }
        result = generate_domain_grid_plot(data, path)
        assert os.path.exists(result)
        assert os.path.getsize(result) > 0

    def test_empty_data_creates_placeholder(self):
        path = os.path.join(_tmpdir, "test_empty_grid.png")
        result = generate_domain_grid_plot({"domains": []}, path)
        assert os.path.exists(result)
        assert os.path.getsize(result) > 0


class TestGenerateMetricsBarPlot:
    def test_creates_png(self):
        path = os.path.join(_tmpdir, "test_metrics_bar.png")
        metrics = {"spot_count": 100.0, "gene_count": 50.0, "agreement": 0.85}
        result = generate_metrics_bar_plot(metrics, path)
        assert os.path.exists(result)
        assert os.path.getsize(result) > 0

    def test_empty_metrics_creates_placeholder(self):
        path = os.path.join(_tmpdir, "test_empty_bar.png")
        result = generate_metrics_bar_plot({}, path)
        assert os.path.exists(result)
        assert os.path.getsize(result) > 0


class TestGenerateMarkdownReport:
    def test_creates_md_file(self):
        path = os.path.join(_tmpdir, "test_report.md")
        exp_info = {
            "experiment_id": "exp123",
            "name": "Test Exp",
            "status": "running",
            "task_type": "domain_detection",
        }
        runs = [
            {
                "run_id": "r1",
                "algorithm_id": "spagcn-lite",
                "status": "succeeded",
                "metrics": {"spot_count": 100.0},
                "artifacts": [
                    {"kind": "csv", "uri": "/path/to/file.csv", "description": "test"}
                ],
            }
        ]
        result = generate_markdown_report(exp_info, runs, path)
        assert os.path.exists(result)

        content = open(path, encoding="utf-8").read()
        assert "Test Exp" in content
        assert "spagcn-lite" in content
        assert "spot_count" in content

    def test_empty_runs(self):
        path = os.path.join(_tmpdir, "test_empty_report.md")
        exp_info = {"experiment_id": "e1", "name": "Empty", "status": "created"}
        result = generate_markdown_report(exp_info, [], path)
        assert os.path.exists(result)
        content = open(path, encoding="utf-8").read()
        assert "Empty" in content


class TestGenerateExperimentReport:
    """Integration test using a real SQLite database."""

    def _make_db(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from st_platform.storage.database import Base

        db_path = os.path.join(_tmpdir, f"report_test_{os.urandom(4).hex()}.db")
        engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        return Session()

    def test_generate_full_report(self):
        from st_platform.storage.repositories import ExperimentRepo, RunRepo

        db = self._make_db()
        exp_repo = ExperimentRepo(db)
        run_repo = RunRepo(db)

        exp = exp_repo.create(name="Report Test", task_type="domain_detection")
        run_repo.create(
            algorithm_id="spagcn-lite",
            task_type="domain_detection",
            experiment_id=exp.experiment_id,
        )

        # Mark run as succeeded with metrics and artifacts
        run = db.query(
            __import__("st_platform.storage.models", fromlist=["RunModel"]).RunModel
        ).filter_by(experiment_id=exp.experiment_id).first()

        # Write a domain assignments file for the run to reference
        run_root = os.path.join(_tmpdir, run.run_id)
        os.makedirs(run_root, exist_ok=True)
        domain_path = os.path.join(run_root, "domains.json")
        domain_data = {
            "domains": [
                {"spot_id": "s1", "domain": 0, "x": 1.0, "y": 2.0},
                {"spot_id": "s2", "domain": 1, "x": 3.0, "y": 4.0},
            ]
        }
        with open(domain_path, "w") as f:
            json.dump(domain_data, f)

        run_repo.mark_succeeded(
            run.run_id,
            summary={"message": "done"},
            metrics={"spot_count": 100.0, "gene_count": 50.0},
            artifacts=[
                {
                    "kind": "domain_assignments",
                    "uri": domain_path,
                    "description": "test domains",
                }
            ],
        )

        out_dir = os.path.join(_tmpdir, f"report_output_{os.urandom(4).hex()}")
        paths = generate_experiment_report(exp.experiment_id, db, out_dir)

        assert "all_metrics_csv" in paths
        assert os.path.exists(paths["all_metrics_csv"])
        assert "markdown_report" in paths
        assert os.path.exists(paths["markdown_report"])

        # Per-run artifacts
        csv_key = f"{run.run_id}_metrics_csv"
        assert csv_key in paths
        assert os.path.exists(paths[csv_key])

        bar_key = f"{run.run_id}_metrics_bar_png"
        assert bar_key in paths
        assert os.path.exists(paths[bar_key])

        dom_csv_key = f"{run.run_id}_domain_predictions_csv"
        assert dom_csv_key in paths
        assert os.path.exists(paths[dom_csv_key])

        grid_key = f"{run.run_id}_domain_grid_png"
        assert grid_key in paths
        assert os.path.exists(paths[grid_key])

        db.close()

    def test_experiment_not_found(self):
        db = self._make_db()
        with pytest.raises(ValueError, match="not found"):
            generate_experiment_report("nonexistent", db, _tmpdir)
        db.close()
