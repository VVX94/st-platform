---
description: Start or resume the ST Platform Planner -> Generator -> Evaluator implementation harness.
---

Start or resume ST Platform benchmark platform implementation.

## Startup Context

Read these files first:

1. Read `CLAUDE.md`.
2. Read `docs/harness/README.md`.
3. Read `docs/benchmark_platform_design_plan.md`.
4. Read `docs/harness/agent_coding_governance.md`.
5. Read `docs/harness/project_structure_map.md`.
6. Read the latest files under `docs/harness/decisions/`.
7. Read the latest files under `docs/harness/sessions/`.
8. Read the latest files under `docs/harness/reviews/`.
9. Read task status files under `docs/harness/tasks/**/status.md`.

Do not assume the first sprint is current. Completed sprint contracts are historical evidence, not the active work item.

## Harness Flow

Use the three agents in this order:

1. Use the `planner` subagent to choose exactly one next work point.
2. If no active sprint contract exists for that work point, have `planner` create one under `docs/harness/sprints/`.
3. Use the `generator` subagent to implement only that approved sprint contract.
4. Use the `evaluator` subagent to independently verify the implementation.
5. If evaluation fails, plan the smallest follow-up fix sprint instead of broad refactoring.

Every sprint must end with:

- Updated session record in `docs/harness/sessions/`.
- Generator handoff in the sprint directory.
- Evaluator report and acceptance status in the sprint directory.
- Relevant tests or smoke commands recorded with results.
- A Git commit containing only source/docs intended for version control.

Do not commit generated datasets, reports, plots, CSV/JSON artifacts, local databases, `runs/`, `web/dist/`, `node_modules/`, caches, virtualenvs, or uploaded data.

## Current Default Priority

If there is no newer user instruction and no active sprint, start with the highest-priority gap from:

- `docs/harness/reviews/2026-05-27-current-project-code-review.md`

Current recommended next sprint:

`SPRINT-20260527-007-artifact-access-report-preview`

Goal:

- Fix the broken Reports artifact flow.
- Add backend artifact download/preview API.
- Stop exposing server absolute paths to the frontend.
- Make Web reports show generated plots and download CSV artifacts.
- Add API tests and, if feasible in the environment, Playwright or equivalent frontend smoke coverage.

Current north star:

Make the app become a deployable Web benchmark platform:

- FastAPI backend starts.
- React/Vite frontend starts.
- SQLite metadata store works.
- SQLite queued worker can run benchmark jobs.
- Data and benchmark artifacts are designed for OSS-backed storage.
- Report and visualization artifacts can be viewed and downloaded from Web.
- Agent work remains auditable through task, sprint, session, handoff, review, and commit records.

Docker packaging remains out of scope until the main app works end to end through Web/API/worker/artifact flows.
