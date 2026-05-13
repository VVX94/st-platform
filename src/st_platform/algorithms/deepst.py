from __future__ import annotations

import contextlib
import io
import json
import random
import sys
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


class DeepSTDomainAlgorithm(Algorithm):
    spec = AlgorithmSpec(
        algorithm_id="deepst",
        name="DeepST Domain Detection",
        task_type=TaskType.DOMAIN_DETECTION,
        runtime="python",
        version="benchmarkst",
        description=(
            "Runs the local DeepST graph autoencoder and clusters the learned "
            "embeddings into spatial domains."
        ),
        tags=("classic", "deepst", "domain", "graph-autoencoder"),
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
        pre_epochs = int(parameters.get("pre_epochs", 1))
        epochs = int(parameters.get("epochs", 1))
        neighbor_k = int(parameters.get("neighbor_k", 3))
        neighbor_k = max(1, min(neighbor_k, n_spots - 1))
        xy = coordinates[:, :2].astype(float)
        features = _scale_features(matrix)
        graph = _build_graph_dict(
            xy=xy,
            neighbor_k=neighbor_k,
            kneighbors_graph=backend.kneighbors_graph,
            torch_module=backend.torch,
        )

        model = backend.DeepST_model(
            input_dim=features.shape[1],
            linear_encoder_hidden=[
                int(parameters.get("linear_hidden", 8)),
                int(parameters.get("linear_embedding", 4)),
            ],
            linear_decoder_hidden=[int(parameters.get("decoder_hidden", 8))],
            conv_hidden=[
                int(parameters.get("conv_hidden", 4)),
                int(parameters.get("conv_embedding", 2)),
            ],
            p_drop=float(parameters.get("dropout", 0.0)),
            dec_cluster_n=n_clusters,
        )
        trainer = backend.train(
            features,
            graph,
            model,
            pre_epochs=max(0, pre_epochs),
            epochs=max(0, epochs),
            lr=float(parameters.get("lr", 5e-4)),
            use_gpu=False,
        )

        with warnings.catch_warnings(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
            io.StringIO()
        ):
            warnings.simplefilter("ignore")
            if pre_epochs > 0 and epochs > 0:
                trainer.fit(cluster_n=n_clusters, pretrain=True)
            elif pre_epochs > 0:
                trainer.pretrain()
            embedding, _ = trainer.process()
            embedding = np.asarray(embedding, dtype=float)

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
                "pre_epochs": pre_epochs,
                "epochs": epochs,
                "random_state": random_state,
            },
        )
        output_path = Path(str(context["run_root"])) / "deepst-domains.json"
        output_path.write_text(json.dumps(assignments, indent=2), encoding="utf-8")

        domain_counts = Counter(int(label) for label in labels)
        return AlgorithmOutput(
            summary={
                "message": "DeepST domain detection completed.",
                "backend": "DeepST",
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
                    "description": "Per-spot DeepST spatial domain assignments.",
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
        DeepST_model: Any,
        KMeans: Any,
        kneighbors_graph: Any,
        torch: Any,
        train: Any,
    ) -> None:
        self.DeepST_model = DeepST_model
        self.KMeans = KMeans
        self.kneighbors_graph = kneighbors_graph
        self.torch = torch
        self.train = train


def _load_backend() -> _Backend:
    repo_root = Path(__file__).resolve().parents[4]
    deepst_root = repo_root / "BenchmarkST" / "DeepST" / "deepst"
    if str(deepst_root) not in sys.path:
        sys.path.insert(0, str(deepst_root))
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from model import DeepST_model
            from sklearn.cluster import KMeans
            from sklearn.neighbors import kneighbors_graph
            from trainer import train
            import torch
    except ImportError as exc:
        raise RuntimeError(
            "DeepST dependencies are not installed. Install torch-geometric, scikit-network, "
            "torchvision, scanpy, and scikit-learn into the uv environment."
        ) from exc
    return _Backend(
        DeepST_model=DeepST_model,
        KMeans=KMeans,
        kneighbors_graph=kneighbors_graph,
        torch=torch,
        train=train,
    )


def _seed_backend(random_state: int, torch_module: Any) -> None:
    random.seed(random_state)
    np.random.seed(random_state)
    torch_module.manual_seed(random_state)
    if torch_module.cuda.is_available():
        torch_module.cuda.manual_seed_all(random_state)


def _scale_features(matrix: np.ndarray) -> np.ndarray:
    values = np.log1p(np.clip(matrix.astype(float), a_min=0, a_max=None))
    minimum = values.min(axis=0, keepdims=True)
    maximum = values.max(axis=0, keepdims=True)
    spread = maximum - minimum
    spread[spread == 0] = 1.0
    return (values - minimum) / spread


def _build_graph_dict(
    xy: np.ndarray,
    neighbor_k: int,
    kneighbors_graph: Any,
    torch_module: Any,
) -> dict[str, Any]:
    adjacency = kneighbors_graph(
        xy,
        n_neighbors=neighbor_k,
        mode="connectivity",
        include_self=False,
    )
    dense = ((adjacency + adjacency.T) > 0).astype(float).toarray()
    dense = dense + np.eye(dense.shape[0], dtype=float)
    edge_rows, edge_cols = np.nonzero(dense)
    edge_index = torch_module.tensor(
        np.vstack([edge_rows, edge_cols]),
        dtype=torch_module.long,
    )
    adj_label = torch_module.tensor(dense, dtype=torch_module.float32)
    total_entries = float(dense.shape[0] * dense.shape[0])
    negative_entries = max(total_entries - float(dense.sum()), 1.0)
    return {
        "adj_norm": edge_index,
        "adj_label": adj_label,
        "norm_value": total_entries / (2.0 * negative_entries),
    }


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
