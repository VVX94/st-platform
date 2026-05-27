# Session: Code review and open gap inventory

日期：2026-05-27 20:49:51 CST

关联目标：

- 梳理当前项目尚未完善或需要增加的功能。
- 继续代码审查。
- 将发现落到文档，方便后续修正和项目管理。

## 本轮操作

| 步骤 | 操作 | 结果 |
|---|---|---|
| 1 | 读取 `coderabbit:code-review` 和 `read-repo` 技能说明 | 明确外部 CodeRabbit 审查和本地证据式 repo 审查边界 |
| 2 | 执行 `coderabbit --version` | 失败：`coderabbit` CLI 未安装，本轮未运行外部 CodeRabbit 审查 |
| 3 | 执行 repo inventory | 确认 `st-platform` 为 git root，包含 Python API/worker/storage/benchmark、React Web、harness 文档 |
| 4 | 阅读 API/storage/worker/benchmark/io/algorithms/web/tests/.claude 关键文件 | 发现 OSS、artifact route、worker 可靠性、Playwright、agent 命令等缺口 |
| 5 | 执行 targeted pytest 和 Web build | 均通过 |
| 6 | 执行 full pytest | `137 passed, 6 skipped, 168 warnings` |
| 7 | 新增 code review 文档 | `docs/harness/reviews/2026-05-27-current-project-code-review.md` |

## 验证命令

```bash
coderabbit --version
python3 /home/wx/.codex/skills/read-repo/scripts/repo_inventory.py /home/wx/project/aaa/spatial-transcriptomic/经典算法/st-platform --max-depth 3
env PYTHONPATH=src timeout 30s python3 -m pytest tests/test_api.py::TestHealth::test_health_returns_200 -q
env PYTHONPATH=src python3 -m pytest tests/test_storage.py tests/test_worker.py tests/test_reports.py -q
npm run build
env PYTHONPATH=src timeout 180s python3 -m pytest -q
env PYTHONPATH=src python3 -m pytest -q -rs
```

## 验证结果

| 命令 | 结果 |
|---|---|
| `coderabbit --version` | 失败，CLI 未安装 |
| API health targeted test | `1 passed in 0.84s` |
| storage/worker/reports tests | `27 passed in 1.56s` |
| Web build | 通过 |
| full pytest | `137 passed, 6 skipped, 168 warnings in 4.70s` |
| full pytest with skip reasons | 6 skipped 均为经典算法外部依赖未安装 |

## 关键发现摘要

本轮详细发现已经写入：

- `docs/harness/reviews/2026-05-27-current-project-code-review.md`

最高优先级缺口：

1. OSS data/artifact backend 未实现。
2. Reports 前端引用 `/artifacts/file`，后端无对应 route。
3. 真实数据登记仍使用服务器本地路径。
4. h5ad reader 把矩阵整体转 list，资源风险较高。
5. worker queue 缺少原子 claim、attempt、worker_id、heartbeat、stale recovery。
6. experiment 状态不会随 run 完成自动收敛。
7. 算法 availability 未暴露，不可运行依赖仍会展示给用户选择。
8. 缺少 Playwright/browser E2E。
9. Claude longrun 命令仍固定指向已完成 Sprint 1。
10. Sprint 3 acceptance 与 task-level status 存在历史状态冲突。

## 本轮代码变更

无运行时代码变更。

新增文档：

- `docs/harness/reviews/2026-05-27-current-project-code-review.md`
- `docs/harness/sessions/2026-05-27-code-review-open-gaps.md`

## 后续建议

建议下一轮先开 Sprint 7：

- 修复 artifact preview/download API。
- 修复 Reports 页面图片和 CSV 下载。
- 增加最小 Playwright smoke，覆盖 Web 报告可视化。

原因：这是当前“本地有结果”到“Web 上可直观看到结果”的最短闭环，也能直接支撑后续 PPT 和真实演示。
