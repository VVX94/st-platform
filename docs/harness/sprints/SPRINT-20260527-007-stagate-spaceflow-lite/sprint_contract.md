# Sprint Contract: STAGATE & SpaceFlow Lite Adapters

Sprint ID：SPRINT-20260527-007-stagate-spaceflow-lite
关联任务：TASK-20260527-001-runtime-smoke-platform
状态：pending

## 本轮目标

为 STAGATE 和 SpaceFlow 算法创建轻量级适配器（lite），使用纯 numpy/sklearn 实现核心功能，无需 torch_sparse 或 gudhi 依赖。

### 算法说明

| 算法 | 原始依赖 | Lite 策略 |
|---|---|---|
| STAGATE | torch, torch_sparse | PCA + KMeans + 邻域精炼 |
| SpaceFlow | torch, gudhi | PCA + KMeans + 空间正则化 |

### 实现方案

**STAGATE Lite** (`stagate-lite`):
1. 表达矩阵 log1p + z-score 标准化
2. PCA 降维 (默认 50 维)
3. 空间坐标拼接 (加权)
4. KMeans 聚类
5. k-NN 邻域投票精炼标签

**SpaceFlow Lite** (`spaceflow-lite`):
1. 表达矩阵 log1p + z-score 标准化
2. PCA 降维 (默认 50 维)
3. 空间坐标拼接 (加权)
4. KMeans 聚类
5. 空间一致性后处理

## 明确不做

- 不做原始 STAGATE/SpaceFlow 的 torch 实现。
- 不做前端改动。
- 不做 Docker。

## 预期改动文件

| 文件 | 说明 |
|---|---|
| `src/st_platform/algorithms/stagate_lite.py` | STAGATE lite 适配器 |
| `src/st_platform/algorithms/spaceflow_lite.py` | SpaceFlow lite 适配器 |
| `src/st_platform/algorithms/builtin.py` | 注册新算法 |
| `tests/test_algos_lite.py` | 新增测试 |

## 验收测试

| 验收点 | 验证方式 | 必须通过 |
|---|---|---|
| stagate-lite 算法注册 | `list-algorithms` 包含 stagate-lite | 是 |
| spaceflow-lite 算法注册 | `list-algorithms` 包含 spaceflow-lite | 是 |
| stagate-lite demo run | `run-demo --algorithm stagate-lite` 成功 | 是 |
| spaceflow-lite demo run | `run-demo --algorithm spaceflow-lite` 成功 | 是 |
| 输出格式正确 | JSON artifacts 包含 domain_assignments | 是 |
| 指标计算 | spatial_neighbor_agreement 有值 | 是 |
| 测试通过 | `pytest tests/test_algos_lite.py` 全部通过 | 是 |
| 总测试通过 | `pytest tests/` 无新增失败 | 是 |

## 回滚和兼容性

- 纯增量添加，不修改已有算法。
- 无新依赖。
