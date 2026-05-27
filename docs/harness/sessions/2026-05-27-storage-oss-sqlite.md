# Session: OSS storage and SQLite current database

日期：2026-05-27  
参与角色：Planner  
关联任务：修正部署存储方案

## 用户请求

用户明确：数据使用阿里云 OSS 存储，服务器没有太大硬盘，只有 OSS；Docker 不能太大；数据库目前用 SQLite，之后部署 Postgres。

## 本轮上下文

- 上一轮文档刚写入阿里云单机 Docker Compose 部署目标。
- 上一版仍把 Postgres、Redis 和 artifact volume 写成首期部署目标。
- 本轮需要将首期方案修正为 SQLite + OSS + 轻量 Docker，Postgres/Redis 作为后续升级路径。

## 执行动作

| 步骤 | 动作 | 文件/命令 | 结果 |
|---|---|---|---|
| 1 | 检索冲突表述 | `rg "Postgres|Redis|artifact volume|SQLite|OSS" docs/...` | 找到主文档和旧 decision 中的冲突点 |
| 2 | 修改主目标文档 | `docs/benchmark_platform_design_plan.md` | 将首期存储改为 SQLite + OSS，并加入 Docker 轻量化约束 |
| 3 | 修正上一条部署决策 | `docs/harness/decisions/2026-05-27-deployment-target.md` | 标明被本轮存储决策修正 |
| 4 | 新增存储决策 | `docs/harness/decisions/2026-05-27-storage-oss-sqlite.md` | 记录 OSS 主存储和 SQLite 当前数据库决策 |
| 5 | 新增会话记录 | `docs/harness/sessions/2026-05-27-storage-oss-sqlite.md` | 记录本轮用户要求、修改和验证 |

## 修改文件

| 文件 | 修改类型 | 说明 |
|---|---|---|
| `docs/benchmark_platform_design_plan.md` | 修改 | 首期部署改为 SQLite + OSS + 本地临时缓存；Postgres/Redis 后续升级 |
| `docs/harness/decisions/2026-05-27-deployment-target.md` | 修改 | 修正旧的 Postgres/Redis/artifact volume 首期表述 |
| `docs/harness/decisions/2026-05-27-storage-oss-sqlite.md` | 新增 | 记录 OSS 和 SQLite 存储决策 |
| `docs/harness/sessions/2026-05-27-storage-oss-sqlite.md` | 新增 | 本轮审计记录 |

## 验证记录

| 命令/检查 | 结果 | 备注 |
|---|---|---|
| `rg "OSS|SQLite|Postgres|Redis|Docker 镜像|轻量|storage_backend|OSS URI|本地临时" docs/benchmark_platform_design_plan.md docs/harness/decisions` | 通过 | 检查 OSS、SQLite、后续 Postgres/Redis 和轻量 Docker 表述 |
| 旧存储冲突检查 | 通过 | 未发现 `artifact volume`、`SQLite + 文件 artifact`、首期 Postgres/Redis 等旧默认方案 |
| 敏感规格关键字检查 | 通过 | 确认未写入临时测试服务器具体规格 |
| `git commit -- docs/benchmark_platform_design_plan.md docs/harness/decisions docs/harness/sessions/2026-05-27-storage-oss-sqlite.md` | 通过 | 创建本轮审计提交；提交哈希见最终回复 |

## 决策

- 数据集和 artifact 主存储使用阿里云 OSS。
- 当前数据库使用 SQLite。
- Postgres 是后续部署升级目标。
- Redis 独立队列是后续升级目标。
- Docker 镜像必须轻量，不打包数据、运行结果或 checkpoint。

## 风险和阻塞

- 大多数算法仍可能需要将数据下载到本地临时目录运行，需要实现严格清理和容量限制。
- OSS 权限、bucket、签名 URL 和备份策略仍需后续确认。

## 下一步

验证文档一致性并提交本轮 Git 快照。
