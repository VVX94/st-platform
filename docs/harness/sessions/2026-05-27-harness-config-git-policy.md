# Session: harness config and git policy

日期：2026-05-27  
参与角色：Planner  
关联任务：完善 benchmark 平台目标文档中的三智能体 harness 配置，并加入 Git 提交和中间产物管理规则

## 用户请求

用户确认将 Planner / Generator / Evaluator 三智能体 harness 配置写入 `docs/benchmark_platform_design_plan.md`。同时要求增加限制：每跑完一轮任务都需要 Git 提交，但项目里的中间文件不要存到 Git，需要修改 `.gitignore`。

## 本轮上下文

- `docs/harness/` 已建立作为 agent 编码审计根目录。
- `docs/harness/agent_coding_governance.md` 已作为高优先级治理规范。
- 当前工作树中还有此前生成的文档和演示产物，提交时需要避免把中间产物纳入 Git。

## 执行动作

| 步骤 | 动作 | 文件/命令 | 结果 |
|---|---|---|---|
| 1 | 读取 `.gitignore` | `sed -n '1,220p' .gitignore` | 确认已有 `runs/`、缓存和虚拟环境基础规则 |
| 2 | 读取目标文档 | `sed -n '1,120p' docs/benchmark_platform_design_plan.md` | 确认适合在项目目标后新增 harness 配置 |
| 3 | 读取治理规范 | `sed -n '1,220p' docs/harness/agent_coding_governance.md` | 确认需要增加 Git 和产物管理章节 |
| 4 | 修改 `.gitignore` | `.gitignore` | 增加本地配置、数据库、生成报告、上传数据、前端构建产物忽略规则 |
| 5 | 修改目标文档 | `docs/benchmark_platform_design_plan.md` | 增加 Planner / Generator / Evaluator harness 配置 |
| 6 | 修改治理规范 | `docs/harness/agent_coding_governance.md` | 增加每轮任务 Git 提交和提交白/黑名单规则 |

## 修改文件

| 文件 | 修改类型 | 说明 |
|---|---|---|
| `.gitignore` | 修改 | 排除本地环境、数据库、生成报告、上传数据、前端构建产物 |
| `docs/benchmark_platform_design_plan.md` | 修改 | 新增 `2.1 多智能体 Harness 配置` |
| `docs/harness/agent_coding_governance.md` | 修改 | 新增 Git 和产物管理规则 |
| `docs/harness/sessions/2026-05-27-harness-config-git-policy.md` | 新增 | 本轮会话审计记录 |

## 验证记录

| 命令/检查 | 结果 | 备注 |
|---|---|---|
| `rg "每轮任务|Git 提交|Planner|Generator|Evaluator|中间产物|presentation_results|benchmark_results|node_modules|sqlite" docs/benchmark_platform_design_plan.md docs/harness/agent_coding_governance.md .gitignore` | 通过 | 确认 harness、Git 提交和中间产物忽略规则可检索 |
| `git check-ignore -v presentation_results/starmap_domain_demo/starmap_algorithm_summary.csv presentation_results/starmap_domain_demo/starmap_domain_grid.png runs/05f9bc99a56b/deepst-domains.json .venv-spagcn/pyvenv.cfg` | 通过 | 确认生成 CSV/PNG、runs 输出和 `.venv-spagcn` 被忽略 |
| `git status --short` | 通过 | 确认未跟踪的生成 CSV/JSON/PNG 不再显示；仍有此前 staged 的非本轮文件，提交时需要 pathspec 限制 |
| `git commit -- .gitignore docs/benchmark_platform_design_plan.md docs/harness` | 通过 | 创建本轮审计提交，排除无关 staged 文件；最终提交哈希以 `git rev-parse --short HEAD` 为准 |

## 决策

- 每轮 task 或 sprint 结束必须创建 Git 提交。
- 提交只包含源码、测试、规范、配置、manifest 和必要脚本。
- 运行中间产物、上传数据、数据库、模型权重、生成报告文件和前端构建结果不直接进入 Git。
- 如需审计中间产物，只在 `docs/harness/data/` 或 `docs/harness/artifacts/` 中登记 manifest。

## 风险和阻塞

- 当前仓库已有此前 staged/untracked 文件；本轮提交必须用 pathspec 限制提交范围，避免误提交无关产物。

## 下一步

完成验证并提交本轮相关文件后，继续确认下一条设计修正项。
