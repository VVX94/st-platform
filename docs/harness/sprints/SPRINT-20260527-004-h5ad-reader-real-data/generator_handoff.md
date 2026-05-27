# Generator Handoff: SPRINT-20260527-004-h5ad-reader-real-data

关联 sprint：SPRINT-20260527-004-h5ad-reader-real-data
生成日期：2026-05-27

## 实现摘要

接入真实 h5ad 数据读取，注册 STARmap/osmFISH 数据集，计算 ARI/NMI。

## 文件变更

| 文件 | 说明 |
|---|---|
| `src/st_platform/io/__init__.py` | IO 模块 |
| `src/st_platform/io/h5ad_reader.py` | read_h5ad_to_bundle() |
| `src/st_platform/api/schemas.py` | DatasetRegisterReal |
| `src/st_platform/api/routes/datasets.py` | POST /api/datasets/register-real |
| `src/st_platform/benchmark/metrics.py` | compute_ari(), compute_nmi() |
| `src/st_platform/worker/runner.py` | h5ad 加载 + ARI/NMI 计算 |
| `tests/test_io.py` | 13 个 h5ad reader 测试 |
| `tests/test_e2e.py` | 真实数据端到端测试 |

## 自测命令

| 命令 | 结果 |
|---|---|
| `PYTHONPATH=src python3 -m pytest tests/ -x` | 97 passed, 6 skipped |
