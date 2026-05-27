from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Tuple

from st_platform.data import SpatialDataBundle
from st_platform.tasks import TaskType


@dataclass(frozen=True)
class AlgorithmSpec:
    algorithm_id: str
    name: str
    task_type: TaskType
    runtime: str
    version: str
    description: str
    tags: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm_id": self.algorithm_id,
            "name": self.name,
            "task_type": self.task_type.value,
            "runtime": self.runtime,
            "version": self.version,
            "description": self.description,
            "tags": list(self.tags),
        }


@dataclass
class AlgorithmOutput:
    summary: Dict[str, Any]
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


class Algorithm(ABC):
    spec: AlgorithmSpec

    def is_available(self) -> bool:
        """Return True if this algorithm's dependencies are installed."""
        return True

    @abstractmethod
    def run(
        self,
        data: SpatialDataBundle,
        parameters: Mapping[str, Any],
        context: Mapping[str, Any],
    ) -> AlgorithmOutput:
        raise NotImplementedError

