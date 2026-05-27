"""Tests for multi-algorithm benchmark experiments."""

from __future__ import annotations

import os
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from st_platform.storage.database import Base

_tmpdir = tempfile.mkdtemp()

from fastapi.testclient import TestClient

from st_platform.api.deps import get_db_session
from st_platform.api.app import create_app


@pytest.fixture
def client():
    """Create a test client with an isolated DB per test."""
    db_path = os.path.join(_tmpdir, f"multi_{os.urandom(4).hex()}.db")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    db = TestSession()

    app = create_app()

    def _override_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db_session] = _override_db
    test_client = TestClient(app)

    yield test_client

    db.close()


class TestMultiAlgorithmExperiment:
    """Create an experiment with multiple algorithms, run them, and verify the report."""

    def test_multi_algo_experiment_flow(self, client):
        # 1. Register demo dataset
        resp = client.post("/api/datasets/register-demo")
        assert resp.status_code == 201
        dataset = resp.json()
        ds_id = dataset["dataset_id"]
        assert dataset["name"] == "STARmap BY3 1k (Demo)"

        # 2. Create experiment with two algorithms
        exp_payload = {
            "name": "Multi-Algo Benchmark",
            "task_type": "domain_detection",
            "algorithm_ids": ["spagcn-lite", "mock-domain"],
            "dataset_id": ds_id,
            "parameters": {"n_clusters": 3},
        }
        resp = client.post("/api/experiments", json=exp_payload)
        assert resp.status_code == 201
        experiment = resp.json()
        exp_id = experiment["experiment_id"]
        assert experiment["run_count"] == 2
        assert experiment["status"] == "running"

        # 3. Verify 2 queued runs were created
        resp = client.get(f"/api/experiments/{exp_id}/runs")
        assert resp.status_code == 200
        runs = resp.json()
        assert len(runs) == 2
        algo_ids = {r["algorithm_id"] for r in runs}
        assert algo_ids == {"spagcn-lite", "mock-domain"}
        for run in runs:
            assert run["status"] == "queued"

        # 4. Trigger worker poll - should process both runs
        resp = client.post("/api/worker/poll")
        assert resp.status_code == 200
        poll_result = resp.json()
        assert poll_result["processed"] == 2

        # 5. Verify both runs succeeded
        resp = client.get(f"/api/experiments/{exp_id}/runs")
        assert resp.status_code == 200
        runs_after = resp.json()
        assert len(runs_after) == 2
        for run in runs_after:
            assert run["status"] == "succeeded"
            assert run["started_at"] is not None
            assert run["finished_at"] is not None

        # 6. Get experiment report and verify it has metrics for both algorithms
        resp = client.get(f"/api/experiments/{exp_id}/report")
        assert resp.status_code == 200
        report = resp.json()
        assert report["experiment_id"] == exp_id
        assert report["name"] == "Multi-Algo Benchmark"
        assert len(report["runs"]) == 2

        # Verify each run has metrics
        for run in report["runs"]:
            assert len(run["metrics"]) > 0, f"No metrics for {run['algorithm_id']}"

        # 7. Verify the report includes a comparison summary
        comparison = report.get("comparison_summary", {})
        assert len(comparison) == 2, "Expected comparison for 2 algorithms"
        assert "spagcn-lite" in comparison
        assert "mock-domain" in comparison
        # Each algorithm should have at least one metric
        assert len(comparison["spagcn-lite"]) > 0
        assert len(comparison["mock-domain"]) > 0

    def test_multi_algo_register_all_demos(self, client):
        """Test the batch demo registration endpoint."""
        resp = client.post("/api/datasets/register-demo-all")
        assert resp.status_code == 201
        datasets = resp.json()
        assert len(datasets) == 2
        names = {d["name"] for d in datasets}
        assert "STARmap BY3 1k (Demo)" in names
        assert "osmFISH Mouse SS (Demo)" in names
        for d in datasets:
            assert d["metadata"]["demo"] is True

    def test_single_algo_no_comparison(self, client):
        """Verify comparison_summary is empty for single-algorithm experiments."""
        # Register demo dataset
        resp = client.post("/api/datasets/register-demo")
        assert resp.status_code == 201
        ds_id = resp.json()["dataset_id"]

        # Create experiment with single algorithm
        exp_payload = {
            "name": "Single Algo Test",
            "task_type": "domain_detection",
            "algorithm_ids": ["mock-domain"],
            "dataset_id": ds_id,
        }
        resp = client.post("/api/experiments", json=exp_payload)
        assert resp.status_code == 201
        exp_id = resp.json()["experiment_id"]

        # Run worker
        resp = client.post("/api/worker/poll")
        assert resp.status_code == 200

        # Get report - comparison_summary should be empty
        resp = client.get(f"/api/experiments/{exp_id}/report")
        assert resp.status_code == 200
        report = resp.json()
        comparison = report.get("comparison_summary", {})
        assert len(comparison) == 0, "No comparison expected for single algorithm"
