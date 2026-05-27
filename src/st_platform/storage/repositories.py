from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from st_platform.storage.models import (
    ArtifactModel,
    DatasetModel,
    ExperimentModel,
    MetricModel,
    RunModel,
)


class DatasetRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        name: str,
        platform: str = "visium",
        sample_id: str = "",
        uri: Optional[str] = None,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DatasetModel:
        ds = DatasetModel(
            name=name,
            platform=platform,
            sample_id=sample_id,
            uri=uri,
            description=description,
            metadata_json=json.dumps(metadata or {}),
        )
        self.db.add(ds)
        self.db.commit()
        self.db.refresh(ds)
        return ds

    def get(self, dataset_id: str) -> Optional[DatasetModel]:
        return self.db.query(DatasetModel).filter(DatasetModel.dataset_id == dataset_id).first()

    def list_all(self) -> List[DatasetModel]:
        return self.db.query(DatasetModel).all()


class ExperimentRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        name: str,
        task_type: str,
        dataset_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> ExperimentModel:
        exp = ExperimentModel(
            name=name,
            task_type=task_type,
            dataset_id=dataset_id,
            parameters_json=json.dumps(parameters or {}),
        )
        self.db.add(exp)
        self.db.commit()
        self.db.refresh(exp)
        return exp

    def get(self, experiment_id: str) -> Optional[ExperimentModel]:
        return (
            self.db.query(ExperimentModel)
            .filter(ExperimentModel.experiment_id == experiment_id)
            .first()
        )

    def list_all(self) -> List[ExperimentModel]:
        return self.db.query(ExperimentModel).all()

    def update_status(self, experiment_id: str, status: str) -> Optional[ExperimentModel]:
        exp = self.get(experiment_id)
        if exp:
            exp.status = status
            self.db.commit()
            self.db.refresh(exp)
        return exp


class RunRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        algorithm_id: str,
        task_type: str,
        experiment_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        dataset: Optional[Dict[str, Any]] = None,
    ) -> RunModel:
        run = RunModel(
            algorithm_id=algorithm_id,
            task_type=task_type,
            experiment_id=experiment_id,
            parameters_json=json.dumps(parameters or {}),
            dataset_json=json.dumps(dataset or {}),
            status="queued",
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def get(self, run_id: str) -> Optional[RunModel]:
        return self.db.query(RunModel).filter(RunModel.run_id == run_id).first()

    def list_all(self) -> List[RunModel]:
        return self.db.query(RunModel).all()

    def list_queued(self) -> List[RunModel]:
        return self.db.query(RunModel).filter(RunModel.status == "queued").all()

    def mark_running(self, run_id: str) -> Optional[RunModel]:
        run = self.get(run_id)
        if run:
            run.status = "running"
            run.started_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(run)
        return run

    def mark_succeeded(
        self,
        run_id: str,
        summary: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, float]] = None,
        artifacts: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[RunModel]:
        run = self.get(run_id)
        if run:
            run.status = "succeeded"
            run.finished_at = datetime.now(timezone.utc)
            run.summary_json = json.dumps(summary or {})
            self.db.commit()
            # Write metrics
            if metrics:
                for name, value in metrics.items():
                    m = MetricModel(run_id=run_id, name=name, value=float(value))
                    self.db.add(m)
            # Write artifacts
            if artifacts:
                for art in artifacts:
                    a = ArtifactModel(
                        run_id=run_id,
                        kind=art.get("kind", ""),
                        uri=art.get("uri", ""),
                        description=art.get("description", ""),
                        metadata_json=json.dumps(art.get("metadata", {})),
                    )
                    self.db.add(a)
            self.db.commit()
            self.db.refresh(run)
        return run

    def mark_failed(self, run_id: str, error: str) -> Optional[RunModel]:
        run = self.get(run_id)
        if run:
            run.status = "failed"
            run.finished_at = datetime.now(timezone.utc)
            run.error = error
            self.db.commit()
            self.db.refresh(run)
        return run


class MetricRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_run(self, run_id: str) -> List[MetricModel]:
        return self.db.query(MetricModel).filter(MetricModel.run_id == run_id).all()


class ArtifactRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_run(self, run_id: str) -> List[ArtifactModel]:
        return self.db.query(ArtifactModel).filter(ArtifactModel.run_id == run_id).all()
