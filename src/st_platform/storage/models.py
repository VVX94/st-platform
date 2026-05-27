from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from st_platform.storage.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return uuid.uuid4().hex


class DatasetModel(Base):
    __tablename__ = "datasets"

    dataset_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_new_id)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    platform: Mapped[str] = mapped_column(String(64), nullable=False, default="visium")
    sample_id: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    uri: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    experiments: Mapped[list["ExperimentModel"]] = relationship(back_populates="dataset")


class ExperimentModel(Base):
    __tablename__ = "experiments"

    experiment_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_new_id)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    task_type: Mapped[str] = mapped_column(String(64), nullable=False)
    dataset_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("datasets.dataset_id"), nullable=True
    )
    parameters_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="created")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    dataset: Mapped[DatasetModel | None] = relationship(back_populates="experiments")
    runs: Mapped[list["RunModel"]] = relationship(back_populates="experiment")


class RunModel(Base):
    __tablename__ = "runs"

    run_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_new_id)
    experiment_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("experiments.experiment_id"), nullable=True
    )
    algorithm_id: Mapped[str] = mapped_column(String(128), nullable=False)
    task_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    parameters_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    dataset_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    summary_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    run_root: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    experiment: Mapped[ExperimentModel | None] = relationship(back_populates="runs")
    metrics: Mapped[list["MetricModel"]] = relationship(back_populates="run")
    artifacts: Mapped[list["ArtifactModel"]] = relationship(back_populates="run")


class MetricModel(Base):
    __tablename__ = "metrics"

    metric_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_new_id)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("runs.run_id"), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    run: Mapped[RunModel] = relationship(back_populates="metrics")


class ArtifactModel(Base):
    __tablename__ = "artifacts"

    artifact_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_new_id)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("runs.run_id"), nullable=False)
    kind: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    uri: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    run: Mapped[RunModel] = relationship(back_populates="artifacts")
