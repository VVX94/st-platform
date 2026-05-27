# Generator Handoff: SPRINT-20260527-006-paper-level-metrics

关联 sprint：SPRINT-20260527-006-paper-level-metrics
生成日期：2026-05-27

## 实现摘要

实现完整论文级指标：HOM, COM, ASW, CHAOS, PAS, Moran's I, Geary's C, memory_peak_mb。

## 文件变更

| 文件 | 说明 |
|---|---|
| `src/st_platform/benchmark/metrics.py` | 新增 8 个指标函数 + compute_all_metrics |
| `src/st_platform/worker/runner.py` | tracemalloc 内存追踪 + compute_all_metrics 集成 |
| `src/st_platform/benchmark/reports.py` | 指标分类着色 + 类别标注 |
| `tests/test_metrics.py` | 37 个新测试（总计 63 个） |
| `tests/test_e2e.py` | 验证新指标 |

## 自测命令

| 命令 | 结果 |
|---|---|
| `PYTHONPATH=src python3 -m pytest tests/ -x` | 137 passed, 6 skipped |
