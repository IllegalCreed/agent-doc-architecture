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
| Task closeout, cancellation, supersession, or the end of a migration | Consolidate knowledge, retain necessary evidence, and remove artifacts with no dependencies as described below; record destinations and pending items in the existing implementation or migration record | Status decisions still follow the table; the agent checks uses and dependencies |

Write-back is part of **the same commit**: when the code lands, the matching document is already in its new state.

Note: the tool checks only that a superseded change's `Replaced by` exists and is registered. Whether the new change's `Replaces` points back is left to the write-back. Writing `-` in the index "Next step" is also only a convention.

## Retiring documents and artifacts

**Retirement is complete when knowledge has been carried forward, necessary evidence is traceable, and remaining disposable artifacts have no dependencies. Archiving is not the default destination.** Decide by the content's future use. One file may contain both knowledge to consolidate and evidence to retain:

| Content | Destination | Retirement criteria |
|---|---|---|
| Verified knowledge that will still apply | The matching current spec, guide, or project knowledge | Keep applicability conditions and sources, resolve conflicts with current rules, and confirm the destination has incorporated it. The original is removable only if it has no independent evidence value |
| Records necessary to prove this conclusion | The matching task evidence or historical archive | Enough to review the conclusion and find recovery instructions: executor identity (person / agent and execution role), environment / version, key actions and results, failures and retries, and a recovery entry (commit, backup, or rollback instructions) |
| Temporary files, duplicates, and reproducible artifacts with no consumers | Verify, then remove; no need to archive them all | No current references, task or tool dependencies, or recovery use. For a reproducible artifact, confirm the inputs and generation method remain available |

Before cleanup, search document links, path references, scripts / CI, and delivery entries; also check ongoing tasks and recovery needs. **Finding no links does not by itself prove there are no consumers.** An original failure log from one execution may not be reproducible; a successful rerun cannot replace it.

Protect stable identities and necessary history. Registered bundles, Cases, and required deliverables are not deleted or moved at closeout; maintain status and replacement chains as usual. Archiving means leaving current fact and the default route, without requiring a directory move or a complete process transcript. Record any explicit evidence retention period or review trigger in the matching record, then reassess its use when due.

When a use or dependency is uncertain, hold the artifact and record an owner, the open checks, and a review date or trigger in the existing task record. Reassess when due; do not delete automatically. Use the existing implementation or migration record for the closeout summary too: knowledge destinations, evidence and recovery entries, categories removed, and held items. Do not create a separate cleanup ledger.

`doc-lint` and link checks verify structure and broken links. They cannot decide whether knowledge was incorporated, evidence is sufficient, or external consumers exist; check those individually. After cleanup or a move, run the link check and regenerate and verify derived views when present.

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
- The roadmap has at most 5 banners at the top. Apply the retirement rules to older content: necessary records become evidence; incorporated duplicates can be removed. Do not write live progress into the index or the overview.
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
- **Scattered legacy files** (`notes.md` and the like): keep them until their use is understood. Do not weave content you cannot verify into a new document or the entry file as a rule. Register it as "awaiting a person" in the project-layer document, with an owner and review conditions. Once verified, apply the retirement rules. A `TEMPLATE-NONE` WARN is expected.
- **When to create a change document.** A small team can use a threshold: open a bundle when the work spans several PRs, affects data, an interface, or a process, or needs a person's approval. A fix of a change or two belongs in the commit message. Write the threshold into the project-layer documentation model.
- **Where the release-seal checklist lives.** When there is no separate release-process document, it is a section of the project-layer documentation model, and the routing row points at it. Move it when a process document exists.
- **A person approves status.** The write-back table above is the full process. A small project's shorter path: a change an agent creates after the work is done may be recorded directly as `implemented` (skipping draft / approved), with `Next action` set to "awaiting acceptance" (a terminal change's `Next action` is `-`). Only an explicit instruction from a person advances `approved` and `verified`.

## Deciding "should this be a new document"

1. Is it one deliverable change? → Create a bundle (or the lightweight shape).
2. Is it a long-lived topic across several changes? → A track (navigation only; no plan and no status).
3. Is it evidence of one execution? → `reports/` or another record directory, filename `YYYYMMDD-<slug>.md`.
4. None of those, only "I want to write something" → First ask which routing question it answers. If it answers none, do not create it.
