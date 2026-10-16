# Project-layer documentation model: a minimal example

This is the `docs/handbook/engineering/documentation-model.md` that step 3 of the steady state asks you to write. Below is a skeleton you can edit directly (a fictional small invoicing system). Write only the parts you have **adopted**. List the parts you have not adopted under "Not adopted yet". The full vocabulary is in `rules.md`. The write-back loop and the enforcement gradient are in `lifecycle.md`.

```markdown
# Documentation model (project layer)

> Status: draft
> Last reviewed: 2030-01-02

## AI Quick Path

This document answers: how this project names documents, when to create a change document, and which documents to update after the code changes.
Read "Changes and numbering" and "Write-back loop" first. Before sealing a release, read "Release-seal checklist".

## Changes and numbering

- Change documents live in `docs/plans/<YYYYMMDD-letterNNN-slug>/`. Take a number with `python3 scripts/doc-lint.py next-id --type <type name>`.
- Type letters: feature F, bugfix B, refactor R, test-infrastructure T, docs D, ops O, release C.
- **When to open a change:** it spans several PRs, it affects data, an interface, or a process, or it needs a person's approval. A fix of a change or two goes in the commit message. The default shape is lightweight (requirements plus an implementation record only).

## Write-back loop

| Event | Must update |
|---|---|
| A change starts | Create the bundle and add one row to the main index |
| Implementation is done | Set the status to implemented, register the cases, and update the index "Next step" |
| A release | The changelog, the release-seal test report, and Last reviewed on the overview |

## Release-seal checklist

1. Cut a tag (with no tag, the staleness check does not run).
2. `python3 scripts/doc-lint.py --release` is 0 ERROR.
3. Write the release-seal test report to `docs/reports/tests/releases/YYYYMMDD-<slug>.md`.

## Awaiting a person

- Build and test commands: the repo has no source that can be verified. None yet.
- The deployment notes in `notes.md`: not verified. Do not follow them as a rule.

## Building the documentation system itself

Do not require a change document for this setup. If you create one, follow the threshold above, set the status to `implemented`, and set `Next action` to "awaiting acceptance".

## Not adopted yet

overview, roadmap, releases, inherit_pairs (there is no shared layer), CI. Create them when there is content, or when they are needed.
```

Points:

- `Status` is `draft`. Change it to `approved` after a person approves it. A spec document must have `Last reviewed`.
- "Awaiting a person" registers a fact the agent **cannot verify**. Do not weave it into a rule.
- A row of the routing table (`AGENTS.md`) points at a section of this document, so this document is written **before** the routing table.
