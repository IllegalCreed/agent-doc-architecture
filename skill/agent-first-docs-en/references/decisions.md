# Key decisions: the evidence, and what was rejected

`SKILL.md` lists 10 decisions you cannot skip. This file is where each one comes from. When an agent builds the system itself, **without this evidence it picks the other side.** The evidence is the real history of an enterprise payment-approval system (800+ documents, 3600+ commits). Items marked **baseline observation** are a different kind of evidence: the author ran an internal trial, on two small fixtures (an empty project, and a project with old plans), of an agent building a documentation system without this skill. Each fixture was run once (n=1). The notes were not committed. Treat them as a direction, not as a statistic.

## 1. A stable ID, plus `next-id`

- **Rejected: a date prefix only** (`20260101-fix-login/`). Two changes on the same day, or one change opened on each of two parallel branches, collide or cannot be told apart. An agent also cannot tell the type from the directory name.
- **Rejected: an incrementing serial** (`plan-017`). Parallel branches each take the next number, and the merge collides.
- **What to do:** `<letter>-YYYYMMDD-NNN`. The type letter lets the index and the directories be scanned by type. The date only shrinks the collision window. The real backstop is `next-id`, which scans every local branch, every remote-tracking branch, and every worktree, plus the rule that the later claimant moves on a collision. `next-id` does not fetch. A new remote branch is visible only after `git fetch`.
- **Baseline observation:** an agent without the skill, in an existing project, kept the old `YYYY-MM-DD-slug` and did not look at the other branches.

## 2. A finished change stays where it is

- **Rejected: move it to `archive/` or `done/` when it is finished.** Once a change is cited (a case, a changelog, another change's `Related plans`), moving the directory breaks a batch of links. The agent then edits a pile of unrelated files to repair the links.
- **What to do:** status lives in the metadata (`verified`). The status column of the index is a projection. Only superseded history goes in `docs/plans/archive/` (a reserved directory of doc-lint; directories inside it are not checked as bundles), and it keeps `Replaced by`.
- **Baseline observation:** an agent without the skill, designing the system itself, wrote into the rules "when finished, `git mv` it to `plans/archive/`".

## 3. Do not delete old documents, and do not rewrite them

- **Rejected: rewrite old documents to make the format uniform.** A rewrite drops the decision context of the time. An agent that rewrites also tends to "polish", and makes a conclusion that is no longer true read as if it were true now.
- **What to do:** move the text as-is. Text you move out goes into a migration record (`migration-record`). **Check the facts once before the move and once after.** An as-is move carries errors with it, and not checking after the move is the same as accepting the errors.

## 4. An index only answers "where to read"

- **Rejected: progress, dates, and long explanations in the index.** Progress then has to be updated in two places on every change, and the two copies drift. A multi-line preamble inflates what L0 and L1 have to read.
- **What to do:** six fixed columns, a limit on row width, and no date banners. Status comes from the change's own metadata. `doc-lint` checks that the index matches the metadata.
- **Evidence:** before governance, the source project's main index averaged 394 characters per row, with a longest row of 1128. After governance it was six fixed columns, averaging 157, longest 227. The cause of the growth was "while I am here, add one sentence to the index".

## 5. One template per document kind

- **Rejected: "follow the previous document of this kind".** Each document takes the previous one as its sample, and the error accumulates document by document. That is how the changelog, the test reports, and the release notes drifted version by version in the source project.
- **What to do:** one template per document kind. The header comment declares where it applies and what it must contain or must not contain. That header comment **is** the check rule for that kind of document. `doc-lint` reads it directly. There is no second rule list to maintain.
- The flow for a new document kind: create the template first, then write the document.

## 6. Staleness is "older than the latest release", not an age in days

- **Rejected: fail when `Last reviewed` is older than N days.** Baseline observation: an agent without the skill designed a `last_verified` date field plus a script check. Under the pressure of a check, that kind of field is the easiest to refresh by changing the date and not the content, which manufactures false freshness.
- **What to do:** "current fact" documents (by default: overview, roadmap, handbook specs, testing guides, deployment README) must have `Last reviewed`. Missing it is ERROR. Older than the latest release is only WARN. In release-seal mode (`--release`), only a stale `strict_fresh` document (by default the overview and the roadmap) becomes ERROR. When the repo has no tag, the comparison does not run (`--release` emits an INFO reminder). Checking the content still depends on the write-back loop (see lifecycle).

## 7. Do not pre-write a document that has no content

- **Rejected: generate a "complete documentation system" in one pass** (5 guides, plus an overview, plus an ADR, all created as skeletons first). Baseline observation: an agent without the skill, in an empty project that had only a `notes.md`, committed more than ten such documents in one commit. An empty document provides no fact, but an agent cites it as "a document that exists" and starts inventing into it.
- **What to do:** create only what has content now. When something is missing, create it when there is a fact. The placement rules in a directory README already say where it will go.

## 8. Enforcement is one row in the routing table, plus the release-seal gate

- **The source project's choice (the user decided):** no pre-commit hook and no CI. The two enforcement points are a **routing-table row** ("after changing docs, run doc-lint before committing"), which every agent reads before starting, and **0 ERROR from `--release`** in the release-seal checklist, which is the last gate. **The cost:** a violation can land in the repo first and is caught only at release seal. That is a known tradeoff, not a recommendation. A project that has CI hangs CI on top of these two, and the enforcement is stronger.
- **The checker itself has to be tested.** The rules evolve with the vocabulary and the templates. Without unit tests, one edit quietly lets a class of errors through. The source project at the time had 62 tests and 36 check codes. The version shipped with this skill has 64+ tests and 39 check codes (including `BASELINE-STALE` and the other codes added for onboarding).

## 9. Every entry-file item is a rule, a reason, and a link

- **Rejected: packing worked cases into the entry file.** The source project's entry file went from 128 lines to 406 lines to 457 lines, and the rules were mixed with long narratives of real cases. One release seal both failed to read the full-suite test definition (that definition was already written in the testing spec, but the entry had no sign pointing at it) and forgot to write the release documents.
- **What to do:** each item keeps only "a rule, one sentence of reason, and a link". Several agents' entry files only forward, so two copies do not grow apart.

## 10. Personal memory holds only collaboration preferences

- **Rejected: storing a project lesson in one agent's personal memory.** Other agents, other sessions, and a new colleague all cannot see it. Switching tools is the same as never having written it down.
- **What to do:** a general lesson goes in the repo (the entry file or a spec, visible to everyone through git). Personal memory stores only preferences for how this person collaborates, such as reply language and how approval works.

## A few extra reminders

- A large rearrangement (bulk moves, renames, a migration) is its own commit, so it can be reverted in one step.
- Do not write a person down as "the reader". A person approves, decides, and accepts. The manual and the changelog are deliverables. Their reader is the business side, and they do not enter the agent's route.
- Do not make the index, the roadmap, and the manual all chase the same "current status". Status is written in one place. Everywhere else is a link.
