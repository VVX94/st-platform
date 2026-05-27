# Decision: OSS 主存储与 SQLite 当前数据库

日期：2026-05-27  
状态：accepted  
关联文档：`docs/benchmark_platform_design_plan.md`

## 背景

最终部署面向阿里云服务器，但服务器本地硬盘不适合作为数据集和 benchmark artifact 的主存储。用户确认数据和产物应使用阿里云 OSS；当前数据库先使用 SQLite，后续再迁移 Postgres；Docker 镜像不能过大。

## 决策

首期部署采用：

- 元数据：SQLite。
- 数据集对象：阿里云 OSS。
- benchmark artifact：阿里云 OSS。
- 本地磁盘：只保存 SQLite、小型日志和可清理临时缓存。
- 队列：SQLite queued runs + worker 轮询。

后续升级采用：

- 元数据迁移到 Postgres。
- 队列迁移到 Redis + RQ/Celery/Arq。
- artifact 继续保留在 OSS。
- 重型算法拆分为可选 runner 镜像，避免主镜像过大。

## Docker 约束

- 镜像不打包原始数据。
- 镜像不打包运行结果。
- 镜像不打包模型 checkpoint。
- API 和 worker 镜像优先使用 slim base image 和最小依赖。
- 重型算法依赖后续按 runner 镜像拆分，不阻塞基础 Web 平台部署。

## 影响

- `storage/` 需要抽象 metadata store 和 object store。
- artifact 表应保存 `uri` 和 `storage_backend`，而不是只保存本地文件路径。
- dataset 登记应支持 OSS URI。
- worker 运行时只下载必要数据到临时目录，并在 run 结束后清理。
- Evaluator 需要验证 OSS 写入、OSS artifact 索引和本地临时文件清理。

## 未决问题

- OSS bucket 命名、地域和 RAM 权限。
- 前端上传是否使用服务端转发还是预签名 URL。
- SQLite 备份到 OSS 的频率和恢复流程。

