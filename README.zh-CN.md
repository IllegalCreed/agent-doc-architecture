[English](README.md) | 简体中文

<div align="center">

# Agent-first 大型项目文档分层

文档的第一读者是 Agent，文档体系是给 Agent 用的路由系统。

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Skill: agent-first-docs](https://img.shields.io/badge/skill-agent--first--docs-6f42c1.svg)](skill/agent-first-docs/SKILL.md)
[![Blog: 4 posts](https://img.shields.io/badge/blog-4%20posts-orange.svg)](blog/01-agent-is-not-amnesiac.md)

</div>

## 为什么

在 AI Agent 写大部分代码的项目里，文档的第一读者是 Agent。文档体系是给 Agent 用的路由系统。Agent 不是失忆，是找不到入口。

它本来就没有跨会话记忆，每次会话都是从入口走进来的新人。所谓「忘了」，通常是规范已经在仓库里，从入口出发却没有路标指向它。要修的是路由，不是模型。

这套实践来自某企业级支付审批系统 7 个月的 AI 协作开发。下面的系列是模型，skill 是可以抄进下一个项目的部分。

## L0–L3 总模型

三条原则，见[第一篇](blog/01-agent-is-not-amnesiac.md)：入口只路由、不承载；常驻层只放违反了就来不及的约定；当前事实和历史分开，状态与替代关系写成字段，而不是靠语气去意会。

```text
每次会话（自动加载，必须短）
        │
        ▼
┌──────────────────────────────────────────────────────────┐
│ L0  常驻                                                 │
│ 硬约定（一句规则、一句理由、一个链接）                   │
│ + 「操作 → 必读」表                                      │
└──────────────────────────────────────────────────────────┘
        │  只读与手头任务对应的那一行
        ▼
┌──────────────────────────────────────────────────────────┐
│ L1  按工作类型                                           │
│ 一份规范：开发 / 测试 / DB / 封板 / 手册 / 部署          │
│ 通用层 + 项目层                                          │
└──────────────────────────────────────────────────────────┘
        │  进入该模块或该变更时才读
        ▼
┌──────────────────────────────────────────────────────────┐
│ L2  按模块 / 变更                                        │
│ plan bundle、长期专题、交接文档                          │
│ 必须有状态、有替代关系                                   │
└──────────────────────────────────────────────────────────┘
        │  需要证据时才下钻
        ▼
┌──────────────────────────────────────────────────────────┐
│ L3  证据                                                 │
│ 封板测试报告、审计输出、事故报告                         │
│ 不承担入口职责                                           │
└──────────────────────────────────────────────────────────┘

交付物——更新日志、用户手册、运维交接说明——在这四层之外。
Agent 维护它们，但不从它们获取工作知识。
```

| 层 | 内容 | 何时读 | 约束 |
|---|---|---|---|
| L0 常驻 | 入口文件硬约定 + 路由表 | 每次会话自动加载 | 必须短 |
| L1 按工作类型 | 规范（开发 / 测试 / DB / 封板 / 手册 / 部署） | 开工前按路由表只读一份 | 通用层 + 项目层 |
| L2 按模块 / 变更 | plan bundle、长期专题、交接文档 | 进入该模块时 | 有状态、有替代关系 |
| L3 证据 | 封板测试报告、审计输出、事故报告 | 需要证据时下钻 | 不承担入口职责 |

## 系列

1. [Agent 不是失忆，是找不到入口——总模型](blog/01-agent-is-not-amnesiac.md)
2. [让 Agent 只读该读的——路由](blog/02-routing.md)
3. [让每份文档都有唯一的位置——寻址](blog/03-addressing.md)
4. [让文档不烂——生命周期](blog/04-lifecycle.md)

英文译本在 [blog/en/](blog/en/01-agent-is-not-amnesiac.md)。设计（系列论点、大纲、事实素材库）见 [specs/2026-10-14-blog-series-design.md](specs/2026-10-14-blog-series-design.md)。

## Skill：agent-first-docs

系列落成可直接使用的 skill，中英各一份，规则相同，文档语言不同：

- [skill/agent-first-docs/](skill/agent-first-docs/)：简体中文。项目文档用中文时安装这一份。
- [skill/agent-first-docs-en/](skill/agent-first-docs-en/)：英文。项目文档用英文时安装这一份。

每一份都是自包含的，复制整个目录即可单独使用：

- `SKILL.md`：何时使用、10 条不能省的决策、稳态步骤、red flags。
- `references/`：路由、词表与格式速查、决策与证据、生命周期、接入（存量项目）、通用规范全文。
- `assets/`：`scripts/`（doc-lint、链接检查、`next-id`、`init-baseline`，64+ 个单测）与 `templates/`（通用文档模板）。

各版的检查器只认该版的标签。中文版的索引表头、用例表头、实施记录标题、继承标记是中文（`scripts/doclint/vocab.py`）；英文版是英文。不要混用。

安装：把其中一个 skill 目录复制到 `~/.claude/skills/`（或你的 Agent 的 skills 目录）。

```bash
# 简体中文
cp -R skill/agent-first-docs ~/.claude/skills/

# 英文
cp -R skill/agent-first-docs-en ~/.claude/skills/
```

两个目录的 skill 名不同（`agent-first-docs` 与 `agent-first-docs-en`），可以同时放在 skills 目录里。安装与你要写的文档语言一致的那一份。

## 仓库结构

```text
README.md          英文（面向国际读者）
README.zh-CN.md    简体中文（本文件）
specs/             设计文档（系列论点、大纲、事实素材库）——写作前先读
plans/             写作执行计划
blog/              博客系列正文（4 篇，中文）
blog/en/           同四篇的英文译本
scripts/           稿件检查脚本 check-post.py
                   （脱敏、篇幅、章节、数字出处；--repo 全仓脱敏扫描）
tests/             检查脚本的单元测试
                   （python3 -m unittest discover -s tests）
skill/             系列提炼出的 Agent skill
                   agent-first-docs（中文）与 agent-first-docs-en（英文）
                   （各自含 SKILL.md + references/ + 可直接复制的 assets/）
```

## 许可

[MIT](LICENSE)
