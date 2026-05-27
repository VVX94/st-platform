# Sprint Contract: Metrics Enhancement + Report Generation

Sprint ID：SPRINT-20260527-003-metrics-reports
关联任务：TASK-20260527-001-runtime-smoke-platform
状态：accepted

## 本轮目标

增强指标计算和报告生成能力：

1. Worker 执行完成后生成 CSV 报告（run_metrics.csv, domain_predictions.csv）。
2. Worker 执行完成后生成 Markdown 报告（report.md）。
3. Worker 执行完成后生成空间域可视化图（domain_grid.png）。
4. Worker 执行完成后生成指标对比图（metrics_bar.png）。
5. 报告产物作为 artifact 写入 SQLite 并可通过 API 下载。
6. 新增 GET /api/experiments/{id}/report 端点返回报告摘要。
7. 前端 Reports 页面展示指标表、空间域图、下载链接。

## 明确不做

- 不做 ARI/NMI（demo 数据无 ground truth）。
- 不做 OSS 上传（报告存本地 runs/ 目录）。
- 不做 Docker。
- 不做真实 h5ad 数据读取。

## 预期改动文件

- `src/st_platform/benchmark/metrics.py` - 新增：spatial neighbor agreement, artifact completeness, runtime 计算
- `src/st_platform/benchmark/reports.py` - 新增：CSV, PNG, Markdown 报告生成
- `src/st_platform/worker/runner.py` - 调用报告生成
- `src/st_platform/api/routes/experiments.py` - 新增 report 端点
- `src/st_platform/api/schemas.py` - ReportOut schema
- `web/src/pages/Reports.tsx` - 新增报告页面
- `web/src/App.tsx` - 新增报告路由
- `web/src/api/client.ts` - 报告 API 函数
- `tests/test_metrics.py` - 指标计算测试
- `tests/test_reports.py` - 报告生成测试

## 验收测试

| 验收点 | 验证方式 | 必须通过 |
|---|---|---|
| 指标计算 | spatial_neighbor_agreement, runtime, artifact_completeness 正确 | 是 |
| CSV 报告 | run_metrics.csv 和 domain_predictions.csv 生成 | 是 |
| PNG 报告 | domain_grid.png 和 metrics_bar.png 生成 | 是 |
| Markdown 报告 | report.md 生成且内容完整 | 是 |
| Artifact 索引 | 报告文件作为 artifact 记录到 SQLite | 是 |
| Report API | GET /api/experiments/{id}/report 返回摘要 | 是 |
| 前端报告页 | 展示指标表和下载链接 | 是 |
| 测试通过 | test_metrics.py + test_reports.py 全部通过 | 是 |

## 回滚和兼容性

- 保留 Sprint 1-2 所有功能。
- 报告生成失败不应导致 run 标记为 failed（warnings 而非 exceptions）。
