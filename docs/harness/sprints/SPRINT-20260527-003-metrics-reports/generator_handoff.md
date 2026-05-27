# Generator Handoff: SPRINT-20260527-003-metrics-reports

关联 sprint：SPRINT-20260527-003-metrics-reports
生成日期：2026-05-27

## 实现摘要

增强指标计算和报告生成：metrics 模块、CSV/PNG/Markdown 报告、worker 集成、report API、前端报告页。

## 文件变更

| 文件 | 说明 |
|---|---|
| `src/st_platform/benchmark/metrics.py` | spatial_neighbor_agreement, artifact_completeness, runtime |
| `src/st_platform/benchmark/reports.py` | CSV, PNG, Markdown 报告生成 |
| `src/st_platform/benchmark/__init__.py` | 导出新函数 |
| `src/st_platform/worker/runner.py` | 成功后自动生成报告 |
| `src/st_platform/api/routes/experiments.py` | GET /api/experiments/{id}/report |
| `src/st_platform/api/schemas.py` | ExperimentReportOut |
| `web/src/pages/Reports.tsx` | 报告页面 |
| `web/src/App.tsx` | Reports 路由 |
| `web/src/api/client.ts` | getExperimentReport |
| `tests/test_metrics.py` | 16 个指标测试 |
| `tests/test_reports.py` | 13 个报告测试 |

## 自测命令

| 命令 | 结果 |
|---|---|
| `PYTHONPATH=src python3 -m pytest tests/ -x` | 73 passed, 6 skipped |

## 已知问题

- Evaluator 错误地报告前端文件不存在（实际 Reports.tsx 11.4KB 已创建）。
- 报告存本地 runs/ 目录，未对接 OSS。
