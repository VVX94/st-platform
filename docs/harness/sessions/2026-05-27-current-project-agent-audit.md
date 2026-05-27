# Session: current project and agent audit

日期：2026-05-27  
参与角色：Evaluator  
关联任务：当前项目功能缺口和 agent 运行方式审计

## 用户请求

用户询问如何启动 Claude 相关动作，并要求查看当前项目还有哪些功能没有完善或需要增加，以及 agent 的运行方式是否正确。

## 本轮上下文

- 项目已有 `.claude/agents/planner.md`、`.claude/agents/generator.md`、`.claude/agents/evaluator.md`。
- 项目已有 `.claude/commands/start-st-platform-longrun.md`。
- 当前目标是先保证程序可运行，Docker 打包后置。
- 首期默认技术路径为 FastAPI、React/Vite、SQLite、SQLite queued runs、OSS artifact 设计。

## 执行动作

| 步骤 | 动作 | 文件/命令 | 结果 |
|---|---|---|---|
| 1 | 查看项目结构 | `find . -maxdepth 3 -type f` | 确认已有 API、worker、storage、benchmark、React Web、Claude agents |
| 2 | 查看 Claude 入口 | `CLAUDE.md`、`.claude/commands/start-st-platform-longrun.md`、`.claude/agents/*.md` | 确认启动方式和三 agent 配置存在 |
| 3 | 查看 sprint 状态 | `docs/harness/sprints/*/acceptance_status.md` | 发现多数 sprint accepted，但 SPRINT-003 记录仍显示 NOT accepted |
| 4 | 运行分组测试 | `PYTHONPATH=src python3 -m pytest tests/test_storage.py tests/test_worker.py tests/test_reports.py -q` | 27 passed |
| 5 | 前端构建 | `npm run build` | 通过，Vite build 成功 |
| 6 | CLI smoke | `PYTHONPATH=src python3 -m st_platform run-demo --task domain_detection --algorithm spagcn-lite` | succeeded |
| 7 | API 测试定位 | `pytest tests/test_api.py::TestHealth::test_health_returns_200` | 30s timeout，TestClient/lifespan 有阻塞风险 |
| 8 | 检查中间文件忽略 | `git check-ignore`、`git status --short` | 发现 `st_platform.db-shm` 和 `st_platform.db-wal` 未被忽略 |

## 修改文件

| 文件 | 修改类型 | 说明 |
|---|---|---|
| `.gitignore` | 修改 | 增加 SQLite WAL/SHM/journal 中间文件忽略规则 |
| `docs/harness/sessions/2026-05-27-current-project-agent-audit.md` | 新增 | 本轮审计记录 |

## 验证记录

| 命令/检查 | 结果 | 备注 |
|---|---|---|
| `PYTHONPATH=src python3 -m pytest tests/test_storage.py tests/test_worker.py tests/test_reports.py -q` | 通过 | 27 passed |
| `npm run build` | 通过 | TypeScript + Vite build succeeded |
| `PYTHONPATH=src python3 -m st_platform run-demo --task domain_detection --algorithm spagcn-lite` | 通过 | CLI demo succeeded |
| `pytest tests/test_api.py::TestHealth::test_health_returns_200` | 超时 | TestClient 在 startup/request 阶段挂起，需要修复 |
| `git commit -- .gitignore docs/harness/sessions/2026-05-27-current-project-agent-audit.md` | 待执行 | 创建本轮审计提交 |

## 当前结论

- Claude agent 结构总体正确，入口文件齐全。
- 当前项目已有可运行底座，但 API TestClient、OSS 实装、Playwright E2E、artifact 下载路由、文档状态一致性仍需补齐。
- `.claude/commands/start-st-platform-longrun.md` 仍指向第一个 sprint，后续应更新为“读取当前 task status 并由 planner 选择下一个 sprint”。

## 风险和阻塞

- API 测试超时会影响 evaluator 对后端 API 的可靠验收。
- OSS 目前更多停留在文档和 URI 设计层，源码未看到完整 OSS client / upload sign 实现。
- 前端没有 Playwright 配置，与 harness 的前端验收策略不一致。

## 下一步

建议先创建一个修复 sprint：修复 API TestClient 超时、补 Playwright 测试设施、补 artifact file/download 路由、实现 OSS storage adapter 的最小 dev backend。

