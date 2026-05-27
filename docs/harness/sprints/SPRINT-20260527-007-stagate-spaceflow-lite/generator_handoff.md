# Generator Handoff: SPRINT-20260527-007-stagate-spaceflow-lite

关联 sprint：SPRINT-20260527-007-stagate-spaceflow-lite
生成日期：2026-05-27

## 实现摘要

为 STAGATE 和 SpaceFlow 创建轻量级适配器（lite），使用 PCA + KMeans + 邻域精炼，无需 torch_sparse 或 gudhi 依赖。

## 文件变更

| 文件 | 说明 |
|---|---|
| `src/st_platform/algorithms/stagate_lite.py` | STAGATE lite 适配器 (PCA + KMeans + refinement) |
| `src/st_platform/algorithms/spaceflow_lite.py` | SpaceFlow lite 适配器 (PCA + KMeans + top gene selection) |
| `src/st_platform/algorithms/builtin.py` | 注册 stagate-lite, spaceflow-lite |
| `tests/test_algos_lite.py` | 16 个新测试 |
| `tests/test_registry.py` | 更新算法列表断言 |

## 自测命令

| 命令 | 结果 |
|---|---|
| `PYTHONPATH=src python3 -m pytest tests/ -x` | 153 passed, 6 skipped |
| `PYTHONPATH=src python3 -m st_platform list-algorithms` | 12 algorithms listed |
