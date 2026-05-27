"""Read h5ad files into SpatialDataBundle objects."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Optional

import numpy as np

from st_platform.data import DataAsset, DatasetRef, SpatialDataBundle

logger = logging.getLogger(__name__)


def read_h5ad_to_bundle(
    path: str,
    spatial_key: str = "spatial",
    label_column: Optional[str] = None,
) -> SpatialDataBundle:
    """Read an h5ad file and return a SpatialDataBundle.

    Parameters
    ----------
    path : str
        Path to the h5ad file.
    spatial_key : str
        Key in adata.obsm for spatial coordinates. Default ``"spatial"``.
    label_column : str or None
        Column name in adata.obs containing ground-truth labels.
        If provided and present, labels are stored in the bundle metadata.

    Returns
    -------
    SpatialDataBundle
        Bundle with counts_table and spatial_coordinates assets populated
        from the h5ad file.
    """
    import anndata

    h5ad_path = Path(path)
    if not h5ad_path.exists():
        raise FileNotFoundError(f"h5ad file not found: {path}")

    adata = anndata.read_h5ad(str(h5ad_path))

    # --- counts matrix: handle sparse and dense ---
    X = adata.X
    if hasattr(X, "toarray"):
        matrix = X.toarray()
    elif hasattr(X, "todense"):
        matrix = np.asarray(X.todense())
    else:
        matrix = np.asarray(X)
    matrix = matrix.astype(float).tolist()

    # --- spatial coordinates ---
    if spatial_key not in adata.obsm:
        raise KeyError(
            f"Spatial key '{spatial_key}' not found in adata.obsm. "
            f"Available keys: {list(adata.obsm.keys())}"
        )
    coords = np.asarray(adata.obsm[spatial_key], dtype=float)
    coordinates = coords.tolist()

    # --- spot and gene identifiers ---
    spot_ids = [str(s) for s in adata.obs_names.tolist()]
    gene_names = [str(g) for g in adata.var_names.tolist()]

    n_obs, n_vars = adata.shape

    # --- dataset identifier from file path hash ---
    path_hash = hashlib.sha256(str(h5ad_path.resolve()).encode()).hexdigest()[:16]
    filename = h5ad_path.stem

    # --- optional ground-truth labels ---
    bundle_metadata: dict = {
        "n_obs": n_obs,
        "n_vars": n_vars,
        "spatial_key": spatial_key,
    }
    if label_column is not None:
        if label_column in adata.obs.columns:
            labels = [str(v) for v in adata.obs[label_column].tolist()]
            bundle_metadata["labels"] = labels
            bundle_metadata["label_column"] = label_column
            logger.info(
                "Loaded ground-truth labels from column '%s' (%d values)",
                label_column,
                len(labels),
            )
        else:
            logger.warning(
                "Label column '%s' not found in adata.obs. "
                "Available columns: %s",
                label_column,
                list(adata.obs.columns),
            )

    bundle = SpatialDataBundle(
        dataset=DatasetRef(
            dataset_id=path_hash,
            platform="h5ad",
            sample_id=filename,
            uri=str(h5ad_path.resolve()),
        ),
        coordinate_key=spatial_key,
        assets=[
            DataAsset(
                kind="counts_table",
                key="counts",
                description=f"Counts matrix from {filename} ({n_obs} spots x {n_vars} genes).",
                metadata={
                    "matrix": matrix,
                    "spot_ids": spot_ids,
                    "gene_names": gene_names,
                },
            ),
            DataAsset(
                kind="spatial_coordinates",
                key="coordinates",
                description=f"Spatial coordinates from {filename} ({n_obs} spots).",
                metadata={
                    "columns": ["x", "y"],
                    "coordinates": coordinates,
                },
            ),
        ],
        metadata=bundle_metadata,
    )

    logger.info(
        "Loaded h5ad bundle: %d spots, %d genes, platform=h5ad",
        n_obs,
        n_vars,
    )
    return bundle
