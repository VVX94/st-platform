# Evaluator Report: SPRINT-20260527-004-h5ad-reader-real-data

Date: 2026-05-27
Evaluator: automated

## Test Results

```
97 passed, 6 skipped, 168 warnings in 3.85s
```

All tests pass. Skipped tests are for optional heavy dependencies (SpaGCN, GraphST, SEDR, CCST, conST, DeepST) that are not installed in the test environment. This is expected behavior.

## Acceptance Criteria Verification

### AC1: h5ad reader reads STARmap file correctly

PASS. `src/st_platform/io/h5ad_reader.py` implements `read_h5ad_to_bundle()` which:
- Reads h5ad via `anndata.read_h5ad()`
- Handles sparse and dense matrices
- Extracts spatial coordinates from `adata.obsm[spatial_key]`
- Extracts spot IDs and gene names
- Returns a `SpatialDataBundle` with `counts_table` and `spatial_coordinates` assets
- Optionally loads ground-truth labels from a specified obs column

`tests/test_io.py` validates:
- Bundle shape: 1207 spots x 1020 genes
- Spatial coordinates: 1207 x 2
- Spot IDs and gene names extraction
- Labels included when `label_column` provided
- Labels omitted when not requested
- Error handling for missing files and invalid label columns

### AC2: POST /api/datasets/register-real returns 201

PASS. `src/st_platform/api/routes/datasets.py` lines 72-101 define the `register-real` endpoint:
- Accepts `DatasetRegisterReal` schema (name, path, spatial_key, label_column, description)
- Calls `read_h5ad_to_bundle()` to validate and read the file
- Creates a dataset record with platform="h5ad", demo=False
- Stores n_obs, n_vars, label_column, spatial_key in metadata
- Returns 201 with `DatasetOut`

`tests/test_ee.py::TestRealDataBenchmarkFlow::test_real_starmap_benchmark_flow` confirms 201 response.

### AC3: Worker loads real h5ad data for runs

PASS. `src/st_platform/worker/runner.py` lines 243-259:
- When `ds_platform == "h5ad"` and `ds_uri` is set, imports and calls `read_h5ad_to_bundle()`
- Passes `spatial_key` and `label_column` from dataset metadata
- On failure, marks the run as failed with a clear error message

### AC4: ARI/NMI computed when ground truth exists

PASS. `src/st_platform/worker/runner.py` lines 130-180 (`_compute_clustering_metrics`):
- Extracts predicted domains from `domain_assignments` artifact
- Compares against `ground_truth_labels` from bundle metadata
- Calls `compute_ari()` and `compute_nmi()` from `benchmark/metrics.py`
- Handles label count mismatches gracefully

`src/st_platform/benchmark/metrics.py`:
- `compute_ari()`: wraps `sklearn.metrics.adjusted_rand_score`, returns float in [-1, 1]
- `compute_nmi()`: wraps `sklearn.metrics.normalized_mutual_info_score`, returns float in [0, 1]

### AC5: Reports include ARI/NMI

PASS. `src/st_platform/benchmark/reports.py`:
- `generate_run_metrics_csv()`: writes all metrics (including ARI/NMI) to CSV
- `generate_metrics_bar_plot()`: renders bar chart of all metrics
- `generate_markdown_report()`: includes metrics table per run

The worker's `_generate_run_reports()` passes `result.metrics` (which includes ARI/NMI after `_compute_clustering_metrics`) to these report generators.

The e2e test verifies ARI/NMI are present in both the run response metrics dict and the `/api/runs/{id}/metrics` endpoint.

### AC6: osmFISH dataset can be registered

PASS. Verified manually:
- File exists at `/home/wx/project/aaa/spatial-transcriptomic/经典算法/SDMBench/Data/osmfish.h5ad`
- `read_h5ad_to_bundle()` successfully reads it: 4839 spots, 33 genes
- Ground-truth labels from `obs['Region']` are loaded correctly
- The `register-real` endpoint accepts any h5ad path, so osmFISH can be registered via the same mechanism as STARmap

### AC7: test_io.py + test_e2e.py all all pass

PASS. All 97 tests pass (6 skipped for optional dependencies). test_io.py has 12 tests for the h5ad reader. test_e2e.py has TestRealDataBenchmarkFlow with the full end-to-end STARmap benchmark flow plus existing tests.

### AC8: CLI preserved

PASS. Verified:
- `list-tasks` returns all 5 task types
- `list-algorithms` returns all registered algorithms
- `cli.py` is unchanged from previous sprints

## No Login/RBAC Added

Verified: no authentication, login, RBAC, password, or token references exist in the API routes. The API remains open as designed.

## Files Verified

| File | Status |
|------|--------|
| `src/st_platform/io/h5ad_reader.py` | New, correct |
| `src/st_platform/io/__init__.py` | New |
| `src/st_platform/api/routes/datasets.py` | Modified, register-real added |
| `src/st_platform/api/schemas.py` | Modified, DatasetRegisterReal added |
| `src/st_platform/worker/runner.py` | Modified, h5ad loading + ARI/NMI |
| `src/st_platform/benchmark/metrics.py` | Modified, compute_ari/compute_nmi |
| `src/st_platform/benchmark/reports.py` | Modified, metrics in reports |
| `tests/test_io.py` | New, 12 tests |
| `tests/test_e2e.py` | Modified, TestRealDataBenchmarkFlow added |
| `src/st_platform/cli.py` | Unchanged, preserved |
