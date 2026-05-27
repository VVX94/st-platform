# Decision: SQLite Queued Runs 与低并发 Worker

日期：2026-05-27  
状态：accepted  
关联文档：`docs/benchmark_platform_design_plan.md`

## 背景

平台首期需要部署到资源敏感的阿里云单机环境。为了减少常驻服务数量和部署复杂度，用户确认 worker/队列先采用 SQLite queued runs + 低并发 worker 轮询，后续再迁移 Redis/Celery 等独立队列。

## 决策

首期采用：

- SQLite `runs` 表保存队列状态。
- FastAPI 只负责创建 queued run 和查询状态。
- worker 轮询 queued runs。
- 默认单 worker 顺序执行。
- artifact 写入 OSS。
- 本地只使用可清理临时目录。

暂不采用：

- Redis。
- Celery / RQ / Arq。
- Kubernetes job。
- 多 worker 并发调度。

## 运行要求

- worker 应记录 `worker_id`、`heartbeat_at`、`attempt`、`started_at`、`finished_at`。
- worker 异常退出后，重启时应识别 stale running runs。
- 单个 run 失败不影响其他 queued runs。
- 任务结束后必须清理本地临时目录。
- 运行日志和 artifact manifest 需要可追踪到 OSS URI。

## 升级路径

- 队列从 SQLite 轮询迁移到 Redis + RQ/Celery/Arq。
- 元数据从 SQLite 迁移到 Postgres。
- 重型算法迁移到独立 runner 镜像或集群任务。

