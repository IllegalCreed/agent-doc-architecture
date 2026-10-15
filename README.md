# Agent-first 大型项目文档分层

一个企业级支付审批系统 7 个月 AI 协作开发中沉淀的文档分层实践：**文档的第一读者是 Agent**，文档体系就是给 Agent 用的路由系统。

## 结构

```text
specs/   设计文档（系列论点、大纲、事实素材库）——写作前先读
plans/   写作执行计划
blog/    博客系列正文（4 篇）
scripts/ 稿件检查脚本 check-post.py（脱敏、篇幅、章节、数字出处；--repo 全仓脱敏扫描）
tests/   检查脚本的单元测试（python3 -m unittest discover -s tests）
skill/   系列定稿后提炼的 Agent skill（待建）
```

## 系列

1. [Agent 不是失忆，是找不到入口——总模型](blog/01-agent-is-not-amnesiac.md)
2. [让 Agent 只读该读的——路由](blog/02-routing.md)
3. [让每份文档都有唯一的位置——寻址](blog/03-addressing.md)
4. [让文档不烂——生命周期](blog/04-lifecycle.md)

设计见 [specs/2026-10-14-blog-series-design.md](specs/2026-10-14-blog-series-design.md)。
