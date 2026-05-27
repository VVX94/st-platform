"""Pydantic request/response schemas for the API."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------- Health ----------

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"


# ---------- Algorithm ----------

class AlgorithmOut(BaseModel):
    algorithm_id: str
    name: str
    task_type: str
    runtime: str
    version: str
    description: str
    tags: List[str] = []


# ---------- Dataset ----------

class DatasetCreate(BaseModel):
    name: str
    platform: str = "visium"
    sample_id: str = ""
    uri: Optional[str] = None
    description: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DatasetRegisterReal(BaseModel):
    name: str
    path: str  # local h5ad file path
    spatial_key: str = "spatial"
    label_column: Optional[str] = None
    description: str = ""


class DatasetOut(BaseModel):
    dataset_id: str
    name: str
    platform: str
    sample_id: str
    uri: Optional[str] = None
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


# ---------- Experiment ----------

class ExperimentCreate(BaseModel):
    name: str
    task_type: str
    algorithm_ids: List[str] = Field(default_factory=list)
    dataset_id: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ExperimentOut(BaseModel):
    experiment_id: str
    name: str
    task_type: str
    dataset_id: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    status: str = "created"
    run_count: int = 0
    created_at: Optional[datetime] = None


# ---------- Run ----------

class RunOut(BaseModel):
    run_id: str
    experiment_id: Optional[str] = None
    algorithm_id: str
    task_type: str
    status: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dataset: Dict[str, Any] = Field(default_factory=dict)
    summary: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, float] = Field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    error: Optional[str] = None
    run_root: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


# ---------- Metric ----------

class MetricOut(BaseModel):
    metric_id: str
    run_id: str
    name: str
    value: float
    created_at: Optional[datetime] = None


# ---------- Artifact ----------

class ArtifactOut(BaseModel):
    artifact_id: str
    run_id: str
    kind: str
    uri: str
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


# ---------- Worker ----------

class ExperimentReportOut(BaseModel):
    experiment_id: str
    name: str
    status: str
    task_type: str = ""
    runs: List[RunOut] = Field(default_factory=list)
    metrics_summary: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[ArtifactOut] = Field(default_factory=list)


class WorkerPollResponse(BaseModel):
    processed: int
