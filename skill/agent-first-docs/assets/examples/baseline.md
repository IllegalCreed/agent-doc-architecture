# 接入配置 `baseline.json` 说明

`scripts/doclint/baseline.json` 是存量项目中途采用本规则时的**接入配置**：把接入那一刻已有的违规登记为豁免，让 `doc-lint` 立即 0 ERROR，此后只有**新增**违规会失败。JSON 不能写注释，所以逐键说明放在本文件；[baseline.json](baseline.json) 是一份虚构项目的示例。

新项目不需要这个文件：文件不存在时 `doc-lint` 按「无豁免、断链基线 0、bundle 平铺在 `docs/plans/` 下」严格检查。

## 生成

```bash
python3 scripts/doc-lint.py init-baseline                      # 只打印将写入的 JSON
python3 scripts/doc-lint.py init-baseline --write              # 写入 scripts/doclint/baseline.json
python3 scripts/doc-lint.py init-baseline --bundle-root docs/plans/changes --frozen docs/plans/legacy --write
```

- 先把下面「不可豁免」的问题修掉：`init-baseline` 发现它们时逐条打印 `must-fix …`、退出码 1、**不写文件**。
- 写入后再跑 `python3 scripts/doc-lint.py`，应为 0 ERROR。

### 不可豁免（must-fix）

工具依赖它们解析其余内容，或改动很小、没有对应的豁免键，必须接入前修好。完整清单见 `scripts/doclint/onboard.py` 的 `MUST_FIX`，主要是：

- 结构性：缺 `docs/plans/index.md`（PLAN-INDEX-MISSING）或 `docs/testing/cases/index.md`（CASE-INDEX-MISSING）；索引 / 用例表头错误、列数不齐；Stable ID 或 Case ID 重复；状态 / 类型 / 层级不在词表；模板缺头注释或未登记目录。
- 局部：入口文档断链（LINK-ENTRY）、索引日期横幅、bundle 未登记 / 元信息缺失、生成视图过期（跑 `gen-views`）、规范文档缺 `Last reviewed` 等。

两个索引可以直接从模板建：复制 `docs/handbook/templates/singleton/plans-index.md`、`singleton/cases-index.md`，删掉首行头注释，然后跑 `python3 scripts/doc-lint.py gen-views`。

## 豁免只减不增（ratchet）

- 四个豁免列表（`naming_exceptions`、`bundle_file_exceptions`、`case_id_exceptions`、`template_exceptions`）和 `broken_links_total` 是**只能变小**的棘轮。
- 某条豁免对应的文件被删除、改名或已经合规时，`doc-lint` 报 `WARN BASELINE-STALE <路径>`，提示把该条从配置里删掉；断链数低于基线时报 `INFO LINK-BASELINE`，提示下调 `broken_links_total`。
- 删除失效条目可以手改 JSON，也可以重跑 `init-baseline --write`，二者等价。**重跑只会删除条目，绝不会新增**：已有配置时，列表取与现有配置的交集、断链基线取较小值，新出现的违规不会被登记，而是作为 `must-fix` 报出（退出码 1、不写文件）。
- 不要用 `init-baseline` 给新违规「补豁免」；新违规就地修。确需从头重新接入（例如大规模迁移后），先删掉 `baseline.json` 再跑——这是一次需要评审的显式决定。

## 逐键说明

| 键 | 由谁维护 | 含义 | 缺省 |
|---|---|---|---|
| `bundle_root` | `init-baseline`（`--bundle-root` 优先，其次沿用现值，再次 `docs/plans/changes` 存在时自动取） | 变更 bundle 的根目录；`docs/plans/index.md` 的 Plan 链接按它解析，模板头注释里的 `{bundle_root}` 也替换成它 | `docs/plans`（bundle 平铺） |
| `rules_effective_since` | `init-baseline`（首次接入取当天 `YYYYMMDD`，重跑沿用） | 规则生效日。目录日期早于它的 bundle 不检查「Stable ID 首字母与 Type 对应」（BUNDLE-ID-LETTER） | 无：全部严格检查 |
| `frozen_dirs` | `init-baseline --frozen`（不给则沿用现值） | 冻结目录：整目录不做模板一致性检查，用于只读的历史归档 | `[]` |
| `broken_links_total` | `init-baseline`；只可下调 | 全库（`docs/` 与 `AGENTS.md`）断链数上限，超过即 ERROR。入口文档（`AGENTS.md`、`docs/README.md`、`docs/handbook/`、`docs/testing/` 等）的断链不受此基线保护，始终 ERROR | `0` |
| `naming_exceptions` | `init-baseline`；只减不增 | 不符合 `YYYYMMDD-<英文slug>.md` 命名的存量记录类文件（`docs/reports/`、`docs/testing/infrastructure/`、`docs/releases/`），仓库相对路径 | `[]` |
| `bundle_file_exceptions` | `init-baseline`；只减不增 | bundle 内不在文件白名单的存量文件，写成相对 `bundle_root` 的 `<bundle 目录>/<文件名>`；同时跳过这些文件的模板检查 | `[]` |
| `case_id_exceptions` | `init-baseline`；只减不增 | 格式不符合 `TC-<模块>-NNN` 的存量 Case ID（ID 稳定、不可改名）。只豁免格式，重复仍报错 | `[]` |
| `template_exceptions` | `init-baseline`；只减不增 | 不符合所匹配模板（必备章节 / 必含字段）的存量文档，仓库相对路径 | `[]` |
| `inherit_pairs` | 手工；`init-baseline` 原样保留 | `[项目层, 通用层]` 路径对：项目层前 15 行须有「> 继承：」链接到通用层，通用层前 20 行须有「> 项目落地：」链接回项目层 | `[]` |
| `fresh_docs` | 手工；`init-baseline` 原样保留 | 需要 `Last reviewed: YYYY-MM-DD` 的当前事实文档（glob，`*` 不跨目录、`**/` 跨目录）。早于最近一个 tag 报 WARN | `docs/overview.md`、`docs/roadmap.md`、`docs/deployment/README.md`、`docs/handbook/**/*.md`、`docs/testing/guides/*.md` |
| `strict_fresh` | 手工；`init-baseline` 原样保留 | `fresh_docs` 中在 `--release`（封板）模式下过期即 ERROR 的文档 | `docs/overview.md`、`docs/roadmap.md` |

示例中 `inherit_pairs` 的两个路径只是演示，接入时按项目实际放置通用层与项目层文档的位置填写；没有分层就省略该键。
