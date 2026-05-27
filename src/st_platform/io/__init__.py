"""I/O utilities for reading spatial transcriptomics data files."""

from .h5ad_reader import read_h5ad_to_bundle

__all__ = ["read_h5ad_to_bundle"]
