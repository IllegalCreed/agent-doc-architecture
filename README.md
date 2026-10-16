English | [简体中文](README.zh-CN.md)

<div align="center">

# Agent-first Documentation for Large Projects

The first reader of the docs is the agent. The doc system is a routing system.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Skill: agent-first-docs](https://img.shields.io/badge/skill-agent--first--docs-6f42c1.svg)](skill/agent-first-docs/SKILL.md)
[![Blog: 4 posts](https://img.shields.io/badge/blog-4%20posts-orange.svg)](blog/en/01-agent-is-not-amnesiac.md)

</div>

## Why

In a project where an AI agent writes most of the code, the first reader of the documentation is the agent. The documentation system is a routing system for that agent. Agents are not amnesiac. They can't find the entry point.

They have no memory across sessions, so every session is a newcomer walking in through the entry file. When an agent "forgets" a rule, the rule is usually already in the repo, and nothing on the path from that entry points at it. Fix the route, not the model.

The practice comes from seven months of AI-collaborative development on an enterprise payment-approval system. The posts below are the model; the skill is the part you can copy into the next project.

## The L0–L3 model

Three principles, from the [first post](blog/en/01-agent-is-not-amnesiac.md): the entry file only routes, it does not carry content; the always-loaded layer holds only rules that are too late to discover after the damage; current fact and history stay apart, and status and replacement are fields, not tone of voice.

```text
every session (auto-loaded, must stay short)
        │
        ▼
┌──────────────────────────────────────────────────────────┐
│ L0  resident                                             │
│ hard rules (one line, one reason, one link)              │
│ + an "operation → required reading" table                │
└──────────────────────────────────────────────────────────┘
        │  read the one row that matches the task
        ▼
┌──────────────────────────────────────────────────────────┐
│ L1  by work type                                         │
│ one spec: dev / test / DB / release seal / handbook /    │
│ deploy. Shared layer + project layer.                    │
└──────────────────────────────────────────────────────────┘
        │  only when entering that module or change
        ▼
┌──────────────────────────────────────────────────────────┐
│ L2  by module / change                                   │
│ plan bundle, long-running track, handoff                │
│ must have status and a replacement link                  │
└──────────────────────────────────────────────────────────┘
        │  only when evidence is needed
        ▼
┌──────────────────────────────────────────────────────────┐
│ L3  evidence                                             │
│ release-seal test reports, audits, incident reports      │
│ never an entry point                                     │
└──────────────────────────────────────────────────────────┘

Deliverables — changelog, user manual, ops handover —
sit outside this stack. The agent maintains them.
It does not learn the job from them.
```

| Layer | What it holds | When it is read | Constraint |
|---|---|---|---|
| L0 resident | Hard rules in the entry file, plus the routing table | Loaded automatically every session | Must stay short |
| L1 by work type | Specs (dev, test, DB, release seal, handbook, deploy) | Before starting, and only the one row the table names | Shared layer + project layer |
| L2 by module / change | Plan bundles, long-running tracks, handoff docs | When entering that module | Has status and a replacement link |
| L3 evidence | Release-seal test reports, audit output, incident reports | Drill down when evidence is needed | Does not serve as an entry |

## The series

1. [Agents Aren't Amnesiac — They Can't Find the Entry Point](blog/en/01-agent-is-not-amnesiac.md) — the model
2. [Make the Agent Read Only What It Should](blog/en/02-routing.md) — routing
3. [Give Every Document Exactly One Place](blog/en/03-addressing.md) — addressing
4. [Keep Documents from Rotting](blog/en/04-lifecycle.md) — lifecycle

Chinese originals live in [blog/](blog/01-agent-is-not-amnesiac.md). The design notes (thesis, outline, and the fact base the numbers come from) are in Chinese: [specs/2026-10-14-blog-series-design.md](specs/2026-10-14-blog-series-design.md).

## Skill: agent-first-docs

The series is packaged as a skill you can drop into an agent, at [skill/agent-first-docs/](skill/agent-first-docs/):

- `SKILL.md` — when to use it, the 10 decisions you cannot skip, the steady-state steps, and the red flags.
- `references/` — routing, the vocabulary and format cheat sheet, decisions and evidence, lifecycle, onboarding an existing tree, and the full shared spec.
- `assets/` — `scripts/` (`doc-lint`, link checking, `next-id`, `init-baseline`, 64+ unit tests) and `templates/` (the document templates).

The skill documentation is in Chinese. An English edition is coming.

Install: copy `skill/agent-first-docs/` to `~/.claude/skills/` (or your agent's skills directory).

```bash
cp -R skill/agent-first-docs ~/.claude/skills/
```

## Repository

```text
README.md          English (this file)
README.zh-CN.md    简体中文
specs/             Design notes: thesis, outline, fact base — read before writing
plans/             Writing plans for the series
blog/              Blog series, Chinese (4 posts)
blog/en/           English translations of the same four posts
scripts/           Post checker check-post.py
                   (redaction, length, required sections, number sourcing;
                   --repo scans the whole repo)
tests/             Unit tests for the checker
                   (python3 -m unittest discover -s tests)
skill/             The skill extracted from the series: agent-first-docs
                   (SKILL.md + references/ + assets/ you can copy)
```

## License

[MIT](LICENSE)
