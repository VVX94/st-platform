# Sprint Contract: Paper-Level Metrics

Sprint ID：SPRINT-20260527-006-paper-level-metrics
关联任务：TASK-20260527-001-runtime-smoke-platform
状态：accepted

## 本轮目标

实现完整论文级指标，扩展 `core_spatial_v1` 为 `full_spatial_v1`：

### 需要新增的指标

| 指标 | 类型 | 说明 | 实现方式 |
|---|---|---|---|
| HOM (Homogeneity) | 有标签 | 每个聚类只包含一个类别的成员 | sklearn.metrics.homogeneity_score |
| COM (Completeness) | 有标签 | 同一类别的成员都在同一聚类 | sklearn.metrics.completeness_score |
| ASW (Average Silhouette Width) | 所有 run | 聚类轮廓系数，基于表达矩阵 | sklearn.metrics.silhouette_score |
| CHAOS | 所有 run | 空间混乱度：邻域内不同域的比例 | 自定义：1 - spatial_neighbor_agreement |
| PAS | 所有 run | 边界点比例：至少一个邻居在不同域的点 | 自定义：边界点数 / 总点数 |
| Moran's I | 所有 run | 空间自相关：域标签的空间聚集程度 | 自定义：基于 k-NN 权重矩阵 |
| Geary's C | 所有 run | 空间自相关：邻域差异度 | 自定义：基于 k-NN 权重矩阵 |
| memory_peak_mb | 所有 run | 算法执行期间峰值内存(MB) | tracemalloc |

### 指标分类

- **有标签数据**：ARI, NMI, HOM, COM
- **空间指标**：spatial_neighbor_agreement, CHAOS, PAS, Moran's I, Geary's C
- **通用指标**：runtime_seconds, artifact_completeness, ASW, memory_peak_mb

## 明确不做

- 不做新的算法接入。
- 不做前端页面改动（指标自动通过现有报告管道展示）。
- 不做 Docker。
- 不做 OSS。

## 预期改动文件

- `src/st_platform/benchmark/metrics.py` - 新增 7 个指标函数
- `src/st_platform/worker/runner.py` - 调用新指标 + tracemalloc 内存追踪
- `src/st_platform/benchmark/reports.py` - 报告中标注指标分类
- `tests/test_metrics.py` - 新增测试
- `tests/test_e2e.py` - 验证真实 run 产出完整指标

## 验收测试

| 验收点 | 验证方式 | 必须通过 |
|---|---|---|
| HOM 计算 | 同 NMI 输入，输出 float | 是 |
| COM 计算 | 同 NMI 输入，输出 float | 是 |
| ASW 计算 | 基于表达矩阵 + labels | 是 |
| CHAOS 计算 | 1 - spatial_neighbor_agreement | 是 |
| PAS 计算 | 边界点比例 | 是 |
| Moran's I 计算 | k-NN 权重矩阵，输出 [-1, 1] | 是 |
| Geary's C 计算 | k-NN 权重矩阵，输出 [0, 2] | 是 |
| memory_peak_mb | tracemalloc 追踪 | 是 |
| Worker 集成 | 真实 run 产出所有指标 | 是 |
| 测试通过 | test_metrics.py 全部通过 | 是 |

## 回滚和兼容性

- 保留所有已有指标。
- 新指标是增量添加，不改变已有指标的计算逻辑。
- 报告自动包含新指标。
