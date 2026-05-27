---
description: Start or resume the long-running ST Platform benchmark implementation harness.
---

Start or resume long-running ST Platform benchmark implementation.

Follow this order:

1. Read `CLAUDE.md`.
2. Read `docs/benchmark_platform_design_plan.md`.
3. Read `docs/harness/agent_coding_governance.md`.
4. Read latest files in `docs/harness/decisions/` and `docs/harness/sessions/`.
5. Read `docs/harness/tasks/TASK-20260527-001-runtime-smoke-platform/task_spec.md`.
6. Read `docs/harness/sprints/SPRINT-20260527-001-runtime-foundation/sprint_contract.md`.
7. Use the `planner` subagent first only if the task spec or sprint contract needs revision.
8. Use the `generator` subagent to implement the approved sprint contract.
9. Use the `evaluator` subagent after implementation to verify the running app.
10. Keep Docker packaging out of scope until the main app runs end to end.
11. End every sprint with updated harness docs and a Git commit.

Current north star:

Make the app run correctly first:

- FastAPI backend starts.
- React/Vite frontend starts.
- SQLite metadata store works.
- OSS-backed dataset/artifact flow is designed and testable.
- SQLite queued worker can run a STARmap smoke benchmark.
- Report and visualization artifacts can be viewed from Web.
