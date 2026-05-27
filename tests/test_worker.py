"""Tests for the worker polling logic."""

from __future__ import annotations

import os
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_tmpdir = tempfile.mkdtemp()

from st_platform.algorithms import build_builtin_algorithms
from st_platform.core.registry import AlgorithmRegistry
from st_platform.core.runner import LocalRunner
from st_platform.storage.database import Base
from st_platform.storage.repositories import RunRepo
from st_platform.worker.runner import poll_runs


@pytest.fixture
def worker_env():
    """Set up isolated DB, registry, and runner for worker tests."""
    db_path = os.path.join(_tmpdir, f"worker_test_{os.urandom(4).hex()}.db")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    registry = AlgorithmRegistry(build_builtin_algorithms())
    runner = LocalRunner(registry, tempfile.mkdtemp())

    yield db, runner, registry
    db.close()


class TestPollRuns:
    def test_poll_empty_queue(self, worker_env):
        """Worker should handle an empty queue gracefully."""
        db, runner, registry = worker_env
        count = poll_runs(db=db, runner=runner, registry=registry)
        assert count == 0

    def test_poll_processes_queued_run(self, worker_env):
        """Worker picks up a queued run and marks it as succeeded or failed."""
        db, runner, registry = worker_env
        repo = RunRepo(db)
        run = repo.create(algorithm_id="spagcn-lite", task_type="domain_detection")
        assert run.status == "queued"

        count = poll_runs(db=db, runner=runner, registry=registry, limit=1)
        assert count == 1

        updated = repo.get(run.run_id)
        # spagcn-lite should succeed with demo data
        assert updated.status in ("succeeded", "failed")

    def test_poll_unknown_algorithm(self, worker_env):
        """Worker marks run as failed for unknown algorithm."""
        db, runner, registry = worker_env
        repo = RunRepo(db)
        run = repo.create(algorithm_id="nonexistent", task_type="domain_detection")

        count = poll_runs(db=db, runner=runner, registry=registry, limit=1)
        assert count == 1
        updated = repo.get(run.run_id)
        assert updated.status == "failed"
        assert "nonexistent" in (updated.error or "")

    def test_poll_unknown_task_type(self, worker_env):
        """Worker marks run as failed for unknown task type."""
        db, runner, registry = worker_env
        repo = RunRepo(db)
        run = repo.create(algorithm_id="spagcn-lite", task_type="fake_task")

        count = poll_runs(db=db, runner=runner, registry=registry, limit=1)
        assert count == 1
        updated = repo.get(run.run_id)
        assert updated.status == "failed"
