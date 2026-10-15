# 词表与格式速查

下面是 `doc-lint` 检查的主要内容（个别「顺序固定」「终态写 `-`」只是约定，工具不查）。词表集中在 `scripts/doclint/vocab.py`；要换语言，还需同步 `plans.py`、`cases.py` 里按中文列名取列的地方（vocab 的 docstring 有说明）。

## 变更：编号、元信息、状态

**Stable ID** = `<字母>-YYYYMMDD-NNN`；目录 = `YYYYMMDD-<小写字母>NNN-<slug>/`，两者机械互推。`NNN` 按（日期，字母）各自从 001 起；slug 是 `[a-z0-9-]+`（中文标题写在 H1 和索引里）。取号永远用 `doc-lint next-id --type <类型>`：它扫描所有本地分支、远端跟踪分支和所有 worktree，防并行分支撞号。撞号时**后占方搬移**，内容不变，写明原号。

| 类型 | 字母 | 用途 |
|---|---|---|
| feature | F | 新能力 |
| bugfix | B | 修复缺陷（记录复现、根因、回归用例） |
| refactor | R | 结构调整，外部行为不变 |
| test-infrastructure | T | 测试框架、fixture、补覆盖专项 |
| docs | D | 文档规范、治理 |
| ops | O | 部署、环境、运维 |
| release | C | 封板、出包（字母映射在 `vocab.py`，想改就改那里，定义后不得再改） |

**元信息块**（`requirements.md` 的 H1 之后，英文键，顺序固定；必需 7 键）：

```markdown
> Status: draft
> Stable ID: F-20260101-001
> Type: feature
> Created: 2026-01-01
> Last reviewed: 2026-01-01
> Replaces: none
> Replaced by: none
```

可选键放在必需键之后：`Owner`、`Progress`、`Blocked by`、`Next action`、`Related plans`、`Related tests`。

| 状态 | 含义 | Agent 怎么用 |
|---|---|---|
| draft | 讨论中 | 只能参考背景，不得作为实现依据 |
| approved | 已批准，未实现 | 可作为实现依据 |
| in-progress | 实施中 | 实现时同步回填 |
| implemented | 代码已落地，验证未完整 | 读实施记录与测试记录 |
| verified | 实现与验证均确认（含已发布） | 可作为当前事实 |
| superseded | 被新变更接管 | **必须**跳到 `Replaced by`（doc-lint 检查它写的是主索引里已登记的 Stable ID：`BUNDLE-SUPERSEDE`）；原目录原地保留，不搬 |
| deprecated | 不再代表当前行为，仍有历史价值 | 只用于追溯 |
| obsolete | 已失效 | 不得作为实现依据 |
| cancelled | 决定不做 | 不得作为实现依据；看取消原因 |

## 变更的形态

| 形态 | 判定 | 必需文件 |
|---|---|---|
| 标准 | 含 `design.md` | `requirements.md`、`design.md`、`implementation.md`（状态 ≥ implemented）、`test-cases.md` |
| 轻量 | 不含 `design.md` | `requirements.md`；状态 ≥ implemented 时必须有 `## 实施记录` 节 |

可选文件白名单（只允许这些名字）：`impact-map.md`、`handoff.md`、`manual-test-cases.md`、`stages.md` + `stage<N>[a-z]-<slug>.md`、`review-<agent>-YYYYMMDD.md`。新增白名单外文件报错——脚本放 `scripts/`，不放变更目录。

阅读顺序：requirements → design → impact-map → implementation → test-cases；`handoff` / `review` / `manual-test-cases` 只在执行、审核、验收时读。

## 主索引（`docs/plans/index.md`）

只有：H1、一行说明、一张表、专题入口。表头固定六列：

```
| Stable ID | Type | 标题 | 状态 | 下一步 | Plan |
```

标题 ≤ 50 字；下一步 ≤ 80 字，终态（verified / superseded / deprecated / obsolete / cancelled）写 `-`；Plan 列只放变更入口链接。**禁止日期横幅和多行导语**——进度写进变更自己的文档，版本动态写路线图（路线图横幅最多 5 块，旧的归档）。

## 目录、命名、专题

- 目录按**职责**：当前事实（handbook、overview）、变更（plans）、测试定义（testing）、执行证据（reports）、发布（releases）、运维（deployment）、附件（assets）。每个目录 README 写「放置规则」表。
- 记录类目录（reports、releases 等）文件名 `YYYYMMDD-<slug>.md`；发布文档 `vX.Y.Z.md` / `vX.Y.Z-delivery.md`；中文标题写在 H1。
- **bundle 是短期**（一次可交付的变更，多阶段大变更也是一个 bundle + `stages.md`）；**track 是长期**（跨多个独立变更的主题导航）：只写为什么、先后顺序、边界、关联变更链接，**不放 plan、不写状态**。
- 用例编号 `TC-<模块>-NNN`（无版本段）。用例主表是唯一事实源，按层级 / 按模块的视图由 `gen-views` 生成，不手写。

## 用例层级

工具词表固定为 `L1`–`L5` + `manual`（`vocab.py` 的 `CASE_LAYERS`）。含义由**项目测试规范**定义；项目还没有测试规范时，在用例主表顶部写一行「层级暂定义：L1 …」（尚无任何用例时可不写），等规范建立后迁过去。一个用例只归一个主层级。

## 用例表

主表表头固定九列：`Case ID | 标题 | 所属功能 / 模块 | Owner Plan | 层级 | 自动化路径 | 状态 | 最后验证 | 备注`；用例状态：`active` / `stale` / `deprecated` / `obsolete`。

## 模板

`templates/README.md` 是目录；模板第一行起的 `<!-- template … -->` 头注释声明 `applies-to`（glob；多个用全角「；」）、`must-contain` / `must-not-contain`；头注释之后的 H2 就是必备章节，按顺序检查，以「（可选）」结尾的不强制。模板里不写 Markdown 链接。没有适用模板的文档类型：先建模板并登记目录，再写文档。
