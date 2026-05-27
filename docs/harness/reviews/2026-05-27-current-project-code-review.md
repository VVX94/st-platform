# Code Review: Current Project Gaps and Unfinished Platform Work

日期：2026-05-27

审查范围：

- `src/st_platform/` 后端 API、SQLite storage、worker、benchmark metrics/report、h5ad reader、算法适配。
- `web/` React/Vite 前端页面和 API client。
- `tests/` 当前自动化测试覆盖。
- `.claude/` 三智能体配置和长任务启动命令。
- `docs/harness/` sprint、session、decision、task 状态文档。

本轮结论：

- 当前代码已经具备可运行的 benchmark MVP 底座。
- 后端测试和前端构建本轮均通过。
- 但目前仍偏向“本地演示可运行”，距离“可部署到 Web 的完整 benchmark 平台”还有明确缺口，尤其是 OSS 主存储、artifact 下载/预签名访问、worker 可靠性、前端 E2E、agent 启动入口和审计文档一致性。
- CodeRabbit CLI 未安装，本轮没有运行外部 CodeRabbit 审查；以下为本地证据式代码审查。

## 验证结果

| 命令 | 结果 | 备注 |
|---|---:|---|
| `coderabbit --version` | 失败 | `/bin/bash: 行 1: coderabbit：未找到命令` |
| `env PYTHONPATH=src timeout 30s python3 -m pytest tests/test_api.py::TestHealth::test_health_returns_200 -q` | 通过 | `1 passed in 0.84s`，历史 TestClient 超时本轮未复现 |
| `env PYTHONPATH=src python3 -m pytest tests/test_storage.py tests/test_worker.py tests/test_reports.py -q` | 通过 | `27 passed in 1.56s` |
| `npm run build` in `web/` | 通过 | TypeScript + Vite build 成功 |
| `env PYTHONPATH=src timeout 180s python3 -m pytest -q` | 通过 | `137 passed, 6 skipped, 168 warnings in 4.70s` |
| `env PYTHONPATH=src python3 -m pytest -q -rs` | 通过 | 6 skipped 均为经典算法外部依赖未安装 |

跳过的测试：

- `tests/test_runner.py::... SpaGCN dependencies are not installed`
- `tests/test_runner.py::... GraphST dependencies are not installed`
- `tests/test_runner.py::... SEDR dependencies are not installed`
- `tests/test_runner.py::... CCST dependencies are not installed`
- `tests/test_runner.py::... conST dependencies are not installed`
- `tests/test_runner.py::... DeepST dependencies are not installed`

## Findings

### F-001: OSS 主存储仍未实装，当前 artifact 和真实数据流仍依赖本地文件系统

严重级别：High

证据：

- 设计文档要求数据集和 benchmark artifact 走 OSS；`docs/harness/decisions/2026-05-27-storage-oss-sqlite.md` 已记录 OSS 主存储。
- 代码中没有 OSS storage adapter、OSS client、预签名上传/下载接口。
- `src/st_platform/worker/runner.py` 生成报告 artifact 时直接写入 `run_root` 本地路径，并把本地路径写入 `ArtifactModel.uri`。
- `src/st_platform/io/h5ad_reader.py:49-56` 将 h5ad 读取到内存并转成 Python list。
- `src/st_platform/api/routes/datasets.py:100-126` 的真实数据登记接口接收服务器本地路径。

影响：

- 部署到小磁盘服务器时，数据和报告会继续落本地，违背“服务器无大硬盘，数据/产物走 OSS”的约束。
- 前端展示和下载依赖本地路径，不具备跨机器、容器、重启后的稳定访问能力。
- 后续迁移到 Postgres/多 worker 时 artifact URI 语义会变得混乱。

建议修复：

- 新增 `st_platform.storage.object_store` 或 `st_platform.storage.artifacts` 抽象：`LocalArtifactStore` + `AliyunOSSArtifactStore`。
- 后端配置 `ST_PLATFORM_ARTIFACT_BACKEND=local|oss`、`ST_PLATFORM_OSS_BUCKET`、`ST_PLATFORM_OSS_ENDPOINT`、`ST_PLATFORM_OSS_PREFIX`。
- worker 写 artifact 时先写临时目录，再上传到 OSS，DB 只保存 `oss://bucket/key` 或受控相对 key。
- 测试用 fake/local OSS backend，验证 upload、download、signed URL、temp cleanup。

### F-002: 前端报告页调用 `/artifacts/file`，但后端没有对应路由

严重级别：High

证据：

- `web/src/pages/Reports.tsx:200`
- `web/src/pages/Reports.tsx:217`
- `web/src/pages/Reports.tsx:246`
- `web/src/pages/Reports.tsx:256`
- `rg "FileResponse|StaticFiles|artifacts/file" src web` 只发现前端引用，未发现后端实现。

影响：

- Reports 页面虽然能编译，但 plot 图片和 CSV 下载链接在实际浏览器中会 404。
- 当前 pytest 没覆盖浏览器渲染和 artifact 下载，所以这个问题不会被后端测试发现。

建议修复：

- 增加后端 artifact 访问 API，例如：
  - `GET /api/artifacts/{artifact_id}/download`
  - `GET /api/artifacts/{artifact_id}/resolve`
- local backend 返回 `FileResponse`，OSS backend 返回短期 signed URL 或后端代理下载。
- 前端不要直接传服务器绝对路径，应使用 artifact id。
- 增加 API 测试和 Playwright 测试：创建实验、运行 worker、打开 report、确认图片非 404、CSV 可下载。

### F-003: 真实数据登记接口暴露服务器本地路径，不适合公开 Web 平台

严重级别：High

证据：

- `web/src/pages/Datasets.tsx:53` 将用户输入的 `path` 发给 `/api/datasets/register-real`。
- `src/st_platform/api/routes/datasets.py:100-126` 接收 `DatasetRegisterReal.path` 并在服务端直接读取。
- `src/st_platform/api/schemas.py` 中 `DatasetRegisterReal.path` 注释为 local h5ad file path。

影响：

- 公开匿名站点不应让用户提交任意服务器路径。
- 真实部署中用户浏览器无法知道服务器本地路径。
- 这会和 OSS 上传/登记模型冲突。

建议修复：

- 把 `register-real` 调整为开发/管理员工具，或仅在本地模式启用。
- Web 首版使用 OSS 预签名上传：
  - `POST /api/uploads/init`
  - 浏览器直传 OSS
  - `POST /api/datasets/register` 只提交 OSS URI、checksum、metadata。
- 真实数据读取由 worker 从 OSS 临时下载到受控 temp dir，运行后清理。

### F-004: h5ad reader 会把矩阵整体转成 Python list，内存开销偏高

严重级别：High

证据：

- `src/st_platform/io/h5ad_reader.py:49-56` 对 `adata.X` 使用 `toarray()` 并 `tolist()`。
- worker 再把 `asset.metadata["matrix"]` 转回 `np.array` 计算指标和算法输入。

影响：

- STARmap 小数据可跑，但稍大 Visium/h5ad 会出现明显内存膨胀。
- 2 核 4GB 级测试服务器上容易 OOM。
- JSON-like metadata 携带大矩阵不适合作为平台内部数据模型。

建议修复：

- `SpatialDataBundle` 中不要把大矩阵塞进 metadata list。
- 引入本地临时数据引用：matrix 存 `.npy`/`.npz`/AnnData 临时文件，asset metadata 只放 shape、dtype、path/URI。
- 对算法适配层提供统一 loader，按算法需要读取数组。
- 对 h5ad reader 增加 `max_obs`、`max_vars`、抽样或预处理策略，首版明确资源保护。

### F-005: worker 队列缺少原子 claim、attempt、heartbeat 和 stale running 恢复

严重级别：High

证据：

- `src/st_platform/storage/repositories.py:123` 仅按 `status == "queued"` 查询。
- `src/st_platform/worker/runner.py:210` 直接 `repo.list_queued()[:limit]`。
- `src/st_platform/storage/models.py` 的 `RunModel` 没有 `attempt`、`worker_id`、`heartbeat_at`、`locked_at`。
- `docs/harness/decisions/2026-05-27-worker-sqlite-queue.md` 已要求 worker 记录 `worker_id`、`heartbeat_at`、`attempt`。

影响：

- 如果同时启动两个 worker，可能重复领取同一个 queued run。
- worker 异常退出后，running run 没有恢复机制。
- 无法审计某个 run 是哪个 worker、哪次尝试执行的。

建议修复：

- SQLite 首版也要实现近似原子 claim：在事务中按 `created_at` 选择 queued run 并更新为 running。
- 增加 `attempt`、`worker_id`、`heartbeat_at`、`locked_at`、`last_error` 字段。
- worker 启动时扫描 stale running 并按策略 requeue/failed。
- 增加并发领取测试和 stale recovery 测试。

### F-006: Experiment 状态不会随 run 完成自动收敛

严重级别：Medium

证据：

- `src/st_platform/api/routes/experiments.py:86` 创建 run 后直接 `repo.update_status(exp.experiment_id, "running")`。
- worker 成功或失败时只调用 `RunRepo.mark_succeeded/mark_failed`，没有更新 experiment 状态。

影响：

- 前端会长期显示 experiment 为 `running`，即使全部 runs 已经 succeeded/failed。
- 报告页状态和 runs 实际状态不一致，影响演示可信度。

建议修复：

- worker 每完成一个 run 后调用 `ExperimentRepo.recompute_status(experiment_id)`。
- 状态规则建议：
  - 所有 run succeeded -> `succeeded`
  - 任一 failed 且无 queued/running -> `failed` 或 `partially_failed`
  - 有 queued/running -> `running`
- 增加多算法实验状态收敛测试。

### F-007: 算法列表中已注册经典算法，但依赖未安装时仍可能被用户选择

严重级别：Medium

证据：

- `src/st_platform/algorithms/builtin.py` 注册了 `ccst`、`const`、`deepst`、`graphst`、`sedr`、`spagcn`、`spagcn-lite`。
- 本轮 `pytest -rs` 显示 6 个真实算法测试因依赖缺失跳过。
- 算法 API 当前只返回静态 spec，没有 runtime availability/capability 状态。

影响：

- Web 上用户可以选择不可运行算法，worker 执行后才失败。
- 对 PPT/演示来说，会造成“接入”和“实际可运行”边界不清。

建议修复：

- 算法 registry 增加 `availability`：
  - `ready`
  - `missing_dependency`
  - `disabled_by_config`
  - `experimental`
- `/api/algorithms` 返回 `available`、`missing_packages`、`last_smoke_status`。
- 前端默认禁用不可运行算法，并展示原因。
- 每个真实算法适配必须有最小 smoke 数据和明确安装命令。

### F-008: STAGATE、SpaceFlow、ADEPT、ConGI 等空间域相关目录存在，但尚未纳入当前平台 registry

严重级别：Medium

证据：

- 仓库外层存在 `BenchmarkST/STAGATE_pyG`、`SpaceFlow`、`SDMBench/SpaceFlow_DC`、`STAGATE` 等目录。
- `src/st_platform/algorithms/` 当前没有 `stagate.py`、`spaceflow.py`、`adept.py`、`congi.py`。
- `build_builtin_algorithms()` 未注册这些算法。

影响：

- 和目标算法范围相比，仍有空间域识别算法没有平台化。
- 后续 benchmark 排名/对比的算法覆盖不完整。

建议修复：

- 下一批算法建议按依赖难度拆 sprint：
  - Sprint A：STAGATE + SpaceFlow availability probe + smoke adapter。
  - Sprint B：ADEPT/ConGI 先做 registry capability 和文档化安装，不强行上线不可运行适配。
- 每个算法先实现 `--dry-run`/small smoke，再接真实数据。

### F-009: 缺少 Playwright 或等价浏览器 E2E，无法验证前端真实可用性

严重级别：Medium

证据：

- `web/package.json` 只有 `dev`、`build`、`preview`。
- `rg "playwright" src web tests docs/harness .claude` 未发现前端 E2E 配置。
- `docs/harness/agent_coding_governance.md` 已要求涉及 React 页面时默认需要 Playwright 或等价验证。

影响：

- TypeScript build 只能证明编译通过，不能证明按钮、路由、报告图片、下载、表单提交实际可用。
- F-002 这类前端/后端断裂不会被当前测试捕获。

建议修复：

- 增加 `web/playwright.config.ts` 和 `web/tests/benchmark.spec.ts`。
- 最小 E2E：
  - 打开 Dashboard。
  - 注册 demo dataset。
  - 创建 spagcn-lite experiment。
  - 触发 worker 或调用 API seed。
  - 打开 report 页面。
  - 检查 metrics 表、runs 表、plot image response、CSV download link。

### F-010: `.claude/commands/start-st-platform-longrun.md` 启动命令仍指向已完成的 Sprint 1

严重级别：Medium

证据：

- `.claude/commands/start-st-platform-longrun.md:14` 固定读取 `SPRINT-20260527-001-runtime-foundation/sprint_contract.md`。
- `docs/harness/tasks/TASK-20260527-001-runtime-smoke-platform/status.md` 当前状态为 `done`。

影响：

- 新一轮 Claude harness 启动后可能回到已完成工作，而不是选择当前最高优先级缺口。
- 不利于长期多轮 agent 编码。

建议修复：

- 改成动态启动流程：
  - 读取 `docs/harness/tasks/**/status.md`。
  - 查找 `in_progress` 或 `planned` task。
  - 若没有当前 task，先让 planner 根据最新 review 创建下一 sprint。
- 启动命令明确：每轮只做一个 work point，结束时更新 session/review/sprint 并 commit。

### F-011: sprint/task 状态文档存在冲突，影响后续审计

严重级别：Medium

证据：

- `docs/harness/sprints/SPRINT-20260527-003-metrics-reports/acceptance_status.md:18` 写着 `Sprint NOT accepted`。
- 同文件说明前端 Reports 页未交付。
- `docs/harness/tasks/TASK-20260527-001-runtime-smoke-platform/status.md` 却将 `SPRINT-20260527-003-metrics-reports` 标为 accepted。
- 后续 Sprint 5 已补前端 Reports，但 Sprint 3 本身的 acceptance 文档未标注 superseded/resolved。

影响：

- 审计时无法判断 Sprint 3 到底是否通过。
- Planner/Evaluator 可能基于旧失败状态重复规划。

建议修复：

- 不建议直接篡改历史 evaluator 结论。
- 在 Sprint 3 acceptance 文档追加 `Resolution`：
  - 原 Sprint 3 当时未通过。
  - 后续 `SPRINT-20260527-005-multi-algo-frontend` 补齐 AC #7。
  - 当前 task-level acceptance 已 resolved。
- 在 task status 中记录 resolved by sprint。

### F-012: 数据库 schema 仍是 MVP 形态，缺少迁移、约束、索引和 Postgres 过渡策略

严重级别：Medium

证据：

- `src/st_platform/storage/database.py:11-28` 在 import 时创建全局 engine 和 SessionLocal。
- `src/st_platform/storage/models.py` 多个 JSON 字段以 `Text` 保存。
- 当前无 Alembic/迁移目录。
- 列表接口未分页，repository 查询没有显式排序。

影响：

- 测试可用，但长期演进会遇到 schema 变更不可控的问题。
- SQLite 到 Postgres 迁移需要重新整理 JSON 字段、索引和迁移策略。

建议修复：

- 引入轻量 migration 机制，至少先有 `scripts/migrate_db.py` 或 Alembic。
- 增加索引：`runs.status`、`runs.experiment_id`、`created_at`、`artifacts.run_id`、`metrics.run_id`。
- 列表接口增加分页和排序。
- 为 Postgres 迁移保留 JSON/JSONB 类型设计说明。

### F-013: API 输入校验不足，错误会推迟到 worker 阶段才暴露

严重级别：Medium

证据：

- `ExperimentCreate.algorithm_ids` 允许空 list。
- `create_experiment()` 未校验算法是否存在、算法 task_type 是否匹配 experiment task_type。
- 未校验 dataset_id 不存在时是否应创建 experiment。

影响：

- 用户可能创建空实验、未知算法实验或算法任务类型不匹配实验。
- UI 会显示 queued/running，但 worker 后续失败，体验不清晰。

建议修复：

- 创建 experiment 时立即校验：
  - 至少一个算法。
  - dataset_id 存在。
  - 每个算法存在且支持该 task_type。
  - 算法可用性为 ready。
- 对失败请求返回 400/422，并在前端展示可读错误。

### F-014: API 路由中暴露手动 `/api/worker/poll`，不适合公开站点直接触发计算

严重级别：Medium

证据：

- `src/st_platform/api/routes/worker.py` 提供 `POST /api/worker/poll`。
- `web/src/pages/Experiments.tsx` 通过 `Run Worker` 按钮调用该接口。
- `scripts/start_worker.sh` 已存在独立轮询 worker，但前端仍依赖手动触发。

影响：

- 公开匿名站点中，任意用户可以触发 worker poll。
- 用户体验上也不应要求手动点击 Run Worker。

建议修复：

- 保留 `/api/worker/poll` 为 dev-only，生产关闭或仅本地可用。
- 正式路径：创建 experiment 后由独立 worker 进程自动消费 queued runs。
- 前端只负责展示状态和刷新，不负责触发 worker。

### F-015: 当前报告 artifact 会把服务器绝对路径暴露到 UI/API

严重级别：Medium

证据：

- `RunOut.artifacts` 返回 artifact `uri`。
- `web/src/pages/RunDetail.tsx` 直接展示 artifact URI。
- 当前 artifact URI 是 worker 写入的本地文件路径。

影响：

- 暴露服务器目录结构。
- OSS 切换后 URI 语义也会变化。

建议修复：

- API 返回 artifact `artifact_id`、`kind`、`display_name`、`download_url` 或 `preview_url`。
- 对外隐藏绝对路径，内部 URI 仅后端可见。

### F-016: 前端仍是原型级 UI，缺少完整产品态交互和状态处理

严重级别：Low

证据：

- 前端大量 inline style，无统一组件、loading/error/empty 状态抽象。
- 没有分页、筛选、搜索、排序。
- 没有前端 E2E。

影响：

- 可以演示，但长期作为 benchmark 管理后台维护成本偏高。

建议修复：

- 先补 Playwright，再考虑组件化。
- 首期聚焦可用工作流：数据集、算法可用性、创建实验、运行记录、报告详情。

## 当前未完善点清单

按“是否阻塞完整 Web benchmark 平台”排序：

1. OSS data/artifact backend 未实现。
2. artifact preview/download API 缺失，Reports 页面图片/CSV 链接不通。
3. 真实数据上传/登记仍是服务器本地路径模式。
4. h5ad reader 和 bundle 数据结构对大数据内存不友好。
5. worker queue 缺少原子 claim、attempt、worker_id、heartbeat、stale recovery。
6. experiment 状态不会随 runs 自动完成。
7. 算法可用性没有显式暴露，缺依赖算法仍可选。
8. STAGATE、SpaceFlow、ADEPT、ConGI 等尚未接入 registry。
9. 缺少 Playwright/browser E2E。
10. Claude longrun 命令仍指向旧 Sprint 1。
11. Sprint 3 与 task status 文档状态冲突。
12. 数据库缺少迁移、索引、分页和 Postgres 迁移准备。
13. API 创建 experiment 的输入校验不足。
14. 手动 worker poll 不适合公开站点。
15. artifact 绝对路径泄露到 API/UI。
16. 前端仍是可演示原型，未到完整产品态。

## 建议下一批修复 Sprint

### Sprint 7: Artifact 访问闭环和报告页可视化修复

目标：

- 新增 artifact download/preview API。
- 修复 Reports 页面 `/artifacts/file` 404 问题。
- 用 local artifact backend 先跑通下载和图片预览。
- 增加 API 测试和 Playwright smoke。

验收：

- 运行 spagcn-lite demo 后，Reports 页能显示 `domain_grid_plot` 和 `metrics_bar_plot`。
- CSV 下载链接返回 200。
- 不暴露服务器绝对路径。

### Sprint 8: OSS object store 抽象和本地 fake backend

目标：

- 定义 artifact/object storage interface。
- local fake backend 通过测试。
- OSS backend 配置、URI 规范、预签名 URL 设计落地。

验收：

- worker 产物可写入 backend。
- API 可 resolve artifact。
- fake backend 测试覆盖 upload/download/signed URL/temp cleanup。

### Sprint 9: Worker 可靠性和 experiment 状态收敛

目标：

- 原子 claim queued run。
- 增加 `worker_id`、`attempt`、`heartbeat_at`。
- stale running recovery。
- experiment 状态自动从 running 收敛到 succeeded/failed。

验收：

- 并发 worker 不重复执行同一 run。
- worker 崩溃后 stale run 可恢复。
- 多算法 experiment 完成后状态正确。

### Sprint 10: 数据集上传/OSS 登记替代本地路径登记

目标：

- Web 不再要求输入服务器本地路径。
- 增加 upload init/register flow。
- `register-real` 改为 dev-only 或 CLI-only。

验收：

- 前端完成 h5ad/Visium 数据登记流程。
- DB 保存 OSS URI、checksum、metadata。
- worker 从 OSS 临时拉取并清理。

### Sprint 11: 算法可用性和下一批空间域算法

目标：

- API 返回算法 availability。
- 前端禁用 missing dependency 算法。
- 接入 STAGATE/SpaceFlow 的最小 smoke adapter 或至少 capability probe。

验收：

- Web 能清楚区分 ready/missing_dependency/experimental。
- 不会把不可运行算法伪装为已可运行。

## 审查结论

当前项目可以继续作为 benchmark 平台 MVP 基础推进，不需要推倒重来。

下一步不应优先继续堆算法数量，而应先修复 artifact 访问、OSS 存储、worker 状态和浏览器 E2E。否则算法越多，失败路径和审计成本会迅速变高，PPT 和真实 Web 演示也会出现“后端有结果、前端看不到图/下载不了”的问题。
