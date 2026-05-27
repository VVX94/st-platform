from __future__ import annotations

import contextlib
import io
import json
import random
import sys
import warnings
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
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


class CCSTDomainAlgorithm(Algorithm):
    spec = AlgorithmSpec(
        algorithm_id="ccst",
        name="CCST Domain Detection",
        task_type=TaskType.DOMAIN_DETECTION,
        runtime="python",
        version="benchmarkst",
        description=(
            "Runs the local CCST DGI encoder and clusters learned spatial graph "
            "representations into domains."
        ),
        tags=("classic", "ccst", "domain", "dgi"),
    )

    def is_available(self) -> bool:
        try:
            import torch_geometric  # noqa: F401
            return True
        except ImportError:
            return False

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
        hidden = int(parameters.get("hidden", 4))
        neighbor_k = int(parameters.get("neighbor_k", 3))
        neighbor_k = max(1, min(neighbor_k, n_spots - 1))
        xy = coordinates[:, :2].astype(float)
        features = np.log1p(np.clip(matrix, a_min=0, a_max=None))

        adjacency = backend.kneighbors_graph(
            xy,
            n_neighbors=neighbor_k,
            mode="connectivity",
            include_self=False,
        )
        adjacency = ((adjacency + adjacency.T) > 0).astype(float).tocsr()

        with warnings.catch_warnings(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
            io.StringIO()
        ):
            warnings.simplefilter("ignore")
            graph_bags = backend.get_graph(adjacency, features)
            loader = backend.DataLoader(graph_bags, batch_size=1)
            args = SimpleNamespace(
                gpu_id=0,
                hidden=hidden,
                load=False,
                model_path=f"{context['run_root']}/",
                lambda_I=0.3,
                num_epoch=epochs,
            )
            model = backend.train_DGI(args, loader, features.shape[1])
            device = next(model.parameters()).device
            graph = graph_bags[0].to(device)
            model.eval()
            embedding = model.encoder(graph).detach().cpu().numpy()

        kmeans = backend.KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            n_init=10,
        )
        labels = kmeans.fit_predict(embedding)
        neighbors = _nearest_neighbors(_zscore(xy), neighbor_k)

        spot_ids = _metadata_names(counts_asset.metadata.get("spot_ids"), n_spots, "spot")
        gene_names = _metadata_names(counts_asset.metadata.get("gene_names"), n_genes, "gene")
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
                "hidden": hidden,
                "random_state": random_state,
            },
        )
        output_path = Path(str(context["run_root"])) / "ccst-domains.json"
        output_path.write_text(json.dumps(assignments, indent=2), encoding="utf-8")

        domain_counts = Counter(int(label) for label in labels)
        return AlgorithmOutput(
            summary={
                "message": "CCST domain detection completed.",
                "backend": "CCST",
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
                    "description": "Per-spot CCST spatial domain assignments.",
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
    def __init__(
        self,
        DataLoader: Any,
        KMeans: Any,
        get_graph: Any,
        kneighbors_graph: Any,
        torch: Any,
        train_DGI: Any,
    ) -> None:
        self.DataLoader = DataLoader
        self.KMeans = KMeans
        self.get_graph = get_graph
        self.kneighbors_graph = kneighbors_graph
        self.torch = torch
        self.train_DGI = train_DGI


def _load_backend() -> _Backend:
    repo_root = Path(__file__).resolve().parents[4]
    ccst_root = repo_root / "BenchmarkST" / "CCST"
    if str(ccst_root) not in sys.path:
        sys.path.insert(0, str(ccst_root))
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from CCST import get_graph, train_DGI
            from sklearn.cluster import KMeans
            from sklearn.neighbors import kneighbors_graph
            from torch_geometric.data import DataLoader
            import torch
    except ImportError as exc:
        raise RuntimeError(
            "CCST dependencies are not installed. Install torch-geometric into the uv environment."
        ) from exc
    return _Backend(
        DataLoader=DataLoader,
        KMeans=KMeans,
        get_graph=get_graph,
        kneighbors_graph=kneighbors_graph,
        torch=torch,
        train_DGI=train_DGI,
    )


def _seed_backend(random_state: int, torch_module: Any) -> None:
    random.seed(random_state)
    np.random.seed(random_state)
    torch_module.manual_seed(random_state)
    if torch_module.cuda.is_available():
        torch_module.cuda.manual_seed_all(random_state)


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
