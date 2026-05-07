from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional
from uuid import uuid4

from st_platform.core.registry import AlgorithmRegistry
from st_platform.data import SpatialDataBundle
from st_platform.tasks import TaskType


class RunStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class RunResult:
    run_id: str
    task_type: str
    algorithm_id: str
    status: RunStatus
    created_at: str
    started_at: str
    finished_at: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dataset: Dict[str, Any] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    run_root: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload


class LocalRunner:
    def __init__(self, registry: AlgorithmRegistry, working_directory: Path) -> None:
        self.registry = registry
        self.working_directory = Path(working_directory)
        self.working_directory.mkdir(parents=True, exist_ok=True)

    def execute(
        self,
        task_type: TaskType,
        algorithm_id: str,
        data: SpatialDataBundle,
        parameters: Optional[Mapping[str, Any]] = None,
    ) -> RunResult:
        created_at = self._now()
        started_at = created_at
        run_id = uuid4().hex[:12]
        run_root = self.working_directory / run_id
        run_root.mkdir(parents=True, exist_ok=True)
        params = dict(parameters or {})
        algorithm = self.registry.get(algorithm_id)

        if algorithm.spec.task_type != task_type:
            finished_at = self._now()
            return RunResult(
                run_id=run_id,
                task_type=task_type.value,
                algorithm_id=algorithm_id,
                status=RunStatus.FAILED,
                created_at=created_at,
                started_at=started_at,
                finished_at=finished_at,
                parameters=params,
                dataset=data.summary(),
                run_root=str(run_root),
                error=(
                    f"Algorithm '{algorithm_id}' is registered for "
                    f"'{algorithm.spec.task_type.value}', not '{task_type.value}'."
                ),
            )

        context = {
            "run_id": run_id,
            "run_root": str(run_root),
            "created_at": created_at,
        }

        try:
            output = algorithm.run(data=data, parameters=params, context=context)
        except Exception as exc:
            finished_at = self._now()
            return RunResult(
                run_id=run_id,
                task_type=task_type.value,
                algorithm_id=algorithm_id,
                status=RunStatus.FAILED,
                created_at=created_at,
                started_at=started_at,
                finished_at=finished_at,
                parameters=params,
                dataset=data.summary(),
                run_root=str(run_root),
                error=str(exc),
            )

        finished_at = self._now()
        return RunResult(
            run_id=run_id,
            task_type=task_type.value,
            algorithm_id=algorithm_id,
            status=RunStatus.SUCCEEDED,
            created_at=created_at,
            started_at=started_at,
            finished_at=finished_at,
            parameters=params,
            dataset=data.summary(),
            summary=output.summary,
            artifacts=output.artifacts,
            metrics=output.metrics,
            warnings=output.warnings,
            run_root=str(run_root),
        )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

