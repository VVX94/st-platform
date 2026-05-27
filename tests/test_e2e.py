"""End-to-end test for the full benchmark flow."""

from __future__ import annotations

import json
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
from st_platform.storage.repositories import RunRepo


@pytest.fixture
def client():
    """Create a test client with an isolated DB per test."""
    db_path = os.path.join(_tmpdir, f"e2e_{os.urandom(4).hex()}.db")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    db = TestSession()

    app = create_app()

    def _override_db():
        try:
            yield db
        finally:
            pass  # Don't close here, fixture handles cleanup

    app.dependency_overrides[get_db_session] = _override_db
    test_client = TestClient(app)

    yield test_client

    db.close()


class TestFullBenchmarkFlow:
    """Register demo dataset -> create experiment -> poll worker -> check results."""

    def test_full_benchmark_flow(self, client):
        # 1. Register demo dataset
        resp = client.post("/api/datasets/register-demo")
        assert resp.status_code == 201
        dataset = resp.json()
        ds_id = dataset["dataset_id"]
        assert dataset["name"] == "STARmap BY3 1k (Demo)"
        assert dataset["platform"] == "starmap"
        assert dataset["metadata"]["demo"] is True

        # 2. Create experiment with spagcn-lite
        exp_payload = {
            "name": "E2E Benchmark Test",
            "task_type": "domain_detection",
            "algorithm_ids": ["spagcn-lite"],
            "dataset_id": ds_id,
            "parameters": {"n_clusters": 3},
        }
        resp = client.post("/api/experiments", json=exp_payload)
        assert resp.status_code == 201
        experiment = resp.json()
        exp_id = experiment["experiment_id"]
        assert experiment["run_count"] == 1
        assert experiment["status"] == "running"

        # 3. Verify run is queued
        resp = client.get(f"/api/experiments/{exp_id}/runs")
        assert resp.status_code == 200
        runs = resp.json()
        assert len(runs) == 1
        run = runs[0]
        run_id = run["run_id"]
        assert run["status"] == "queued"
        assert run["algorithm_id"] == "spagcn-lite"

        # Verify dataset info was passed to the run
        assert run["dataset"]["dataset_id"] == ds_id
        assert run["dataset"]["metadata"]["demo"] is True

        # 4. Trigger worker poll
        resp = client.post("/api/worker/poll")
        assert resp.status_code == 200
        poll_result = resp.json()
        assert poll_result["processed"] == 1

        # 5. Verify run succeeded
        resp = client.get(f"/api/runs/{run_id}")
        assert resp.status_code == 200
        run_after = resp.json()
        assert run_after["status"] == "succeeded"
        assert run_after["started_at"] is not None
        assert run_after["finished_at"] is not None

        # 6. Verify metrics exist
        resp = client.get(f"/api/runs/{run_id}/metrics")
        assert resp.status_code == 200
        metrics = resp.json()
        assert isinstance(metrics, list)
        assert len(metrics) > 0
        # Each metric should have required fields
        for m in metrics:
            assert "metric_id" in m
            assert "name" in m
            assert "value" in m
            assert m["run_id"] == run_id

        # 7. Verify artifacts exist
        resp = client.get(f"/api/runs/{run_id}/artifacts")
        assert resp.status_code == 200
        artifacts = resp.json()
        assert isinstance(artifacts, list)
        assert len(artifacts) > 0
        for a in artifacts:
            assert "artifact_id" in a
            assert "kind" in a
            assert "uri" in a
            assert a["run_id"] == run_id

    def test_experiment_runs_endpoint(self, client):
        """Test the experiment runs listing endpoint."""
        # Create an experiment
        resp = client.post(
            "/api/datasets/register",
            json={"name": "Test DS", "platform": "visium"},
        )
        ds_id = resp.json()["dataset_id"]

        resp = client.post(
            "/api/experiments",
            json={
                "name": "Runs Test Exp",
                "task_type": "domain_detection",
                "algorithm_ids": ["spagcn-lite"],
                "dataset_id": ds_id,
            },
        )
        exp_id = resp.json()["experiment_id"]

        # List runs for this experiment
        resp = client.get(f"/api/experiments/{exp_id}/runs")
        assert resp.status_code == 200
        runs = resp.json()
        assert len(runs) == 1
        assert runs[0]["experiment_id"] == exp_id

    def test_experiment_runs_not_found(self, client):
        """Test 404 for nonexistent experiment runs."""
        resp = client.get("/api/experiments/nonexistent/runs")
        assert resp.status_code == 404

    def test_run_metrics_not_found(self, client):
        """Test 404 for nonexistent run metrics."""
        resp = client.get("/api/runs/nonexistent/metrics")
        assert resp.status_code == 404

    def test_run_artifacts_not_found(self, client):
        """Test 404 for nonexistent run artifacts."""
        resp = client.get("/api/runs/nonexistent/artifacts")
        assert resp.status_code == 404
