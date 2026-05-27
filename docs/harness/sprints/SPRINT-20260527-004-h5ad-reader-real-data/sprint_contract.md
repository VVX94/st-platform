# Sprint Contract: h5ad Reader + Real Data + ARI/NMI

Sprint ID：SPRINT-20260527-004-h5ad-reader-real-data
关联任务：TASK-20260527-001-runtime-smoke-platform
状态：accepted

## 本轮目标

接入真实 h5ad 数据，实现完整 benchmark 链路：

1. 创建 `src/st_platform/io/` 模块，实现 h5ad reader。
2. 注册真实 STARmap 数据集（1207 spots, 1020 genes, 有 ground truth label）。
3. Worker 从 h5ad 文件加载真实数据构建 SpatialDataBundle。
4. 运行 spagcn-lite 时计算 ARI/NMI（有 ground truth）。
5. 报告中包含 ARI/NMI 指标。
6. 支持注册 osmFISH 数据集（4839 spots, 33 genes）。

## 明确不做

- 不做 Visium 目录读取（只做 h5ad）。
- 不做 OSS 上传/下载。
- 不做 Docker。
- 不做 STAGATE/SpaceFlow 新算法接入。

## 真实数据路径

- STARmap: `/home/wx/project/aaa/spatial-transcriptomic/经典算法/BenchmarkST/ADEPT/dataset/STARmap/STARmap_20180505_BY3_1k.h5ad`
  - Shape: (1207, 1020)
  - Obs columns: Total_counts, X, Y, label
  - obsm['spatial']: (1207, 2)
  - Ground truth: obs['label']
- osmFISH: `/home/wx/project/aaa/spatial-transcriptomic/经典算法/SDMBench/Data/osmfish.h5ad`
  - Shape: (4839, 33)
  - Obs columns: ClusterName, ClusterID, Region
  - obsm['spatial']: (4839, 2)
  - Ground truth: obs['Region']

## 预期改动文件

- `src/st_platform/io/__init__.py` - 新建
- `src/st_platform/io/h5ad_reader.py` - 新建：read_h5ad_to_bundle(path) -> SpatialDataBundle
- `src/st_platform/api/routes/datasets.py` - 修改：register-real 端点注册本地 h5ad 文件
- `src/st_platform/worker/runner.py` - 修改：从 h5ad 文件加载真实数据
- `src/st_platform/benchmark/metrics.py` - 修改：增加 ARI/NMI 计算
- `src/st_platform/benchmark/reports.py` - 修改：报告中包含 ARI/NMI
- `tests/test_io.py` - 新建：h5ad reader 测试
- `tests/test_e2e.py` - 修改：增加真实数据端到端测试

## 验收测试

| 验收点 | 验证方式 | 必须通过 |
|---|---|---|
| h5ad reader | read_h5ad_to_bundle 能读取 STARmap 文件 | 是 |
| 真实数据集注册 | POST /api/datasets/register-real 返回 201 | 是 |
| Worker 加载真实数据 | Worker 从 h5ad 构建 SpatialDataBundle | 是 |
| ARI/NMI 计算 | 有 ground truth 时输出 ARI 和 NMI | 是 |
| 报告含 ARI/NMI | report.md 和 CSV 包含 ARI/NMI | 是 |
| osmFISH 支持 | 能注册 osmFISH 数据集 | 是 |
| 测试通过 | test_io.py + test_e2e.py 全部通过 | 是 |
| CLI 不破坏 | list-algorithms 仍正常 | 是 |

## 回滚和兼容性

- 保留 Sprint 1-3 所有功能。
- demo 数据集仍可用。
- h5ad 读取失败给出清晰错误信息。
