# Session: Claude longrun command update

日期：2026-05-27 20:56:04 CST

关联目标：

- 用户要求修改 Claude Code 启动命令，让后续继续工作时不要回到已完成的旧 sprint。

## 背景

此前 `.claude/commands/start-st-platform-longrun.md` 固定读取：

- `docs/harness/sprints/SPRINT-20260527-001-runtime-foundation/sprint_contract.md`

但 `TASK-20260527-001-runtime-smoke-platform` 已经标记为 `done`，并且最新审查文档已经给出新的高优先级缺口：

- `docs/harness/reviews/2026-05-27-current-project-code-review.md`

固定指向 Sprint 1 会让 Claude Code 继续旧任务，不利于后续 Planner / Generator / Evaluator 流程。

## 本轮修改

| 文件 | 修改 |
|---|---|
| `.claude/commands/start-st-platform-longrun.md` | 改为动态启动流程，先读取 harness 总入口、设计文档、治理文档、结构图、最新 decisions/sessions/reviews/tasks 状态 |
| `.claude/commands/start-st-platform-longrun.md` | 明确 completed sprint 是历史证据，不是当前工作项 |
| `.claude/commands/start-st-platform-longrun.md` | 明确 Planner -> Generator -> Evaluator 顺序 |
| `.claude/commands/start-st-platform-longrun.md` | 默认下一 sprint 指向 `SPRINT-20260527-007-artifact-access-report-preview` |
| `.claude/commands/start-st-platform-longrun.md` | 明确每轮结束需要 session、handoff、evaluator/acceptance、测试记录和 Git commit |

## 当前默认下一步

如果没有新的用户指令，Claude Code 运行 `/start-st-platform-longrun` 后应优先处理：

`SPRINT-20260527-007-artifact-access-report-preview`

目标：

- 修复 Reports 页面 artifact 访问链路。
- 增加后端 artifact preview/download API。
- 避免前端直接暴露服务器绝对路径。
- 让 Web report 可以展示 plot 并下载 CSV。
- 增加 API 测试；如果环境允许，增加 Playwright 或等价前端 smoke。

## 验证

待本轮提交前执行：

```bash
rg "SPRINT-20260527-001-runtime-foundation|SPRINT-20260527-007-artifact-access-report-preview|Planner|Generator|Evaluator|reviews" .claude/commands/start-st-platform-longrun.md
git diff -- .claude/commands/start-st-platform-longrun.md docs/harness/sessions/2026-05-27-claude-longrun-command-update.md
```

## 运行时代码

无运行时代码变更。
