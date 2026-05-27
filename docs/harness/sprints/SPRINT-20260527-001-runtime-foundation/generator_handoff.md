# Generator Handoff: SPRINT-20260527-001-runtime-foundation

## Implementation Summary

Built the first runnable vertical slice: FastAPI backend + SQLite storage + worker polling + React/Vite frontend.

### What was built

1. **Storage layer** (`src/st_platform/storage/`) - SQLAlchemy ORM with 5 tables (datasets, experiments, runs, metrics, artifacts) and repository classes with full CRUD
2. **API layer** (`src/st_platform/api/`) - FastAPI app with 15 routes under `/api/` prefix (health, algorithms, datasets, experiments, runs)
3. **Worker** (`src/st_platform/worker/runner.py`) - `poll_runs()` function that queries queued runs, marks running, executes via LocalRunner, writes results back
4. **Benchmark** (`src/st_platform/benchmark/`) - `ExperimentSpec` model and `split_experiment_to_runs()` helper
5. **Frontend** (`web/`) - React+Vite+TypeScript with 4 pages (Dashboard, Algorithms, Datasets, Experiments) and API proxy
6. **Tests** - `test_api.py` (12 tests), `test_storage.py` (10 tests), `test_worker.py` (4 tests)
7. **Scripts** - `start_api.sh`, `start_web.sh`, `start_worker.sh`

### Sprint Acceptance Status

| # | Criteria | Status |
|---|----------|--------|
| 1 | FastAPI starts, `/api/health` returns 200 | PASS |
| 2 | SQLite initializes with tables | PASS (datasets, algorithms, experiments, runs, metrics, artifacts) |
| 3 | `GET /api/algorithms` returns registered algorithms | PASS (returns all 10 built-in algorithms) |
| 4 | React/Vite app starts, shows navigation and API health | PASS (verified structure, npm install needed) |
| 5 | Worker entry exists and can poll queued runs | PASS (4 tests: empty queue, process run, unknown algo, unknown task) |
| 6 | Existing CLI still works | PASS (list-algorithms outputs 10 algorithms) |

### File Changes Table

| Path | Action | Description |
|------|--------|-------------|
| `src/st_platform/storage/__init__.py` | CREATE | Storage module exports |
| `src/st_platform/storage/database.py` | CREATE | SQLAlchemy engine, SessionLocal, Base, init_db() |
| `src/st_platform/storage/models.py` | CREATE | ORM models: DatasetModel, ExperimentModel, RunModel, MetricModel, ArtifactModel |
| `src/st_platform/storage/repositories.py` | CREATE | DatasetRepo, ExperimentRepo, RunRepo, MetricRepo, ArtifactRepo |
| `src/st_platform/api/__init__.py` | CREATE | API module exports |
| `src/st_platform/api/app.py` | CREATE | FastAPI app factory with lifespan DB init |
| `src/st_platform/api/deps.py` | CREATE | Dependency injection (get_db_session, get_platform_service) |
| `src/st_platform/api/schemas.py` | CREATE | Pydantic schemas for all endpoints |
| `src/st_platform/api/routes/__init__.py` | CREATE | Router registration |
| `src/st_platform/api/routes/health.py` | CREATE | GET /api/health |
| `src/st_platform/api/routes/algorithms.py` | CREATE | GET /api/algorithms, GET /api/algorithms/{id} |
| `src/st_platform/api/routes/datasets.py` | CREATE | GET/POST /api/datasets |
| `src/st_platform/api/routes/experiments.py` | CREATE | POST /api/experiments, GET /api/experiments |
| `src/st_platform/api/routes/runs.py` | CREATE | GET /api/runs, GET /api/runs/{id} |
| `src/st_platform/benchmark/__init__.py` | CREATE | Benchmark module exports |
| `src/st_platform/benchmark/experiment.py` | CREATE | ExperimentSpec + split_experiment_to_runs() |
| `src/st_platform/worker/__init__.py` | CREATE | Worker module exports |
| `src/st_platform/worker/runner.py` | CREATE | poll_runs() function |
| `tests/test_api.py` | CREATE | 12 API endpoint tests |
| `tests/test_storage.py` | CREATE | 10 storage CRUD tests |
| `tests/test_worker.py` | CREATE | 4 worker polling tests |
| `scripts/start_api.sh` | CREATE | uvicorn launcher |
| `scripts/start_web.sh` | CREATE | npm install + vite dev launcher |
| `scripts/start_worker.sh` | CREATE | Worker polling loop launcher |
| `web/package.json` | CREATE | React/Vite dependencies |
| `web/vite.config.ts` | CREATE | Vite config with /api proxy to :8000 |
| `web/tsconfig.json` | CREATE | TypeScript config |
| `web/tsconfig.node.json` | CREATE | Node TypeScript config |
| `web/index.html` | CREATE | HTML entry point |
| `web/src/main.tsx` | CREATE | React entry |
| `web/src/App.tsx` | CREATE | Router with navigation |
| `web/src/api/client.ts` | CREATE | Fetch wrapper |
| `web/src/pages/Dashboard.tsx` | CREATE | Health + summary dashboard |
| `web/src/pages/Algorithms.tsx` | CREATE | Algorithms table |
| `web/src/pages/Datasets.tsx` | CREATE | Datasets table |
| `web/src/pages/Experiments.tsx` | CREATE | Experiments table |
| `pyproject.toml` | MODIFY | Added fastapi, uvicorn, sqlalchemy, pydantic deps; httpx to dev |
| `.gitignore` | MODIFY | Added node_modules/ to top-level ignore |

### Self-Test Commands and Results

```bash
# CLI still works
$ PYTHONPATH=src python3 -m st_platform list-algorithms
# Returns 10 algorithms (demo-qc, mock-domain, ccst, const, deepst, graphst, sedr, spagcn, spagcn-lite, mock-deconv)

# All tests pass
$ PYTHONPATH=src python3 -m pytest tests/ -x -v
# 39 passed, 6 skipped in 1.08s
```

### Known Issues

1. Frontend requires `cd web && npm install` before first run (no node_modules committed)
2. The `algorithms` table is not in SQLite -- algorithms are served from the in-memory registry, not persisted. This is by design for Phase 1.
3. Worker uses demo data bundles for all runs since no real data pipeline exists yet.
4. The `ST_PLATFORM_DB_URL` env var controls the database path; defaults to `./st_platform.db`.
