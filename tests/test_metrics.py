"""Tests for benchmark metric computation helpers."""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest

from st_platform.benchmark.metrics import (
    compute_ari,
    compute_artifact_completeness,
    compute_asw,
    compute_chaos,
    compute_completeness,
    compute_gearys_c,
    compute_homogeneity,
    compute_morans_i,
    compute_nmi,
    compute_pas,
    compute_runtime_seconds,
    compute_spatial_neighbor_agreement,
    compute_all_metrics,
)


class TestSpatialNeighborAgreement:
    def test_identical_labels_returns_one(self):
        """All spots have the same label -> agreement = 1.0."""
        labels = np.array([0, 0, 0, 0, 0])
        coords = np.array([[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]], dtype=float)
        result = compute_spatial_neighbor_agreement(labels, coords, k=2)
        assert result == pytest.approx(1.0)

    def test_two_clusters_linear(self):
        """Two distinct clusters on a line -> high agreement."""
        labels = np.array([0, 0, 0, 1, 1, 1])
        coords = np.array([[0, 0], [1, 0], [2, 0], [10, 0], [11, 0], [12, 0]], dtype=float)
        result = compute_spatial_neighbor_agreement(labels, coords, k=2)
        assert result > 0.9

    def test_alternating_labels_low_agreement(self):
        """Alternating labels with interleaved positions -> low agreement."""
        labels = np.array([0, 1, 0, 1, 0, 1])
        coords = np.array([[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0]], dtype=float)
        result = compute_spatial_neighbor_agreement(labels, coords, k=1)
        assert result < 0.2

    def test_single_spot(self):
        """Single spot should return 1.0."""
        labels = np.array([0])
        coords = np.array([[0, 0]], dtype=float)
        result = compute_spatial_neighbor_agreement(labels, coords, k=6)
        assert result == 1.0

    def test_two_spots(self):
        """Two spots, same label -> 1.0."""
        labels = np.array([0, 0])
        coords = np.array([[0, 0], [1, 0]], dtype=float)
        result = compute_spatial_neighbor_agreement(labels, coords, k=1)
        assert result == pytest.approx(1.0)

    def test_k_larger_than_n_minus_one(self):
        """k > n-1 should be clamped."""
        labels = np.array([0, 1, 0])
        coords = np.array([[0, 0], [10, 0], [20, 0]], dtype=float)
        result = compute_spatial_neighbor_agreement(labels, coords, k=100)
        assert 0.0 <= result <= 1.0

    def test_result_in_range(self):
        """Result always in [0, 1]."""
        rng = np.random.RandomState(42)
        labels = rng.randint(0, 5, size=50)
        coords = rng.randn(50, 2)
        result = compute_spatial_neighbor_agreement(labels, coords, k=6)
        assert 0.0 <= result <= 1.0


class TestArtifactCompleteness:
    def test_all_present(self):
        artifacts = [{"kind": "csv"}, {"kind": "plot"}]
        assert compute_artifact_completeness(artifacts, ["csv", "plot"]) == pytest.approx(1.0)

    def test_partial(self):
        artifacts = [{"kind": "csv"}]
        assert compute_artifact_completeness(artifacts, ["csv", "plot"]) == pytest.approx(0.5)

    def test_none_present(self):
        artifacts = [{"kind": "other"}]
        assert compute_artifact_completeness(artifacts, ["csv", "plot"]) == pytest.approx(0.0)

    def test_empty_required(self):
        assert compute_artifact_completeness([{"kind": "x"}], []) == pytest.approx(1.0)

    def test_empty_both(self):
        assert compute_artifact_completeness([], []) == pytest.approx(1.0)

    def test_empty_artifacts_nonempty_required(self):
        assert compute_artifact_completeness([], ["csv"]) == pytest.approx(0.0)


class TestRuntimeSeconds:
    def test_basic(self):
        start = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        finish = datetime(2025, 1, 1, 0, 1, 30, tzinfo=timezone.utc)
        assert compute_runtime_seconds(start, finish) == pytest.approx(90.0)

    def test_same_time(self):
        t = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert compute_runtime_seconds(t, t) == pytest.approx(0.0)

    def test_negative_when_reversed(self):
        start = datetime(2025, 1, 1, 0, 1, 0, tzinfo=timezone.utc)
        finish = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        assert compute_runtime_seconds(start, finish) == pytest.approx(-60.0)


class TestARI:
    """Tests for compute_ari (Adjusted Rand Index)."""

    def test_identical_labels(self):
        labels = np.array([0, 0, 1, 1, 2, 2])
        assert compute_ari(labels, labels) == pytest.approx(1.0)

    def test_random_labels_in_range(self):
        rng = np.random.RandomState(42)
        true = rng.randint(0, 5, size=100)
        pred = rng.randint(0, 5, size=100)
        ari = compute_ari(true, pred)
        assert -1.0 <= ari <= 1.0

    def test_permuted_labels(self):
        """Permuting cluster IDs should give perfect ARI."""
        true = np.array([0, 0, 1, 1, 2, 2])
        pred = np.array([2, 2, 0, 0, 1, 1])
        assert compute_ari(true, pred) == pytest.approx(1.0)

    def test_completely_wrong(self):
        """Opposite assignments should give low ARI."""
        true = np.array([0, 0, 0, 1, 1, 1])
        pred = np.array([1, 1, 1, 0, 0, 0])
        assert compute_ari(true, pred) == pytest.approx(1.0)  # permuted = perfect

    def test_single_cluster(self):
        true = np.array([0, 0, 0])
        pred = np.array([0, 0, 0])
        assert compute_ari(true, pred) == pytest.approx(1.0)


class TestNMI:
    """Tests for compute_nmi (Normalized Mutual Information)."""

    def test_identical_labels(self):
        labels = np.array([0, 0, 1, 1, 2, 2])
        assert compute_nmi(labels, labels) == pytest.approx(1.0)

    def test_random_labels_in_range(self):
        rng = np.random.RandomState(42)
        true = rng.randint(0, 5, size=100)
        pred = rng.randint(0, 5, size=100)
        nmi = compute_nmi(true, pred)
        assert 0.0 <= nmi <= 1.0

    def test_permuted_labels(self):
        """Permuting cluster IDs should give perfect NMI."""
        true = np.array([0, 0, 1, 1, 2, 2])
        pred = np.array([2, 2, 0, 0, 1, 1])
        assert compute_nmi(true, pred) == pytest.approx(1.0)

    def test_single_cluster(self):
        true = np.array([0, 0, 0])
        pred = np.array([0, 0, 0])
        assert compute_nmi(true, pred) == pytest.approx(1.0)

    def test_completely_different_structure(self):
        true = np.array([0, 0, 0, 1, 1, 1])
        pred = np.array([0, 1, 0, 1, 0, 1])
        nmi = compute_nmi(true, pred)
        assert nmi < 0.5  # should be low


class TestHomogeneity:
    """Tests for compute_homogeneity."""

    def test_perfect_match(self):
        """Perfect match should give homogeneity = 1.0."""
        true = np.array([0, 0, 1, 1, 2, 2])
        pred = np.array([0, 0, 1, 1, 2, 2])
        assert compute_homogeneity(true, pred) == pytest.approx(1.0)

    def test_permuted_labels(self):
        """Permuting cluster IDs should give perfect homogeneity."""
        true = np.array([0, 0, 1, 1, 2, 2])
        pred = np.array([2, 2, 0, 0, 1, 1])
        assert compute_homogeneity(true, pred) == pytest.approx(1.0)

    def test_random_labels_low(self):
        """Random labels should give low homogeneity."""
        rng = np.random.RandomState(42)
        true = rng.randint(0, 5, size=100)
        pred = rng.randint(0, 5, size=100)
        hom = compute_homogeneity(true, pred)
        assert hom < 0.5

    def test_single_class(self):
        """Single class should give homogeneity = 1.0."""
        true = np.array([0, 0, 0])
        pred = np.array([0, 1, 2])
        assert compute_homogeneity(true, pred) == pytest.approx(1.0)


class TestCompleteness:
    """Tests for compute_completeness."""

    def test_perfect_match(self):
        """Perfect match should give completeness = 1.0."""
        true = np.array([0, 0, 1, 1, 2, 2])
        pred = np.array([0, 0, 1, 1, 2, 2])
        assert compute_completeness(true, pred) == pytest.approx(1.0)

    def test_permuted_labels(self):
        """Permuting cluster IDs should give perfect completeness."""
        true = np.array([0, 0, 1, 1, 2, 2])
        pred = np.array([2, 2, 0, 0, 1, 1])
        assert compute_completeness(true, pred) == pytest.approx(1.0)

    def test_random_labels_low(self):
        """Random labels should give low completeness."""
        rng = np.random.RandomState(42)
        true = rng.randint(0, 5, size=100)
        pred = rng.randint(0, 5, size=100)
        com = compute_completeness(true, pred)
        assert com < 0.5

    def test_single_cluster(self):
        """Single cluster should give completeness = 1.0."""
        true = np.array([0, 0, 1, 1])
        pred = np.array([0, 0, 0, 0])
        assert compute_completeness(true, pred) == pytest.approx(1.0)


class TestASW:
    """Tests for compute_asw (Average Silhouette Width)."""

    def test_known_clusters_positive(self):
        """Well-separated clusters should have positive ASW."""
        # Two distinct clusters
        features = np.array([
            [0, 0], [0.1, 0], [0, 0.1],
            [10, 10], [10.1, 10], [10, 10.1],
        ])
        labels = np.array([0, 0, 0, 1, 1, 1])
        asw = compute_asw(features, labels)
        assert asw > 0.5

    def test_single_spot(self):
        """Single spot should return 0.0."""
        features = np.array([[1, 2]])
        labels = np.array([0])
        assert compute_asw(features, labels) == pytest.approx(0.0)

    def test_single_label(self):
        """All same label should return 0.0."""
        features = np.array([[0, 0], [1, 1], [2, 2]])
        labels = np.array([0, 0, 0])
        assert compute_asw(features, labels) == pytest.approx(0.0)

    def test_range(self):
        """ASW should be in [-1, 1]."""
        rng = np.random.RandomState(42)
        features = rng.randn(50, 10)
        labels = rng.randint(0, 3, size=50)
        asw = compute_asw(features, labels)
        assert -1.0 <= asw <= 1.0

    def test_subsampling(self):
        """Large input should be subsampled without error."""
        rng = np.random.RandomState(42)
        features = rng.randn(100, 5)
        labels = rng.randint(0, 3, size=100)
        asw = compute_asw(features, labels, sample_size=50)
        assert -1.0 <= asw <= 1.0


class TestChaos:
    """Tests for compute_chaos."""

    def test_all_same_label(self):
        """All same label should give chaos = 0.0."""
        labels = np.array([0, 0, 0, 0, 0])
        coords = np.array([[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]], dtype=float)
        assert compute_chaos(labels, coords, k=2) == pytest.approx(0.0)

    def test_alternating_labels_high(self):
        """Alternating labels should give high chaos."""
        labels = np.array([0, 1, 0, 1, 0, 1])
        coords = np.array([[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0]], dtype=float)
        chaos = compute_chaos(labels, coords, k=1)
        assert chaos > 0.7

    def test_single_spot(self):
        """Single spot should give chaos = 0.0."""
        labels = np.array([0])
        coords = np.array([[0, 0]], dtype=float)
        assert compute_chaos(labels, coords) == pytest.approx(0.0)

    def test_range(self):
        """Chaos should be in [0, 1]."""
        rng = np.random.RandomState(42)
        labels = rng.randint(0, 3, size=20)
        coords = rng.randn(20, 2)
        chaos = compute_chaos(labels, coords, k=3)
        assert 0.0 <= chaos <= 1.0


class TestPAS:
    """Tests for compute_pas (Pathology-Aware Spatial coherence)."""

    def test_all_same_label(self):
        """All same label should give PAS = 0.0 (no boundary spots)."""
        labels = np.array([0, 0, 0, 0, 0])
        coords = np.array([[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]], dtype=float)
        assert compute_pas(labels, coords, k=2) == pytest.approx(0.0)

    def test_checkerboard_high(self):
        """Checkerboard pattern should give high PAS."""
        labels = np.array([0, 1, 0, 1, 0, 1])
        coords = np.array([[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0]], dtype=float)
        pas = compute_pas(labels, coords, k=1)
        assert pas > 0.7

    def test_single_spot(self):
        """Single spot should give PAS = 0.0."""
        labels = np.array([0])
        coords = np.array([[0, 0]], dtype=float)
        assert compute_pas(labels, coords) == pytest.approx(0.0)

    def test_two_clusters_adjacent(self):
        """Two adjacent clusters should have boundary spots."""
        labels = np.array([0, 0, 0, 1, 1, 1])
        coords = np.array([[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0]], dtype=float)
        pas = compute_pas(labels, coords, k=2)
        # Boundary spots: spot 2 (neighbors include spot 3) and spot 3 (neighbors include spot 2)
        assert 0.0 < pas < 1.0


class TestMoransI:
    """Tests for compute_morans_i."""

    def test_all_same_label(self):
        """All same label should give Moran's I close to 1.0."""
        labels = np.array([5, 5, 5, 5, 5, 5])
        coords = np.array([[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0]], dtype=float)
        # All same -> z = 0 -> I = 0 (edge case)
        I = compute_morans_i(labels, coords, k=2)
        assert I == pytest.approx(0.0)

    def test_spatial_autocorrelation(self):
        """Spatially clustered labels should give positive Moran's I."""
        labels = np.array([0, 0, 0, 1, 1, 1])
        coords = np.array([[0, 0], [1, 0], [2, 0], [10, 0], [11, 0], [12, 0]], dtype=float)
        I = compute_morans_i(labels, coords, k=2)
        assert I > 0.5

    def test_random_labels_near_zero(self):
        """Random labels should give Moran's I near 0."""
        rng = np.random.RandomState(42)
        labels = rng.randint(0, 5, size=100)
        coords = rng.randn(100, 2)
        I = compute_morans_i(labels, coords, k=6)
        assert abs(I) < 0.3

    def test_single_spot(self):
        """Single spot should return 0.0."""
        labels = np.array([5])
        coords = np.array([[0, 0]], dtype=float)
        assert compute_morans_i(labels, coords) == pytest.approx(0.0)

    def test_string_labels(self):
        """String labels should be encoded and computed without error."""
        labels = np.array(["A", "A", "A", "B", "B", "B"])
        coords = np.array([[0, 0], [1, 0], [2, 0], [10, 0], [11, 0], [12, 0]], dtype=float)
        I = compute_morans_i(labels, coords, k=2)
        assert isinstance(I, float)

    def test_range(self):
        """Moran's I should be in [-1, 1] for typical inputs."""
        rng = np.random.RandomState(42)
        labels = rng.randn(50)
        coords = rng.randn(50, 2)
        I = compute_morans_i(labels, coords, k=6)
        assert -1.5 <= I <= 1.5


class TestGearysC:
    """Tests for compute_gearys_c."""

    def test_all_same_label(self):
        """All same label should give Geary's C close to 0.0."""
        labels = np.array([5, 5, 5, 5, 5, 5])
        coords = np.array([[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0]], dtype=float)
        # All same -> z = 0 -> C = 0 (edge case)
        C = compute_gearys_c(labels, coords, k=2)
        assert C == pytest.approx(0.0)

    def test_spatial_autocorrelation_low_c(self):
        """Spatially clustered labels should give C < 1."""
        labels = np.array([0, 0, 0, 1, 1, 1])
        coords = np.array([[0, 0], [1, 0], [2, 0], [10, 0], [11, 0], [12, 0]], dtype=float)
        C = compute_gearys_c(labels, coords, k=2)
        assert C < 1.0

    def test_random_labels_near_one(self):
        """Random labels should give Geary's C near 1.0."""
        rng = np.random.RandomState(42)
        labels = rng.randint(0, 5, size=100)
        coords = rng.randn(100, 2)
        C = compute_gearys_c(labels, coords, k=6)
        assert 0.7 < C < 1.3

    def test_single_spot(self):
        """Single spot should return 0.0."""
        labels = np.array([5])
        coords = np.array([[0, 0]], dtype=float)
        assert compute_gearys_c(labels, coords) == pytest.approx(0.0)

    def test_string_labels(self):
        """String labels should be encoded and computed without error."""
        labels = np.array(["A", "A", "A", "B", "B", "B"])
        coords = np.array([[0, 0], [1, 0], [2, 0], [10, 0], [11, 0], [12, 0]], dtype=float)
        C = compute_gearys_c(labels, coords, k=2)
        assert isinstance(C, float)

    def test_range(self):
        """Geary's C should be in [0, 2] for typical inputs."""
        rng = np.random.RandomState(42)
        labels = rng.randn(50)
        coords = rng.randn(50, 2)
        C = compute_gearys_c(labels, coords, k=6)
        assert 0.0 <= C <= 2.5


class TestComputeAllMetrics:
    """Tests for compute_all_metrics."""

    def test_returns_expected_keys_with_true_labels(self):
        """Should return all expected keys when true_labels provided."""
        true = np.array([0, 0, 1, 1, 2, 2])
        pred = np.array([0, 0, 1, 1, 2, 2])
        coords = np.array([[0, 0], [1, 0], [2, 0], [10, 0], [11, 0], [12, 0]], dtype=float)
        features = np.array([[0, 0], [0.1, 0], [0, 0.1], [10, 10], [10.1, 10], [10, 10.1]])

        result = compute_all_metrics(
            pred_labels=pred,
            coordinates=coords,
            features=features,
            true_labels=true,
        )

        expected_keys = {
            "ari", "nmi", "homogeneity", "completeness",
            "spatial_neighbor_agreement", "chaos", "pas",
            "morans_i", "gearys_c", "asw",
        }
        assert expected_keys.issubset(set(result.keys()))

    def test_returns_expected_keys_without_true_labels(self):
        """Should skip label-dependent metrics when true_labels is None."""
        pred = np.array([0, 0, 1, 1, 2, 2])
        coords = np.array([[0, 0], [1, 0], [2, 0], [10, 0], [11, 0], [12, 0]], dtype=float)

        result = compute_all_metrics(
            pred_labels=pred,
            coordinates=coords,
        )

        assert "ari" not in result
        assert "nmi" not in result
        assert "homogeneity" not in result
        assert "completeness" not in result
        assert "spatial_neighbor_agreement" in result
        assert "chaos" in result
        assert "pas" in result
        assert "morans_i" in result
        assert "gearys_c" in result

    def test_returns_expected_keys_without_features(self):
        """Should skip ASW when features is None."""
        true = np.array([0, 0, 1, 1])
        pred = np.array([0, 0, 1, 1])
        coords = np.array([[0, 0], [1, 0], [10, 0], [11, 0]], dtype=float)

        result = compute_all_metrics(
            pred_labels=pred,
            coordinates=coords,
            true_labels=true,
        )

        assert "asw" not in result
        assert "ari" in result

    def test_artifact_completeness(self):
        """Should compute artifact_completeness when artifacts provided."""
        pred = np.array([0, 0, 1, 1])
        coords = np.array([[0, 0], [1, 0], [10, 0], [11, 0]], dtype=float)

        result = compute_all_metrics(
            pred_labels=pred,
            coordinates=coords,
            artifacts=[{"kind": "csv"}],
            required_artifact_kinds=["csv", "plot"],
        )

        assert "artifact_completeness" in result
        assert result["artifact_completeness"] == pytest.approx(0.5)
