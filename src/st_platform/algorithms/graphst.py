from __future__ import annotations

import contextlib
import io
import json
import random
import warnings
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from st_platform.algorithms.base import Algorithm, AlgorithmOutput, AlgorithmSpec
from st_platform.algorithms.spagcn_lite import (
    _as_2d_array,
    _build_assignment_payload,
    _nearest_neighbors,
    _neighbor_agreement,
    _require_asset,
)
from st_platform.data import SpatialDataBundle
from st_platform.tasks import TaskType


class GraphSTDomainAlgorithm(Algorithm):
    spec = AlgorithmSpec(
        algorithm_id="graphst",
        name="GraphST Domain Detection",
        task_type=TaskType.DOMAIN_DETECTION,
        runtime="python",
        version="1.1.1",
        description=(
            "Runs the local GraphST package to learn spatial representations, then "
            "clusters them into spatial domains."
        ),
        tags=("classic", "graphst", "domain", "representation"),
    )

    def run(
        self,
        data: SpatialDataBundle,
        parameters: Mapping[str, Any],
        context: Mapping[str, Any],
    ) -> AlgorithmOutput:
        backend = _load_backend()
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

        random_state = int(parameters.get("random_state", 0))
        _seed_backend(random_state, backend.torch)

        epochs = int(parameters.get("epochs", 2))
        dim_output = int(parameters.get("dim_output", 4))
        neighbor_k = int(parameters.get("neighbor_k", 3))
        neighbor_k = max(1, min(neighbor_k, n_spots - 1))
        xy = coordinates[:, :2].astype(float)

        spot_ids = _metadata_names(counts_asset.metadata.get("spot_ids"), n_spots, "spot")
        gene_names = _metadata_names(counts_asset.metadata.get("gene_names"), n_genes, "gene")
        adata = backend.AnnData(matrix.astype(float))
        adata.obs_names = spot_ids
        adata.var_names = gene_names
        adata.obsm["spatial"] = xy
        adata.var["highly_variable"] = True

        with warnings.catch_warnings(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
            io.StringIO()
        ):
            warnings.simplefilter("ignore")
            model = backend.GraphST(
                adata,
                device="cpu",
                epochs=epochs,
                random_seed=random_state,
                dim_output=dim_output,
            )
            output = model.train()
            embedding = np.asarray(output.obsm["emb"], dtype=float)

        kmeans = backend.KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            n_init=10,
        )
        labels = kmeans.fit_predict(embedding)
        neighbors = _nearest_neighbors(_zscore(xy), neighbor_k)

        assignments = _build_assignment_payload(
            spot_ids=spot_ids,
            coordinates=xy,
            labels=labels,
            gene_names=gene_names,
            algorithm_id=self.spec.algorithm_id,
            parameters={
                "n_clusters": n_clusters,
                "neighbor_k": neighbor_k,
                "epochs": epochs,
                "dim_output": dim_output,
                "random_state": random_state,
            },
        )
        output_path = Path(str(context["run_root"])) / "graphst-domains.json"
        output_path.write_text(json.dumps(assignments, indent=2), encoding="utf-8")

        domain_counts = Counter(int(label) for label in labels)
        return AlgorithmOutput(
            summary={
                "message": "GraphST domain detection completed.",
                "backend": "GraphST",
                "dataset": data.summary(),
                "predicted_domains": len(domain_counts),
                "domain_counts": {str(k): v for k, v in sorted(domain_counts.items())},
                "embedding_shape": list(embedding.shape),
            },
            artifacts=[
                {
                    "kind": "domain_assignments",
                    "name": output_path.name,
                    "uri": str(output_path),
                    "description": "Per-spot GraphST spatial domain assignments.",
                }
            ],
            metrics={
                "spot_count": float(n_spots),
                "gene_count": float(n_genes),
                "spatial_neighbor_agreement": _neighbor_agreement(labels, neighbors),
                "kmeans_inertia": float(kmeans.inertia_),
            },
        )


class _Backend:
    def __init__(self, AnnData: Any, GraphST: Any, KMeans: Any, torch: Any) -> None:
        self.AnnData = AnnData
        self.GraphST = GraphST
        self.KMeans = KMeans
        self.torch = torch


def _load_backend() -> _Backend:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from anndata import AnnData
            from GraphST.GraphST import GraphST
            from sklearn.cluster import KMeans
            import torch
    except ImportError as exc:
        raise RuntimeError(
            "GraphST is not installed. Install it into the uv environment with "
            "`uv pip install --python .venv-spagcn/bin/python -e ../GraphST pot`."
        ) from exc
    return _Backend(AnnData=AnnData, GraphST=GraphST, KMeans=KMeans, torch=torch)


def _seed_backend(random_state: int, torch_module: Any) -> None:
    random.seed(random_state)
    np.random.seed(random_state)
    torch_module.manual_seed(random_state)


def _metadata_names(value: Any, expected_length: int, prefix: str) -> list[str]:
    if value is None:
        return [f"{prefix}_{idx + 1}" for idx in range(expected_length)]
    names = [str(item) for item in value]
    if len(names) != expected_length:
        raise ValueError(f"{prefix} names must contain {expected_length} entries.")
    return names


def _zscore(values: np.ndarray) -> np.ndarray:
    mean = values.mean(axis=0, keepdims=True)
    std = values.std(axis=0, keepdims=True)
    std[std == 0] = 1.0
    return (values - mean) / std
