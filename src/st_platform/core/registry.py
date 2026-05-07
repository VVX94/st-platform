from __future__ import annotations

from typing import Dict, Iterable, List

from st_platform.algorithms import Algorithm
from st_platform.tasks import TaskDefinition, TaskType


class TaskCatalog:
    def __init__(self, tasks: Iterable[TaskDefinition] = ()) -> None:
        self._tasks: Dict[TaskType, TaskDefinition] = {}
        for task in tasks:
            self.register(task)

    def register(self, task: TaskDefinition) -> None:
        self._tasks[task.task_type] = task

    def get(self, task_type: TaskType) -> TaskDefinition:
        return self._tasks[task_type]

    def list(self) -> List[TaskDefinition]:
        return list(self._tasks.values())


class AlgorithmRegistry:
    def __init__(self, algorithms: Iterable[Algorithm] = ()) -> None:
        self._algorithms: Dict[str, Algorithm] = {}
        for algorithm in algorithms:
            self.register(algorithm)

    def register(self, algorithm: Algorithm) -> None:
        self._algorithms[algorithm.spec.algorithm_id] = algorithm

    def get(self, algorithm_id: str) -> Algorithm:
        return self._algorithms[algorithm_id]

    def list(self) -> List[Algorithm]:
        return list(self._algorithms.values())

    def list_for_task(self, task_type: TaskType) -> List[Algorithm]:
        return [
            algorithm
            for algorithm in self._algorithms.values()
            if algorithm.spec.task_type == task_type
        ]

