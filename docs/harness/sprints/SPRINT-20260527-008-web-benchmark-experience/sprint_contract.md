# Sprint Contract: Web Benchmark Experience

Sprint ID：SPRINT-20260527-008-web-benchmark-experience  
关联任务：ST Platform deployable benchmark Web platform  
状态：pending  
默认执行 agent：Planner -> Generator -> Evaluator

## 本轮目标

将当前 `web/` 从临时后台页面升级为对标 SDMBench 的科研 benchmark 门户体验，并补齐 Web 报告查看所需的最小 artifact 访问闭环。

本轮不是继续堆算法数量，而是先让用户能在 Web 上清楚完成：

```text
查看平台概览 -> 浏览数据集/算法 -> 创建或查看任务 -> 查看任务进度 -> 查看报告图和指标 -> 下载 artifact
```

## 使用 UI/UX Pro Max Skill

Claude Code 开始本 sprint 前必须先确认 UI skill 可用。

推荐在项目根目录运行：

```bash
npx uipro-cli init --ai claude
```

然后重启 Claude Code，并在本 sprint 中读取：

```text
.claude/skills/ui-ux-pro-max/SKILL.md
```

如果 `.claude/skills/ui-ux-pro-max/` 不存在，则使用本 sprint contract 中的设计约束作为强制准则，不得自由发挥视觉风格。

## 设计定位

产品类型：scientific benchmark portal + data-dense analytics dashboard  
对标方向：SDMBench-style benchmark website  
用户：空间转录组算法研究者、平台维护者、需要比较算法结果的用户  
首要体验：可信、清晰、可审计、数据密集但不凌乱

## 强制视觉系统

### Style

- Scientific benchmark portal, not admin CRUD demo.
- Data-dense dashboard with restrained enterprise gateway feel.
- Light mode first.
- No purple gradients.
- No decorative blobs, bokeh, floating orbs, oversized marketing cards.
- No emoji icons; use text, CSS shapes, or installed icon library if available.
- No nested cards.
- Cards are only for repeated items, chart panels, artifact panels, and forms.

### Colors

| Token | Value |
|---|---|
| Background | `#F6F8FB` |
| Surface | `#FFFFFF` |
| Muted surface | `#F8FAFC` |
| Border | `#E4E7EC` |
| Strong border | `#CBD5E1` |
| Text | `#172033` |
| Muted text | `#667085` |
| Primary | `#1E40AF` |
| Secondary | `#3B82F6` |
| Accent | `#F59E0B` |
| Success | `#12A150` |
| Warning | `#F59E0B` |
| Error | `#D92D20` |

### Typography

- Use system font or Fira Sans if introduced.
- H1: `28px / 36px / 700`.
- H2: `22px / 30px / 700`.
- Section title: `18px / 26px / 600`.
- Body: `14px / 22px`.
- Table text: `13px / 20px`.
- Metric numbers may use tabular/monospace figures.
- Letter spacing must be `0` except small uppercase eyebrows.

### Layout

- Top navigation height: `64px`.
- Main content max width: `1200px`.
- Desktop page padding: `24px`.
- Mobile page padding: `16px`.
- Cards/panels radius: `8px`.
- Tables must sit inside horizontal-scroll wrappers on mobile.
- Use responsive grid: desktop 2-4 columns, mobile 1 column.
- Every page must have a consistent page header: eyebrow, title, subtitle, optional actions.

## Required Page Information Architecture

### App Shell

Files likely affected:

- `web/src/App.tsx`
- `web/src/main.tsx`
- `web/src/styles/theme.css`
- `web/src/i18n/*`
- `web/src/components/*`

Requirements:

- Unified top navigation.
- Language switcher: `中文 / EN`.
- Language persisted in `localStorage`.
- Skip link for keyboard users.
- Active navigation state.
- No visible hard-coded text in page components when practical; use translation keys.

### Dashboard

Purpose: platform overview and entry point.

Must show:

- Platform mission: spatial domain benchmark platform.
- KPI cards: datasets, algorithms, experiments, runs.
- Recent runs table.
- Recent experiments table.
- Quick entry actions: datasets, methods, runs, reports.

### Benchmark

If a standalone `Benchmark` route is too large for this sprint, add a benchmark section to Dashboard or Reports.

Must show at least:

- Algorithm comparison summary.
- Metric-oriented view: algorithm x metric table or heatmap-like grid.
- Filters or placeholders for dataset/method/metric filters.

### Datasets

Must improve current page but keep behavior:

- Demo registration actions.
- Real dataset registration remains marked as local/dev-only until OSS upload flow exists.
- Dataset table with platform, sample, n_obs, n_vars, label column, demo/real status.
- Empty, loading, and error states.

### Methods / Algorithms

Must improve current page:

- Group by task type.
- Show runtime, version, tags.
- Show availability status:
  - `ready` for lightweight/demo adapters.
  - `external dependency` for adapters likely requiring missing packages.
  - If backend does not expose availability yet, derive a conservative UI label from algorithm id and tags.

### Experiments / Runs

Must improve current page:

- Runs table should show status, progress percent, current stage, started/finished time.
- Manual `Run Worker` button may remain but must be visually marked as dev/manual control.
- Creating experiment must have clear form labels and validation messages.

### Run Detail

Must show:

- Summary header: run id, algorithm, task type, status, elapsed time.
- Progress bar.
- Stage timeline.
- Metrics table.
- Artifact list.
- Error panel with recovery hint if failed.

Initial progress may be derived from status/timestamps:

| Stage | Condition |
|---|---|
| queued | status `queued` |
| loading_dataset | status `running` and no metrics/artifacts yet |
| running_algorithm | status `running` |
| computing_metrics | metrics exist |
| generating_artifacts | artifacts exist |
| succeeded | status `succeeded` |
| failed | status `failed` |

### Reports

Must show:

- Experiment report summary.
- Metrics summary table.
- Algorithm comparison table or heatmap-like view.
- Artifact gallery.
- Spatial domain plot preview for `domain_grid_plot`.
- Metrics plot preview for `metrics_bar_plot`.
- CSV download links for metrics/domain predictions.
- Empty, loading, error states.

## Backend Minimal Artifact API

Current issue:

- Frontend references `/artifacts/file?path=...`.
- Backend has no matching route.
- UI leaks server absolute paths.

This sprint must add a minimal local artifact route.

Recommended API:

```text
GET /api/artifacts/{artifact_id}/file
```

Behavior:

- Look up artifact by `artifact_id`.
- In local mode, return `FileResponse` if the stored `uri` points to an existing file.
- Return 404 if artifact or file missing.
- Only allow files already recorded in `ArtifactModel`; do not accept arbitrary filesystem path from query params.
- Use appropriate media type for `.png`, `.csv`, `.json`, `.md`.

Frontend:

- Use `artifact_id` URL, not raw server path.
- UI may show a shortened artifact name/kind, not absolute path.

Explicitly out of scope:

- Full OSS signed URL implementation.
- Auth/RBAC/login.
- Docker packaging.

## Suggested File Changes

| Area | Files |
|---|---|
| Styles | `web/src/styles/theme.css` |
| i18n | `web/src/i18n/index.tsx`, `web/src/i18n/messages.ts` |
| Components | `web/src/components/Layout.tsx`, `StatusBadge.tsx`, `DataTable.tsx`, `ProgressTimeline.tsx`, `MetricBars.tsx`, `ArtifactGallery.tsx` |
| Pages | `web/src/App.tsx`, `Dashboard.tsx`, `Datasets.tsx`, `Algorithms.tsx`, `Experiments.tsx`, `RunDetail.tsx`, `Reports.tsx` |
| API client | `web/src/api/client.ts` |
| Backend route | `src/st_platform/api/routes/artifacts.py`, `src/st_platform/api/routes/__init__.py` |
| Tests | `tests/test_artifact_api.py` or extension of `tests/test_api.py` |

## Acceptance Criteria

| # | Acceptance Point | Verification |
|---|---|---|
| 1 | UI has unified benchmark portal visual style | Manual code review: shared CSS/classes, no page-level random inline styling for main layout |
| 2 | Chinese/English switch works | Web build plus manual smoke; language persists in localStorage |
| 3 | Dashboard shows platform KPIs and recent runs/experiments | Browser/manual or component smoke |
| 4 | Run Detail shows progress bar and stage timeline | Browser/manual or test fixture state |
| 5 | Reports shows metrics tables and artifact gallery | Browser/manual/API smoke |
| 6 | Plot artifacts are loaded through controlled backend route | API test for `GET /api/artifacts/{id}/file` |
| 7 | CSV artifacts can be downloaded through controlled backend route | API test |
| 8 | UI does not expose absolute server paths as primary artifact links | Code review |
| 9 | Mobile layout remains usable at 375px width | Browser/manual or Playwright if available |
| 10 | `npm run build` passes | Required |
| 11 | `PYTHONPATH=src python3 -m pytest ...` relevant tests pass | Required |
| 12 | No generated artifacts or local DB files are committed | `git status --short` and `.gitignore` review |

## Recommended Verification Commands

```bash
PYTHONPATH=src python3 -m pytest tests/test_api.py tests/test_storage.py tests/test_worker.py tests/test_reports.py -q
PYTHONPATH=src python3 -m pytest tests/test_artifact_api.py -q
npm run build
git status --short
```

If Playwright is added:

```bash
npm run test:e2e
```

## Generator Guidance

- Implement in small vertical slices.
- Prefer shared components over copy-paste page CSS.
- Keep backend artifact API minimal and local-only for this sprint.
- Preserve existing API behavior unless changing it is needed for artifact display.
- Do not introduce auth/RBAC/login.
- Do not commit `.codex/`, `.claude/skills/`, `runs/`, `web/dist/`, `node_modules/`, local DB files, generated plots, CSV, or JSON artifacts.

## Evaluator Focus

Evaluator must reject the sprint if:

- Reports page still uses arbitrary `path=` query to read files.
- Report image/CSV links are visually present but return 404.
- Chinese/English switch is partial or only changes nav text.
- Main pages still use unrelated one-off visual systems.
- Generated artifacts are committed.
- `npm run build` fails.
