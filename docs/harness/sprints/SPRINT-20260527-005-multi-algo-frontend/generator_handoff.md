# Generator Handoff: SPRINT-20260527-005-multi-algo-frontend

关联 sprint：SPRINT-20260527-005-multi-algo-frontend
生成日期：2026-05-27

## 实现摘要

多算法对比 benchmark + 前端体验增强。

## 文件变更

| 文件 | 说明 |
|---|---|
| `src/st_platform/benchmark/reports.py` | 算法对比表 |
| `src/st_platform/api/schemas.py` | comparison_summary |
| `src/st_platform/api/routes/datasets.py` | register-demo-all |
| `src/st_platform/api/routes/experiments.py` | 对比摘要 |
| `web/src/pages/Experiments.tsx` | 自动刷新 + 对比表 |
| `web/src/pages/Dashboard.tsx` | 概览统计 |
| `web/src/pages/Datasets.tsx` | 详情 + 注册按钮 |
| `web/src/pages/Algorithms.tsx` | 标签 + 详情 |
| `web/src/api/client.ts` | 新 API 函数 |
| `tests/test_multi_algo.py` | 3 个多算法测试 |

## 自测命令

| 命令 | 结果 |
|---|---|
| `PYTHONPATH=src python3 -m pytest tests/ -x` | 100 passed, 6 skipped |
