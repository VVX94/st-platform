from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from st_platform.algorithms.base import Algorithm, AlgorithmOutput, AlgorithmSpec
from st_platform.algorithms.spagcn_lite import (
    _as_2d_array,
    _build_assignment_payload,
    _nearest_neighbors,
    _neighbor_agreement,
    _refine_labels,
    _require_asset,
    _zscore,
)
from st_platform.data import SpatialDataBundle
from st_platform.tasks import TaskType


class SpaceFlowLiteDomainAlgorithm(Algorithm):
    spec = AlgorithmSpec(
        algorithm_id="spaceflow-lite",
        name="SpaceFlow Lite Domain Detection",
        task_type=TaskType.DOMAIN_DETECTION,
        runtime="python",
        version="0.1.0",
        description=(
            "A dependency-light SpaceFlow adapter using PCA embeddings with "
            "spatial-aware clustering for domain detection."
        ),
        tags=("classic", "spaceflow", "domain", "lightweight"),
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

        n_components_default = min(50, n_spots - 1, n_genes)
        n_components = int(parameters.get("n_components", n_components_default))
        neighbor_k = int(parameters.get("neighbor_k", 6))
        neighbor_k = max(1, min(neighbor_k, n_spots - 1))
        spatial_weight = float(parameters.get("spatial_weight", 0.2))
        random_state = int(parameters.get("random_state", 0))
        n_top_genes = parameters.get("n_top_genes", None)
        if n_top_genes is not None:
            n_top_genes = int(n_top_genes)

        expression = np.log1p(np.clip(matrix, a_min=0, a_max=None))

        if n_top_genes is not None and n_top_genes < n_genes:
            gene_vars = np.var(expression, axis=0)
            top_indices = np.argsort(gene_vars)[-n_top_genes:]
            expression = expression[:, top_indices]

        expression = _zscore(expression)
        n_components = min(n_components, expression.shape[1], n_spots - 1)
        xy = coordinates[:, :2].astype(float)
        xy_scaled = _zscore(xy)

        pca = PCA(n_components=n_components, random_state=random_state)
        embedding = pca.fit_transform(expression)

        features = np.concatenate([embedding, xy_scaled * spatial_weight], axis=1)

        labels = KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            n_init=10,
        ).fit_predict(features)

        neighbors = _nearest_neighbors(xy_scaled, neighbor_k)
        refined_labels = _refine_labels(labels, neighbors)
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
                "n_components": n_components,
                "neighbor_k": neighbor_k,
                "spatial_weight": spatial_weight,
                "random_state": random_state,
                "n_top_genes": n_top_genes,
            },
        )
        output_path = Path(str(context["run_root"])) / "spaceflow-lite-domains.json"
        output_path.write_text(json.dumps(assignments, indent=2), encoding="utf-8")

        domain_counts = Counter(int(label) for label in refined_labels)
        return AlgorithmOutput(
            summary={
                "message": "SpaceFlow-lite domain detection completed.",
                "dataset": data.summary(),
                "predicted_domains": len(domain_counts),
                "domain_counts": {str(k): v for k, v in sorted(domain_counts.items())},
                "refinement_changes": refinement_changes,
                "explained_variance_ratio": float(pca.explained_variance_ratio_.sum()),
            },
            artifacts=[
                {
                    "kind": "domain_assignments",
                    "name": output_path.name,
                    "uri": str(output_path),
                    "description": "Per-spot SpaceFlow-lite spatial domain assignments.",
                }
            ],
            metrics={
                "spot_count": float(n_spots),
                "gene_count": float(n_genes),
                "spatial_neighbor_agreement": _neighbor_agreement(refined_labels, neighbors),
                "refinement_changes": float(refinement_changes),
                "pca_explained_variance": float(pca.explained_variance_ratio_.sum()),
            },
        )
