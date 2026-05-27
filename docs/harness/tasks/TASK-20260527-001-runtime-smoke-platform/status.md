# Status: Runtime Smoke Benchmark Platform

任务 ID：TASK-20260527-001-runtime-smoke-platform  
当前状态：done
最近更新：2026-05-27

## 当前结论

TASK-20260527-001-runtime-smoke-platform 全部验收标准已满足。核心 benchmark 平台已完成。

## 已完成 sprint

- SPRINT-20260527-001-runtime-foundation: accepted
- SPRINT-20260527-002-dataset-experiment-worker: accepted
- SPRINT-20260527-003-metrics-reports: accepted
- SPRINT-20260527-004-h5ad-reader-real-data: accepted
- SPRINT-20260527-005-multi-algo-frontend: accepted

## 验收状态

| 验收点 | 状态 |
|---|---|
| python -m pytest 通过 | 100 passed, 6 skipped |
| API health check | /api/health 返回 200 |
| Web 页面可打开 | React/Vite 启动，6 个页面 |
| SQLite 可初始化 | 自动建 5 张表 |
| Worker 可执行 run | spagcn-lite + mock-domain |
| STARmap smoke run 完成 | 真实 1207 spots 数据 |
| core_spatial_v1 指标 | ARI, NMI, runtime, spatial_neighbor_agreement, artifact_completeness |
| Web 查看 run 状态/指标/报告 | 前端全部页面可用 |

## 后续可选

- STAGATE / SpaceFlow 算法接入（需 torch, torch_geometric）
- Docker Compose 打包
- OSS 存储对接
- 完整论文级指标

