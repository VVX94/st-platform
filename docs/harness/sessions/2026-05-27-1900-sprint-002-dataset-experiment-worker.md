# Session: Sprint 002 Dataset + Experiment + Worker E2E

日期：2026-05-27 19:00
参与角色：Generator, Evaluator
关联任务：TASK-20260527-001-runtime-smoke-platform
关联 sprint：SPRINT-20260527-002-dataset-experiment-worker

## 用户请求

继续实现 benchmark 平台，打通完整 benchmark 链路。

## 本轮上下文

Sprint 1 已建立骨架。Sprint 2 目标是打通：注册数据集 -> 创建 experiment -> worker 执行 -> 查询 metrics/artifacts。

## 执行动作

| 步骤 | 动作 | 结果 |
|---|---|---|
| 1 | Generator 实现 Sprint 2 | 12 文件创建/修改 |
| 2 | 运行测试 | 44 passed, 6 skipped |
| 3 | Evaluator 独立验证 | 全部 9 验收点通过 |

## 修改文件

| 文件 | 修改类型 | 说明 |
|---|---|---|
| `src/st_platform/api/routes/datasets.py` | MODIFY | 新增 register-demo 端点 |
| `src/st_platform/api/routes/worker.py` | CREATE | POST /api/worker/poll |
| `src/st_platform/api/routes/runs.py` | MODIFY | 新增 metrics/artifacts 端点 |
| `src/st_platform/api/routes/experiments.py` | MODIFY | 新增 experiment runs 端点，改进创建逻辑 |
| `src/st_platform/api/routes/__init__.py` | MODIFY | 注册 worker router |
| `src/st_platform/api/schemas.py` | MODIFY | 补充 schemas |
| `src/st_platform/worker/runner.py` | MODIFY | 数据集感知逻辑 |
| `web/src/pages/Experiments.tsx` | MODIFY | 展示 runs，worker 按钮 |
| `web/src/pages/RunDetail.tsx` | CREATE | Run 详情页 |
| `web/src/App.tsx` | MODIFY | 新增 RunDetail 路由 |
| `web/src/api/client.ts` | MODIFY | 新增 API 函数 |
| `tests/test_e2e.py` | CREATE | 端到端测试 |

## 验证记录

| 命令/检查 | 结果 |
|---|---|
| `PYTHONPATH=src python3 -m pytest tests/ -x` | 44 passed, 6 skipped |
| `PYTHONPATH=src python3 -m st_platform list-algorithms` | 10 algorithms |
| Evaluator report | passed |

## 决策

- Sprint 2 accepted。核心 benchmark 链路已打通。

## 下一步

Sprint 3：指标计算增强 + 报告生成 + CSV/PNG/Markdown 输出。
