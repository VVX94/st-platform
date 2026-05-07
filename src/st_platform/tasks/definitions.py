from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, Tuple


class TaskType(str, Enum):
    DATA_INGEST = "data_ingest"
    QUALITY_CONTROL = "quality_control"
    DOMAIN_DETECTION = "domain_detection"
    DECONVOLUTION = "deconvolution"
    CROSS_MODAL_MAPPING = "cross_modal_mapping"
    VISUALIZATION = "visualization"


@dataclass
class TaskDefinition:
    task_type: TaskType
    title: str
    description: str
    required_assets: Tuple[str, ...] = ()
    default_parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_type": self.task_type.value,
            "title": self.title,
            "description": self.description,
            "required_assets": list(self.required_assets),
            "default_parameters": dict(self.default_parameters),
        }


def build_default_tasks() -> Iterable[TaskDefinition]:
    return [
        TaskDefinition(
            task_type=TaskType.DATA_INGEST,
            title="Data Ingest",
            description="Normalize input metadata and convert source files into the platform bundle.",
            required_assets=("counts_table", "spatial_coordinates"),
        ),
        TaskDefinition(
            task_type=TaskType.QUALITY_CONTROL,
            title="Quality Control",
            description="Validate spot or cell coverage, metadata completeness, and baseline QC metrics.",
            required_assets=("counts_table", "spatial_coordinates"),
            default_parameters={"min_features": 200, "max_mito_ratio": 0.2},
        ),
        TaskDefinition(
            task_type=TaskType.DOMAIN_DETECTION,
            title="Domain Detection",
            description="Infer spatial domains or niches from expression and coordinates.",
            required_assets=("counts_table", "spatial_coordinates"),
            default_parameters={"resolution": 0.8},
        ),
        TaskDefinition(
            task_type=TaskType.DECONVOLUTION,
            title="Deconvolution",
            description="Estimate cell type composition in each spot or region.",
            required_assets=("counts_table", "reference_signatures"),
            default_parameters={"normalize": True},
        ),
        TaskDefinition(
            task_type=TaskType.CROSS_MODAL_MAPPING,
            title="Cross-modal Mapping",
            description="Map single-cell references onto spatial coordinates.",
            required_assets=("counts_table", "reference_cells", "spatial_coordinates"),
            default_parameters={"top_k": 20},
        ),
    ]

