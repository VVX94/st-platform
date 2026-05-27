# Evaluator Report: SPRINT-20260527-003-metrics-reports

Date: 2026-05-27
Evaluator: automated

## Test Results

All 73 tests pass (6 skipped). The skipped tests are for real backend integrations (CCST, ConST, DeepST, GraphST, SEDR, SpaGCN) that require external dependencies not available in the test environment -- this is expected and unrelated to this sprint.

## Acceptance Criterion Evaluation

### AC #1: spatial_neighbor_agreement, runtime, artifact_completeness computed correctly -- PASS

Source: `src/st_platform/benchmark/metrics.py`
Tests: `tests/test_metrics.py` (13 tests, all pass)

- `compute_spatial_neighbor_agreement(labels, coordinates, k)`: Uses pairwise Euclidean distances, k-NN, returns fraction of matching labels in [0,1]. Handles edge cases: single spot, two spots, k > n-1 (clamped). 7 tests cover identical labels, two clusters, alternating labels, single/two spots, k overflow, and range validation.
- `compute_artifact_completeness(artifacts, required_kinds)`: Returns fraction of required kinds present. Handles empty inputs gracefully (returns 1.0 for empty required). 6 tests cover all present, partial, none, empty required, empty both, empty artifacts with nonempty required.
- `compute_runtime_seconds(started_at, finished_at)`: Returns `total_seconds()` delta. 3 tests cover normal, zero, and negative delta.

### AC #2: run_metrics.csv and domain_predictions.csv generated -- PASS

Source: `src/st_platform/benchmark/reports.py` (`generate_run_metrics_csv`, `generate_domain_predictions_csv`)
Tests: `tests/test_reports.py` (5 tests across 2 classes, all pass)

- `generate_run_metrics_csv`: Writes CSV with columns [run_id, algorithm_id, metric_name, metric_value]. Creates parent directories. Tested with valid data, empty metrics, and nested paths.
- `generate_domain_predictions_csv`: Writes CSV with columns [spot_id, domain, x, y]. Creates parent directories. Tested with valid data and empty domains.
- Both are called from `worker/runner.py::_generate_run_reports` after successful run completion.

### AC #3: domain_grid.png and metrics_bar.png generated -- PASS

Source: `src/st_platform/benchmark/reports.py` (`generate_domain_grid_plot`, `generate_metrics_bar_plot`)
Tests: `tests/test_reports.py` (4 tests across 2 classes, all pass)

- `generate_domain_grid_plot`: Scatter plot colored by domain label, with colorbar, axis labels, inverted y-axis. Creates placeholder image for empty data.
- `generate_metrics_bar_plot`: Bar chart with value labels. Creates placeholder for empty metrics.
- Both produce valid PNG files (size > 0 verified in tests).
- Both are called from `worker/runner.py::_generate_run_reports`.

### AC #4: report.md generated with complete content -- PASS

Source: `src/st_platform/benchmark/reports.py` (`generate_markdown_report`, `generate_experiment_report`)
Tests: `tests/test_reports.py` (4 tests including integration test, all pass)

- `generate_markdown_report`: Produces Markdown with experiment header (ID, status, task type, run count), summary table (run ID, algorithm, status, metrics), and per-run details (status, error, metrics table, artifacts table).
- `generate_experiment_report`: Orchestrates all report generation -- aggregate CSV, per-run CSVs, bar plots, domain predictions CSV, domain grid plots, and Markdown report. Tested with a real SQLite database in `test_generate_full_report`.
- Content verified: experiment name, algorithm ID, and metric names appear in output.

### AC #5: Report files recorded as artifacts in SQLite -- PASS

Source: `src/st_platform/worker/runner.py` (`_generate_run_reports`)
Tests: `tests/test_e2e.py::test_full_benchmark_flow` (artifacts verified via API)

- `_generate_run_reports` creates `ArtifactModel` entries for each generated report:
  - `kind="metrics_csv"` for the metrics CSV
  - `kind="metrics_bar_plot"` for the bar chart
  - `kind="domain_predictions_csv"` for the domain CSV
  - `kind="domain_grid_plot"` for the domain grid plot
- All artifacts committed to SQLite in a single transaction with rollback on failure.
- E2E test verifies artifacts are retrievable via `GET /api/runs/{run_id}/artifacts`.

### AC #6: GET /api/experiments/{id}/report returns summary -- PASS

Source: `src/st_platform/api/routes/experiments.py` (lines 130-197)
Schema: `src/st_platform/api/schemas.py` (`ExperimentReportOut`)

- Endpoint registered at `GET /api/experiments/{experiment_id}/report`.
- Returns `ExperimentReportOut` with: experiment_id, name, status, task_type, runs (list of RunOut), metrics_summary (per-metric avg/min/max/count), artifacts (list of ArtifactOut).
- Metrics summary aggregation computes avg, min, max, count across all runs for each metric name.
- 404 handling for nonexistent experiment.
- No direct API-level test for this endpoint exists (only the underlying `generate_experiment_report` function is tested in `test_reports.py`).

### AC #7: Frontend Reports page shows metrics and download links -- FAIL

Source: expected at `web/src/pages/Reports.tsx` (per sprint contract)

- The `frontend/` and `web/` directories do not exist in the repository.
- No React/TypeScript files exist anywhere in the project.
- No frontend code was delivered in this sprint.
- The sprint contract specifies `web/src/pages/Reports.tsx`, `web/src/App.tsx`, and `web/src/api/client.ts` as expected changes -- none were created.

### AC #8: test_metrics.py + test_reports.py all pass -- PASS

- `tests/test_metrics.py`: 13 tests, all pass
- `tests/test_reports.py`: 12 tests (including 2 integration tests with real SQLite), all pass
- Total test suite: 73 passed, 6 skipped, 0 failures

## No Login/RBAC Added

Verified: grep for "login", "auth", "rbac", "permission", "token", "jwt" across all source files returns zero matches. No authentication or authorization was introduced.

## Issues Found

1. **Missing frontend (AC #7)**: The Reports frontend page was not delivered. This is a required acceptance criterion.

2. **No API-level test for report endpoint (AC #6)**: While `GET /api/experiments/{id}/report` is implemented and the underlying `generate_experiment_report` function is tested, there is no test that exercises the HTTP endpoint itself (e.g., via TestClient). The e2e test (`test_e2e.py`) tests metrics and artifacts endpoints but not the report endpoint.

## Verdict

**7 of 8 acceptance criteria passed. 1 failed (AC #7: frontend Reports page).**
