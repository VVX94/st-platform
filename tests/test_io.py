"""Tests for the h5ad reader module."""

from __future__ import annotations

import pytest

from st_platform.io.h5ad_reader import read_h5ad_to_bundle

STARMAP_PATH = (
    "/home/wx/project/aaa/spatial-transcriptomic/经典算法/"
    "BenchmarkST/ADEPT/dataset/STARmap/STARmap_20180505_BY3_1k.h5ad"
)


@pytest.fixture
def starmap_bundle():
    """Load the real STARmap h5ad file with labels."""
    return read_h5ad_to_bundle(STARMAP_PATH, label_column="label")


@pytest.fixture
def starmap_bundle_no_label():
    """Load the real STARmap h5ad file without labels."""
    return read_h5ad_to_bundle(STARMAP_PATH)


class TestReadH5adToBundle:
    """Tests for read_h5ad_to_bundle with real STARmap data."""

    def test_bundle_dataset_ref(self, starmap_bundle):
        ds = starmap_bundle.dataset
        assert ds.platform == "h5ad"
        assert ds.sample_id == "STARmap_20180505_BY3_1k"
        assert ds.uri is not None
        assert ds.dataset_id  # non-empty hash

    def test_bundle_has_two_assets(self, starmap_bundle):
        assert len(starmap_bundle.assets) == 2
        kinds = {a.kind for a in starmap_bundle.assets}
        assert kinds == {"counts_table", "spatial_coordinates"}

    def test_counts_table_shape(self, starmap_bundle):
        counts = [a for a in starmap_bundle.assets if a.kind == "counts_table"][0]
        matrix = counts.metadata["matrix"]
        assert len(matrix) == 1207  # n_obs
        assert len(matrix[0]) == 1020  # n_vars

    def test_spatial_coordinates_shape(self, starmap_bundle):
        coords = [a for a in starmap_bundle.assets if a.kind == "spatial_coordinates"][0]
        coordinates = coords.metadata["coordinates"]
        assert len(coordinates) == 1207
        assert len(coordinates[0]) == 2  # x, y

    def test_spot_ids_extraction(self, starmap_bundle):
        counts = [a for a in starmap_bundle.assets if a.kind == "counts_table"][0]
        spot_ids = counts.metadata["spot_ids"]
        assert len(spot_ids) == 1207
        assert all(isinstance(s, str) for s in spot_ids)

    def test_gene_names_extraction(self, starmap_bundle):
        counts = [a for a in starmap_bundle.assets if a.kind == "counts_table"][0]
        gene_names = counts.metadata["gene_names"]
        assert len(gene_names) == 1020
        assert all(isinstance(g, str) for g in gene_names)

    def test_labels_included_when_column_provided(self, starmap_bundle):
        labels = starmap_bundle.metadata.get("labels")
        assert labels is not None
        assert len(labels) == 1207
        assert starmap_bundle.metadata.get("label_column") == "label"

    def test_labels_not_included_when_not_requested(self, starmap_bundle_no_label):
        assert "labels" not in starmap_bundle_no_label.metadata
        assert "label_column" not in starmap_bundle_no_label.metadata

    def test_metadata_n_obs_n_vars(self, starmap_bundle):
        assert starmap_bundle.metadata["n_obs"] == 1207
        assert starmap_bundle.metadata["n_vars"] == 1020

    def test_spatial_key_in_metadata(self, starmap_bundle):
        assert starmap_bundle.metadata["spatial_key"] == "spatial"

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            read_h5ad_to_bundle("/nonexistent/path.h5ad")

    def test_invalid_label_column_warns(self, caplog):
        """Passing a nonexistent label_column should warn but not fail."""
        bundle = read_h5ad_to_bundle(STARMAP_PATH, label_column="nonexistent_col")
        assert "labels" not in bundle.metadata
        assert "nonexistent_col" in caplog.text

    def test_custom_spatial_key(self):
        """Loading with the default spatial_key should work for STARmap."""
        bundle = read_h5ad_to_bundle(STARMAP_PATH, spatial_key="spatial")
        assert bundle.metadata["spatial_key"] == "spatial"
