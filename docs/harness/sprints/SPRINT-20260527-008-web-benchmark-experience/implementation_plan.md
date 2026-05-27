# Web Benchmark Experience Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or the local project harness (`Planner -> Generator -> Evaluator`) to implement this plan round-by-round. Steps use checklist syntax for tracking. Each round must end with validation, sprint docs, and a git commit.

**Goal:** 将当前 `web/` 升级为可部署的、对标 SDMBench 的空间转录组 benchmark 门户，并补齐报告图、artifact 下载和任务进度展示闭环。

**Architecture:** 本 sprint 采用小步垂直切片：先统一 Web 设计系统和 i18n，再重做核心页面，随后补齐后端 artifact 文件访问 API，最后用 Reports 和 Run Detail 验证完整用户路径。后端保持 SQLite + 本地 artifact 文件模式，不引入 OSS 签名 URL、鉴权或 Docker 变更。

**Tech Stack:** FastAPI, SQLite, React, Vite, TypeScript, CSS, Claude Code harness, UI/UX Pro Max skill.

---

状态：ready for Claude Code  
使用对象：Claude Code Planner / Generator / Evaluator  
前置文档：`sprint_contract.md`

## 0. 启动方式

在项目根目录启动 Claude Code：

```bash
cd /home/wx/project/aaa/spatial-transcriptomic/经典算法/st-platform
claude
```

进入 Claude Code 后运行：

```text
/start-st-platform-longrun
```

如果 Claude Code 没有识别 UI/UX Pro Max skill，先在项目根目录运行：

```bash
npx uipro-cli init --ai claude
```

然后重启 Claude Code，再读取：

```text
.claude/skills/ui-ux-pro-max/SKILL.md
docs/harness/sprints/SPRINT-20260527-008-web-benchmark-experience/sprint_contract.md
docs/harness/sprints/SPRINT-20260527-008-web-benchmark-experience/implementation_plan.md
```

## 1. Sprint 执行原则

Claude Code 必须按以下 agent 顺序执行：

1. Planner：确认范围，不做代码。
2. Generator：实现一个明确工作点。
3. Evaluator：独立验证，不替 Generator 擦屁股。

每轮结束必须：

- 更新本 sprint 目录下的 `generator_handoff.md`。
- 更新本 sprint 目录下的 `evaluator_report.md` 和 `acceptance_status.md`。
- 新增或更新 `docs/harness/sessions/*.md`。
- 运行相关测试。
- 创建 git commit。

## 2. 推荐分轮执行

### Round 1: Design System + i18n + App Shell

目标：

- 建立统一视觉底座。
- 建立中英文切换。
- 重构全局 layout。

建议文件：

```text
web/src/styles/theme.css
web/src/i18n/messages.ts
web/src/i18n/index.tsx
web/src/components/Layout.tsx
web/src/components/StatusBadge.tsx
web/src/App.tsx
web/src/main.tsx
```

具体任务：

- [ ] 引入 `theme.css`。
- [ ] 定义颜色、字号、间距、panel、table、button、badge、progress、timeline 基础类。
- [ ] 新增 i18n provider。
- [ ] 顶部导航改为统一 app shell。
- [ ] 增加 `中文 / EN` 切换，持久化到 `localStorage`。
- [ ] 增加 skip link 和 active nav state。
- [ ] 运行 `npm run build`。
- [ ] 更新 sprint 文档并提交：`git commit -m "feat(web): add benchmark app shell and i18n"`。

验收：

```bash
npm run build
```

视觉检查：

- 不再是深色临时 nav + 随机 inline 页面。
- 页面背景、panel、表格、按钮样式一致。
- 中英文切换至少覆盖导航、页面标题、主要按钮。

### Round 2: Dashboard / Algorithms / Datasets Redesign

目标：

- 将入口页改成 benchmark portal 首页。
- 数据集和算法页从 CRUD 表格升级为科研平台信息页。

建议文件：

```text
web/src/pages/Dashboard.tsx
web/src/pages/Algorithms.tsx
web/src/pages/Datasets.tsx
web/src/components/DataTable.tsx
web/src/components/MetricCard.tsx
```

具体任务：

- [ ] Dashboard 显示 platform mission、KPI、recent experiments、recent runs。
- [ ] Algorithms 按 task type 分组，显示 runtime/version/tags/availability。
- [ ] Datasets 显示 demo/real/local-dev 状态。
- [ ] 所有表格使用共享 table 样式。
- [ ] loading/error/empty states 统一。
- [ ] 运行 `npm run build`。
- [ ] 更新 sprint 文档并提交：`git commit -m "feat(web): redesign benchmark overview pages"`。

验收：

```bash
npm run build
```

视觉检查：

- 适合 PPT 展示。
- 首页第一屏能说明这是空间转录组 benchmark 平台。
- 数据表不溢出移动端。

### Round 3: Backend Artifact File API

目标：

- 修复 Reports 页面 artifact 链接无法访问的问题。
- 禁止前端通过任意 `path=` 参数读服务器文件。

建议文件：

```text
src/st_platform/api/routes/artifacts.py
src/st_platform/api/routes/__init__.py
tests/test_artifact_api.py
web/src/api/client.ts
```

API：

```text
GET /api/artifacts/{artifact_id}/file
```

具体任务：

- [ ] 根据 `artifact_id` 查询 DB。
- [ ] 只允许返回 DB 已登记 artifact 的 `uri`。
- [ ] 本地文件存在则 `FileResponse`。
- [ ] 文件不存在返回 404。
- [ ] 设置 `.png`, `.csv`, `.json`, `.md` 的 media type。
- [ ] 新增测试覆盖 PNG/CSV/missing artifact/missing file。
- [ ] 运行 artifact/API 相关 pytest。
- [ ] 更新 sprint 文档并提交：`git commit -m "feat(api): serve recorded artifact files"`。

验收：

```bash
PYTHONPATH=src python3 -m pytest tests/test_artifact_api.py -q
PYTHONPATH=src python3 -m pytest tests/test_api.py tests/test_reports.py -q
```

安全检查：

- 不接受 `?path=/...` 这种任意路径读取。
- UI 不再拼接服务器绝对路径。

### Round 4: Reports Page Redesign

目标：

- 报告页成为结果展示核心页面。

建议文件：

```text
web/src/pages/Reports.tsx
web/src/components/ArtifactGallery.tsx
web/src/components/MetricBars.tsx
web/src/components/ComparisonHeatmap.tsx
```

具体任务：

- [ ] 展示 experiment summary。
- [ ] 展示 metrics summary table。
- [ ] 展示 algorithm comparison heatmap-like table。
- [ ] 展示 artifact gallery。
- [ ] 对 `domain_grid_plot` 和 `metrics_bar_plot` 显示图片预览。
- [ ] 对 CSV/JSON/MD artifact 显示下载按钮。
- [ ] 图片/下载 URL 使用 `/api/artifacts/{artifact_id}/file`。
- [ ] 运行 `npm run build`，并 smoke 检查报告图片/CSV 链接。
- [ ] 更新 sprint 文档并提交：`git commit -m "feat(web): redesign benchmark reports"`。

验收：

```bash
npm run build
```

浏览器 smoke：

- 创建或复用一个含报告 artifact 的 run。
- 打开 Reports。
- 图片显示不是空白。
- CSV 下载返回 200。

### Round 5: Runs / Run Detail Progress Experience

目标：

- 让用户能看到任务执行过程，而不是只看最终状态。

建议文件：

```text
web/src/pages/Experiments.tsx
web/src/pages/RunDetail.tsx
web/src/components/ProgressTimeline.tsx
web/src/components/ProgressBar.tsx
```

具体任务：

- [ ] Runs/Experiments 表格显示 status、progress、current stage。
- [ ] Run Detail 显示 progress bar。
- [ ] Run Detail 显示 stage timeline。
- [ ] 首版 progress 从 status/timestamps/metrics/artifacts 派生。
- [ ] failed 状态显示错误面板和 recovery hint。
- [ ] 运行 `npm run build`，并 smoke 检查 queued/succeeded/failed 三类状态。
- [ ] 更新 sprint 文档并提交：`git commit -m "feat(web): show benchmark run progress"`。

验收：

```bash
npm run build
```

浏览器 smoke：

- queued run 显示 queued stage。
- succeeded run 显示完整 timeline。
- failed run 显示 error panel。

### Round 6: Full Validation and Audit

目标：

- 做一次完整验证。
- 写 handoff/evaluator/acceptance。
- commit。

具体任务：

- [ ] 运行后端 API/worker/report/artifact 测试。
- [ ] 运行前端生产构建。
- [ ] 如果环境可用，运行 Playwright 或等价浏览器 smoke。
- [ ] 检查 `git status --short`，确认没有中间文件、DB、artifact、`.codex/` 或 `.claude/skills/` 被提交。
- [ ] 更新 `evaluator_report.md`、`acceptance_status.md`、`generator_handoff.md` 和 session 文档。
- [ ] 最终提交：`git commit -m "test(web): validate benchmark experience sprint"`。

命令：

```bash
PYTHONPATH=src python3 -m pytest tests/test_api.py tests/test_storage.py tests/test_worker.py tests/test_reports.py tests/test_artifact_api.py -q
npm run build
git status --short
```

如果新增 Playwright：

```bash
npm run test:e2e
```

## 3. UI Component Contract

Generator 应优先创建这些组件，而不是继续在页面里复制样式：

| Component | Purpose |
|---|---|
| `Layout` | app shell, top nav, language switch |
| `PageHeader` | eyebrow/title/subtitle/actions |
| `Panel` | chart/table/form surface |
| `MetricCard` | KPI display |
| `StatusBadge` | queued/running/succeeded/failed |
| `DataTable` | consistent scrollable tables |
| `ProgressBar` | percent progress |
| `ProgressTimeline` | stage list |
| `MetricBars` | metric bar chart without heavy dependency |
| `ComparisonHeatmap` | algorithm x metric matrix |
| `ArtifactGallery` | preview/download artifact cards |
| `EmptyState` | consistent empty/error/loading states |

## 4. i18n Contract

Minimum translation coverage:

- Navigation labels.
- Page titles/subtitles.
- Buttons/actions.
- Status labels.
- Table column labels.
- Empty/error/loading states.
- Run progress stage names.
- Artifact action labels.

Suggested message namespaces:

```text
nav.*
dashboard.*
datasets.*
algorithms.*
experiments.*
runs.*
reports.*
status.*
artifact.*
common.*
```

Language switch:

- `zh` default if browser language starts with `zh`.
- `en` otherwise.
- User selection persists in `localStorage`.

## 5. Data and API Assumptions

Do not block this sprint on new backend run event tables.

Allowed derived progress:

```text
queued: 5%
running/loading_dataset: 25%
running/running_algorithm: 50%
metrics exist: 75%
artifacts exist: 90%
succeeded: 100%
failed: 100% with error state
```

Future sprint can add:

```text
run_events(event_id, run_id, stage, message, level, created_at)
runs.progress_percent
runs.current_stage
runs.worker_id
runs.heartbeat_at
```

## 6. Do Not Do

- Do not implement login/RBAC/auth.
- Do not implement full OSS signed URL flow in this sprint.
- Do not add Docker packaging.
- Do not add large charting libraries unless necessary.
- Do not introduce random visual styles per page.
- Do not commit generated run artifacts, local DB files, `web/dist`, `node_modules`, `.codex`, `.claude/skills`, or `runs`.

## 7. Expected Commit Shape

Recommended commits:

1. `feat(web): add benchmark design system and i18n`
2. `feat(api): add controlled artifact file endpoint`
3. `feat(web): redesign reports and run progress views`
4. `docs(harness): accept web benchmark experience sprint`

If Claude Code works in one round, one commit is acceptable, but the handoff must clearly separate the implemented slices.
