from __future__ import annotations

import json
import tempfile
from pathlib import Path

import numpy as np
import pytest

from st_platform.algorithms.stagate_lite import STAGATELiteDomainAlgorithm
from st_platform.algorithms.spaceflow_lite import SpaceFlowLiteDomainAlgorithm
from st_platform.data import DataAsset, DatasetRef, SpatialDataBundle
from st_platform.tasks import TaskType


def _make_bundle(n_spots: int = 120, n_genes: int = 50) -> SpatialDataBundle:
    rng = np.random.default_rng(42)
    matrix = rng.poisson(lam=5, size=(n_spots, n_genes)).astype(float)
    coords = np.column_stack([
        np.tile(np.arange(10), n_spots // 10 + 1)[:n_spots].astype(float),
        np.repeat(np.arange(n_spots // 10 + 1), 10)[:n_spots].astype(float),
    ])
    return SpatialDataBundle(
        dataset=DatasetRef(
            dataset_id="test-dataset",
            platform="test",
            sample_id="test-sample",
            uri="file:///tmp/test.h5ad",
        ),
        coordinate_key="spatial",
        table_name="X",
        modality="transcriptomics",
        assets=[
            DataAsset(
                kind="counts_table",
                key="counts_table",
                description="Test counts",
                uri="file:///tmp/counts",
                metadata={
                    "matrix": matrix.tolist(),
                    "spot_ids": [f"s{i}" for i in range(n_spots)],
                    "gene_names": [f"g{i}" for i in range(n_genes)],
                },
            ),
            DataAsset(
                kind="spatial_coordinates",
                key="spatial_coordinates",
                description="Test coords",
                uri="file:///tmp/coords",
                metadata={"coordinates": coords.tolist()},
            ),
        ],
        metadata={},
    )


@pytest.fixture
def bundle() -> SpatialDataBundle:
    return _make_bundle()


@pytest.fixture
def run_root(tmp_path: Path) -> Path:
    root = tmp_path / "run_output"
    root.mkdir()
    return root


class TestSTAGATELite:
    def test_spec(self):
        algo = STAGATELiteDomainAlgorithm()
        assert algo.spec.algorithm_id == "stagate-lite"
        assert algo.spec.task_type == TaskType.DOMAIN_DETECTION

    def test_run_produces_output(self, bundle, run_root):
        algo = STAGATELiteDomainAlgorithm()
        output = algo.run(
            bundle,
            {"n_clusters": 3, "neighbor_k": 4, "random_state": 0},
            {"run_root": str(run_root)},
        )
        assert output.summary["predicted_domains"] == 3
        assert "spatial_neighbor_agreement" in output.metrics
        assert output.metrics["spot_count"] == 120.0

    def test_artifact_written(self, bundle, run_root):
        algo = STAGATELiteDomainAlgorithm()
        output = algo.run(
            bundle,
            {"n_clusters": 3, "random_state": 0},
            {"run_root": str(run_root)},
        )
        artifact_path = run_root / "stagate-lite-domains.json"
        assert artifact_path.exists()
        data = json.loads(artifact_path.read_text())
        assert data["algorithm_id"] == "stagate-lite"
        assert len(data["domains"]) == 120

    def test_domain_assignments_format(self, bundle, run_root):
        algo = STAGATELiteDomainAlgorithm()
        output = algo.run(
            bundle,
            {"n_clusters": 4, "random_state": 0},
            {"run_root": str(run_root)},
        )
        data = json.loads((run_root / "stagate-lite-domains.json").read_text())
        for domain in data["domains"]:
            assert "spot_id" in domain
            assert "domain" in domain
            assert "x" in domain
            assert "y" in domain

    def test_pca_variance_reported(self, bundle, run_root):
        algo = STAGATELiteDomainAlgorithm()
        output = algo.run(
            bundle,
            {"n_clusters": 3, "random_state": 0},
            {"run_root": str(run_root)},
        )
        assert 0.0 < output.metrics["pca_explained_variance"] <= 1.0

    def test_refinement_changes(self, bundle, run_root):
        algo = STAGATELiteDomainAlgorithm()
        output = algo.run(
            bundle,
            {"n_clusters": 3, "neighbor_k": 6, "random_state": 0},
            {"run_root": str(run_root)},
        )
        assert output.metrics["refinement_changes"] >= 0.0

    def test_invalid_n_clusters(self, bundle, run_root):
        algo = STAGATELiteDomainAlgorithm()
        with pytest.raises(ValueError, match="n_clusters"):
            algo.run(bundle, {"n_clusters": 1}, {"run_root": str(run_root)})

    def test_mismatched_dimensions(self, run_root):
        bundle = _make_bundle(n_spots=50, n_genes=30)
        bad_bundle = SpatialDataBundle(
            dataset=bundle.dataset,
            coordinate_key=bundle.coordinate_key,
            table_name=bundle.table_name,
            modality=bundle.modality,
            assets=[
                DataAsset(
                    kind="counts_table",
                    key="counts_table",
                    description="Test",
                    uri="file:///tmp/counts",
                    metadata={
                        "matrix": np.zeros((50, 30)).tolist(),
                        "spot_ids": [f"s{i}" for i in range(50)],
                        "gene_names": [f"g{i}" for i in range(30)],
                    },
                ),
                DataAsset(
                    kind="spatial_coordinates",
                    key="spatial_coordinates",
                    description="Test",
                    uri="file:///tmp/coords",
                    metadata={"coordinates": np.zeros((30, 2)).tolist()},
                ),
            ],
            metadata={},
        )
        algo = STAGATELiteDomainAlgorithm()
        with pytest.raises(ValueError, match="same number"):
            algo.run(bad_bundle, {"n_clusters": 3}, {"run_root": str(run_root)})


class TestSpaceFlowLite:
    def test_spec(self):
        algo = SpaceFlowLiteDomainAlgorithm()
        assert algo.spec.algorithm_id == "spaceflow-lite"
        assert algo.spec.task_type == TaskType.DOMAIN_DETECTION

    def test_run_produces_output(self, bundle, run_root):
        algo = SpaceFlowLiteDomainAlgorithm()
        output = algo.run(
            bundle,
            {"n_clusters": 3, "neighbor_k": 4, "random_state": 0},
            {"run_root": str(run_root)},
        )
        assert output.summary["predicted_domains"] == 3
        assert "spatial_neighbor_agreement" in output.metrics
        assert output.metrics["spot_count"] == 120.0

    def test_artifact_written(self, bundle, run_root):
        algo = SpaceFlowLiteDomainAlgorithm()
        output = algo.run(
            bundle,
            {"n_clusters": 3, "random_state": 0},
            {"run_root": str(run_root)},
        )
        artifact_path = run_root / "spaceflow-lite-domains.json"
        assert artifact_path.exists()
        data = json.loads(artifact_path.read_text())
        assert data["algorithm_id"] == "spaceflow-lite"
        assert len(data["domains"]) == 120

    def test_top_genes_parameter(self, bundle, run_root):
        algo = SpaceFlowLiteDomainAlgorithm()
        output = algo.run(
            bundle,
            {"n_clusters": 3, "n_top_genes": 20, "random_state": 0},
            {"run_root": str(run_root)},
        )
        assert output.summary["predicted_domains"] == 3

    def test_domain_assignments_format(self, bundle, run_root):
        algo = SpaceFlowLiteDomainAlgorithm()
        output = algo.run(
            bundle,
            {"n_clusters": 4, "random_state": 0},
            {"run_root": str(run_root)},
        )
        data = json.loads((run_root / "spaceflow-lite-domains.json").read_text())
        for domain in data["domains"]:
            assert "spot_id" in domain
            assert "domain" in domain
            assert "x" in domain
            assert "y" in domain

    def test_pca_variance_reported(self, bundle, run_root):
        algo = SpaceFlowLiteDomainAlgorithm()
        output = algo.run(
            bundle,
            {"n_clusters": 3, "random_state": 0},
            {"run_root": str(run_root)},
        )
        assert 0.0 < output.metrics["pca_explained_variance"] <= 1.0

    def test_invalid_n_clusters(self, bundle, run_root):
        algo = SpaceFlowLiteDomainAlgorithm()
        with pytest.raises(ValueError, match="n_clusters"):
            algo.run(bundle, {"n_clusters": 1}, {"run_root": str(run_root)})

    def test_mismatched_dimensions(self, run_root):
        bundle = _make_bundle(n_spots=50, n_genes=30)
        bad_bundle = SpatialDataBundle(
            dataset=bundle.dataset,
            coordinate_key=bundle.coordinate_key,
            table_name=bundle.table_name,
            modality=bundle.modality,
            assets=[
                DataAsset(
                    kind="counts_table",
                    key="counts_table",
                    description="Test",
                    uri="file:///tmp/counts",
                    metadata={
                        "matrix": np.zeros((50, 30)).tolist(),
                        "spot_ids": [f"s{i}" for i in range(50)],
                        "gene_names": [f"g{i}" for i in range(30)],
                    },
                ),
                DataAsset(
                    kind="spatial_coordinates",
                    key="spatial_coordinates",
                    description="Test",
                    uri="file:///tmp/coords",
                    metadata={"coordinates": np.zeros((30, 2)).tolist()},
                ),
            ],
            metadata={},
        )
        algo = SpaceFlowLiteDomainAlgorithm()
        with pytest.raises(ValueError, match="same number"):
            algo.run(bad_bundle, {"n_clusters": 3}, {"run_root": str(run_root)})
