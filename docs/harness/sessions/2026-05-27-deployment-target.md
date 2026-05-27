# Session: deployment target confirmation

日期：2026-05-27  
参与角色：Planner  
关联任务：确认 benchmark 平台部署目标和资源策略

## 用户请求

用户确认最终平台需要部署到阿里云服务器。当前测试环境资源有限，应作为规划参考，但不要把临时测试服务器的具体规格写入文档。

## 本轮上下文

- 上一轮已确认 Planner / Generator / Evaluator 三智能体 harness。
- `docs/harness/agent_coding_governance.md` 要求每轮任务结束后提交 Git 快照。
- 当前主目标文档仍保留“Docker / 容器 runner”和“生产级部署和监控”不在首版范围的表述，需要调整为“首个可部署目标包含 Docker Compose，但完整容器化算法隔离和生产级监控告警后续实现”。

## 执行动作

| 步骤 | 动作 | 文件/命令 | 结果 |
|---|---|---|---|
| 1 | 读取目标文档 | `sed -n '1,260p' docs/benchmark_platform_design_plan.md` | 找到首版范围和技术架构位置 |
| 2 | 读取治理规范 | `sed -n '1,240p' docs/harness/agent_coding_governance.md` | 确认本轮需要记录和提交 |
| 3 | 更新部署目标 | `docs/benchmark_platform_design_plan.md` | 增加阿里云 Web 部署目标、Docker Compose 拓扑、服务边界和资源原则 |
| 4 | 记录架构决策 | `docs/harness/decisions/2026-05-27-deployment-target.md` | 新增部署目标 ADR |
| 5 | 记录本轮会话 | `docs/harness/sessions/2026-05-27-deployment-target.md` | 新增审计记录 |

## 修改文件

| 文件 | 修改类型 | 说明 |
|---|---|---|
| `docs/benchmark_platform_design_plan.md` | 修改 | 首版范围加入 Docker Compose / Postgres / Redis / artifact volume；新增部署目标章节 |
| `docs/harness/decisions/2026-05-27-deployment-target.md` | 新增 | 记录阿里云单机 Docker Compose 部署目标 |
| `docs/harness/sessions/2026-05-27-deployment-target.md` | 新增 | 记录本轮用户确认、修改和验证 |

## 验证记录

| 命令/检查 | 结果 | 备注 |
|---|---|---|
| `rg "阿里云|Docker Compose|Postgres|Redis|artifact volume|低并发|临时测试服务器|资源约束" docs/benchmark_platform_design_plan.md docs/harness/decisions/2026-05-27-deployment-target.md docs/harness/sessions/2026-05-27-deployment-target.md` | 通过 | 检查部署目标和资源策略 |
| 敏感规格关键字检查 | 通过 | 未在 `docs/benchmark_platform_design_plan.md` 或 `docs/harness/` 写入临时测试服务器具体规格 |
| `git commit -- docs/benchmark_platform_design_plan.md docs/harness/decisions/2026-05-27-deployment-target.md docs/harness/sessions/2026-05-27-deployment-target.md` | 通过 | 创建本轮审计提交；提交哈希见最终回复 |

## 决策

- 首个部署目标采用阿里云单机 Docker Compose。
- 生产形态默认使用 FastAPI、React/Nginx、worker、Postgres、Redis 和 artifact volume。
- 不把临时测试服务器具体规格写入项目文档。
- 完整容器化算法隔离、弹性扩缩容和生产级监控告警后续分阶段建设。

## 风险和阻塞

- 初期资源有限，重型算法和大数据集 benchmark 需要低并发、后台队列和小型 smoke 参数。
- 生产部署目标提高了首版工程量，需要后续 sprint 明确切分。

## 下一步

验证文档关键字，确认未记录临时测试服务器具体规格，并提交本轮 Git 快照。
