from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

import numpy as np
from sklearn.cluster import KMeans

from st_platform.algorithms.base import Algorithm, AlgorithmOutput, AlgorithmSpec
from st_platform.data import DataAsset, SpatialDataBundle
from st_platform.tasks import TaskType


class SpaGCNLiteDomainAlgorithm(Algorithm):
    spec = AlgorithmSpec(
        algorithm_id="spagcn-lite",
        name="SpaGCN Lite Domain Detection",
        task_type=TaskType.DOMAIN_DETECTION,
        runtime="python",
        version="0.1.0",
        description=(
            "A dependency-light SpaGCN adapter that combines expression features, "
            "spatial coordinates, and neighborhood refinement for MVP domain detection."
        ),
        tags=("classic", "spagcn", "domain", "lightweight"),
    )

    def run(
        self,
        data: SpatialDataBundle,
        parameters: Mapping[str, Any],
        context: Mapping[str, Any],
    ) -> AlgorithmOutput:
        counts_asset = _require_asset(data, "counts_table")
        coordinates_asset = _require_asset(data, "spatial_coordinates")

        matrix = _as_2d_array(
            counts_asset.metadata.get("matrix"),
            "counts_table.metadata['matrix']",
        )
        coordinates = _as_2d_array(
            coordinates_asset.metadata.get("coordinates"),
            "spatial_coordinates.metadata['coordinates']",
        )
        if coordinates.shape[1] < 2:
            raise ValueError("spatial coordinates must include at least x and y columns.")
        if matrix.shape[0] != coordinates.shape[0]:
            raise ValueError(
                "counts matrix and spatial coordinates must describe the same number of spots."
            )

        n_spots, n_genes = matrix.shape
        n_clusters = int(parameters.get("n_clusters", 3))
        if not 2 <= n_clusters <= n_spots:
            raise ValueError("n_clusters must be between 2 and the number of spots.")

        neighbor_k = int(parameters.get("neighbor_k", 6))
        neighbor_k = max(1, min(neighbor_k, n_spots - 1))
        spatial_weight = float(parameters.get("spatial_weight", 0.25))
        random_state = int(parameters.get("random_state", 0))
        should_refine = bool(parameters.get("refine", True))

        expression = _zscore(np.log1p(np.clip(matrix, a_min=0, a_max=None)))
        xy = coordinates[:, :2].astype(float)
        xy_scaled = _zscore(xy)
        features = np.concatenate([expression, xy_scaled * spatial_weight], axis=1)

        labels = KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            n_init=10,
        ).fit_predict(features)
        neighbors = _nearest_neighbors(xy_scaled, neighbor_k)
        refined_labels = _refine_labels(labels, neighbors) if should_refine else labels
        refinement_changes = int(np.sum(labels != refined_labels))

        spot_ids = counts_asset.metadata.get("spot_ids")
        if spot_ids is None:
            spot_ids = [f"spot_{idx + 1}" for idx in range(n_spots)]
        gene_names = counts_asset.metadata.get("gene_names")
        if gene_names is None:
            gene_names = [f"gene_{idx + 1}" for idx in range(n_genes)]

        assignments = _build_assignment_payload(
            spot_ids=spot_ids,
            coordinates=xy,
            labels=refined_labels,
            gene_names=gene_names,
            algorithm_id=self.spec.algorithm_id,
            parameters={
                "n_clusters": n_clusters,
                "neighbor_k": neighbor_k,
                "spatial_weight": spatial_weight,
                "random_state": random_state,
                "refine": should_refine,
            },
        )
        output_path = Path(str(context["run_root"])) / "spagcn-lite-domains.json"
        output_path.write_text(json.dumps(assignments, indent=2), encoding="utf-8")

        domain_counts = Counter(int(label) for label in refined_labels)
        return AlgorithmOutput(
            summary={
                "message": "SpaGCN-lite domain detection completed.",
                "dataset": data.summary(),
                "predicted_domains": len(domain_counts),
                "domain_counts": {str(k): v for k, v in sorted(domain_counts.items())},
                "refinement_changes": refinement_changes,
            },
            artifacts=[
                {
                    "kind": "domain_assignments",
                    "name": output_path.name,
                    "uri": str(output_path),
                    "description": "Per-spot SpaGCN-lite spatial domain assignments.",
                }
            ],
            metrics={
                "spot_count": float(n_spots),
                "gene_count": float(n_genes),
                "spatial_neighbor_agreement": _neighbor_agreement(refined_labels, neighbors),
                "refinement_changes": float(refinement_changes),
            },
        )


def _require_asset(data: SpatialDataBundle, kind: str) -> DataAsset:
    for asset in data.assets:
        if asset.kind == kind:
            return asset
    raise ValueError(f"Missing required asset kind: {kind}.")


def _as_2d_array(value: Any, label: str) -> np.ndarray:
    if value is None:
        raise ValueError(f"Missing required payload: {label}.")
    array = np.asarray(value, dtype=float)
    if array.ndim != 2 or array.shape[0] == 0 or array.shape[1] == 0:
        raise ValueError(f"{label} must be a non-empty 2D array.")
    return array


def _zscore(values: np.ndarray) -> np.ndarray:
    mean = values.mean(axis=0, keepdims=True)
    std = values.std(axis=0, keepdims=True)
    std[std == 0] = 1.0
    return (values - mean) / std


def _nearest_neighbors(coordinates: np.ndarray, neighbor_k: int) -> np.ndarray:
    deltas = coordinates[:, None, :] - coordinates[None, :, :]
    distances = np.sqrt(np.sum(deltas * deltas, axis=2))
    return np.argsort(distances, axis=1)[:, 1 : neighbor_k + 1]


def _refine_labels(labels: np.ndarray, neighbors: np.ndarray) -> np.ndarray:
    refined = labels.copy()
    for index, neighbor_indices in enumerate(neighbors):
        votes = Counter(int(labels[neighbor]) for neighbor in neighbor_indices)
        winner, count = votes.most_common(1)[0]
        if count > len(neighbor_indices) / 2:
            refined[index] = winner
    return refined


def _neighbor_agreement(labels: np.ndarray, neighbors: np.ndarray) -> float:
    total = int(neighbors.size)
    if total == 0:
        return 0.0
    matches = 0
    for index, neighbor_indices in enumerate(neighbors):
        matches += int(np.sum(labels[neighbor_indices] == labels[index]))
    return matches / total


def _build_assignment_payload(
    spot_ids: Sequence[str],
    coordinates: np.ndarray,
    labels: np.ndarray,
    gene_names: Sequence[str],
    algorithm_id: str,
    parameters: Dict[str, Any],
) -> Dict[str, Any]:
    domains: List[Dict[str, Any]] = []
    for index, spot_id in enumerate(spot_ids):
        domains.append(
            {
                "spot_id": str(spot_id),
                "domain": int(labels[index]),
                "x": float(coordinates[index, 0]),
                "y": float(coordinates[index, 1]),
            }
        )
    return {
        "algorithm_id": algorithm_id,
        "parameters": parameters,
        "spot_count": len(domains),
        "gene_count": len(gene_names),
        "domains": domains,
    }
