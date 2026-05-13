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


class SpaGCNDomainAlgorithm(Algorithm):
    spec = AlgorithmSpec(
        algorithm_id="spagcn",
        name="SpaGCN Domain Detection",
        task_type=TaskType.DOMAIN_DETECTION,
        runtime="python",
        version="1.2.7",
        description=(
            "Runs the local SpaGCN package for spatial domain detection using "
            "expression counts and spatial coordinates."
        ),
        tags=("classic", "spagcn", "domain", "gcn"),
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

        xy = coordinates[:, :2].astype(float)
        num_pcs = int(parameters.get("num_pcs", min(50, n_spots, n_genes)))
        num_pcs = max(1, min(num_pcs, n_spots, n_genes))
        neighbor_k = int(parameters.get("neighbor_k", 6))
        neighbor_k = max(1, min(neighbor_k, n_spots - 1))
        l_value = float(parameters.get("l", 1.0))
        max_epochs = int(parameters.get("max_epochs", 20))
        learning_rate = float(parameters.get("lr", 0.01))
        tolerance = float(parameters.get("tol", 1e-3))

        adata = backend.AnnData(matrix.astype(float))
        adata.obs_names = _metadata_names(counts_asset.metadata.get("spot_ids"), n_spots, "spot")
        adata.var_names = _metadata_names(counts_asset.metadata.get("gene_names"), n_genes, "gene")

        with contextlib.redirect_stdout(io.StringIO()):
            adjacency = backend.calculate_adj_matrix(
                x=xy[:, 0].tolist(),
                y=xy[:, 1].tolist(),
                histology=False,
            )
            model = backend.SpaGCN()
            model.set_l(l_value)
            model.train(
                adata,
                adjacency,
                num_pcs=num_pcs,
                lr=learning_rate,
                max_epochs=max_epochs,
                init="kmeans",
                n_clusters=n_clusters,
                tol=tolerance,
            )
            labels, probabilities = model.predict()

        labels = np.asarray(labels, dtype=int)
        probabilities = np.asarray(probabilities, dtype=float)
        neighbors = _nearest_neighbors(_zscore(xy), neighbor_k)

        assignments = _build_assignment_payload(
            spot_ids=adata.obs_names.tolist(),
            coordinates=xy,
            labels=labels,
            gene_names=adata.var_names.tolist(),
            algorithm_id=self.spec.algorithm_id,
            parameters={
                "n_clusters": n_clusters,
                "neighbor_k": neighbor_k,
                "num_pcs": num_pcs,
                "l": l_value,
                "max_epochs": max_epochs,
                "lr": learning_rate,
                "tol": tolerance,
                "random_state": random_state,
            },
        )
        for index, probability in enumerate(probabilities):
            assignments["domains"][index]["max_probability"] = float(np.max(probability))

        output_path = Path(str(context["run_root"])) / "spagcn-domains.json"
        output_path.write_text(json.dumps(assignments, indent=2), encoding="utf-8")

        domain_counts = Counter(int(label) for label in labels)
        return AlgorithmOutput(
            summary={
                "message": "SpaGCN domain detection completed.",
                "backend": "SpaGCN",
                "dataset": data.summary(),
                "predicted_domains": len(domain_counts),
                "domain_counts": {str(k): v for k, v in sorted(domain_counts.items())},
                "num_pcs": num_pcs,
                "l": l_value,
            },
            artifacts=[
                {
                    "kind": "domain_assignments",
                    "name": output_path.name,
                    "uri": str(output_path),
                    "description": "Per-spot SpaGCN spatial domain assignments.",
                }
            ],
            metrics={
                "spot_count": float(n_spots),
                "gene_count": float(n_genes),
                "spatial_neighbor_agreement": _neighbor_agreement(labels, neighbors),
                "mean_max_probability": float(np.mean(np.max(probabilities, axis=1))),
            },
        )


class _Backend:
    def __init__(self, AnnData: Any, SpaGCN: Any, calculate_adj_matrix: Any, torch: Any) -> None:
        self.AnnData = AnnData
        self.SpaGCN = SpaGCN
        self.calculate_adj_matrix = calculate_adj_matrix
        self.torch = torch


def _load_backend() -> _Backend:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from anndata import AnnData
            from SpaGCN import SpaGCN, calculate_adj_matrix
            import torch
    except ImportError as exc:
        raise RuntimeError(
            "SpaGCN is not installed. Create the uv environment with "
            "`uv pip install --python .venv-spagcn/bin/python -e . "
            "-e ../SpaGCN/SpaGCN_package`."
        ) from exc
    return _Backend(
        AnnData=AnnData,
        SpaGCN=SpaGCN,
        calculate_adj_matrix=calculate_adj_matrix,
        torch=torch,
    )


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
