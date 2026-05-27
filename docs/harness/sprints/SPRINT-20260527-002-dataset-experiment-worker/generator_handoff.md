# Generator Handoff: SPRINT-20260527-002-dataset-experiment-worker

关联 sprint：SPRINT-20260527-002-dataset-experiment-worker
生成日期：2026-05-27

## 实现摘要

打通完整 benchmark 链路：注册 demo 数据集 -> 创建 experiment -> worker 执行 -> 查询 metrics/artifacts。

## 文件变更

| 文件 | 说明 |
|---|---|
| `src/st_platform/api/routes/datasets.py` | 新增 POST /api/datasets/register-demo |
| `src/st_platform/api/routes/worker.py` | 新增 POST /api/worker/poll |
| `src/st_platform/api/routes/runs.py` | 新增 GET metrics/artifacts 端点 |
| `src/st_platform/api/routes/experiments.py` | 新增 experiment runs 端点 |
| `src/st_platform/api/routes/__init__.py` | 注册 worker router |
| `src/st_platform/api/schemas.py` | WorkerPollResponse, MetricOut, ArtifactOut |
| `src/st_platform/worker/runner.py` | 数据集感知 bundle 构建 |
| `web/src/pages/Experiments.tsx` | 展示 runs + worker 按钮 |
| `web/src/pages/RunDetail.tsx` | Run 详情页 |
| `web/src/App.tsx` | /runs/:runId 路由 |
| `web/src/api/client.ts` | 新增 API 函数 |
| `tests/test_e2e.py` | 端到端测试 |

## 自测命令

| 命令 | 结果 |
|---|---|
| `PYTHONPATH=src python3 -m pytest tests/ -x` | 44 passed, 6 skipped |
| `PYTHONPATH=src python3 -m st_platform list-algorithms` | 10 algorithms |

## 已知问题

- 真实 h5ad 数据读取未实现，仅支持 demo 数据。
- 前端需 npm install 才能运行。
