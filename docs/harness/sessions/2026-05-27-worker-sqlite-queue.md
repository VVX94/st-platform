# Session: SQLite queued runs worker decision

日期：2026-05-27  
参与角色：Planner  
关联任务：确认 worker/队列首期方案

## 用户请求

用户确认 worker/队列正式按 SQLite queued runs + 低并发 worker 轮询起步，后续再迁移 Redis/Celery。同时要求后续几条建议一次性发出，待用户一次性回复后再一次性修改文档。

## 本轮上下文

- 当前部署目标是阿里云轻量单机 Docker Compose。
- 数据和 artifact 主存储是 OSS。
- 当前数据库是 SQLite，后续迁移 Postgres。
- Docker 镜像需要轻量，避免引入过多常驻服务。

## 执行动作

| 步骤 | 动作 | 文件/命令 | 结果 |
|---|---|---|---|
| 1 | 读取 Worker 章节 | `sed -n '500,555p' docs/benchmark_platform_design_plan.md` | 找到现有单 worker 设计 |
| 2 | 更新 Worker 章节 | `docs/benchmark_platform_design_plan.md` | 写入 SQLite queued runs、OSS artifact、本地临时清理和升级路径 |
| 3 | 新增决策记录 | `docs/harness/decisions/2026-05-27-worker-sqlite-queue.md` | 记录 worker/队列首期决策 |
| 4 | 新增会话记录 | `docs/harness/sessions/2026-05-27-worker-sqlite-queue.md` | 记录本轮操作和后续确认要求 |

## 修改文件

| 文件 | 修改类型 | 说明 |
|---|---|---|
| `docs/benchmark_platform_design_plan.md` | 修改 | Worker 设计升级为 SQLite queued runs + 低并发轮询 |
| `docs/harness/decisions/2026-05-27-worker-sqlite-queue.md` | 新增 | worker/队列架构决策 |
| `docs/harness/sessions/2026-05-27-worker-sqlite-queue.md` | 新增 | 本轮审计记录 |

## 验证记录

| 命令/检查 | 结果 | 备注 |
|---|---|---|
| `rg "SQLite queued runs|低并发|worker_id|heartbeat_at|temp_dir|Redis|Celery" docs/benchmark_platform_design_plan.md docs/harness/decisions/2026-05-27-worker-sqlite-queue.md` | 通过 | 检查 worker/队列关键设计 |
| `git commit -- docs/benchmark_platform_design_plan.md docs/harness/decisions/2026-05-27-worker-sqlite-queue.md docs/harness/sessions/2026-05-27-worker-sqlite-queue.md` | 通过 | 创建本轮审计提交；提交哈希见最终回复 |

## 决策

- 首期队列使用 SQLite queued runs。
- worker 默认低并发，首期顺序执行。
- Redis/Celery/RQ 作为后续升级。
- worker 必须清理本地临时目录。

## 风险和阻塞

- SQLite 轮询适合首期低并发，不适合未来高并发。
- 需要在实现阶段控制 worker 轮询频率，避免无意义 CPU 占用。

## 下一步

提交本轮 Git 快照，然后一次性给用户列出后续待确认建议。
