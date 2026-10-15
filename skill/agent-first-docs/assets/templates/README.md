# 文档模板目录

> 本目录放在项目的 `docs/handbook/templates/`（doc-lint 默认从这里读取模板）。路径列均相对 `docs/`。

> 每种文档只有一个模板。新建文档：复制对应模板 → 删除首行 `<!-- template … -->` 头注释 → 按章节内注释填写。**禁止参考上一份同类文档的结构仿写**：上一份的偏差会被复制并叠加。

## 使用规则

- 模板 H2 即必备章节，文字与顺序不可改（可带「1.」「一、」编号）；无内容写「无」。带「（可选）」的章节不用就删，用时去掉「（可选）」。允许增加模板外的章节。
- 头注释 `applies-to` 声明本模板管辖的路径，`must-contain` / `must-not-contain` 声明必含 / 禁止字段（HTML 注释内的文字不计）。doc-lint 直接读取模板检查，不另维护规则清单。
- 没有适用模板的文档类型：先在本目录建模板并登记下表，再写文档。
- 改模板不追溯已有文档；接入前的存量不合规文档登记在接入配置 `template_exceptions`，只减不增。

## 目录

| 类型 | 模板 | 适用于 | 写 / 读 |
|---|---|---|---|
| 需求 | [plan/requirements.md](plan/requirements.md) | bundle `requirements.md`（标准 / 轻量共用） | Agent 写，用户批准 |
| 设计 | [plan/design.md](plan/design.md) | bundle `design.md` | Agent |
| 实施记录 | [plan/implementation.md](plan/implementation.md) | bundle `implementation.md` | Agent |
| 测试用例 | [plan/test-cases.md](plan/test-cases.md) | bundle `test-cases.md` | Agent |
| 交接 | [plan/handoff.md](plan/handoff.md) | bundle `handoff.md` | 交接方写，执行 / 审核 Agent 读 |
| 影响面 | [plan/impact-map.md](plan/impact-map.md) | bundle `impact-map.md` | Agent |
| 手工用例 | [plan/manual-test-cases.md](plan/manual-test-cases.md) | bundle `manual-test-cases.md` | Agent 写，用户执行 |
| 阶段划分 | [plan/stages.md](plan/stages.md) | bundle `stages.md` | Agent |
| 阶段分册 | [plan/stage.md](plan/stage.md) | bundle `stage<N>-<slug>.md` | Agent |
| 复审 | [plan/review.md](plan/review.md) | bundle `review-<agent>-YYYYMMDD.md` | 审查 Agent |
| 长期专题 | [plan/track-readme.md](plan/track-readme.md) | `plans/tracks/<主题>/README.md` | Agent |
| 更新日志 | [release/notes.md](release/notes.md) | `releases/vX.Y.Z.md` | Agent 写，最终用户读 |
| 交接说明 | [release/delivery.md](release/delivery.md) | `releases/vX.Y.Z-delivery.md` | Agent 写，运维读 |
| 封板测试报告 | [release/test-report.md](release/test-report.md) | `reports/tests/releases/` | Agent |
| 专项测试报告 | [testing/test-report.md](testing/test-report.md) | `reports/tests/`（封板报告除外） | Agent |
| 人工回归 | [testing/regression.md](testing/regression.md) | `testing/cases/regressions/` | Agent 写，用户执行 |
| 规则目录 | [testing/catalog.md](testing/catalog.md) | `testing/cases/catalogs/` | Agent |
| 事故报告 | [report/incident.md](report/incident.md) | `reports/incidents/YYYY-MM/` | Agent |
| 审计报告 | [report/audit.md](report/audit.md) | `reports/audits/`、`reports/security/` | Agent |
| 迁移证据包 | [report/migration-readme.md](report/migration-readme.md) | `reports/migrations/<主题>/README.md` | Agent |
| 迁移执行记录 | [report/migration-record.md](report/migration-record.md) | `reports/migrations/<主题>/*.md` | Agent / 运维 |
| 运维记录 | [report/operations.md](report/operations.md) | `reports/operations/YYYY-MM/` | Agent / 运维 |
| 分析报告 | [report/analysis.md](report/analysis.md) | `reports/analysis/`、`reports/refactoring/` | Agent |
| 规范文档 | [handbook/handbook.md](handbook/handbook.md) | `handbook/`、`testing/guides/` | Agent |
| 部署手册 | [handbook/runbook.md](handbook/runbook.md) | `deployment/` | Agent 写，运维读 |
| 项目概览 | [singleton/overview.md](singleton/overview.md) | `overview.md` | Agent |
| 路线图 | [singleton/roadmap.md](singleton/roadmap.md) | `roadmap.md` | Agent |
| 变更索引 | [singleton/plans-index.md](singleton/plans-index.md) | `plans/index.md` | Agent |
| 用例索引 | [singleton/cases-index.md](singleton/cases-index.md) | `testing/cases/index.md` | Agent |
| 用户手册 | [singleton/operation-manual.md](singleton/operation-manual.md) | `operation-manual.md` | Agent 写，最终用户读 |
| 目录 README | [singleton/dir-readme.md](singleton/dir-readme.md) | 各级目录 `README.md` | Agent |
