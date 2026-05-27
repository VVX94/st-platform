"""Tests for benchmark metric computation helpers."""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest

from st_platform.benchmark.metrics import (
    compute_artifact_completeness,
    compute_runtime_seconds,
    compute_spatial_neighbor_agreement,
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
