# Decision: 先保证程序运行，Docker 后置打包

日期：2026-05-27  
状态：accepted  
关联文档：`docs/benchmark_platform_design_plan.md`

## 背景

用户准备使用 Claude Code 长时间运行任务，当前目标是保证项目能正确运行。Docker 化可以在项目完成后再打包，不应阻塞首期功能实现。

## 决策

当前阶段优先级：

1. 本地/测试服务器直接运行 FastAPI、React/Vite、worker。
2. SQLite metadata store 可初始化和读写。
3. OSS 数据和 artifact 流程可跑通。
4. STARmap smoke benchmark 可从 Web 创建、由 worker 执行并展示结果。
5. Docker Compose / 镜像打包后置到主功能完成之后。

## 影响

- 文档不再把 Docker Compose 作为首期实现验收。
- Claude Code 长任务应先实现可运行服务和 smoke 链路。
- `deploy/` 目录可以暂不创建；等主功能稳定后再进入 Docker 打包 sprint。

## 验收

首期验收以“程序能运行”为准：

- API health check 可访问。
- Web 页面可打开。
- worker 可轮询 SQLite queued runs。
- OSS artifact 写读可用。
- STARmap smoke run 可完成并展示报告。

