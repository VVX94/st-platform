# Session: Sprint 006 Paper-Level Metrics

日期：2026-05-27 23:00
参与角色：Generator, Evaluator
关联任务：TASK-20260527-001-runtime-smoke-platform
关联 sprint：SPRINT-20260527-006-paper-level-metrics

## 执行动作

| 步骤 | 动作 | 结果 |
|---|---|---|
| 1 | Generator 实现论文级指标 | 5 文件修改 |
| 2 | 运行测试 | 137 passed, 6 skipped |
| 3 | Evaluator 验证 | 全部 10 验收点通过 |

## 新增指标

| 指标 | 类型 | 说明 |
|---|---|---|
| HOM | 有标签 | homogeneity_score |
| COM | 有标签 | completeness_score |
| ASW | 通用 | silhouette_score (subsampled) |
| CHAOS | 空间 | 1 - spatial_neighbor_agreement |
| PAS | 空间 | 边界点比例 |
| Moran's I | 空间 | k-NN 权重空间自相关 |
| Geary's C | 空间 | k-NN 权重空间自相关 |
| memory_peak_mb | 通用 | tracemalloc 峰值内存 |

## 决策

- Sprint 6 accepted。完整论文级指标已实现。

## 指标体系总览

| 指标 | 需要标签 | 类别 |
|---|---|---|
| ARI | 是 | Label Dependent |
| NMI | 是 | Label Dependent |
| HOM | 是 | Label Dependent |
| COM | 是 | Label Dependent |
| spatial_neighbor_agreement | 否 | Spatial |
| CHAOS | 否 | Spatial |
| PAS | 否 | Spatial |
| Moran's I | 否 | Spatial |
| Geary's C | 否 | Spatial |
| ASW | 否 | General |
| runtime_seconds | 否 | General |
| artifact_completeness | 否 | General |
| memory_peak_mb | 否 | General |
