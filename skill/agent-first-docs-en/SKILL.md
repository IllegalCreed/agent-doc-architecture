---
name: agent-first-docs-en
description: Use when setting up, restructuring, or auditing project documentation that AI coding agents read and write — agents don't know which docs to read, read stale or superseded docs, forget to write results back, or plans, test reports, release notes, and indexes sprawl. Also when adding doc naming and numbering rules, doc templates, a doc linter, or migrating an existing docs tree. English edition. Triggers include document layering, an agent that cannot find the entry point, document indexes, plan numbering, document templates, doc-lint, document governance, and migrating an existing docs tree.
---

# Agent-first documentation

## Core

The first reader **and the main author** of the docs is the agent. The system is a **routing system**: the agent, with the least context, reads what it should read and can trust, and knows where to write. Three questions, and all three are required:

| Question | Mechanism | Detail |
|---|---|---|
| Which documents should it read? | The entry file only routes, plus an "operation → required reading" table | `references/routing.md` |
| Where to look, and which copy to trust? | Duty-based directories, stable IDs, the main index, status and the replacement chain, templates | `references/decisions.md` (why) · `references/rules.md` (vocabulary and format cheat sheet) |
| Where to write, and how does it stay current? | Write-back loop, machine checks, freshness | `references/lifecycle.md` |

A person is the **adjudicator** (approve, decide, accept), not the reader and not the maintainer. The full shared spec, which you can copy into a project as the shared layer: `references/general-model.md`.

## Decide the mode first

| Project state | Mode | What to do |
|---|---|---|
| No docs, or almost none | **Steady state**: build to the rules from day one, no exemptions, baseline at zero | The steps below |
| Plans, reports, and indexes already exist | **Onboarding**: keep the originals, freeze first, then tighten | `references/onboarding.md` |

## Decisions you cannot skip

When an agent builds the system itself, these are the choices it gets wrong most often. Evidence and the rejected alternatives are in `references/decisions.md`:

1. **A change has a stable ID** (`<letter>-YYYYMMDD-NNN`, directory `YYYYMMDD-<letter>NNN-slug`). Take the number with `python3 scripts/doc-lint.py next-id --type <type name>`. A date alone collides when two changes land on the same day.
2. **A finished change stays where it is.** Status lives in the metadata. Do not move a directory in order to "archive" it (that breaks every reference). Only superseded history goes in `docs/plans/archive/`.
3. **Do not delete or rewrite old documents.** Text you move out is stored in a migration record.
4. **An index only answers "where to read".** Fixed columns, limited row width. Status comes from the document's metadata; the index is a projection of it.
5. **One template per document kind.** The template header comment is the check rule. Forbid "copy the structure of the previous document of this kind".
6. **Staleness means "older than the latest release", not an age in days.** An age check pushes the agent to change the date without re-checking the content. Tag before sealing a release, or this comparison does not run.
7. **Do not pre-write a document that has no content.** Do not write a guide for something that does not exist.
8. **Enforcement is one row in the routing table plus the release-seal gate.** Hang it on CI when you have CI. The checker itself has to be tested.
9. **Every entry-file item is a rule, one sentence of reason, and a link.** Other agents' entry files only forward.
10. **Personal memory holds only collaboration preferences.** Project lessons go in the repo. Another agent cannot see your memory.

## Steps (steady state)

Document language: follow this edition's English column names and headings (the index header, the case-table header, and the other labels are English). Write project documents in English. To change the labels, see the top of `references/rules.md`.

1. Copy this skill's `assets/scripts/` to the project's `scripts/`, and `assets/templates/` to `docs/handbook/templates/`.
2. Create `docs/README.md` (split directories by **duty**, not by type or status), `docs/plans/index.md`, and `docs/testing/cases/index.md` (templates `singleton/plans-index.md` and `singleton/cases-index.md`; doc-lint errors if either is missing). Then run `doc-lint.py gen-views`.
3. **Write the project-layer documentation model first:** `docs/handbook/engineering/documentation-model.md`. The `handbook/handbook.md` template is only a skeleton. Write the content from `references/project-model-example.md`: the numbering letters, when to open a change, the write-back loop, the release-seal checklist, "awaiting a person", and "not adopted yet". **Then** write the routing table in the entry file (`AGENTS.md`). See `references/routing.md`. A file a routing row points at must already exist, or `LINK-ENTRY` fails. A spec document must carry `Last reviewed: YYYY-MM-DD`. A spec an agent drafts has `Status: draft`; change it to `approved` only after a person approves it.
4. For any new document: `cp` the matching template, delete the header comment (`sed '1,/^-->/d' template > new-doc`; other `<!-- … -->` comments in the body are fill-in hints — delete them yourself after filling; the tool does not check them; only an unremoved opening header comment reports `TEMPLATE-LEFTOVER`), and fill the sections. Take a number with `python3 scripts/doc-lint.py next-id --type <type>`.
5. When the entry file already exists, **merge it; do not rewrite it.** Keep the existing rules (add the reason and the link) and append the routing table. If the spec a routing row would point at does not exist yet, do not create it; write "none yet".
6. Run `python3 scripts/doc-lint.py` until there are 0 ERROR. Unit tests: `python3 -m unittest discover -s scripts/doclint/tests -t scripts`.
7. Add `__pycache__/` to `.gitignore` (the copied scripts and tests produce it). When copying `assets/scripts`, delete any `__pycache__` already inside it.
8. Put "run doc-lint before committing a docs change" in the routing table, and put "`doc-lint --release` is 0 ERROR" in the release-seal checklist.

Command cheat sheet: `doc-lint.py` (all checks) · `--release` (release-seal mode; a stale overview or roadmap becomes ERROR) · `next-id --type <feature|bugfix|refactor|test-infrastructure|docs|ops|release>` (pass the type name, not the letter) · `gen-views` (regenerate the case views) · `init-baseline` (onboarding mode; see onboarding).

## Red flags — stop

| Thought | Reality |
|---|---|
| "Migrate everything to the new format first, then turn the checks on" | Onboarding freezes first, writes a baseline, then tightens |
| "Putting dates and project paths in the checker is simpler" | Those belong only in the onboarding config. The code stays project-agnostic |
| "Move it to archive once it is done" | A stable path comes first. Status goes in the metadata |
| "If the checker passed, the document is correct" | The checker cannot tell whether the content is actually current. The write-back loop and a person's adjudication cannot be skipped |
| "Tidy the old document before moving it" | Move it as-is so the information stays, and **check the facts once before the move and once after**. An as-is move carries errors with it |
| "It is in personal memory, so it does not belong in the repo" | Other agents cannot read it |
