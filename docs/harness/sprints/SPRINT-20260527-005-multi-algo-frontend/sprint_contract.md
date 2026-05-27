# Sprint Contract: Multi-Algorithm Benchmark + Frontend Polish

Sprint ID：SPRINT-20260527-005-multi-algo-frontend
关联任务：TASK-20260527-001-runtime-smoke-platform
状态：accepted

## 本轮目标

实现多算法对比 benchmark 和前端体验增强：

1. 支持创建包含多个算法的 experiment（spagcn-lite + mock-domain）。
2. Worker 依次执行所有算法 runs。
3. Report 对比多个算法的 metrics（ARI, NMI, runtime, spatial_neighbor_agreement）。
4. 前端 Experiment 详情页展示算法对比表。
5. 前端支持运行状态自动刷新（polling）。
6. 前端 Dashboard 展示最近 experiments 和 runs 概览。
7. 支持同时注册 STARmap 和 osmFISH 数据集。
8. 创建多数据集 x 多算法 experiment。

## 明确不做

- 不做 STAGATE/SpaceFlow 新算法接入。
- 不做 OSS。
- 不做 Docker。
- 不做用户登录。

## 预期改动文件

- `src/st_platform/api/routes/experiments.py` - 改进：多算法 experiment 创建
- `src/st_platform/api/routes/datasets.py` - 改进：批量注册 demo 数据集
- `src/st_platform/benchmark/reports.py` - 改进：算法对比表
- `web/src/pages/Experiments.tsx` - 改进：算法对比表、状态自动刷新
- `web/src/pages/Dashboard.tsx` - 改进：概览统计
- `web/src/pages/Datasets.tsx` - 改进：显示数据集详情
- `web/src/pages/Algorithms.tsx` - 改进：显示算法详情和参数
- `web/src/App.tsx` - 路由改进
- `web/src/api/client.ts` - API 函数补充
- `tests/test_multi_algo.py` - 多算法 benchmark 测试

## 验收测试

| 验收点 | 验证方式 | 必须通过 |
|---|---|---|
| 多算法 experiment | 创建含 spagcn-lite + mock-domain 的 experiment | 是 |
| Worker 执行多算法 | 两个 runs 都 succeeded | 是 |
| 算法对比报告 | report 包含两个算法的 metrics 对比 | 是 |
| 前端算法对比表 | Experiments 页展示对比表 | 是 |
| 状态自动刷新 | 前端自动 poll run 状态 | 是 |
| Dashboard 概览 | 展示 experiments 和 runs 统计 | 是 |
| 多数据集注册 | STARmap + osmFISH 都可注册 | 是 |
| 测试通过 | test_multi_algo.py 全部通过 | 是 |

## 回滚和兼容性

- 保留 Sprint 1-4 所有功能。
- 单算法 experiment 仍可用。
