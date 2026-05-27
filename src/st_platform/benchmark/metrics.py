"""Benchmark metric computation helpers."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

import numpy as np


def compute_ari(true_labels: np.ndarray, pred_labels: np.ndarray) -> float:
    """Adjusted Rand Index between ground-truth and predicted labels.

    Parameters
    ----------
    true_labels : np.ndarray
        1-D array of ground-truth labels.
    pred_labels : np.ndarray
        1-D array of predicted labels.

    Returns
    -------
    float
        ARI score in [-1, 1].
    """
    from sklearn.metrics import adjusted_rand_score

    return float(adjusted_rand_score(np.asarray(true_labels), np.asarray(pred_labels)))


def compute_nmi(true_labels: np.ndarray, pred_labels: np.ndarray) -> float:
    """Normalized Mutual Information between ground-truth and predicted labels.

    Parameters
    ----------
    true_labels : np.ndarray
        1-D array of ground-truth labels.
    pred_labels : np.ndarray
        1-D array of predicted labels.

    Returns
    -------
    float
        NMI score in [0, 1].
    """
    from sklearn.metrics import normalized_mutual_info_score

    return float(normalized_mutual_info_score(np.asarray(true_labels), np.asarray(pred_labels)))


def compute_spatial_neighbor_agreement(
    labels: np.ndarray, coordinates: np.ndarray, k: int = 6
) -> float:
    """Fraction of spots whose k nearest neighbors share the same label.

    Parameters
    ----------
    labels : np.ndarray
        1-D array of integer domain labels, one per spot.
    coordinates : np.ndarray
        (n_spots, 2) array of spatial x/y coordinates.
    k : int
        Number of nearest neighbors to consider.

    Returns
    -------
    float
        Agreement ratio in [0, 1].
    """
    labels = np.asarray(labels)
    coordinates = np.asarray(coordinates, dtype=float)
    n = len(labels)
    if n <= 1:
        return 1.0
    k = min(k, n - 1)

    # Pairwise Euclidean distances
    deltas = coordinates[:, None, :] - coordinates[None, :, :]
    dists = np.sqrt(np.sum(deltas * deltas, axis=2))
    # Exclude self by setting diagonal to inf
    np.fill_diagonal(dists, np.inf)
    neighbors = np.argsort(dists, axis=1)[:, :k]

    total = n * k
    if total == 0:
        return 0.0
    matches = 0
    for i in range(n):
        matches += int(np.sum(labels[neighbors[i]] == labels[i]))
    return matches / total


def compute_artifact_completeness(
    artifacts: list[dict], required_kinds: list[str]
) -> float:
    """Fraction of required artifact kinds that are present.

    Parameters
    ----------
    artifacts : list[dict]
        Each dict must have a ``kind`` key.
    required_kinds : list[str]
        Kinds that should be present.

    Returns
    -------
    float
        Completeness ratio in [0, 1].
    """
    if not required_kinds:
        return 1.0
    present = {a.get("kind") for a in artifacts}
    hits = sum(1 for k in required_kinds if k in present)
    return hits / len(required_kinds)


def compute_runtime_seconds(started_at: datetime, finished_at: datetime) -> float:
    """Seconds between two datetimes.

    Parameters
    ----------
    started_at : datetime
    finished_at : datetime

    Returns
    -------
    float
        Elapsed seconds.
    """
    delta = finished_at - started_at
    return delta.total_seconds()


def compute_homogeneity(true_labels: np.ndarray, pred_labels: np.ndarray) -> float:
    """Homogeneity: each cluster contains only members of a single class.

    Requires ground truth. Uses sklearn.metrics.homogeneity_score.

    Parameters
    ----------
    true_labels : np.ndarray
        1-D array of ground-truth labels.
    pred_labels : np.ndarray
        1-D array of predicted labels.

    Returns
    -------
    float
        Homogeneity score in [0, 1].
    """
    from sklearn.metrics import homogeneity_score

    return float(homogeneity_score(np.asarray(true_labels), np.asarray(pred_labels)))


def compute_completeness(true_labels: np.ndarray, pred_labels: np.ndarray) -> float:
    """Completeness: all members of a given class are assigned to the same cluster.

    Requires ground truth. Uses sklearn.metrics.completeness_score.

    Parameters
    ----------
    true_labels : np.ndarray
        1-D array of ground-truth labels.
    pred_labels : np.ndarray
        1-D array of predicted labels.

    Returns
    -------
    float
        Completeness score in [0, 1].
    """
    from sklearn.metrics import completeness_score

    return float(completeness_score(np.asarray(true_labels), np.asarray(pred_labels)))


def compute_asw(features: np.ndarray, labels: np.ndarray, sample_size: int = 5000) -> float:
    """Average Silhouette Width on expression features.

    Uses sklearn.metrics.silhouette_score with euclidean metric.
    If n_samples > sample_size, subsample for efficiency.

    Parameters
    ----------
    features : np.ndarray
        (n_samples, n_features) expression matrix.
    labels : np.ndarray
        1-D array of cluster labels.
    sample_size : int
        Maximum number of samples for silhouette computation.

    Returns
    -------
    float
        ASW score in [-1, 1].
    """
    from sklearn.metrics import silhouette_score

    features = np.asarray(features, dtype=float)
    labels = np.asarray(labels)
    n = len(labels)

    if n <= 1:
        return 0.0

    # Need at least 2 distinct labels
    if len(np.unique(labels)) < 2:
        return 0.0

    if n > sample_size:
        rng = np.random.RandomState(42)
        idx = rng.choice(n, size=sample_size, replace=False)
        features = features[idx]
        labels = labels[idx]

    return float(silhouette_score(features, labels, metric="euclidean"))


def _build_knn_neighbors(coordinates: np.ndarray, k: int) -> np.ndarray:
    """Build k-NN neighbor indices from coordinates.

    Parameters
    ----------
    coordinates : np.ndarray
        (n, 2) spatial coordinates.
    k : int
        Number of nearest neighbors.

    Returns
    -------
    np.ndarray
        (n, k) array of neighbor indices.
    """
    n = len(coordinates)
    k = min(k, n - 1)
    deltas = coordinates[:, None, :] - coordinates[None, :, :]
    dists = np.sqrt(np.sum(deltas * deltas, axis=2))
    np.fill_diagonal(dists, np.inf)
    return np.argsort(dists, axis=1)[:, :k]


def compute_chaos(labels: np.ndarray, coordinates: np.ndarray, k: int = 6) -> float:
    """Spatial chaos: fraction of neighbor pairs with different labels.

    CHAOS = 1 - spatial_neighbor_agreement.

    Parameters
    ----------
    labels : np.ndarray
        1-D array of domain labels.
    coordinates : np.ndarray
        (n_spots, 2) spatial coordinates.
    k : int
        Number of nearest neighbors.

    Returns
    -------
    float
        Chaos score in [0, 1]. Higher = more mixed.
    """
    return 1.0 - compute_spatial_neighbor_agreement(labels, coordinates, k)


def compute_pas(labels: np.ndarray, coordinates: np.ndarray, k: int = 6) -> float:
    """Pathology-Aware Spatial coherence: fraction of boundary spots.

    A boundary spot has at least one k-NN neighbor in a different domain.

    Parameters
    ----------
    labels : np.ndarray
        1-D array of domain labels.
    coordinates : np.ndarray
        (n_spots, 2) spatial coordinates.
    k : int
        Number of nearest neighbors.

    Returns
    -------
    float
        PAS score in [0, 1]. Higher = more boundary.
    """
    labels = np.asarray(labels)
    coordinates = np.asarray(coordinates, dtype=float)
    n = len(labels)

    if n <= 1:
        return 0.0

    neighbors = _build_knn_neighbors(coordinates, k)

    boundary_count = 0
    for i in range(n):
        if np.any(labels[neighbors[i]] != labels[i]):
            boundary_count += 1

    return boundary_count / n


def compute_morans_i(labels: np.ndarray, coordinates: np.ndarray, k: int = 6) -> float:
    """Moran's I spatial autocorrelation statistic.

    Uses binary k-NN spatial weights matrix.
    I = (n / S0) * sum_ij(wij * zi * zj) / sum_i(zi^2)

    Parameters
    ----------
    labels : np.ndarray
        1-D array of numeric labels (int or float). Strings will be encoded.
    coordinates : np.ndarray
        (n_spots, 2) spatial coordinates.
    k : int
        Number of nearest neighbors.

    Returns
    -------
    float
        Moran's I, typically in [-1, 1].
    """
    from sklearn.preprocessing import LabelEncoder

    labels = np.asarray(labels)
    coordinates = np.asarray(coordinates, dtype=float)
    n = len(labels)

    if n <= 1:
        return 0.0

    # Encode string labels to integers
    if labels.dtype.kind in ("U", "S", "O"):
        labels = LabelEncoder().fit_transform(labels)

    labels = labels.astype(float)
    k = min(k, n - 1)

    z = labels - np.mean(labels)
    ss = np.sum(z * z)
    if ss == 0:
        return 0.0

    neighbors = _build_knn_neighbors(coordinates, k)

    # S0 = n * k (each spot has k neighbors)
    S0 = n * k
    if S0 == 0:
        return 0.0

    # Vectorized: sum_ij(wij * zi * zj) = sum_i(zi * sum_{j in N(i)} zj)
    cross = 0.0
    for i in range(n):
        cross += z[i] * np.sum(z[neighbors[i]])

    I = (n / S0) * cross / ss
    return float(I)


def compute_gearys_c(labels: np.ndarray, coordinates: np.ndarray, k: int = 6) -> float:
    """Geary's C spatial autocorrelation statistic.

    Uses binary k-NN spatial weights matrix.
    C = (n-1) / (2*S0) * sum_ij(wij * (zi - zj)^2) / sum_i(zi^2)

    Parameters
    ----------
    labels : np.ndarray
        1-D array of numeric labels (int or float). Strings will be encoded.
    coordinates : np.ndarray
        (n_spots, 2) spatial coordinates.
    k : int
        Number of nearest neighbors.

    Returns
    -------
    float
        Geary's C, typically in [0, 2]. C < 1 = positive autocorrelation.
    """
    from sklearn.preprocessing import LabelEncoder

    labels = np.asarray(labels)
    coordinates = np.asarray(coordinates, dtype=float)
    n = len(labels)

    if n <= 1:
        return 0.0

    # Encode string labels to integers
    if labels.dtype.kind in ("U", "S", "O"):
        labels = LabelEncoder().fit_transform(labels)

    labels = labels.astype(float)
    k = min(k, n - 1)

    z = labels - np.mean(labels)
    ss = np.sum(z * z)
    if ss == 0:
        return 0.0

    neighbors = _build_knn_neighbors(coordinates, k)

    S0 = n * k
    if S0 == 0:
        return 0.0

    # Vectorized: sum_ij(wij * (zi - zj)^2) = sum_i sum_{j in N(i)} (zi - zj)^2
    diff_sq_sum = 0.0
    for i in range(n):
        diff_sq_sum += np.sum((z[i] - z[neighbors[i]]) ** 2)

    C = (n - 1) / (2 * S0) * diff_sq_sum / ss
    return float(C)


def compute_all_metrics(
    pred_labels: np.ndarray,
    coordinates: np.ndarray,
    features: Optional[np.ndarray] = None,
    true_labels: Optional[np.ndarray] = None,
    k: int = 6,
    artifacts: Optional[list[dict]] = None,
    required_artifact_kinds: Optional[list[str]] = None,
) -> dict[str, float]:
    """Compute all applicable metrics and return as dict.

    Skips label-dependent metrics when true_labels is None.
    Skips ASW when features is None.

    Parameters
    ----------
    pred_labels : np.ndarray
        1-D array of predicted domain labels.
    coordinates : np.ndarray
        (n_spots, 2) spatial coordinates.
    features : np.ndarray or None
        (n_spots, n_features) expression matrix for ASW.
    true_labels : np.ndarray or None
        1-D array of ground-truth labels.
    k : int
        Number of nearest neighbors for spatial metrics.
    artifacts : list[dict] or None
        Run artifacts for completeness check.
    required_artifact_kinds : list[str] or None
        Required artifact kinds for completeness check.

    Returns
    -------
    dict[str, float]
        All computed metric values.
    """
    metrics: dict[str, float] = {}

    # Label-dependent metrics (require ground truth)
    if true_labels is not None:
        true_labels = np.asarray(true_labels)
        pred_labels_arr = np.asarray(pred_labels)
        metrics["ari"] = compute_ari(true_labels, pred_labels_arr)
        metrics["nmi"] = compute_nmi(true_labels, pred_labels_arr)
        metrics["homogeneity"] = compute_homogeneity(true_labels, pred_labels_arr)
        metrics["completeness"] = compute_completeness(true_labels, pred_labels_arr)

    # Spatial metrics
    pred_labels_arr = np.asarray(pred_labels)
    coordinates_arr = np.asarray(coordinates, dtype=float)
    metrics["spatial_neighbor_agreement"] = compute_spatial_neighbor_agreement(
        pred_labels_arr, coordinates_arr, k
    )
    metrics["chaos"] = compute_chaos(pred_labels_arr, coordinates_arr, k)
    metrics["pas"] = compute_pas(pred_labels_arr, coordinates_arr, k)
    metrics["morans_i"] = compute_morans_i(pred_labels_arr, coordinates_arr, k)
    metrics["gearys_c"] = compute_gearys_c(pred_labels_arr, coordinates_arr, k)

    # ASW (requires features)
    if features is not None:
        metrics["asw"] = compute_asw(np.asarray(features, dtype=float), pred_labels_arr)

    # Artifact completeness
    if artifacts is not None and required_artifact_kinds is not None:
        metrics["artifact_completeness"] = compute_artifact_completeness(
            artifacts, required_artifact_kinds
        )

    return metrics
