# Routing: make the agent read only what it should

The entry file only routes. It is not an encyclopedia. An agent has no memory across sessions and a limited context, so every time it comes in through the entry it must know, within a few seconds, which document to read first for this task.

## Four layers

| Layer | Contents | When to read | Constraint |
|---|---|---|---|
| L0, resident | The entry file: hard rules plus the routing table | Loaded automatically every session | Must stay short |
| L1, by kind of work | Specs (development, testing, database, release seal, deployment, …) | Before starting, read only the one row the routing table names | Shared layer plus project layer |
| L2, by module or change | Change documents, long-lived topics, handoff documents | When entering that module | Has a status and a replacement relationship |
| L3, evidence | Test reports, audits, incident records | Drill in when evidence is needed | Never an entry point |

The user manual, the changelog, and the delivery note are **deliverables**. Their readers are business users and operators. They do not enter this routing stack. The routing table only records when each of them must be updated.

## Entry-file skeleton

```markdown
# AGENTS.md

## L0 hard rules
<Each item: a rule, one sentence of reason, and a link. Full worked cases live in L1/L2; this file only keeps the link>

## Operation → required spec
| Operation | Required spec | One-line point |
|---|---|---|
| Create or edit any document under docs | [documentation-model.md](docs/handbook/engineering/documentation-model.md) | Copy a template first; do not imitate the previous document. Run doc-lint before committing, 0 ERROR. Take numbers with next-id |
| Write, change, or review any test | [project-testing.md](docs/testing/guides/project-testing.md) | Pick the layer from "kind of work → test layer" first |
| Seal a release, produce a package, or cut a tag | [release-process.md](docs/handbook/engineering/release-process.md) | The full definition is that file. Before sealing, doc-lint --release is 0 ERROR |
| Change the database schema | [database-changes.md](docs/handbook/database/database-changes.md) | A schema change requires an incremental script |
| Code review | That change's handoff review checklist | A conclusion must carry "path:line" evidence |

**Write the required-spec column as a Markdown link.** `doc-lint`'s `LINK-ENTRY` checks links only. A bare path that points at a missing file is not reported.

**Layered reading.** L0 is always in force. Before starting, L1 means reading only the one row the routing table names. Read L2 when you enter the module. Do not read the whole tree for one task, and do not start from memory without reading L1.
```

### How to choose rows

- **Include** operations that are high-risk, infrequent, and easy to get wrong from memory (sealing a release, a database change, writing tests, changing a core engine, code review).
- **Leave out** everyday coding that is frequent and low-risk.
- **The "one-line point" column is required.** Even if the agent does not follow the link, it still has the single most important constraint.
- When the spec a row would point at **does not exist yet**, do not pre-create an empty document. Point at a section of a document that does exist (for example the "release-seal checklist" section of the project-layer documentation model), and say "no dedicated document yet" in the one-line point.
- If the project already has a root `README.md`, add one line pointing at `docs/README.md` and leave the rest alone. When build, run, or test commands still have no source you can verify, the entry file says "none yet, awaiting a person". **Do not invent them.**
- The routing table is an index **by kind of work**, not by directory. The agent knows what it is about to do. It does not know where the document lives.

## Every hop names the next hop

- The documentation entry (`docs/README.md`) opens by saying "find a document by its duty; do not guess a location from a filename".
- Each top-level directory README is a second-level route plus placement rules.
- Each spec opens with `## AI Quick Path`: what question this document answers, what to read first, and the 1–3 constraints that matter most.

## Shared layer → project layer

Specs come in two layers. The **shared layer** is reusable across projects and leaves placeholders. The **project layer** fills those placeholders and records the current state, the exceptions, and the pitfalls of this project. Within its first 15 lines the project layer writes `> Inherits:` and links the shared layer. Within its first 20 lines the shared layer writes `> Project landing:` and links each project layer. Register the pair in `inherit_pairs` of `scripts/doclint/baseline.json` (a new project with no legacy exemptions may have a file that contains only this key). `doc-lint` checks that both ends declare the link. Without the declaration, an agent that follows the routing table into the project layer does not learn that a shared spec still has to be read.

## Several agents

There is **one** entry file (for example `AGENTS.md`). Other agents' entry files (`CLAUDE.md` and the like) only forward: "The spec is `AGENTS.md`. Do not copy rules here." A lesson that applies generally goes in the repo. It does not stay in one agent's personal memory.

## A handoff is a one-time route

When you hand a task to another agent to carry out or to review, write `handoff.md`: what to read first (in order), the global constraints, the steps and the verification command for each task, **the evidence every review submission must attach**, and the review blocking checklist. That file is a routing table written for the next agent.
