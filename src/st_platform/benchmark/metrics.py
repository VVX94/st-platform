"""Benchmark metric computation helpers."""

from __future__ import annotations

from datetime import datetime
from typing import List

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
