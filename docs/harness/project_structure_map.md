# ST Platform 当前项目结构审计

审计日期：2026-05-27  
审计范围：`/home/wx/project/aaa/spatial-transcriptomic/经典算法/st-platform`  
目的：为后续 Planner / Generator / Evaluator 三智能体编码提供稳定的项目地图和审计基线。

## 1. 项目定位

`st-platform` 当前是空间转录组算法平台底座，已经具备：

- 统一任务类型。
- 统一数据对象。
- 算法注册表。
- 本地 runner。
- CLI demo 入口。
- 多个空间域识别算法 adapter。
- STARmap 真实数据演示结果。

当前还不是完整 Web benchmark 平台。API、Web、持久化数据库、异步队列、部署编排、公开访问保护和生产监控仍待建设。

## 2. 顶层结构

```text
st-platform/
├─ docs/                         # 设计、路线图、项目管理 spec
├─ examples/                     # quickstart 示例
├─ presentation_results/          # 演示级结果和 PPT 展示素材
├─ runs/                         # LocalRunner 运行产物
├─ scripts/                      # 实验脚本
├─ src/st_platform/              # Python 平台源码
├─ tests/                        # 当前单元测试
├─ pyproject.toml                # Python 包配置和 CLI entrypoint
└─ README.md                     # 项目说明
```

## 3. 源码模块

```text
src/st_platform/
├─ __main__.py                   # python -m st_platform 入口
├─ cli.py                        # st-platform CLI 命令
├─ algorithms/                   # 算法接口、mock 算法和真实算法 adapter
├─ core/                         # registry、runner、task catalog
├─ data/                         # DatasetRef / DataAsset / SpatialDataBundle
├─ tasks/                        # 任务类型和默认任务定义
└─ workflows/                    # PlatformService 组合入口
```

### 3.1 `algorithms/`

当前职责：

- 定义 `Algorithm` / `AlgorithmSpec` 等算法契约。
- 注册内置 mock 算法和真实空间域算法。
- 已有 adapter：`spagcn`、`graphst`、`sedr`、`ccst`、`const`、`deepst`、`spagcn-lite`。

后续注意：

- 不应把 benchmark 编排、数据库访问、Web 请求处理写入 `algorithms/`。
- 每个算法 adapter 应继续只负责输入转换、算法调用、输出 artifact。

### 3.2 `core/`

当前职责：

- `registry.py`：算法注册和按任务查询。
- `runner.py`：本地执行算法、记录 status、产出 run 目录。

后续注意：

- Web benchmark runner 可以复用当前 `LocalRunner`，但生产任务队列需要在 `benchmark/` 或 `worker/` 层封装。

### 3.3 `data/`

当前职责：

- 定义平台内部数据 bundle。
- 以 `DatasetRef`、`DataAsset`、`SpatialDataBundle` 表达数据集和资产。

后续注意：

- h5ad / Visium 读取器应新增到独立 `io/` 或 `benchmark/io` 层，不应塞入 model dataclass。

### 3.4 `tasks/`

当前职责：

- 定义任务类型：数据摄入、质控、空间域识别、去卷积、跨模态映射、可视化等。

后续注意：

- benchmark 平台首要使用 `domain_detection`，但结构应保留多任务扩展能力。

### 3.5 `workflows/`

当前职责：

- `PlatformService` 组合 task catalog、algorithm registry 和 runner。
- 构造小型 demo dataset。

后续注意：

- API 层可以引用 service，但不应让 service 承担数据库、队列、报告生成全部职责。

## 4. 入口和命令

当前 CLI entrypoint 来自 `pyproject.toml`：

```text
st-platform = "st_platform.cli:main"
```

常用命令：

```bash
python -m st_platform list-tasks
python -m st_platform list-algorithms
python -m st_platform run-demo --task domain_detection --algorithm spagcn-lite
```

真实算法环境常用命令：

```bash
UV_CACHE_DIR=/tmp/uv-cache .venv-spagcn/bin/python -m st_platform run-demo --task domain_detection --algorithm spagcn
```

## 5. 现有测试

```text
tests/
├─ test_cli.py
├─ test_registry.py
└─ test_runner.py
```

当前测试覆盖平台底座和 CLI 基础能力。完整 Web benchmark 平台还需要新增：

- API 测试。
- dataset reader 测试。
- worker 状态流转测试。
- metric/report 测试。
- frontend E2E 测试。
- Docker Compose smoke test。

## 6. 现有文档

```text
docs/
├─ architecture.md
├─ benchmark_platform_design_plan.md
├─ project_roadmap.md
└─ st_platform_project_management_spec.md
```

文档定位：

- `architecture.md`：早期平台架构说明。
- `project_roadmap.md`：早期 MVP 路线图。
- `st_platform_project_management_spec.md`：截至真实算法和 STARmap demo 的项目管理 spec。
- `benchmark_platform_design_plan.md`：当前需要升级为完整 Web benchmark 平台实施总纲。

## 7. 现有产物

```text
presentation_results/starmap_domain_demo/
├─ ppt_organization_notes.md
├─ starmap_algorithm_summary.csv
├─ starmap_algorithm_summary.json
├─ starmap_dataset_summary.json
├─ starmap_domain_grid.png
├─ starmap_domain_predictions.csv
├─ starmap_ground_truth.png
└─ starmap_metrics_bar.png
```

`runs/` 下存在大量 LocalRunner 运行产物，主要是各算法的 `*-domains.json` 和部分 CCST 训练权重。后续审计不直接复制这些产物，而是在 `docs/harness/artifacts/` 中记录 manifest。

## 8. 后续新增模块建议

完整 Web benchmark 平台建议逐步新增：

```text
src/st_platform/
├─ api/                          # FastAPI routes / schemas / dependencies
├─ benchmark/                    # experiment / metrics / reports / orchestration
├─ io/                           # h5ad / Visium reader
├─ storage/                      # database repositories and artifact index
├─ worker/                       # async worker entrypoint and queue adapter

web/                             # React 管理后台
deploy/                          # 项目主功能完成后补充 Docker Compose, env examples, reverse proxy
```

这些目录尚未存在，后续由 Generator 在对应 sprint 中创建。
