# 空间转录组 Benchmark Web 平台实施总纲

版本：2026-05-27  
状态：实施总纲草案，用于多智能体协作、项目管理和后续调整  
范围：在现有 `st-platform` 基础上建设可通过 Web 使用、可部署、可复现评测、支持多算法多数据集的空间转录组空间域/聚类 benchmark 平台

## 1. 文档定位

本文档是完整算法 benchmark 平台的实施总纲草案，不是冻结版 PRD。它用于把目标、范围、架构、交付阶段和验收标准组织成可执行的项目管理 spec，后续可以继续修改范围、优先级、技术方案和里程碑。

最终目标不是停留在脚本演示或本地 MVP，而是形成一个可以部署到 Web 环境的完整可用项目。平台应支持用户通过浏览器完成数据集管理、算法选择、评测配置、后台运行、指标对比、报告查看和 artifact 下载，并保证每次 benchmark run 可追踪、可复现、可诊断。

实施方式允许分阶段推进，但每个阶段都应服务于最终完整平台，而不是形成彼此割裂的 demo。阶段性交付可以先采用较轻的本地配置，但文档必须同时明确生产可部署目标和后续升级路径。

后续通过 agent 推进代码实现时，编码治理、会话留痕、任务包、sprint contract、评审报告、数据 manifest 和 artifact manifest 以 `docs/harness/agent_coding_governance.md` 为准；当前仓库结构基线以 `docs/harness/project_structure_map.md` 为准。

当前基础：

- `st-platform` 已具备统一任务、算法注册、runner、CLI 和结果对象。
- 已接入空间域识别算法：SpaGCN、GraphST、SEDR、CCST、conST、DeepST、SpaGCN-lite。
- 已在 STARmap BY3 1k 真实数据上生成过演示级 benchmark 结果。

下一阶段目标是把这些能力从“脚本演示”升级为“可管理、可复现、可比较、可部署”的 API + Web benchmark 平台，并为多智能体并行实现提供清晰边界。

## 2. 项目目标

建设一个用于空间转录组空间域/聚类算法的 benchmark 评测平台，支持：

1. 统一管理数据集。
2. 统一管理算法适配器。
3. 配置多数据集 x 多算法评测任务。
4. 异步运行算法并记录状态。
5. 计算可比较指标。
6. 生成表格、图片和 Markdown 报告。
7. 在 Web 管理后台中查看数据集、算法、运行记录和报告。

首版重点不是追求所有算法和所有指标的完整覆盖，而是把 benchmark 主链路做稳定：

```text
登记数据集 -> 选择算法 -> 创建评测 -> 后台运行 -> 计算指标 -> 生成报告 -> Web 查看/下载
```

### 2.1 多智能体 Harness 配置

后续代码实现采用 Planner / Generator / Evaluator 三智能体 harness，而不是按后端、前端、算法等模块拆分长期固定 agent。模块边界由任务和 sprint contract 决定，agent 角色按“规划、生成、评估”分离。

核心闭环：

```text
用户目标
  -> Planner 更新产品 spec、任务包、验收标准
  -> Generator 提出 sprint contract
  -> Evaluator 审核 contract 是否可测
  -> Generator 实现代码、测试和必要文档
  -> Evaluator 独立验证 UI / API / worker / database / artifact
  -> 通过则提交 Git 快照并进入下一轮，不通过则退回 Generator 修复
```

角色配置：

| Agent | 主要职责 | 主要输出 | 禁止事项 |
|---|---|---|---|
| Planner | 拆解用户目标、维护任务包、定义验收标准、识别依赖和风险 | `docs/harness/tasks/`、`docs/harness/sprints/`、`docs/harness/decisions/` | 不直接修改运行时代码，不替 Generator 宣称完成 |
| Generator | 按已确认 contract 实现一个 sprint，补充测试和自测记录 | 代码、测试、脚本、`generator_handoff.md`、变更清单 | 不跳过 contract，不用 stub 冒充完整功能，不批准自己的工作 |
| Evaluator | 独立验证 contract，运行测试、点击 Web、检查 API/worker/database/artifact | `evaluator_report.md`、`acceptance_status.md`、bug queue | 不因“看起来接近”放过核心流程失败，不把无法验证标记为通过 |

通信和留痕：

- 所有跨 agent 交接通过 `docs/harness/` 下的 Markdown 文件完成。
- 每一轮重要对话必须写入 `docs/harness/sessions/`。
- 每个可执行任务必须有 `task_spec.md`、状态记录和验收标准。
- 每个编码 sprint 必须先有 `sprint_contract.md`，再进入实现。
- 每轮任务结束必须提交一次 Git 快照，提交信息应能对应到 task 或 sprint。
- Git 提交只包含源码、测试、规范文档、配置和 manifest；运行中间文件、数据库、上传数据、模型权重、生成图片、CSV/JSON 报告等产物默认只在 manifest 中登记，不直接进入 Git。

## 3. 首版范围

### 3.1 包含内容

首版包含：

- FastAPI 后端。
- React 管理后台。
- 异步 worker。
- SQLite 元数据存储。
- 阿里云 OSS 数据和 artifact 存储。
- 本地小容量临时缓存目录。
- Docker Compose 部署骨架。
- h5ad 和 10x Visium 数据读取。
- 空间域/聚类算法评测。
- 核心 + 空间指标。
- CSV、PNG、Markdown 报告导出。

### 3.2 暂不包含内容

首版不包含：

- 登录、用户、角色、权限和审计。
- 浏览器大文件上传。
- 多机/集群调度。
- 复杂并发任务调度。
- 完整容器化算法隔离 runner。
- 弹性扩缩容。
- Redis / Celery / RQ 等独立队列服务。
- Postgres 生产数据库迁移。
- 完整生产级监控告警。
- 完整论文级指标集。

这些能力作为后续阶段规划。

## 4. 技术架构

推荐整体结构：

```text
st-platform/
├─ src/st_platform/
│  ├─ api/                  # FastAPI 路由、schemas、依赖注入
│  ├─ benchmark/            # experiment、metrics、reports、worker 协调
│  ├─ io/                   # h5ad / Visium 数据读取与 SpatialDataBundle 转换
│  ├─ storage/              # SQLite repository、OSS artifact 管理
│  ├─ algorithms/           # 现有算法适配器 + STAGATE / SpaceFlow
│  ├─ core/                 # 现有 registry、runner、RunResult
│  ├─ data/                 # 现有数据契约
│  ├─ tasks/                # 现有任务定义
│  └─ workflows/            # 现有 PlatformService
├─ web/                     # React 管理后台
├─ deploy/                  # Docker Compose、Nginx、env 示例和部署脚本
├─ scripts/                 # 启动 worker、初始化数据库、迁移辅助脚本
├─ docs/
└─ runs/                    # artifact 根目录
```

设计原则：

- `algorithms/` 继续只负责算法适配，不承担 benchmark 编排。
- `benchmark/` 负责多数据集、多算法、指标和报告。
- `io/` 负责把真实数据转换成平台统一数据对象。
- `storage/` 负责 SQLite 元数据、OSS 对象索引和临时缓存路径，不把持久化逻辑散落在 service 中。
- React 前端只通过 API 访问平台，不直接读取本地文件。

### 4.1 部署目标

最终部署目标面向阿里云服务器上的 Web 服务。首个可部署形态采用轻量单机 Docker Compose：服务容器尽量少，镜像尽量小，服务器本地磁盘只保存 SQLite 元数据、小型日志和运行期临时缓存；真实数据、运行产物、报告图表、预测表和模型权重统一存入阿里云 OSS。

后续再根据真实负载演进到更强的单机规格、多机部署、Postgres、Redis 队列或更完整的算法容器隔离。

首个部署拓扑：

```text
Nginx / web
  -> React static assets
  -> reverse proxy /api to FastAPI

FastAPI api
  -> SQLite metadata database
  -> OSS dataset/artifact storage
  -> local temp cache

worker
  -> SQLite queued runs
  -> algorithm runner
  -> OSS dataset/artifact storage
  -> local temp cache cleanup
```

建议部署目录：

```text
deploy/
├─ docker-compose.yml
├─ api.Dockerfile
├─ worker.Dockerfile
├─ web.Dockerfile
├─ nginx.conf
└─ .env.example
```

服务边界：

| 服务 | 职责 | 初期资源策略 |
|---|---|---|
| `web` | 托管 React 静态资源，反向代理 API | 静态服务，保持轻量 |
| `api` | FastAPI 路由、鉴权、实验配置、状态查询、OSS 上传/下载签名 | 不执行长任务，只创建任务和查询 |
| `worker` | 后台执行 benchmark run、读写 OSS artifacts | 默认低并发，运行后清理本地临时文件 |
| `sqlite` | 当前元数据存储 | 小文件持久化，可定期备份到 OSS |
| `oss` | 数据集、运行产物、报告、图表、预测表、模型权重 | 主存储，不依赖服务器大硬盘 |

资源约束原则：

- 初期按小资源单机环境设计，避免把 API、Web 和算法执行耦合在同一进程，也避免在首期引入过多常驻容器。
- 默认 worker 并发为低并发，算法 run 通过队列串行或小并发执行。
- demo 和 smoke test 使用小型数据集和低训练轮数，完整 benchmark 作为后台任务运行。
- 大型数据、模型权重、报告图片和 CSV/JSON 产物只落 OSS，不进入 Git。
- worker 只在 run 期间把必要数据下载到本地临时目录，任务结束后清理。
- Docker 镜像不打包原始数据、运行结果、模型 checkpoint 或完整演示产物；重依赖算法后续可拆成独立 runner 镜像。
- 文档不固化临时测试服务器规格，只记录可扩展部署原则和资源敏感策略。

### 4.2 存储演进路线

当前和首期部署：

- 元数据：SQLite。
- 数据集对象：阿里云 OSS。
- artifact：阿里云 OSS。
- 本地磁盘：只保存 SQLite、小日志和可清理临时缓存。
- 队列：首期可使用 SQLite queued runs + worker 轮询，减少常驻服务数量。

后续升级：

- 元数据从 SQLite 迁移到 Postgres。
- 队列从 SQLite 轮询迁移到 Redis + RQ/Celery/Arq。
- artifact 继续使用 OSS，只替换索引和签名策略，不迁移大文件回服务器。
- 重型算法拆分为可选 runner 镜像，避免主 API / worker 镜像过大。

## 5. 后端模块设计

### 5.1 Dataset Reader

职责：

- 读取 h5ad。
- 读取 10x Visium 目录。
- 提取表达矩阵、空间坐标、spot/cell id、gene id。
- 读取可选真实标签列。
- 转换为 `SpatialDataBundle`。
- 生成数据集摘要：shape、平台类型、坐标键、标签列、标签类别数。

首版支持格式：

| 格式 | 输入 | 说明 |
|---|---|---|
| h5ad | OSS URI 或开发模式本地 `.h5ad` 文件路径 | 需要 `obsm["spatial"]` 或用户指定坐标键 |
| Visium | OSS 前缀或开发模式本地 10x Visium 目录路径 | 读取表达矩阵、`spatial/` 坐标和 metadata |

标签策略：

- 有标签数据：计算 ARI、NMI 等监督指标。
- 无标签数据：只计算空间指标、运行时间、产物完整性指标。

### 5.2 Experiment Spec

职责：

- 描述一个 benchmark experiment。
- 支持多数据集 x 多算法。
- 为每个算法保存参数模板。
- 固化运行时配置，保证可复现。

建议字段：

```json
{
  "name": "STARmap-DLPFC-osmFISH spatial clustering benchmark",
  "dataset_ids": ["..."],
  "algorithm_ids": ["spagcn", "graphst", "sedr"],
  "parameters": {
    "spagcn": {},
    "graphst": {}
  },
  "metric_profile": "core_spatial_v1"
}
```

首版不做复杂参数搜索，只做固定参数配置。

### 5.3 Benchmark Runner

职责：

- 将 experiment 拆成多个 run。
- 每个 run 表示一个 `dataset x algorithm` 组合。
- 调用现有 `LocalRunner` 或等价服务执行算法。
- 记录 run 状态、开始时间、结束时间、错误信息。
- 写入 artifact 索引。

run 状态：

| 状态 | 说明 |
|---|---|
| `queued` | 已创建，等待 worker 执行 |
| `running` | worker 正在执行 |
| `succeeded` | 算法完成且产物写入成功 |
| `failed` | 算法失败或指标/报告生成失败 |

### 5.4 Metric Service

首版指标采用“核心 + 空间”集合：

| 指标 | 需要真实标签 | 说明 |
|---|---|---|
| ARI | 是 | 聚类与真实标签一致性 |
| NMI | 是 | 聚类信息一致性 |
| runtime seconds | 否 | 运行时间 |
| spatial neighbor agreement | 否 | 邻域内预测标签一致性 |
| spatial continuity | 否 | 空间连续性简化指标 |

后续 TODO：实现完整论文级指标，包括 HOM、COM、CHAOS、PAS、ASW、Moran's I、Geary's C、内存峰值等。

### 5.5 Report Service

职责：

- 为 experiment 生成汇总表。
- 为每个 run 生成预测表。
- 生成空间域可视化图。
- 生成指标对比图。
- 生成 Markdown 报告。

首版输出：

```text
oss://<bucket>/benchmark_results/<experiment_id>/
├─ experiment_summary.csv
├─ run_metrics.csv
├─ domain_predictions.csv
├─ domain_grid.png
├─ metrics_bar.png
└─ report.md
```

开发模式可以把同样结构写入本地 `benchmark_results/`，但部署环境默认写入 OSS。

## 6. 算法范围

首版算法范围：

| algorithm_id | 算法 | 状态 |
|---|---|---|
| `spagcn` | SpaGCN | 已接入，需纳入 benchmark |
| `graphst` | GraphST | 已接入，需纳入 benchmark |
| `sedr` | SEDR | 已接入，需纳入 benchmark |
| `ccst` | CCST | 已接入，需纳入 benchmark |
| `const` | conST | 已接入，需纳入 benchmark |
| `deepst` | DeepST | 已接入，需纳入 benchmark |
| `spagcn-lite` | SpaGCN-lite | 已接入，作为 lightweight baseline |
| `stagate` | STAGATE | 待接入 |
| `spaceflow` | SpaceFlow | 待接入 |

算法接入标准：

- 必须提供 `AlgorithmSpec`。
- 必须实现统一 `Algorithm.run(data, parameters, context)`。
- 必须输出 `domain_assignments` artifact。
- 必须在失败时返回可读错误。
- 必须支持低成本 smoke-test 参数。
- 必须在 registry 中可见。

## 7. 示例数据集

首版内置/登记示例数据：

| 数据集 | 格式 | 说明 |
|---|---|---|
| STARmap BY3 1k | h5ad | 小型真实数据，已有演示结果 |
| DLPFC 151673 | Visium / h5 | 更接近 10x Visium 场景 |
| osmFISH | h5ad / CSV | 小型空间转录组数据，可用于多数据集评测 |

数据集登记方式：

- 首版部署使用 OSS URI / OSS prefix 登记。
- 开发模式允许使用本地路径登记。
- 不把大文件复制到服务器长期保存。
- 浏览器上传后也应尽快进入 OSS，服务器只做流式转发或签名授权。
- 平台只保存 URI、storage backend、metadata、解析状态和标签列配置。

## 8. 存储设计

首版使用 SQLite + OSS artifact。服务器本地只保留小型 SQLite 文件、运行日志和可清理临时缓存；大文件、报告、图表、预测表和模型权重都写入 OSS。

### 8.1 SQLite 表草案

`datasets`

| 字段 | 说明 |
|---|---|
| `id` | 数据集 ID |
| `name` | 显示名称 |
| `format` | `h5ad` 或 `visium` |
| `uri` | OSS URI 或开发模式本地路径 |
| `storage_backend` | `oss` / `local` |
| `n_obs` | spot/cell 数 |
| `n_vars` | gene 数 |
| `spatial_key` | 坐标键 |
| `label_column` | 可选真实标签列 |
| `status` | `registered` / `validated` / `failed` |
| `created_at` | 创建时间 |

`algorithms`

| 字段 | 说明 |
|---|---|
| `id` | algorithm_id |
| `name` | 算法名称 |
| `task_type` | 任务类型 |
| `backend` | 后端说明 |
| `status` | `available` / `missing_dependency` / `disabled` |

`experiments`

| 字段 | 说明 |
|---|---|
| `id` | experiment ID |
| `name` | 评测名称 |
| `status` | 聚合状态 |
| `spec_json` | 固化后的 experiment spec |
| `created_at` | 创建时间 |
| `finished_at` | 结束时间 |

`runs`

| 字段 | 说明 |
|---|---|
| `id` | run ID |
| `experiment_id` | 所属 experiment |
| `dataset_id` | 数据集 |
| `algorithm_id` | 算法 |
| `status` | run 状态 |
| `parameters_json` | 固化参数 |
| `started_at` | 开始时间 |
| `finished_at` | 结束时间 |
| `error` | 错误信息 |

`metrics`

| 字段 | 说明 |
|---|---|
| `id` | metric ID |
| `run_id` | 所属 run |
| `name` | 指标名 |
| `value` | 指标值 |

`artifacts`

| 字段 | 说明 |
|---|---|
| `id` | artifact ID |
| `run_id` | 所属 run |
| `kind` | `domain_assignments` / `plot` / `table` / `report` |
| `uri` | OSS URI 或开发模式本地路径 |
| `storage_backend` | `oss` / `local` |
| `description` | 描述 |

## 9. API 草案

### 数据集

| Method | Path | 说明 |
|---|---|---|
| `GET` | `/api/datasets` | 数据集列表 |
| `POST` | `/api/datasets/register` | 登记本地数据集路径 |
| `GET` | `/api/datasets/{dataset_id}` | 数据集详情 |
| `POST` | `/api/datasets/{dataset_id}/validate` | 重新解析/验证数据集 |

### 算法

| Method | Path | 说明 |
|---|---|---|
| `GET` | `/api/algorithms` | 算法列表 |
| `GET` | `/api/algorithms/{algorithm_id}` | 算法详情 |

### 评测

| Method | Path | 说明 |
|---|---|---|
| `POST` | `/api/experiments` | 创建 benchmark experiment |
| `GET` | `/api/experiments` | experiment 列表 |
| `GET` | `/api/experiments/{experiment_id}` | experiment 详情 |
| `GET` | `/api/experiments/{experiment_id}/runs` | run 列表 |
| `GET` | `/api/experiments/{experiment_id}/report` | 报告摘要 |

### 运行和产物

| Method | Path | 说明 |
|---|---|---|
| `GET` | `/api/runs/{run_id}` | run 详情 |
| `GET` | `/api/artifacts/{artifact_id}/download` | 下载 artifact |

## 10. React 管理后台

首版包含五个模块。

### 10.1 数据集模块

页面能力：

- 列出已登记数据集。
- 登记 OSS URI / OSS prefix，开发模式可登记本地路径。
- 显示格式、shape、标签列、解析状态。
- 查看数据集详情。

### 10.2 算法模块

页面能力：

- 列出已注册算法。
- 显示 task type、backend、依赖状态。
- 显示默认参数模板。
- 标注 STAGATE / SpaceFlow 等新增算法接入状态。

### 10.3 评测配置模块

页面能力：

- 创建 benchmark experiment。
- 选择多个数据集。
- 选择多个算法。
- 编辑算法参数。
- 预览将生成的 run 数量。

### 10.4 运行记录模块

页面能力：

- 显示 queued / running / succeeded / failed。
- 查看每个 run 的数据集、算法、参数、耗时、错误。
- 支持按 experiment、算法、状态筛选。

### 10.5 报告/可视化模块

页面能力：

- 展示指标表。
- 展示空间域图。
- 展示算法对比图。
- 下载 CSV、PNG、Markdown 报告。

## 11. Worker 和队列设计

首期正式采用 SQLite queued runs + 低并发 worker 轮询。这样可以减少 Redis / Celery / RQ 等常驻服务，降低初期阿里云单机部署和 Docker 镜像维护成本。

首期执行链路：

```text
FastAPI API
  -> 写入 SQLite runs(status=queued)
  -> worker 低频轮询 queued runs
  -> 获取一个 run 并标记 running
  -> 从 OSS 下载必要数据到本地临时目录
  -> 调用 BenchmarkRunner / LocalRunner
  -> metrics 写入 SQLite
  -> artifacts 写入 OSS
  -> 清理本地临时目录
  -> 标记 succeeded 或 failed
```

约束：

- 首期默认单 worker 顺序执行。
- 可保留配置项支持极低并发，但默认不打开。
- 不做取消。
- 不做自动重试。
- 不引入 Redis / Celery / RQ。
- 单个算法崩溃时应记录 run failed，不影响其他 queued run。
- worker 启动时应能识别上次异常退出遗留的 `running` run，并标记为 failed 或 stale。
- worker 只在 run 期间占用本地临时目录，任务结束后必须清理。

SQLite runs 表建议增加字段：

| 字段 | 说明 |
|---|---|
| `queued_at` | 入队时间 |
| `started_at` | 开始执行时间 |
| `finished_at` | 结束时间 |
| `heartbeat_at` | worker 最近心跳 |
| `worker_id` | 执行该 run 的 worker 标识 |
| `attempt` | 当前尝试次数，首期默认 1 |
| `temp_dir` | 运行期临时目录，任务结束后应清空 |

后续升级路径：

- Redis + RQ/Celery/Arq 队列。
- Postgres metadata store。
- 容器化算法 runner。
- Kubernetes job 或其他集群调度。

## 12. 指标体系

首版 metric profile：`core_spatial_v1`。

| 指标 | 适用范围 | 首版状态 |
|---|---|---|
| ARI | 有真实标签 | 必做 |
| NMI | 有真实标签 | 必做 |
| runtime seconds | 所有 run | 必做 |
| spatial neighbor agreement | 所有 run | 必做 |
| spatial continuity | 所有 run | 必做 |
| memory peak | 所有 run | TODO |
| HOM / COM | 有真实标签 | TODO |
| CHAOS / PAS | 空间聚类 | TODO |
| ASW | embedding / feature | TODO |
| Moran's I / Geary's C | 空间统计 | TODO |

指标输出要求：

- 每个 metric 都写入 SQLite。
- 每个 experiment 生成汇总 CSV。
- 报告中必须标注哪些指标因为缺少真实标签而未计算。

## 13. 风险与处理

| 风险 | 影响 | 首版处理 |
|---|---|---|
| 算法依赖冲突 | 算法无法同时安装或运行 | 继续使用单 uv 环境，文档标注风险 |
| `torch_sparse` 等依赖难装 | 影响 conST/STAGATE 类算法 | 首版允许 model-path adapter，后续做环境隔离 |
| 运行时间长 | Web 请求超时 | 使用后台 worker |
| 数据文件大 | 上传、复制和本地磁盘占用成本高 | 首版以 OSS URI 登记为主，服务器只保留临时缓存 |
| 无标签数据不可算 ARI/NMI | 指标不完整 | 按有标签/无标签分级展示 |
| React + FastAPI 工程量增加 | 延长首版周期 | UI 聚焦五个 benchmark 核心模块 |
| 完整论文指标未实现 | benchmark 深度不足 | 明确列为后续 TODO |

## 14. 测试计划

### 14.1 单元测试

- h5ad reader 能读取 STARmap 和 osmFISH。
- Visium reader 能读取 DLPFC 151673。
- dataset registration 能写入 SQLite。
- algorithm listing 能返回当前注册算法。
- experiment splitter 能把多数据集 x 多算法拆成 run。
- metric service 在固定输入下输出稳定 ARI/NMI/邻域一致性。
- report service 能生成 CSV、PNG、Markdown。

### 14.2 集成测试

- 登记 STARmap、DLPFC、osmFISH。
- 创建包含多个数据集和多个算法的 experiment。
- worker 执行 run 并写入 metrics/artifacts。
- experiment 详情 API 返回完整状态。
- 报告 API 返回可下载 artifact。

### 14.3 前端验收

- 数据集页面能展示 shape 和标签列。
- 算法页面能展示算法状态。
- 评测配置页面能创建 experiment。
- 运行记录页面能看到状态流转。
- 报告页面能展示指标表和空间图。

## 15. 分阶段实施建议

### 阶段 1：后端数据和存储

交付：

- SQLite schema。
- 数据集登记 API。
- h5ad / Visium reader。
- 数据集列表和详情 API。

验收：

- STARmap、DLPFC、osmFISH 能登记并解析 metadata。

### 阶段 2：Experiment 和 Worker

交付：

- ExperimentSpec。
- experiment 创建 API。
- run 拆分逻辑。
- 单进程 worker。

验收：

- 创建一个多数据集 x 多算法 experiment 后，能生成 queued runs。
- worker 能执行至少一个完整 run。

### 阶段 3：Metric 和 Report

交付：

- core_spatial_v1 指标。
- CSV / PNG / Markdown 报告。
- artifact 索引。

验收：

- 完成一个小型 experiment 后，报告目录完整生成。

### 阶段 4：React 管理后台

交付：

- 数据集模块。
- 算法模块。
- 评测配置模块。
- 运行记录模块。
- 报告/可视化模块。

验收：

- 用户可以从 Web 完成一次 benchmark 创建、运行查看和报告下载。

### 阶段 5：算法扩展

交付：

- STAGATE adapter。
- SpaceFlow adapter。
- 对应 smoke tests。

验收：

- STAGATE 和 SpaceFlow 出现在算法列表中。
- 能参与至少一个小型 benchmark run。

## 16. 当前默认决策

- 交付形态：FastAPI + React。
- 执行模型：SQLite queued runs + 低并发 worker，后续可迁移 Redis 队列。
- 存储：SQLite 元数据 + 阿里云 OSS 数据/artifact，后续可迁移 Postgres 元数据。
- 数据输入：登记 OSS h5ad / Visium 前缀，开发模式可用本地路径。
- 任务范围：空间域/聚类 benchmark。
- 指标范围：首版核心 + 空间指标，完整论文指标后续实现。
- 算法范围：当前 7 个 + STAGATE + SpaceFlow。
- 管理后台：五个核心模块，不做登录/RBAC。

## 17. 后续 TODO

- 明确 SQLite 是否直接使用标准库 `sqlite3`，还是引入 SQLAlchemy。
- 明确 React 工程使用 Vite 还是其他脚手架。
- 明确 FastAPI 项目启动命令和端口。
- 设计 `ExperimentSpec` 的最终 JSON schema。
- 确认 DLPFC 151673 的 ground truth label 列。
- 确认 osmFISH 的 label 列和空间坐标键。
- 评估 STAGATE / SpaceFlow 的最小可运行参数。
- 设计完整论文指标的优先级和验收数据。
