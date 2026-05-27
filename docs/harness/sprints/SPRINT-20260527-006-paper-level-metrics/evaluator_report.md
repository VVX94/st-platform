# Evaluator Report: SPRINT-20260527-006-paper-level-metrics

**Evaluator**: Evaluator Agent
**Date**: 2026-05-27
**Sprint**: SPRINT-20260527-006-paper-level-metrics

---

## Test Results

- **Total tests**: 137 passed, 6 skipped, 0 failed
- **test_metrics.py**: 63 tests passed (37 new from this sprint)
- **test_e2e.py**: 6 tests passed (including real STARmap benchmark with new metrics)

---

## Acceptance Criteria Verification

### 1. HOM computed correctly (sklearn wrapper) -- PASS

`compute_homogeneity` at line 134 of `metrics.py` wraps `sklearn.metrics.homogeneity_score`. Tests: `TestHomogeneity` (4 tests) verify perfect match (1.0), permuted labels (1.0), random labels (<0.5), and single-class edge case (1.0).

### 2. COM computed correctly (sklearn wrapper) -- PASS

`compute_completeness` at line 156 of `metrics.py` wraps `sklearn.metrics.completeness_score`. Tests: `TestCompleteness` (4 tests) verify perfect match (1.0), permuted labels (1.0), random labels (<0.5), and single-cluster edge case (1.0).

### 3. ASW computed correctly (silhouette_score with subsampling) -- PASS

`compute_asw` at line 178 of `metrics.py` uses `sklearn.metrics.silhouette_score` with `metric="euclidean"`. Subsampling is implemented: when `n > sample_size`, a `RandomState(42)` selects a fixed subset. Edge cases handled: single spot returns 0.0, single label returns 0.0. Tests: `TestASW` (5 tests) verify well-separated clusters (>0.5), single spot, single label, range [-1,1], and subsampling.

### 4. CHAOS = 1 - spatial_neighbor_agreement -- PASS

`compute_chaos` at line 243 of `metrics.py` is a one-liner: `return 1.0 - compute_spatial_neighbor_agreement(labels, coordinates, k)`. Tests: `TestChaos` (4 tests) verify all-same-label (0.0), alternating labels (high), single spot (0.0), and range [0,1].

### 5. PAS = boundary spot fraction -- PASS

`compute_pas` at line 265 of `metrics.py` uses `_build_knn_neighbors` to find k-NN, then counts spots where at least one neighbor has a different label, divided by n. Tests: `TestPAS` (4 tests) verify all-same-label (0.0), checkerboard pattern (high), single spot (0.0), and two adjacent clusters (between 0 and 1).

### 6. Moran's I with k-NN weights, range [-1,1] -- PASS

`compute_morans_i` at line 301 of `metrics.py` implements the formula:
```
I = (n / S0) * sum_ij(wij * zi * zj) / sum_i(zi^2)
```
where z = labels - mean(labels), S0 = n*k, and binary k-NN weights. String labels are encoded via `LabelEncoder`. The cross term is computed as `sum_i(zi * sum_{j in N(i)} zj)`. This matches the standard Moran's I formula. Tests: `TestMoransI` (6 tests) verify all-same-label (0.0 due to zero variance), spatial autocorrelation (>0.5), random labels (near zero), single spot, string label encoding, and range.

### 7. Geary's C with k-NN weights, range [0,2] -- PASS

`compute_gearys_c` at line 358 of `metrics.py` implements the formula:
```
C = (n-1) / (2*S0) * sum_ij(wij * (zi - zj)^2) / sum_i(zi^2)
```
where z = labels - mean(labels), S0 = n*k, and binary k-NN weights. String labels encoded via `LabelEncoder`. The diff-squared sum is computed as `sum_i sum_{j in N(i)} (zi - zj)^2`. This matches the standard Geary's C formula. Tests: `TestGearysC` (6 tests) verify all-same-label (0.0), spatial autocorrelation (<1.0), random labels (near 1.0), single spot, string labels, and range [0,2].

### 8. memory_peak_mb via tracemalloc -- PASS

`runner.py` lines 300-316 implement memory tracking:
- `tracemalloc.start()` before `runner.execute()`
- `tracemalloc.get_traced_memory()` after execution (both success and failure paths)
- `tracemalloc.stop()` called in both paths
- `peak_bytes / (1024 * 1024)` stored as `memory_peak_mb` in result metrics

### 9. Worker integration: real run produces all metrics -- PASS

`runner.py` `_compute_clustering_metrics` (line 131) calls `compute_all_metrics` from the benchmark metrics module. In `poll_runs` (line 300+):
- `tracemalloc` wraps execution for memory tracking
- `memory_peak_mb` is added to result_metrics
- `_compute_clustering_metrics` is called when ground-truth labels are available
- `compute_all_metrics` computes: ARI, NMI, HOM, COM, spatial_neighbor_agreement, chaos, PAS, Moran's I, Geary's C, and ASW (when features available)

The E2E test `test_real_starmap_benchmark_flow` verifies all new metrics are present in a real run: homogeneity, completeness, chaos, pas, morans_i, gearys_c, memory_peak_mb.

### 10. test_metrics.py all pass -- PASS

63 tests pass in test_metrics.py (37 new from this sprint):
- TestHomogeneity: 4 tests
- TestCompleteness: 4 tests
- TestASW: 5 tests
- TestChaos: 4 tests
- TestPAS: 4 tests
- TestMoransI: 6 tests
- TestGearysC: 6 tests
- TestComputeAllMetrics: 4 tests

---

## Metric Categorization in reports.py

`_METRIC_CATEGORIES` in `reports.py` (line 124) correctly categorizes:
- **label_dependent**: ari, nmi, homogeneity, completeness
- **spatial**: spatial_neighbor_agreement, chaos, pas, morans_i, gearys_c
- **general**: asw, runtime_seconds, memory_peak_mb, artifact_completeness

All new metrics are properly categorized.

---

## Overall Verdict

**ALL 10 ACCEPTANCE CRITERIA: PASS**
