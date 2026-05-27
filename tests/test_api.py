"""Tests for the FastAPI API endpoints."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

# Use a temp DB for isolation
_tmpdir = tempfile.mkdtemp()
os.environ["ST_PLATFORM_DB_URL"] = f"sqlite:///{_tmpdir}/test.db"

from fastapi.testclient import TestClient

from st_platform.api.app import create_app
from st_platform.storage.database import init_db


@pytest.fixture(scope="module")
def client():
    """Create a test client with a fresh DB."""
    init_db()
    app = create_app()
    return TestClient(app)


class TestHealth:
    def test_health_returns_200(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestAlgorithms:
    def test_list_algorithms(self, client):
        resp = client.get("/api/algorithms")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Check first algorithm has required fields
        algo = data[0]
        assert "algorithm_id" in algo
        assert "name" in algo
        assert "task_type" in algo

    def test_get_algorithm_by_id(self, client):
        # First get the list
        resp = client.get("/api/algorithms")
        algo_id = resp.json()[0]["algorithm_id"]
        resp2 = client.get(f"/api/algorithms/{algo_id}")
        assert resp2.status_code == 200
        assert resp2.json()["algorithm_id"] == algo_id

    def test_get_algorithm_not_found(self, client):
        resp = client.get("/api/algorithms/nonexistent-algo")
        assert resp.status_code == 404


class TestDatasets:
    def test_list_datasets_empty(self, client):
        resp = client.get("/api/datasets")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_register_and_get_dataset(self, client):
        payload = {
            "name": "Test Dataset",
            "platform": "visium",
            "sample_id": "sample-1",
            "description": "A test dataset",
            "metadata": {"organism": "human"},
        }
        resp = client.post("/api/datasets/register", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        ds_id = data["dataset_id"]
        assert data["name"] == "Test Dataset"
        assert data["platform"] == "visium"

        # Get by ID
        resp2 = client.get(f"/api/datasets/{ds_id}")
        assert resp2.status_code == 200
        assert resp2.json()["dataset_id"] == ds_id

    def test_get_dataset_not_found(self, client):
        resp = client.get("/api/datasets/nonexistent")
        assert resp.status_code == 404


class TestExperiments:
    def test_create_experiment(self, client):
        # Register a dataset first
        ds_resp = client.post(
            "/api/datasets/register",
            json={"name": "Exp Dataset", "platform": "visium"},
        )
        ds_id = ds_resp.json()["dataset_id"]

        payload = {
            "name": "Test Experiment",
            "task_type": "domain_detection",
            "algorithm_ids": ["spagcn-lite"],
            "dataset_id": ds_id,
            "parameters": {"n_clusters": 3},
        }
        resp = client.post("/api/experiments", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Test Experiment"
        assert data["task_type"] == "domain_detection"
        assert data["run_count"] == 1

    def test_list_experiments(self, client):
        resp = client.get("/api/experiments")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_experiment_not_found(self, client):
        resp = client.get("/api/experiments/nonexistent")
        assert resp.status_code == 404


class TestRuns:
    def test_list_runs(self, client):
        resp = client.get("/api/runs")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_run_not_found(self, client):
        resp = client.get("/api/runs/nonexistent")
        assert resp.status_code == 404
