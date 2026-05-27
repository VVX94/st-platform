# Evaluator Report: Runtime Foundation

关联 sprint：SPRINT-20260527-001-runtime-foundation
评估日期：2026-05-27
结论：passed

## 验证环境

- OS: Linux 6.8.0-106-generic
- Python: 3.10.12
- Node: (available, npm install succeeded)
- Working directory: /home/wx/project/aaa/spatial-transcriptomic/经典算法/st-platform

## Contract 覆盖检查

| 验收点 | 结果 | 证据 |
|---|---|---|
| 1. API 可启动 | PASS | `PYTHONPATH=src python3 -m uvicorn st_platform.api.app:create_app --factory --host 0.0.0.0 --port 18765` starts successfully. `Application startup complete.` confirmed. |
| 2. SQLite 可初始化 | PASS | `init_db()` creates all 5 tables: datasets, experiments, runs, metrics, artifacts. Verified via `sqlalchemy.inspect(engine).get_table_names()`. |
| 3. 算法列表可查询 | PASS | `GET /api/algorithms` returns 200 with 10 algorithms: demo-qc, mock-domain, ccst, const, deepst, graphst, sedr, spagcn, spagcn-lite, mock-deconv. |
| 4. Web 可启动 | PASS | `cd web && npm install && npx vite` starts Vite dev server on port 5173. `VITE v5.4.21 ready in 107 ms` confirmed. |
| 5. Web 能读 API health | PASS | `Dashboard.tsx` fetches `/api/health` on mount and displays `health.status` ("ok") and `health.version` ("0.1.0"). Shows "API unreachable" on error. |
| 6. Worker 入口存在 | PASS | `poll_runs()` in `worker/runner.py` returns 0 for empty queue. 4 worker tests pass: empty queue, process queued run, unknown algorithm, unknown task type. |
| 7. 测试记录完整 | PASS | `generator_handoff.md` documents all commands and results. This evaluator report provides independent verification. |

## UI 检查

- `web/package.json` has React 18, react-router-dom 6, Vite 5, TypeScript 5.
- `web/vite.config.ts` proxies `/api` to `http://localhost:8000`.
- `web/src/App.tsx` has BrowserRouter with 4 routes: Dashboard, Datasets, Algorithms, Experiments.
- `web/src/pages/Dashboard.tsx` fetches `/api/health`, `/api/algorithms`, `/api/datasets`, `/api/experiments` and displays summary cards.
- `web/src/api/client.ts` provides `api.get()` and `api.post()` fetch wrappers.
- No login, auth, or RBAC UI elements found.

## API 检查

- `src/st_platform/api/app.py`: `create_app()` factory with `lifespan` that calls `init_db()` on startup.
- `src/st_platform/api/routes/health.py`: `GET /api/health` returns `HealthResponse(status="ok", version="0.1.0")` -- 200 OK.
- `src/st_platform/api/routes/algorithms.py`: `GET /api/algorithms` returns `List[AlgorithmOut]` from `PlatformService.list_algorithms()` which reads from the in-memory registry.
- `src/st_platform/api/routes/datasets.py`: CRUD for datasets.
- `src/st_platform/api/routes/experiments.py`: CRUD for experiments.
- `src/st_platform/api/routes/runs.py`: List/get runs.
- 15 total routes registered via `api_router`.
- No auth middleware, no JWT, no login routes.

## Worker / 数据库 / Artifact 检查

- `src/st_platform/storage/database.py`: SQLAlchemy engine with SQLite, WAL mode, foreign keys enabled. `init_db()` imports models and calls `Base.metadata.create_all()`.
- `src/st_platform/storage/models.py`: 5 ORM models -- DatasetModel, ExperimentModel, RunModel, MetricModel, ArtifactModel. All with UUID primary keys, timestamps, and proper foreign keys.
- `src/st_platform/storage/repositories.py`: DatasetRepo, ExperimentRepo, RunRepo, MetricRepo, ArtifactRepo with full CRUD.
- `src/st_platform/worker/runner.py`: `poll_runs()` queries queued runs, marks running, executes via LocalRunner, writes results back. Handles empty queue (returns 0), unknown algorithm (marks failed), unknown task type (marks failed).
- `scripts/start_worker.sh`: Polls every 5 seconds in a loop.

## 测试结果

```
$ PYTHONPATH=src python3 -m pytest tests/ -x -v
39 passed, 6 skipped in 1.00s
```

Test breakdown:
- `test_api.py`: 12 tests (health, algorithms, datasets, experiments, runs)
- `test_storage.py`: 10 tests (DB init, dataset CRUD, experiment CRUD, run CRUD)
- `test_worker.py`: 4 tests (empty queue, process run, unknown algo, unknown task)
- `test_cli.py`: 8 tests (algorithm-specific demo defaults)
- `test_registry.py`: 2 tests (filtering, default tasks)
- `test_runner.py`: 9 tests (6 skipped for real backends, 3 passed for demo/mock)

CLI verification:
```
$ PYTHONPATH=src python3 -m st_platform list-algorithms
# Returns 10 algorithms (JSON output)
```

## 发现的问题

| 严重级别 | 问题 | 证据 | 建议 |
|---|---|---|---|
| INFO | `algorithms` table not in SQLite; served from in-memory registry | By design per handoff note #2 | Acceptable for Phase 1; document in architecture |
| INFO | Frontend requires `npm install` before first run | `web/node_modules/` not committed (correct) | Document in README; `start_web.sh` handles this |
| INFO | `st_platform.db` created at runtime but gitignored | `.gitignore` includes `*.db` | No action needed |
| INFO | Generator handoff claims "39 passed, 6 skipped" | Actual: 39 passed, 6 skipped | Matches exactly |

## Hard-fail 条件检查

| 条件 | 结果 |
|---|---|
| Core user flow does not run | NOT VIOLATED -- API starts, health works, algorithms queryable |
| UI reports success while backend run failed | NOT VIOLATED -- UI correctly shows error on API failure |
| Generated files or intermediate artifacts committed to Git | NOT VIOLATED -- no .db, node_modules, __pycache__ tracked |
| Sprint lacks verifiable commands, handoff notes, or acceptance evidence | NOT VIOLATED -- handoff.md exists with commands and results |
| Implementation adds login/RBAC/API auth | NOT VIOLATED -- no auth middleware or login routes found |

## 最终结论

SPRINT-20260527-001-runtime-foundation PASSES all 7 acceptance criteria. No hard-fail conditions triggered. The Generator delivered a working vertical slice: FastAPI backend with SQLite storage, algorithm registry integration, worker polling, and React/Vite frontend with API health display. All 39 tests pass. CLI remains functional.
