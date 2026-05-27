# ST Platform Claude Code Guide

This repository is the ST Platform benchmark project.

## Current Goal

Make the project run correctly first. Docker Compose and image packaging are deferred until the core app works end to end.

The first running slice is:

```text
React/Vite Web -> FastAPI API -> SQLite metadata -> SQLite queued runs
-> worker -> OSS-backed artifacts -> Web report view
```

Use STARmap as the smoke demo dataset. DLPFC 151673 and osmFISH are registration/metadata targets first; full benchmark runs can follow later.

## Authoritative Docs

Read these before planning or coding:

1. `docs/benchmark_platform_design_plan.md`
2. `docs/harness/agent_coding_governance.md`
3. `docs/harness/project_structure_map.md`
4. `docs/harness/decisions/`
5. The current task/sprint files under `docs/harness/tasks/` and `docs/harness/sprints/`

## Confirmed Decisions

- Public anonymous research website: no login, users, RBAC, or API auth.
- Backend: FastAPI + Pydantic.
- SQLite access: SQLAlchemy or SQLModel, not raw `sqlite3`.
- Storage: SQLite metadata + Aliyun OSS data/artifact URIs.
- Queue: SQLite queued runs + low-concurrency worker polling.
- Frontend: React + Vite + TypeScript.
- Metrics: `core_spatial_v1` = ARI, NMI, runtime, spatial neighbor agreement, artifact completeness.
- Docker: defer packaging until main app works; later keep images small and do not bake data/artifacts/checkpoints into images.

## Harness Workflow

Use project subagents in `.claude/agents/`:

- `planner`: scope, task spec, sprint contract, acceptance criteria.
- `generator`: implement one approved sprint contract.
- `evaluator`: verify independently and write evaluator report.

Start with:

- `docs/harness/tasks/TASK-20260527-001-runtime-smoke-platform/task_spec.md`
- `docs/harness/sprints/SPRINT-20260527-001-runtime-foundation/sprint_contract.md`

Every sprint must leave:

- task spec or linked task
- sprint contract
- generator handoff
- evaluator report
- acceptance status
- artifact/data manifests when applicable
- Git commit

Generated datasets, run outputs, plots, CSV/JSON reports, SQLite files, caches, and checkpoints must not be committed.

## Python Environment

This project uses **uv** as the primary Python environment and package manager.

Rules:

1. Use `uv` to create and manage virtual environments (`uv venv`, `uv pip install`).
2. Pin Python version with a `.python-version` file when creating a new environment.
3. Do not use `conda`, `pipenv`, `poetry`, or raw `venv` + `pip` unless uv is unavailable on the target machine.
4. If uv is unavailable, fall back to standard `python -m venv` + `pip install -e .[dev]`.
5. Never mix package managers in the same environment.

Typical workflow:

```bash
# Install uv (if not present)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create environment
uv venv .venv --python 3.11

# Install project + dev dependencies
uv pip install -e ".[dev]" --cache-dir /tmp/uv-cache

# Run tests
PYTHONPATH=src .venv/bin/python -m pytest
```

## Useful Commands

Current Python package smoke checks:

```bash
PYTHONPATH=src python3 -m pytest
PYTHONPATH=src python3 -m st_platform list-tasks
PYTHONPATH=src python3 -m st_platform list-algorithms
PYTHONPATH=src python3 -m st_platform run-demo --task domain_detection --algorithm spagcn-lite
```

Use the existing uv environment if needed:

```bash
UV_CACHE_DIR=/tmp/uv-cache .venv-spagcn/bin/python -m st_platform list-algorithms
```
