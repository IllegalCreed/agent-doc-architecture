# 项目层文档模型：最小示例

稳态第 3 步要写的 `docs/handbook/engineering/documentation-model.md`。下面是一份可直接改的骨架（虚构的小型开票系统）；只写**已采用**的部分，没采用的列进「暂未采用」。完整词表见 `rules.md`，写回闭环与强制手段见 `lifecycle.md`。

```markdown
# 文档模型（项目层）

> Status: draft
> Last reviewed: 2030-01-02

## AI Quick Path

本文回答：本项目的文档怎么命名、何时建变更文档、改完代码要同步哪些文档。
先读「变更与编号」「写回闭环」；封板前读「封板清单」。

## 变更与编号

- 变更文档放 `docs/plans/<YYYYMMDD-字母NNN-slug>/`，取号 `python3 scripts/doc-lint.py next-id --type <类型名>`。
- 类型字母：feature F、bugfix B、refactor R、test-infrastructure T、docs D、ops O、release C。
- **何时建变更**：跨多个 PR、影响数据 / 接口 / 流程、或需要人批准；一两处改动的修复写进提交说明。默认用轻量形态（只有 requirements + 实施记录）。

## 写回闭环

| 事件 | 必须更新 |
|---|---|
| 开始一项变更 | 建 bundle，主索引加一行 |
| 实现完成 | 状态改 implemented，登记用例，更新索引「下一步」 |
| 发版 | 更新日志、封板测试报告、概览的 Last reviewed |

## 封板清单

1. 打 tag（没有 tag，过期检查不生效）。
2. `python3 scripts/doc-lint.py --release` 0 ERROR。
3. 封板测试报告写入 `docs/reports/tests/releases/YYYYMMDD-<slug>.md`。

## 待人确认

- 构建 / 测试命令：仓库里没有可核实来源，尚无。
- `notes.md` 中的部署说明：未核实，不得当规则执行。

## 建立文档体系本身

不强制为这次搭建建变更文档；若建，按上面阈值，状态写 `implemented`、`Next action` 写「等人验收」。

## 暂未采用

overview、roadmap、releases、inherit_pairs（没有通用层）、CI。有了内容或需要时再建。
```

要点：

- `Status` 写 `draft`，人批准后改 `approved`；规范文档必须有 `Last reviewed`。
- 「待人确认」登记 Agent **无法核实**的事实，不要编进规则。
- 路由表（`AGENTS.md`）的行指向这份文档的对应小节，所以它要**先于**路由表写好。
