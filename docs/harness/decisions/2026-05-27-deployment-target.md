# Decision: 阿里云单机 Docker Compose 部署目标

日期：2026-05-27  
状态：accepted  
关联文档：`docs/benchmark_platform_design_plan.md`

## 背景

benchmark 平台最终目标不是本地脚本或一次性 demo，而是可以部署到 Web 环境的完整可用项目。用户确认最终部署目标面向阿里云服务器，同时要求规划阶段注意初期测试环境资源有限，但不要把临时测试服务器的具体规格写入项目文档。

## 决策

采用单机 Docker Compose 作为首个可部署目标：

- `web`：React 静态资源和 Nginx 反向代理。
- `api`：FastAPI 后端。
- `worker`：后台 benchmark 任务执行。
- `postgres`：生产元数据存储。
- `redis`：任务队列和短期状态。
- `artifact volume`：运行产物、报告、图表和日志。

开发模式可以继续支持 SQLite 和本地 worker，但最终 Web 部署目标以 Postgres + Redis + Docker Compose 为准。

## 资源策略

- 按小资源单机优先设计，不把长任务放进 API 请求线程。
- worker 默认低并发，先保证可控、可恢复、可诊断。
- smoke test 使用小型数据和低成本参数。
- 真实 benchmark 通过队列后台执行。
- 不在项目文档中固化临时测试服务器的具体规格。

## 影响

- `docs/benchmark_platform_design_plan.md` 的首版范围需要包含 Docker Compose 部署骨架、Postgres、Redis 和 artifact volume。
- 后续 Generator 实现部署相关 sprint 时，应创建 `deploy/` 目录和 `.env.example`。
- Evaluator 在部署 sprint 中必须验证 Compose 服务启动、健康检查、API 可访问、worker 可消费任务、artifact volume 可写。

## 未决问题

- 是否在第一阶段就实现完整鉴权。
- 是否引入对象存储作为 artifact backend。
- 是否为算法 runner 进一步做容器隔离。

