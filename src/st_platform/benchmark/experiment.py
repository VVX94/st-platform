from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExperimentSpec:
    """Describes an experiment: which task, which algorithms, which dataset."""

    name: str
    task_type: str
    algorithm_ids: List[str] = field(default_factory=list)
    dataset_id: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


def split_experiment_to_runs(
    experiment: ExperimentSpec,
) -> List[Dict[str, Any]]:
    """Break an experiment into one run spec per algorithm."""
    runs: List[Dict[str, Any]] = []
    for algo_id in experiment.algorithm_ids:
        runs.append(
            {
                "algorithm_id": algo_id,
                "task_type": experiment.task_type,
                "dataset_id": experiment.dataset_id,
                "parameters": dict(experiment.parameters),
            }
        )
    return runs
