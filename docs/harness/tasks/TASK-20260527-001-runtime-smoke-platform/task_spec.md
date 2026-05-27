# Task: Runtime Smoke Benchmark Platform

任务 ID：TASK-20260527-001-runtime-smoke-platform  
状态：ready  
负责人角色：Planner -> Generator -> Evaluator  
创建日期：2026-05-27

## 背景

当前项目已有算法注册、CLI runner、多个空间域算法 adapter 和 STARmap 历史演示产物，但还没有完整 Web benchmark 平台。用户准备使用 Claude Code 长时间运行任务，当前优先级是保证程序能正确运行；Docker 化在主功能完成后再处理。

## 目标

实现第一条可运行纵切链路：

```text
React/Vite Web
  -> FastAPI API
  -> SQLite metadata
  -> SQLite queued runs
  -> worker
  -> OSS-backed artifacts or local OSS-compatible dev backend
  -> Web report / visualization view
```

STARmap 作为 smoke demo 数据。首期至少跑通一个轻量算法，例如 `spagcn-lite`。

## 非目标

- 不做 Docker Compose 打包。
- 不做 Postgres 迁移。
- 不引入 Redis / Celery / RQ。
- 不做登录、用户、RBAC 或 API auth。
- 不要求首期跑通所有真实算法和所有数据集。
- 不把真实大数据、报告图、CSV/JSON 产物或 SQLite 数据库提交到 Git。

## 输入

- `docs/benchmark_platform_design_plan.md`
- `docs/harness/agent_coding_governance.md`
- `docs/harness/project_structure_map.md`
- `CLAUDE.md`
- `.claude/agents/*.md`
- 现有 `src/st_platform/` 平台底座和算法 adapter。

## 输出

- 可启动的 FastAPI app。
- 可启动的 React/Vite app。
- SQLite schema 和初始化逻辑。
- Dataset / algorithm / experiment / run / artifact 基础 API。
- SQLite queued worker。
- STARmap smoke benchmark 运行路径。
- 指标表和空间域可视化展示入口。
- Generator handoff、Evaluator report、artifact/data manifest 和 Git commit。

## 影响范围

允许修改：

- `src/st_platform/api/`
- `src/st_platform/benchmark/`
- `src/st_platform/io/`
- `src/st_platform/storage/`
- `src/st_platform/worker/`
- `web/`
- `tests/`
- `scripts/`
- `docs/harness/tasks/`
- `docs/harness/sprints/`
- `docs/harness/artifacts/`
- `docs/harness/data/`

避免修改：

- 已有算法 adapter 的核心算法逻辑，除非为统一 artifact/metric 格式做小范围兼容。
- 历史运行产物和大文件。

## 验收标准

- `python -m pytest` 通过，或明确记录无法通过的原因和最小失败集。
- API health check 可访问。
- Web 页面可打开。
- SQLite metadata store 可初始化和读写。
- Worker 可从 SQLite queued runs 领取任务。
- 至少一个 STARmap smoke run 可完成。
- 至少生成 `core_spatial_v1` 指标中的 runtime、spatial neighbor agreement、artifact completeness；有标签时生成 ARI/NMI。
- Web 能查看 run 状态、指标表、空间域图和报告下载入口。
- Evaluator report 明确结论为 `passed`、`failed` 或 `blocked`。

## 依赖

- OSS bucket / credential 可用，或提供本地 OSS-compatible dev backend / fake backend 用于测试。
- STARmap smoke 数据路径或可下载/可登记 URI。
- Python / Node 环境可用。

## 风险

- 当前 `scripts/` 下没有可复现实验脚本，历史演示产物不可直接重跑。
- 重型真实算法依赖可能导致环境安装失败；首期应使用 `spagcn-lite` 跑通链路。
- OSS 凭证如果不可用，需要先实现抽象接口和本地 dev backend。

## 审计要求

- 每轮 sprint 必须更新 `docs/harness/sprints/`。
- 每轮实现必须写 generator handoff。
- 每轮评估必须写 evaluator report。
- 每轮结束必须 Git commit。
- 中间产物只写 manifest，不进 Git。

