from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class DatasetRef:
    dataset_id: str
    platform: str
    sample_id: str
    uri: Optional[str] = None


@dataclass
class DataAsset:
    kind: str
    key: str
    description: str
    uri: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpatialDataBundle:
    dataset: DatasetRef
    coordinate_key: str = "spatial"
    table_name: str = "table"
    modality: str = "spatial_transcriptomics"
    assets: List[DataAsset] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> Dict[str, Any]:
        return {
            "dataset_id": self.dataset.dataset_id,
            "platform": self.dataset.platform,
            "sample_id": self.dataset.sample_id,
            "modality": self.modality,
            "coordinate_key": self.coordinate_key,
            "table_name": self.table_name,
            "asset_count": len(self.assets),
            "metadata_keys": sorted(self.metadata.keys()),
        }

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

