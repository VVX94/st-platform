# Session: batch platform defaults

日期：2026-05-27  
参与角色：Planner  
关联任务：批量确认首期技术和验收默认决策

## 用户请求

用户一次性确认了九条建议：

1. 后端 FastAPI + Pydantic + SQLAlchemy/SQLModel。
2. OSS 数据登记和预签名上传策略。
3. 公益科研网站，所有人可用，不做登录和权限校验。
4. React + Vite + TypeScript。
5. 主 Docker 镜像轻量，重依赖算法后续 runner。
6. 首期 `core_spatial_v1` 指标范围。
7. STARmap smoke demo，DLPFC/osmFISH 作为登记和后续 benchmark 数据。
8. Docker Compose 部署验收标准。
9. Harness / CI 审计要求。

## 本轮上下文

- 已确认部署目标：阿里云轻量单机 Docker Compose。
- 已确认存储：SQLite + OSS。
- 已确认 worker：SQLite queued runs + 低并发 worker。

## 执行动作

| 步骤 | 动作 | 文件/命令 | 结果 |
|---|---|---|---|
| 1 | 检索冲突表述 | `rg "登录|权限|鉴权|RBAC|FastAPI|OSS|Vite|core_spatial_v1"` | 找到主文档和 harness 中需要同步的位置 |
| 2 | 更新主目标文档 | `docs/benchmark_platform_design_plan.md` | 写入后端、OSS、无登录、前端、算法、指标、数据集、部署验收和审计要求 |
| 3 | 更新项目结构基线 | `docs/harness/project_structure_map.md` | 移除 auth 模块建议，改为公开访问保护 |
| 4 | 更新部署决策 | `docs/harness/decisions/2026-05-27-deployment-target.md` | 移除鉴权未决项 |
| 5 | 新增批量决策 | `docs/harness/decisions/2026-05-27-batch-platform-defaults.md` | 记录九条已确认决策 |

## 修改文件

| 文件 | 修改类型 | 说明 |
|---|---|---|
| `docs/benchmark_platform_design_plan.md` | 修改 | 批量写入首期默认技术和验收策略 |
| `docs/harness/project_structure_map.md` | 修改 | 同步公开访问策略，不再建议 auth 模块 |
| `docs/harness/decisions/2026-05-27-deployment-target.md` | 修改 | 移除鉴权未决项 |
| `docs/harness/decisions/2026-05-27-batch-platform-defaults.md` | 新增 | 批量决策记录 |
| `docs/harness/sessions/2026-05-27-batch-platform-defaults.md` | 新增 | 本轮审计记录 |

## 验证记录

| 命令/检查 | 结果 | 备注 |
|---|---|---|
| `rg "FastAPI|Pydantic|SQLAlchemy|SQLModel|预签名|公开匿名|Vite|TypeScript|core_spatial_v1|STARmap|部署验收|evaluator report" docs/benchmark_platform_design_plan.md docs/harness/decisions/2026-05-27-batch-platform-defaults.md` | 通过 | 检查九条决策落地 |
| `rg "登录|RBAC|鉴权|auth/|用户系统|API 权限校验|权限校验" docs/benchmark_platform_design_plan.md docs/harness/project_structure_map.md docs/harness/decisions` | 通过 | 仅保留“明确不做登录/RBAC/API 权限校验”的表述，未发现要求实现登录或鉴权 |
| `rg "浏览器大文件上传|登记本地数据集路径|React 工程使用 Vite|明确 SQLite 是否" docs/benchmark_platform_design_plan.md` | 通过 | 未发现旧 TODO 或旧 API 描述残留 |
| `git commit -- docs/benchmark_platform_design_plan.md docs/harness/project_structure_map.md docs/harness/decisions docs/harness/sessions/2026-05-27-batch-platform-defaults.md` | 通过 | 创建本轮审计提交；提交哈希见最终回复 |

## 决策

以 `docs/harness/decisions/2026-05-27-batch-platform-defaults.md` 为准。

## 风险和阻塞

- 公开匿名网站需要通过非身份类限制控制滥用和资源消耗。
- OSS 签名 URL、bucket、RAM 权限和生命周期策略仍需部署前确认。

## 下一步

校验文档一致性并提交本轮 Git 快照。
