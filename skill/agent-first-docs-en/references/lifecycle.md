# Lifecycle: keep documents from rotting

Every session an agent starts is a new one. The moment one document falls behind the code, the next session treats it as fact. Documents rot for almost the same reasons: **nobody required the write-back, nobody checked the write-back, and nobody tested the check itself.**

## The write-back loop

Each kind of event has a document that must be updated. Put this table in the spec, and point the routing table at it:

| Event | Must update | Who adjudicates |
|---|---|---|
| A change starts | Create the bundle (`next-id` → requirements), add one row to the main index, status `draft` | A person approves, then change it to `approved` |
| During implementation | Status `in-progress`; the implementation record in `implementation.md`; metadata (`Progress` / `Next action`) | — |
| Implementation is done | Status `implemented`; register cases in `test-cases.md`; the index status and the next step | — |
| Verification passes | Status `verified`; the index "Next step" is `-` | A person accepts |
| Taken over by a newer change | The old change is `superseded` plus `Replaced by`; the new change has `Replaces`; **status and next step on both rows of the main index** (the old row writes `-`); the old directory stays in place | A person confirms |
| Implementation and the document disagree | Prefer fixing the document so it matches the facts. If the code is wrong, open a bugfix change and record it | A person decides which side is wrong |
| A release | Changelog, delivery note, `Last reviewed` on the overview and the roadmap, the release-seal test report | A person signs it off |
| An incident | An incident record (reproduction, root cause, fix, regression case). A hole in the spec is patched into the spec, and a routing row is added | A person reviews it |

Write-back is part of **the same commit**: when the code lands, the matching document is already in its new state.

Note: the tool checks only that a superseded change's `Replaced by` exists and is registered. Whether the new change's `Replaces` points back is left to the write-back. Writing `-` in the index "Next step" is also only a convention.

## A gradient of enforcement

From weak to strong. Pick the strongest level you can actually do. Do not stop at "a reminder":

1. **Write it in the spec.** The agent may never read it.
2. **Add one row to the entry-file routing table.** Every agent reads it before starting. Lowest cost, widest coverage.
3. **The template header comment.** Put the rule in the file that creating a document necessarily copies.
4. **`doc-lint`.** Machine-checks structure, metadata, numbering, index consistency, links, and template sections.
5. **The release-seal gate.** "`doc-lint --release` is 0 ERROR" goes in the release-seal checklist. A stale overview or roadmap becomes ERROR here.
6. **CI.** Hang it on CI when you have CI. Not having CI is not a reason to skip 1–5.

The checker is code. The vocabulary, the template headers, and the baseline all change, so it must have unit tests (this skill's `assets/scripts/doclint/tests/`).

## Freshness

- The `Last reviewed` metadata is the date the content was **last checked**, not the date it was last edited.
- "Current fact" documents (the default `fresh_docs`: overview, roadmap, handbook, testing guides, deployment README) must have it. Missing it is ERROR. Older than the latest release is WARN. Under `--release`, only `strict_fresh` (overview, roadmap) becomes ERROR. **Do not fail on an age in days.**
- When the repo has no tag, the comparison does not run. `--release` emits `FRESH-NOTAG` as INFO: the first step of the release-seal checklist is to cut a tag.
- The roadmap has at most 5 banners at the top. Archive the older ones past that. Do not write live progress into the index or the overview.
- Agreement between documents and code comes from the write-back loop plus a person's acceptance. `doc-lint` can check structure. **It cannot check whether the content is actually current.**

## Links and references

- A stable path is the precondition (decision 2). Otherwise a link breaks when the status changes.
- `check-doc-links` only checks that a relative path points at a file that exists. **It does not check `#anchors`.** `mask_fences` / `mask_code` keep example links inside code blocks from being reported.
- After a migration or a move, run the link check. Do not fix links by hand in bulk: in a one-shot migration script, `import doclint.linkfix` and recompute relative links with `rebase_links`.
- When a document mentions a fact, link the document that holds the fact. Do not restate it. A restatement is a second copy that will go stale.

## Memory layers

| Layer | What goes there | Where |
|---|---|---|
| Repo | Project lessons, specs, decisions, pitfalls | Entry file / handbook / change documents (visible to everyone through git) |
| Personal memory | Collaboration preferences: reply language, how approval works, taste in output | The agent's memory directory |
| Session | The current task's context | Not persisted |

When a personal memory turns out to be a project-wide lesson, move it into the repo and delete the memory.

## Where a person adjudicates (only these)

Approve `draft → approved`. Accept `implemented → verified`. Confirm `superseded` / `cancelled`. Decide which side is wrong when the implementation and the document disagree. Sign off a release. Review an incident. **Everything else is drafted, maintained, and written back by the agent. A person is not the maintainer of the documents.**

## Common situations

- **Do not copy the whole shared layer.** `references/general-model.md` is long and assumes a complete system (by-layer, roadmap, operation-manual, and the rest). For a small project, the project-layer documentation model stands on its own, records only the parts you have adopted, and lists the sections that do not apply yet under "exceptions / not adopted yet". Copy the shared layer only when you need an inheritance pair.
- **Scattered legacy files** (`notes.md` and the like): do not delete them and do not rewrite them. Do not weave content you cannot verify into a new document, and do not write it into the entry file as a rule. Register it as "awaiting a person" in the project-layer document. A `TEMPLATE-NONE` WARN is expected.
- **When to create a change document.** A small team can use a threshold: open a bundle when the work spans several PRs, affects data, an interface, or a process, or needs a person's approval. A fix of a change or two belongs in the commit message. Write the threshold into the project-layer documentation model.
- **Where the release-seal checklist lives.** When there is no separate release-process document, it is a section of the project-layer documentation model, and the routing row points at it. Move it when a process document exists.
- **A person approves status.** The write-back table above is the full process. A small project's shorter path: a change an agent creates after the work is done may be recorded directly as `implemented` (skipping draft / approved), with `Next action` set to "awaiting acceptance" (a terminal change's `Next action` is `-`). Only an explicit instruction from a person advances `approved` and `verified`.

## Deciding "should this be a new document"

1. Is it one deliverable change? → Create a bundle (or the lightweight shape).
2. Is it a long-lived topic across several changes? → A track (navigation only; no plan and no status).
3. Is it evidence of one execution? → `reports/` or another record directory, filename `YYYYMMDD-<slug>.md`.
4. None of those, only "I want to write something" → First ask which routing question it answers. If it answers none, do not create it.
