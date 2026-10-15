---
name: agent-first-docs
description: Use when setting up, restructuring or auditing project documentation that AI coding agents read and write — agents don't know which docs to read, read stale or superseded docs, forget to write results back, or plans, test reports, release notes and indexes sprawl. Also when adding doc naming/numbering rules, doc templates, a doc linter, or migrating an existing docs tree. 中文触发：文档分层、Agent 失忆、文档索引、plan 编号、文档模板、doc-lint、文档治理、存量文档迁移。
---

# Agent-first 文档体系

## 核心

文档的第一读者**和主要作者**都是 Agent。体系的本质是**路由系统**：让 Agent 用最少上下文读到该读的、信得过的、并且知道写到哪。三个问题，缺一不可：

| 问题 | 机制 | 细节 |
|---|---|---|
| 该读哪几份？ | 入口文件只路由 + 「操作 → 必读」表 | `references/routing.md` |
| 去哪找、信哪份？ | 职责目录、稳定编号、主索引、状态与替代链、模板 | `references/decisions.md`（为什么）· `references/rules.md`（词表与格式速查） |
| 写到哪、怎么不烂？ | 写回闭环、机器检查、新鲜度 | `references/lifecycle.md` |

人是**裁决者**（批准、拍板、验收），不是读者也不是维护者。完整的通用规范文本（可复制进项目当通用层）：`references/general-model.md`。

## 先判断模式

| 项目现状 | 模式 | 做法 |
|---|---|---|
| 没有或几乎没有 docs | **稳态**：第一天按规则建，无豁免，基线为零 | 下面「步骤」 |
| 已有计划、报告、索引等 | **接入**：保留原文，先冻结、再收紧 | `references/onboarding.md` |

## 不能省的决策

Agent 自己搭体系时，下面这些最容易选错（每条的证据和被否决的做法见 `references/decisions.md`）：

1. **变更要有稳定 ID**（`<字母>-YYYYMMDD-NNN`，目录 `YYYYMMDD-<字母>NNN-slug`），用 `python3 scripts/doc-lint.py next-id --type <类型名>` 取号；只用日期会在同一天撞名。
2. **做完的变更原地不动**，状态写在元信息里；不要为「归档」移目录（会断掉所有引用）。被替代的历史才放 `docs/plans/archive/`。
3. **旧文档不删、不改写**；挪走的文字存进迁出记录。
4. **索引只回答「去哪读」**：固定列、限行宽；状态以文档元信息为准，索引是它的投影。
5. **一种文档一个模板**，模板头注释就是检查规则；禁止「参考上一份同类文档」。
6. **过期按「早于最近一次发布」提示**，不按天数报错（会逼 Agent 只改日期不核对）；封板前先打 tag，这项比较才生效。
7. **不预写没有内容的文档**；不存在的东西不建指南。
8. **强制靠路由表里的一行 + 封板门禁**，有 CI 就挂 CI；检查工具本身也要被测试。
9. **入口文件每条 = 规则 + 一句理由 + 链接**；其他 Agent 的入口文件只转发。
10. **个人记忆只放协作偏好**，项目教训进仓库（别的 Agent 看不到你的记忆）。

## 步骤（稳态）

1. 把本 skill 的 `assets/scripts/` 复制为项目的 `scripts/`，`assets/templates/` 复制为 `docs/handbook/templates/`。
2. 建 `docs/README.md`（按**职责**分目录，不按类型或状态）、`docs/plans/index.md` 和 `docs/testing/cases/index.md`（模板 `singleton/plans-index.md`、`singleton/cases-index.md`，缺一个 doc-lint 就报错），再跑 `doc-lint.py gen-views`。
3. **先写项目层文档模型** `docs/handbook/engineering/documentation-model.md`（模板 `handbook/handbook.md` 只给骨架；内容照 `references/project-model-example.md`：编号字母、何时建变更、写回闭环、封板清单、「待人确认」「暂未采用」），**再**在入口文件（`AGENTS.md`）写路由表，见 `references/routing.md`——路由行指向的文件必须已存在，否则 `LINK-ENTRY` 报错。规范文档必须带 `Last reviewed: YYYY-MM-DD`；Agent 起草的规范 `Status` 写 `draft`，人批准后才改 `approved`。
4. 新建任何文档：先 `cp` 对应模板、删头注释（`sed '1,/^-->/d' 模板 > 新文档`，H1 保留）、按章节填写。取号：`python3 scripts/doc-lint.py next-id --type <类型>`。
5. 入口文件已存在时**合并而不是重写**：保留原有规则（补上理由和链接），追加路由表；路由行指向的规范还不存在就别建，写「尚无」。
6. 跑 `python3 scripts/doc-lint.py`，直到 0 ERROR；单测：`python3 -m unittest discover -s scripts/doclint/tests -t scripts`。
7. `.gitignore` 加 `__pycache__/`（复制来的脚本和单测会产生）；复制 `assets/scripts` 时先清掉它里面已有的 `__pycache__`。
8. 把「改 docs 后提交前跑 doc-lint」写进路由表，把「`doc-lint --release` 0 ERROR」写进封板清单。

命令速查：`doc-lint.py`（全部检查）· `--release`（封板模式，概览/路线图过期升为 ERROR）· `next-id --type <feature|bugfix|refactor|test-infrastructure|docs|ops|release>`（传类型名，不是字母）· `gen-views`（重生成用例视图）· `init-baseline`（接入模式，见 onboarding）。

## Red flags — 停下来

| 想法 | 现实 |
|---|---|
| 「先全部迁成新格式，再开检查」 | 接入模式先冻结、写基线，再逐步收紧 |
| 「日期、项目路径写进检查代码更省事」 | 只进接入配置；代码保持项目无关 |
| 「完成了就挪去 archive」 | 路径稳定优先，状态写元信息 |
| 「检查脚本过了就是对的」 | 它查不了内容是否真的新；写回闭环和人的裁决不能省 |
| 「把旧文档里的内容整理一下再迁」 | 原样搬移保留信息，但**搬前后各核一遍事实**（原样搬会连错误一起搬走） |
| 「个人记忆里有，不用写进仓库」 | 其他 Agent 读不到 |
