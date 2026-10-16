# Keep Documents from Rotting: The Document Lifecycle in the Agent Era (4)

*This post is an English translation of the Chinese original: [让文档不烂——Agent 时代的文档生命周期（四）](../04-lifecycle.md).*

> This is the last post in the series "Agent-first Documentation Layers for Large Projects." The first three answered which document to read, where to look, and which copy to trust. This post answers: once a document is written, how does it not rot? The material comes from an enterprise payment-approval system, and from one documentation cleanup done on it.

## 1. The rules were all there. The docs rotted anyway.

[Post 1](01-agent-is-not-amnesiac.md) closed with a judgment: the agent that writes the docs is amnesiac too. The evidence comes from a documentation health check on October 14. The problems it found have one thing in common: **the rule had been written long before, and the document that violated it was lying next to the rule.**

- The documentation-model spec defined 8 statuses. The plan index actually had 9 spellings. `completed`, `done`, and free-form Chinese were all in there.
- The spec says the index "enforces only six columns." It actually had 8. Another 4 rows had the wrong column count, and nobody had noticed.
- The two same-numbered bundles from the opening of post 3 (`F-20260909-005`): the later claimant wrote a line in its header, "⚠️ same number, left on record." Someone had noticed, left a note, and did not fix it.
- The repo had a link-checking script, and it was attached to no execution point. Broken links at the entry layer were 0. Deeper broken links numbered in the five hundreds. On an ordinary day, nobody could see that number.

A fair share of these documents came from an agent's hand. Post 1 counted it: nearly four in ten of the commits that touched docs carried an agent attribution, and that is only a lower bound. At the moment of writing, the agent most likely obeyed the rule it had read. It does not remember a convention another session settled, and it does not go back to check whether the whole system is consistent with itself.

Group the symptoms and there are three ways docs rot. **The work is done and nothing is written back**: the implementation record is missing, and the next agent can read only the plan. **The convention depends on good intentions**: vocabulary, column count, and IDs are written only in the spec, and nothing checks them at commit time. **Old facts do not leave the stage**: date banners, a stale overview, and old conclusions in personal memory stay hanging. The root cause is the same. When a document is written, where it is written, who checks it, and when it leaves the stage were only hoped for. They were never designed.

The "same number, left on record" line makes the point best: **without machine enforcement, noticing is not fixing.** The cheapest move is to leave a sentence. Once the sentence is there, the problem becomes a "known situation," and it never gets fixed.

## 2. Three principles

**Principle 1: write-back is part of the change.** (Answers "no memory across sessions.") The definition of done includes writing the docs back: the implementation record, the status in the index, the cases, the spec, the manual. If what should have been written was not written, the change is not done. How it was actually done, and where it departed from the plan, exists only in the session that did the work. When the session ends, that is gone.

**Principle 2: a machine enforces the convention. The human only adjudicates.** (Answers "is also the main author" and "can grep, glob, and run scripts.") The session that writes the spec and the session that violates it may be the same agent twice. A convention that depends on good intentions will drift. Whenever a convention is parseable — vocabulary, IDs, metadata fields, table headers — hand it to a checker. The human shows up only where a machine cannot judge: is the definition right, is this exception granted, does this problem get fixed.

**Principle 3: zero tolerance at the entry layer. Deeper layers have a baseline that may only fall, never rise.** (Answers "no memory across sessions" and "follows the literal text and does not infer intent.") Every session enters through the entry, so one error in the entry is executed literally by every session. It has to be 0. Deeper documents are a large existing stock. Demanding they be cleared to zero at once means stopping all work to sweep. The practice is to record today's number as a baseline. A new problem may not push the number above the baseline. Fix one, and the baseline drops by one.

## 3. Mechanism 1: the write-back loop

Principle 1 lands as a table of "change type → what must be written back before it is done → who checks." The source is the write-back rules scattered across several of our specs. The full version, expanded by document type, is in section 10. The two rows below are the ones that table does not include:

| Change type | Must be written back before done | Who checks |
|---|---|---|
| Any registered change | The implementation record; the status in the metadata and in the index | doc-lint |
| A new business flow | A mobile-adaptation assessment | One row of the routing table + code review |

**The "who checks" column cannot be empty.** The write-back rule existed on March 4: after development, backfill the plan's "actual execution record," and update the roadmap at the same time. Execution was entirely a matter of good intentions. Post 1 counted it: a batch of completed bundles had no implementation record.

**Lower the bar, and write-back actually happens.** Requiring the four-piece bundle for a small defect usually ends as one requirements file, with write-back skipped entirely. The lightweight shape defined in post 3 needs only a requirements document, but when the status enters "implemented," the document must gain a section called "implementation record."

**Deliverables are inside the loop, and outside the route.** The user manual, the changelog, and the handover note are for business users and operations. The agent maintains them and does not learn the job from them. The routing table records only "after which change this must be updated." The user manual in post 1, eight days late, is the cost of that row being absent.

## 4. Mechanism 2: from an incident to a check

After every accident, a rule walks a pipeline: **incident → codified rule → check.** The problem is that it often stops halfway.

I rank the force of a rule as a ladder, weak to strong:

1. **Narrative.** Write the accident as a story. Only a session that happens to read it is affected.
2. **An L0 one-sentence rule.** Written into the entry file, with one sentence of reason and a link. Every session reads it. Whether it is obeyed is up to the agent.
3. **L1 detail.** Spell out how to do it, and what counts as a violation. The rule goes from "known" to "executable and decidable."
4. **A code-review check.** A violation is stopped, before merge, by the reviewer against a list. The reviewer is often another agent. The "Code review" items in the entry file sit at this rung.
5. **A shared helper or an automatic check.** The wrong way cannot be written, or it goes red as soon as it runs. It no longer depends on anyone remembering.

The further up, the less it depends on "being read and being remembered." Two examples. One climbed to the fifth rung. One stopped halfway.

**Climbed to the fifth rung: the download endpoint's magic header.** Tests of the download endpoint used to check only the filename suffix. A JSON 500 from the backend was still judged green. A rule was then codified: a download must verify the magic header at the start of the file (the fixed bytes that identify the format), and it was made a shared helper. A new test calls the helper and the check happens. The correct way became the cheapest way. The helper is not the only way out. A hand-written check is allowed too, as long as it compares the magic-header bytes, and that part is still backed by the review list.

**Stopped halfway: taking a migration number.** After the migration collision in the opening of post 3, the rule "before taking a number, check every parallel branch and worktree" is still a manual rule today. The other half of the same kind of problem did climb to the fifth rung. The plan-bundle collision on `f005` was changed, during the cleanup, so that taking a number uses only doc-lint's number command, and a duplicate ID is an error from the check directly.

The pipeline asks one question of every rule: **can it climb one more rung?** A rule that stays on a low rung is not necessarily wrong. Some judgments a machine cannot make. But it has to be clear that the rule depends on good intentions. I recommend that the L1 detail note which rung each rule is on.

## 5. Mechanism 3: doc-lint, the test suite for docs

doc-lint is the core product of this cleanup: a script that checks documents, which is what post 1 called "the test suite for docs." It has 36 check codes, and it carries 62 unit tests of its own. What it checks falls into a few groups:

- **IDs and registration.** Stable IDs are unique. A bundle's directory name corresponds mechanically to its ID. Every bundle is registered in the index; otherwise, for an agent that enters through the index, it does not exist.
- **Vocabulary and metadata.** Status and type may take only values from the vocabulary. A bundle's metadata block must be complete, and `Replaced by` is a required key. The problem post 2 left lands here: the field may be filled with `none`, but it may not be omitted, or the rule "if you read a superseded document, jump first" spins in place. The tool checks only that the key is present. It does not check that a superseded document really filled in the new ID, and that half still depends on review. (The skill shipped with this series has since added the check: a `superseded` document's `Replaced by` must be an ID already registered in the index.) The status in the metadata and the status in the index must agree. The metadata is the single source of truth.
- **Index shape.** The header is fixed at six columns, and every row has the same column count. Title and "next step" have length limits. Date banners are forbidden.
- **Write-back.** An implemented bundle must have an implementation record. In the lightweight shape, that is an "implementation record" section (mechanism 1).
- **Cases.** The main table's header, and the Case ID format. Case narrative may not be mixed in ahead of the main table. The two derived views, by layer and by module, must match what the script generates.
- **Links.** One broken link at the entry layer is an error. Broken links across the repo may not exceed the baseline (principle 3).
- **The rest.** A project-layer spec must declare which shared spec it inherits. A current-fact document must carry a review date (mechanism 5). A new filename in a record directory must be glob-matchable. A document must contain the required sections of its template (templates are the subject of post 3).

The output is one problem per line, with the check code, the file, and the reason. An agent can read it and fix it. The tool also does two jobs of "make the correct way the cheapest way":

```bash
python3 scripts/doc-lint.py
python3 scripts/doc-lint.py next-id --type <type>
python3 scripts/doc-lint.py gen-views
```

In order: run every check; return the next free ID, so taking a number no longer depends on the agent counting directories itself; regenerate the derived views from the case main table. The views may not be edited by hand, and a disagreement with the main table is an error.

### Steady-state rules and the onboarding config

The checker code contains not one date constant, and not one historical path. The special cases of an existing project are gathered in one onboarding config:

- The exemption list: existing documents that do not match a template or the naming rule, existing files inside a bundle that are outside the allowlist, and old-format Case IDs.
- 3 frozen directories; old-format documents are read-only.
- A repo-wide broken-link baseline of 521.
- The rule effective date, and the bundle root.

A new project has no such file: no frozen area, no effective date, and a baseline of zero. That is post 3's "steady-state rules versus onboarding an existing tree," landing on the tool. Not one line of project history may enter the checker code. That boundary was held in review. See section 8.

### The enforcement point: not a hook, and not CI

Post 1 said that "is also the main author" implies machine enforcement. The general shape is a git hook (a script that runs automatically before a commit, such as a pre-commit hook) or a CI gate (a pipeline that runs the check automatically before merge). Our project has explicitly decided to do neither. There are only two enforcement points.

**The first is one row of the routing table.** A row was added to the entry file's "operation → required reading" table (excerpt, redacted; the original table really is two columns like this, which is exactly the shape post 2 criticizes):

```markdown
| Create or edit any document under docs/ | The documentation-model spec. A new document starts by copying the matching template; imitating the previous document of the same kind is forbidden. Before committing, doc-lint must report 0 ERRORs. A new change takes its number only from next-id. After editing the case main table, run gen-views. |
```

**The second is the release-seal gate.** The release-seal checklist gains a step: doc-lint in release-seal mode reports 0 ERRORs. If it does not pass, do not continue.

Why does this still count as machine enforcement? I have three reasons.

First, the routing table is the one place the agent is certain to read. "If you changed docs, run doc-lint" is resident for every session that edits a document. The script makes the judgment. The agent is only responsible for running it.

Second, the release seal is a point every version passes through. The checklist is executed by the agent and accepted by a human. A violation that was skipped in ordinary work is stopped here at the latest, and what the human sees is one line, "0 ERROR."

Third, when a hook stops an agent, the cheapest way out is often to step around it, not to fix the document. Put the check inside the agent's own workflow, and the output tells it directly which line is wrong. Fixing is cheaper than stepping around.

The cost should be stated too. Without a hook, whether doc-lint was run depends on the agent reading that row and following it. Between two release seals, a violation can enter the repo first, and it is stopped at the next release seal at the latest. If a project allows CI, I would hang the same command on it. The check logic does not change. There is only one more execution point.

## 6. Mechanism 4: layers of memory

Post 2 gave the test: if the agent changes, or the machine changes, should this still be in force? If yes, it goes into the repo. The cleanup carried that out once, and two new problems showed up.

**Before migrating, check whether it is still true.** Personal memory held one line: "OCR (optical character recognition of images) has no server, and is deliberately not integrated." During the migration, the code and the roadmap were checked, and the production environment had long since integrated GPU OCR. The memory was long stale, and it had kept loading with every session as a "fact." It was not migrated. It was deleted. The migration procedure gained a step, "first check whether it is still true." Following that step, of the 21 memories moved into the repo, 4 were partly stale, and only the part that was still true was moved. Personal memory has no review date and no checker. Once it is stale, it is hard to notice.

**A verbatim move moves the error along with the rule.** The old entry file said "dev = the user's notion of 'production / real data.'" In fact the three environments, dev, test, and prod, each mean something, and "production" does not mean dev. That sentence went from the entry file into personal memory, and during the cleanup it was moved verbatim into a newly written development-environment document. A word-for-word move guaranteed that no rule was lost, and it also guaranteed that no error was lost. Review found it. After the user corrected it, the repo and the personal memory were both fixed.

So the full rule is: personal memory holds only collaboration preferences; project-level lessons go into L0 or L1 according to their layer; before a migration, verify and then move; and check the facts once before the move and once after.

## 7. Mechanism 5: freshness

Current-fact documents — the project overview, the roadmap, the various specs — are believed by the agent as soon as it reads them. What they fear most is having been right once and being wrong now. Post 1 noted that the project overview stopped on September 3, and several versions shipped after that without a change to it.

**A review date.** The header of a current-fact document must carry `Last reviewed: YYYY-MM-DD`. If it is missing, that is an error. A review date earlier than the most recent release means the last time someone confirmed it was still right was before the previous version. The ordinary check only warns on this. It does not block the work, but the warning is visible every time. After the cleanup was merged there were 10 such warnings. In release-seal mode (`--release`), an outdated project overview or roadmap is an error outright.

**A cap on banners.** Post 1 noted that the date banners at the top of the roadmap were stacked one on another and had become a second changelog. The rule now: the top of the roadmap keeps at most 5 banners, and older ones move into the archive. The plan index is allowed none. The full record belongs in implementation records and in L3 execution reports. The two release documents are deliverables, and they do not receive banners. A banner says "what happened recently." Capping it is what makes it roll.

## 8. Where the human adjudicates

The second half of principle 2, "the human only adjudicates," has a record in this cleanup:

- **Approving the plan.** The cleanup itself was a documentation change (ID D-20261014-001). By project rule the plan was written first and implemented after approval. The code in the plan had already been rehearsed on a copy of the repo. What the human approved was a plan that had been run on real data (section 9).
- **Drawing a boundary.** Task review found that the doc-lint code given in the plan had written this project's old status mapping (such as `completed` → `verified`) into the vocabulary, and that the inheritance relation had this project's paths hardcoded. After the user adjudicated, the first moved into a one-shot migration script, and the second moved into project config. "Project history does not enter the checker code," in section 5, is the boundary that decision held.
- **Correcting a definition.** The sentence "production = dev" in section 6 was found in review and corrected by the user.
- **Rejecting a false defect.** Review found that a comment on a save endpoint said "in flight, the current handler only," while the implementation also let the creator through, and recorded it as "suspected defect, pending a decision." The user pointed out that the detail page calls this save endpoint before "approve" is clicked, so it cannot be tightened. After the call chain and the fix record of August 20 were checked, the judgment was withdrawn, and the document was changed to "the comment is narrower than the implementation; the code is the authority." A comment is not the source of truth. The call chain is.
- **Deciding not to do it.** No hook, and no CI gate, is a project-level decision. doc-lint's two enforcement points were designed from that decision.

What they share: a machine can find an inconsistency. It cannot judge which side is right.

## 9. The cleanup, as it happened

There were 33 commits related to the cleanup. In the table below, "before" is the start of the cleanup branch, and "after" is the main development branch once the cleanup had been merged. The same script measured each item. Only the rows that bear on lifecycle are kept:

| Metric | Before | After |
|---|---|---|
| doc-lint violations (measured with the tool from after the cleanup) | 304 ERRORs | 0 ERRORs |
| Entry file AGENTS.md | 457 lines | 242 lines (the 9 Code review items are still in the entry file) |
| Broken links across the repo (the same new checker) | 521 (0 at the entry layer) | 521 (0 at the entry layer) |

The addressing rows — IDs, status, metadata, the index, and the case views — are in section 11 of post 3.

**The same ruler.** 304 is what the post-cleanup doc-lint measured on the pre-cleanup tree. The leading items are in post 3. Different tools, and the numbers are not comparable. The same ruler, and anyone can re-run it against the pre-cleanup commit.

Broken links are the example in the other direction. Measuring the post-cleanup tree with the old pre-cleanup checker produced 638, more than before the cleanup. That was a false positive: the old checker treated example links inside code blocks as broken links, and the post-cleanup docs contain more examples. The new checker measures 521 both before and after. The count of deep broken links did not change. All of them went into the baseline, which may only fall, never rise.

The cleanup itself also exposed problems. Two of them bear directly on this post's argument.

**Rehearse the plan on real data first.** The code was pulled out of the plan and run on a copy of the repo. Before approval, 5 defects turned up. Truncating the "next step" text cut into a Markdown link and produced a new broken link. The index preamble does not start with `> 20`, so the banner check missed it. When a missing row was registered, the title repeated the ID prefix. One test forgot to pass the onboarding config. And a batch of old-format Case IDs did not match the new rule. Before the rehearsal, that version of the tool reported 308 ERRORs. After the rehearsal, 0. A migration script is code, the same as lint, and it has to be run on real data first.

**A one-shot migration script cannot be re-run.** The plan said that when merging the main development branch, "take its index and re-run the migration script." Final review simulated this in a temporary worktree and found that the script aborted on the rows with the wrong column count. Even if that were bypassed, it would drop the cleanup change's own index rows and write the status back. In the end it was absorbed by hand. A migration script is written for one starting point. That has to be written into the document, or the next agent will re-run it because the text says to.

## 10. Each document: when it is written back, who checks, and what the human does

| Document | Write-back trigger | Where it is written | Who enforces | Human's role |
|---|---|---|---|---|
| Requirements / design | Before starting; when scope or the design changes | The change's bundle | doc-lint (registration, metadata) | Approve the plan |
| Implementation record | When status enters "implemented" | The bundle's implementation record; in the lightweight shape, an "implementation record" section inside requirements | doc-lint | Read the deviation summary and confirm the departure is acceptable |
| Case index | A case is added or changed | The case main table; views are generated by script | doc-lint | At acceptance, confirm a coverage gap is acceptable |
| Development / testing spec | An incident is codified; a reusable pitfall is hit | The L1 spec, plus one L0 row when the risk is high | Code review | Make the call on the new rule and the definition |
| DB migration | A schema change or cross-environment data | The migration script and the migration index | A review check; taking a number is still a manual rule | Before deploy, confirm the execution list |
| Deployment runbook | The environment or the process changes | The matching booklet | Code review | Approve production |
| Incident report | After an incident | L3; the lesson takes the rule-codifying pipeline separately | A human | Confirm the root cause, and decide which rung the rule is codified onto |
| Project overview / roadmap | A release, or a change of scope | The current-fact document, with banners capped | doc-lint (review date, banners) | Make the call when definitions conflict |
| User manual | A user-visible feature change | The matching section of the manual | Code review | Spot-check, then confirm the deliverable |
| Changelog / handover note | A release | The deliverables directory, against the template | The release-seal checklist + doc-lint | Accept the release seal, and confirm the deliverable |
| Personal memory | A collaboration preference changes | Memory on this machine | None; preferences only | When a definition is corrected, confirm both places change together |

The more formatted something is, the earlier it is handed to a machine. Whether the content is right still depends on review and on a human. No cell of "human's role" says "maintain."

## 11. How this mechanism breaks

### Failure 1: the checker itself is wrong

A checker is code, and it can be wrong. The link checker originally did not skip code blocks. Example links in the cleanup plan itself were false positives, 58 of them, and existing documents produced 12 more. The 638 measured by the old checker, earlier in this post, is the same defect. One case where the template check judged its scope by phrases in the body, and skipped a document, is in post 3. Problems of this kind show up only when the check is run on the tool's own documents (dogfooding: checking yourself with your own product).

Rules go stale too. Vocabulary, column count, and length limits are all set by today's practice. When the practice changes and the rule does not, the agent will twist the document to satisfy an outdated rule. The counter: list the check rules as a table in the documentation-model spec, one-to-one with the check codes. When a rule forces a document out of shape, hand the rule change to a human. The spec, the code, and the tests change together. The agent does not step around it.

### Failure 2: enforcement that is too heavy forces the agent to step around it

A rule that cannot be satisfied will be satisfied by the agent in the cheapest way: boilerplate in a required section, a formally valid value in a field, or adding the file to the exemption list. So enforcement has to come with an exception path. Existing problems go into the exemption list of the onboarding config. Sections of a template that are not required are marked "optional." Banners are capped rather than cleared to zero. The old-format Case IDs during the cleanup took this path: into the exemption list, and not renamed. The exception path has one requirement: **explicit, gathered in one place, and visible.** Every exemption is one line in the same file, and the change shows up in the diff.

### Failure 3: "only fall, never rise" is only written down

The spec says the baseline file may only be lowered. The tool delivers half of that. Repo-wide broken links have a numeric baseline, and exceeding it is an error. The exemption list does not. Template exemptions started at 315 during the cleanup, were trimmed to 314, and gained another 4 when the main development branch was merged, becoming 318. Those 4 were existing documents that had already been filed before the rule took effect and came in with the merge, and the commit message stated the reason. This increase had a reason. Even with no reason, no check would have reported an error. Entries in the list that are no longer in force are not reported either. The second half of principle 3, today, depends on someone reading the diff. The repair is not hard — for example, compare the exemption count with the previous tag (the version mark placed on a commit at release time) and allow only fewer, never more. Until that is added, it is the softest link in the mechanism.

### Failure 4: the list of forbidden words leaks itself

This happened in the repo where this series was written. While the plan was being written, the whole redaction word list and the real configuration names were committed as test fixtures. Final review found them. The handling: the word list exists only in a directory that is not committed; test fixtures are concatenated at runtime; the checker gained a repo-wide scan, and commit messages are scanned too; the repo history was rebuilt, and the old history was kept only as a local backup. The lesson: **the list of words that must not appear is itself sensitive.** A checker's configuration is a document too, and it has a lifecycle of its own.

## 12. Summary

1. Docs rot in three places: the work is done and nothing is written back, the convention depends on good intentions, and old facts do not leave the stage. A written rule does not stop it. The agent that writes the docs is amnesiac too.
2. Three principles. Write-back is part of the change (no memory across sessions). A machine enforces the convention, and the human only adjudicates (is also the main author, and can run scripts). Zero tolerance at the entry layer, and deeper layers have a baseline that may only fall, never rise (every session enters through the entry and follows the literal text).
3. Every rule sits on the enforcement ladder, from narrative up to an automatic check. The question to ask is "can it climb one more rung?"
4. doc-lint is the test suite for docs. It does not depend on a hook or on CI. The enforcement points are one row of the routing table plus the release-seal gate. The cost is that a violation can enter the repo first, with the release seal as the backstop.
5. Personal memory holds only collaboration preferences, and a migration verifies first. Current fact carries a review date, and banners are capped so they roll.
6. The mechanism breaks on its own: the tool false-positives, rules go stale, exemptions can quietly grow, and even the redaction list can leak. The checker has to be checked too.

### End of the series

Read together, the four posts are one sentence: in a project where an agent writes most of the code, documentation is a routing system for the agent. Post 1 gives the four-layer model. Post 2 builds the roads. Post 3 fixes the locations. This post keeps all of that from rotting over time. The human in the middle is no longer the reader and the maintainer. The human is the adjudicator.

The mechanisms in the four posts will be extracted into a skill, in two modes — initializing a new project, and onboarding an existing tree — and published separately.

### Series

1. [Agents Aren't Amnesiac — They Can't Find the Entry Point: Documentation Layers for Large Projects (1)](01-agent-is-not-amnesiac.md)
2. [Make the Agent Read Only What It Should: Documentation Routing (2)](02-routing.md)
3. [Give Every Document Exactly One Place: Documentation Addressing (3)](03-addressing.md)
4. Keep Documents from Rotting: The Document Lifecycle in the Agent Era (4) (this post)
