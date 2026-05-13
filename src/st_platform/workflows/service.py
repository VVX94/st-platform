from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from st_platform.algorithms import build_builtin_algorithms
from st_platform.core import AlgorithmRegistry, LocalRunner, TaskCatalog
from st_platform.data import DataAsset, DatasetRef, SpatialDataBundle
from st_platform.tasks import TaskType, build_default_tasks


@dataclass
class PlatformService:
    task_catalog: TaskCatalog
    algorithm_registry: AlgorithmRegistry
    runner: LocalRunner

    def list_tasks(self) -> Iterable[Dict[str, Any]]:
        return [task.to_dict() for task in self.task_catalog.list()]

    def list_algorithms(self, task_type: Optional[TaskType] = None) -> Iterable[Dict[str, Any]]:
        if task_type is None:
            algorithms = self.algorithm_registry.list()
        else:
            algorithms = self.algorithm_registry.list_for_task(task_type)
        return [algorithm.spec.to_dict() for algorithm in algorithms]

    def run(
        self,
        task_type: TaskType,
        algorithm_id: str,
        data: SpatialDataBundle,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        return self.runner.execute(
            task_type=task_type,
            algorithm_id=algorithm_id,
            data=data,
            parameters=parameters,
        )

    def build_demo_dataset(self, platform: str = "visium") -> SpatialDataBundle:
        return SpatialDataBundle(
            dataset=DatasetRef(
                dataset_id="demo-visium-001",
                platform=platform,
                sample_id="sample-a",
                uri="memory://demo-visium-001",
            ),
            assets=[
                DataAsset(
                    kind="counts_table",
                    key="counts",
                    description="Small in-memory counts matrix for demo algorithm execution.",
                    metadata={
                        "spot_ids": [
                            "spot_a1",
                            "spot_a2",
                            "spot_a3",
                            "spot_b1",
                            "spot_b2",
                            "spot_b3",
                            "spot_c1",
                            "spot_c2",
                            "spot_c3",
                        ],
                        "gene_names": ["EPCAM", "KRT8", "COL1A1", "LYZ", "MS4A1"],
                        "matrix": [
                            [9, 8, 1, 0, 0],
                            [8, 9, 1, 0, 0],
                            [9, 7, 0, 1, 0],
                            [0, 1, 9, 8, 1],
                            [1, 0, 8, 9, 1],
                            [0, 1, 9, 7, 2],
                            [1, 0, 0, 1, 9],
                            [0, 1, 1, 0, 8],
                            [1, 0, 0, 2, 9],
                        ],
                    },
                ),
                DataAsset(
                    kind="spatial_coordinates",
                    key="coordinates",
                    description="Small in-memory spatial coordinate matrix for demo execution.",
                    metadata={
                        "columns": ["x", "y"],
                        "coordinates": [
                            [0.0, 0.0],
                            [0.0, 1.0],
                            [1.0, 0.0],
                            [5.0, 5.0],
                            [5.0, 6.0],
                            [6.0, 5.0],
                            [10.0, 0.0],
                            [10.0, 1.0],
                            [11.0, 0.0],
                        ],
                    },
                ),
                DataAsset(
                    kind="reference_signatures",
                    key="reference",
                    description="Mock cell type signature placeholder.",
                ),
            ],
            metadata={
                "platform_version": "demo",
                "organism": "human",
                "spot_count": 9,
                "gene_count": 5,
            },
        )


def create_platform_service(project_root: Optional[str] = None) -> PlatformService:
    base_dir = Path(project_root or Path.cwd())
    task_catalog = TaskCatalog(build_default_tasks())
    algorithm_registry = AlgorithmRegistry(build_builtin_algorithms())
    runner = LocalRunner(algorithm_registry, base_dir / "runs")
    return PlatformService(
        task_catalog=task_catalog,
        algorithm_registry=algorithm_registry,
        runner=runner,
    )

