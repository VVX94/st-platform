# Acceptance Status: SPRINT-20260527-002-dataset-experiment-worker

评估日期：2026-05-27
评估结论：passed

## 验收状态

| # | 验收点 | 状态 | 说明 |
|---|---|---|---|
| 1 | Demo 数据集注册 | PASS | POST /api/datasets/register-demo 返回 201 |
| 2 | Experiment 创建 | PASS | POST /api/experiments 创建包含 spagcn-lite 的 experiment |
| 3 | Run 创建 | PASS | 创建 experiment 后自动产生 queued run |
| 4 | Worker 执行 | PASS | POST /api/worker/poll 后 run 状态变为 succeeded |
| 5 | Metrics 写入 | PASS | GET /api/runs/{id}/metrics 返回 spatial_neighbor_agreement 等 |
| 6 | Artifacts 写入 | PASS | GET /api/runs/{id}/artifacts 返回 domain_assignments |
| 7 | 前端展示 | PASS | Experiments 页面展示 experiment 和 run 状态 |
| 8 | 端到端测试 | PASS | test_e2e.py 全部通过（44 passed, 6 skipped） |
| 9 | CLI 不破坏 | PASS | list-algorithms 正常输出 10 个算法 |

## 验证命令

```bash
# 运行全部测试
PYTHONPATH=src python3 -m pytest tests/ -x -v

# 运行 CLI
PYTHONPATH=src python3 -m st_platform list-algorithms
```

## 测试结果摘要

- 总测试数: 50
- 通过: 44
- 跳过: 6 (需外部依赖的真实算法测试: ccst, const, deepst, graphst, sedr, spagcn)
- 失败: 0

## 备注

- 当前 sprint 目录缺少 generator_handoff.md（低严重级别，不影响验收）。
- 无 login/RBAC 代码引入，符合 sprint contract 约定。
- Worker 支持 dataset-aware 逻辑，兼容 demo 和真实数据集（真实数据集加载暂未实现，返回明确错误）。
