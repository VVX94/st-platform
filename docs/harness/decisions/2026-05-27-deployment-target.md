# Decision: 阿里云单机 Docker Compose 部署目标

日期：2026-05-27  
状态：accepted，已被 `2026-05-27-storage-oss-sqlite.md` 修正存储和数据库细节  
关联文档：`docs/benchmark_platform_design_plan.md`

## 背景

benchmark 平台最终目标不是本地脚本或一次性 demo，而是可以部署到 Web 环境的完整可用项目。用户确认最终部署目标面向阿里云服务器，同时要求规划阶段注意初期测试环境资源有限，但不要把临时测试服务器的具体规格写入项目文档。

## 决策

采用单机 Docker Compose 作为首个可部署目标：

- `web`：React 静态资源和 Nginx 反向代理。
- `api`：FastAPI 后端。
- `worker`：后台 benchmark 任务执行。
- `sqlite`：当前元数据存储。
- `oss`：数据集、运行产物、报告、图表和模型权重主存储。
- `local temp`：运行期小型临时缓存，任务结束后清理。

当前 Web 部署目标以 SQLite + OSS + 轻量 Docker Compose 为准。Postgres 和 Redis 作为后续升级路径，不进入首期部署默认依赖。

## 资源策略

- 按小资源单机优先设计，不把长任务放进 API 请求线程。
- worker 默认低并发，先保证可控、可恢复、可诊断。
- smoke test 使用小型数据和低成本参数。
- 真实 benchmark 通过队列后台执行。
- 服务器本地不保存大型数据和 artifact，大文件统一进入 OSS。
- Docker 镜像不打包原始数据、运行结果或模型 checkpoint。
- 不在项目文档中固化临时测试服务器的具体规格。

## 影响

- `docs/benchmark_platform_design_plan.md` 的首版范围需要包含 Docker Compose 部署骨架、SQLite、OSS 和本地临时缓存策略。
- 后续 Generator 实现部署相关 sprint 时，应创建 `deploy/` 目录和 `.env.example`。
- Evaluator 在部署 sprint 中必须验证 Compose 服务启动、健康检查、API 可访问、worker 可消费任务、OSS 读写配置和本地临时文件清理。

## 未决问题

- 是否在第一阶段就实现完整鉴权。
- OSS bucket、RAM 权限和签名 URL 策略。
- 是否为算法 runner 进一步做容器隔离。
