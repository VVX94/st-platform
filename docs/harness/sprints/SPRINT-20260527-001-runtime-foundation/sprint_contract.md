# Sprint Contract: Runtime Foundation

Sprint ID：SPRINT-20260527-001-runtime-foundation  
关联任务：TASK-20260527-001-runtime-smoke-platform  
状态：agreed

## 本轮目标

建立第一条可运行纵切链路的基础骨架：

1. FastAPI app 可启动，并提供 health check。
2. SQLite metadata store 可初始化。
3. 数据集、算法、experiment、run 的最小 API schema 明确。
4. SQLite queued runs 表和低并发 worker 轮询入口存在。
5. React/Vite app 可启动，并能显示基础导航和 API health 状态。
6. 文档记录如何本地启动 API、worker 和 Web。

## 明确不做

- 不做 Docker Compose。
- 不做 Postgres。
- 不做 Redis / Celery / RQ。
- 不做登录、用户、RBAC 或 API auth。
- 不要求真实 OSS 凭证可用；可以先实现 OSS storage interface 和 local dev backend。
- 不要求首轮完成 STARmap 真实运行，但必须为下一 sprint 留出明确接口。

## 预期改动文件

- `src/st_platform/api/`
- `src/st_platform/storage/`
- `src/st_platform/benchmark/`
- `src/st_platform/worker/`
- `web/`
- `tests/`
- `README.md` 或 `docs/harness/sprints/...`

## 用户可见行为

- 用户能启动 API 并访问 health endpoint。
- 用户能启动 Web 并看到平台首页/导航。
- Web 能显示 API health 状态。
- 用户能通过 API 查看已注册算法列表。

## API / 数据库 / 前端变更

API 最低要求：

- `GET /api/health`
- `GET /api/algorithms`
- `GET /api/datasets`
- `POST /api/datasets/register`
- `GET /api/experiments`
- `POST /api/experiments`
- `GET /api/runs`

SQLite 最低表：

- `datasets`
- `experiments`
- `runs`
- `metrics`
- `artifacts`

前端最低页面：

- Dashboard / runs overview。
- Datasets。
- Algorithms。
- Experiments。

## 验收测试

| 验收点 | 验证方式 | 必须通过 |
|---|---|---|
| API 可启动 | 启动 FastAPI 后访问 `/api/health` | 是 |
| SQLite 可初始化 | 运行 init 命令或 API 启动自动建表 | 是 |
| 算法列表可查询 | `GET /api/algorithms` 返回当前 registry 算法 | 是 |
| Web 可启动 | 启动 Vite dev server | 是 |
| Web 能读 API health | 页面显示 API 可用状态 | 是 |
| Worker 入口存在 | worker 可启动并轮询 queued runs，即使队列为空 | 是 |
| 测试记录完整 | generator handoff 和 evaluator report 写明命令与结果 | 是 |

## 回滚和兼容性

- 保留现有 CLI：`PYTHONPATH=src python3 -m st_platform list-tasks`、`list-algorithms`、`run-demo` 不能被破坏。
- 当前系统优先使用 `python3`，例如 `PYTHONPATH=src python3 -m st_platform list-algorithms`。
- 旧的 `LocalRunner` 和 algorithm registry 保持可用。
- 新增 Web/API 不应要求真实 OSS 凭证才能运行基础 health 和算法列表。

## Evaluator 审核意见

本 contract 可测。Evaluator 需要重点检查：

- CLI 是否仍可用。
- API/Web/worker 是否真的能启动。
- SQLite 文件是否被 `.gitignore` 排除。
- Docker 是否没有被误设为当前 sprint 必做项。
