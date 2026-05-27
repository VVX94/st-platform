# Evaluator Report: Dataset + Experiment + Worker End-to-End

关联 sprint：SPRINT-20260527-002-dataset-experiment-worker
评估日期：2026-05-27
结论：passed

## 验证环境

- Python: 3.10.12
- pytest: 9.0.3
- OS: Linux 6.8.0-106-generic
- 工作目录: /home/wx/project/aaa/spatial-transcriptomic/经典算法/st-platform

## Contract 覆盖检查

| 验收点 | 结果 | 证据 |
|---|---|---|
| Demo 数据集注册 | PASS | POST /api/datasets/register-demo 返回 201，返回 STARmap BY3 1k (Demo) 数据集，metadata.demo=True。路由定义于 src/st_platform/api/routes/datasets.py:57-69。test_e2e.py:54-60 验证通过。 |
| Experiment 创建 | PASS | POST /api/experiments 创建包含 spagcn-lite 的 experiment，返回 201，run_count=1，status=running。路由定义于 src/st_platform/api/routes/experiments.py:33-82。test_e2e.py:63-75 验证通过。 |
| Run 创建 | PASS | 创建 experiment 后自动产生 queued run，status=queued，algorithm_id=spagcn-lite，dataset 信息已传递。experiments.py:69-77 创建 runs。test_e2e.py:78-89 验证通过。 |
| Worker 执行 | PASS | POST /api/worker/poll 返回 processed=1，run 状态变为 succeeded，started_at 和 finished_at 非空。路由定义于 src/st_platform/api/routes/worker.py:15-25。worker/runner.py 实现 poll_runs 逻辑。test_e2e.py:92-103 验证通过。 |
| Metrics 写入 | PASS | GET /api/runs/{id}/metrics 返回 metrics 列表，包含 metric_id、name、value 字段。spagcn_lite.py:120-126 产出 spatial_neighbor_agreement、spot_count、gene_count、refinement_changes。test_e2e.py:106-116 验证通过。 |
| Artifacts 写入 | PASS | GET /api/runs/{id}/artifacts 返回 artifacts 列表，包含 artifact_id、kind=domain_assignments、uri。spagcn_lite.py:112-118 产出 domain_assignments artifact。test_e2e.py:119-128 验证通过。 |
| 前端展示 | PASS | Experiments.tsx 展示 experiment 列表、状态徽章、run 列表、Worker 触发按钮。RunDetail.tsx 展示 run 详情、metrics 表格、artifacts 表格。client.ts 包含 getExperimentRuns、getRunMetrics、getRunArtifacts、triggerWorkerPoll 方法。 |
| 端到端测试 | PASS | test_e2e.py 全部 5 个测试通过（test_full_benchmark_flow、test_experiment_runs_endpoint、test_experiment_runs_not_found、test_run_metrics_not_found、test_run_artifacts_not_found）。全部 44 个测试通过，6 个跳过（需外部依赖的真实算法测试）。 |
| CLI 不破坏 | PASS | `PYTHONPATH=src python3 -m st_platform list-algorithms` 正常输出 10 个算法。 |

## UI 检查

Experiments.tsx:
- 展示 experiment 列表表格，包含 ID、Name、Task Type、Status、Runs、Actions 列。
- 状态徽章颜色区分：queued(灰)、running(蓝)、succeeded(绿)、failed(红)。
- "View Runs" 按钮点击后加载并展示该 experiment 下的 runs 列表。
- "Run Worker" 按钮触发 POST /api/worker/poll，处理完成后刷新列表。
- Runs 列表包含 Run ID、Algorithm、Status、Started、Finished、Details 列。
- "View Detail" 链接跳转到 /runs/{runId}。

RunDetail.tsx:
- 展示 Run ID、Algorithm、Task Type、Status、Started At、Finished At 详情。
- 错误信息以红色背景展示。
- Metrics 表格展示 Metric 名称和 Value（保留 4 位小数）。
- Artifacts 表格展示 Kind、URI、Description。
- 包含返回 Experiments 页面的导航链接。

## API 检查

| 端点 | 方法 | 状态码 | 说明 |
|---|---|---|---|
| /api/datasets/register-demo | POST | 201 | 注册内置 STARmap demo 数据集 |
| /api/datasets/register | POST | 201 | 通用数据集注册（Sprint 1 保留） |
| /api/datasets | GET | 200 | 列出所有数据集 |
| /api/datasets/{id} | GET | 200/404 | 获取单个数据集 |
| /api/experiments | POST | 201 | 创建 experiment，自动创建 queued runs |
| /api/experiments | GET | 200 | 列出所有 experiments |
| /api/experiments/{id} | GET | 200/404 | 获取单个 experiment |
| /api/experiments/{id}/runs | GET | 200/404 | 获取 experiment 下的 runs |
| /api/runs | GET | 200 | 列出所有 runs |
| /api/runs/{id} | GET | 200/404 | 获取单个 run 详情 |
| /api/runs/{id}/metrics | GET | 200/404 | 获取 run 的 metrics |
| /api/runs/{id}/artifacts | GET | 200/404 | 获取 run 的 artifacts |
| /api/worker/poll | POST | 200 | 触发 worker 执行一轮 polling |

所有端点无认证/授权要求，符合 sprint contract "不做 login/RBAC" 的约定。

## Worker / 数据库 / Artifact 检查

Worker 逻辑 (worker/runner.py):
- poll_runs 从数据库查询 queued runs，逐个执行。
- 支持 dataset-aware 逻辑：检查 dataset_json 中的 metadata.demo 标志。
- demo 数据集使用 build_demo_bundle() 构建数据。
- 无 URI 的数据集也回退到 demo bundle。
- 有真实 URI 的数据集暂不支持，返回明确错误信息。
- 执行结果通过 RunRepo.mark_succeeded 写入 metrics 和 artifacts。

数据库模型 (storage/models.py):
- DatasetModel、ExperimentModel、RunModel、MetricModel、ArtifactModel 完整定义。
- RunModel 包含 dataset_json 字段存储数据集信息。
- MetricModel 和 ArtifactModel 通过 ForeignKey 关联 RunModel。

Repository (storage/repositories.py):
- RunRepo.mark_succeeded 同时写入 summary、metrics 和 artifacts。
- MetricRepo.list_for_run 和 ArtifactRepo.list_for_run 支持按 run_id 查询。

算法输出 (algorithms/spagcn_lite.py):
- 产出 metrics: spot_count、gene_count、spatial_neighbor_agreement、refinement_changes。
- 产出 artifacts: kind=domain_assignments，uri 指向 run_root 下的 JSON 文件。
- 使用 KMeans 聚类 + 邻域 refinement，非 stub 实现。

## 发现的问题

| 严重级别 | 问题 | 证据 | 建议 |
|---|---|---|---|
| Low | 当前 sprint 目录缺少 generator_handoff.md | docs/harness/sprints/SPRINT-20260527-002-dataset-experiment-worker/ 仅有 sprint_contract.md | Generator 应在实现完成后补充 generator_handoff.md，记录文件变更和自测命令。不影响功能验收。 |

## 最终结论

SPRINT-20260527-002-dataset-experiment-worker 全部 9 项验收标准通过。

核心 benchmark 链路已打通：注册 demo 数据集 -> 创建 experiment -> worker 执行 -> 写入 metrics/artifacts -> API 查询 -> 前端展示。端到端测试覆盖完整流程，44 个测试全部通过（6 个跳过为需外部依赖的真实算法测试，非本次 sprint 范围）。CLI 功能保留完好。无 login/RBAC 代码引入。

结论：passed。
