"""Tests for the storage layer: DB init and CRUD operations."""

from __future__ import annotations

import json
import os
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Use a separate temp DB for storage tests
_tmpdir = tempfile.mkdtemp()
os.environ["ST_PLATFORM_DB_URL"] = f"sqlite:///{_tmpdir}/test_storage.db"

from st_platform.storage.database import Base, init_db
from st_platform.storage.models import (
    ArtifactModel,
    DatasetModel,
    ExperimentModel,
    MetricModel,
    RunModel,
)
from st_platform.storage.repositories import (
    ArtifactRepo,
    DatasetRepo,
    ExperimentRepo,
    MetricRepo,
    RunRepo,
)


@pytest.fixture(autouse=True)
def fresh_db():
    """Create fresh tables for each test."""
    from st_platform.storage import database as db_mod

    # Re-create engine pointing to a per-test file
    db_path = os.path.join(_tmpdir, f"test_{os.urandom(4).hex()}.db")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    db_mod.engine = engine
    db_mod.SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = db_mod.SessionLocal()
    yield db
    db.close()


class TestDBInit:
    def test_tables_created(self, fresh_db):
        """Verify all expected tables exist."""
        from st_platform.storage.database import engine

        tables = set(Base.metadata.tables.keys())
        assert "datasets" in tables
        assert "experiments" in tables
        assert "runs" in tables
        assert "metrics" in tables
        assert "artifacts" in tables


class TestDatasetRepo:
    def test_create_and_get(self, fresh_db):
        repo = DatasetRepo(fresh_db)
        ds = repo.create(name="Test", platform="visium", sample_id="s1")
        assert ds.dataset_id
        assert ds.name == "Test"

        fetched = repo.get(ds.dataset_id)
        assert fetched is not None
        assert fetched.name == "Test"

    def test_list_all(self, fresh_db):
        repo = DatasetRepo(fresh_db)
        repo.create(name="A")
        repo.create(name="B")
        assert len(repo.list_all()) == 2


class TestExperimentRepo:
    def test_create_and_get(self, fresh_db):
        repo = ExperimentRepo(fresh_db)
        exp = repo.create(name="Exp1", task_type="domain_detection")
        assert exp.experiment_id
        assert exp.status == "created"

        fetched = repo.get(exp.experiment_id)
        assert fetched is not None

    def test_update_status(self, fresh_db):
        repo = ExperimentRepo(fresh_db)
        exp = repo.create(name="Exp2", task_type="domain_detection")
        updated = repo.update_status(exp.experiment_id, "running")
        assert updated is not None
        assert updated.status == "running"


class TestRunRepo:
    def test_create_and_get(self, fresh_db):
        repo = RunRepo(fresh_db)
        run = repo.create(algorithm_id="spagcn-lite", task_type="domain_detection")
        assert run.run_id
        assert run.status == "queued"

    def test_list_queued(self, fresh_db):
        repo = RunRepo(fresh_db)
        repo.create(algorithm_id="spagcn-lite", task_type="domain_detection")
        repo.create(algorithm_id="ccst", task_type="domain_detection")
        queued = repo.list_queued()
        assert len(queued) == 2

    def test_mark_running(self, fresh_db):
        repo = RunRepo(fresh_db)
        run = repo.create(algorithm_id="spagcn-lite", task_type="domain_detection")
        updated = repo.mark_running(run.run_id)
        assert updated.status == "running"
        assert updated.started_at is not None

    def test_mark_succeeded(self, fresh_db):
        repo = RunRepo(fresh_db)
        run = repo.create(algorithm_id="spagcn-lite", task_type="domain_detection")
        repo.mark_succeeded(
            run.run_id,
            summary={"clusters": 3},
            metrics={"silhouette": 0.45},
            artifacts=[{"kind": "plot", "uri": "/tmp/plot.png", "description": "test"}],
        )
        updated = repo.get(run.run_id)
        assert updated.status == "succeeded"
        assert updated.finished_at is not None

        # Check metrics and artifacts were written
        metric_repo = MetricRepo(fresh_db)
        metrics = metric_repo.list_for_run(run.run_id)
        assert len(metrics) == 1
        assert metrics[0].name == "silhouette"

        art_repo = ArtifactRepo(fresh_db)
        arts = art_repo.list_for_run(run.run_id)
        assert len(arts) == 1

    def test_mark_failed(self, fresh_db):
        repo = RunRepo(fresh_db)
        run = repo.create(algorithm_id="spagcn-lite", task_type="domain_detection")
        repo.mark_failed(run.run_id, "Something broke")
        updated = repo.get(run.run_id)
        assert updated.status == "failed"
        assert updated.error == "Something broke"
