# Session: Web benchmark experience implementation plan

日期：2026-05-27 22:25:22 CST

关联目标：

- 用户准备让 Claude Code 实现前端体验优化。
- 本轮只形成计划，不实现前端。
- 计划需要落到本地文档，供 Claude Code 调用。

## 背景

用户反馈当前前端风格太像临时后台，目标需要对标 SDMBench：

- 更专业的科研 benchmark 门户风格。
- 中英文切换。
- 能查看任务执行进度过程。
- 能展示报告图、指标图和 artifact 下载。
- 需要稳定设计约束，避免 Claude Code 生成风格不一致或审美较差的页面。

## 本轮操作

| 步骤 | 操作 | 结果 |
|---|---|---|
| 1 | 确认已有 sprint 编号 | 发现 `SPRINT-20260527-007-stagate-spaceflow-lite` 已存在并已验收 |
| 2 | 创建新 sprint 目录 | `SPRINT-20260527-008-web-benchmark-experience` |
| 3 | 新增 sprint contract | 写入目标、视觉系统、页面 IA、artifact API、验收标准 |
| 4 | 新增 implementation plan | 写入 Claude Code 可执行的分轮计划 |
| 5 | 更新 longrun 命令 | 默认下一步改为 Sprint 8 |
| 6 | 更新 `.gitignore` | 忽略 `.codex/` 本地 skill 安装目录，避免提交本地工具文件 |
| 7 | 清理误启动实现残留 | 还原 `web/` 和 runtime 代码改动，仅保留计划文档和 harness 配置 |

## 新增/修改文件

| 文件 | 类型 | 说明 |
|---|---|---|
| `docs/harness/sprints/SPRINT-20260527-008-web-benchmark-experience/sprint_contract.md` | 新增 | Sprint 8 contract |
| `docs/harness/sprints/SPRINT-20260527-008-web-benchmark-experience/implementation_plan.md` | 新增 | Claude Code 执行计划 |
| `.claude/commands/start-st-platform-longrun.md` | 修改 | 默认推荐 sprint 改为 Sprint 8 |
| `.gitignore` | 修改 | 忽略 `.codex/` |
| `docs/harness/sessions/2026-05-27-web-benchmark-experience-plan.md` | 新增 | 本轮记录 |

## Claude Code 使用方式

```bash
cd /home/wx/project/aaa/spatial-transcriptomic/经典算法/st-platform
claude
```

进入 Claude Code 后：

```text
/start-st-platform-longrun
```

如果 Claude Code 环境没有 UI/UX Pro Max skill：

```bash
npx uipro-cli init --ai claude
```

重启 Claude Code 后读取：

```text
docs/harness/sprints/SPRINT-20260527-008-web-benchmark-experience/sprint_contract.md
docs/harness/sprints/SPRINT-20260527-008-web-benchmark-experience/implementation_plan.md
```

## 本轮不做

- 不实现前端代码。
- 不新增后端 artifact API。
- 不运行前端构建或 pytest。
- 不提交 `.codex/` 本地安装目录。

## 后续建议

Claude Code 执行时优先按 implementation plan 分轮：

1. Design system + i18n + App Shell。
2. Dashboard / Algorithms / Datasets redesign。
3. Backend artifact file API。
4. Reports redesign。
5. Runs / Run Detail progress experience。
6. Full validation and audit。
