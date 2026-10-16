# Give Every Document Exactly One Place: Documentation Addressing (3)

*This post is an English translation of the Chinese original: [让每份文档都有唯一的位置——文档寻址设计（三）](../03-addressing.md).*

> This is the third post in the series "Agent-first Documentation Layers for Large Projects." [Post 1](01-agent-is-not-amnesiac.md) treated the doc system as a routing system for agents and left three questions. [Post 2](02-routing.md) answered "which documents should be read," and left placement rules and templates for this post. This post answers the second question: where do I look, and which copy do I trust? The material is still the enterprise payment-approval system. The project has already run one round of documentation cleanup along the lines of this series. The "before / after" numbers in the text were measured by the same script on the two trees.

## 1. After moving 235 files

On September 3 the project reshuffled its documentation architecture and touched 235 files. Before that, test material was scattered in four places, several ways of splitting plans sat side by side under the plan root, and an agent looking for a document was basically guessing the filename. After the reshuffle, test material was gathered into one place. Plans were collected into three kinds: structured change bundles (one change's requirements, design, implementation record, and test cases in a single directory), long-running tracks, and early single-file plans. The top of the docs home said to find a document by its responsibility first, and to stop guessing a location from the filename (see post 2).

The locations existed. The problem was not over.

- **IDs collided.** Two changes were both numbered `F-20260909-005`: two directories, one number. At the time, taking a plan number had no rule and no check.
- **Migrations collided too.** On September 29, two database migration scripts with the same number had both already run in production. The only option was to move them and rework, and only afterward was the rule written: "before taking a number, check every parallel branch and worktree" (a worktree is several working directories checked out from the same repo at once).
- **Package names could not be told apart.** On September 30 an old package with the same name was deployed by mistake. After that, package names were required to carry the hour, minute, and second.
- **More than one account of the same thing.** The README of the change directory declared "we do not maintain a second status table," and then maintained a status list of its own, stopped on September 22.

A directory only answers "which area." For an agent to find a document and trust it, it also has to know which one (the ID), whether it still counts (status and replacement), and which section the information is in (the template). I call the four layers together **addressing**.

## 2. Symptoms and root cause

Addressing failed in this project in five shapes.

1. **Guessing.** Migrations, bundles, and test reports were named "date + English slug." Early single-file plans and incident reports were long Chinese titles. There was no one pattern that could glob the documents of a kind.
2. **The same number.** Two directories, one ID. An agent starting from the ID does not know which directory to enter.
3. **One fact in several places.** Status was written in the bundle header, the index, and the directory README. Beside the case index there were two views kept in sync by hand. Where they disagreed, the agent could only pick one and believe it.
4. **The directory name was read as a status.** Early plans lived under `legacy/`. The literal word is "left over," and it is easily read as "finished and archived."
5. **The section cannot be found inside the document.** Each version of the same kind of report had different sections. Finding "rollback steps" meant reading from the top to the bottom.

There is one root cause: **location, identity, status, and structure — these four pieces of information were either only a convention, or written in more than one place, or expressed by borrowing something else.** A directory name was used to express status. The previous document was used to express structure. A human infers. An agent that follows the literal text does not: the directory is whatever it is called, and this document looks like the previous one.

## 3. Three principles

**Principle 1: split directories by responsibility, not by type and not by status. When the work is done, do not move it.** (Answers "can grep, glob, and run scripts.") A directory answers only "what this document is for." Type and status are both fields. The moment directories are split by status, a finished change has to move house, and every reference to it — other documents, commit messages, comments inside migration scripts — breaks together. Paths stay stable, and the agent can find a document by pattern instead of by memory.

**Principle 2: one fact has one source. Everything else is a derived view.** (Answers "is also the main author.") Two hand-maintained copies will drift. This session edits the bundle header. The next session may not remember to edit the index. So name one source. Every other place either holds only a link, or is generated by a script.

**Principle 3: status is written in the document. It is not expressed by the directory.** (Answers "follows the literal text and does not infer intent.") Status is a field with a fixed vocabulary. Replacement is a field pointing at the new ID. A directory name means only a responsibility.

One more sentence on naming. The reason for a uniform name is that **a machine can match it**, not that it looks tidy (the same answer to "can grep / glob"). `YYYYMMDD-<slug>` can be described by one regular expression. A long Chinese title cannot.

## 4. Mechanism 1: responsibility directories + placement rules

The steady-state directory structure is below (excerpt). "Steady state" means the shape a new project should have on day one. How that differs from onboarding an existing project is mechanism 6.

```text
docs/
├── README.md                    Docs home: split by responsibility + placement rules
├── overview.md                  What the system is, and where its boundary is (current fact)
├── roadmap.md                   The global roadmap
├── handbook/                    Specs that stay in force
│   └── templates/               One template per document kind
├── testing/
│   ├── guides/                  Testing specs
│   └── cases/                   The global case index and its derived views
├── deployment/                  The deployment runbook that can be executed now
├── plans/
│   ├── index.md                 The change index
│   ├── YYYYMMDD-<t>NNN-<slug>/  One bundle per change, flat; stays put when finished
│   └── tracks/<topic>/          Navigation for a long-running track
├── reports/                     Execution evidence: tests, audits, incidents, migrations
└── releases/                    Deliverables: changelogs, handover notes
```

Two choices. `reports/` is L3 evidence, for the agent to drill into. `releases/` is deliverables, for business users and operations. They are separate for that reason. Under `plans/` there is no `done/` or `bugfix/` subdirectory. Type and status are both fields.

Each top-level directory's README has two sections: "Navigation" for the agent that reads, "Placement rules" for the agent that writes. Placement rules look like this:

```markdown
## Placement rules

| Directory | What goes here | Rule for adding |
|---|---|---|
| Bundles under plans/ | One deliverable change | Take a number, then create the directory; type and status go in metadata, not in a physical split |
| tracks/ | A long-running topic that spans many changes | Navigation and links to related bundles only; no plans, no status |
| Not in this directory | Execution evidence, deliverables | Those go to reports/ and releases/ respectively |
```

Placement rules are the route for writing. Before the agent creates a document, it reads the README of the target directory once, and it knows where the document lands and which template to use.

## 5. Mechanism 2: a stable ID scheme

A Stable ID is a document's fixed number. It is taken when the document is created, and it does not change later with the title, the directory, or the type. The ID scheme is the part of this mechanism most worth copying directly:

| Object | ID / filename | Mechanical relation |
|---|---|---|
| Change | `<T>-YYYYMMDD-NNN` ↔ directory `YYYYMMDD-<t>NNN-<slug>` | Each can be derived from the other; the first letter is fixed by the type at creation |
| Database migration | `NNNN-YYYYMMDD-<slug>.sql` | The global sequence decides execution order |
| Test case | `TC-<module>-NNN` | The module can be read off the ID |
| Reports and other records | `YYYYMMDD-<slug>.md` | Sorted by date; a release-seal test report's slug carries the version (`test-report-vX.Y.Z`) and can be grepped by version |
| Release documents | `vX.Y.Z.md` / `vX.Y.Z-delivery.md` | Changelog and handover note come in pairs, by version |
| Release package | `vX.Y.Z-YYYYMMDD-HHMMSS-dist.zip` | Several packages on the same day can be told apart |

An agent holding `D-20261014-001` can glob `20261014-d001-*` without opening the index. Holding a directory name, it can derive the ID the other way. This one was already done well before the cleanup: of the 51 bundles, 35 carried a Stable ID, and directory name matched ID 35/35, with zero misalignment.

The first-letter map has a small trap. The shared layer recommends `V` for `release` (from version). Our project uses `C`, from the early `chore/release` type. An ID, once issued, cannot be changed, so the first-letter map is defined by the project layer and then left alone. The first letter of a new ID is decided by the type at creation, and a later change of type does not change the ID. By the same reasoning, the cleanup found 9 case IDs in the old format. The treatment was to exempt them in the onboarding config, not to rename them. The entire value of a Stable ID is that it does not change.

**The rule for taking a number** is the easiest piece to underestimate. Several agents work in parallel on different branches and different worktrees. Each looks at its own directory and takes "the next number." A collision is almost inevitable. Both collisions in the opening had this shape. The rule is:

- Before taking a number, scan every local branch, every remote branch, and every worktree, and take the first number that is free globally. For bundle IDs, the cleanup turned this step into a number-taking command (see post 4).
- On a collision, **the later claimant moves**: the directory, the ID, and every reference change together, the content does not, and the move-out record states the original number.

A migration collision costs more, because the sequence is the execution order. Adding the hour, minute, and second to a release package is the same idea. An ID has to make "this one" and "that one" impossible to confuse in the eyes of a machine. Two packages on the same day, and a date is not enough.

## 6. Mechanism 3: the bundle, and the lightweight shape

The bundle's four pieces each answer one question:

| File | Answers | When it is written |
|---|---|---|
| requirements | What is wanted | At creation; the header carries the metadata block |
| design | How it is intended to be done | Before approval |
| implementation | How it was actually done, and what departed | Backfilled during implementation |
| test-cases | How it is proved | In step with the implementation |

Define only the four pieces, and reality grows other files on its own. Before the cleanup, bundles contained 7 hand-written case files, 5 impact analyses, 4 handoff documents, more than ten stage booklets, and even `.mjs` scripts. The spec defined none of them. After the cleanup this became an **optional-file allowlist**:

```markdown
| Optional file | When it is needed | When it is read |
|---|---|---|
| impact-map.md | The impact crosses layers or modules and is large | After design |
| handoff.md | Handed to another agent to implement or review | At implementation or review |
| manual-test-cases.md | Some cases must be accepted by a human | At acceptance |
| review-<agent>-YYYYMMDD.md | An independent re-review record | At review |
| stages.md + stage booklets | A large change split into stages | When entering the matching stage |
```

Existing files outside the allowlist stay where they are and are registered as exemptions (14 of them). A new file outside the allowlist is always an error. Scripts go in `scripts/`.

The other end is the small change. Before the cleanup, 20 bundles contained only a requirements file, and 18 completed bundles had no implementation. The spec had never defined what a small change looks like, and the write-back loop broke there. After the cleanup a **lightweight shape** was defined: a small bugfix, a docs change, or a release-type change needs only requirements, and when the status advances to "implemented," the document must contain a section called "implementation record." The shape is distinguished by a condition that can be judged: whether there is a design.

**Short-term and long-term have to be split too.** A bundle is short-term: one deliverable change. A large change with several stages is still one bundle plus a stage split. A track is long-term: topic navigation across several independent changes. It writes only why, the order, the boundary, and links to the related bundles. **It does not hold plans, and it does not write status.** Post 1 noted that our refactoring track had swallowed over a hundred short-term plans and a roadmap with status marks. On top of that, 3 shelved items were not registered in the index, and the IDs in the roadmap did not match the filenames. Writing status inside a track creates a second source of status, which violates principle 2.

## 7. Mechanism 4: a thin index + derived views

The index answers only "where to read." It does not answer "what it is." After the cleanup the header is fixed at six columns:

```markdown
| Stable ID | Type | Title | Status | Next step | Plan |
|---|---|---|---|---|---|
```

A few hard rules go with it. The title is at most 50 characters. The next step is at most 80. A terminal state's next step is `-`. The Plan column holds only the link to the bundle entry. Date banners (progress announcements that start with a date) are not allowed in the index. Version news goes on the roadmap. Progress goes in the bundle.

More important is source versus projection: **the metadata block in the bundle header is the single source of truth for status, and the index is its projection.** A disagreement is an error from the checker. That is where principle 2 lands. The README list from the opening, stopped on September 22, has no place to stand under this rule.

Unregistered is the same. Before the cleanup, one bundle was not in the index. For an agent that enters through the index, it did not exist. Now an unregistered bundle is an error outright.

The case index works the same way. The main table is the only source. The two views, by layer and by module, are generated by a script from the main table and may not be edited by hand. Before the cleanup, narrative written batch by batch was piled on top of the main table, and many IDs in the narrative were not in the main table. Each of the two views also had a batch of IDs the main table did not have. An agent coming in through different doors saw a different "all the cases." After the cleanup, IDs in the narrative moved back to the change they belonged to, and the views became generated (the numbers are in section 11). When a human wants progress, the agent summarizes it on the spot, or runs a script to generate a view.

## 8. Mechanism 5: the state machine, the replacement chain, and archive

Every value in the status vocabulary has to correspond to a way the agent uses it. Writing the "meaning" is not enough. The agent needs to know what to do after it reads the status:

| Status | Meaning | How the agent uses it |
|---|---|---|
| draft | Under discussion | Background only; not a basis for implementation |
| approved | Approved, not implemented | May be a basis for implementation |
| in-progress | Being implemented | Backfill while implementing |
| implemented | Code has landed; verification is incomplete | Read the implementation record and the test record |
| verified | Implementation and verification are both confirmed | May be treated as current fact |
| superseded | Taken over by a new change | Must jump to `Replaced by` |
| deprecated | No longer represents current behavior | For tracing only |
| obsolete | No longer in force | Not a basis for implementation |
| cancelled | Decided not to do | Not a basis for implementation; read the reason it was cancelled |

Before the cleanup, the index contained `completed`, `done`, `in_progress`, and free-form Chinese. In the type column, bug and fix were mixed, and there were combinations such as `feature/fix`. If the vocabulary allows near-synonyms, the agent is invited to infer whether `done` is `verified`. During the cleanup the old spellings were mapped onto the vocabulary by a one-shot migration script. The mapping table is recorded only in the project layer. It does not enter the shared layer or the checker.

The **replacement chain** is a pair of fields. The old document writes `Replaced by: <new ID>`. The new document writes `Replaces: <old ID>`. An agent that reads superseded must jump. It may not keep looking for the answer in the old document. Post 1 gave the reason this rule spun in place: the field was not there. After the cleanup every bundle writes `Replaced by`, and if there is none it writes `none`. An explicit "none" is information too.

Last is **archive**, the word most easily misused. Archive means only **history that has been superseded**, for example an old manual replaced by a new deployment runbook: move it out of the current directory, and leave a link to the new document in the old place. **A finished change is not archived.** It stays where it is, and the status is written in the metadata. The reason goes back to principle 1. A finished change is exactly what is referenced the most. Moving it breaks every reference.

## 9. Mechanism 6: steady-state rules versus onboarding an existing tree

The easiest mistake, when abstracting a shared spec out of one project, is to treat that project's history as shared structure. In the shared part of the source project's documentation-model spec, the "recommended target structure" drew `legacy/YYYYMM/`. Review pointed out, one after another, that both `legacy/` and `changes/` are products of onboarding. Exceptions that draw a line by date are more hidden. They were scattered through the rule text and through the checker code. Another example inside the checker code is in post 4.

So a spec has to be written for two situations.

**Steady state.** A new project files documents by the rules from day one. There is no frozen area, no date exception, and the exemption baseline is zero. Under `plans/` there is only the index, bundles laid out flat, and `tracks/`. Bundles are distinguished from `tracks/` by the name pattern `YYYYMMDD-<t>NNN-`. They do not need another wrapping directory called `changes/`. In our project that extra layer existed only to separate bundles from the frozen area. And "change," read literally, means "a modification." The first feature of a new project does not modify anything, and an agent that follows the literal text will be misled by the name.

**Onboarding an existing tree.** An old project that adopts the rules midway needs four onboarding pieces, and **all of them live in one onboarding config.** The rule text and the checker code contain no date constant and no historical path:

| Onboarding piece | What it does | When it exits |
|---|---|---|
| Frozen area | Old-format documents from before onboarding; read-only, nothing new | When touched, migrate to a standard bundle and mark the replacement |
| Rule effective date | Objects filed before this date are exempt from the rule (for example, the ID's first letter) | Permanent; applies only to what already existed |
| Exemption baseline | The list and the count of existing violations | May only fall, never rise; delete it when it reaches zero |
| Historical directory layer | A directory layer that is heavily referenced, where renaming costs too much | Migrate with a major version, or keep it permanently |

Our project's `changes/` is the fourth piece. It is referenced from 73 files in 564 places, and the comments in 13 migration scripts that have already been executed cannot be changed, so it stays. The onboarding config declares where the bundle root is. The skeleton of that config:

```json
{
  "bundle_root": "docs/plans/changes",
  "rules_effective_since": "20261014",
  "frozen_dirs": ["<frozen directory>"],
  "template_exceptions": ["<existing path that did not match a template before onboarding>"],
  "naming_exceptions": ["<existing path that did not match the naming rule before onboarding>"]
}
```

A new project has no such file, and the checker runs a full check with zero exemptions.

The name of the frozen area needs extra care. A frozen area means **old format**. It does not mean **finished**. Work that still has to move forward must be registered in the index. The word `legacy` naturally pulls a person toward "finished and archived." Under our `legacy/202504/` there was only one file, and the filename ended in "do this later" — a piece of work that was explicitly unfinished, lying in a directory that looked archived. A human sees the mismatch at a glance. An agent that follows the literal text treats it as done.

## 10. Mechanism 7: the template is addressing inside the document

Directories and IDs answer "where the document is." The template answers "which section the information is in." Section names are fixed, so the agent can jump straight to "rollback and acceptance boundary" and does not have to read the whole document.

What happens with no template is on record, in full, as a counterexample. Post 2 noted that the release-seal spec, at the time the rule was written, said of the handover note "the template is to follow v2.0.2-delivery.md." Naming a historical document as the sample writes imitation into the rules. From v2.0.3 on, the handover notes were missing SHA-256. The drift went much further than that one spot. The rollback section was missing for 8 versions in a row, from v2.0.1 through v2.2.0, and came back only in v2.2.1. From v2.0.3 on, the changelog lost the two sections "tests in this version" and "build traceability." The section counts of the release-seal test reports ran 6 → 3 → 5 → 5 → 5 → 4 → 8 → 6 → 6 → 6. There were 5 incident reports, 13 audit reports, and 10 migration handovers, and almost every one invented its own structure. The only section that stayed stable was "delivery result" in the handover note: 14 of 14 had it. I call this **imitation drift**. Each generation is only "write it like the previous one," and the deviation is passed on generation after generation.

The rules of a template:

- **One template per document kind**, all of them in the same template directory. The directory README registers them in one table: kind | template | applies to | write / read.
- The template's header comment declares the **paths it applies to** and the **fields it must contain**. The template's H2 headings are the required sections, in a fixed order.
- **The template is the lint rule.** The checker reads the template directly. It does not keep a separate rule list.
- A new document is created by copying the template and deleting the header comment, then filling it in. **Copying the previous document of the same kind is forbidden.**

The handover-note template (excerpt, redacted):

```markdown
<!-- template
applies-to: docs/releases/v*-delivery.md
must-contain: SHA-256；回滚；tag
-->
# vX.Y.Z artifact handover note

## Delivery result
## Artifacts and verification
## Release scope
## Deploy order and smoke
## Rollback and acceptance boundary
## Record
```

The first two tokens inside `must-contain` — `SHA-256`, and `回滚` (rollback) — are exactly the things imitation drift had dropped. The rule lives in the template. Change the template, and the check changes with it. There is no "the spec says one thing and the check looks for another."

After the cleanup, the documentation-model spec was split out of a 1,123-line mixture (about 460 lines of it were templates) into a 252-line project layer, a separate shared layer, and 31 templates. The templates cover 338 applicable documents in the repo. None is unowned, and none is owned by two templates.

## 11. Before and after the cleanup

How it was measured: "before" is the start of the cleanup branch (October 14), and "after" is the state once the cleanup had been merged (October 15). The two trees were measured item by item with the same statistics script, and the measurement can be repeated. The table below keeps only the rows that bear on addressing. Checker violations, the entry file, and broken links are in post 4.

| Metric | Before | After |
|---|---|---|
| Plan-index columns / rows | 8 columns / 56 rows, 4 rows with the wrong column count | 6 columns / 62 rows, 0 misaligned rows |
| Index row width (characters), average / max | 394 / 1128 | 157 / 227 |
| Distinct status spellings | 9 (including `done` inside a misaligned row) | 6 actually used (vocabulary of 9) |
| Distinct type spellings | 13 | 6 |
| Duplicate Stable IDs | 1 | 0 |
| Bundles not registered in the index | 1 (51 in total) | 0 (53 in total) |
| Bundles with no Stable ID / no `Replaced by` | 16 / 35 | 0 / 0 |
| Metadata formats | 3 coexisting | 1 |
| Case index | 457 lines; main table has 86 IDs; the narrative has another 83 IDs not in the main table | 169 lines; the main table's 86 IDs unchanged; narrative IDs: 0 |
| Derived case views | By layer, 204 lines (25 IDs not in the main table); by module, 248 lines (18 IDs) | 123 lines / 148 lines, 0 such IDs, generated by script |
| Document templates | 0 | 31 |

A thinner index is not deleted information. The row count did not shrink. What got narrower is each row, and the progress narrative went back to the bundle. Of the checker's ERRORs before the cleanup (how they were measured, and how many, is in post 4), the top four were all addressing problems: case narrative mixed in ahead of the main table, 102; type not in the vocabulary, 39; bundle missing metadata, 35; status not in the vocabulary, 28.

## 12. Where each document goes, what it is called, and which copy to trust

| Document | Where | Name / ID | Source of truth | Derived view | Template | Human's role |
|---|---|---|---|---|---|---|
| Requirements / design | The bundle under `plans/` | `<T>-YYYYMMDD-NNN` ↔ directory | The bundle metadata block | One row of the index | One each for requirements and design | Approve the plan, and make the call on scope |
| Implementation record | The same bundle (in the lightweight shape, an "implementation record" section inside requirements) | Follows the bundle | This document | — | Implementation record | Confirm the departure is acceptable |
| Long-running track | `plans/tracks/<topic>/` | Topic name | Metadata of the related bundles | — | Track README | Make the call on track priority and on closing it |
| Test case | The global case index + the bundle's test-cases | `TC-<module>-NNN` | The index's main table | By layer / by module (generated) | Case index, case | At acceptance, confirm a coverage gap is acceptable |
| Database migration | The migration directory | `NNNN-YYYYMMDD-<slug>.sql` | The script itself; the sequence sets the order | — | — (not a document) | Before deploy, confirm the execution list |
| Release-seal test report (L3) | `reports/` | `YYYYMMDD-test-report-vX.Y.Z.md` | The report itself | — | Release-seal test report | Accept the release seal: release on the evidence |
| Incident report (L3) | `reports/`, by month | `YYYYMMDD-<slug>.md` | The report itself | — | Incident report | Confirm the root cause, and decide whether to codify a rule |
| Spec (L1) | `handbook/`, `testing/guides/` | A fixed filename; shared layer and project layer in pairs | This document | — | Spec document | Make the call when a rule is codified |
| Deployment runbook | `deployment/` | By environment / topic | This document | — | Deployment runbook | Approve production |
| Changelog / handover note (deliverables) | `releases/` | `vX.Y.Z.md` / `vX.Y.Z-delivery.md` | This document | — | One each | Confirm the deliverable |
| User manual (deliverable) | The docs root | A fixed filename | This document | — | User manual | Spot-check, then confirm the deliverable |

Most cells of "derived view" are "—". Build one only when there really are several ways to read the same source, and once it exists a script generates it. Deliverables do not enter the routing system, and they still have templates, because they drift under imitation too. Every cell of "human's role" is approve, make the call, accept, or confirm. The human does not need to know where a document lives or what it is called. Addressing is for the agent.

## 13. How addressing breaks

### Failure 1: exemptions make the template govern mostly new documents

Most existing documents were written before onboarding and do not match a template, so they can only go into the exemption list. After the templates go live, what they govern is mostly new documents. Existing ones wait until they are touched, and are migrated then. Naming exemptions work the same way. 40 existing filenames do not match the rule. By principle 1 they are not moved unless someone migrates them, and a pattern glob keeps missing them. The exemption list was supposed to only fall, never rise. What makes "only fall, never rise" real is in post 4.

The counter: when a frozen area or an exempted file is touched, migrate it to the standard shape in passing, so the list actually moves down.

### Failure 2: work that was already open before the rules landed hits the new rules only at merge

The changelog and handover note for v2.3.2 were committed to the main development branch on the morning of October 15. About 30 minutes later, the cleanup was merged in. When they were written, the main development branch had no doc-lint and no templates. The only "previous one" available to copy was the old format: registration reused the old eight-column index, and the sections did not follow a template. The check reported it at merge time, and it passed only after the sections were filled in against the template. This is not someone breaking a rule. It is work that was already open before the rules landed, hitting the new rules only at merge.

The counter: during the cleanup, "a new document starts by copying the template; do not imitate the previous one" was written into that row of the routing table, and into the AI Quick Path at the top of the documentation-model spec. A branch opened before the rule landed cannot read it. Re-running the check at merge is the last gate, and this one was stopped there.

### Failure 3: a template that is too strict forces the agent to fill in empty phrases

If every section is required, the agent will stuff boilerplate into it to pass the check, and boilerplate looks the same as real content. The adjudicator cannot tell them apart. The counter is to press the required sections down to the minimum. Mark the rest "(optional)," and delete them if they are unused. If there is nothing to say, write "none," which is more honest than a paragraph of boilerplate. Sections outside the template are allowed. A template specifies **where to look**, not **how much to write**.

### Failure 4: judging the scope of application by the content

The template check originally decided whether a document was a generated view, and whether to skip it, by looking for phrases in the body. The result was that a design document which mentioned the generate command was skipped entirely. It was found only when the check was run on the cleanup plan's own document. Scope of application is an addressing problem, so it should be judged by path. The applicable path in the template's header comment is more reliable than any feature of the body. How the tool itself is tested is left to post 4.

## 14. Summary

1. Addressing has four layers. The directory answers which area. The ID answers which one. Status and the replacement chain answer whether it still counts. The template answers which section the information is in. Drop a layer, and the agent has to guess.
2. Three principles. Split directories by responsibility, and do not move finished work (can grep / glob). One fact, one source; the rest are derived views (is also the main author). Status is written in the document, not expressed by the directory (follows the literal text).
3. IDs have to be mechanically derivable in both directions. Taking a number scans every parallel branch and worktree. On a collision the later claimant moves, and records the original number. An ID that has already been issued is exempted rather than renamed.
4. Steady-state rules and onboarding an existing tree are written apart. A new project has zero exemptions and no frozen area. An old project's frozen area, effective date, exemption baseline, and historical directory layer all go into one onboarding config. Names are read literally. `legacy` and `changes` both are.
5. The template is addressing inside the document, and it is the check rule itself. Without a template, the agent only imitates the previous document. It breaks when exemptions make the template govern mostly new documents, when work opened before the rules landed hits them only at merge, when a template that is too strict forces empty phrases, and when scope is judged by content instead of by path.

### Series

1. [Agents Aren't Amnesiac — They Can't Find the Entry Point: Documentation Layers for Large Projects (1)](01-agent-is-not-amnesiac.md)
2. [Make the Agent Read Only What It Should: Documentation Routing (2)](02-routing.md)
3. Give Every Document Exactly One Place: Documentation Addressing (3) (this post)
4. [Keep Documents from Rotting: The Document Lifecycle in the Agent Era (4)](04-lifecycle.md)
