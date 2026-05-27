# ST Platform 使用指南

## 目录

- [项目简介](#项目简介)
- [系统架构](#系统架构)
- [环境准备](#环境准备)
- [快速启动](#快速启动)
- [模块详解](#模块详解)
- [使用流程](#使用流程)
- [CLI 命令行工具](#cli-命令行工具)
- [API 接口参考](#api-接口参考)
- [前端页面说明](#前端页面说明)
- [算法列表](#算法列表)
- [指标体系](#指标体系)
- [常见问题](#常见问题)

---

## 项目简介

ST Platform 是一个**空间转录组学算法基准测试平台**，用于统一评测空间域检测（spatial domain detection）等任务的算法性能。

核心能力：
- 注册和管理空间转录组数据集（h5ad 格式）
- 对比运行多种空间域检测算法
- 自动计算 13 项评价指标（ARI、NMI、ASW、CHAOS 等）
- 生成可视化报告（散点图、柱状图、雷达图、CSV）
- 通过 Web 界面管理实验、查看进度、下载结果

---

## 系统架构

```
┌─────────────┐     HTTP      ┌──────────────┐     SQLAlchemy     ┌──────────┐
│  React Web  │ ──────────── → │   FastAPI     │ ──────────────── → │  SQLite  │
│  (Vite)     │ ← ────────── │   Backend     │ ← ─────────────── │  (WAL)   │
└─────────────┘               └──────┬───────┘                    └──────────┘
                                     │
                                     │ poll
                                     ▼
                              ┌──────────────┐
                              │    Worker     │
                              │  (轮询执行)   │
                              └──────┬───────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
              ┌──────────┐    ┌──────────┐    ┌──────────┐
              │ 算法适配器 │    │ 指标计算  │    │ 报告生成  │
              │ (12种算法) │    │ (13项)   │    │ CSV/PNG  │
              └──────────┘    └──────────┘    └──────────┘
```

**三大组件：**
1. **FastAPI 后端** — 提供 REST API，管理元数据（SQLite），调度任务
2. **Worker 工作进程** — 轮询 SQLite 队列，执行算法，计算指标，生成报告
3. **React 前端** — Ant Design UI，ECharts 图表，中英文切换

---

## 环境准备

### Python 环境（使用 uv）

```bash
# 安装 uv（如果没有）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
cd st-platform
uv venv .venv-spagcn --python 3.11

# 安装项目依赖
uv pip install -e ".[dev]" --cache-dir /tmp/uv-cache

# 如需运行完整算法（非 lite），还需安装对应算法包：
# uv pip install --python .venv-spagcn/bin/python -e ../SEDR
# uv pip install --python .venv-spagcn/bin/python -e ../GraphST pot
# uv pip install --python .venv-spagcn/bin/python -e ../SpaGCN/SpaGCN_package
```

### Node.js 环境

```bash
cd web
npm install
```

### 依赖说明

**Python 核心依赖：**
| 包 | 用途 |
|---|---|
| fastapi | Web API 框架 |
| uvicorn | ASGI 服务器 |
| sqlalchemy | ORM，SQLite 访问 |
| pydantic | 数据校验 |
| numpy | 数值计算 |
| scikit-learn | 聚类、降维、指标 |
| anndata | h5ad 文件读取 |
| matplotlib | 报告图表生成 |
| pandas | 数据表格处理 |

**前端依赖：**
| 包 | 用途 |
|---|---|
| react | UI 框架 |
| antd | 企业级组件库 |
| echarts / echarts-for-react | 数据可视化 |
| react-i18next / i18next | 国际化（中/英） |
| react-router-dom | 路由 |

---

## 快速启动

### 方式一：使用启动脚本

```bash
# 终端 1：启动后端 API（端口 8000）
bash scripts/start_api.sh

# 终端 2：启动前端（端口 5173）
bash scripts/start_web.sh

# 终端 3：启动 Worker 轮询（可选，也可通过 Web 触发）
bash scripts/start_worker.sh
```

### 方式二：手动启动

```bash
# 后端 API
PYTHONPATH=src python3 -m uvicorn st_platform.api.app:create_app --factory --host 0.0.0.0 --port 8000 --reload

# 前端
cd web && npm run dev

# Worker（可选）
PYTHONPATH=src python3 -c "
from st_platform.worker import poll_runs
from st_platform.storage import SessionLocal, init_db
from st_platform.workflows import create_platform_service
init_db()
svc = create_platform_service()
db = SessionLocal()
poll_runs(db, svc.runner, svc.registry, svc.build_demo_bundle)
db.close()
"
```

启动后访问：
- **前端界面**：http://localhost:5173
- **API 文档**：http://localhost:8000/docs（Swagger UI）
- **健康检查**：http://localhost:8000/api/health

---

## 模块详解

### 1. `algorithms/` — 算法适配器层

**职责**：将各种空间域检测算法封装为统一接口。

**核心抽象**：
- `Algorithm` — 抽象基类，所有算法必须实现 `run(data, parameters, context)` 方法
- `AlgorithmSpec` — 算法元数据（ID、名称、版本、标签）
- `AlgorithmOutput` — 算法输出（摘要、产物、指标、警告）

**算法分类**：
- **Mock 算法**（demo-qc, mock-domain, mock-deconv）— 用于测试，无需外部依赖
- **Lite 算法**（spagcn-lite, stagate-lite, spaceflow-lite）— 仅需 numpy + sklearn，无需 GPU
- **Full 算法**（ccst, const, deepst, graphst, sedr, spagcn）— 需要对应的外部算法包

**如何添加新算法**：
1. 在 `algorithms/` 下创建新的 `.py` 文件
2. 继承 `Algorithm` 基类，实现 `run()` 方法
3. 在 `builtin.py` 的 `build_builtin_algorithms()` 中注册

### 2. `api/` — FastAPI 后端

**职责**：提供 REST API，处理前端请求。

**关键文件**：
- `app.py` — 应用工厂，lifespan 管理数据库初始化
- `deps.py` — 依赖注入（数据库会话、PlatformService 单例）
- `schemas.py` — Pydantic 请求/响应模型
- `routes/` — 7 个路由模块（health, algorithms, datasets, experiments, runs, artifacts, worker）

### 3. `benchmark/` — 基准测试引擎

**职责**：计算指标、生成报告。

- `metrics.py` — 13 项指标计算函数
- `reports.py` — CSV / PNG / Markdown 报告生成
- `experiment.py` — 实验规格定义，将实验拆分为多个 Run

### 4. `storage/` — 数据持久化

**职责**：SQLite 数据库管理。

- `database.py` — SQLAlchemy 引擎（WAL 模式）、会话工厂
- `models.py` — 5 个 ORM 模型（Dataset, Experiment, Run, Metric, Artifact）
- `repositories.py` — 5 个仓库类，封装数据库查询

**数据库表结构**：
```
datasets        — 数据集注册信息
experiments     — 实验定义（关联多个 Run）
runs            — 单次算法运行（状态机：queued → running → succeeded/failed）
metrics         — 运行指标（ARI, NMI 等）
artifacts       — 运行产物（CSV, PNG 等文件路径）
```

### 5. `worker/` — 任务执行器

**职责**：轮询 SQLite 队列，执行算法运行。

`poll_runs()` 的执行流程：
1. 查询状态为 `queued` 的 Run
2. 标记为 `running`
3. 加载数据集（h5ad 或 demo 数据）
4. 调用算法适配器的 `run()` 方法
5. 计算所有适用的指标
6. 生成报告产物（CSV、PNG）
7. 标记为 `succeeded` 或 `failed`

### 6. `io/` — 数据读取

**职责**：读取 h5ad 格式的空间转录组数据。

`read_h5ad_to_bundle()` 将 h5ad 文件转换为平台统一的 `SpatialDataBundle` 格式。

### 7. `tasks/` — 任务定义

**职责**：定义平台支持的任务类型。

| 任务类型 | 说明 |
|---|---|
| data_ingest | 数据导入 |
| quality_control | 质量控制 |
| domain_detection | 空间域检测（主要任务） |
| deconvolution | 反卷积 |
| cross_modal_mapping | 跨模态映射 |

### 8. `workflows/` — 业务编排

**职责**：组装 TaskCatalog、AlgorithmRegistry、LocalRunner，提供统一的 PlatformService。

---

## 使用流程

### 完整基准测试流程

```
注册数据集 → 创建实验 → 触发 Worker → 查看进度 → 查看报告
```

#### 步骤 1：注册数据集

**方式 A：注册演示数据集（快速体验）**
```bash
curl -X POST http://localhost:8000/api/datasets/register-demo
# 或注册所有演示数据集
curl -X POST http://localhost:8000/api/datasets/register-demo-all
```

**方式 B：注册真实数据集**
```bash
curl -X POST http://localhost:8000/api/datasets/register-real \
  -H "Content-Type: application/json" \
  -d '{
    "name": "STARmap Mouse Visual Cortex",
    "path": "/path/to/starmap.h5ad",
    "label_column": "label"
  }'
```

h5ad 文件要求：
- 包含 `X` 或 `layers` 中的表达矩阵
- 包含 `obsm["spatial"]` 中的空间坐标
- 如需计算 ARI/NMI 等标签指标，需在 `obs` 中包含标签列

#### 步骤 2：创建实验

```bash
curl -X POST http://localhost:8000/api/experiments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "STARmap Benchmark",
    "task_type": "domain_detection",
    "algorithm_ids": ["spagcn-lite", "stagate-lite", "spaceflow-lite"],
    "dataset_id": "<上一步返回的 dataset_id>"
  }'
```

系统会自动为每个算法创建一个状态为 `queued` 的 Run。

#### 步骤 3：触发 Worker 执行

**方式 A：手动触发**
```bash
curl -X POST http://localhost:8000/api/worker/poll
```

**方式 B：启动 Worker 轮询脚本**
```bash
bash scripts/start_worker.sh
```

**方式 C：通过 Web 界面**
在 Experiments 页面点击 "Run Worker" 按钮。

#### 步骤 4：查看进度

- Web 界面 Experiments 页面会自动刷新（每 3 秒）
- 进度条显示 completed / total
- 状态标签：queued（灰）→ running（蓝）→ succeeded（绿）/ failed（红）

#### 步骤 5：查看报告

- **Reports 页面**：柱状图对比各算法指标、雷达图多维对比、指标汇总表
- **RunDetail 页面**：单次运行的详细指标、执行时间线、产物下载
- **产物文件**：metrics.csv、domain_predictions.csv、domain_grid_plot.png、metrics_bar_plot.png

---

## CLI 命令行工具

```bash
# 设置 PYTHONPATH
export PYTHONPATH=src

# 列出所有支持的任务类型
python3 -m st_platform list-tasks

# 列出所有已注册算法
python3 -m st_platform list-algorithms

# 按任务类型筛选算法
python3 -m st_platform list-algorithms --task domain_detection

# 运行演示（使用内置 9 点数据集）
python3 -m st_platform run-demo --task domain_detection --algorithm spagcn-lite
```

---

## API 接口参考

启动后端后访问 http://localhost:8000/docs 查看完整的 Swagger 文档。

### 核心接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 健康检查 |
| GET | `/api/algorithms` | 列出所有算法 |
| GET | `/api/datasets` | 列出所有数据集 |
| POST | `/api/datasets/register-demo` | 注册 STARmap 演示数据集 |
| POST | `/api/datasets/register-demo-all` | 注册所有演示数据集 |
| POST | `/api/datasets/register-real` | 注册真实 h5ad 数据集 |
| POST | `/api/experiments` | 创建实验（自动创建 Run 队列） |
| GET | `/api/experiments` | 列出所有实验 |
| GET | `/api/experiments/{id}/report` | 获取实验报告（含指标对比） |
| GET | `/api/runs` | 列出所有运行 |
| GET | `/api/runs/{id}` | 获取运行详情 |
| GET | `/api/runs/{id}/metrics` | 获取运行指标 |
| POST | `/api/worker/poll` | 触发一次 Worker 轮询 |
| GET | `/api/artifacts/file?path=...` | 下载产物文件 |

---

## 前端页面说明

| 页面 | 路由 | 功能 |
|---|---|---|
| **Dashboard** | `/` | 平台概览：API 状态、算法/数据集/实验/运行数量统计、运行状态饼图、最近实验和运行列表 |
| **Datasets** | `/datasets` | 数据集管理：查看已注册数据集、注册演示数据集、注册真实 h5ad 数据集（弹窗表单） |
| **Algorithms** | `/algorithms` | 算法浏览：按任务类型分组、按算法家族着色标签、展开查看描述 |
| **Experiments** | `/experiments` | 实验管理：创建实验（选算法+数据集）、查看运行进度、触发 Worker、算法对比柱状图 |
| **Reports** | `/reports` | 报告查看：指标对比柱状图、多指标雷达图、指标汇总表、产物图片预览、CSV 下载 |
| **RunDetail** | `/runs/:id` | 运行详情：执行时间线、指标水平柱状图、错误日志、产物列表 |

### 国际化

点击右上角 "中文" / "EN" 按钮切换语言。支持中英文，覆盖所有页面文本和指标名称。

---

## 算法列表

### 当前已注册的 12 种算法

| ID | 名称 | 类型 | 依赖 |
|---|---|---|---|
| `demo-qc` | Demo QC | Mock | 无 |
| `mock-domain` | Mock Domain Detection | Mock | 无 |
| `mock-deconv` | Mock Deconvolution | Mock | 无 |
| `spagcn-lite` | SpaGCN Lite | Lite | numpy + sklearn |
| `stagate-lite` | STAGATE Lite | Lite | numpy + sklearn |
| `spaceflow-lite` | SpaceFlow Lite | Lite | numpy + sklearn |
| `spagcn` | SpaGCN | Full | SpaGCN 包 |
| `ccst` | CCST | Full | torch-geometric + BenchmarkST/CCST |
| `const` | conST | Full | torch + BenchmarkST/conST |
| `deepst` | DeepST | Full | torch + BenchmarkST/DeepST |
| `graphst` | GraphST | Full | GraphST 包 |
| `sedr` | SEDR | Full | SEDR 包 |

**建议**：初次体验使用 Lite 算法（无需 GPU 和 PyTorch），正式评测使用 Full 算法。

### 运行 Full 算法的前置条件

Full 算法需要对应的外部算法仓库克隆到 st-platform 同级目录：

```
parent/
├── st-platform/          ← 本项目
├── BenchmarkST/          ← 包含 CCST, conST, DeepST
│   ├── CCST/
│   ├── conST/
│   └── DeepST/
├── GraphST/              ← GraphST 包
├── SEDR/                 ← SEDR 包
└── SpaGCN/               ← SpaGCN 包
```

---

## 指标体系

### 13 项评价指标

| 指标 | 全称 | 说明 | 需要标签 |
|---|---|---|---|
| ARI | Adjusted Rand Index | 聚类与真实标签的相似度 | 是 |
| NMI | Normalized Mutual Information | 互信息归一化 | 是 |
| HOM | Homogeneity | 同质性 | 是 |
| COM | Completeness | 完整性 | 是 |
| ASW | Average Silhouette Width | 轮廓系数（表达特征） | 否 |
| CHAOS | CHAOS Score | 1 - 空间邻域一致性 | 否 |
| PAS | Pathology-Aware Spatial | 边界区域比例 | 否 |
| Moran's I | Moran's I | 空间自相关（正） | 否 |
| Geary's C | Geary's C | 空间自相关（负） | 否 |
| Runtime | Runtime | 运行时间（秒） | 否 |
| Memory | Memory Peak | 内存峰值（MB） | 否 |
| Spatial Agreement | Spatial Neighbor Agreement | 邻域标签一致比例 | 否 |
| Artifact Completeness | Artifact Completeness | 产物完整度 | 否 |

**说明**：ARI、NMI、HOM、COM 需要数据集中有真实标签（ground truth）。其他指标仅需空间坐标和预测结果。

---

## 常见问题

### Q: Worker 没有执行 Run？

确保 Worker 正在运行（`bash scripts/start_worker.sh`），或手动触发 `POST /api/worker/poll`。也可以在 Web 的 Experiments 页面点击 "Run Worker" 按钮。

### Q: 算法运行失败？

检查 RunDetail 页面的错误日志。常见原因：
- Full 算法缺少外部依赖包
- h5ad 文件格式不正确（缺少 spatial 坐标）
- 内存不足

### Q: 如何查看 API 文档？

访问 http://localhost:8000/docs（Swagger UI）或 http://localhost:8000/redoc（ReDoc）。

### Q: 数据库在哪里？

默认在项目根目录的 `st_platform.db`（SQLite）。可通过环境变量 `ST_PLATFORM_DB_URL` 修改。

### Q: 如何重置数据库？

```bash
rm st_platform.db
# 重启 API 服务会自动重建表
```

### Q: 如何使用自己的数据集？

准备一个 h5ad 文件，确保包含：
- `X` 或 `layers` 中的表达矩阵
- `obsm["spatial"]` 中的空间坐标（N×2 矩阵）
- `obs` 中的标签列（可选，用于计算 ARI/NMI）

然后通过 API 注册：
```bash
curl -X POST http://localhost:8000/api/datasets/register-real \
  -H "Content-Type: application/json" \
  -d '{"name": "My Dataset", "path": "/path/to/data.h5ad", "label_column": "cell_type"}'
```

### Q: 如何添加新算法？

1. 在 `src/st_platform/algorithms/` 下创建新文件
2. 继承 `Algorithm` 基类
3. 实现 `run(data: SpatialDataBundle, parameters: dict, context: dict) -> AlgorithmOutput`
4. 在 `builtin.py` 的 `build_builtin_algorithms()` 中实例化并添加到列表
5. 运行测试验证：`PYTHONPATH=src python3 -m pytest tests/`
