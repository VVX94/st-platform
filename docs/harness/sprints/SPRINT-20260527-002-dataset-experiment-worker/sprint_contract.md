# Sprint Contract: Dataset + Experiment + Worker End-to-End

Sprint ID：SPRINT-20260527-002-dataset-experiment-worker
关联任务：TASK-20260527-001-runtime-smoke-platform
状态：accepted

## 本轮目标

打通第一条完整 benchmark 链路：

1. 注册 STARmap demo 数据集（使用平台内置 demo 数据）。
2. 创建 experiment，选择 spagcn-lite 算法。
3. Worker 领取 queued run，执行算法，写入 metrics 和 artifacts。
4. API 可查询 run 详情、metrics、artifacts。
5. 前端 Experiments 页面可展示 experiment 和 run 状态。
6. 前端 Runs 页面可查看 run 详情和 metrics。

## 明确不做

- 不做真实 h5ad 文件读取（用内置 demo 数据 bundle）。
- 不做 OSS 上传/下载。
- 不做 Docker。
- 不做 ARI/NMI（demo 数据无 ground truth 标签）。
- 不做报告生成（Sprint 3）。

## 预期改动文件

- `src/st_platform/api/routes/datasets.py` - 增加 demo 数据集自动注册
- `src/st_platform/api/routes/experiments.py` - 创建 experiment 时自动关联 dataset
- `src/st_platform/api/routes/runs.py` - 增加 run metrics 和 artifacts 查询
- `src/st_platform/api/routes/worker.py` - 新增 POST /api/worker/poll 触发 worker
- `src/st_platform/api/schemas.py` - 补充 schemas
- `src/st_platform/worker/runner.py` - 改进为从 dataset 构建 data bundle
- `src/st_platform/benchmark/experiment.py` - 改进 split 逻辑
- `src/st_platform/api/deps.py` - 注入 PlatformService
- `web/src/pages/Experiments.tsx` - 展示 experiment 详情和 runs
- `web/src/pages/Runs.tsx` - 新增 run 详情页
- `tests/test_e2e.py` - 端到端测试：注册数据集 -> 创建 experiment -> worker 执行 -> 查询结果

## 用户可见行为

- 用户可通过 API 注册 demo 数据集。
- 用户可创建 experiment 选择算法。
- 用户可触发 worker poll 执行 queued runs。
- 用户可查询 run 的 metrics 和 artifacts。
- 前端可展示 experiment 列表、run 状态、metrics。

## API / 数据库 / 前端变更

API 新增/修改：

- `POST /api/datasets/register-demo` - 注册内置 STARmap demo 数据集
- `POST /api/worker/poll` - 手动触发 worker 执行一轮 polling
- `GET /api/runs/{run_id}/metrics` - 查询 run 的 metrics
- `GET /api/runs/{run_id}/artifacts` - 查询 run 的 artifacts
- `GET /api/experiments/{experiment_id}/runs` - 查询 experiment 下的 runs

前端新增/修改：

- Experiments 页面：点击 experiment 查看详情和关联 runs
- 新增 Runs 页面：查看 run 状态、metrics、artifacts

## 验收测试

| 验收点 | 验证方式 | 必须通过 |
|---|---|---|
| Demo 数据集注册 | POST /api/datasets/register-demo 返回 201 | 是 |
| Experiment 创建 | POST /api/experiments 创建包含 spagcn-lite 的 experiment | 是 |
| Run 创建 | 创建 experiment 后自动产生 queued run | 是 |
| Worker 执行 | POST /api/worker/poll 后 run 状态变为 succeeded | 是 |
| Metrics 写入 | GET /api/runs/{id}/metrics 返回 spatial_neighbor_agreement 等 | 是 |
| Artifacts 写入 | GET /api/runs/{id}/artifacts 返回 domain_assignments | 是 |
| 前端展示 | Experiments 页面可展示 experiment 和 run 状态 | 是 |
| 端到端测试 | test_e2e.py 全部通过 | 是 |
| CLI 不破坏 | list-algorithms 仍正常 | 是 |

## 回滚和兼容性

- 保留 Sprint 1 所有功能。
- 新增的 register-demo 端点不影响现有 register 端点。
- Worker 改进后仍兼容无 dataset 的 run。

## Evaluator 审核意见

评估日期：2026-05-27
结论：passed

全部 9 项验收标准通过。44 个测试通过，6 个跳过（需外部依赖的真实算法测试）。核心 benchmark 链路已完整打通。详见 evaluator_report.md 和 acceptance_status.md。
